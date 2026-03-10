from __future__ import annotations


def test_backtest_debug_env_flag_parsing(monkeypatch) -> None:
    # Import module once (helper reads env at call time, not import time).
    from core.backtest import engine as engine_mod

    monkeypatch.delenv("GENESIS_DEBUG_BACKTEST", raising=False)
    assert engine_mod._debug_backtest_enabled() is False

    monkeypatch.setenv("GENESIS_DEBUG_BACKTEST", "")
    assert engine_mod._debug_backtest_enabled() is False

    monkeypatch.setenv("GENESIS_DEBUG_BACKTEST", "0")
    assert engine_mod._debug_backtest_enabled() is False

    monkeypatch.setenv("GENESIS_DEBUG_BACKTEST", "false")
    assert engine_mod._debug_backtest_enabled() is False

    monkeypatch.setenv("GENESIS_DEBUG_BACKTEST", "1")
    assert engine_mod._debug_backtest_enabled() is True

    monkeypatch.setenv("GENESIS_DEBUG_BACKTEST", "yes")
    assert engine_mod._debug_backtest_enabled() is True
