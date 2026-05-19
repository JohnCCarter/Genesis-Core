from __future__ import annotations

import json
from pathlib import Path

import pytest

import core.config.authority as authority_mod
from core.config.authority import ConfigAuthority


def _ri_runtime_patch() -> dict:
    return {
        "strategy_family": "ri",
        "thresholds": {
            "entry_conf_overall": 0.25,
            "regime_proba": {"balanced": 0.36},
            "signal_adaptation": {
                "atr_period": 14,
                "zones": {
                    "low": {"entry_conf_overall": 0.16, "regime_proba": 0.33},
                    "mid": {"entry_conf_overall": 0.40, "regime_proba": 0.51},
                    "high": {"entry_conf_overall": 0.32, "regime_proba": 0.57},
                },
            },
        },
        "gates": {"hysteresis_steps": 3, "cooldown_bars": 2},
    }


def test_config_roundtrip_and_hash(tmp_path: Path) -> None:
    path = tmp_path / "runtime.json"
    auth = ConfigAuthority(path)
    cfg, h1, ver1 = auth.get()
    assert ver1 == 0
    assert cfg.strategy_family == "legacy"
    snap = auth.propose_update(
        {"thresholds": {"entry_conf_overall": 0.5}}, actor="t", expected_version=0
    )
    assert snap.version == 1
    # Hash should be stable for the same canonical content
    snap2 = auth.load()
    assert snap2.hash == snap.hash


def test_authority_init_does_not_warn_when_runtime_matches_latest_audit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    runtime_path = tmp_path / "runtime.json"
    audit_path = tmp_path / "config_audit.jsonl"
    monkeypatch.setattr(authority_mod, "AUDIT_LOG", audit_path)

    auth = ConfigAuthority(runtime_path)
    auth.propose_update(
        {"thresholds": {"entry_conf_overall": 0.5}},
        actor="t",
        expected_version=0,
    )

    caplog.set_level("WARNING")
    _ = ConfigAuthority(runtime_path)

    assert not any(
        "runtime_config_state_diverged_from_audit" in rec.message for rec in caplog.records
    )


def test_authority_init_warns_on_runtime_drift_without_side_effects(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    runtime_path = tmp_path / "runtime.json"
    audit_path = tmp_path / "config_audit.jsonl"
    monkeypatch.setattr(authority_mod, "AUDIT_LOG", audit_path)

    writer = ConfigAuthority(runtime_path)
    writer.propose_update(
        {"thresholds": {"entry_conf_overall": 0.5}},
        actor="t",
        expected_version=0,
    )

    drifted_payload = json.loads(runtime_path.read_text(encoding="utf-8"))
    drifted_payload["cfg"]["thresholds"]["entry_conf_overall"] = 0.75
    drifted_text = authority_mod._json_dumps_canonical(drifted_payload)
    runtime_path.write_text(drifted_text, encoding="utf-8")

    audit_before = audit_path.read_text(encoding="utf-8")

    caplog.set_level("WARNING")
    auth = ConfigAuthority(runtime_path)
    cfg, _hash, version = auth.get()

    assert version == 1
    assert cfg.thresholds.entry_conf_overall == pytest.approx(0.75)
    assert runtime_path.read_text(encoding="utf-8") == drifted_text
    assert audit_path.read_text(encoding="utf-8") == audit_before
    assert any("runtime_config_state_diverged_from_audit" in rec.message for rec in caplog.records)


def test_authority_init_fails_open_without_audit_log(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    runtime_path = tmp_path / "runtime.json"
    audit_path = tmp_path / "config_audit.jsonl"
    monkeypatch.setattr(authority_mod, "AUDIT_LOG", audit_path)

    writer = ConfigAuthority(runtime_path)
    writer.propose_update(
        {"thresholds": {"entry_conf_overall": 0.5}},
        actor="t",
        expected_version=0,
    )
    audit_path.unlink()

    caplog.set_level("WARNING")
    auth = ConfigAuthority(runtime_path)
    cfg, _hash, version = auth.get()

    assert version == 1
    assert cfg.thresholds.entry_conf_overall == pytest.approx(0.5)
    assert not any(
        "runtime_config_state_diverged_from_audit" in rec.message for rec in caplog.records
    )


def test_authority_init_fails_open_when_latest_audit_line_is_not_comparable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    runtime_path = tmp_path / "runtime.json"
    audit_path = tmp_path / "config_audit.jsonl"
    monkeypatch.setattr(authority_mod, "AUDIT_LOG", audit_path)

    writer = ConfigAuthority(runtime_path)
    writer.propose_update(
        {"thresholds": {"entry_conf_overall": 0.5}},
        actor="t",
        expected_version=0,
    )

    runtime_before = runtime_path.read_text(encoding="utf-8")
    audit_with_non_comparable_tail = audit_path.read_text(encoding="utf-8") + '{"ts": 1}\n'
    audit_path.write_text(audit_with_non_comparable_tail, encoding="utf-8")

    caplog.set_level("WARNING")
    auth = ConfigAuthority(runtime_path)
    cfg, _hash, version = auth.get()

    assert version == 1
    assert cfg.thresholds.entry_conf_overall == pytest.approx(0.5)
    assert runtime_path.read_text(encoding="utf-8") == runtime_before
    assert audit_path.read_text(encoding="utf-8") == audit_with_non_comparable_tail
    assert not any(
        "runtime_config_state_diverged_from_audit" in rec.message for rec in caplog.records
    )


def test_propose_update_atomic_locking_conflict(tmp_path: Path) -> None:
    path = tmp_path / "runtime.json"
    auth = ConfigAuthority(path)
    # First update to bump version to 1
    auth.propose_update({"gates": {"hysteresis_steps": 3}}, actor="t", expected_version=0)
    # Second update with stale expected_version
    with pytest.raises(RuntimeError):
        auth.propose_update({"gates": {"cooldown_bars": 1}}, actor="t", expected_version=0)


def test_only_whitelisted_keys_change(tmp_path: Path) -> None:
    path = tmp_path / "runtime.json"
    auth = ConfigAuthority(path)
    with pytest.raises(ValueError):
        auth.propose_update(
            {"features": {"percentiles": {"rsi": [-1, 1]}}}, actor="t", expected_version=0
        )


def test_exit_enabled_singleton_patch_is_whitelisted(tmp_path: Path) -> None:
    path = tmp_path / "runtime.json"
    auth = ConfigAuthority(path)

    snap = auth.propose_update(
        {"exit": {"enabled": False}},
        actor="t",
        expected_version=0,
    )

    assert snap.version == 1
    assert snap.cfg.exit.enabled is False
    assert snap.cfg.exit.stop_loss_pct == pytest.approx(0.02)

    persisted = json.loads(path.read_text(encoding="utf-8"))
    assert persisted["cfg"]["exit"]["enabled"] is False
    assert persisted["cfg"]["exit"]["stop_loss_pct"] == pytest.approx(0.02)


@pytest.mark.parametrize(
    "payload",
    [
        {"exit": False},
        {"exit": {}},
        {"exit": {"stop_loss_pct": 0.01}},
        {"exit": {"enabled": False, "stop_loss_pct": 0.01}},
    ],
)
def test_exit_patch_rejects_non_singleton_shapes_atomically(
    tmp_path: Path, payload: dict[str, object]
) -> None:
    path = tmp_path / "runtime.json"
    auth = ConfigAuthority(path)

    initial_cfg, initial_hash, initial_version = auth.get()

    with pytest.raises(ValueError, match="non_whitelisted_field:exit"):
        auth.propose_update(payload, actor="t", expected_version=initial_version)

    cfg_after, hash_after, version_after = auth.get()
    assert version_after == initial_version
    assert hash_after == initial_hash
    assert cfg_after.model_dump_canonical() == initial_cfg.model_dump_canonical()


def test_multi_timeframe_regime_intelligence_authority_mode_whitelisted(tmp_path: Path) -> None:
    path = tmp_path / "runtime.json"
    auth = ConfigAuthority(path)

    snap = auth.propose_update(
        {
            **_ri_runtime_patch(),
            "multi_timeframe": {"regime_intelligence": {"authority_mode": "regime_module"}},
        },
        actor="t",
        expected_version=0,
    )

    assert snap.version == 1
    assert snap.cfg.multi_timeframe.regime_intelligence.authority_mode == "regime_module"
    assert snap.cfg.strategy_family == "ri"


def test_multi_timeframe_regime_intelligence_authority_mode_strict_value(tmp_path: Path) -> None:
    path = tmp_path / "runtime.json"
    auth = ConfigAuthority(path)

    with pytest.raises(ValueError):
        auth.propose_update(
            {"multi_timeframe": {"regime_intelligence": {"authority_mode": "invalid_mode"}}},
            actor="t",
            expected_version=0,
        )


def test_multi_timeframe_regime_intelligence_regime_definition_whitelisted(tmp_path: Path) -> None:
    path = tmp_path / "runtime.json"
    auth = ConfigAuthority(path)

    snap = auth.propose_update(
        {
            **_ri_runtime_patch(),
            "multi_timeframe": {
                "regime_intelligence": {
                    "authority_mode": "regime_module",
                    "regime_definition": {
                        "adx_trend_threshold": 25.0,
                        "adx_range_threshold": 20.0,
                        "slope_threshold": 0.001,
                        "volatility_threshold": 0.05,
                    },
                }
            },
        },
        actor="t",
        expected_version=0,
    )

    regime_definition = snap.cfg.multi_timeframe.regime_intelligence.regime_definition
    assert regime_definition is not None
    assert regime_definition.adx_trend_threshold == 25.0
    assert regime_definition.adx_range_threshold == 20.0


def test_multi_timeframe_research_policy_router_whitelisted(tmp_path: Path) -> None:
    path = tmp_path / "runtime.json"
    auth = ConfigAuthority(path)

    snap = auth.propose_update(
        {
            **_ri_runtime_patch(),
            "multi_timeframe": {
                "regime_intelligence": {"authority_mode": "regime_module"},
                "research_policy_router": {
                    "enabled": True,
                    "switch_threshold": 2,
                    "hysteresis": 1,
                    "continuation_release_hysteresis": 0,
                    "min_dwell": 3,
                    "defensive_size_multiplier": 0.5,
                },
            },
        },
        actor="t",
        expected_version=0,
    )

    assert snap.version == 1
    router_cfg = snap.cfg.multi_timeframe.research_policy_router
    assert router_cfg is not None
    assert router_cfg.enabled is True
    assert router_cfg.switch_threshold == 2
    assert router_cfg.hysteresis == 1
    assert router_cfg.continuation_release_hysteresis == 0
    assert router_cfg.min_dwell == 3
    assert router_cfg.defensive_size_multiplier == pytest.approx(0.5)

    persisted = json.loads(path.read_text(encoding="utf-8"))
    assert persisted["cfg"]["multi_timeframe"]["research_policy_router"] == {
        "enabled": True,
        "switch_threshold": 2,
        "hysteresis": 1,
        "continuation_release_hysteresis": 0,
        "min_dwell": 3,
        "defensive_size_multiplier": 0.5,
    }


def test_multi_timeframe_regime_intelligence_rejects_non_whitelisted_nested_keys(
    tmp_path: Path,
) -> None:
    path = tmp_path / "runtime.json"
    auth = ConfigAuthority(path)

    with pytest.raises(ValueError):
        auth.propose_update(
            {"multi_timeframe": {"regime_intelligence": {"authority_mode": "legacy", "extra": 1}}},
            actor="t",
            expected_version=0,
        )


def test_multi_timeframe_regime_intelligence_rejects_partial_regime_definition(
    tmp_path: Path,
) -> None:
    path = tmp_path / "runtime.json"
    auth = ConfigAuthority(path)

    with pytest.raises(ValueError):
        auth.propose_update(
            {
                "multi_timeframe": {
                    "regime_intelligence": {
                        "regime_definition": {
                            "adx_trend_threshold": 25.0,
                            "adx_range_threshold": 20.0,
                        }
                    }
                }
            },
            actor="t",
            expected_version=0,
        )


def test_multi_timeframe_regime_intelligence_rejects_regime_definition_extra_keys(
    tmp_path: Path,
) -> None:
    path = tmp_path / "runtime.json"
    auth = ConfigAuthority(path)

    with pytest.raises(ValueError):
        auth.propose_update(
            {
                "multi_timeframe": {
                    "regime_intelligence": {
                        "regime_definition": {
                            "adx_trend_threshold": 25.0,
                            "adx_range_threshold": 20.0,
                            "slope_threshold": 0.001,
                            "volatility_threshold": 0.05,
                            "extra": 1,
                        }
                    }
                }
            },
            actor="t",
            expected_version=0,
        )


def test_regime_unified_alias_only_is_canonicalized_before_persist(tmp_path: Path) -> None:
    path = tmp_path / "runtime.json"
    auth = ConfigAuthority(path)

    snap = auth.propose_update(
        {**_ri_runtime_patch(), "regime_unified": {"authority_mode": "regime_module"}},
        actor="t",
        expected_version=0,
    )

    assert snap.version == 1
    assert snap.cfg.multi_timeframe.regime_intelligence.authority_mode == "regime_module"
    assert snap.cfg.strategy_family == "ri"

    persisted = json.loads(path.read_text(encoding="utf-8"))
    cfg = persisted.get("cfg") or {}
    assert "regime_unified" not in cfg
    assert cfg["strategy_family"] == "ri"
    assert cfg["multi_timeframe"]["regime_intelligence"]["authority_mode"] == "regime_module"


def test_regime_unified_alias_non_dict_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "runtime.json"
    auth = ConfigAuthority(path)

    with pytest.raises(ValueError):
        auth.validate({"regime_unified": "legacy"})

    with pytest.raises(ValueError):
        auth.propose_update(
            {"regime_unified": "legacy"},
            actor="t",
            expected_version=0,
        )


def test_regime_unified_alias_extra_key_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "runtime.json"
    auth = ConfigAuthority(path)

    payload = {"regime_unified": {"authority_mode": "legacy", "extra": 1}}

    with pytest.raises(ValueError):
        auth.validate(payload)

    with pytest.raises(ValueError):
        auth.propose_update(payload, actor="t", expected_version=0)


def test_regime_unified_alias_conflict_uses_canonical_value(tmp_path: Path) -> None:
    path = tmp_path / "runtime.json"
    auth = ConfigAuthority(path)

    snap = auth.propose_update(
        {
            "multi_timeframe": {"regime_intelligence": {"authority_mode": "legacy"}},
            "regime_unified": {"authority_mode": "regime_module"},
        },
        actor="t",
        expected_version=0,
    )

    assert snap.version == 1
    assert snap.cfg.multi_timeframe.regime_intelligence.authority_mode == "legacy"
    assert snap.cfg.strategy_family == "legacy"


def test_regime_unified_alias_conflict_invalid_canonical_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "runtime.json"
    auth = ConfigAuthority(path)

    with pytest.raises(ValueError):
        auth.propose_update(
            {
                "multi_timeframe": {"regime_intelligence": {"authority_mode": "invalid_mode"}},
                "regime_unified": {"authority_mode": "regime_module"},
            },
            actor="t",
            expected_version=0,
        )


def test_legacy_runtime_rejects_ri_signature_markers(tmp_path: Path) -> None:
    path = tmp_path / "runtime.json"
    auth = ConfigAuthority(path)

    with pytest.raises(ValueError):
        auth.validate(
            {
                "strategy_family": "legacy",
                "thresholds": {
                    "entry_conf_overall": 0.25,
                    "regime_proba": {"balanced": 0.36},
                    "signal_adaptation": {
                        "atr_period": 14,
                        "zones": {
                            "low": {"entry_conf_overall": 0.16, "regime_proba": 0.33},
                            "mid": {"entry_conf_overall": 0.40, "regime_proba": 0.51},
                            "high": {"entry_conf_overall": 0.32, "regime_proba": 0.57},
                        },
                    },
                },
                "gates": {"hysteresis_steps": 3, "cooldown_bars": 2},
                "multi_timeframe": {"regime_intelligence": {"authority_mode": "legacy"}},
            }
        )


def test_authority_bootstraps_legacy_family_when_runtime_file_is_missing(tmp_path: Path) -> None:
    path = tmp_path / "runtime.json"
    auth = ConfigAuthority(path)

    cfg, _hash, version = auth.get()

    assert version == 0
    assert cfg.strategy_family == "legacy"
    assert cfg.multi_timeframe.regime_intelligence.authority_mode == "legacy"
