"""
Tests for exit Fibonacci calculator module.
"""

import pytest

from src.core.indicators.exit_fibonacci import (
    calculate_exit_fibonacci_levels,
    calculate_swing_improvement,
    format_exit_levels_for_display,
    get_next_exit_level,
    validate_swing_for_exit,
)


class TestExitFibonacciLevels:
    """Test exit Fibonacci level calculation with symmetric logic."""

    def test_long_exit_levels_symmetric(self):
        """Test LONG exit levels with symmetric Chamoun logic."""
        swing_high = 110000.0
        swing_low = 100000.0

        exit_levels = calculate_exit_fibonacci_levels("LONG", swing_high, swing_low)

        # Should use inverted levels: [0.786, 0.618, 0.5, 0.382]
        expected_levels = {
            0.786: 110000.0 - (10000.0 * 0.786),  # 102,140
            0.618: 110000.0 - (10000.0 * 0.618),  # 103,820
            0.5: 110000.0 - (10000.0 * 0.5),  # 105,000
            0.382: 110000.0 - (10000.0 * 0.382),  # 106,180
        }

        assert exit_levels == expected_levels

        # Verify order: highest to lowest (0.786 → 0.382)
        sorted_levels = sorted(exit_levels.items(), reverse=True)
        assert sorted_levels[0][0] == 0.786  # Highest level first
        assert sorted_levels[-1][0] == 0.382  # Lowest level last

    def test_short_exit_levels_symmetric(self):
        """Test SHORT exit levels with symmetric Chamoun logic."""
        swing_high = 110000.0
        swing_low = 100000.0

        exit_levels = calculate_exit_fibonacci_levels("SHORT", swing_high, swing_low)

        # Should use inverted levels: [0.786, 0.618, 0.5, 0.382]
        expected_levels = {
            0.786: 100000.0 + (10000.0 * 0.786),  # 107,860
            0.618: 100000.0 + (10000.0 * 0.618),  # 106,180
            0.5: 100000.0 + (10000.0 * 0.5),  # 105,000
            0.382: 100000.0 + (10000.0 * 0.382),  # 103,820
        }

        assert exit_levels == expected_levels

        # Verify order: highest to lowest (0.786 → 0.382)
        sorted_levels = sorted(exit_levels.items(), reverse=True)
        assert sorted_levels[0][0] == 0.786  # Highest level first
        assert sorted_levels[-1][0] == 0.382  # Lowest level last

    def test_custom_levels(self):
        """Test with custom Fibonacci levels."""
        swing_high = 1000.0
        swing_low = 900.0
        custom_levels = [0.5, 0.618]

        exit_levels = calculate_exit_fibonacci_levels("LONG", swing_high, swing_low, custom_levels)

        expected_levels = {
            0.5: 1000.0 - (100.0 * 0.5),  # 950
            0.618: 1000.0 - (100.0 * 0.618),  # 938.2
        }

        assert exit_levels == expected_levels

    def test_symmetric_consistency(self):
        """Test that LONG and SHORT use same levels but different directions."""
        swing_high = 1000.0
        swing_low = 900.0
        range_size = 100.0

        long_levels = calculate_exit_fibonacci_levels("LONG", swing_high, swing_low)
        short_levels = calculate_exit_fibonacci_levels("SHORT", swing_high, swing_low)

        # Both should have same Fibonacci levels
        assert set(long_levels.keys()) == set(short_levels.keys())

        # LONG: levels below swing_high
        for level, price in long_levels.items():
            assert price < swing_high
            expected = swing_high - (range_size * level)
            assert abs(price - expected) < 0.001

        # SHORT: levels above swing_low
        for level, price in short_levels.items():
            assert price > swing_low
            expected = swing_low + (range_size * level)
            assert abs(price - expected) < 0.001

    def test_invalid_inputs(self):
        """Test error handling for invalid inputs."""
        # Invalid swing order
        with pytest.raises(ValueError, match="Invalid swing"):
            calculate_exit_fibonacci_levels("LONG", 100.0, 110.0)

        # Invalid side
        with pytest.raises(ValueError, match="Invalid side"):
            calculate_exit_fibonacci_levels("INVALID", 110.0, 100.0)


class TestSwingValidation:
    """Test swing validation for exit calculations."""

    def test_valid_swing(self):
        """Test validation of valid swing."""
        is_valid, reason = validate_swing_for_exit(
            swing_high=110000.0,
            swing_low=100000.0,
            current_price=105000.0,
            current_atr=1000.0,
            min_swing_size_atr=3.0,
            max_distance_atr=8.0,
        )

        assert is_valid is True
        assert reason == "OK"

    def test_swing_too_small(self):
        """Test validation of swing that's too small."""
        is_valid, reason = validate_swing_for_exit(
            swing_high=101000.0,  # Only 1 ATR swing
            swing_low=100000.0,
            current_price=100500.0,
            current_atr=1000.0,
            min_swing_size_atr=3.0,
        )

        assert is_valid is False
        assert "SWING_TOO_SMALL" in reason

    def test_swing_too_far(self):
        """Test validation of swing that's too far from current price."""
        is_valid, reason = validate_swing_for_exit(
            swing_high=110000.0,
            swing_low=100000.0,
            current_price=50000.0,  # Very far from swing
            current_atr=1000.0,
            max_distance_atr=8.0,
        )

        assert is_valid is False
        assert "SWING_TOO_FAR" in reason

    def test_invalid_swing_order(self):
        """Test validation with invalid swing order."""
        is_valid, reason = validate_swing_for_exit(
            swing_high=100000.0,  # High < Low
            swing_low=110000.0,
            current_price=105000.0,
            current_atr=1000.0,
        )

        assert is_valid is False
        assert reason == "INVALID_SWING_ORDER"


class TestSwingImprovement:
    """Test swing improvement calculation."""

    def test_long_swing_improvement(self):
        """Test swing improvement for LONG positions."""
        # Better swing: higher high
        improvement = calculate_swing_improvement(
            old_swing_high=100000.0,
            old_swing_low=90000.0,
            new_swing_high=110000.0,  # Higher high
            new_swing_low=90000.0,
            side="LONG",
        )

        assert improvement > 0  # Positive improvement

    def test_short_swing_improvement(self):
        """Test swing improvement for SHORT positions."""
        # Better swing: lower low
        improvement = calculate_swing_improvement(
            old_swing_high=110000.0,
            old_swing_low=100000.0,
            new_swing_high=110000.0,
            new_swing_low=90000.0,  # Lower low
            side="SHORT",
        )

        assert improvement > 0  # Positive improvement

    def test_no_improvement(self):
        """Test when swing doesn't improve."""
        improvement = calculate_swing_improvement(
            old_swing_high=100000.0,
            old_swing_low=90000.0,
            new_swing_high=100000.0,  # Same high
            new_swing_low=90000.0,  # Same low
            side="LONG",
        )

        assert improvement == 0.0  # No improvement


class TestExitLevelHelpers:
    """Test helper functions for exit level management."""

    def test_get_next_exit_level_long(self):
        """Test finding next exit level for LONG position."""
        exit_levels = {
            0.786: 102140.0,
            0.618: 103820.0,
            0.5: 105000.0,
            0.382: 106180.0,
        }
        current_price = 104000.0  # Between 0.618 and 0.5

        next_level, next_price = get_next_exit_level(exit_levels, current_price, "LONG")

        # Should find 0.618 level (103820) as next target (highest under current price)
        assert next_level == 0.618
        assert next_price == 103820.0

    def test_get_next_exit_level_short(self):
        """Test finding next exit level for SHORT position."""
        exit_levels = {
            0.786: 107860.0,
            0.618: 106180.0,
            0.5: 105000.0,
            0.382: 103820.0,
        }
        current_price = 104000.0  # Between 0.5 and 0.382

        next_level, next_price = get_next_exit_level(exit_levels, current_price, "SHORT")

        # Should find 0.5 level (105000) as next target
        assert next_level == 0.5
        assert next_price == 105000.0

    def test_get_next_exit_level_with_triggered(self):
        """Test finding next exit level with some levels already triggered."""
        exit_levels = {
            0.786: 102140.0,
            0.618: 103820.0,
            0.5: 105000.0,
            0.382: 106180.0,
        }
        current_price = 104000.0
        triggered_levels = {0.618}  # 0.618 already triggered

        next_level, next_price = get_next_exit_level(
            exit_levels, current_price, "LONG", triggered_levels
        )

        # Should find 0.786 level (102140) as next target (highest under current price)
        assert next_level == 0.786
        assert next_price == 102140.0

    def test_format_exit_levels_display(self):
        """Test formatting exit levels for display."""
        exit_levels = {
            0.786: 102140.0,
            0.618: 103820.0,
            0.5: 105000.0,
            0.382: 106180.0,
        }
        current_price = 105000.0

        formatted = format_exit_levels_for_display(exit_levels, "LONG", current_price)

        assert "Exit Levels (LONG):" in formatted
        assert "0.786: $102,140" in formatted
        assert "0.618: $103,820" in formatted
        assert "0.500: $105,000" in formatted
        assert "0.382: $106,180" in formatted


class TestChamounSymmetry:
    """Test Chamoun's symmetric approach comprehensively."""

    def test_entry_vs_exit_symmetry(self):
        """Test that entry and exit use symmetric logic."""
        swing_high = 110000.0
        swing_low = 100000.0
        range_size = 10000.0

        # Exit levels (our implementation)
        exit_levels = calculate_exit_fibonacci_levels("LONG", swing_high, swing_low)

        # Entry levels (simulated - should be symmetric)
        # Entry: swing_low + (range * level) for levels [0.382, 0.5, 0.618, 0.786]
        entry_levels = {
            0.382: swing_low + (range_size * 0.382),  # 103,820
            0.5: swing_low + (range_size * 0.5),  # 105,000
            0.618: swing_low + (range_size * 0.618),  # 106,180
            0.786: swing_low + (range_size * 0.786),  # 107,860
        }

        # Verify symmetry: entry and exit use same Fibonacci levels
        assert set(exit_levels.keys()) == set(entry_levels.keys())

        # Verify exit levels are below swing_high (profit-taking)
        for _level, price in exit_levels.items():
            assert price < swing_high

        # Verify entry levels are above swing_low (pullback entry)
        for _level, price in entry_levels.items():
            assert price > swing_low

    def test_fibonacci_psychology(self):
        """Test that Fibonacci levels follow psychological principles."""
        swing_high = 100000.0
        swing_low = 90000.0

        exit_levels = calculate_exit_fibonacci_levels("LONG", swing_high, swing_low)

        # For LONG exit: 0.786 should be closest to swing_high (early profit-taking)
        # 0.382 should be closest to swing_low (deep retracement)
        # Since we use swing_high - (range * level), higher levels = lower prices
        assert exit_levels[0.786] < exit_levels[0.618] < exit_levels[0.5] < exit_levels[0.382]

        # All levels should be between swing_low and swing_high
        for _level, price in exit_levels.items():
            assert swing_low < price < swing_high


if __name__ == "__main__":
    pytest.main([__file__])
