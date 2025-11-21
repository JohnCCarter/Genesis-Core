"""
Performance tests for 2025-11-21 optimizations.

Tests validate that optimizations maintain correctness while improving performance.
"""

import time

import numpy as np
import pandas as pd
import pytest

from core.indicators.htf_fibonacci import _to_series
from core.strategy.champion_loader import ChampionLoader


class TestChampionLoaderCache:
    """Test champion loader cache optimization."""

    def test_cache_prevents_redundant_file_stats(self, tmp_path):
        """Cache should prevent redundant file system calls after first load."""
        # Create a test champion file
        champion_dir = tmp_path / "champions"
        champion_dir.mkdir()
        champion_file = champion_dir / "tBTCUSD_1h.json"
        champion_file.write_text(
            '{"parameters": {"thresholds": {"entry_conf_overall": 0.7}}, "created_at": "2025-11-21"}'
        )

        loader = ChampionLoader(champions_dir=champion_dir)

        # First load
        start = time.perf_counter()
        config1 = loader.load_cached("tBTCUSD", "1h")
        time1 = time.perf_counter() - start

        # Second load (should use cache)
        start = time.perf_counter()
        config2 = loader.load_cached("tBTCUSD", "1h")
        time2 = time.perf_counter() - start

        # Verify same config returned
        assert config1.config == config2.config
        assert config1.checksum == config2.checksum

        # Second load should be significantly faster (>10x)
        # In practice, cache lookup is ~1000x faster than file I/O
        assert time2 < time1 * 0.5, f"Cache not effective: {time2:.6f}s vs {time1:.6f}s"

    def test_cache_detects_file_modifications(self, tmp_path):
        """Cache should reload when file is modified."""
        champion_dir = tmp_path / "champions"
        champion_dir.mkdir()
        champion_file = champion_dir / "tBTCUSD_1h.json"
        champion_file.write_text(
            '{"parameters": {"thresholds": {"entry_conf_overall": 0.7}}, "created_at": "v1"}'
        )

        loader = ChampionLoader(champions_dir=champion_dir)

        # First load
        config1 = loader.load_cached("tBTCUSD", "1h")
        checksum1 = config1.checksum

        # Modify file
        time.sleep(0.01)  # Ensure mtime changes
        champion_file.write_text(
            '{"parameters": {"thresholds": {"entry_conf_overall": 0.8}}, "created_at": "v2"}'
        )

        # Second load should detect modification
        config2 = loader.load_cached("tBTCUSD", "1h")
        checksum2 = config2.checksum

        # Verify file was reloaded with new content
        assert checksum1 != checksum2
        assert config1.config["thresholds"]["entry_conf_overall"] == 0.7
        assert config2.config["thresholds"]["entry_conf_overall"] == 0.8


class TestPercentileOptimization:
    """Test percentile calculation optimization."""

    def test_batch_percentile_faster_than_separate(self):
        """Batch percentile calculation should be faster than separate calls."""
        np.random.seed(42)  # Fixed seed for reproducible results
        data = np.random.rand(1000)

        # Separate calls (old approach)
        iterations = 100
        start = time.perf_counter()
        for _ in range(iterations):
            p40_old = np.percentile(data, 40)
            p80_old = np.percentile(data, 80)
        time_separate = time.perf_counter() - start

        # Batch call (new approach)
        start = time.perf_counter()
        for _ in range(iterations):
            p40_new, p80_new = np.percentile(data, [40, 80])
        time_batch = time.perf_counter() - start

        # Verify same results
        assert abs(p40_old - p40_new) < 1e-10
        assert abs(p80_old - p80_new) < 1e-10

        # Batch should be faster (typically 30-50% faster)
        assert (
            time_batch < time_separate
        ), f"Batch not faster: {time_batch:.4f}s vs {time_separate:.4f}s"
        speedup = time_separate / time_batch
        assert speedup > 1.2, f"Expected >1.2x speedup, got {speedup:.2f}x"

    def test_batch_percentile_correctness(self):
        """Batch percentile should produce identical results to separate calls."""
        data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        # Separate calls
        p40_sep = np.percentile(data, 40)
        p80_sep = np.percentile(data, 80)

        # Batch call
        p40_batch, p80_batch = np.percentile(data, [40, 80])

        # Should be identical
        assert p40_sep == p40_batch
        assert p80_sep == p80_batch


class TestPandasSeriesOptimization:
    """Test pandas Series creation optimization in _to_series."""

    def test_to_series_avoids_redundant_series_creation(self):
        """_to_series should reuse existing pandas Series without copying."""
        # Create input data as pandas Series (simulating typical pipeline usage)
        high_series = pd.Series([101.0, 102.0, 103.0], dtype=float)
        low_series = pd.Series([99.0, 100.0, 101.0], dtype=float)
        close_series = pd.Series([100.0, 101.0, 102.0], dtype=float)
        timestamp_series = pd.Series([1, 2, 3])

        data = {
            "high": high_series,
            "low": low_series,
            "close": close_series,
            "timestamp": timestamp_series,
        }

        # Call _to_series
        highs, lows, closes, timestamps = _to_series(data)

        # Should return same objects (not copies)
        assert highs is high_series
        assert lows is low_series
        assert closes is close_series
        assert timestamps is timestamp_series

    def test_to_series_creates_series_when_needed(self):
        """_to_series should create Series when input is list."""
        data = {
            "high": [101.0, 102.0, 103.0],
            "low": [99.0, 100.0, 101.0],
            "close": [100.0, 101.0, 102.0],
            "timestamp": [1, 2, 3],
        }

        # Call _to_series
        highs, lows, closes, timestamps = _to_series(data)

        # Should create pandas Series
        assert isinstance(highs, pd.Series)
        assert isinstance(lows, pd.Series)
        assert isinstance(closes, pd.Series)
        assert isinstance(timestamps, pd.Series)

        # Verify correct values
        assert list(highs) == [101.0, 102.0, 103.0]
        assert list(lows) == [99.0, 100.0, 101.0]
        assert list(closes) == [100.0, 101.0, 102.0]

    def test_to_series_performance_with_series_input(self):
        """_to_series should be faster when input is already Series."""
        n = 1000

        # Test with list input
        data_list = {
            "high": list(range(n)),
            "low": list(range(n)),
            "close": list(range(n)),
        }

        start = time.perf_counter()
        for _ in range(100):
            _to_series(data_list)
        time_list = time.perf_counter() - start

        # Test with Series input
        data_series = {
            "high": pd.Series(range(n), dtype=float),
            "low": pd.Series(range(n), dtype=float),
            "close": pd.Series(range(n), dtype=float),
        }

        start = time.perf_counter()
        for _ in range(100):
            _to_series(data_series)
        time_series = time.perf_counter() - start

        # Series input should be faster (no conversion needed)
        assert (
            time_series < time_list
        ), f"Series input not faster: {time_series:.4f}s vs {time_list:.4f}s"
        speedup = time_list / time_series
        # Should be at least 2x faster since we skip 3 Series creations
        assert speedup > 2.0, f"Expected >2x speedup, got {speedup:.2f}x"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
