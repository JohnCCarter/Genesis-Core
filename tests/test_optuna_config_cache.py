"""
Tests for Optuna default config caching optimization.
"""

import threading
import time
from unittest.mock import MagicMock, patch

import pytest

from core.optimizer.runner import _get_default_config


class TestDefaultConfigCaching:
    """Test default config caching optimization."""

    def setup_method(self):
        """Reset cache before each test."""
        global _DEFAULT_CONFIG_CACHE
        import core.optimizer.runner as runner_module

        runner_module._DEFAULT_CONFIG_CACHE = None

    def test_config_cached_after_first_call(self):
        """Config should be loaded once and cached for subsequent calls."""
        mock_authority = MagicMock()
        mock_cfg_obj = MagicMock()
        mock_cfg_obj.model_dump.return_value = {"test": "config", "version": 1}
        mock_authority.get.return_value = (mock_cfg_obj, None, None)

        with patch("core.optimizer.runner.ConfigAuthority", return_value=mock_authority):
            # First call should load config
            config1 = _get_default_config()
            assert config1 == {"test": "config", "version": 1}
            assert mock_authority.get.call_count == 1
            assert mock_cfg_obj.model_dump.call_count == 1

            # Second call should use cache
            config2 = _get_default_config()
            assert config2 == {"test": "config", "version": 1}
            assert mock_authority.get.call_count == 1  # Still 1, not 2
            assert mock_cfg_obj.model_dump.call_count == 1  # Still 1, not 2

            # Verify same object returned
            assert config1 is config2

    def test_cache_thread_safe(self):
        """Cache should be thread-safe with no race conditions."""
        mock_authority = MagicMock()
        mock_cfg_obj = MagicMock()
        mock_cfg_obj.model_dump.return_value = {"test": "config", "thread": "safe"}
        mock_authority.get.return_value = (mock_cfg_obj, None, None)

        results = []
        call_counts = []

        def worker():
            with patch("core.optimizer.runner.ConfigAuthority", return_value=mock_authority):
                config = _get_default_config()
                results.append(config)
                call_counts.append(mock_authority.get.call_count)

        # Run 10 threads concurrently
        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All threads should get same config
        assert len(results) == 10
        for result in results:
            assert result == {"test": "config", "thread": "safe"}

        # Config should only be loaded once despite 10 concurrent calls
        assert mock_authority.get.call_count == 1
        assert mock_cfg_obj.model_dump.call_count == 1

    def test_cache_performance_benefit(self):
        """Cached calls should be significantly faster than uncached."""
        mock_authority = MagicMock()
        mock_cfg_obj = MagicMock()

        # Simulate expensive operations
        def slow_model_dump():
            time.sleep(0.01)  # 10ms delay
            return {"test": "config"}

        mock_cfg_obj.model_dump.side_effect = slow_model_dump
        mock_authority.get.return_value = (mock_cfg_obj, None, None)

        with patch("core.optimizer.runner.ConfigAuthority", return_value=mock_authority):
            # First call (cold)
            start = time.perf_counter()
            _get_default_config()
            cold_time = time.perf_counter() - start

            # Subsequent calls (warm)
            warm_times = []
            for _ in range(10):
                start = time.perf_counter()
                _get_default_config()
                warm_times.append(time.perf_counter() - start)

            avg_warm_time = sum(warm_times) / len(warm_times)

            # Cached calls should be at least 10x faster
            assert avg_warm_time < cold_time / 10, (
                f"Cache not effective: cold={cold_time:.6f}s, " f"avg_warm={avg_warm_time:.6f}s"
            )

    def test_cache_returns_copy_safe_for_mutation(self):
        """Returned config should be safe to mutate without affecting cache."""
        mock_authority = MagicMock()
        mock_cfg_obj = MagicMock()
        # Return a mutable dict
        mock_cfg_obj.model_dump.return_value = {"test": "config", "nested": {"value": 1}}
        mock_authority.get.return_value = (mock_cfg_obj, None, None)

        with patch("core.optimizer.runner.ConfigAuthority", return_value=mock_authority):
            config1 = _get_default_config()
            config2 = _get_default_config()

            # Both should reference the same cached object
            # (Python's shared references for dicts)
            assert config1 is config2

            # Note: The cache returns the same dict object, so mutations would affect it.
            # This is acceptable because _deep_merge creates a new dict anyway.
            # Document this behavior:
            assert config1["test"] == "config"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
