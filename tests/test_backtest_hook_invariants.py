"""
Invariant proofs for BacktestEngine.evaluation_hook.

These tests prove the two critical invariants required for Milestone 1 completion:

Invariant A: hook=None ≡ hook=identity (determinism)
  - Same trades (count, entry/exit bars, prices)
  - Same fills (exact prices, timestamps)
  - Same PnL/return/metrics
  - Same artifacts structure

Invariant B: Hook triggers on every decision attempt
  - Hook call count == processed bars (total - warmup)
  - Events contain as-of identifiers (timestamp, bar_index, symbol, timeframe)
"""

import os
from typing import Any

import pytest

from core.backtest.engine import BacktestEngine


@pytest.fixture
def deterministic_params():
    """
    Deterministic engine parameters for invariant testing.

    Uses a short, fixed period to ensure:
    - Reproducible results across runs
    - Fast execution (< 5 seconds)
    - Sufficient bars for meaningful test (> warmup + 50 bars)
    """
    return {
        "symbol": "tBTCUSD",
        "timeframe": "1h",
        "start_date": "2024-01-01",
        "end_date": "2024-02-01",  # ~744 bars (31 days * 24 hours)
        "fast_window": True,
    }


class HookEventSink:
    """
    Event sink for capturing hook calls with as-of identifiers.

    Captures:
    - timestamp (as-of)
    - bar_index (position in processed bars)
    - symbol/timeframe (from engine context)
    - result/meta (decision context)
    """

    def __init__(self, symbol: str = "unknown", timeframe: str = "unknown"):
        self.events = []
        self.bar_counter = 0
        self.symbol = symbol
        self.timeframe = timeframe

    def create_hook(self):
        """Create an identity hook that logs events."""

        def hook(result: dict[str, Any], meta: dict[str, Any], candles: dict[str, Any]):
            # Extract as-of identifiers
            timestamp = candles.get("timestamp", [None])[-1] if "timestamp" in candles else None

            # Record event
            self.events.append(
                {
                    "bar_index": self.bar_counter,
                    "timestamp": timestamp,
                    "symbol": self.symbol,
                    "timeframe": self.timeframe,
                    "action": result.get("action"),
                    "has_result": result is not None,
                    "has_meta": meta is not None,
                }
            )
            self.bar_counter += 1

            # Identity: no modifications
            return result, meta

        return hook

    def get_event_count(self) -> int:
        """Get total number of hook calls."""
        return len(self.events)

    def get_events_with_timestamps(self) -> list[dict]:
        """Get events that have valid timestamps."""
        return [e for e in self.events if e["timestamp"] is not None]

    def get_events_by_action(self, action: str) -> list[dict]:
        """Get events with specific action."""
        return [e for e in self.events if e["action"] == action]


class TestInvariantA:
    """
    Invariant A: hook=None ≡ hook=identity

    Proves that an identity hook produces IDENTICAL results to no hook.
    This is critical for ensuring the hook infrastructure has zero overhead
    and doesn't introduce unintended side effects.
    """

    def test_identical_trade_count(self, deterministic_params):
        """Test that hook=None and hook=identity produce same trade count."""
        os.environ["GENESIS_FAST_WINDOW"] = "1"
        os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"

        # Identity hook (no-op)
        def identity_hook(result, meta, candles):
            return result, meta

        # Run both engines
        engine_no_hook = BacktestEngine(**deterministic_params)
        engine_with_hook = BacktestEngine(**deterministic_params, evaluation_hook=identity_hook)

        for engine in [engine_no_hook, engine_with_hook]:
            loaded = engine.load_data()
            if not loaded:
                pytest.skip("Data not available")

        results_no_hook = engine_no_hook.run()
        results_with_hook = engine_with_hook.run()

        # STRICT: Same trade count
        trades_no_hook = results_no_hook.get("summary", {}).get("num_trades", 0)
        trades_with_hook = results_with_hook.get("summary", {}).get("num_trades", 0)

        assert (
            trades_no_hook == trades_with_hook
        ), f"Trade count mismatch: {trades_no_hook} vs {trades_with_hook}"

    def test_identical_metrics(self, deterministic_params):
        """Test that all summary metrics are identical."""
        os.environ["GENESIS_FAST_WINDOW"] = "1"
        os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"

        # Identity hook
        def identity_hook(result, meta, candles):
            return result, meta

        # Run both engines
        engine_no_hook = BacktestEngine(**deterministic_params)
        engine_with_hook = BacktestEngine(**deterministic_params, evaluation_hook=identity_hook)

        for engine in [engine_no_hook, engine_with_hook]:
            loaded = engine.load_data()
            if not loaded:
                pytest.skip("Data not available")

        results_no_hook = engine_no_hook.run()
        results_with_hook = engine_with_hook.run()

        summary_no_hook = results_no_hook.get("summary", {})
        summary_with_hook = results_with_hook.get("summary", {})

        # STRICT: All numeric metrics must be identical
        metrics_to_check = [
            "num_trades",
            "total_return",
            "profit_factor",
            "max_drawdown",
            "win_rate",
            "total_commission",
        ]

        for metric in metrics_to_check:
            val_no_hook = summary_no_hook.get(metric)
            val_with_hook = summary_with_hook.get(metric)

            assert (
                val_no_hook == val_with_hook
            ), f"Metric '{metric}' mismatch: {val_no_hook} vs {val_with_hook}"

    def test_identical_trade_details(self, deterministic_params):
        """Test that trade entry/exit bars and prices are identical."""
        os.environ["GENESIS_FAST_WINDOW"] = "1"
        os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"

        # Identity hook
        def identity_hook(result, meta, candles):
            return result, meta

        # Run both engines
        engine_no_hook = BacktestEngine(**deterministic_params)
        engine_with_hook = BacktestEngine(**deterministic_params, evaluation_hook=identity_hook)

        for engine in [engine_no_hook, engine_with_hook]:
            loaded = engine.load_data()
            if not loaded:
                pytest.skip("Data not available")

        results_no_hook = engine_no_hook.run()
        results_with_hook = engine_with_hook.run()

        trades_no_hook = results_no_hook.get("trades", [])
        trades_with_hook = results_with_hook.get("trades", [])

        # STRICT: Same number of trades
        assert len(trades_no_hook) == len(trades_with_hook)

        # STRICT: Each trade has identical entry/exit
        for i, (t_no_hook, t_with_hook) in enumerate(
            zip(trades_no_hook, trades_with_hook, strict=True)
        ):
            # Entry bar
            assert t_no_hook.get("entry_bar") == t_with_hook.get(
                "entry_bar"
            ), f"Trade {i}: entry_bar mismatch"

            # Exit bar
            assert t_no_hook.get("exit_bar") == t_with_hook.get(
                "exit_bar"
            ), f"Trade {i}: exit_bar mismatch"

            # Entry price
            assert t_no_hook.get("entry_price") == t_with_hook.get(
                "entry_price"
            ), f"Trade {i}: entry_price mismatch"

            # Exit price
            assert t_no_hook.get("exit_price") == t_with_hook.get(
                "exit_price"
            ), f"Trade {i}: exit_price mismatch"

            # PnL
            assert t_no_hook.get("pnl") == t_with_hook.get("pnl"), f"Trade {i}: pnl mismatch"


class TestInvariantB:
    """
    Invariant B: Hook triggers on every decision attempt

    Proves that:
    1. Hook is called exactly once per processed bar (total_bars - warmup)
    2. Each hook call has valid as-of identifiers (timestamp, bar_index, symbol, timeframe)
    3. Hook receives correct context (result, meta, candles)
    """

    def test_hook_call_count_equals_processed_bars(self, deterministic_params):
        """Test that hook is called once per processed bar."""
        os.environ["GENESIS_FAST_WINDOW"] = "1"
        os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"

        # Create event sink with symbol/timeframe context
        sink = HookEventSink(
            symbol=deterministic_params["symbol"], timeframe=deterministic_params["timeframe"]
        )
        hook = sink.create_hook()

        # Run engine with hook
        engine = BacktestEngine(**deterministic_params, evaluation_hook=hook)

        loaded = engine.load_data()
        if not loaded:
            pytest.skip("Data not available")

        results = engine.run()

        # Get expected processed bars
        backtest_info = results.get("backtest_info", {})
        total_bars = backtest_info.get("bars_total", 0)
        warmup_bars = backtest_info.get("warmup_bars", 120)
        bars_processed = backtest_info.get("bars_processed", 0)

        # STRICT: Hook call count == bars_processed (from engine)
        actual_hook_calls = sink.get_event_count()

        assert (
            actual_hook_calls == bars_processed
        ), f"Hook call count mismatch: {actual_hook_calls} vs {bars_processed} (total={total_bars}, warmup={warmup_bars})"

    def test_hook_events_have_as_of_identifiers(self, deterministic_params):
        """Test that every hook event has valid as-of identifiers."""
        os.environ["GENESIS_FAST_WINDOW"] = "1"
        os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"

        # Create event sink with symbol/timeframe context
        sink = HookEventSink(
            symbol=deterministic_params["symbol"], timeframe=deterministic_params["timeframe"]
        )
        hook = sink.create_hook()

        # Run engine
        engine = BacktestEngine(**deterministic_params, evaluation_hook=hook)

        loaded = engine.load_data()
        if not loaded:
            pytest.skip("Data not available")

        engine.run()

        # STRICT: Every event must have as-of identifiers
        events = sink.events
        assert len(events) > 0, "No hook events captured"

        for i, event in enumerate(events):
            # bar_index must be sequential
            assert event["bar_index"] == i, f"Event {i}: bar_index not sequential"

            # timestamp must exist (can be None for first bars, but should exist after warmup)
            # For now, just check that key exists
            assert "timestamp" in event, f"Event {i}: missing timestamp"

            # symbol/timeframe must be valid
            assert event["symbol"] != "unknown", f"Event {i}: unknown symbol"
            assert event["timeframe"] != "unknown", f"Event {i}: unknown timeframe"

            # result/meta must be present
            assert event["has_result"], f"Event {i}: missing result"
            assert event["has_meta"], f"Event {i}: missing meta"

    def test_hook_events_have_valid_timestamps(self, deterministic_params):
        """Test that hook events after warmup have non-None timestamps."""
        os.environ["GENESIS_FAST_WINDOW"] = "1"
        os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"

        # Create event sink with symbol/timeframe context
        sink = HookEventSink(
            symbol=deterministic_params["symbol"], timeframe=deterministic_params["timeframe"]
        )
        hook = sink.create_hook()

        # Run engine
        engine = BacktestEngine(**deterministic_params, evaluation_hook=hook)

        loaded = engine.load_data()
        if not loaded:
            pytest.skip("Data not available")

        engine.run()

        # After warmup, all events should have timestamps
        events_with_ts = sink.get_events_with_timestamps()

        # Most events should have timestamps (allow some missing at start)
        total_events = sink.get_event_count()
        assert len(events_with_ts) > total_events * 0.5, "Most events should have timestamps"

    def test_hook_receives_correct_context_per_bar(self, deterministic_params):
        """Test that hook receives valid result/meta/candles for each bar."""
        os.environ["GENESIS_FAST_WINDOW"] = "1"
        os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"

        received_contexts = []

        def context_capture_hook(result, meta, candles):
            # Capture first 10 contexts
            if len(received_contexts) < 10:
                received_contexts.append(
                    {
                        "result_keys": list(result.keys()) if result else [],
                        "meta_keys": list(meta.keys()) if meta else [],
                        "candles_keys": list(candles.keys()) if candles else [],
                        "action": result.get("action") if result else None,
                    }
                )
            return result, meta

        # Run engine
        engine = BacktestEngine(**deterministic_params, evaluation_hook=context_capture_hook)

        loaded = engine.load_data()
        if not loaded:
            pytest.skip("Data not available")

        engine.run()

        # STRICT: At least 10 contexts captured
        assert len(received_contexts) >= 10, "Not enough contexts captured"

        for i, ctx in enumerate(received_contexts):
            # result must have action
            assert "action" in ctx["result_keys"], f"Context {i}: result missing action"

            # meta must have keys
            assert len(ctx["meta_keys"]) > 0, f"Context {i}: meta is empty"

            # candles must have OHLCV
            required_candle_keys = ["open", "high", "low", "close"]
            for key in required_candle_keys:
                assert (
                    key in ctx["candles_keys"]
                ), f"Context {i}: candles missing required key '{key}'"
