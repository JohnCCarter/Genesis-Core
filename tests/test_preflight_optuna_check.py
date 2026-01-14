from __future__ import annotations

import sys
import types

import pytest

from scripts.preflight_optuna_check import (
    _parse_snapshot_date_range,
    _pick_data_file,
    check_champion_drift_smoke,
    check_htf_requirements,
    check_mode_flags_consistency,
    check_storage_resume_sanity,
)


def test_mode_flags_requires_precompute(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GENESIS_MODE_EXPLICIT", raising=False)
    monkeypatch.setenv("GENESIS_FAST_WINDOW", "1")
    monkeypatch.delenv("GENESIS_PRECOMPUTE_FEATURES", raising=False)

    ok, msg = check_mode_flags_consistency()
    assert ok is False
    assert "requires" in msg or "kräver" in msg


def test_storage_resume_warns_when_storage_null(monkeypatch: pytest.MonkeyPatch) -> None:
    ok, msg = check_storage_resume_sanity(
        storage=None,
        allow_resume=True,
        n_jobs=1,
        max_concurrent=1,
    )
    assert ok is True
    assert "storage=null" in msg


def test_htf_requirements_fails_without_1d_data(monkeypatch: pytest.MonkeyPatch) -> None:
    # Use an intentionally unknown symbol to avoid relying on repo data.
    meta = {"symbol": "tNOTAREAL"}
    parameters = {"htf_exit_config": {"enable_partials": {"type": "fixed", "value": True}}}

    monkeypatch.delenv("GENESIS_HTF_EXITS", raising=False)

    ok, msg = check_htf_requirements(meta, parameters)
    assert ok is False
    assert "1D" in msg


def test_htf_requirements_warns_when_env_missing_but_data_exists(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # This test is only meaningful if repo contains 1D candles for tBTCUSD.
    if _pick_data_file("tBTCUSD", "1D") is None:
        pytest.skip("No tBTCUSD 1D data found in repo")

    meta = {"symbol": "tBTCUSD"}
    parameters = {"htf_exit_config": {"enable_partials": {"type": "fixed", "value": True}}}

    monkeypatch.delenv("GENESIS_HTF_EXITS", raising=False)

    ok, msg = check_htf_requirements(meta, parameters)
    assert ok is True
    assert msg.startswith("[WARN]")


def test_htf_requirements_ok_when_env_set(monkeypatch: pytest.MonkeyPatch) -> None:
    if _pick_data_file("tBTCUSD", "1D") is None:
        pytest.skip("No tBTCUSD 1D data found in repo")

    meta = {"symbol": "tBTCUSD"}
    parameters = {"htf_exit_config": {"enable_partials": {"type": "fixed", "value": True}}}

    monkeypatch.setenv("GENESIS_HTF_EXITS", "1")

    ok, msg = check_htf_requirements(meta, parameters)
    assert ok is True
    assert msg.startswith("[OK]")


def test_parse_snapshot_date_range_parses_expected_format() -> None:
    dr = _parse_snapshot_date_range("snap_tBTCUSD_2024-01-01_2024-12-31_v1")
    assert dr is not None
    start_dt, end_dt = dr
    assert start_dt.date().isoformat() == "2024-01-01"
    assert end_dt.date().isoformat() == "2024-12-31"


def test_champion_drift_smoke_can_be_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GENESIS_PREFLIGHT_CHAMPION_SMOKE", "0")
    ok, msg = check_champion_drift_smoke("tBTCUSD", "1h")
    assert ok is True
    assert msg.startswith("[SKIP]")


def test_main_fails_when_timeout_check_fails(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    # Regression test: preflight ska INTE säga OK om end_at/timeout-checken failar.
    from scripts import preflight_optuna_check as preflight

    cfg_path = tmp_path / "cfg.yaml"
    cfg_path.write_text(
        """
meta:
  runs:
    optuna:
      end_at: "2000-01-01T00:00:00Z"
parameters: {}
""".lstrip(),
        encoding="utf-8",
    )

    # Isolera testet från miljö/beroenden: patcha bort alla andra checks.
    monkeypatch.setattr(preflight, "maybe_load_dotenv", lambda: (True, "[OK]"))
    monkeypatch.setattr(preflight, "check_optuna_installed", lambda: (True, "[OK]"))
    monkeypatch.setattr(preflight, "check_storage_writable", lambda storage: (True, "[OK]"))
    monkeypatch.setattr(
        preflight, "check_study_resume", lambda storage, study_name, allow_resume: (True, "[OK]")
    )
    monkeypatch.setattr(preflight, "check_sampler_settings", lambda optuna_cfg: (True, "[OK]"))
    monkeypatch.setattr(preflight, "check_duplicate_guard", lambda: (True, "[OK]"))

    # Detta är den enda check vi vill att ska faila.
    monkeypatch.setattr(
        preflight,
        "check_timeout_config",
        lambda max_trials, timeout_seconds, end_at: (False, "[FAIL] end_at ligger i dåtiden"),
    )

    monkeypatch.setattr(preflight, "check_mode_flags_consistency", lambda: (True, "[OK]"))
    monkeypatch.setattr(
        preflight,
        "check_storage_resume_sanity",
        lambda storage, allow_resume, n_jobs, max_concurrent: (True, "[OK]"),
    )
    monkeypatch.setattr(preflight, "check_parameters_valid", lambda parameters: (True, "[OK]"))
    monkeypatch.setattr(
        preflight, "check_snapshot_exists", lambda snapshot_id, symbol, timeframe: (True, "[OK]")
    )
    monkeypatch.setattr(
        preflight, "check_htf_requirements", lambda meta, parameters: (True, "[OK]")
    )
    monkeypatch.setattr(preflight, "check_date_source", lambda meta, runs_cfg: (True, "[OK]"))
    monkeypatch.setattr(
        preflight, "check_requested_data_coverage", lambda meta, runs_cfg: (True, "[OK]")
    )
    monkeypatch.setattr(
        preflight, "check_champion_drift_smoke", lambda symbol, timeframe: (True, "[OK]")
    )
    monkeypatch.setattr(
        preflight, "check_precompute_functionality", lambda symbol, timeframe: (True, "[OK]")
    )

    # main() importerar validate_config dynamiskt; injicera en stub så vi slipper beroenden.
    stub = types.ModuleType("scripts.validate_optimizer_config")
    stub.validate_config = lambda path: 0  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "scripts.validate_optimizer_config", stub)

    # Kör som CLI.
    monkeypatch.setattr(sys, "argv", ["preflight_optuna_check.py", str(cfg_path)])
    assert preflight.main() == 1
