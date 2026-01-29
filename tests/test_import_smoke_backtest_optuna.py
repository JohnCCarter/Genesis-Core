"""Dependency smoke tests.

These tests intentionally do not execute backtests or Optuna runs.
They ensure that a plain `pip install .` provides enough dependencies to import
Genesis-Core's offline backtest and optimizer entrypoints.

This protects against dependency drift where modules import third-party packages
that are only declared in optional extras.
"""


def test_imports_for_backtest_and_optuna_smoke() -> None:
    import core.backtest.engine  # noqa: F401
    import core.optimizer.runner  # noqa: F401
    import core.pipeline  # noqa: F401
