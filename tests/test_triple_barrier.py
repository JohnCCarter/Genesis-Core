"""Tests for triple-barrier labeling methods."""

from __future__ import annotations

import pytest

from core.ml.labeling import (
    generate_adaptive_triple_barrier_labels,
    generate_triple_barrier_labels,
)


class TestTripleBarrierLabeling:
    """Test triple-barrier labeling logic."""

    def test_profit_target_hit(self):
        """Test label when profit target hit first."""
        # Price rises quickly to hit profit target
        prices = [100.0, 100.1, 100.2, 100.35, 100.5]
        labels = generate_triple_barrier_labels(
            prices,
            profit_threshold_pct=0.3,
            stop_threshold_pct=0.2,
            max_holding_bars=3,
        )
        assert labels[0] == 1  # Profit target hit at bar 3 (+0.35%)

    def test_stop_loss_hit(self):
        """Test label when stop loss hit first."""
        # Price falls quickly to hit stop
        prices = [100.0, 99.9, 99.8, 99.75, 99.7]
        labels = generate_triple_barrier_labels(
            prices,
            profit_threshold_pct=0.3,
            stop_threshold_pct=0.2,
            max_holding_bars=3,
        )
        assert labels[0] == 0  # Stop hit at bar 3 (-0.25%)

    def test_time_exit_neutral(self):
        """Test label when neither barrier hit (small move)."""
        # Small oscillation
        prices = [100.0, 100.05, 99.95, 100.02, 100.01]
        labels = generate_triple_barrier_labels(
            prices,
            profit_threshold_pct=0.3,
            stop_threshold_pct=0.2,
            max_holding_bars=3,
        )
        assert labels[0] is None  # Too small move

    def test_asymmetric_barriers(self):
        """Test asymmetric profit/stop (1.5:1 R:R)."""
        prices = [100.0, 100.1, 100.2, 100.45, 100.5]
        labels = generate_triple_barrier_labels(
            prices,
            profit_threshold_pct=0.45,
            stop_threshold_pct=0.3,
            max_holding_bars=3,
        )
        assert labels[0] == 1  # Profit target hit

    def test_insufficient_future_bars(self):
        """Test labels are None when not enough future data."""
        prices = [100.0, 101.0, 102.0]
        labels = generate_triple_barrier_labels(
            prices,
            profit_threshold_pct=0.3,
            stop_threshold_pct=0.2,
            max_holding_bars=5,
        )
        assert all(label is None for label in labels)  # Not enough future bars

    def test_invalid_prices(self):
        """Test handling of zero/negative prices."""
        prices = [100.0, 0.0, -50.0, 100.5]
        labels = generate_triple_barrier_labels(
            prices,
            profit_threshold_pct=0.3,
            stop_threshold_pct=0.2,
            max_holding_bars=2,
        )
        assert labels[0] is None  # Entry at 100, but next price invalid
        assert labels[1] is None  # Invalid entry
        assert labels[2] is None  # Invalid entry

    def test_empty_input(self):
        """Test with empty input."""
        assert generate_triple_barrier_labels([]) == []

    def test_invalid_thresholds(self):
        """Test validation of thresholds."""
        with pytest.raises(ValueError):
            generate_triple_barrier_labels([100], profit_threshold_pct=0, stop_threshold_pct=0.2)
        with pytest.raises(ValueError):
            generate_triple_barrier_labels([100], profit_threshold_pct=0.3, stop_threshold_pct=-0.1)

    def test_invalid_holding_bars(self):
        """Test validation of max_holding_bars."""
        with pytest.raises(ValueError):
            generate_triple_barrier_labels([100, 101], max_holding_bars=0)
        with pytest.raises(ValueError):
            generate_triple_barrier_labels([100, 101], max_holding_bars=-1)

    def test_realistic_scenario(self):
        """Test realistic price action."""
        # Volatile price action with eventual profit
        prices = [
            100.0,
            100.1,
            99.9,
            100.15,
            100.05,
            100.25,
            100.35,
            100.5,
        ]
        labels = generate_triple_barrier_labels(
            prices,
            profit_threshold_pct=0.3,
            stop_threshold_pct=0.2,
            max_holding_bars=5,
        )
        # Should hit profit at bar 6 (+0.35%)
        assert labels[0] == 1


class TestAdaptiveTripleBarrierLabeling:
    """Test ATR-adaptive triple-barrier labeling."""

    def test_high_volatility_wider_barriers(self):
        """Test that high ATR creates wider barriers."""
        prices = [100.0, 100.5, 101.0, 101.5, 102.0]
        atr_high = [2.0] * 5  # High volatility
        atr_low = [0.5] * 5  # Low volatility

        labels_high = generate_adaptive_triple_barrier_labels(
            prices,
            atr_high,
            profit_multiplier=1.5,
            stop_multiplier=1.0,
            max_holding_bars=3,
        )
        labels_low = generate_adaptive_triple_barrier_labels(
            prices,
            atr_low,
            profit_multiplier=1.5,
            stop_multiplier=1.0,
            max_holding_bars=3,
        )

        # Low ATR should label sooner (tighter barriers)
        assert labels_low[0] == 1  # Hits target easily
        # High ATR might not hit target
        assert labels_high[0] in [1, None]

    def test_profit_target_with_atr(self):
        """Test profit target calculation with ATR."""
        prices = [100.0, 100.5, 101.5, 102.5, 103.0]
        atr = [1.0] * 5  # ATR = 1.0

        labels = generate_adaptive_triple_barrier_labels(
            prices, atr, profit_multiplier=1.5, stop_multiplier=1.0, max_holding_bars=3
        )
        # Target = 100 + 1.5*1.0 = 101.5, hit at bar 2
        assert labels[0] == 1

    def test_stop_loss_with_atr(self):
        """Test stop loss calculation with ATR."""
        prices = [100.0, 99.5, 98.5, 98.0, 97.5]
        atr = [1.0] * 5

        labels = generate_adaptive_triple_barrier_labels(
            prices, atr, profit_multiplier=1.5, stop_multiplier=1.0, max_holding_bars=3
        )
        # Stop = 100 - 1.0*1.0 = 99.0, hit at bar 2
        assert labels[0] == 0

    def test_mismatched_lengths(self):
        """Test validation of input lengths."""
        with pytest.raises(ValueError):
            generate_adaptive_triple_barrier_labels([100, 101], [1.0], max_holding_bars=2)

    def test_invalid_atr(self):
        """Test handling of invalid ATR values."""
        prices = [100.0, 101.0, 102.0]
        atr = [0.0, -1.0, float("nan")]

        labels = generate_adaptive_triple_barrier_labels(
            prices, atr, profit_multiplier=1.5, stop_multiplier=1.0, max_holding_bars=1
        )
        assert all(label is None for label in labels)  # All invalid

    def test_empty_input(self):
        """Test with empty input."""
        assert generate_adaptive_triple_barrier_labels([], []) == []

    def test_invalid_multipliers(self):
        """Test validation of multipliers."""
        with pytest.raises(ValueError):
            generate_adaptive_triple_barrier_labels([100], [1.0], profit_multiplier=0)
        with pytest.raises(ValueError):
            generate_adaptive_triple_barrier_labels([100], [1.0], stop_multiplier=-1.0)

    def test_realistic_scenario_with_atr(self):
        """Test realistic scenario with varying ATR."""
        prices = [100.0, 100.5, 101.5, 102.0, 103.0]
        atr = [1.0, 1.2, 1.5, 1.3, 1.1]  # Varying volatility

        labels = generate_adaptive_triple_barrier_labels(
            prices, atr, profit_multiplier=1.5, stop_multiplier=1.0, max_holding_bars=3
        )
        # First bar: target = 100 + 1.5*1.0 = 101.5, hit at bar 2
        assert labels[0] == 1
