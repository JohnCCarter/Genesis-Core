#!/usr/bin/env python3
"""
Unit Tests för Exit Fibonacci Calculator

Testar symmetrisk Fibonacci-logik för exit-nivåer.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.indicators.exit_fibonacci import (
    calculate_exit_fibonacci_levels,
    calculate_swing_improvement,
    get_next_exit_level,
    validate_swing_for_exit,
)


def test_calculate_exit_fibonacci_levels_long():
    """Test LONG exit level calculation."""
    print("\n=== TEST: LONG Exit Levels ===")

    swing_high = 115_000
    swing_low = 98_000
    range_size = 17_000

    levels = calculate_exit_fibonacci_levels(
        side="LONG", swing_high=swing_high, swing_low=swing_low
    )

    # Verify calculations (from high downward)
    expected = {
        0.382: swing_high - 0.382 * range_size,  # 108,506
        0.5: swing_high - 0.500 * range_size,  # 106,500
        0.618: swing_high - 0.618 * range_size,  # 104,494
    }

    print(f"Swing: {swing_low:,.0f} -> {swing_high:,.0f} (range: {range_size:,.0f})")
    print("\nCalculated exit levels (retracement från high):")
    for level in sorted(levels.keys()):
        calculated = levels[level]
        expected_val = expected[level]
        diff = abs(calculated - expected_val)
        status = "[OK]" if diff < 1.0 else "[FAIL]"
        print(f"  {level:.3f}: ${calculated:,.0f} (expected: ${expected_val:,.0f}) {status}")

    # Assertions
    for level in expected:
        assert (
            abs(levels[level] - expected[level]) < 1.0
        ), f"Level {level} mismatch: {levels[level]} vs {expected[level]}"

    print("\n[PASS] LONG exit levels korrekt beräknade")
    return True


def test_calculate_exit_fibonacci_levels_short():
    """Test SHORT exit level calculation."""
    print("\n=== TEST: SHORT Exit Levels ===")

    swing_high = 115_000
    swing_low = 98_000
    range_size = 17_000

    levels = calculate_exit_fibonacci_levels(
        side="SHORT", swing_high=swing_high, swing_low=swing_low
    )

    # Verify calculations (from low upward)
    expected = {
        0.382: swing_low + 0.382 * range_size,  # 104,494
        0.5: swing_low + 0.500 * range_size,  # 106,500
        0.618: swing_low + 0.618 * range_size,  # 108,506
    }

    print(f"Swing: {swing_low:,.0f} -> {swing_high:,.0f} (range: {range_size:,.0f})")
    print("\nCalculated exit levels (retracement från low):")
    for level in sorted(levels.keys()):
        calculated = levels[level]
        expected_val = expected[level]
        diff = abs(calculated - expected_val)
        status = "[OK]" if diff < 1.0 else "[FAIL]"
        print(f"  {level:.3f}: ${calculated:,.0f} (expected: ${expected_val:,.0f}) {status}")

    # Assertions
    for level in expected:
        assert (
            abs(levels[level] - expected[level]) < 1.0
        ), f"Level {level} mismatch: {levels[level]} vs {expected[level]}"

    print("\n[PASS] SHORT exit levels korrekt beräknade")
    return True


def test_validate_swing_for_exit():
    """Test swing validation logic."""
    print("\n=== TEST: Swing Validation ===")

    # Test 1: Valid swing
    swing_high = 115_000
    swing_low = 98_000
    is_valid, reason = validate_swing_for_exit(
        swing_high=swing_high,
        swing_low=swing_low,
        current_price=110_000,
        current_atr=500,
        min_swing_size_atr=3.0,
        max_distance_atr=40.0,  # Increased - distance to high is 5k/500 = 10 ATR
    )
    print(f"\nTest 1 - Valid swing: {is_valid} ({reason})")
    assert is_valid and reason == "OK", f"Expected valid, got: {reason}"

    # Test 2: Swing too small
    is_valid, reason = validate_swing_for_exit(
        swing_high=115_000,
        swing_low=114_000,  # Only 1k range
        current_price=114_500,
        current_atr=500,  # 1k/500 = 2 ATR (less than min 3 ATR)
        min_swing_size_atr=3.0,
    )
    print(f"Test 2 - Swing too small: {is_valid} ({reason})")
    assert not is_valid and "SWING_TOO_SMALL" in reason

    # Test 3: Swing too far from price
    is_valid, reason = validate_swing_for_exit(
        swing_high=115_000,
        swing_low=98_000,
        current_price=200_000,  # Very far from swing
        current_atr=500,
        max_distance_atr=8.0,
    )
    print(f"Test 3 - Swing too far: {is_valid} ({reason})")
    assert not is_valid and "SWING_TOO_FAR" in reason

    # Test 4: Invalid swing order
    is_valid, reason = validate_swing_for_exit(
        swing_high=98_000,  # High is lower than low!
        swing_low=115_000,
        current_price=110_000,
        current_atr=500,
    )
    print(f"Test 4 - Invalid swing order: {is_valid} ({reason})")
    assert not is_valid and reason == "INVALID_SWING_ORDER"

    print("\n[PASS] Swing validation working correctly")
    return True


def test_calculate_swing_improvement():
    """Test swing improvement calculation."""
    print("\n=== TEST: Swing Improvement ===")

    # Test 1: LONG - Higher high is better
    improvement = calculate_swing_improvement(
        old_swing_high=110_000,
        old_swing_low=95_000,
        new_swing_high=115_000,  # +5k improvement
        new_swing_low=98_000,
        side="LONG",
    )
    expected = 5_000 / 110_000  # ~4.5%
    print(f"\nTest 1 - LONG improvement: {improvement:.2%} (expected: {expected:.2%})")
    assert abs(improvement - expected) < 0.001

    # Test 2: LONG - Lower high is worse
    improvement = calculate_swing_improvement(
        old_swing_high=115_000,
        old_swing_low=98_000,
        new_swing_high=110_000,  # -5k (worse)
        new_swing_low=95_000,
        side="LONG",
    )
    expected = -5_000 / 115_000  # ~-4.3%
    print(f"Test 2 - LONG degradation: {improvement:.2%} (expected: {expected:.2%})")
    assert abs(improvement - expected) < 0.001

    # Test 3: SHORT - Lower low is better
    improvement = calculate_swing_improvement(
        old_swing_high=115_000,
        old_swing_low=100_000,
        new_swing_high=118_000,
        new_swing_low=95_000,  # -5k improvement for SHORT
        side="SHORT",
    )
    expected = 5_000 / 100_000  # 5%
    print(f"Test 3 - SHORT improvement: {improvement:.2%} (expected: {expected:.2%})")
    assert abs(improvement - expected) < 0.001

    print("\n[PASS] Swing improvement calculation correct")
    return True


def test_get_next_exit_level():
    """Test next exit level selection."""
    print("\n=== TEST: Next Exit Level ===")

    exit_levels = {0.382: 108_500, 0.5: 106_500, 0.618: 104_500}

    # Test 1: LONG - Price above all levels
    current_price = 110_000
    triggered = set()

    next_level, next_price = get_next_exit_level(
        exit_levels=exit_levels,
        current_price=current_price,
        side="LONG",
        triggered_levels=triggered,
    )

    print(f"\nTest 1 - LONG, price above all: Next = {next_level} @ ${next_price:,.0f}")
    assert (
        next_level == 0.382 and next_price == 108_500
    ), f"Expected 0.382 @ 108500, got {next_level} @ {next_price}"

    # Test 2: LONG - After TP1 triggered
    triggered = {0.382}
    next_level, next_price = get_next_exit_level(
        exit_levels=exit_levels,
        current_price=current_price,
        side="LONG",
        triggered_levels=triggered,
    )

    print(f"Test 2 - LONG, TP1 done: Next = {next_level} @ ${next_price:,.0f}")
    assert next_level == 0.5 and next_price == 106_500

    # Test 3: SHORT - Price below all levels
    current_price = 102_000
    triggered = set()

    next_level, next_price = get_next_exit_level(
        exit_levels=exit_levels,
        current_price=current_price,
        side="SHORT",
        triggered_levels=triggered,
    )

    print(f"Test 3 - SHORT, price below all: Next = {next_level} @ ${next_price:,.0f}")
    assert next_level == 0.618 and next_price == 104_500

    # Test 4: All triggered
    triggered = {0.382, 0.5, 0.618}
    next_level, next_price = get_next_exit_level(
        exit_levels=exit_levels,
        current_price=current_price,
        side="LONG",
        triggered_levels=triggered,
    )

    print(f"Test 4 - All triggered: Next = {next_level}")
    assert next_level is None and next_price is None

    print("\n[PASS] Next exit level selection correct")
    return True


def test_edge_cases():
    """Test edge cases."""
    print("\n=== TEST: Edge Cases ===")

    # Test 1: Same high and low (invalid)
    try:
        levels = calculate_exit_fibonacci_levels(side="LONG", swing_high=100_000, swing_low=100_000)
        print("\n[FAIL] Should have raised ValueError for same high/low")
        return False
    except ValueError as e:
        print(f"\n[OK] Correctly raised ValueError: {e}")

    # Test 2: Invalid side
    try:
        levels = calculate_exit_fibonacci_levels(
            side="INVALID", swing_high=110_000, swing_low=95_000
        )
        print("[FAIL] Should have raised ValueError for invalid side")
        return False
    except ValueError as e:
        print(f"[OK] Correctly raised ValueError: {e}")

    # Test 3: Custom levels
    custom_levels = [0.236, 0.786, 1.0]
    levels = calculate_exit_fibonacci_levels(
        side="LONG", swing_high=110_000, swing_low=100_000, levels=custom_levels
    )
    print(f"[OK] Custom levels work: {list(levels.keys())}")
    assert set(levels.keys()) == set(custom_levels)

    print("\n[PASS] Edge cases handled correctly")
    return True


def run_all_tests():
    """Run all unit tests."""
    print("\n" + "=" * 70)
    print("EXIT FIBONACCI CALCULATOR - UNIT TESTS")
    print("=" * 70)

    tests = [
        ("LONG Exit Levels", test_calculate_exit_fibonacci_levels_long),
        ("SHORT Exit Levels", test_calculate_exit_fibonacci_levels_short),
        ("Swing Validation", test_validate_swing_for_exit),
        ("Swing Improvement", test_calculate_swing_improvement),
        ("Next Exit Level", test_get_next_exit_level),
        ("Edge Cases", test_edge_cases),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"\n[FAIL] {test_name}: {e}")
            import traceback

            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 70)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
