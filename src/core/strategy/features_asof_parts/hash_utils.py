from __future__ import annotations

import hashlib
import os
from typing import Any

import numpy as np

from core.utils.logging_redaction import get_logger

_log = get_logger(__name__)


def as_config_dict(value: Any, *, logger: Any = None) -> dict[str, Any]:
    active_logger = logger if logger is not None else _log
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        try:
            return value.model_dump()  # type: ignore[return-value]
        except Exception as exc:
            if active_logger:
                active_logger.warning("model_dump fallback to empty dict: %s", exc)
            return {}
    return {}


def safe_series_value(series: list[float] | np.ndarray | None, idx: int) -> float:
    if series is None or idx < 0:
        return 0.0
    try:
        if len(series) <= idx:
            return 0.0
        return float(series[idx])
    except Exception:
        return 0.0


def compute_candles_hash(candles: dict[str, list[float] | np.ndarray], asof_bar: int) -> str:
    """Compute a cache key for candles up to asof_bar.

    Fast path (opt-in): GENESIS_FAST_HASH=1 -> simple f-string on asof_bar:last_close
    Default: deterministic compact digest over a small, representative state.
    """
    # Optional ultra-fast key for tight loops
    if str(os.environ.get("GENESIS_FAST_HASH", "")).strip().lower() in {"1", "true"}:
        try:
            close = candles.get("close")
            last_close = safe_series_value(close, asof_bar)

            # Backwards compatibility: keep legacy shape for close-only minimal inputs.
            if set(candles.keys()) <= {"close"}:
                return f"{asof_bar}:{last_close:.4f}"

            close_len = int(len(close)) if close is not None else 0
            c_prev = safe_series_value(close, asof_bar - 1)
            c_first = safe_series_value(close, 0)
            o_now = safe_series_value(candles.get("open"), asof_bar)
            h_now = safe_series_value(candles.get("high"), asof_bar)
            l_now = safe_series_value(candles.get("low"), asof_bar)
            v_now = safe_series_value(candles.get("volume"), asof_bar)

            import struct

            payload = struct.pack(
                "<qqddddddd",
                int(asof_bar),
                close_len,
                last_close,
                c_prev,
                c_first,
                o_now,
                h_now,
                l_now,
                v_now,
            )
            digest = hashlib.blake2b(payload, digest_size=8).hexdigest()
            return f"{asof_bar}:{last_close:.4f}:{digest}"
        except Exception:
            return f"{asof_bar}:0.0000"

    # Default deterministic key
    # NOTE: Avoid Python's built-in hash() here, because it is salted per process
    # (depends on PYTHONHASHSEED) and would make cache keys non-deterministic across runs.
    # We include asof_bar, last close, and a few sample points to reduce collisions
    # without hashing the entire array.
    try:
        close = candles.get("close")
        high = candles.get("high")
        low = candles.get("low")

        # Sample points: current, -1, -10, -50
        c_now = safe_series_value(close, asof_bar)
        c_prev = safe_series_value(close, asof_bar - 1)
        h_now = safe_series_value(high, asof_bar)
        l_now = safe_series_value(low, asof_bar)

        import struct

        # Pack as bytes to get a deterministic digest across processes.
        payload = struct.pack("<qdddd", int(asof_bar), c_now, c_prev, h_now, l_now)
        return hashlib.blake2b(payload, digest_size=16).hexdigest()
    except Exception:
        # Fallback to robust string construction if something fails
        data_str = f"{asof_bar}"
        for key in ["open", "high", "low", "close", "volume"]:
            if key in candles:
                start_idx = max(0, asof_bar - 99)
                data = candles[key][start_idx : asof_bar + 1]
                length = len(data)
                data_sum = float(np.sum(data)) if length else 0.0
                last_val = float(data[-1]) if length else 0.0
                data_str += f"|{key}:{length}:{data_sum:.2f}:{last_val:.2f}"
        return hashlib.sha256(data_str.encode()).hexdigest()
