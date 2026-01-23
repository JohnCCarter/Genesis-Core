"""
Higher Timeframe (HTF) Fibonacci mapping module.

This module provides functionality to map Fibonacci levels from a higher timeframe
(e.g., 1D) to a lower timeframe (e.g., 1h) with strict "as-of" semantics
to ensure no lookahead bias during backtesting or live trading.
"""

import hashlib
import json
import math
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from core.indicators.fibonacci import (
    FibonacciConfig,
    calculate_atr,
    calculate_fibonacci_levels,
    detect_swing_points,
)
from core.utils import is_case_sensitive_directory, timeframe_filename_suffix
from core.utils.logging_redaction import get_logger

# --- Module-level caches / constants ---

# Cache: {"{symbol}_{htf_timeframe}_{config_hash}": {"fib_df": pd.DataFrame}}
_htf_context_cache: dict[str, dict[str, Any]] = {}

# Small in-memory candle cache to avoid repeated parquet reads in hot paths.
_candles_cache: dict[tuple[str, str], pd.DataFrame] = {}

_LOGGER = get_logger(__name__)

# Guardrail: HTF context older than this is considered stale.
# Needs to be low enough to flag clearly outdated mappings (tests cover 40d stale).
MAX_HTF_AGE_HOURS = 24.0 * 30.0


def _normalize_timestamp(value: Any) -> pd.Timestamp | None:
    """Normalize timestamps into tz-aware UTC pandas Timestamps.

    Returns None for missing/NaT/unparseable values.
    """

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


def load_candles_data(symbol: str, timeframe: str) -> pd.DataFrame:
    """Load candles from frozen/curated/legacy parquet with deterministic priority.

    Priority:
      1) data/raw/{symbol}_{tf}_frozen.parquet
      2) data/curated/v1/candles/{symbol}_{tf}.parquet
      3) data/candles/{symbol}_{tf}.parquet
    """

    tf_in = str(timeframe)
    tf_cache = timeframe_filename_suffix(tf_in)
    cache_key = (symbol, tf_cache)
    cached = _candles_cache.get(cache_key)
    if cached is not None:
        return cached

    repo_root = Path(__file__).resolve().parents[3]
    data_dir = repo_root / "data"

    suffixes: list[str]
    if tf_in in {"1M", "1mo"}:
        suffixes = ["1mo"]
        if is_case_sensitive_directory(data_dir):
            suffixes.append("1M")
    else:
        suffixes = [tf_cache]

    path: Path | None = None
    for tf in suffixes:
        candidates = [
            data_dir / "raw" / f"{symbol}_{tf}_frozen.parquet",
            data_dir / "curated" / "v1" / "candles" / f"{symbol}_{tf}.parquet",
            data_dir / "candles" / f"{symbol}_{tf}.parquet",
        ]
        path = next((p for p in candidates if p.exists()), None)
        if path is not None:
            break
    if path is None:
        tried = []
        for tf in suffixes:
            tried.extend(
                [
                    data_dir / "raw" / f"{symbol}_{tf}_frozen.parquet",
                    data_dir / "curated" / "v1" / "candles" / f"{symbol}_{tf}.parquet",
                    data_dir / "candles" / f"{symbol}_{tf}.parquet",
                ]
            )
        raise FileNotFoundError(
            f"No candle parquet found for {symbol} {tf_cache}. Tried: {', '.join(str(p) for p in tried)}"
        )

    df = pd.read_parquet(path)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    _candles_cache[cache_key] = df
    return df


def get_swings_as_of(
    swing_highs: list[int],
    swing_lows: list[int],
    current_idx: int,
    highs: pd.Series,
    lows: pd.Series,
) -> dict[str, Any]:
    """
    Get the most recent valid swings as of a specific index.

    Args:
        swing_highs: List of indices for swing highs
        swing_lows: List of indices for swing lows
        current_idx: Current bar index (inclusive, but swings must be confirmed before)
        highs: Series of high prices
        lows: Series of low prices

    Returns:
        Dictionary containing lists of valid high/low prices and current swing points.
    """
    # Filter swings that occurred at or before current_idx
    valid_high_indices = [i for i in swing_highs if i <= current_idx]
    valid_low_indices = [i for i in swing_lows if i <= current_idx]

    valid_high_prices = [highs.iloc[i] for i in valid_high_indices]
    valid_low_prices = [lows.iloc[i] for i in valid_low_indices]

    current_high_price = valid_high_prices[-1] if valid_high_prices else None
    current_low_price = valid_low_prices[-1] if valid_low_prices else None

    current_high_idx = valid_high_indices[-1] if valid_high_indices else None
    current_low_idx = valid_low_indices[-1] if valid_low_indices else None

    return {
        "highs": valid_high_prices,
        "lows": valid_low_prices,
        "current_high": current_high_price,
        "current_low": current_low_price,
        "current_high_idx": current_high_idx,
        "current_low_idx": current_low_idx,
    }


def compute_htf_fibonacci_levels(
    htf_candles: pd.DataFrame,
    config: FibonacciConfig,
) -> pd.DataFrame:
    """
    Compute 1D Fibonacci levels for each bar in the HTF DataFrame.

    Each row i contains Fibonacci levels calculated using only HTF data
    available at or before bar i.

    Args:
        htf_candles: DataFrame containing HTF (e.g., 1D) OHLCV data.
        config: Configuration for Fibonacci calculation.

    Returns:
        DataFrame aligned with htf_candles index containing Fibonacci levels and swings.
    """
    # Ensure datetime objects for comparison
    if not pd.api.types.is_datetime64_any_dtype(htf_candles["timestamp"]):
        htf_candles["timestamp"] = pd.to_datetime(htf_candles["timestamp"])

    # Precompute ATR once and slice it per as-of window.
    atr_series = calculate_atr(htf_candles["high"], htf_candles["low"], htf_candles["close"])
    atr_arr = atr_series.to_numpy(copy=False)

    htf_results: list[dict[str, Any]] = []
    n = int(len(htf_candles))
    lookback = int(getattr(config, "max_lookback", 250) or 250)

    # IMPORTANT:
    # We must compute swings with AS-OF semantics. A single global `detect_swing_points()`
    # pass anchored at the end of the series will (by design) keep only recent swings
    # within `max_lookback` of the latest swing, which makes early history appear to have
    # no swings at all. That caused HTF levels to be unavailable for entire earlier
    # windows (e.g. 2024) and made HTF gating parameters inert during optimization.
    for i in range(n):
        htf_time = htf_candles.iloc[i]["timestamp"]
        window_start = max(0, i - lookback)
        window_end = i + 1

        highs = htf_candles["high"].iloc[window_start:window_end]
        lows = htf_candles["low"].iloc[window_start:window_end]
        closes = htf_candles["close"].iloc[window_start:window_end]
        atr_values = atr_arr[window_start:window_end]

        swing_high_idx, swing_low_idx, swing_high_prices, swing_low_prices = detect_swing_points(
            highs,
            lows,
            closes,
            config,
            atr_values=atr_values,
        )

        fib_levels_list = calculate_fibonacci_levels(
            swing_high_prices, swing_low_prices, config.levels
        )
        if len(fib_levels_list) == len(config.levels):
            fib_levels = dict(zip(config.levels, fib_levels_list, strict=False))
        else:
            fib_levels = {}

        # Convert window-relative indices to absolute indices for swing age.
        h_idx = (window_start + int(swing_high_idx[-1])) if swing_high_idx else None
        l_idx = (window_start + int(swing_low_idx[-1])) if swing_low_idx else None
        swing_age = i - max(
            h_idx if h_idx is not None else -1,
            l_idx if l_idx is not None else -1,
        )
        swing_high = float(swing_high_prices[-1]) if swing_high_prices else None
        swing_low = float(swing_low_prices[-1]) if swing_low_prices else None

        htf_results.append(
            {
                "htf_timestamp_close": htf_time,
                "htf_fib_0382": fib_levels.get(0.382),
                "htf_fib_05": fib_levels.get(0.5),
                "htf_fib_0618": fib_levels.get(0.618),
                "htf_fib_0786": fib_levels.get(0.786),
                "htf_swing_high": swing_high,
                "htf_swing_low": swing_low,
                "htf_swing_age_bars": swing_age if swing_age >= 0 else 0,
            }
        )

    return pd.DataFrame(htf_results)


def compute_htf_fibonacci_mapping(
    htf_candles: pd.DataFrame,
    ltf_candles: pd.DataFrame,
    config: FibonacciConfig | None = None,
) -> pd.DataFrame:
    """
    Compute 1D Fibonacci levels and project to LTF timestamps.

    AS-OF SEMANTICS: Each LTF bar gets the latest 1D Fib levels
    that were available BEFORE that bar (no lookahead).

    Ideally, for an LTF bar starting at time T, we use HTF data available
    strictly before T. For example, if 1D closes at 00:00, then 01:00 LTF bar
    can use it.

    Args:
        htf_candles: DataFrame containing HTF (e.g., 1D) OHLCV data.
        ltf_candles: DataFrame containing LTF (e.g., 1h) OHLCV data.
        config: Configuration for Fibonacci calculation.

    Returns:
        DataFrame aligned with LTF index containing HTF Fibonacci levels.
        Columns:
            - timestamp (LTF)
            - htf_fib_0382
            - htf_fib_05
            - htf_fib_0618
            - htf_swing_high
            - htf_swing_low
    """
    config_obj = config or FibonacciConfig()
    htf_df = compute_htf_fibonacci_levels(htf_candles, config_obj)
    if htf_df is None or htf_df.empty:
        return ltf_candles[["timestamp"]].assign(htf_data_age_hours=np.nan)

    def _normalize_dt_series(values: Any, *, tz_aware: bool) -> pd.Series:
        ts = pd.to_datetime(values, utc=True, errors="coerce")
        if tz_aware:
            return ts
        # Drop tz (keep UTC clock time) to match naive LTF inputs.
        try:
            return ts.dt.tz_convert("UTC").dt.tz_localize(None)
        except Exception:
            # Fallback for older pandas edge cases
            return pd.to_datetime(ts.dt.tz_localize(None), errors="coerce")

    ltf_left = ltf_candles[["timestamp"]].copy()
    ltf_ts_in = pd.to_datetime(ltf_left["timestamp"], errors="coerce")
    tz_aware = getattr(ltf_ts_in.dt, "tz", None) is not None
    ltf_left["timestamp"] = _normalize_dt_series(ltf_left["timestamp"], tz_aware=tz_aware)

    htf_df = htf_df.copy()

    # Normalize timestamp semantics:
    # - If `htf_timestamp_close` exists, treat it as HTF period start (open time) and
    #   compute a strict availability timestamp `valid_from = open + frequency`.
    # - If `timestamp` exists (cached/precomputed frames), treat it as availability timestamp.
    if "htf_timestamp_close" in htf_df.columns:
        htf_df["htf_timestamp"] = _normalize_dt_series(
            htf_df["htf_timestamp_close"], tz_aware=tz_aware
        )
        deltas = htf_df["htf_timestamp"].diff().dropna()
        frequency = deltas.median() if len(deltas) > 0 else pd.Timedelta(days=1)
        htf_df["valid_from"] = htf_df["htf_timestamp"] + frequency
    elif "timestamp" in htf_df.columns:
        htf_df["htf_timestamp"] = _normalize_dt_series(htf_df["timestamp"], tz_aware=tz_aware)
        htf_df = htf_df.drop(columns=["timestamp"])
        htf_df["valid_from"] = htf_df["htf_timestamp"]
    else:
        raise KeyError("HTF fibonacci dataframe missing timestamp column")

    htf_df["valid_from"] = pd.to_datetime(htf_df["valid_from"], errors="coerce")

    merged = pd.merge_asof(
        ltf_left,
        htf_df,
        left_on="timestamp",
        right_on="valid_from",
        direction="backward",
        allow_exact_matches=True,
    )

    marker_col = "htf_fib_0618" if "htf_fib_0618" in merged.columns else None
    age_hours = (merged["timestamp"] - merged["htf_timestamp"]).dt.total_seconds() / 3600
    if marker_col is not None:
        merged["htf_data_age_hours"] = age_hours.where(merged[marker_col].notna(), np.nan)
    else:
        merged["htf_data_age_hours"] = age_hours.where(merged["htf_timestamp"].notna(), np.nan)

    return merged


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
    """
    Get HTF Fibonacci context with caching and age validation.

    Args:
        ltf_candles: LTF candles (dict/list) for as-of reference
        timeframe: LTF timeframe (e.g., '1h', '30m')
        symbol: Asset symbol
        htf_timeframe: HTF timeframe to fetch (default '1D')
        config: Optional FibonacciConfig
        **kwargs: Extra args for compatibility

    Returns:
        Dict containing HTF Fibonacci context (availablity, levels, age, etc.)
    """

    def _reference_timestamp() -> pd.Timestamp | None:
        if isinstance(ltf_candles, dict):
            timestamps = ltf_candles.get("timestamp")
            if timestamps:
                ts = _normalize_timestamp(timestamps[-1])
                if ts is not None:
                    return ts
        elif isinstance(ltf_candles, list) and ltf_candles:
            raw = ltf_candles[-1][0] if len(ltf_candles[-1]) > 0 else None
            ts = _normalize_timestamp(raw)
            if ts is not None:
                return ts
        return None

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

    reference_ts = _reference_timestamp()

    # Create a stable hash of the config to prevent stale cache when params change
    config_hash = "default"
    if config:
        try:
            # Convert dataclass to dict, sort keys, and hash string representation
            cfg_dict = config.__dict__
            cfg_str = json.dumps(cfg_dict, sort_keys=True, default=str)
            # Cache-key fingerprint only (not used for security): use SHA-256 to satisfy Bandit (B324).
            config_hash = hashlib.sha256(cfg_str.encode("utf-8")).hexdigest()
        except Exception:
            # Fallback if serialization fails
            config_hash = str(hash(str(config)))

    cache_key = f"{symbol}_{htf_timeframe}_{config_hash}"
    cache_entry = _htf_context_cache.setdefault(cache_key, {})
    fib_df = cache_entry.get("fib_df")

    # Normalize/alias the input timeframe to avoid surprising "NOT_APPLICABLE" outcomes.
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

    # Only provide HTF context for LTF timeframes.
    if tf_norm not in ["1h", "30m", "6h", "15m"]:
        return {
            "available": False,
            "reason": "HTF_NOT_APPLICABLE",
            "timeframe": tf_norm,
            "htf_timeframe": htf_timeframe,
        }

    # Load or reuse cached HTF fib dataframe
    if fib_df is None:
        try:
            htf_candles = load_candles_data(symbol, htf_timeframe)
            if htf_candles is not None:
                fib_df = compute_htf_fibonacci_levels(htf_candles, config or FibonacciConfig())
                cache_entry["fib_df"] = fib_df
        except FileNotFoundError as e:
            _LOGGER.debug("HTF data not found for %s %s: %s", symbol, htf_timeframe, e)
            return {"available": False, "reason": "HTF_DATA_NOT_FOUND"}
        except Exception:
            _LOGGER.exception("HTF load/compute failed for %s %s", symbol, htf_timeframe)
            return {"available": False, "reason": "HTF_ERROR"}

    if fib_df is None or fib_df.empty:
        return {"available": False, "reason": "NO_HTF_SWINGS"}

    try:
        # Safety: never select HTF context without an as-of timestamp.
        # Otherwise we'd implicitly use the last HTF row (lookahead) when callers
        # pass candles without timestamps.
        if reference_ts is None:
            return {
                "available": False,
                "reason": "HTF_MISSING_REFERENCE_TS",
                "htf_timeframe": htf_timeframe,
            }

        # Ensure we select the latest HTF row that is actually available as-of reference_ts
        # (no lookahead).
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

        # Validate that all required levels are present and finite.
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

        last_htf_timestamp = _normalize_timestamp(latest_htf[ts_col])
        data_age_hours = _compute_age_hours(last_htf_timestamp, reference_ts)

        if data_age_hours > MAX_HTF_AGE_HOURS:
            return {"available": False, "reason": "HTF_DATA_STALE", "htf_timeframe": htf_timeframe}

        # Return HTF context
        swing_high = float(latest_htf["htf_swing_high"])
        swing_low = float(latest_htf["htf_swing_low"])

        # Guard: swing bounds must be sane, otherwise downstream exit-context init will be invalid.
        # This can happen when "latest swing high" and "latest swing low" are selected independently.
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

        # Sanity: levels should live within the swing bounds (with tiny epsilon).
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

        htf_context = {
            "available": True,
            "levels": levels,
            "swing_high": swing_high,
            "swing_low": swing_low,
            "swing_age_bars": int(latest_htf["htf_swing_age_bars"]),
            "data_age_hours": float(data_age_hours),
            "htf_timeframe": htf_timeframe,
            "last_update": last_htf_timestamp,
        }

        return htf_context

    except Exception:
        _LOGGER.exception("HTF context failed for %s %s", symbol, htf_timeframe)
        return {"available": False, "reason": "HTF_ERROR"}


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
