from __future__ import annotations

import json
import os
from pathlib import Path

from core.optimizer import runner


class _StubEngine:
    def __init__(self) -> None:
        # Simulate a case where load_data succeeds but precompute did not populate features.
        self._precomputed_features = None

    def load_data(self) -> bool:
        return True


class _StubEnginePrecomputeFlag:
    def __init__(self) -> None:
        self.precompute_features = False

    def load_data(self) -> bool:
        # Keep the test focused on env parsing; we don't need a full backtest run.
        return False


def test_direct_execution_fails_fast_when_canonical_precompute_missing(monkeypatch, tmp_path: Path):
    """Optimizer direct-execution must not silently fall back to slow path.

    If canonical mode requests precompute (1/1) but precomputed features are missing,
    `_run_backtest_direct` should fail fast with a clear error.
    """

    # Ensure we start in a non-canonical / explicit state to prove the function forces canonical.
    monkeypatch.setenv("GENESIS_MODE_EXPLICIT", "1")
    monkeypatch.setenv("GENESIS_FAST_WINDOW", "0")
    monkeypatch.setenv("GENESIS_PRECOMPUTE_FEATURES", "0")

    # Patch engine creation to return a stub where precompute never becomes available.
    monkeypatch.setattr(
        "core.pipeline.GenesisPipeline.create_engine",
        lambda self, **kwargs: _StubEngine(),
    )

    # Minimal config payload expected by _run_backtest_direct.
    config_path = tmp_path / "trial_config.json"
    config_path.write_text(json.dumps({"cfg": {}, "merged_config": {}, "runtime_version": 1}))

    trial = runner.TrialConfig(
        snapshot_id="unit",
        symbol="tBTCUSD",
        timeframe="1h",
        warmup_bars=10,
        parameters={},
        start_date="2024-01-01",
        end_date="2024-01-02",
    )

    # Clear global engine cache to avoid cross-test contamination.
    with runner._DATA_LOCK:
        runner._DATA_CACHE.clear()

    rc, log, results = runner._run_backtest_direct(trial, config_path, optuna_context=None)

    assert rc == 1
    assert results is None
    assert "precompute" in log.lower()

    # Should have enforced canonical env (1/1) despite initial explicit 0/0.
    assert os.environ.get("GENESIS_MODE_EXPLICIT") == "0"
    assert os.environ.get("GENESIS_FAST_WINDOW") == "1"
    assert os.environ.get("GENESIS_PRECOMPUTE_FEATURES") == "1"


def test_direct_execution_does_not_enable_precompute_when_env_is_zero_and_setup_env_missing(
    monkeypatch, tmp_path: Path
):
    """Regression: avoid treating env value '0' as truthy.

    When `setup_environment` is unavailable (e.g., unit test stubs), direct execution should
    not accidentally enable precompute just because the env var is present but set to "0".
    """

    monkeypatch.setenv("GENESIS_MODE_EXPLICIT", "0")
    monkeypatch.setenv("GENESIS_FAST_WINDOW", "0")
    monkeypatch.setenv("GENESIS_PRECOMPUTE_FEATURES", "0")

    # Force the fallback path where canonical env is NOT enforced via pipeline.setup_environment.
    monkeypatch.setattr("core.pipeline.GenesisPipeline.setup_environment", None, raising=False)

    engine = _StubEnginePrecomputeFlag()
    monkeypatch.setattr(
        "core.pipeline.GenesisPipeline.create_engine",
        lambda self, **kwargs: engine,
    )

    config_path = tmp_path / "trial_config.json"
    config_path.write_text(json.dumps({"cfg": {}, "merged_config": {}, "runtime_version": 1}))

    trial = runner.TrialConfig(
        snapshot_id="unit",
        symbol="tBTCUSD",
        timeframe="1h",
        warmup_bars=10,
        parameters={},
        start_date="2024-01-01",
        end_date="2024-01-02",
    )

    with runner._DATA_LOCK:
        runner._DATA_CACHE.clear()

    rc, _log, results = runner._run_backtest_direct(trial, config_path, optuna_context=None)

    assert rc == 1
    assert results is None
    assert engine.precompute_features is False
