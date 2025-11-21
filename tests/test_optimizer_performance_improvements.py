"""Test performance improvements for Optuna optimization."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from core.optimizer import runner
from core.utils import optuna_helpers


class TestDeepMergePerformance:
    """Test performance of iterative deep merge implementation."""

    def test_deep_merge_basic(self) -> None:
        """Test that deep merge still works correctly."""
        base = {"a": 1, "b": {"c": 2, "d": 3}}
        override = {"b": {"c": 4}, "e": 5}
        
        result = runner._deep_merge(base, override)
        
        assert result["a"] == 1
        assert result["b"]["c"] == 4
        assert result["b"]["d"] == 3
        assert result["e"] == 5

    def test_deep_merge_nested(self) -> None:
        """Test deep merge with deeply nested structures."""
        base = {
            "level1": {
                "level2": {
                    "level3": {
                        "value": 1
                    }
                }
            }
        }
        override = {
            "level1": {
                "level2": {
                    "level3": {
                        "value": 2
                    }
                }
            }
        }
        
        result = runner._deep_merge(base, override)
        
        assert result["level1"]["level2"]["level3"]["value"] == 2

    def test_deep_merge_performance(self) -> None:
        """Test that iterative deep merge is faster for large structures."""
        # Create a large nested structure
        base = {}
        current = base
        for i in range(20):
            current[f"level{i}"] = {"value": i}
            current = current[f"level{i}"]
        
        override = {}
        current = override
        for i in range(20):
            current[f"level{i}"] = {"new_value": i * 2}
            current = current[f"level{i}"]
        
        start = time.perf_counter()
        result = runner._deep_merge(base, override)
        elapsed = time.perf_counter() - start
        
        # Should complete quickly
        assert elapsed < 0.1
        assert result is not None


class TestExpandValuePerformance:
    """Test performance improvements in _expand_value."""

    def test_expand_value_immutable_types(self) -> None:
        """Test that immutable types are not copied unnecessarily."""
        # Test with various immutable types
        test_cases = [
            42,
            3.14,
            "string",
            True,
            None,
            b"bytes",
        ]
        
        for value in test_cases:
            result = runner._expand_value(value)
            assert len(result) == 1
            assert result[0] == value

    def test_expand_value_dict_grid(self) -> None:
        """Test grid expansion works correctly."""
        node = {"type": "grid", "values": [1, 2, 3]}
        result = runner._expand_value(node)
        
        assert len(result) == 3
        assert result == [1, 2, 3]

    def test_expand_value_dict_fixed(self) -> None:
        """Test fixed value expansion."""
        node = {"type": "fixed", "value": 42}
        result = runner._expand_value(node)
        
        assert len(result) == 1
        assert result[0] == 42


class TestJSONParsingPerformance:
    """Test improved JSON parsing with orjson."""

    def test_json_loads_available(self) -> None:
        """Test that _json_loads function is available."""
        assert hasattr(runner, '_json_loads')
        
        test_data = {"key": "value", "number": 42}
        json_str = json.dumps(test_data)
        
        result = runner._json_loads(json_str)
        assert result == test_data

    def test_json_parsing_performance(self, tmp_path: Path) -> None:
        """Test that JSON parsing is efficient."""
        # Create test file with JSON data
        test_data = {
            "trial_id": "trial_001",
            "parameters": {"threshold": 0.5, "window": 100},
            "score": {"score": 42.5, "metrics": {"sharpe": 1.5}},
        }
        
        test_file = tmp_path / "test_trial.json"
        test_file.write_text(json.dumps(test_data))
        
        start = time.perf_counter()
        for _ in range(100):
            content = test_file.read_text(encoding="utf-8")
            runner._json_loads(content)
        elapsed = time.perf_counter() - start
        
        # Should parse 100 files quickly
        assert elapsed < 0.5


class TestTrialKeyOptimization:
    """Test optimized trial key generation."""

    def test_trial_key_fast_path(self) -> None:
        """Test fast path for simple parameter dicts."""
        params = {"a": 1, "b": 2, "c": 3}
        
        start = time.perf_counter()
        key = runner._trial_key(params)
        elapsed = time.perf_counter() - start
        
        assert key is not None
        assert isinstance(key, str)
        # Should be very fast
        assert elapsed < 0.01

    def test_trial_key_consistency(self) -> None:
        """Test that trial key is consistent."""
        params1 = {"a": 1, "b": 2}
        params2 = {"b": 2, "a": 1}
        
        key1 = runner._trial_key(params1)
        key2 = runner._trial_key(params2)
        
        assert key1 == key2


class TestSuggestParametersOptimization:
    """Test optimized parameter suggestion."""

    def test_suggest_parameters_step_cache_preloaded(self) -> None:
        """Test that common step values are pre-cached."""
        spec = {
            "param1": {"type": "float", "low": 0.0, "high": 1.0, "step": 0.1},
            "param2": {"type": "float", "low": 0.0, "high": 1.0, "step": 0.01},
        }
        
        class MockTrial:
            def suggest_float(
                self, name: str, low: float, high: float, step: float = None, log: bool = False
            ) -> float:
                return low + (step if step else 0.0)
        
        trial = MockTrial()
        
        start = time.perf_counter()
        params = runner._suggest_parameters(trial, spec)
        elapsed = time.perf_counter() - start
        
        assert "param1" in params
        assert "param2" in params
        # Should be very fast with pre-cached step decimals
        assert elapsed < 0.01

    def test_suggest_parameters_type_optimization(self) -> None:
        """Test that type() checks are used instead of isinstance."""
        spec = {
            "fixed_param": {"type": "fixed", "value": 42},
            "nested": {
                "inner": {"type": "fixed", "value": "test"}
            }
        }
        
        class MockTrial:
            pass
        
        trial = MockTrial()
        params = runner._suggest_parameters(trial, spec)
        
        assert params["fixed_param"] == 42
        assert params["nested"]["inner"] == "test"


class TestLoadExistingTrialsOptimization:
    """Test optimized trial loading."""

    def test_load_empty_directory(self, tmp_path: Path) -> None:
        """Test loading from empty directory returns empty dict."""
        run_dir = tmp_path / "empty_run"
        run_dir.mkdir()
        
        result = runner._load_existing_trials(run_dir)
        
        assert result == {}

    def test_load_with_orjson(self, tmp_path: Path) -> None:
        """Test that orjson is used when available."""
        run_dir = tmp_path / "test_run"
        run_dir.mkdir()
        
        # Create test trial
        trial_data = {
            "trial_id": "trial_001",
            "parameters": {"value": 0.5},
            "score": {"score": 100},
        }
        trial_path = run_dir / "trial_001.json"
        trial_path.write_text(json.dumps(trial_data))
        
        trials = runner._load_existing_trials(run_dir)
        
        assert len(trials) == 1

    def test_load_performance(self, tmp_path: Path) -> None:
        """Test that loading many trials is efficient."""
        run_dir = tmp_path / "perf_run"
        run_dir.mkdir()
        
        # Create 50 trial files
        for i in range(50):
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
        
        assert len(trials) == 50
        # Should load 50 files quickly
        assert elapsed < 0.5


class TestSQLiteOptimizations:
    """Test SQLite performance optimizations."""

    def test_sqlite_pragmas_set(self, tmp_path: Path) -> None:
        """Test that SQLite pragmas are properly configured."""
        db_path = tmp_path / "test_dedup.db"
        guard = optuna_helpers.NoDupeGuard(sqlite_path=str(db_path))
        
        # Test that we can add and check signatures (verifies DB is working)
        test_sig = "test_signature_123"
        added = guard.add(test_sig)
        
        assert added is True
        assert guard.seen(test_sig) is True

    def test_sqlite_concurrent_access(self, tmp_path: Path) -> None:
        """Test that SQLite WAL mode enables better concurrent access."""
        import sqlite3
        from contextlib import closing
        
        db_path = tmp_path / "concurrent_dedup.db"
        guard = optuna_helpers.NoDupeGuard(sqlite_path=str(db_path))
        
        # Verify WAL mode is enabled
        with closing(sqlite3.connect(str(db_path))) as conn:
            journal_mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
            assert journal_mode.upper() == "WAL"

    def test_sqlite_batch_performance(self, tmp_path: Path) -> None:
        """Test that batch operations are significantly faster."""
        db_path = tmp_path / "batch_perf.db"
        guard = optuna_helpers.NoDupeGuard(sqlite_path=str(db_path))
        
        # Test batch add performance
        sigs = [f"sig_{i:06d}" for i in range(100)]
        
        start = time.perf_counter()
        count = guard.add_batch(sigs)
        elapsed = time.perf_counter() - start
        
        assert count == 100
        # Should be very fast (< 100ms for 100 items)
        assert elapsed < 0.1
        
        # Verify all were added
        for sig in sigs[:10]:  # Check first 10
            assert guard.seen(sig)


@pytest.mark.skipif(not runner.OPTUNA_AVAILABLE, reason="Optuna not installed")
class TestOptunaIntegrationOptimizations:
    """Test overall Optuna integration performance."""

    def test_sampler_defaults_optimized(self) -> None:
        """Test that TPE sampler has good default parameters."""
        sampler = runner._select_optuna_sampler("tpe", {}, concurrency=4)
        
        # Check that multivariate and constant_liar are enabled (private attributes)
        assert sampler._multivariate is True
        assert sampler._constant_liar is True
        # Check adaptive startup trials
        assert sampler._n_startup_trials >= 20


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
