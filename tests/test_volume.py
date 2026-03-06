"""Tests for volume indicators."""

from __future__ import annotations

import math

import pytest

from core.indicators.volume import (
    calculate_volume_ema,
    calculate_volume_sma,
    obv,
    volume_change,
    volume_price_divergence,
    volume_spike,
    volume_trend,
)


@pytest.mark.parametrize(
    "indicator",
    [volume_change, volume_spike, volume_trend],
    ids=["volume_change", "volume_spike", "volume_trend"],
)
def test_empty_input_indicators_return_empty_list(indicator):
    """Shared parity test for indicators with empty-input default behavior."""
    assert indicator([]) == []


@pytest.mark.parametrize(
    ("indicator", "close", "volume", "expected"),
    [
        (volume_price_divergence, [100.0, 101.0], [1000.0], []),
        (volume_price_divergence, [], [], []),
        (obv, [100.0, 101.0], [1000.0], []),
        (obv, [], [], []),
    ],
    ids=[
        "volume_price_divergence_mismatched_lengths",
        "volume_price_divergence_empty_input",
        "obv_mismatched_lengths",
        "obv_empty_input",
    ],
)
def test_two_input_indicator_guardrails(indicator, close, volume, expected):
    """Shared guardrail parity tests for two-input volume indicators."""
    assert indicator(close, volume) == expected


@pytest.mark.parametrize(
    ("func", "args", "expected"),
    [
        (volume_change, ([1000, 2000], 0), []),
        (volume_change, ([1000, 2000], -1), []),
        (volume_spike, ([1000, 2000], 0), []),
        (volume_spike, ([1000, 2000], 5, -1.0), []),
        (calculate_volume_ema, ([100, 200], 0), []),
    ],
    ids=[
        "volume_change_invalid_period_zero",
        "volume_change_invalid_period_negative",
        "volume_spike_invalid_period_zero",
        "volume_spike_invalid_threshold_negative",
        "volume_ema_invalid_period_zero",
    ],
)
def test_invalid_parameter_guardrails(func, args, expected):
    """Shared parity tests for invalid-parameter guardrails."""
    assert func(*args) == expected


@pytest.mark.parametrize(
    ("func", "args", "expected"),
    [
        (calculate_volume_ema, ([], 5), []),
        (calculate_volume_sma, ([], 5), []),
    ],
    ids=[
        "volume_ema_empty_input",
        "volume_sma_empty_input",
    ],
)
def test_moving_average_empty_input_guardrails(func, args, expected):
    """Shared parity tests for moving-average empty-input guardrails."""
    assert func(*args) == expected


@pytest.mark.parametrize(
    ("func", "args", "expected"),
    [
        (volume_change, ([1000.0, 2000.0], 5), []),
        (volume_price_divergence, ([100.0, 101.0], [1000.0, 1100.0], 5), []),
    ],
    ids=[
        "volume_change_insufficient_data",
        "volume_price_divergence_insufficient_data",
    ],
)
def test_insufficient_data_guardrails(func, args, expected):
    """Shared parity tests for insufficient-data guardrails."""
    assert func(*args) == expected


class TestVolumeChange:
    """Test volume change indicator."""

    def test_basic_volume_change(self):
        """Test basic volume change calculation."""
        # Volume doubles from average
        volume = [1000.0, 1000.0, 1000.0, 1000.0, 2000.0]
        period = 4

        vc = volume_change(volume, period)

        # First 3 values should be NaN
        assert all(math.isnan(vc[i]) for i in range(3))

        # At index 4: current=2000, avg=(1000+1000+1000+2000)/4=1250
        # change = (2000-1250)/1250 = 0.6
        assert abs(vc[4] - 0.6) < 0.001

    def test_volume_below_average(self):
        """Test volume change when below average."""
        volume = [2000.0, 2000.0, 2000.0, 2000.0, 1000.0]
        period = 4

        vc = volume_change(volume, period)

        # At index 4: current=1000, avg=(2000+2000+2000+1000)/4=1750
        # change = (1000-1750)/1750 = -0.428...
        assert vc[4] < 0
        assert abs(vc[4] - (-0.428571)) < 0.001


class TestVolumeSpike:
    """Test volume spike detection."""

    def test_spike_detection(self):
        """Test spike detection with threshold 2.0."""
        volume = [1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 3500.0]
        period = 5
        threshold = 2.0

        spikes = volume_spike(volume, period, threshold)

        # First 4 should be False (not enough data)
        assert all(not spikes[i] for i in range(4))

        # At index 5: current=3500, avg=(1000+1000+1000+1000+3500)/5=1700
        # 3500 > 2.0*1700=3400, so True
        assert spikes[5] is True

    def test_no_spike(self):
        """Test when no spike occurs."""
        volume = [1000.0, 1000.0, 1000.0, 1000.0, 1500.0]
        period = 4
        threshold = 2.0

        spikes = volume_spike(volume, period, threshold)

        # 1500 < 2.0 * 1125 = False
        assert spikes[4] is False

    def test_custom_threshold(self):
        """Test with custom threshold."""
        volume = [1000.0] * 4 + [1600.0]
        period = 4

        # With threshold 1.2
        spikes_12 = volume_spike(volume, period, threshold=1.2)
        # avg=(1000+1000+1000+1600)/4=1150, 1600 > 1.2*1150=1380
        assert spikes_12[4] is True

        # With threshold 1.5
        spikes_15 = volume_spike(volume, period, threshold=1.5)
        # 1600 < 1.5*1150=1725
        assert spikes_15[4] is False


class TestVolumeTrend:
    """Test volume trend indicator."""

    def test_increasing_volume_trend(self):
        """Test with increasing volume."""
        # Volume increases over time
        volume = [1000.0] * 30 + [2000.0] * 30
        fast_period = 10
        slow_period = 30

        trend = volume_trend(volume, fast_period, slow_period)

        # Last value should show fast > slow (ratio > 1.0)
        assert not math.isnan(trend[-1])
        assert trend[-1] > 1.0

    def test_decreasing_volume_trend(self):
        """Test with decreasing volume."""
        # Volume decreases over time
        volume = [2000.0] * 30 + [1000.0] * 30
        fast_period = 10
        slow_period = 30

        trend = volume_trend(volume, fast_period, slow_period)

        # Last value should show fast < slow (ratio < 1.0)
        assert not math.isnan(trend[-1])
        assert trend[-1] < 1.0

    def test_stable_volume_trend(self):
        """Test with stable volume."""
        volume = [1000.0] * 60
        fast_period = 10
        slow_period = 30

        trend = volume_trend(volume, fast_period, slow_period)

        # Ratio should be close to 1.0
        assert abs(trend[-1] - 1.0) < 0.01

    def test_insufficient_data(self):
        """Test with insufficient data."""
        volume = [1000.0] * 20
        fast_period = 10
        slow_period = 30

        trend = volume_trend(volume, fast_period, slow_period)

        # All should be NaN (not enough data for slow period)
        assert all(math.isnan(x) for x in trend)


class TestVolumeEMA:
    """Test volume EMA calculation."""

    def test_basic_ema(self):
        """Test basic EMA calculation."""
        volume = [100.0, 110.0, 120.0, 130.0, 140.0]
        period = 3

        ema = calculate_volume_ema(volume, period)

        # First 2 values should be NaN
        assert all(math.isnan(ema[i]) for i in range(2))

        # EMA should respond to trend
        assert ema[2] < ema[3] < ema[4]

    def test_constant_values(self):
        """Test EMA with constant values."""
        volume = [100.0] * 10
        period = 5

        ema = calculate_volume_ema(volume, period)

        # After initialization, all values should be 100.0
        assert all(abs(ema[i] - 100.0) < 0.01 for i in range(4, 10))


class TestVolumePriceDivergence:
    """Test volume-price divergence indicator."""

    def test_bullish_divergence(self):
        """Test bullish divergence (price down, volume up)."""
        close = [100.0, 99.0, 98.0, 97.0, 96.0]
        volume = [1000.0, 1100.0, 1200.0, 1300.0, 1400.0]
        lookback = 5

        div = volume_price_divergence(close, volume, lookback)

        # Should detect bullish divergence (positive value)
        assert not math.isnan(div[-1])
        assert div[-1] > 0

    def test_bearish_divergence(self):
        """Test bearish divergence (price up, volume down)."""
        close = [100.0, 101.0, 102.0, 103.0, 104.0]
        volume = [1400.0, 1300.0, 1200.0, 1100.0, 1000.0]
        lookback = 5

        div = volume_price_divergence(close, volume, lookback)

        # Should detect bearish divergence (negative value)
        assert not math.isnan(div[-1])
        assert div[-1] < 0

    def test_no_divergence(self):
        """Test when price and volume move together."""
        # Both rising
        close = [100.0, 101.0, 102.0, 103.0, 104.0]
        volume = [1000.0, 1100.0, 1200.0, 1300.0, 1400.0]
        lookback = 5

        div = volume_price_divergence(close, volume, lookback)

        # Should be near zero or negative (both rising = no bullish div)
        assert not math.isnan(div[-1])
        assert div[-1] < 0.1


class TestOBV:
    """Test On-Balance Volume indicator."""

    @pytest.mark.parametrize(
        ("close", "volume", "expected"),
        [
            (
                [100.0, 101.0, 102.0, 103.0, 104.0],
                [1000.0, 1000.0, 1000.0, 1000.0, 1000.0],
                [1000.0, 2000.0, 3000.0, 4000.0, 5000.0],
            ),
            (
                [104.0, 103.0, 102.0, 101.0, 100.0],
                [1000.0, 1000.0, 1000.0, 1000.0, 1000.0],
                [1000.0, 0.0, -1000.0, -2000.0, -3000.0],
            ),
            (
                [100.0, 100.0, 100.0, 100.0],
                [1000.0, 1000.0, 1000.0, 1000.0],
                [1000.0, 1000.0, 1000.0, 1000.0],
            ),
            (
                [100.0, 102.0, 101.0, 103.0, 102.0],
                [1000.0, 2000.0, 1500.0, 2500.0, 1000.0],
                [1000.0, 3000.0, 1500.0, 4000.0, 3000.0],
            ),
        ],
        ids=[
            "basic_obv_accumulation",
            "obv_distribution",
            "obv_unchanged_price",
            "obv_mixed_movement",
        ],
    )
    def test_obv_scenarios(self, close, volume, expected):
        """Test OBV scenario parity via full sequence equality."""
        obv_vals = obv(close, volume)
        assert obv_vals == expected


class TestVolumeSMA:
    """Test volume SMA helper function."""

    def test_basic_sma(self):
        """Test basic volume SMA calculation."""
        volume = [1000.0, 2000.0, 3000.0, 4000.0, 5000.0]
        period = 3

        sma = calculate_volume_sma(volume, period)

        # First 2 should be NaN
        assert all(math.isnan(sma[i]) for i in range(2))

        # SMA at index 2: (1000+2000+3000)/3 = 2000
        assert sma[2] == 2000.0

        # SMA at index 3: (2000+3000+4000)/3 = 3000
        assert sma[3] == 3000.0


class TestVolumeIntegration:
    """Integration tests for volume indicators."""

    def test_volume_confirmation(self):
        """Test volume confirming price movement."""
        # Strong uptrend with increasing volume (bullish)
        close = [100.0, 102.0, 105.0, 109.0, 114.0, 120.0]
        volume = [1000.0, 1200.0, 1500.0, 1800.0, 2200.0, 2700.0]

        # Volume change should be positive
        vc = volume_change(volume, period=3)
        assert vc[-1] > 0

        # OBV should be strongly positive
        obv_vals = obv(close, volume)
        assert obv_vals[-1] > obv_vals[0] * 5

        # No divergence (both rising)
        div = volume_price_divergence(close, volume, lookback=5)
        assert div[-1] < 0.1

    def test_volume_warning_signal(self):
        """Test volume divergence as warning signal."""
        # Price rising but volume declining (bearish divergence)
        close = [100.0, 102.0, 104.0, 106.0, 108.0]
        volume = [2000.0, 1800.0, 1600.0, 1400.0, 1200.0]

        # Bearish divergence
        div = volume_price_divergence(close, volume, lookback=5)
        assert div[-1] < 0

        # Volume trend declining
        vol_trend = volume_trend([2000.0] * 30 + volume, fast_period=5, slow_period=20)
        assert vol_trend[-1] < 1.0

    def test_breakout_with_volume_spike(self):
        """Test breakout confirmed by volume spike."""
        # Consolidation → breakout with volume spike
        volume = [1000.0] * 10 + [3000.0, 3500.0, 4000.0]

        # Detect spike at breakout
        spikes = volume_spike(volume, period=10, threshold=2.0)
        assert spikes[10] is True  # Breakout candle

        # Volume trend increasing
        vc = volume_change(volume, period=10)
        assert vc[-1] > 1.0  # Much higher than average
