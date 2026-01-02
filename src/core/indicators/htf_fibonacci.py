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
    calculate_fibonacci_levels,
    detect_swing_points,
)


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

    swing_high_idx, swing_low_idx, _, _ = detect_swing_points(
        htf_candles["high"], htf_candles["low"], htf_candles["close"], config
    )

    if isinstance(swing_high_idx, np.ndarray):
        swing_high_idx = swing_high_idx.tolist()
    if isinstance(swing_low_idx, np.ndarray):
        swing_low_idx = swing_low_idx.tolist()

    htf_results = []

    for i in range(len(htf_candles)):
        htf_time = htf_candles.iloc[i]["timestamp"]

        # Get swing context up to this point (AS-OF)
        current_swings = get_swings_as_of(
            swing_high_idx, swing_low_idx, i, htf_candles["high"], htf_candles["low"]
        )

        fib_levels_list = calculate_fibonacci_levels(
            current_swings["highs"], current_swings["lows"], config.levels
        )

        # Map values back to keys
        if len(fib_levels_list) == len(config.levels):
            fib_levels = dict(zip(config.levels, fib_levels_list, strict=False))
        else:
            fib_levels = {}

        # Calculate swing age
        h_idx = current_swings["current_high_idx"]
        l_idx = current_swings["current_low_idx"]
        swing_age = i - max(h_idx if h_idx is not None else -1, l_idx if l_idx is not None else -1)

        htf_results.append(
            {
                "htf_timestamp_close": htf_time,
                "htf_fib_0382": fib_levels.get(0.382),
                "htf_fib_05": fib_levels.get(0.5),
                "htf_fib_0618": fib_levels.get(0.618),
                "htf_swing_high": current_swings["current_high"],
                "htf_swing_low": current_swings["current_low"],
                "htf_swing_age_bars": swing_age if swing_age >= 0 else 0,
            }
        )

    return pd.DataFrame(htf_results)


def compute_htf_fibonacci_mapping(
    htf_candles: pd.DataFrame,
    ltf_candles: pd.DataFrame,
    config: FibonacciConfig,
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
    # 1. Calculate HTF levels
    htf_df = compute_htf_fibonacci_levels(htf_candles, config)

    # 2. Project to LTF bars (forward-fill)
    # We want: for each LTF bar at T, find latest HTF bar where htf_time < T
    # Assuming htf_timestamp represents the OPEN time or close?
    # Usually timestamps are candle open times.
    # An HTF candle opened at D, closes at D+1d.
    # Data from D is only available at D+1d.
    # So if LTF is at T, we need HTF candle where (open_time + period) <= T
    # Or simply: use `asof` merge with direction='backward' but strict inequality.

<<<<<<< HEAD
    # Step 2: Project to LTF bars with AS-OF semantics.
    # Use merge_asof for efficient time-series join.
    ltf_df = ltf_candles[["timestamp"]].copy()

    # Preserve the matched HTF timestamp to compute age correctly.
    htf_df = htf_fib_df.rename(columns={"timestamp": "htf_timestamp"}).copy()

    merged = pd.merge_asof(
        ltf_df.sort_values("timestamp"),
        htf_df.sort_values("htf_timestamp"),
        left_on="timestamp",
        right_on="htf_timestamp",
=======
    # Let's assume timestamp is Open Time.
    # We can only use HTF data from a candle that has CLOSED.
    # If HTF is daily, it closes 24h after open.
    # To simplify, we can map using: valid_from = htf_timestamp + timedelta(1 unit)

    # However, to be generic, let's use the provided timestamps and assume
    # the user ensures they represent "data availability time" or we use strictly
    # "htf_timestamp < ltf_timestamp" if both are open times, which effectively
    # means we use the *previous* day's candle for today's trading, which is correct
    # (today's daily candle is not closed yet).

    htf_df.sort_values("htf_timestamp_close", inplace=True)
    ltf_candles.sort_values("timestamp", inplace=True)

    # Infer HTF frequency to determine "valid_from" time (Close Time)
    if len(htf_df) > 1:
        # Calculate median delta between timestamps
        deltas = htf_df["htf_timestamp_close"].diff().dropna()
        frequency = deltas.median()
    else:
        # Fallback to 1 Day if single row or unclear
        frequency = pd.Timedelta(days=1)

    # valid_from is strictly when the candle closes.
    # We assume 'htf_timestamp_close' is the Open time (standard convention in this codebase).
    # So valid_from = OpenTime + Frequency.
    htf_df["valid_from"] = htf_df["htf_timestamp_close"] + frequency

    # Debug: Ensure types are compatible
    htf_df["valid_from"] = pd.to_datetime(htf_df["valid_from"])

    # Use merge_asof
    # left: LTF (timestamp)
    # right: HTF (valid_from)
    # We want closest HTF where valid_from <= LTF timestamp.
    # direction='backward' gives right_on <= left_on

    merged = pd.merge_asof(
        ltf_candles[["timestamp"]],  # Only keep timestamp to preserve index from left
        htf_df,
        left_on="timestamp",
        right_on="valid_from",
>>>>>>> cd1eda3 (fix: resolve QA suite failures and implement compute_htf_fibonacci_levels)
        direction="backward",
        allow_exact_matches=True,
    )

    merged["htf_data_age_hours"] = (
        (merged["timestamp"] - merged["htf_timestamp"]).dt.total_seconds() / 3600
    ).where(merged["htf_fib_0618"].notna(), None)

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
        return {"available": False, "reason": "HTF_NOT_APPLICABLE", "timeframe": tf_norm}

    # Load or reuse cached HTF fib dataframe
    if fib_df is None:
        try:
            htf_candles = load_candles_data(symbol, htf_timeframe)
            if htf_candles is not None:
                fib_df = compute_htf_fibonacci_levels(htf_candles, config or FibonacciConfig())
                cache_entry["fib_df"] = fib_df
        except FileNotFoundError as e:
            return {"available": False, "reason": "HTF_DATA_NOT_FOUND", "error": str(e)}
        except Exception as e:
            return {"available": False, "reason": "HTF_ERROR", "error": str(e)}

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

        if reference_ts is not None:
            # Ensure 'timestamp' column exists in fib_df (it might be 'htf_timestamp_close' from compute_htf_fibonacci_levels)
            ts_col = "timestamp" if "timestamp" in fib_df.columns else "htf_timestamp_close"
            ref_rows = fib_df[fib_df[ts_col] <= reference_ts]
            if ref_rows.empty:
                return {"available": False, "reason": "HTF_NO_HISTORY"}
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
            return {"available": False, "reason": "HTF_DATA_STALE"}

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

    except Exception as e:
        return {"available": False, "reason": "HTF_ERROR", "error": str(e)}



def get_ltf_fibonacci_context(*args, **kwargs) -> dict[str, Any]:
    """Stub for LTF context."""
    return {}
