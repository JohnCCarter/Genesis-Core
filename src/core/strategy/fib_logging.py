from __future__ import annotations

import logging
import os

from core.utils.logging_redaction import get_logger

_FIB_LOGGER = get_logger("core.strategy.fib_flow")


def _env_flag_true(env_value: str | None, *, default: bool = False) -> bool:
    if env_value is None:
        return default
    return env_value.strip().lower() not in {"0", "false", "off", "no"}


_FIB_FLOW_LOGS_ENABLED = _env_flag_true(os.getenv("FIB_FLOW_LOGS_ENABLED"), default=False)


def fib_flow_enabled() -> bool:
    return _FIB_FLOW_LOGS_ENABLED


def set_fib_flow_enabled(enabled: bool) -> None:
    global _FIB_FLOW_LOGS_ENABLED
    _FIB_FLOW_LOGS_ENABLED = bool(enabled)


def log_fib_flow(
    message: str, *args: object, level: int | None = None, logger: logging.Logger | None = None
) -> None:
    if not _FIB_FLOW_LOGS_ENABLED:
        return
    target_logger = logger or _FIB_LOGGER
    if level is None:
        # If the process is configured with a higher global log level (e.g. LOG_LEVEL=WARNING),
        # INFO may be filtered out even when callers expect fib-flow logging to be visible.
        # Since fib-flow logs are opt-in (via FIB_FLOW_LOGS_ENABLED), fall back to WARNING
        # when INFO is not enabled.
        if target_logger.isEnabledFor(logging.INFO):
            target_logger.info(message, *args)
        else:
            target_logger.warning(message, *args)
    else:
        target_logger.log(level, message, *args)
