"""Tests for BacktestEngine evaluation_hook."""

import os

import pytest

from core.backtest.engine import BacktestEngine


@pytest.fixture
def engine_params():
    """Common engine parameters."""
    return {
        "symbol": "tBTCUSD",
        "timeframe": "1h",
        "start_date": "2024-01-01",
        "end_date": "2024-02-01",  # 1 month = ~720 bars > warmup
        "fast_window": True,
    }


class TestEvaluationHook:
    """Test evaluation_hook functionality."""

    def test_engine_without_hook_works(self, engine_params):
        """Test that engine works normally without hook."""
        os.environ["GENESIS_FAST_WINDOW"] = "1"
        os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"

        engine = BacktestEngine(**engine_params)
        assert engine.evaluation_hook is None

        # Should load and run without errors
        loaded = engine.load_data()
        if not loaded:
            pytest.skip("Data not available")

        results = engine.run()
        assert isinstance(results, dict)
        assert "summary" in results

    def test_hook_is_called(self, engine_params):
        """Test that hook is called during backtest."""
        os.environ["GENESIS_FAST_WINDOW"] = "1"
        os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"

        hook_calls = []

        def test_hook(result, meta, candles):
            hook_calls.append({"result": result, "meta": meta, "candles": candles})
            return result, meta

        engine = BacktestEngine(**engine_params, evaluation_hook=test_hook)

        loaded = engine.load_data()
        if not loaded:
            pytest.skip("Data not available")

        engine.run()

        # Hook should have been called at least once (after warmup)
        assert len(hook_calls) > 0
        assert "result" in hook_calls[0]
        assert "meta" in hook_calls[0]
        assert "candles" in hook_calls[0]

    def test_hook_can_modify_action(self, engine_params):
        """Test that hook can modify action to veto trades."""
        os.environ["GENESIS_FAST_WINDOW"] = "1"
        os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"

        def veto_all_hook(result, meta, candles):
            """Hook that vetos all trades."""
            result["action"] = "NONE"
            return result, meta

        engine_with_hook = BacktestEngine(**engine_params, evaluation_hook=veto_all_hook)
        engine_without_hook = BacktestEngine(**engine_params)

        for engine in [engine_with_hook, engine_without_hook]:
            loaded = engine.load_data()
            if not loaded:
                pytest.skip("Data not available")

        results_with_hook = engine_with_hook.run()
        engine_without_hook.run()  # Run but don't need results

        # Hook should reduce or eliminate trades
        trades_with_hook = results_with_hook.get("summary", {}).get("num_trades", 0)

        # With veto hook, should have 0 trades
        assert trades_with_hook == 0

    def test_hook_signature(self, engine_params):
        """Test hook receives correct arguments."""
        os.environ["GENESIS_FAST_WINDOW"] = "1"
        os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"

        received_args = {}

        def signature_test_hook(result, meta, candles):
            # Capture first call only
            if not received_args:
                received_args["result"] = result
                received_args["meta"] = meta
                received_args["candles"] = candles
            return result, meta

        engine = BacktestEngine(**engine_params, evaluation_hook=signature_test_hook)

        loaded = engine.load_data()
        if not loaded:
            pytest.skip("Data not available")

        engine.run()

        # Check that hook received valid arguments
        assert isinstance(received_args.get("result"), dict)
        assert isinstance(received_args.get("meta"), dict)
        assert isinstance(received_args.get("candles"), dict)

        # Result should have action
        assert "action" in received_args["result"]

        # Candles should have OHLC data
        candles = received_args["candles"]
        assert "close" in candles
        assert "open" in candles
        assert "high" in candles
        assert "low" in candles

    def test_hook_preserves_determinism(self, engine_params):
        """Test that identity hook produces same results as no hook."""
        os.environ["GENESIS_FAST_WINDOW"] = "1"
        os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"

        def identity_hook(result, meta, candles):
            """Hook that does nothing."""
            return result, meta

        engine_no_hook = BacktestEngine(**engine_params)
        engine_with_hook = BacktestEngine(**engine_params, evaluation_hook=identity_hook)

        for engine in [engine_no_hook, engine_with_hook]:
            loaded = engine.load_data()
            if not loaded:
                pytest.skip("Data not available")

        results_no_hook = engine_no_hook.run()
        results_with_hook = engine_with_hook.run()

        # Should produce identical results
        assert results_no_hook.get("summary", {}).get("num_trades") == results_with_hook.get(
            "summary", {}
        ).get("num_trades")

        assert results_no_hook.get("summary", {}).get("total_return") == results_with_hook.get(
            "summary", {}
        ).get("total_return")
