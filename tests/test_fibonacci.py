"""
Tests for Fibonacci indicator module.
"""

import numpy as np
import pandas as pd
import pytest

from src.core.indicators.fibonacci import (
    FibonacciConfig,
    calculate_atr,
    calculate_fibonacci_features,
    calculate_fibonacci_features_vectorized,
    calculate_fibonacci_levels,
    detect_swing_points,
)


class TestFibonacciConfig:
    """Test Fibonacci configuration."""

    def test_default_config(self):
        config = FibonacciConfig()
        assert config.levels == [0.382, 0.5, 0.618, 0.786]
        assert config.weights == {0.382: 0.6, 0.5: 1.0, 0.618: 1.0, 0.786: 0.7}
        assert config.atr_depth == 6.0
        assert config.max_swings == 8
        assert config.min_swings == 3
        assert config.max_lookback == 250


class TestATRCalculation:
    """Test ATR calculation."""

    def test_atr_calculation(self):
        # Create test data
        high = pd.Series([100, 105, 103, 108, 110])
        low = pd.Series([98, 100, 99, 104, 106])
        close = pd.Series([99, 104, 102, 107, 109])

        atr = calculate_atr(high, low, close, period=3)

        # ATR should be positive
        assert len(atr) == 5
        assert all(atr > 0)
        assert not atr.isna().all()


class TestSwingDetection:
    """Test swing point detection."""

    def test_swing_detection_basic(self):
        # Create test data with clear swing points
        n = 100
        high = pd.Series(np.random.randn(n).cumsum() + 100)
        low = high - 2
        close = (high + low) / 2

        # Add clear swing high and low
        high.iloc[30] = high.iloc[30] + 10
        low.iloc[70] = low.iloc[70] - 10

        config = FibonacciConfig(atr_depth=3.0, max_swings=5)
        high_indices, low_indices, high_prices, low_prices = detect_swing_points(
            high, low, close, config
        )

        # Should detect some swing points
        assert isinstance(high_indices, list)
        assert isinstance(low_indices, list)
        assert isinstance(high_prices, list)
        assert isinstance(low_prices, list)

        # Indices should be valid
        if high_indices:
            assert all(0 <= idx < len(high) for idx in high_indices)
        if low_indices:
            assert all(0 <= idx < len(low) for idx in low_indices)


class TestFibonacciLevels:
    """Test Fibonacci level calculation."""

    def test_fibonacci_levels_calculation(self):
        swing_highs = [100, 110, 120]
        swing_lows = [80, 85, 90]
        levels = [0.382, 0.5, 0.618, 0.786]

        fib_levels = calculate_fibonacci_levels(swing_highs, swing_lows, levels)

        # Should calculate levels from most recent swing
        assert len(fib_levels) == len(levels)

        # Most recent swing: high=120, low=90, range=30
        expected_levels = [120 - (30 * level) for level in levels]
        assert fib_levels == expected_levels

    def test_fibonacci_levels_no_swings(self):
        fib_levels = calculate_fibonacci_levels([], [], [0.5, 0.618])
        assert fib_levels == []


class TestFibonacciFeatures:
    """Test Fibonacci feature calculation."""

    def test_fibonacci_features_basic(self):
        config = FibonacciConfig()
        price = 95.0
        fib_levels = [95.5, 95.0, 94.5, 94.0]  # Levels around price
        atr = 1.0
        swing_high = 100.0
        swing_low = 90.0

        features = calculate_fibonacci_features(
            price, fib_levels, atr, config, swing_high, swing_low
        )

        # Check all expected features are present
        expected_features = [
            "fib_dist_min_atr",
            "fib_dist_signed_atr",
            "fib_prox_score",
            "fib0618_prox_atr",
            "fib05_prox_atr",
            "swing_retrace_depth",
        ]

        for feature in expected_features:
            assert feature in features
            assert isinstance(features[feature], int | float)

    def test_fibonacci_features_no_data(self):
        config = FibonacciConfig()
        features = calculate_fibonacci_features(100.0, [], 0.0, config)

        # Should return neutral values
        for value in features.values():
            assert value == 0.0

    def test_swing_retrace_depth(self):
        config = FibonacciConfig()
        price = 95.0
        fib_levels = [95.0]
        atr = 1.0
        swing_high = 100.0
        swing_low = 90.0

        features = calculate_fibonacci_features(
            price, fib_levels, atr, config, swing_high, swing_low
        )

        # Price at 95, swing from 90 to 100
        # Retrace depth = (100 - 95) / (100 - 90) = 0.5
        assert abs(features["swing_retrace_depth"] - 0.5) < 0.001


class TestVectorizedFeatures:
    """Test vectorized Fibonacci feature calculation."""

    def test_vectorized_features_basic(self):
        # Create test DataFrame
        n = 50
        df = pd.DataFrame(
            {
                "high": np.random.randn(n).cumsum() + 100,
                "low": np.random.randn(n).cumsum() + 95,
                "close": np.random.randn(n).cumsum() + 97,
                "volume": np.random.randint(1000, 10000, n),
            }
        )
        df["low"] = df[["high", "low"]].min(axis=1)

        config = FibonacciConfig(atr_depth=3.0, max_swings=3)
        features_df = calculate_fibonacci_features_vectorized(df, config)

        # Check structure
        expected_features = [
            "fib_dist_min_atr",
            "fib_dist_signed_atr",
            "fib_prox_score",
            "fib0618_prox_atr",
            "fib05_prox_atr",
            "swing_retrace_depth",
        ]

        for feature in expected_features:
            assert feature in features_df.columns

        # Check all values are numeric
        assert not features_df.isna().all().all()

        # Check retrace depth is bounded [0, 1]
        retrace_values = features_df["swing_retrace_depth"]
        assert all(retrace_values >= 0.0)
        assert all(retrace_values <= 1.0)


if __name__ == "__main__":
    pytest.main([__file__])
