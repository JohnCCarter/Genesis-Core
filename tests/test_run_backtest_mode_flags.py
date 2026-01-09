from __future__ import annotations

import importlib

import pytest

_run_backtest = importlib.import_module("scripts.run_backtest")
_resolve = _run_backtest._resolve_mode_env_overrides


def test_mode_flags_default_none_no_overrides() -> None:
    assert _resolve(fast_window=None, precompute_features=None) == {}


def test_mode_flags_disable_precompute_disables_fast() -> None:
    assert _resolve(fast_window=None, precompute_features=False) == {
        "GENESIS_PRECOMPUTE_FEATURES": "0",
        "GENESIS_FAST_WINDOW": "0",
    }


def test_mode_flags_disable_fast_disables_precompute() -> None:
    assert _resolve(fast_window=False, precompute_features=None) == {
        "GENESIS_FAST_WINDOW": "0",
        "GENESIS_PRECOMPUTE_FEATURES": "0",
    }


def test_mode_flags_explicit_slow_with_precompute_allowed() -> None:
    # Allowed but can produce a warning later in BacktestEngine due to mixed mode.
    assert _resolve(fast_window=False, precompute_features=True) == {
        "GENESIS_FAST_WINDOW": "0",
        "GENESIS_PRECOMPUTE_FEATURES": "1",
    }


def test_mode_flags_fast_requires_precompute() -> None:
    with pytest.raises(ValueError, match=r"fast-window requires --precompute-features"):
        _resolve(fast_window=True, precompute_features=False)
