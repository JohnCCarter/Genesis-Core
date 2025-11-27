"""Tests for duplicate and zero-trade fixes in optimizer runner."""

from __future__ import annotations

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
