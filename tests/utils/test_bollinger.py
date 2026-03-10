"""Tests for Bollinger Bands indicator."""

from __future__ import annotations

import math

from core.indicators.bollinger import (
    bb_squeeze,
    bollinger_bands,
    calculate_sma,
    calculate_std_dev,
)


class TestCalculateSMA:
    """Test Simple Moving Average calculation."""

    def test_basic_sma(self):
        """Test basic SMA calculation."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        period = 3
        result = calculate_sma(values, period)

        # First 2 values should be NaN
        assert math.isnan(result[0])
        assert math.isnan(result[1])

        # SMA(3) at index 2: (1+2+3)/3 = 2.0
        assert result[2] == 2.0

        # SMA(3) at index 3: (2+3+4)/3 = 3.0
        assert result[3] == 3.0

        # SMA(3) at index 4: (3+4+5)/3 = 4.0
        assert result[4] == 4.0

    def test_empty_input(self):
        """Test SMA with empty input."""
        assert calculate_sma([], 5) == []

    def test_invalid_period(self):
        """Test SMA with invalid period."""
        assert calculate_sma([1, 2, 3], 0) == []
        assert calculate_sma([1, 2, 3], -1) == []

    def test_period_longer_than_data(self):
        """Test SMA when period exceeds data length."""
        values = [1.0, 2.0, 3.0]
        period = 5
        result = calculate_sma(values, period)

        # All values should be NaN
        assert all(math.isnan(x) for x in result)


class TestCalculateStdDev:
    """Test Standard Deviation calculation."""

    def test_basic_std_dev(self):
        """Test basic standard deviation calculation."""
        values = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]
        period = 5
        sma = calculate_sma(values, period)
        result = calculate_std_dev(values, period, sma)

        # First 4 values should be NaN
        assert all(math.isnan(result[i]) for i in range(4))

        # Check std dev is calculated (non-zero)
        assert result[4] > 0

    def test_constant_values(self):
        """Test std dev with constant values (should be 0)."""
        values = [5.0, 5.0, 5.0, 5.0, 5.0]
        period = 3
        sma = calculate_sma(values, period)
        result = calculate_std_dev(values, period, sma)

        # Std dev should be 0 for constant values
        assert result[2] == 0.0
        assert result[3] == 0.0
        assert result[4] == 0.0

    def test_mismatched_lengths(self):
        """Test std dev with mismatched input lengths."""
        values = [1.0, 2.0, 3.0]
        sma = [1.0, 2.0]
        result = calculate_std_dev(values, 2, sma)
        assert result == []


class TestBollingerBands:
    """Test Bollinger Bands calculation."""

    def test_basic_bollinger_bands(self):
        """Test basic Bollinger Bands calculation."""
        close = [100.0, 102.0, 101.0, 103.0, 104.0, 102.0, 105.0, 107.0, 106.0, 108.0]
        period = 5
        std_dev = 2.0

        bb = bollinger_bands(close, period, std_dev)

        # Check all keys are present
        assert "middle" in bb
        assert "upper" in bb
        assert "lower" in bb
        assert "width" in bb
        assert "position" in bb

        # Check lengths
        assert len(bb["middle"]) == len(close)
        assert len(bb["upper"]) == len(close)
        assert len(bb["lower"]) == len(close)
        assert len(bb["width"]) == len(close)
        assert len(bb["position"]) == len(close)

        # First 4 values should be NaN
        for i in range(4):
            assert math.isnan(bb["middle"][i])
            assert math.isnan(bb["upper"][i])
            assert math.isnan(bb["lower"][i])
            assert math.isnan(bb["width"][i])
            assert math.isnan(bb["position"][i])

        # After period, values should be valid
        assert not math.isnan(bb["middle"][4])
        assert not math.isnan(bb["upper"][4])
        assert not math.isnan(bb["lower"][4])

        # Upper should be > middle > lower
        assert bb["upper"][4] > bb["middle"][4]
        assert bb["middle"][4] > bb["lower"][4]

    def test_bb_width_calculation(self):
        """Test BB width calculation."""
        close = [100.0, 100.0, 100.0, 100.0, 100.0]  # No volatility
        period = 3
        std_dev = 2.0

        bb = bollinger_bands(close, period, std_dev)

        # Width should be 0 for constant prices
        assert bb["width"][2] == 0.0
        assert bb["width"][3] == 0.0
        assert bb["width"][4] == 0.0

    def test_bb_position(self):
        """Test BB position calculation."""
        # Price at middle band
        close = [100.0, 100.0, 100.0, 100.0, 100.0]
        period = 3
        bb = bollinger_bands(close, period)

        # Position should be 0.5 when price is at middle
        assert bb["position"][2] == 0.5

    def test_bb_position_at_upper_band(self):
        """Test BB position when price is at upper band."""
        close = [100.0, 101.0, 102.0, 103.0, 110.0]  # Spike up
        period = 3
        bb = bollinger_bands(close, period)

        # Position should be high (close to 1.0) when price spikes
        assert bb["position"][4] > 0.8

    def test_empty_input(self):
        """Test with empty input."""
        bb = bollinger_bands([])
        assert bb["middle"] == []
        assert bb["upper"] == []
        assert bb["lower"] == []

    def test_insufficient_data(self):
        """Test with insufficient data."""
        close = [100.0, 101.0]
        period = 5
        bb = bollinger_bands(close, period)
        assert bb["middle"] == []

    def test_custom_std_dev(self):
        """Test with custom standard deviation multiplier."""
        close = [100.0, 102.0, 101.0, 103.0, 104.0, 102.0, 105.0, 107.0, 106.0, 108.0]
        period = 5

        bb_2std = bollinger_bands(close, period, std_dev=2.0)
        bb_1std = bollinger_bands(close, period, std_dev=1.0)

        # 2 std should have wider bands
        width_2std = bb_2std["width"][5]
        width_1std = bb_1std["width"][5]

        assert width_2std > width_1std
        assert abs(width_2std - 2 * width_1std) < 0.001  # Should be ~2x


class TestBBSqueeze:
    """Test Bollinger Band squeeze detection."""

    def test_squeeze_detection(self):
        """Test squeeze detection when volatility is at minimum."""
        # Create data with decreasing volatility
        bb_width = [0.10, 0.09, 0.08, 0.07, 0.06, 0.05, 0.05, 0.05, 0.06, 0.07]
        lookback = 5

        squeeze = bb_squeeze(bb_width, lookback)

        # At index 5, width is minimum (0.05) in last 5 bars
        assert squeeze[5] is True

        # At index 9, width is not minimum
        assert squeeze[9] is False

    def test_no_squeeze(self):
        """Test when no squeeze is present."""
        bb_width = [0.10, 0.10, 0.10, 0.10, 0.10]
        lookback = 3

        squeeze = bb_squeeze(bb_width, lookback)

        # All values are same, so all are "minimum"
        assert squeeze[2] is True
        assert squeeze[3] is True

    def test_squeeze_with_nan(self):
        """Test squeeze detection with NaN values."""
        bb_width = [float("nan"), float("nan"), 0.10, 0.09, 0.08]
        lookback = 3

        squeeze = bb_squeeze(bb_width, lookback)

        # First 2 should be False (NaN)
        assert squeeze[0] is False
        assert squeeze[1] is False

        # At index 4, should check last 3 valid values
        assert squeeze[4] is True  # 0.08 is minimum

    def test_empty_input(self):
        """Test with empty input."""
        assert bb_squeeze([]) == []

    def test_invalid_lookback(self):
        """Test with invalid lookback."""
        bb_width = [0.10, 0.09, 0.08]
        assert bb_squeeze(bb_width, 0) == []
        assert bb_squeeze(bb_width, -1) == []

    def test_lookback_longer_than_data(self):
        """Test when lookback exceeds data length."""
        bb_width = [0.10, 0.09, 0.08]
        lookback = 10

        squeeze = bb_squeeze(bb_width, lookback)

        # All values should be False (insufficient data)
        assert all(not x for x in squeeze)


class TestBollingerBandsIntegration:
    """Integration tests for Bollinger Bands with realistic data."""

    def test_realistic_price_series(self):
        """Test with realistic price series."""
        # Simulate a trending market with volatility
        close = [
            100.0,
            101.5,
            102.0,
            103.5,
            105.0,
            104.0,
            106.0,
            108.0,
            107.0,
            109.0,
            111.0,
            110.0,
            112.0,
            115.0,
            114.0,
            116.0,
            118.0,
            117.0,
            119.0,
            121.0,
        ]
        period = 20

        bb = bollinger_bands(close, period)

        # Check last value (index 19)
        assert not math.isnan(bb["middle"][19])
        assert not math.isnan(bb["upper"][19])
        assert not math.isnan(bb["lower"][19])

        # Middle band should be close to average of last 20 prices
        expected_middle = sum(close) / period
        assert abs(bb["middle"][19] - expected_middle) < 1.0

        # Width should be positive (volatility exists)
        assert bb["width"][19] > 0

        # Position should be between 0 and 1
        assert 0.0 <= bb["position"][19] <= 1.0

    def test_low_volatility_period(self):
        """Test detection of low volatility period."""
        # Create data with low volatility period
        close = [100.0] * 10 + [100.5, 100.3, 100.4, 100.2, 100.1] + [105.0] * 5
        period = 10

        bb = bollinger_bands(close, period)

        # During low volatility period (indices 10-14), width should be low
        low_vol_widths = bb["width"][10:15]
        high_vol_widths = bb["width"][15:]

        # Average width during low vol should be less than high vol
        avg_low = sum(x for x in low_vol_widths if not math.isnan(x)) / len(
            [x for x in low_vol_widths if not math.isnan(x)]
        )
        avg_high = sum(x for x in high_vol_widths if not math.isnan(x)) / len(
            [x for x in high_vol_widths if not math.isnan(x)]
        )

        assert avg_low < avg_high

    def test_band_expansion_contraction(self):
        """Test that bands expand with volatility and contract without."""
        # Low vol → high vol
        close = [100.0, 100.1, 100.2, 100.1, 100.0] * 4 + [  # Low volatility (20 bars)
            100.0,
            105.0,
            95.0,
            110.0,
            90.0,
            115.0,
            85.0,
        ]  # High volatility (7 bars)
        period = 10

        bb = bollinger_bands(close, period)

        # Width during high volatility should be larger
        high_vol_idx = 24  # During high volatility period
        low_vol_idx = 15  # During low vol period

        # High vol width should be significantly larger
        assert bb["width"][high_vol_idx] > bb["width"][low_vol_idx] * 2
