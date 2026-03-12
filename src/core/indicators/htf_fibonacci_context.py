"""HTF Fibonacci runtime context retrieval and validation helpers."""

import hashlib
import json
import math
from typing import Any

import pandas as pd

from core.indicators.fibonacci import FibonacciConfig
from core.utils.logging_redaction import get_logger

_LOGGER = get_logger(__name__)

# Guardrail: HTF context older than this is considered stale.
MAX_HTF_AGE_HOURS = 24.0 * 30.0


def _normalize_timestamp(value: Any) -> pd.Timestamp | None:
    """Normalize timestamps into tz-aware UTC pandas Timestamps."""
    if value is None:
        return None
    try:
        ts = pd.to_datetime(value, errors="coerce", utc=True)
    except Exception:
        return None
    if ts is None or ts is pd.NaT:
        return None
    try:
        pts = pd.Timestamp(ts)
    except Exception:
        return None
    if getattr(pts, "tz", None) is None:
        try:
            pts = pts.tz_localize("UTC")
        except Exception:
            return None
    else:
        try:
            pts = pts.tz_convert("UTC")
        except Exception:
            return None
    return pts


def _compute_age_hours(last_update: pd.Timestamp | None, ref: pd.Timestamp | None) -> float:
    if last_update is None:
        return float("inf")
    ref_ts = ref or pd.Timestamp.now(tz=last_update.tz)
    try:
        delta_hours = (ref_ts - last_update).total_seconds() / 3600.0
    except Exception:
        return float("inf")
    if delta_hours < 0:
        return 0.0
    return float(delta_hours)


def get_htf_fibonacci_context_impl(
    ltf_candles: Any,
    timeframe: str,
    symbol: str = "tBTCUSD",
    htf_timeframe: str = "1D",
    config: FibonacciConfig | None = None,
    *,
    htf_context_cache: dict[str, dict[str, Any]],
    load_candles_data_fn,
    compute_htf_fibonacci_levels_fn,
    normalize_timestamp_fn=_normalize_timestamp,
    max_htf_age_hours: float = MAX_HTF_AGE_HOURS,
    **kwargs: Any,
) -> dict[str, Any]:
    """Get HTF Fibonacci context with injected cache and loader/compute functions."""

    del kwargs

    def _reference_timestamp() -> pd.Timestamp | None:
        if isinstance(ltf_candles, dict):
            timestamps = ltf_candles.get("timestamp")
            if timestamps:
                ts = normalize_timestamp_fn(timestamps[-1])
                if ts is not None:
                    return ts
        elif isinstance(ltf_candles, list) and ltf_candles:
            raw = ltf_candles[-1][0] if len(ltf_candles[-1]) > 0 else None
            ts = normalize_timestamp_fn(raw)
            if ts is not None:
                return ts
        return None

    reference_ts = _reference_timestamp()

    config_hash = "default"
    if config:
        try:
            cfg_dict = config.__dict__
            cfg_str = json.dumps(cfg_dict, sort_keys=True, default=str)
            config_hash = hashlib.sha256(cfg_str.encode("utf-8")).hexdigest()
        except Exception:
            config_hash = str(hash(str(config)))

    cache_key = f"{symbol}_{htf_timeframe}_{config_hash}"
    cache_entry = htf_context_cache.setdefault(cache_key, {})
    fib_df = cache_entry.get("fib_df")

    tf_raw = "" if timeframe is None else str(timeframe)
    tf_norm = tf_raw.strip().lower()
    tf_aliases = {
        "60m": "1h",
        "1hr": "1h",
        "1hour": "1h",
        "30min": "30m",
        "15min": "15m",
        "360m": "6h",
    }
    tf_norm = tf_aliases.get(tf_norm, tf_norm)

    if not tf_norm:
        return {"available": False, "reason": "HTF_TIMEFRAME_MISSING"}

    if tf_norm not in ["1h", "30m", "6h", "15m"]:
        return {
            "available": False,
            "reason": "HTF_NOT_APPLICABLE",
            "timeframe": tf_norm,
            "htf_timeframe": htf_timeframe,
        }

    if fib_df is None:
        try:
            htf_candles = load_candles_data_fn(symbol, htf_timeframe)
            if htf_candles is not None:
                fib_df = compute_htf_fibonacci_levels_fn(htf_candles, config or FibonacciConfig())
                cache_entry["fib_df"] = fib_df
        except FileNotFoundError as exc:
            _LOGGER.debug("HTF data not found for %s %s: %s", symbol, htf_timeframe, exc)
            return {"available": False, "reason": "HTF_DATA_NOT_FOUND"}
        except Exception:
            _LOGGER.exception("HTF load/compute failed for %s %s", symbol, htf_timeframe)
            return {"available": False, "reason": "HTF_ERROR"}

    if fib_df is None or fib_df.empty:
        return {"available": False, "reason": "NO_HTF_SWINGS"}

    try:
        if reference_ts is None:
            return {
                "available": False,
                "reason": "HTF_MISSING_REFERENCE_TS",
                "htf_timeframe": htf_timeframe,
            }

        ts_col = "timestamp" if "timestamp" in fib_df.columns else "htf_timestamp_close"
        ts_series = pd.to_datetime(fib_df[ts_col], utc=True, errors="coerce")
        if ts_col == "htf_timestamp_close":
            deltas = ts_series.diff().dropna()
            frequency = deltas.median() if len(deltas) > 0 else pd.Timedelta(days=1)
            valid_from = ts_series + frequency
        else:
            valid_from = ts_series
        ref_rows = fib_df[valid_from <= reference_ts]
        if ref_rows.empty:
            return {"available": False, "reason": "HTF_NO_HISTORY", "htf_timeframe": htf_timeframe}
        latest_htf = ref_rows.iloc[-1]

        required_cols = {
            0.382: "htf_fib_0382",
            0.5: "htf_fib_05",
            0.618: "htf_fib_0618",
            0.786: "htf_fib_0786",
        }
        levels: dict[float, float] = {}
        missing_levels: list[float] = []
        for lvl, col in required_cols.items():
            try:
                raw = latest_htf[col]
            except Exception:
                raw = None
            if raw is None or pd.isna(raw):
                missing_levels.append(float(lvl))
                continue
            try:
                val = float(raw)
            except Exception:
                missing_levels.append(float(lvl))
                continue
            if not math.isfinite(val):
                missing_levels.append(float(lvl))
                continue
            levels[float(lvl)] = float(val)

        if missing_levels:
            return {
                "available": False,
                "reason": "HTF_LEVELS_INCOMPLETE",
                "missing_levels": sorted(set(missing_levels)),
                "htf_timeframe": htf_timeframe,
            }

        last_htf_timestamp = normalize_timestamp_fn(latest_htf[ts_col])
        data_age_hours = _compute_age_hours(last_htf_timestamp, reference_ts)

        if data_age_hours > max_htf_age_hours:
            return {"available": False, "reason": "HTF_DATA_STALE", "htf_timeframe": htf_timeframe}

        swing_high = float(latest_htf["htf_swing_high"])
        swing_low = float(latest_htf["htf_swing_low"])

        if pd.isna(swing_high) or pd.isna(swing_low):
            return {
                "available": False,
                "reason": "HTF_SWING_BOUNDS_NAN",
                "htf_timeframe": htf_timeframe,
            }
        if swing_high <= swing_low:
            return {
                "available": False,
                "reason": "HTF_INVALID_SWING_BOUNDS",
                "htf_timeframe": htf_timeframe,
                "swing_high": float(swing_high),
                "swing_low": float(swing_low),
            }

        eps = 1e-9
        if levels and (
            min(levels.values()) < swing_low - eps or max(levels.values()) > swing_high + eps
        ):
            return {
                "available": False,
                "reason": "HTF_LEVELS_OUT_OF_BOUNDS",
                "htf_timeframe": htf_timeframe,
                "swing_high": float(swing_high),
                "swing_low": float(swing_low),
            }

        return {
            "available": True,
            "levels": levels,
            "swing_high": swing_high,
            "swing_low": swing_low,
            "swing_age_bars": int(latest_htf["htf_swing_age_bars"]),
            "data_age_hours": float(data_age_hours),
            "htf_timeframe": htf_timeframe,
            "last_update": last_htf_timestamp,
        }

    except Exception:
        _LOGGER.exception("HTF context failed for %s %s", symbol, htf_timeframe)
        return {"available": False, "reason": "HTF_ERROR"}
