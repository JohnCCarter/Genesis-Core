from __future__ import annotations

import logging
import os
import re
from typing import Any

SENSITIVE_KEYS = {
    "bfx-apikey",
    "bfx-signature",
    "apiKey",
    "apiSecret",
    "BITFINEX_API_KEY",
    "BITFINEX_API_SECRET",
}


def _mask(value: Any) -> Any:
    try:
        s = str(value)
    except Exception:
        return "***"
    if not s:
        return s
    # Visa högst 3 första tecken för felsökning, annars maska helt
    return (s[:3] + "...") if len(s) > 6 else "***"


def redact_mapping(data: dict[str, Any]) -> dict[str, Any]:
    """Returnera en ny dict där kända känsliga nycklar maskas."""
    redacted: dict[str, Any] = {}
    for k, v in data.items():
        if k in SENSITIVE_KEYS:
            redacted[k] = _mask(v)
        else:
            redacted[k] = v
    return redacted


_KV_PATTERNS = [
    re.compile(r"(bfx-apikey\s*:\s*)([^\s]+)", re.IGNORECASE),
    re.compile(r"(bfx-signature\s*:\s*)([^\s]+)", re.IGNORECASE),
    re.compile(r"(apiKey\s*[:=]\s*)([^\s]+)", re.IGNORECASE),
    re.compile(r"(apiSecret\s*[:=]\s*)([^\s]+)", re.IGNORECASE),
]


def redact_text(text: str) -> str:
    """Maskera kända känsliga nycklar i en fri textsträng."""
    if not text:
        return text
    out = text
    for pat in _KV_PATTERNS:
        out = pat.sub(lambda m: m.group(1) + "***", out)
    return out


def _parse_log_level(raw_level: str | None, fallback: int = logging.INFO) -> int:
    if not raw_level:
        return fallback
    # Tillåt "INFO,DEBUG" genom att välja den mest detaljerade nivån
    parts = [segment.strip() for segment in raw_level.split(",") if segment.strip()]
    candidate = parts[-1] if parts else raw_level.strip()
    level_value = getattr(logging, candidate.upper(), None)
    if isinstance(level_value, int):
        return level_value
    return fallback


_EFFECTIVE_LOG_LEVEL = _parse_log_level(os.getenv("CORE_LOG_LEVEL") or os.getenv("LOG_LEVEL"))


class RedactionFilter(logging.Filter):
    """Logging-filter som maskerar kända känsligheter i msg/args."""

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: D401
        try:
            # Hämta färdigformateterad text (msg % args), maskera, nolla args
            try:
                formatted = record.getMessage()
            except Exception:
                formatted = str(record.msg)
            record.msg = redact_text(formatted)
            record.args = ()
        except (TypeError, ValueError, AttributeError) as redaction_err:
            # Maskeringsfel får inte stoppa loggning – logga låg nivå och fortsätt
            logging.getLogger("redaction").debug("redaction_error: %s", redaction_err)
        return True


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not any(isinstance(f, RedactionFilter) for f in logger.filters):
        logger.addFilter(RedactionFilter())
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        logger.addHandler(handler)
    logger.setLevel(_EFFECTIVE_LOG_LEVEL)
    return logger
