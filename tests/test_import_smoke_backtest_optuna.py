"""Dependency smoke tests.

These tests intentionally do not execute backtests or Optuna runs.
They ensure that a plain `pip install .` provides enough dependencies to import
Genesis-Core's offline backtest and optimizer entrypoints.

This protects against dependency drift where modules import third-party packages
that are only declared in optional extras.
"""

import importlib


def test_imports_for_backtest_and_optuna_smoke() -> None:
    assert importlib.import_module("core.backtest.engine") is not None
    assert importlib.import_module("core.optimizer.runner") is not None
    assert importlib.import_module("core.pipeline") is not None
