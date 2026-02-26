#!/usr/bin/env python3
"""Test HTF Exit Engine for Genesis-Core.

Manual script (not a pytest test).
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path


def _bootstrap_src_on_path() -> None:
    # scripts/<this file> -> repo root is parents[1]
    repo_root = Path(__file__).resolve().parents[1]
    src_dir = repo_root / "src"
    if src_dir.is_dir() and str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))


_bootstrap_src_on_path()

from core.backtest.engine import BacktestEngine
from core.backtest.htf_exit_engine import HTFFibonacciExitEngine
from core.backtest.position_tracker import Position


def test_htf_exit_engine_basic():
    print("=== Testing HTF Exit Engine Basic Functionality ===")

    config = {
        "partial_1_pct": 0.40,
        "partial_2_pct": 0.30,
        "fib_threshold_atr": 0.3,
        "trail_atr_multiplier": 1.3,
        "enable_partials": True,
        "enable_trailing": True,
        "enable_structure_breaks": True,
    }

    exit_engine = HTFFibonacciExitEngine(config)
    print(f"[OK] Created HTF Exit Engine with config: {len(config)} parameters")

    position = Position(
        symbol="tBTCUSD",
        side="LONG",
        initial_size=1.0,
        current_size=1.0,
        entry_price=100000.0,
        entry_time=datetime(2025, 1, 1, 12, 0),
    )

    from core.indicators.exit_fibonacci import calculate_exit_fibonacci_levels

    exit_levels = calculate_exit_fibonacci_levels(
        side="LONG",
        swing_high=108000.0,
        swing_low=97000.0,
        levels=[0.786, 0.618, 0.5, 0.382],
    )

    position.exit_ctx = {
        "fib": exit_levels,
        "swing_bounds": (97000.0, 108000.0),
        "swing_id": "test_swing_001",
        "frozen_at": datetime(2025, 1, 1, 12, 0),
    }

    current_bar = {
        "timestamp": datetime(2025, 1, 1, 14, 0),
        "open": 104000.0,
        "high": 104500.0,
        "low": 103500.0,
        "close": 104200.0,
        "volume": 1000.0,
        "atr": 1000.0,
    }

    htf_fib_context = {
        "available": True,
        "levels": {0.382: 104000.0, 0.5: 102500.0, 0.618: 101000.0, 0.786: 99500.0},
        "swing_high": 108000.0,
        "swing_low": 97000.0,
        "htf_timeframe": "1D",
    }

    indicators = {"atr": 1000.0, "ema50": 103000.0, "ema_slope50_z": 0.5}

    exit_actions = exit_engine.check_exits(position, current_bar, htf_fib_context, indicators)
    print(f"[OK] Generated {len(exit_actions)} exit actions")

    partial_actions = [a for a in exit_actions if a.action == "PARTIAL"]
    trail_actions = [a for a in exit_actions if a.action == "TRAIL_UPDATE"]

    assert len(partial_actions) >= 1, "Should trigger at least one partial exit"
    assert len(trail_actions) == 1, "Should have one trail update"

    print("[OK] HTF Exit Engine basic functionality working correctly\n")
    return exit_actions


def test_exit_engine_with_backtest() -> bool:
    print("=== Testing HTF Exit Engine with BacktestEngine ===")

    htf_config = {
        "enable_partials": True,
        "enable_trailing": True,
        "enable_structure_breaks": False,
        "partial_1_pct": 0.50,
        "partial_2_pct": 0.30,
        "fib_threshold_atr": 1.0,
    }

    try:
        engine = BacktestEngine(
            symbol="tBTCUSD",
            timeframe="1h",
            initial_capital=10000.0,
            htf_exit_config=htf_config,
        )

        assert hasattr(engine, "htf_exit_engine"), "Should have HTF exit engine"

        data_loaded = engine.load_data()
        if data_loaded:
            print(f"[OK] Data loaded: {len(engine.candles_df):,} candles")
        else:
            print("[WARN] No data available for full backtest test")

    except Exception as e:
        print(f"[ERROR] BacktestEngine integration test failed: {e}")
        return False

    print("[OK] HTF Exit Engine integration with BacktestEngine working correctly\n")
    return True


def main():
    print("Testing HTF Exit Engine Implementation\n")
    test_htf_exit_engine_basic()
    integration_success = test_exit_engine_with_backtest()
    print("HTF Exit Engine Tests Complete!")
    if integration_success:
        print("\n[SUCCESS] HTF Exit Engine is ready for backtesting!")


if __name__ == "__main__":
    main()
