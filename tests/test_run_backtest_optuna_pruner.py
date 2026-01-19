from __future__ import annotations

import pytest

try:
    import optuna
except ImportError:  # pragma: no cover
    optuna = None

import scripts.run_backtest as run_backtest


@pytest.mark.skipif(optuna is None, reason="optuna not installed")
def test_select_optuna_pruner_defaults_to_noppruner() -> None:
    pruner = run_backtest._select_optuna_pruner(optuna, None, None)
    assert isinstance(pruner, optuna.pruners.NopPruner)


@pytest.mark.skipif(optuna is None, reason="optuna not installed")
def test_select_optuna_pruner_median() -> None:
    pruner = run_backtest._select_optuna_pruner(optuna, "median", {})
    assert isinstance(pruner, optuna.pruners.MedianPruner)
