from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.config.authority import ConfigAuthority


def test_config_roundtrip_and_hash(tmp_path: Path) -> None:
    path = tmp_path / "runtime.json"
    auth = ConfigAuthority(path)
    cfg, h1, ver1 = auth.get()
    assert ver1 == 0
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
        {"multi_timeframe": {"regime_intelligence": {"authority_mode": "regime_module"}}},
        actor="t",
        expected_version=0,
    )

    assert snap.version == 1
    assert snap.cfg.multi_timeframe.regime_intelligence.authority_mode == "regime_module"


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
        {"regime_unified": {"authority_mode": "regime_module"}},
        actor="t",
        expected_version=0,
    )

    assert snap.version == 1
    assert snap.cfg.multi_timeframe.regime_intelligence.authority_mode == "regime_module"

    persisted = json.loads(path.read_text(encoding="utf-8"))
    cfg = persisted.get("cfg") or {}
    assert "regime_unified" not in cfg
    assert cfg["multi_timeframe"]["regime_intelligence"]["authority_mode"] == "regime_module"


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
