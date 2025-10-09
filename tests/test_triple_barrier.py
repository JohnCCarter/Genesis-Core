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
        # Need enough bars: atr_period (14) + max_holding (3) = 17
        n_bars = 20
        closes = [100.0 + i * 0.5 for i in range(n_bars)]
        
        # High volatility: wider highs/lows (ATR ~ 2.0)
        highs_high = [close + 2.0 for close in closes]
        lows_high = [close - 2.0 for close in closes]
        
        # Low volatility: tighter highs/lows (ATR ~ 0.5)
        highs_low = [close + 0.5 for close in closes]
        lows_low = [close - 0.5 for close in closes]

        labels_high = generate_adaptive_triple_barrier_labels(
            closes,
            highs_high,
            lows_high,
            profit_multiplier=1.5,
            stop_multiplier=1.0,
            max_holding_bars=3,
            atr_period=14,
        )
        labels_low = generate_adaptive_triple_barrier_labels(
            closes,
            highs_low,
            lows_low,
            profit_multiplier=1.5,
            stop_multiplier=1.0,
            max_holding_bars=3,
            atr_period=14,
        )

        # With trending price and barriers, first label should be valid
        # Low ATR should label with tighter barriers
        assert labels_low[14] == 1  # First valid label after ATR period
        # High ATR might not hit target (wider barriers)
        assert labels_high[14] in [1, None]

    def test_profit_target_with_atr(self):
        """Test profit target calculation with ATR."""
        # Need enough bars: atr_period (14) + max_holding (3) = 17
        n_bars = 20
        closes = [100.0 + i * 1.0 for i in range(n_bars)]  # Strong uptrend
        highs = [close + 1.0 for close in closes]
        lows = [close - 1.0 for close in closes]

        labels = generate_adaptive_triple_barrier_labels(
            closes, highs, lows, profit_multiplier=1.5, stop_multiplier=1.0, max_holding_bars=3, atr_period=14
        )
        # Target = entry + 1.5*ATR, with strong uptrend should hit profit
        assert labels[14] == 1  # First valid label after ATR period

    def test_stop_loss_with_atr(self):
        """Test stop loss calculation with ATR."""
        # Need enough bars: atr_period (14) + max_holding (3) = 17
        n_bars = 20
        closes = [100.0 - i * 1.0 for i in range(n_bars)]  # Strong downtrend
        highs = [close + 1.0 for close in closes]
        lows = [close - 1.0 for close in closes]

        labels = generate_adaptive_triple_barrier_labels(
            closes, highs, lows, profit_multiplier=1.5, stop_multiplier=1.0, max_holding_bars=3, atr_period=14
        )
        # Stop = entry - 1.0*ATR, with strong downtrend should hit stop
        assert labels[14] == 0  # First valid label after ATR period

    def test_mismatched_lengths(self):
        """Test validation of input lengths."""
        with pytest.raises(ValueError):
            generate_adaptive_triple_barrier_labels([100, 101], [101, 102], [99], max_holding_bars=2)

    def test_invalid_atr(self):
        """Test handling of invalid ATR values (invalid highs/lows)."""
        closes = [100.0, 101.0, 102.0]
        highs = [0.0, -1.0, float("nan")]  # Invalid highs
        lows = [0.0, -1.0, float("nan")]   # Invalid lows

        labels = generate_adaptive_triple_barrier_labels(
            closes, highs, lows, profit_multiplier=1.5, stop_multiplier=1.0, max_holding_bars=1, atr_period=2
        )
        assert all(label is None for label in labels)  # All invalid

    def test_empty_input(self):
        """Test with empty input."""
        assert generate_adaptive_triple_barrier_labels([], [], []) == []

    def test_invalid_multipliers(self):
        """Test validation of multipliers."""
        with pytest.raises(ValueError):
            generate_adaptive_triple_barrier_labels([100], [101], [99], profit_multiplier=0)
        with pytest.raises(ValueError):
            generate_adaptive_triple_barrier_labels([100], [101], [99], stop_multiplier=-1.0)

    def test_realistic_scenario_with_atr(self):
        """Test realistic scenario with varying ATR."""
        # Need enough bars: atr_period (14) + max_holding (3) = 17
        n_bars = 20
        closes = [100.0 + i * 0.7 for i in range(n_bars)]  # Uptrend
        highs = [close + (1.0 + i * 0.1) for i, close in enumerate(closes)]  # Varying volatility
        lows = [close - (1.0 + i * 0.1) for i, close in enumerate(closes)]

        labels = generate_adaptive_triple_barrier_labels(
            closes, highs, lows, profit_multiplier=1.5, stop_multiplier=1.0, max_holding_bars=3, atr_period=14
        )
        # With uptrend and reasonable barriers, should hit profit target
        assert labels[14] == 1  # First valid label after ATR period
