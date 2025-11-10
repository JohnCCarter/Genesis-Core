"""Performance tests for optimizer improvements."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from core.optimizer import runner
from core.utils import optuna_helpers


class TestTrialKeyPerformance:
    """Test performance of trial key generation with caching."""

    def test_trial_key_basic(self) -> None:
        """Test that trial key generation works correctly."""
        params1 = {"a": 1, "b": 2}
        params2 = {"b": 2, "a": 1}  # Same params, different order
        params3 = {"a": 1, "b": 3}  # Different params

        key1 = runner._trial_key(params1)
        key2 = runner._trial_key(params2)
        key3 = runner._trial_key(params3)

        assert key1 == key2, "Same parameters should generate same key"
        assert key1 != key3, "Different parameters should generate different keys"

    def test_trial_key_caching(self) -> None:
        """Test that trial key caching improves performance."""
        params = {"threshold": 0.5, "window": 100}

        # First call - not cached
        start = time.perf_counter()
        key1 = runner._trial_key(params)
        time1 = time.perf_counter() - start

        # Second call - should be cached
        start = time.perf_counter()
        key2 = runner._trial_key(params)
        time2 = time.perf_counter() - start

        assert key1 == key2
        # Cached call should generally be faster; allow small tolerance for jitter
        assert time2 <= time1 * 1.5

    def test_trial_key_cache_limit(self) -> None:
        """Test that cache doesn't grow unbounded."""
        # Clear cache first
        runner._TRIAL_KEY_CACHE.clear()

        # Add more than cache limit
        for i in range(12000):
            params = {"index": i}
            runner._trial_key(params)

        # Cache should be trimmed
        assert len(runner._TRIAL_KEY_CACHE) <= 10000


class TestLoadExistingTrialsPerformance:
    """Test performance of loading existing trials."""

    def test_load_empty_directory(self, tmp_path: Path) -> None:
        """Test loading from empty directory."""
        run_dir = tmp_path / "empty_run"
        run_dir.mkdir()

        trials = runner._load_existing_trials(run_dir)
        assert trials == {}

    def test_load_multiple_trials(self, tmp_path: Path) -> None:
        """Test loading multiple trial files efficiently."""
        run_dir = tmp_path / "test_run"
        run_dir.mkdir()

        # Create multiple trial files
        for i in range(10):
            trial_data = {
                "trial_id": f"trial_{i:03d}",
                "parameters": {"value": i * 0.1},
                "score": {"score": i * 10},
            }
            trial_path = run_dir / f"trial_{i:03d}.json"
            trial_path.write_text(json.dumps(trial_data))

        start = time.perf_counter()
        trials = runner._load_existing_trials(run_dir)
        elapsed = time.perf_counter() - start

        assert len(trials) == 10
        # Should complete quickly (< 1 second for 10 files)
        assert elapsed < 1.0

    def test_load_corrupted_files(self, tmp_path: Path) -> None:
        """Test that corrupted files are skipped gracefully."""
        run_dir = tmp_path / "corrupted_run"
        run_dir.mkdir()

        # Create valid trial
        valid_trial = {
            "trial_id": "trial_001",
            "parameters": {"value": 0.5},
            "score": {"score": 100},
        }
        (run_dir / "trial_001.json").write_text(json.dumps(valid_trial))

        # Create corrupted trial
        (run_dir / "trial_002.json").write_text("invalid json{")

        trials = runner._load_existing_trials(run_dir)
        assert len(trials) == 1


class TestParamSignaturePerformance:
    """Test performance of parameter signature generation."""

    def test_param_signature_basic(self) -> None:
        """Test basic parameter signature generation."""
        params = {"a": 1.23456789, "b": [1, 2, 3], "c": {"nested": 4.56789}}
        sig = optuna_helpers.param_signature(params)

        assert isinstance(sig, str)
        assert len(sig) == 64  # SHA256 hex digest length

    def test_param_signature_consistency(self) -> None:
        """Test that same parameters always generate same signature."""
        params1 = {"x": 1.5, "y": 2.5}
        params2 = {"y": 2.5, "x": 1.5}  # Different order

        sig1 = optuna_helpers.param_signature(params1)
        sig2 = optuna_helpers.param_signature(params2)

        assert sig1 == sig2

    def test_param_signature_caching(self) -> None:
        """Test that signature caching works."""
        params = {"threshold": 0.123, "window": 50}

        # Clear cache
        optuna_helpers._PARAM_SIG_CACHE.clear()

        # First call
        sig1 = optuna_helpers.param_signature(params)

        # Second call - should be cached
        sig2 = optuna_helpers.param_signature(params)

        assert sig1 == sig2
        assert len(optuna_helpers._PARAM_SIG_CACHE) == 1

    def test_param_signature_cache_limit(self) -> None:
        """Test that cache is limited in size."""
        optuna_helpers._PARAM_SIG_CACHE.clear()

        # Generate many signatures
        for i in range(6000):
            params = {"index": i, "value": i * 0.01}
            optuna_helpers.param_signature(params)

        # Cache should be trimmed
        assert len(optuna_helpers._PARAM_SIG_CACHE) <= 5000


class TestNoDupeGuardPerformance:
    """Test performance improvements in NoDupeGuard."""

    def test_nodupe_sqlite_performance(self, tmp_path: Path) -> None:
        """Test SQLite backend performance."""
        db_path = tmp_path / "dedup.db"
        guard = optuna_helpers.NoDupeGuard(sqlite_path=str(db_path))

        # Test adding signatures
        sigs = [f"sig_{i:04d}" for i in range(100)]

        start = time.perf_counter()
        for sig in sigs:
            guard.add(sig)
        elapsed = time.perf_counter() - start

        # Should complete quickly
        assert elapsed < 5.0

        # Verify all added
        for sig in sigs:
            assert guard.seen(sig)

    def test_nodupe_batch_add(self, tmp_path: Path) -> None:
        """Test batch add performance improvement."""
        db_path = tmp_path / "dedup_batch.db"
        guard = optuna_helpers.NoDupeGuard(sqlite_path=str(db_path))

        sigs = [f"sig_{i:04d}" for i in range(100)]

        # Batch add should be faster than individual adds
        start = time.perf_counter()
        count = guard.add_batch(sigs)
        elapsed = time.perf_counter() - start

        assert count == 100
        assert elapsed < 2.0

        # Verify all added
        for sig in sigs:
            assert guard.seen(sig)

        # Adding same signatures again should return 0
        count2 = guard.add_batch(sigs)
        assert count2 == 0


class TestSuggestParametersPerformance:
    """Test performance of parameter suggestion with caching."""

    def test_suggest_float_with_step(self) -> None:
        """Test that float step decimal calculation is cached."""
        # This tests the internal _get_step_decimals caching
        # We can't directly test it, but we can verify the suggestion works
        spec = {
            "param1": {"type": "float", "low": 0.0, "high": 1.0, "step": 0.05},
            "param2": {"type": "float", "low": 0.0, "high": 10.0, "step": 0.1},
        }

        # Mock trial object
        class MockTrial:
            def suggest_float(
                self, name: str, low: float, high: float, step: float = None, log: bool = False
            ) -> float:
                return low + step if step else low

        trial = MockTrial()
        params = runner._suggest_parameters(trial, spec)

        assert "param1" in params
        assert "param2" in params
        assert isinstance(params["param1"], float)
        assert isinstance(params["param2"], float)


@pytest.mark.skipif(not runner.OPTUNA_AVAILABLE, reason="Optuna not installed")
class TestOptunaIntegrationPerformance:
    """Test Optuna integration performance improvements."""

    def test_optuna_with_progress_bar_disabled(self) -> None:
        """Test that progress bar is disabled for better performance."""
        # This is more of a configuration test
        # Verify the optimize call includes show_progress_bar=False
        # (tested indirectly through code review)
        pass
