#!/usr/bin/env python3
"""
Test HTF Exit Engine for Genesis-Core

Verify that HTF Exit Engine integrates correctly with BacktestEngine
and executes HTF-based exit logic properly.
"""

import sys
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.backtest.engine import BacktestEngine
from core.backtest.htf_exit_engine import HTFFibonacciExitEngine
from core.backtest.position_tracker import Position


def test_htf_exit_engine_basic():
    """Test basic HTF Exit Engine functionality."""
    print("=== Testing HTF Exit Engine Basic Functionality ===")

    # Create exit engine with test config
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

    # Create test position with exit context
    position = Position(
        symbol="tBTCUSD",
        side="LONG",
        initial_size=1.0,
        current_size=1.0,
        entry_price=100000.0,
        entry_time=datetime(2025, 1, 1, 12, 0),
    )

    # Add exit context for HTF exit engine
    from core.indicators.exit_fibonacci import calculate_exit_fibonacci_levels

    exit_levels = calculate_exit_fibonacci_levels(
        side="LONG", swing_high=108000.0, swing_low=97000.0, levels=[0.786, 0.618, 0.5, 0.382]
    )

    position.exit_ctx = {
        "fib": exit_levels,
        "swing_bounds": (97000.0, 108000.0),
        "swing_id": "test_swing_001",
        "frozen_at": datetime(2025, 1, 1, 12, 0),
    }

    # Test current bar data
    current_bar = {
        "timestamp": datetime(2025, 1, 1, 14, 0),
        "open": 104000.0,
        "high": 104500.0,
        "low": 103500.0,
        "close": 104200.0,  # Near 0.382 Fib level
        "volume": 1000.0,
        "atr": 1000.0,
    }

    # Test HTF Fibonacci context
    htf_fib_context = {
        "available": True,
        "levels": {
            0.382: 104000.0,  # Close to current price
            0.5: 102500.0,
            0.618: 101000.0,
            0.786: 99500.0,
        },
        "swing_high": 108000.0,
        "swing_low": 97000.0,
        "htf_timeframe": "1D",
    }

    # Test indicators
    indicators = {
        "atr": 1000.0,
        "ema50": 103000.0,
        "ema_slope50_z": 0.5,  # Positive momentum
    }

    # Check exit conditions
    exit_actions = exit_engine.check_exits(position, current_bar, htf_fib_context, indicators)

    print(f"[OK] Generated {len(exit_actions)} exit actions")

    # Verify partial exit was triggered
    partial_actions = [a for a in exit_actions if a.action == "PARTIAL"]
    trail_actions = [a for a in exit_actions if a.action == "TRAIL_UPDATE"]

    assert len(partial_actions) >= 1, "Should trigger at least one partial exit"
    assert len(trail_actions) == 1, "Should have one trail update"

    for action in exit_actions:
        if action.action == "PARTIAL":
            print(f"   Partial Exit: {action.reason} - Size: {action.size:.2f}")
            assert action.reason in ["TP1_0382", "TP2_05"], "Should have valid exit reason"
            assert action.size > 0, "Partial size should be positive"

        elif action.action == "TRAIL_UPDATE":
            print(f"   Trail Update: Stop @ ${action.stop_price:,.0f}")
            assert action.stop_price > 0, "Trail stop should be positive"

    print("[OK] HTF Exit Engine basic functionality working correctly\n")
    return exit_actions


def test_htf_context_fallback():
    """Test fallback behavior when HTF context unavailable."""
    print("=== Testing HTF Context Fallback ===")

    config = {"enable_partials": True, "enable_trailing": True}
    exit_engine = HTFFibonacciExitEngine(config)

    # Create test position
    position = Position(
        symbol="tBTCUSD",
        side="LONG",
        initial_size=1.0,
        current_size=1.0,
        entry_price=100000.0,
        entry_time=datetime(2025, 1, 1, 12, 0),
    )

    current_bar = {"close": 105000.0, "atr": 1000.0}

    # No HTF context available
    htf_fib_context = {"available": False, "reason": "HTF_DATA_NOT_FOUND"}

    indicators = {
        "atr": 1000.0,
        "ema50": 104000.0,
        "ema_slope50_z": 0.0,
    }

    # Should fall back to basic trailing
    exit_actions = exit_engine.check_exits(position, current_bar, htf_fib_context, indicators)

    assert len(exit_actions) == 1, "Should have fallback trail action"
    assert exit_actions[0].action == "TRAIL_UPDATE", "Should be trail update"
    assert exit_actions[0].reason == "FALLBACK_TRAIL", "Should indicate fallback"

    print(f"[OK] Fallback trail stop: ${exit_actions[0].stop_price:,.0f}")
    print("[OK] HTF context fallback working correctly\n")


def test_structure_break_detection():
    """Test structure break detection for full exits."""
    print("=== Testing Structure Break Detection ===")

    config = {"enable_structure_breaks": True}
    exit_engine = HTFFibonacciExitEngine(config)

    # Create LONG position with exit context
    position = Position(
        symbol="tBTCUSD",
        side="LONG",
        initial_size=1.0,
        current_size=0.6,  # Already had partial exits
        entry_price=100000.0,
        entry_time=datetime(2025, 1, 1, 12, 0),
    )

    # Add exit context for structure break detection
    from core.indicators.exit_fibonacci import calculate_exit_fibonacci_levels

    exit_levels = calculate_exit_fibonacci_levels(
        side="LONG", swing_high=108000.0, swing_low=97000.0, levels=[0.786, 0.618, 0.5, 0.382]
    )

    position.exit_ctx = {
        "fib": exit_levels,
        "swing_bounds": (97000.0, 108000.0),
        "swing_id": "test_swing_002",
        "frozen_at": datetime(2025, 1, 1, 12, 0),
    }

    current_bar = {
        "timestamp": datetime(2025, 1, 1, 16, 0),
        "open": 100800.0,
        "high": 100900.0,
        "low": 100200.0,
        "close": 100500.0,  # Below 0.618 Fib level (101000)
        "volume": 1000.0,
        "atr": 1000.0,
    }

    htf_fib_context = {
        "available": True,
        "levels": {
            0.382: 104000.0,
            0.5: 102500.0,
            0.618: 101000.0,  # Current price below this
            0.786: 99500.0,
        },
    }

    indicators = {
        "atr": 1000.0,
        "ema50": 101500.0,
        "ema_slope50_z": -0.8,  # Strong negative momentum
    }

    exit_actions = exit_engine.check_exits(position, current_bar, htf_fib_context, indicators)

    # Should trigger structure break
    structure_breaks = [a for a in exit_actions if a.action == "FULL_EXIT"]
    assert len(structure_breaks) == 1, "Should trigger structure break"
    assert structure_breaks[0].reason == "STRUCTURE_BREAK_DOWN", "Should be downward break"

    print(f"[OK] Structure break detected: {structure_breaks[0].reason}")
    print("[OK] Structure break detection working correctly\n")


def test_exit_engine_with_backtest():
    """Test HTF Exit Engine integration with BacktestEngine."""
    print("=== Testing HTF Exit Engine with BacktestEngine ===")

    # Create backtest engine with HTF exit config
    htf_config = {
        "enable_partials": True,
        "enable_trailing": True,
        "enable_structure_breaks": False,  # Disable for cleaner test
        "partial_1_pct": 0.50,  # 50% at TP1
        "partial_2_pct": 0.30,  # 30% at TP2
        "fib_threshold_atr": 1.0,  # More lenient for test data
    }

    try:
        # Initialize backtest engine
        engine = BacktestEngine(
            symbol="tBTCUSD", timeframe="1h", initial_capital=10000.0, htf_exit_config=htf_config
        )

        print("[OK] BacktestEngine initialized with HTF Exit Engine")
        print(f"   HTF Config: {len(htf_config)} parameters")
        print(f"   Partial 1: {htf_config['partial_1_pct']:.0%}")
        print(f"   Partial 2: {htf_config['partial_2_pct']:.0%}")

        # Verify HTF exit engine was created
        assert hasattr(engine, "htf_exit_engine"), "Should have HTF exit engine"
        assert hasattr(engine, "htf_exit_config"), "Should have HTF config"

        htf_engine = engine.htf_exit_engine
        assert htf_engine.partial_1_pct == 0.50, "Should use configured partial 1%"
        assert htf_engine.partial_2_pct == 0.30, "Should use configured partial 2%"
        assert htf_engine.enable_partials, "Should enable partials"

        print("[OK] HTF Exit Engine configuration verified")

        # Test that data loading works
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


def test_exit_tracking():
    """Test that exits are properly tracked to avoid double-triggering."""
    print("=== Testing Exit Tracking ===")

    config = {"enable_partials": True}
    exit_engine = HTFFibonacciExitEngine(config)

    position = Position(
        symbol="tBTCUSD",
        side="LONG",
        initial_size=1.0,
        current_size=1.0,
        entry_price=100000.0,
        entry_time=datetime(2025, 1, 1, 12, 0),
    )

    current_bar = {"close": 104000.0, "atr": 1000.0}  # At 0.382 level

    htf_fib_context = {
        "available": True,
        "levels": {0.382: 104000.0, 0.5: 102500.0, 0.618: 101000.0},
    }

    indicators = {"atr": 1000.0, "ema50": 103000.0, "ema_slope50_z": 0.0}

    # First call - should trigger TP1
    actions_1 = exit_engine.check_exits(position, current_bar, htf_fib_context, indicators)
    tp1_actions_1 = [a for a in actions_1 if "TP1" in a.reason]

    # Second call - should NOT trigger TP1 again
    actions_2 = exit_engine.check_exits(position, current_bar, htf_fib_context, indicators)
    tp1_actions_2 = [a for a in actions_2 if "TP1" in a.reason]

    assert len(tp1_actions_1) == 1, "Should trigger TP1 first time"
    assert len(tp1_actions_2) == 0, "Should NOT trigger TP1 second time"

    print("[OK] Exit tracking prevents double-triggering")

    # Cleanup
    position_id = f"{position.symbol}_{position.entry_time.isoformat()}"
    exit_engine.cleanup_position(position_id)

    print("[OK] Exit tracking working correctly\n")


def main():
    """Run all HTF Exit Engine tests."""
    print("Testing HTF Exit Engine Implementation\n")

    # Test 1: Basic functionality
    test_htf_exit_engine_basic()

    # Test 2: Fallback behavior
    test_htf_context_fallback()

    # Test 3: Structure break detection
    test_structure_break_detection()

    # Test 4: BacktestEngine integration
    integration_success = test_exit_engine_with_backtest()

    # Test 5: Exit tracking
    test_exit_tracking()

    print("HTF Exit Engine Tests Complete!")
    print("\nNext Steps:")
    print("1. [DONE] Phase 0A: HTF Fibonacci Mapping")
    print("2. [DONE] Phase 0B: Partial Exit Infrastructure")
    print("3. [DONE] Phase 1: HTF Exit Engine")
    print("4. [TODO] Phase 2: Ablation Study & Validation")

    if integration_success:
        print("\n[SUCCESS] HTF Exit Engine is ready for backtesting!")
        print("Ready to run ablation studies comparing:")
        print("- BASELINE: Fixed exits (TP/SL/TIME)")
        print("- PARTIAL_ONLY: HTF partials without trailing")
        print("- TRAIL_ONLY: HTF trailing without partials")
        print("- FULL_HTF: Complete HTF exit system")
    else:
        print("\n[WARNING] Integration issues detected - resolve before ablation study")


if __name__ == "__main__":
    main()
