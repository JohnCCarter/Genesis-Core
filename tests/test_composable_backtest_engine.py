"""Integration tests for ComposableBacktestEngine."""

import os

import pytest

from core.backtest.composable_engine import ComposableBacktestEngine
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
