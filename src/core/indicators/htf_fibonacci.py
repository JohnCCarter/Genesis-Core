"""Higher Timeframe (HTF) Fibonacci public facade.

This module preserves the historical public API while delegating the main
responsibilities to smaller sibling modules.
"""

import math
from collections.abc import Sequence
from typing import Any

import numpy as np
import pandas as pd

from core.indicators.fibonacci import (
    FibonacciConfig,
    calculate_fibonacci_levels,
    detect_swing_points,
)
from core.indicators.htf_fibonacci_compute import (
    compute_htf_fibonacci_levels,
    get_swings_as_of,
)
from core.indicators.htf_fibonacci_context import (
    MAX_HTF_AGE_HOURS,
    _normalize_timestamp,
    get_htf_fibonacci_context_impl,
)
from core.indicators.htf_fibonacci_data import (
    _candles_cache,
    _htf_context_cache,
    load_candles_data,
)
from core.indicators.htf_fibonacci_mapping import compute_htf_fibonacci_mapping_impl

__all__ = [
    "MAX_HTF_AGE_HOURS",
    "_candles_cache",
    "_htf_context_cache",
    "_normalize_timestamp",
    "_to_series",
    "compute_htf_fibonacci_levels",
    "compute_htf_fibonacci_mapping",
    "get_htf_fibonacci_context",
    "get_ltf_fibonacci_context",
    "get_swings_as_of",
    "load_candles_data",
]


def compute_htf_fibonacci_mapping(
    htf_candles: pd.DataFrame,
    ltf_candles: pd.DataFrame,
    config: FibonacciConfig | None = None,
) -> pd.DataFrame:
    """Public facade wrapper that preserves monkeypatch compatibility."""
    return compute_htf_fibonacci_mapping_impl(
        htf_candles,
        ltf_candles,
        config,
        compute_levels_fn=compute_htf_fibonacci_levels,
    )


# --- HELPER FUNCTIONS ---


def _to_series(data: dict) -> tuple:
    """
    Convert candles dict to pandas Series.

    Optimized to reuse existing Series without copying.

    Args:
        data: Dict with 'high', 'low', 'close', 'timestamp' keys

    Returns:
        Tuple of (highs, lows, closes, timestamps) as pandas Series
    """
    high = data.get("high")
    low = data.get("low")
    close = data.get("close")
    timestamp = data.get("timestamp")

    # Reuse existing Series if already pandas Series
    highs = high if isinstance(high, pd.Series) else pd.Series(high, dtype=float)
    lows = low if isinstance(low, pd.Series) else pd.Series(low, dtype=float)
    closes = close if isinstance(close, pd.Series) else pd.Series(close, dtype=float)
    timestamps = timestamp if isinstance(timestamp, pd.Series) else pd.Series(timestamp)

    return highs, lows, closes, timestamps


def get_htf_fibonacci_context(
    ltf_candles: Any,
    timeframe: str,
    symbol: str = "tBTCUSD",
    htf_timeframe: str = "1D",
    config: FibonacciConfig | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Public facade wrapper that preserves cache and monkeypatch compatibility."""
    return get_htf_fibonacci_context_impl(
        ltf_candles,
        timeframe,
        symbol,
        htf_timeframe,
        config,
        htf_context_cache=_htf_context_cache,
        load_candles_data_fn=load_candles_data,
        compute_htf_fibonacci_levels_fn=compute_htf_fibonacci_levels,
        normalize_timestamp_fn=_normalize_timestamp,
        max_htf_age_hours=MAX_HTF_AGE_HOURS,
        **kwargs,
    )


def get_ltf_fibonacci_context(*args, **kwargs) -> dict[str, Any]:
    """Compute same-timeframe Fibonacci context for entry/exit gating.

    This function is *as-of safe* by construction: it only uses the candles passed
    in by the caller.

    Expected caller format (from `features_asof.py`):
      candles={high:[...], low:[...], close:[...], timestamp:[...]}, atr_values=[...]
    """

    candles = args[0] if args else kwargs.get("candles")
    timeframe = kwargs.get("timeframe")
    atr_values = kwargs.get("atr_values")
    cfg = kwargs.get("config")
    config = cfg if isinstance(cfg, FibonacciConfig) else FibonacciConfig()

    tf_raw = "" if timeframe is None else str(timeframe)
    tf_norm = tf_raw.strip().lower()
    if not tf_norm:
        return {"available": False, "reason": "LTF_TIMEFRAME_MISSING"}

    if not isinstance(candles, dict):
        return {"available": False, "reason": "LTF_BAD_INPUT"}

    highs, lows, closes, timestamps = _to_series(candles)
    n = int(len(closes))
    if n < 3:
        return {"available": False, "reason": "LTF_INSUFFICIENT_DATA"}

    atr_seq: Sequence[float] | None = None
    if atr_values is not None:
        try:
            atr_arr = np.asarray(atr_values, dtype=float)
            if atr_arr.size > 0:
                atr_seq = atr_arr.tolist()
        except Exception:
            atr_seq = None

    swing_high_idx, swing_low_idx, swing_high_prices, swing_low_prices = detect_swing_points(
        highs, lows, closes, config, atr_values=atr_seq
    )

    if not swing_high_prices or not swing_low_prices:
        return {"available": False, "reason": "LTF_NO_SWINGS"}

    fib_levels_list = calculate_fibonacci_levels(swing_high_prices, swing_low_prices, config.levels)
    if len(fib_levels_list) != len(config.levels):
        return {"available": False, "reason": "LTF_LEVELS_INCOMPLETE"}

    levels_raw = dict(zip(config.levels, fib_levels_list, strict=False))

    swing_high = float(swing_high_prices[-1])
    swing_low = float(swing_low_prices[-1])
    if not (math.isfinite(swing_high) and math.isfinite(swing_low)):
        return {"available": False, "reason": "LTF_SWING_BOUNDS_NAN"}
    if swing_high <= swing_low:
        return {
            "available": False,
            "reason": "LTF_INVALID_SWING_BOUNDS",
            "swing_high": swing_high,
            "swing_low": swing_low,
        }

    last_hi_idx = swing_high_idx[-1] if swing_high_idx else None
    last_lo_idx = swing_low_idx[-1] if swing_low_idx else None
    last_idx = max(i for i in [last_hi_idx, last_lo_idx] if i is not None)
    swing_age_bars = max(0, (n - 1) - int(last_idx))

    last_update = None
    if len(timestamps) == n:
        last_update = _normalize_timestamp(timestamps.iloc[-1])

    required_levels = [0.382, 0.5, 0.618, 0.786]
    missing: list[float] = []
    levels: dict[float, float] = {}
    for lvl in required_levels:
        raw = levels_raw.get(lvl)
        if raw is None or pd.isna(raw):
            missing.append(float(lvl))
            continue
        try:
            val = float(raw)
        except Exception:
            missing.append(float(lvl))
            continue
        if not math.isfinite(val):
            missing.append(float(lvl))
            continue
        levels[float(lvl)] = float(val)

    if missing:
        return {"available": False, "reason": "LTF_LEVELS_INCOMPLETE", "missing_levels": missing}

    return {
        "available": True,
        "timeframe": tf_norm,
        "levels": levels,
        "swing_high": swing_high,
        "swing_low": swing_low,
        "swing_age_bars": int(swing_age_bars),
        "last_update": last_update,
    }
