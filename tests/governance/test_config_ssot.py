from __future__ import annotations

import json
from pathlib import Path

import pytest

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
