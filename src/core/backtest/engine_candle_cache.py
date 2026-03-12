"""
Candle cache and precompute key helpers for the backtest engine.

Extracted from engine.py to isolate stateless utilities from the main engine class.
"""

import hashlib
import json
import os

import pandas as pd

from core.utils.env_flags import env_flag_enabled
from core.utils.logging_redaction import get_logger

_LOGGER = get_logger(__name__)


# B1: On-disk precompute cache versioning.
#
# This guards against silently reusing stale cached indicators/swings after code or
# configuration changes that affect the precomputed outputs.
PRECOMPUTE_SCHEMA_VERSION = 1


def _precompute_cache_key_material() -> str:
    """Return stable cache key material for precomputed features.

    Includes a schema version and the effective precompute feature spec.
    """

    spec = {
        "schema_version": int(PRECOMPUTE_SCHEMA_VERSION),
        "indicators": {
            "atr_periods": [14, 50],
            "ema_periods": [20, 50],
            "rsi_period": 14,
            "bb": {"period": 20, "std_dev": 2.0},
            "adx_period": 14,
        },
        "fib_cfg": {"atr_depth": 3.0, "max_swings": 8, "min_swings": 1},
    }
    canon = json.dumps(spec, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    digest12 = hashlib.sha256(canon.encode("utf-8")).hexdigest()[:12]
    return f"v{int(PRECOMPUTE_SCHEMA_VERSION)}_{digest12}"


def _debug_backtest_enabled() -> bool:
    """Return whether verbose error output should be enabled for backtests."""

    return env_flag_enabled(os.getenv("GENESIS_DEBUG_BACKTEST"), default=False)


class CandleCache:
    def __init__(self, max_size: int = 4):
        self._max_size = max_size
        self._store: dict[tuple[str, str], pd.DataFrame] = {}

    def get(self, key: tuple[str, str]) -> pd.DataFrame | None:
        return self._store.get(key)

    def put(self, key: tuple[str, str], value: pd.DataFrame) -> None:
        if key in self._store:
            self._store[key] = value
            return
        if len(self._store) >= self._max_size:
            oldest_key = next(iter(self._store))
            del self._store[oldest_key]
        self._store[key] = value

    def clear(self) -> None:
        self._store.clear()
