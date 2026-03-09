from __future__ import annotations

import importlib

import pytest


@pytest.mark.parametrize(
    ("env_value", "expected"),
    [
        pytest.param(None, False, id="unset-default-false"),
        pytest.param("", False, id="empty-default-false"),
        pytest.param("0", False, id="zero-false"),
        pytest.param("false", False, id="false-token"),
        pytest.param("1", True, id="one-true"),
        pytest.param("yes", True, id="yes-true"),
    ],
)
def test_fib_flow_logs_enabled_env_parsing(monkeypatch, env_value, expected) -> None:
    import core.strategy.fib_logging as fib_logging

    if env_value is None:
        monkeypatch.delenv("FIB_FLOW_LOGS_ENABLED", raising=False)
    else:
        monkeypatch.setenv("FIB_FLOW_LOGS_ENABLED", env_value)

    fib_logging = importlib.reload(fib_logging)
    assert fib_logging.fib_flow_enabled() is expected
