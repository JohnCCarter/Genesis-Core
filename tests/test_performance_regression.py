"""
Performance regression tests to ensure optimizations remain effective.

These tests verify that critical performance improvements are maintained.
"""

import time

import pandas as pd
import pytest

from core.indicators.fibonacci import FibonacciConfig, detect_swing_points


class TestSwingDetectionPerformance:
    """Test swing detection performance optimizations."""

    def test_detect_swing_points_performance(self):
        """Verify swing detection completes within reasonable time."""
        # Create test data (200 bars, typical for backtest window)
        dates = pd.date_range("2025-01-01", periods=200, freq="15min")
        data = {
            "high": [100 + i * 0.1 + 0.5 for i in range(200)],
            "low": [100 + i * 0.1 - 0.5 for i in range(200)],
            "close": [100 + i * 0.1 + 0.2 for i in range(200)],
        }

        high = pd.Series(data["high"], index=dates)
        low = pd.Series(data["low"], index=dates)
        close = pd.Series(data["close"], index=dates)

        config = FibonacciConfig()

        # Measure time for 10 iterations (simulating backtest)
        start = time.time()
        for _ in range(10):
            swing_high_idx, swing_low_idx, swing_high_prices, swing_low_prices = (
                detect_swing_points(high, low, close, config)
            )
        elapsed = time.time() - start

        # Should complete 10 iterations in under 0.5 seconds
        # (Before optimization: ~7 seconds for 190 iterations = ~0.037s per call)
        # (After optimization: ~1.5 seconds for 190 iterations = ~0.008s per call)
        # So 10 calls should take < 0.1s, we use 0.5s for safety margin
        assert elapsed < 0.5, f"Swing detection too slow: {elapsed:.3f}s for 10 iterations"

        # Verify results are valid
        assert len(swing_high_idx) > 0
        assert len(swing_low_idx) > 0
        assert len(swing_high_prices) > 0
        assert len(swing_low_prices) > 0

    def test_numpy_array_conversion_benefit(self):
        """Test that numpy array access is faster than pandas iloc."""
        # Create test data
        test_series = pd.Series(range(1000))
        test_array = test_series.values

        # Measure pandas iloc access
        start = time.time()
        total_pandas = 0
        for i in range(100):
            total_pandas += test_series.iloc[i]
        pandas_time = time.time() - start

        # Measure numpy array access
        start = time.time()
        total_numpy = 0
        for i in range(100):
            total_numpy += test_array[i]
        numpy_time = time.time() - start

        # Numpy should be significantly faster (at least 5x) under measurable timings.
        # Om tiderna är extremt små (timerupplösning), acceptera att numpy inte är långsammare.
        eps = 1e-9
        ratio = pandas_time / max(numpy_time, eps)
        if pandas_time < 1e-6 and numpy_time < 1e-6:
            assert numpy_time <= pandas_time, (
                f"Timer resolution too coarse but numpy slower: "
                f"pandas={pandas_time:.9f}s, numpy={numpy_time:.9f}s"
            )
        else:
            assert numpy_time < pandas_time / 5, (
                f"Numpy not faster enough: pandas={pandas_time:.6f}s, "
                f"numpy={numpy_time:.6f}s, ratio={ratio:.1f}x"
            )

        # Verify same results
        assert total_pandas == total_numpy


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
