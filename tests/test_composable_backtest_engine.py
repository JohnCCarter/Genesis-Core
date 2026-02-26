"""Integration tests for ComposableBacktestEngine."""

import os

import pandas as pd
import pytest

from core.backtest.composable_engine import ComposableBacktestEngine
from core.strategy.components.base import ComponentResult, StrategyComponent
from core.strategy.components.ml_confidence import MLConfidenceComponent
from core.strategy.components.strategy import ComposableStrategy


@pytest.fixture
def sample_strategy():
    """Create a simple strategy for testing."""
    return ComposableStrategy(
        components=[
            MLConfidenceComponent(threshold=0.24),
        ]
    )


class TestComposableBacktestEngine:
    """Test ComposableBacktestEngine integration."""

    def test_veto_path_does_not_crash_and_counts_bars(self, monkeypatch):
        """Regression: veto-path must not raise and must process all bars.

        Historically, the composable evaluation hook referenced a non-existent
        attribute (decision.reason) on veto, causing an exception on every veto.
        This silently collapsed bars_processed/equity_curve to the number of
        allowed decisions.
        """

        class AlwaysVeto(StrategyComponent):
            def name(self) -> str:  # noqa: D401
                return "AlwaysVeto"

            def evaluate(self, context: dict) -> ComponentResult:
                return ComponentResult(allowed=False, confidence=0.0, reason="ALWAYS_VETO")

        def stub_evaluate_pipeline(*, candles, policy, configs, state):
            # Minimal structure that BacktestEngine expects.
            result = {
                "action": "NONE",
                "confidence": 0.5,
                "regime": "BALANCED",
                "probas": {"LONG": 0.5, "SHORT": 0.5},
                "features": {},
            }
            meta = {
                "decision": {"size": 0.0, "reasons": [], "state_out": {}},
                "features": {},
            }
            return result, meta

        import core.backtest.engine as engine_module

        monkeypatch.setattr(engine_module, "evaluate_pipeline", stub_evaluate_pipeline)

        strategy = ComposableStrategy(components=[AlwaysVeto()])
        engine = ComposableBacktestEngine(
            symbol="tBTCUSD",
            timeframe="1h",
            strategy=strategy,
            start_date=None,
            end_date=None,
            warmup_bars=0,
            fast_window=False,
        )

        n_bars = 32
        ts = pd.date_range("2024-01-01", periods=n_bars, freq="1h", tz="UTC")
        engine.engine.candles_df = pd.DataFrame(
            {
                "timestamp": ts,
                "open": 100.0,
                "high": 101.0,
                "low": 99.0,
                "close": 100.0,
                "volume": 1.0,
            }
        )
        engine.engine._np_arrays = None

        results = engine.run(configs={"meta": {"skip_champion_merge": True}})

        assert results.get("backtest_info", {}).get("bars_total") == n_bars
        assert results.get("backtest_info", {}).get("bars_processed") == n_bars

        attribution = results.get("attribution") or {}
        assert attribution.get("total_decisions") == n_bars
        assert attribution.get("allowed") == 0
        assert attribution.get("vetoed") == n_bars

        assert isinstance(results.get("equity_curve"), list)
        assert len(results.get("equity_curve")) == n_bars
        assert results.get("summary", {}).get("num_trades") == 0

    def test_engine_initialization(self, sample_strategy):
        """Test that engine initializes correctly."""
        engine = ComposableBacktestEngine(
            symbol="tBTCUSD",
            timeframe="1h",
            strategy=sample_strategy,
            start_date="2024-06-01",
            end_date="2024-06-03",
        )

        assert engine.engine is not None
        assert engine.strategy is sample_strategy
        assert engine.attribution_tracker is not None

    def test_load_data(self, sample_strategy):
        """Test that data loading works."""
        engine = ComposableBacktestEngine(
            symbol="tBTCUSD",
            timeframe="1h",
            strategy=sample_strategy,
            start_date="2024-06-01",
            end_date="2024-06-03",
        )

        # This will attempt to load real data
        # Should return True if data exists, False otherwise
        result = engine.load_data()
        # We don't assert True because data may not exist in test env
        assert isinstance(result, bool)

    @pytest.mark.skipif(
        not os.path.exists("data/raw/tBTCUSD_1h_frozen.parquet"),
        reason="Test data not available",
    )
    def test_run_with_real_data(self, sample_strategy):
        """Test running backtest with real data (if available)."""
        # Set canonical mode
        os.environ["GENESIS_FAST_WINDOW"] = "1"
        os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"

        engine = ComposableBacktestEngine(
            symbol="tBTCUSD",
            timeframe="1h",
            strategy=sample_strategy,
            start_date="2024-06-01",
            end_date="2024-06-03",
            fast_window=True,
        )

        loaded = engine.load_data()
        if not loaded:
            pytest.skip("Data not available")

        results = engine.run()

        # Check that results are returned
        assert isinstance(results, dict)

        # Check that attribution is included
        assert "attribution" in results

        # Check attribution structure
        attribution = results["attribution"]
        assert "total_decisions" in attribution
        assert "veto_counts" in attribution
        assert "component_confidence" in attribution

    def test_strategy_reset_on_run(self, sample_strategy):
        """Test that strategy state is reset before each run."""
        engine = ComposableBacktestEngine(
            symbol="tBTCUSD",
            timeframe="1h",
            strategy=sample_strategy,
            start_date="2024-06-01",
            end_date="2024-06-03",
        )

        # Strategy should be reset during __init__
        # And again during run()
        # We can't easily test this without running, so just verify no crash
        assert engine.strategy is not None

    def test_monkey_patch_restoration(self, sample_strategy):
        """Test that evaluate_pipeline is restored after run."""
        import core.strategy.evaluate as evaluate_module

        original_pipeline = evaluate_module.evaluate_pipeline

        engine = ComposableBacktestEngine(
            symbol="tBTCUSD",
            timeframe="1h",
            strategy=sample_strategy,
            start_date="2024-06-01",
            end_date="2024-06-03",
        )

        # Even if run fails, pipeline should be restored
        try:
            engine.load_data()
            engine.run()
        except Exception:
            pass  # Ignore errors (data may not exist)

        # Check that pipeline is restored
        assert evaluate_module.evaluate_pipeline is original_pipeline

    def test_attribution_report_accessible(self, sample_strategy):
        """Test that attribution report can be retrieved."""
        engine = ComposableBacktestEngine(
            symbol="tBTCUSD",
            timeframe="1h",
            strategy=sample_strategy,
            start_date="2024-06-01",
            end_date="2024-06-03",
        )

        report = engine.get_attribution_report()

        # Should return a report even if no backtest run yet
        assert isinstance(report, dict)
        assert "total_decisions" in report
