from __future__ import annotations

import json
import sys
from pathlib import Path

import scripts.run.run_backtest as run_backtest
from core.backtest.intelligence_shadow import BacktestIntelligenceShadowRecorder


class _DummyCfg:
    def __init__(self, payload: dict):
        self._payload = payload

    def model_dump(self) -> dict:
        return dict(self._payload)


class _DummyAuthority:
    def __init__(self, payload: dict | None = None, runtime_version: int = 7):
        self.payload = payload or {"strategy_family": "legacy"}
        self.runtime_version = runtime_version

    def get(self):
        return _DummyCfg(self.payload), None, self.runtime_version

    def validate(self, merged_cfg: dict):
        return _DummyCfg(merged_cfg)


class _DummyChampionConfig:
    def __init__(self, config: dict):
        self.config = config


class _DummyChampionLoader:
    def __init__(self, config: dict):
        self._config = config

    def load_cached(self, _symbol: str, _timeframe: str):
        return _DummyChampionConfig(self._config)


class _DummyPositionTracker:
    initial_capital = 10000.0
    commission_rate = 0.0
    slippage_rate = 0.0


class _DummyEngine:
    def __init__(self) -> None:
        self.warmup_bars = 0
        self.position_tracker = _DummyPositionTracker()
        self.evaluation_hook = None
        self.champion_loader = _DummyChampionLoader(
            {"strategy_family": "legacy", "thresholds": {"entry_conf_overall": 0.26}}
        )
        self.last_configs = None
        self.last_result = None
        self.last_meta = None
        self.last_results = None

    def load_data(self) -> bool:
        return True

    def run(self, *, policy=None, configs=None, verbose=False, pruning_callback=None, **_kwargs):
        _ = (policy, verbose, pruning_callback)
        self.last_configs = configs
        result = {"action": "LONG", "confidence": {"overall": 0.8}}
        meta = {"decision": {"size": 0.25, "reasons": ["ENTRY_LONG"]}}
        candles = {
            "timestamp": ["2025-01-01T00:00:00+00:00"],
            "bar_index": 0,
            "symbol": "tBTCUSD",
        }
        if self.evaluation_hook is not None:
            result, meta = self.evaluation_hook(result, meta, candles)
        self.last_result = result
        self.last_meta = meta
        self.last_results = {
            "backtest_info": {
                "symbol": "tBTCUSD",
                "timeframe": "1h",
                "start_date": "2025-01-01T00:00:00+00:00",
                "end_date": "2025-01-01T01:00:00+00:00",
                "bars_processed": 1,
                "warmup_bars": 0,
                "seed": "42",
                "git_hash": "dummy",
                "effective_config_fingerprint": "fp-dummy",
            },
            "summary": {
                "num_trades": 1,
                "total_return": 0.0,
                "win_rate": 100.0,
                "profit_factor": 1.0,
            },
            "metrics": {"num_trades": 1},
            "trades": [{"entry_bar": 0, "exit_bar": 1, "pnl": 1.0}],
            "equity_curve": [{"equity": 10000.0}],
        }
        return self.last_results


class _DummyPipeline:
    defaults = {
        "capital": 10000.0,
        "commission": 0.0,
        "slippage": 0.0,
        "warmup": 0,
    }

    def __init__(self, created_engines: list[_DummyEngine]) -> None:
        self._created_engines = created_engines

    def setup_environment(self, seed: int = 42):
        _ = seed

    def create_engine(self, **_kwargs):
        engine = _DummyEngine()
        self._created_engines.append(engine)
        return engine


def test_shadow_hook_is_identity_and_records_event(tmp_path: Path) -> None:
    recorder = BacktestIntelligenceShadowRecorder(
        symbol="tTESTBTC:TESTUSD",
        timeframe="1h",
        repo_root=tmp_path,
    )
    result = {"action": "LONG", "confidence": {"overall": 0.8}}
    meta = {"decision": {"size": 0.125, "reasons": ["ENTRY_LONG"]}}
    candles = {
        "timestamp": ["2025-01-01T00:00:00+00:00"],
        "bar_index": 42,
    }

    hook = recorder.create_hook(upstream_hook=None)
    out_result, out_meta = hook(result, meta, candles)

    assert out_result is result
    assert out_meta is meta
    assert len(recorder.events) == 1
    event = recorder.events[0]
    assert event.event_id.endswith("000042")
    assert event.source == "champion_shadow"
    assert event.asset == "tTESTBTC:TESTUSD"
    assert event.topic == "regime_shadow"
    assert event.signal_type == "decision_observation"
    assert event.confidence == 0.8
    assert event.summary


def test_run_backtest_main_writes_shadow_summary_without_changing_dummy_results(
    monkeypatch,
    tmp_path: Path,
) -> None:
    created_engines: list[_DummyEngine] = []

    def _pipeline_factory():
        return _DummyPipeline(created_engines)

    monkeypatch.setattr(run_backtest, "GenesisPipeline", _pipeline_factory)
    monkeypatch.setattr(run_backtest, "ConfigAuthority", lambda: _DummyAuthority())
    monkeypatch.setattr(
        run_backtest,
        "calculate_metrics",
        lambda results, prefer_summary=False: dict(results.get("metrics") or {}),
    )
    monkeypatch.setattr(run_backtest, "print_metrics_report", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        run_backtest,
        "score_backtest",
        lambda _results: {"score": 0.0, "metrics": {}, "hard_failures": []},
    )
    monkeypatch.setattr(run_backtest, "ROOT_DIR", tmp_path)

    control_argv = [
        "run_backtest.py",
        "--symbol",
        "tBTCUSD",
        "--timeframe",
        "1h",
        "--no-save",
    ]
    monkeypatch.setattr(sys, "argv", control_argv)
    control_code = run_backtest.main()
    control_engine = created_engines[-1]

    shadow_summary_path = (
        tmp_path / "results" / "intelligence_shadow" / "unit-run" / "shadow_summary.json"
    )
    shadow_argv = [
        "run_backtest.py",
        "--symbol",
        "tBTCUSD",
        "--timeframe",
        "1h",
        "--no-save",
        "--intelligence-shadow-out",
        str(shadow_summary_path),
    ]
    monkeypatch.setattr(sys, "argv", shadow_argv)
    shadow_code = run_backtest.main()
    shadow_engine = created_engines[-1]

    assert control_code == 0
    assert shadow_code == 0
    assert control_engine.last_result == shadow_engine.last_result
    assert control_engine.last_meta == shadow_engine.last_meta

    shadow_results_without_summary = dict(shadow_engine.last_results)
    shadow_summary_inline = shadow_results_without_summary.pop("intelligence_shadow")
    assert control_engine.last_results == shadow_results_without_summary
    assert shadow_summary_inline["decision_drift_observed"] is False

    summary = json.loads(shadow_summary_path.read_text(encoding="utf-8"))
    assert summary["shadow_status"] == "completed"
    assert summary["decision_drift_observed"] is False
    assert summary["derived_parameter_set"]["strategy_family"] == "legacy"
    assert summary["counts"]["captured_events"] == 1
    assert summary["counts"]["collected_events"] == 1
    assert (
        summary["top_advisory_parameter_set_id"]
        == summary["derived_parameter_set"]["parameter_set_id"]
    )
    assert (
        tmp_path / "artifacts" / "intelligence_shadow" / "unit-run" / "research_ledger"
    ).exists()
    assert summary["ledger_entity_ids"]
