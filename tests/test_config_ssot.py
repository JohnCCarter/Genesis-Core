from __future__ import annotations

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
