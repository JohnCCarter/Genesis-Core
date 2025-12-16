from __future__ import annotations

from pathlib import Path

import core.optimizer.runner as runner


class _DummyPositionTracker:
    def __init__(self) -> None:
        self.commission_rate = 0.0
        self.slippage_rate = 0.0


class _DummyEngine:
    def __init__(self) -> None:
        self.warmup_bars = 0
        self.position_tracker = _DummyPositionTracker()
        self.last_configs = None

    def load_data(self) -> bool:
        return True

    def run(self, *, policy, configs, verbose, pruning_callback=None):
        self.last_configs = configs
        return {"metrics": {"num_trades": 0}}


class _DummyPipeline:
    def __init__(self) -> None:
        self.engine = _DummyEngine()

    def create_engine(
        self,
        *,
        symbol: str,
        timeframe: str,
        start_date: str | None,
        end_date: str | None,
        warmup_bars: int,
    ):
        self.engine.warmup_bars = warmup_bars
        return self.engine


def test_run_backtest_direct_includes_merged_config(monkeypatch, tmp_path: Path):
    """Direct execution should still attach merged_config + provenance to results.

    This is required so config-equivalence checks work for direct-mode runs where
    results are saved under the run_dir (not results/backtests).
    """

    # Avoid touching real runtime.json in a unit test.
    monkeypatch.setattr(runner, "_get_default_runtime_version", lambda: 777)

    # Ensure the module cache doesn't leak state across tests.
    monkeypatch.setattr(runner, "_DATA_CACHE", {})

    # Patch pipeline used inside _run_backtest_direct.
    import core.pipeline as pipeline_mod

    monkeypatch.setattr(pipeline_mod, "GenesisPipeline", _DummyPipeline)

    config_payload = {
        "cfg": {"a": 1},
        "merged_config": {"a": 2},
        "runtime_version": 123,
        "overrides": {"commission": 0.001, "slippage": 0.0005},
    }
    config_path = tmp_path / "trial_001_config.json"
    config_path.write_text(__import__("json").dumps(config_payload), encoding="utf-8")

    trial = runner.TrialConfig(
        snapshot_id="dummy_snapshot",
        symbol="tBTCUSD",
        timeframe="1h",
        warmup_bars=150,
        parameters={},
        start_date="2024-01-01",
        end_date="2024-01-02",
    )

    code, _log, results = runner._run_backtest_direct(trial, config_path, optuna_context=None)
    assert code == 0
    assert isinstance(results, dict)

    # Ensure the effective config used is the merged_config.
    assert results["merged_config"] == {"a": 2}

    # Runtime/provenance should be attached.
    assert results["runtime_version"] == 123
    assert results["runtime_version_current"] == 777
    assert results["config_provenance"]["used_runtime_merge"] is False
    assert results["config_provenance"]["config_file_is_complete"] is True

    # Sanity: engine saw the effective config.
    engine = runner._DATA_CACHE[
        f"{trial.symbol}_{trial.timeframe}_{trial.start_date}_{trial.end_date}"
    ]
    assert engine.last_configs == {"a": 2}
