"""Tests for duplicate and zero-trade fixes in optimizer runner."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import yaml

try:
    import optuna

    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False

from core.optimizer.runner import _estimate_optuna_search_space, _run_optuna, run_optimizer


def test_estimate_search_space_narrow():
    """Test detection of narrow search spaces."""
    spec = {
        "param1": {"type": "grid", "values": [1, 2]},
        "param2": {"type": "fixed", "value": 10},
        "param3": {"type": "grid", "values": [0.5, 0.6]},
    }

    result = _estimate_optuna_search_space(spec)

    assert result["discrete_params"] == 3
    assert result["continuous_params"] == 0
    assert result["total_discrete_combinations"] == 4  # 2 * 1 * 2
    assert len(result["potential_issues"]) > 0
    assert any("small" in issue.lower() for issue in result["potential_issues"])


def test_estimate_search_space_with_continuous():
    """Test search space with continuous parameters."""
    spec = {
        "discrete": {"type": "grid", "values": [1, 2, 3]},
        "continuous": {"type": "float", "low": 0.0, "high": 1.0},
    }

    result = _estimate_optuna_search_space(spec)

    assert result["discrete_params"] == 1
    assert result["continuous_params"] == 1
    assert result["total_discrete_combinations"] is None  # Has continuous
    assert result["param_choice_counts"]["discrete"] == 3
    assert result["param_choice_counts"]["continuous"] == -1


def test_estimate_search_space_with_steps():
    """Test search space with stepped float parameters."""
    spec = {
        "stepped": {
            "type": "float",
            "low": 0.0,
            "high": 1.0,
            "step": 0.1,
        },
    }

    result = _estimate_optuna_search_space(spec)

    # (1.0 - 0.0) / 0.1 + 1 = 11 steps
    assert result["param_choice_counts"]["stepped"] == 11
    assert result["discrete_params"] == 1


def test_estimate_search_space_nested():
    """Test search space estimation with nested parameters."""
    spec = {
        "thresholds": {
            "entry_conf": {"type": "float", "low": 0.3, "high": 0.5, "step": 0.1},
            "exit_conf": {"type": "fixed", "value": 0.4},
        },
        "risk": {
            "multiplier": {"type": "grid", "values": [1.0, 1.5, 2.0]},
        },
    }

    result = _estimate_optuna_search_space(spec)

    assert result["discrete_params"] == 3
    # entry_conf: 3 steps (0.3, 0.4, 0.5), exit_conf: 1, multiplier: 3
    # Total: 3 * 1 * 3 = 9
    assert result["total_discrete_combinations"] == 9


@pytest.mark.skipif(not OPTUNA_AVAILABLE, reason="Optuna not installed")
def test_duplicate_tracking_in_objective(tmp_path: Path):
    """Test that duplicates and zero-trades are tracked properly."""
    run_dir = tmp_path / "test_run"
    run_dir.mkdir(parents=True)

    # Mock trial data with duplicates and zero trades
    trial_results = [
        {  # Trial 1: valid with trades
            "trial_id": "trial_001",
            "parameters": {"param1": 0.5},
            "score": {"score": 10.0, "metrics": {"num_trades": 5}},
            "constraints": {"ok": True},
        },
        {  # Trial 2: duplicate parameters
            "trial_id": "trial_002",
            "parameters": {"param1": 0.5},
            "skipped": True,
            "reason": "duplicate_within_run",
        },
        {  # Trial 3: zero trades
            "trial_id": "trial_003",
            "parameters": {"param1": 0.6},
            "score": {"score": -95.0, "metrics": {"num_trades": 0}},
            "constraints": {"ok": True},
        },
    ]

    trial_idx = [0]

    def mock_make_trial(
        idx: int, params: dict[str, Any], **kwargs
    ) -> dict[str, Any]:  # Accept optuna_context
        result = trial_results[trial_idx[0]].copy()
        result["parameters"] = params
        trial_idx[0] += 1
        return result

    study_config = {
        "storage": None,
        "study_name": "test_study",
        "sampler": {"name": "random"},
        "pruner": {"name": "none"},
        "dedup_guard_enabled": False,  # Disable SQLite guard for tests
    }

    params_spec = {
        "param1": {"type": "grid", "values": [0.5, 0.6, 0.7]},
    }

    with patch("core.optimizer.runner.optuna") as mock_optuna:
        mock_study = MagicMock()
        mock_study.study_name = "test_study"
        mock_study.trials = []
        mock_study.best_trials = []

        # Track calls to objective
        objective_calls = []

        def mock_optimize(objective, **kwargs):
            # Simulate calling objective 3 times
            for i in range(3):
                trial = MagicMock()
                trial.number = i
                trial.user_attrs = {}

                # Create a proper closure that binds to THIS trial's user_attrs
                def make_setter(attrs_dict):
                    def setter(k, v):
                        attrs_dict[k] = v

                    return setter

                trial.set_user_attr = make_setter(trial.user_attrs)
                trial.suggest_categorical = MagicMock(
                    return_value=[0.5, 0.5, 0.6][i]  # 2 duplicates
                )

                try:
                    score = objective(trial)
                    objective_calls.append((trial, score, None))
                except Exception as e:
                    objective_calls.append((trial, None, e))

        mock_study.optimize = mock_optimize
        mock_optuna.create_study = MagicMock(return_value=mock_study)
        mock_optuna.exceptions = optuna.exceptions

        with patch("core.optimizer.runner._create_optuna_study", return_value=mock_study):
            _run_optuna(
                study_config=study_config,
                parameters_spec=params_spec,
                make_trial=mock_make_trial,
                run_dir=run_dir,
                run_id="test_run",
                existing_trials={},
                max_trials=3,
                concurrency=1,
                allow_resume=False,
            )

    # Verify diagnostics were captured
    assert len(objective_calls) == 3

    # Check that duplicate was detected
    duplicate_trial = objective_calls[1][0]
    assert duplicate_trial.user_attrs.get("duplicate") is True
    assert duplicate_trial.user_attrs.get("penalized_duplicate") is True

    # Check that zero trades was detected
    zero_trade_trial = objective_calls[2][0]
    assert zero_trade_trial.user_attrs.get("zero_trades") is True


@pytest.mark.skipif(not OPTUNA_AVAILABLE, reason="Optuna not installed")
def test_pruned_payload_is_marked_pruned(tmp_path: Path):
    """A payload with error='pruned' should translate to an Optuna TrialPruned."""

    run_dir = tmp_path / "test_run"
    run_dir.mkdir(parents=True)

    def mock_make_trial(idx: int, params: dict[str, Any], **kwargs) -> dict[str, Any]:
        return {
            "trial_id": f"trial_{idx:03d}",
            "parameters": params,
            "results_path": "dummy.json",
            "error": "pruned",
            "pruned_at": 200,
        }

    study_config = {
        "storage": None,
        "study_name": "test_study",
        "sampler": {"name": "random"},
        "pruner": {"name": "none"},
        "dedup_guard_enabled": False,
    }

    params_spec = {
        "param1": {"type": "grid", "values": [0.5]},
    }

    with patch("core.optimizer.runner.optuna") as mock_optuna:
        mock_study = MagicMock()
        mock_study.study_name = "test_study"
        mock_study.trials = []
        mock_study.best_trials = []

        def mock_optimize(objective, **kwargs):
            trial = MagicMock()
            trial.number = 0
            trial._trial_id = 123
            trial.user_attrs = {}

            def setter(k, v):
                trial.user_attrs[k] = v

            trial.set_user_attr = setter
            trial.suggest_categorical = MagicMock(return_value=0.5)
            with pytest.raises(optuna.TrialPruned):
                objective(trial)

        mock_study.optimize = mock_optimize
        mock_optuna.create_study = MagicMock(return_value=mock_study)
        mock_optuna.exceptions = optuna.exceptions
        mock_optuna.TrialPruned = optuna.TrialPruned

        with patch("core.optimizer.runner._create_optuna_study", return_value=mock_study):
            _run_optuna(
                study_config=study_config,
                parameters_spec=params_spec,
                make_trial=mock_make_trial,
                run_dir=run_dir,
                run_id="test_run",
                existing_trials={},
                max_trials=1,
                concurrency=1,
                allow_resume=False,
            )


def test_best_trial_payload_saved_on_constraints_soft_fail(tmp_path):
    pytest.importorskip("optuna")

    # Import here to avoid importing Optuna-dependent code when optuna isn't installed.
    from core.optimizer.runner import _run_optuna

    run_dir = tmp_path / "run"
    run_dir.mkdir(parents=True, exist_ok=True)

    # Minimal Optuna config: 1 trial, no pruner, sqlite storage under tmp_path.
    study_config = {
        "storage": f"sqlite:///{(tmp_path / 'optuna_test.db').as_posix()}",
        "study_name": "test_best_trial_payload_saved",
        "direction": "maximize",
        "sampler": {"name": "random", "kwargs": {"seed": 42}},
        "pruner": {"name": "none", "kwargs": {}},
        "timeout_seconds": None,
        "dedup_guard_enabled": False,
    }

    # Minimal search space: fixed value to avoid any randomness in parameters.
    parameters_spec = {"foo": {"type": "fixed", "value": 1}}

    def make_trial(trial_number, parameters, optuna_context=None):
        # Return a payload that triggers the soft-constraints early return path.
        return {
            "trial_id": f"trial_{trial_number:03d}",
            "parameters": parameters,
            "constraints": {"ok": False, "reasons": ["min_trades:0<50"]},
            "score": {"score": 123.0, "metrics": {"num_trades": 0}, "hard_failures": []},
        }

    _run_optuna(
        study_config=study_config,
        parameters_spec=parameters_spec,
        make_trial=make_trial,
        run_dir=run_dir,
        run_id="run_test_best_payload",
        existing_trials={},
        max_trials=1,
        concurrency=1,
        allow_resume=False,
    )

    # Regression check: best_trial.json should be written even if all trials are soft-fails.
    assert (run_dir / "best_trial.json").exists(), "Expected best_trial.json to be written"


@pytest.mark.skipif(not OPTUNA_AVAILABLE, reason="Optuna not installed")
def test_end_at_sets_effective_timeout(tmp_path: Path):
    """end_at should translate to a finite (computed) timeout passed to Optuna."""

    run_dir = tmp_path / "run"
    run_dir.mkdir(parents=True, exist_ok=True)

    captured: dict[str, Any] = {}

    study = MagicMock()
    study.study_name = "test_end_at"
    study.trials = []
    study.best_trials = []

    def mock_optimize(objective, **kwargs):
        captured.update(kwargs)

    study.optimize = mock_optimize

    # Deadline soon (but not too soon) so the test doesn't flap on slower machines.
    end_at = (datetime.now(tz=UTC) + timedelta(seconds=30)).isoformat()

    study_config = {
        "storage": None,
        "study_name": "test_end_at",
        "sampler": {"name": "random"},
        "pruner": {"name": "none"},
        "timeout_seconds": 10_000,
        "end_at": end_at,
        "dedup_guard_enabled": False,
    }

    params_spec = {"param1": {"type": "fixed", "value": 1}}

    def make_trial(idx: int, params: dict[str, Any], **kwargs) -> dict[str, Any]:
        return {
            "trial_id": f"trial_{idx:03d}",
            "parameters": params,
            "score": {"score": 1.0, "metrics": {"num_trades": 1}, "hard_failures": []},
            "constraints": {"ok": True},
        }

    with patch("core.optimizer.runner._create_optuna_study", return_value=study):
        _run_optuna(
            study_config=study_config,
            parameters_spec=params_spec,
            make_trial=make_trial,
            run_dir=run_dir,
            run_id="run_test_end_at",
            existing_trials={},
            max_trials=1,
            concurrency=1,
            allow_resume=False,
        )

    assert captured.get("timeout") is not None
    assert 0 < int(captured["timeout"]) <= 30


def test_tpe_sampler_defaults():
    """Test that TPE sampler gets better defaults."""
    from core.optimizer.runner import _select_optuna_sampler

    if not OPTUNA_AVAILABLE:
        pytest.skip("Optuna not installed")

    # Default TPE should have improved settings
    sampler = _select_optuna_sampler("tpe", {})

    assert hasattr(sampler, "_multivariate")
    assert hasattr(sampler, "_constant_liar")

    # Check that our defaults were applied
    # Note: TPESampler stores these as private attrs
    assert sampler._n_startup_trials == 25
    assert sampler._n_ei_candidates == 48


def test_tpe_sampler_respects_user_config():
    """Test that user-provided TPE config overrides defaults."""
    from core.optimizer.runner import _select_optuna_sampler

    if not OPTUNA_AVAILABLE:
        pytest.skip("Optuna not installed")

    # User config should override defaults
    sampler = _select_optuna_sampler(
        "tpe",
        {
            "n_startup_trials": 10,
            "multivariate": False,
        },
    )

    assert sampler._n_startup_trials == 10
    # multivariate should be user's choice
    # n_ei_candidates should still use default since not specified
    assert sampler._n_ei_candidates == 48


@pytest.mark.skipif(not OPTUNA_AVAILABLE, reason="Optuna not installed")
def test_optimizer_warns_on_narrow_space(tmp_path: Path, capsys):
    """Test that optimizer warns when search space is narrow."""
    config = {
        "meta": {
            "symbol": "tTEST",
            "timeframe": "1h",
            "snapshot_id": "tTEST_1h_20240101_20240201_v1",
            "runs": {
                "strategy": "optuna",
                "max_trials": 2,
                "max_concurrent": 1,
                "resume": False,
                "optuna": {"storage": None, "study_name": "test-study"},
            },
        },
        "parameters": {
            "param1": {"type": "grid", "values": [0.5, 0.6]},  # Only 2 choices
            "param2": {"type": "fixed", "value": 10},
        },
    }

    config_path = tmp_path / "narrow.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    with (
        patch("core.optimizer.runner.RESULTS_DIR", tmp_path / "results"),
        patch("core.optimizer.runner._ensure_run_metadata"),
        patch("core.optimizer.runner.run_trial") as mock_trial,
        patch("core.optimizer.runner._create_optuna_study") as mock_study,
    ):
        mock_trial.return_value = {
            "trial_id": "trial_001",
            "parameters": {"param1": 0.5, "param2": 10},
            "score": {"score": 1.0, "metrics": {}, "hard_failures": []},
            "constraints": {"ok": True},
        }

        study = MagicMock()
        study.study_name = "test-study"
        study.trials = []
        study.best_trials = []
        study.optimize = MagicMock()
        mock_study.return_value = study

        run_optimizer(config_path, run_id="test_narrow")

        captured = capsys.readouterr()
        assert "Search space warnings" in captured.out
        assert "small" in captured.out.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
