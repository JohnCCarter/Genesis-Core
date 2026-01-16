from __future__ import annotations

import logging
import os

from core.utils.env_flags import env_flag_enabled
from core.utils.logging_redaction import get_logger

_FIB_LOGGER = get_logger("core.strategy.fib_flow")


_FIB_FLOW_LOGS_ENABLED = env_flag_enabled(os.getenv("FIB_FLOW_LOGS_ENABLED"), default=False)


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
