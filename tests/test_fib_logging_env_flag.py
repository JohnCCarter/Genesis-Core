from __future__ import annotations

import importlib


def test_fib_flow_logs_enabled_env_parsing(monkeypatch) -> None:
    import core.strategy.fib_logging as fib_logging

    # Unset -> default False
    monkeypatch.delenv("FIB_FLOW_LOGS_ENABLED", raising=False)
    fib_logging = importlib.reload(fib_logging)
    assert fib_logging.fib_flow_enabled() is False

    # Empty string should behave like unset (regression: previously became True)
    monkeypatch.setenv("FIB_FLOW_LOGS_ENABLED", "")
    fib_logging = importlib.reload(fib_logging)
    assert fib_logging.fib_flow_enabled() is False

    # Explicit falsy tokens
    monkeypatch.setenv("FIB_FLOW_LOGS_ENABLED", "0")
    fib_logging = importlib.reload(fib_logging)
    assert fib_logging.fib_flow_enabled() is False

    monkeypatch.setenv("FIB_FLOW_LOGS_ENABLED", "false")
    fib_logging = importlib.reload(fib_logging)
    assert fib_logging.fib_flow_enabled() is False

    # Truthy values
    monkeypatch.setenv("FIB_FLOW_LOGS_ENABLED", "1")
    fib_logging = importlib.reload(fib_logging)
    assert fib_logging.fib_flow_enabled() is True

    monkeypatch.setenv("FIB_FLOW_LOGS_ENABLED", "yes")
    fib_logging = importlib.reload(fib_logging)
    assert fib_logging.fib_flow_enabled() is True
