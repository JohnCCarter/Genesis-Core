import importlib
import logging
import sys

MODULE = "core.strategy.fib_logging"


def _reload_module(monkeypatch, env_value: str | None):
    if env_value is None:
        monkeypatch.delenv("FIB_FLOW_LOGS_ENABLED", raising=False)
    else:
        monkeypatch.setenv("FIB_FLOW_LOGS_ENABLED", env_value)
    if MODULE in sys.modules:
        del sys.modules[MODULE]
    return importlib.import_module(MODULE)


def test_fib_logging_disabled_by_default(monkeypatch, caplog):
    fib_logging = _reload_module(monkeypatch, None)
    with caplog.at_level(logging.INFO, logger="core.strategy.fib_flow"):
        fib_logging.log_fib_flow("should not appear")
    assert "should not appear" not in caplog.text


def test_fib_logging_enabled_via_env(monkeypatch, caplog):
    fib_logging = _reload_module(monkeypatch, "1")
    with caplog.at_level(logging.INFO, logger="core.strategy.fib_flow"):
        fib_logging.log_fib_flow("fib flow active")
    assert "fib flow active" in caplog.text


def test_fib_logging_runtime_toggle(monkeypatch, caplog):
    fib_logging = _reload_module(monkeypatch, None)
    fib_logging.set_fib_flow_enabled(True)
    with caplog.at_level(logging.INFO, logger="core.strategy.fib_flow"):
        fib_logging.log_fib_flow("runtime toggle")
    assert "runtime toggle" in caplog.text
    fib_logging.set_fib_flow_enabled(False)
    caplog.clear()
    with caplog.at_level(logging.INFO, logger="core.strategy.fib_flow"):
        fib_logging.log_fib_flow("should disappear")
    assert "should disappear" not in caplog.text
