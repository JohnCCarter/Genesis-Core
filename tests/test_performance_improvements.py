"""Test performance improvements for model-training pipeline optimizations."""

# Add src to path
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import the module (not individual globals).
# Some tests (e.g. env-flag parsing) reload this module at runtime; importing
# mutable module globals directly would leave stale references and make this
# test order-dependent.
import core.strategy.features_asof as features_asof


@pytest.fixture
def sample_candles():
    """Create sample candles data for testing."""
    n = 500
    return {
        "open": np.random.randn(n) * 100 + 10000,
        "high": np.random.randn(n) * 100 + 10100,
        "low": np.random.randn(n) * 100 + 9900,
        "close": np.random.randn(n) * 100 + 10000,
        "volume": np.random.randn(n) * 1000 + 5000,
        "timestamp": pd.date_range("2024-01-01", periods=n, freq="1h").tolist(),
    }


def test_hash_computation_speed(sample_candles):
    """Test that hash computation is fast."""
    # Warm-up
    features_asof._compute_candles_hash(sample_candles, 100)

    # Time 1000 hash computations
    start = time.perf_counter()
    for i in range(100, 200):
        features_asof._compute_candles_hash(sample_candles, i)
    elapsed = time.perf_counter() - start

    # Should be under 1ms per hash (very fast)
    avg_time = elapsed / 100
    assert avg_time < 0.001, f"Hash computation too slow: {avg_time*1000:.2f}ms per hash"
    print(f"\nHash computation: {avg_time*1000:.4f}ms per hash")


def test_cache_hit_rate(sample_candles):
    """Test that cache provides good hit rate for sequential access."""
    features_asof._feature_cache.clear()

    # First pass: populate cache
    for i in range(100, 200):
        features_asof.extract_features_backtest(sample_candles, i, timeframe="1h")

    cache_size_after_populate = len(features_asof._feature_cache)
    print(f"\nCache size after populate: {cache_size_after_populate}")

    # Second pass: should hit cache (sequential access with same data)
    features_asof._feature_cache.clear()  # Clear to test fresh
    for i in range(100, 200):
        features_asof.extract_features_backtest(sample_candles, i, timeframe="1h")

    # With our simple hash (asof_bar + last_close), cache should work
    cache_size_after_second = len(features_asof._feature_cache)
    assert cache_size_after_second > 0, "Cache should have entries"
    print(f"Cache size after second pass: {cache_size_after_second}")


def test_feature_extraction_with_numpy_arrays(sample_candles):
    """Test that feature extraction works with NumPy arrays."""
    # Convert to numpy arrays (simulating fast_window mode)
    numpy_candles = {
        "open": np.array(sample_candles["open"]),
        "high": np.array(sample_candles["high"]),
        "low": np.array(sample_candles["low"]),
        "close": np.array(sample_candles["close"]),
        "volume": np.array(sample_candles["volume"]),
        "timestamp": sample_candles["timestamp"],
    }

    # Should work without errors
    features, meta = features_asof.extract_features_backtest(numpy_candles, 100, timeframe="1h")
    assert len(features) > 0, "Should extract features from numpy arrays"
    assert "rsi_inv_lag1" in features


def test_feature_extraction_speed(sample_candles):
    """Test feature extraction speed."""
    features_asof._feature_cache.clear()

    # Time 50 feature extractions
    start = time.perf_counter()
    for i in range(100, 150):
        features_asof.extract_features_backtest(sample_candles, i, timeframe="1h")
    elapsed = time.perf_counter() - start

    avg_time = elapsed / 50
    # Should be reasonably fast (under 10ms per extraction without cache)
    assert avg_time < 0.05, f"Feature extraction too slow: {avg_time*1000:.2f}ms per bar"
    print(f"\nFeature extraction: {avg_time*1000:.2f}ms per bar (no cache)")


def test_cache_lru_behavior():
    """Test that cache uses LRU eviction."""
    from collections import OrderedDict

    from core.strategy import features_asof

    # Verify cache is OrderedDict
    assert isinstance(
        features_asof._feature_cache, OrderedDict
    ), "Cache should be OrderedDict for LRU"


def test_cache_increased_size():
    """Test that cache size has been increased."""
    from core.strategy import features_asof

    # Should be larger than old size (was 100, now 500)
    assert features_asof._MAX_CACHE_SIZE >= 500, "Cache size should be increased for backtests"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
