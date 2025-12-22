"""
Tests for performance optimizations.

Validates that optimized implementations produce same results as original.
"""

import time

import numpy as np
import pandas as pd
import pytest

from core.indicators.volume import (
    calculate_volume_ema,
    calculate_volume_sma,
    obv,
    volume_change,
    volume_price_divergence,
    volume_spike,
)


class TestVolumeOptimizations:
    """Test vectorized volume calculations."""

    def test_volume_sma_basic(self):
        """Test basic SMA calculation."""
        volume = [100, 110, 120, 130, 140]
        result = calculate_volume_sma(volume, period=3)

        # First 2 should be NaN
        assert pd.isna(result[0])
        assert pd.isna(result[1])

        # Check valid values
        assert abs(result[2] - 110.0) < 0.01  # (100+110+120)/3
        assert abs(result[3] - 120.0) < 0.01  # (110+120+130)/3
        assert abs(result[4] - 130.0) < 0.01  # (120+130+140)/3

    def test_volume_change_basic(self):
        """Test volume change calculation."""
        volume = [100, 100, 100, 100, 200]
        result = volume_change(volume, period=3)

        # Last value should show positive change
        # avg of last 3 = (100+100+200)/3 = 133.33, change = (200-133.33)/133.33 = 0.5
        assert result[-1] > 0.4  # Approximately 50% increase over moving average

    def test_volume_spike_detection(self):
        """Test volume spike detection."""
        volume = [100, 100, 100, 100, 400]  # 400 > 2.0 * 175
        result = volume_spike(volume, period=4, threshold=2.0)

        # Last value should be detected as spike
        # avg of last 4 = (100+100+100+400)/4 = 175, threshold = 2.0 * 175 = 350
        # 400 > 350? Yes!
        assert result[-1] is True
        assert result[-2] is False

    def test_volume_ema_basic(self):
        """Test EMA calculation."""
        volume = [100, 110, 120, 130, 140]
        result = calculate_volume_ema(volume, period=3)

        # First 2 should be NaN
        assert pd.isna(result[0])
        assert pd.isna(result[1])

        # Check that EMA values are reasonable
        assert result[2] > 100
        assert result[-1] > result[-2]  # Increasing trend

    def test_obv_basic(self):
        """Test OBV calculation."""
        close = [100, 101, 102, 101, 103]
        volume = [1000, 1000, 1000, 1000, 1000]
        result = obv(close, volume)

        # OBV should accumulate based on price direction
        assert result[0] == 1000  # Initial
        # Check net effect: +1000 (up) +1000 (up) -1000 (down) +1000 (up) = +2000 net
        assert result[-1] > result[0]  # Net positive accumulation

    def test_volume_price_divergence_bullish(self):
        """Test bullish divergence detection."""
        close = [100, 99, 98, 97, 96]  # Declining
        volume = [1000, 1100, 1200, 1300, 1400]  # Increasing
        result = volume_price_divergence(close, volume, lookback=4)

        # Should detect bullish divergence (positive)
        assert not pd.isna(result[-1])
        assert result[-1] > 0

    def test_volume_price_divergence_bearish(self):
        """Test bearish divergence detection."""
        close = [100, 101, 102, 103, 104]  # Rising
        volume = [1400, 1300, 1200, 1100, 1000]  # Declining
        result = volume_price_divergence(close, volume, lookback=4)

        # Should detect bearish divergence (negative)
        assert not pd.isna(result[-1])
        assert result[-1] < 0


class TestDerivedFeaturesOptimizations:
    """Test vectorized derived features."""

    def test_momentum_displacement_basic(self):
        """Test momentum displacement calculation."""
        from core.indicators.derived_features import calculate_momentum_displacement_z

        # Create more realistic data with stronger signal
        closes = [100.0] * 100 + [120.0] * 100  # Larger step change
        atr_values = [1.0] * 200

        result = calculate_momentum_displacement_z(closes, atr_values, period=3, window=50)

        # Should have values
        assert len(result) == 200
        # Check that we get some non-zero z-scores
        assert any(abs(x) > 0.1 for x in result[110:130])  # After the jump

    def test_price_stretch_basic(self):
        """Test price stretch calculation."""
        from core.indicators.derived_features import calculate_price_stretch_z

        # Create more realistic data
        closes = [100.0] * 100 + [110.0] * 100
        ema_values = [100.0] * 200  # Flat EMA
        atr_values = [1.0] * 200

        result = calculate_price_stretch_z(closes, ema_values, atr_values, window=50)

        # Should have values
        assert len(result) == 200
        # Check that we get non-zero values after step change
        assert any(abs(x) > 0.1 for x in result[110:130])

    def test_volume_anomaly_basic(self):
        """Test volume anomaly detection."""
        from core.indicators.derived_features import calculate_volume_anomaly_z

        volumes = [100.0] * 50 + [200.0] * 50  # Volume spike
        result = calculate_volume_anomaly_z(volumes, window=50)

        # Should have values
        assert len(result) == 100
        # After volume spike, z-score should be elevated
        assert result[55] > 0

    def test_regime_persistence_basic(self):
        """Test regime persistence calculation."""
        from core.indicators.derived_features import calculate_regime_persistence

        # Uptrending EMA
        ema_values = list(range(100, 200))
        result = calculate_regime_persistence(ema_values, window=24)

        # Should have values
        assert len(result) == 100
        # Should show positive persistence for uptrend
        assert result[-1] > 0.5


class TestHTFFibonacciOptimizations:
    """Test HTF Fibonacci optimizations."""

    def test_htf_fibonacci_compute_basic(self):
        """Test HTF Fibonacci level computation."""
        from core.indicators.fibonacci import FibonacciConfig
        from core.indicators.htf_fibonacci import compute_htf_fibonacci_levels

        # Create simple test data
        data = {
            "timestamp": pd.date_range("2024-01-01", periods=100, freq="1D"),
            "high": [100 + i * 0.5 for i in range(100)],
            "low": [95 + i * 0.5 for i in range(100)],
            "close": [97 + i * 0.5 for i in range(100)],
        }
        df = pd.DataFrame(data)

        config = FibonacciConfig()
        result = compute_htf_fibonacci_levels(df, config)

        # Should return DataFrame with correct columns
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 100
        assert "htf_fib_0618" in result.columns
        assert "htf_swing_high" in result.columns
        assert "htf_swing_age_bars" in result.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestBacktestLoopPerformance:
    """Test backtest loop performance optimizations."""

    def test_numpy_array_access_vs_iloc(self):
        """Verify numpy array access is faster than pandas iloc in loops."""
        # Create test DataFrame with typical backtest size
        n_bars = 1000
        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2025-01-01", periods=n_bars, freq="1h"),
                "close": np.random.randn(n_bars).cumsum() + 100,
            }
        )

        # Measure pandas iloc access pattern (old way)
        start = time.time()
        total_iloc = 0.0
        for i in range(n_bars):
            bar = df.iloc[i]
            total_iloc += bar["close"]
        iloc_time = time.time() - start

        # Measure numpy array access pattern (optimized way)
        start = time.time()
        close_prices = df["close"].values
        total_numpy = 0.0
        for i in range(n_bars):
            total_numpy += close_prices[i]
        numpy_time = time.time() - start

        # Numpy should be significantly faster
        # Allow for timer resolution issues on fast systems
        if iloc_time > 1e-6 and numpy_time > 1e-6:
            speedup = iloc_time / numpy_time
            assert speedup > 5, (
                f"Numpy array access not significantly faster: "
                f"iloc={iloc_time:.6f}s, numpy={numpy_time:.6f}s, "
                f"speedup={speedup:.1f}x (expected >5x)"
            )
        else:
            # Times too small to measure reliably, just ensure numpy not slower
            assert numpy_time <= iloc_time * 1.5, (
                f"Numpy slower despite small times: "
                f"iloc={iloc_time:.9f}s, numpy={numpy_time:.9f}s"
            )

        # Verify same results
        assert abs(total_iloc - total_numpy) < 1e-9

    def test_vectorized_column_extraction(self):
        """Test that extracting columns as arrays is efficient."""
        # Create large DataFrame
        n_bars = 5000
        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2025-01-01", periods=n_bars, freq="15min"),
                "open": np.random.randn(n_bars).cumsum() + 100,
                "high": np.random.randn(n_bars).cumsum() + 102,
                "low": np.random.randn(n_bars).cumsum() + 98,
                "close": np.random.randn(n_bars).cumsum() + 100,
                "volume": np.random.randint(100, 1000, n_bars),
            }
        )

        # Measure column extraction time
        start = time.time()
        timestamps = df["timestamp"].values
        close_prices = df["close"].values
        extraction_time = time.time() - start

        # Should be very fast (sub-millisecond for 5000 bars)
        assert (
            extraction_time < 0.01
        ), f"Column extraction too slow: {extraction_time:.6f}s for {n_bars} bars"

        # Verify extracted data
        assert len(timestamps) == n_bars
        assert len(close_prices) == n_bars
        assert isinstance(timestamps, np.ndarray)
        assert isinstance(close_prices, np.ndarray)


class TestCopyOptimizations:
    """Test copy/deepcopy optimizations."""

    def test_primitive_list_copy_vs_deepcopy(self):
        """Verify that shallow list copy is faster than deepcopy for primitives.

        This is a performance guardrail. Comparing per-element deepcopy can be
        surprisingly noisy (deepcopy(float) is effectively a no-op), so we
        compare list-level operations instead.
        """
        import copy
        from time import perf_counter

        # Test with list of primitives (typical grid values)
        primitives = [0.1, 0.2, 0.3, 0.4, 0.5] * 100  # 500 float values

        loops = 200

        start = perf_counter()
        for _ in range(loops):
            _ = copy.deepcopy(primitives)
        deepcopy_time = perf_counter() - start

        start = perf_counter()
        for _ in range(loops):
            _ = primitives.copy()
        copy_time = perf_counter() - start

        # Shallow copy should be faster than recursive deepcopy for primitives.
        if deepcopy_time > 1e-6 and copy_time > 1e-6:
            speedup = deepcopy_time / copy_time
            assert speedup > 1.2, (
                f"Shallow list copy not faster than deepcopy: "
                f"deepcopy={deepcopy_time:.6f}s, copy={copy_time:.6f}s, "
                f"speedup={speedup:.1f}x"
            )

    def test_conditional_deepcopy_for_mixed_types(self):
        """Test conditional deepcopy logic for mixed primitive and mutable types."""
        import copy

        # Primitives don't need deepcopy
        primitives = [1, 2.5, "test", True, None]
        for v in primitives:
            if isinstance(v, dict | list):
                result = copy.deepcopy(v)
            else:
                result = v
            assert result == v

        # Mutable containers do need deepcopy
        nested_dict = {"key": {"nested": [1, 2, 3]}}
        copied = copy.deepcopy(nested_dict)
        copied["key"]["nested"].append(4)
        assert len(nested_dict["key"]["nested"]) == 3  # Original unchanged
        assert len(copied["key"]["nested"]) == 4  # Copy modified
