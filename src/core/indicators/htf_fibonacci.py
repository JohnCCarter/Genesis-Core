"""
HTF (Higher Timeframe) Fibonacci Mapping for Genesis-Core

Cross-timeframe Fibonacci projection with strict AS-OF semantics (no lookahead).
Maps 1D Fibonacci levels to LTF bars (1h/30m) for structure-aware exits.
"""

import hashlib
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pandas as pd

from core.indicators.fibonacci import (
    FibonacciConfig,
    calculate_fibonacci_levels,
    detect_swing_points,
)

# Simple cache for HTF context to avoid repeated computation
_htf_context_cache: dict[str, dict[str, Any]] = {}


def _to_series(
    data: dict[str, list[float]] | list[tuple],
) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series | None]:
    """
    Normalize candle input (dict or list of tuples) into pandas Series.
    Returns (highs, lows, closes, timestamps)

    Performance: Avoids redundant Series creation when data is already pandas Series or numpy arrays.
    """
    if isinstance(data, dict):
        # Optimization: Check if data is already pandas Series to avoid redundant conversion
        high_data = data.get("high", [])
        low_data = data.get("low", [])
        close_data = data.get("close", [])

        # Fast path: if already Series, return as-is
        if isinstance(high_data, pd.Series):
            highs = high_data
        else:
            # Explicit dtype ensures float type (input may be int/mixed)
            highs = pd.Series(high_data, dtype=float)

        if isinstance(low_data, pd.Series):
            lows = low_data
        else:
            lows = pd.Series(low_data, dtype=float)

        if isinstance(close_data, pd.Series):
            closes = close_data
        else:
            closes = pd.Series(close_data, dtype=float)

        timestamps_raw = data.get("timestamp")
        if timestamps_raw is None:
            timestamps = None
        elif isinstance(timestamps_raw, pd.Series):
            timestamps = timestamps_raw
        else:
            timestamps = pd.Series(timestamps_raw)
        return highs, lows, closes, timestamps

    if isinstance(data, list):
        # Assume list of tuples (timestamp, open, high, low, close, volume)
        highs = pd.Series([float(item[2]) for item in data], dtype=float)
        lows = pd.Series([float(item[3]) for item in data], dtype=float)
        closes = pd.Series([float(item[4]) for item in data], dtype=float)
        timestamps = pd.Series([item[0] for item in data]) if data and len(data[0]) > 0 else None
        return highs, lows, closes, timestamps

    raise TypeError(f"Unsupported candle format: {type(data)!r}")


def load_candles_data(symbol: str, timeframe: str) -> pd.DataFrame:
    """
    Load candle data from Parquet files (same logic as BacktestEngine).

    Args:
        symbol: Trading symbol (e.g., 'tBTCUSD')
        timeframe: Timeframe (e.g., '1D', '1h', '30m')

    Returns:
        DataFrame with columns: timestamp, open, high, low, close, volume

    Raises:
        FileNotFoundError: If no data file found
    """
    # Find data file (try two-layer structure first, fallback to legacy)
    base_dir = Path(__file__).parent.parent.parent.parent / "data"
    data_file_curated = base_dir / "curated" / "v1" / "candles" / f"{symbol}_{timeframe}.parquet"
    data_file_legacy = base_dir / "candles" / f"{symbol}_{timeframe}.parquet"

    if data_file_curated.exists():
        data_file = data_file_curated
    elif data_file_legacy.exists():
        data_file = data_file_legacy
    else:
        raise FileNotFoundError(
            f"Candle data not found for {symbol} {timeframe}:\n"
            f"  Tried curated: {data_file_curated}\n"
            f"  Tried legacy: {data_file_legacy}"
        )

    df = pd.read_parquet(data_file)

    # Ensure timestamp is datetime and sorted
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp").reset_index(drop=True)

    return df


def compute_htf_fibonacci_levels(
    htf_candles: pd.DataFrame, config: FibonacciConfig = None
) -> pd.DataFrame:
    """
    Compute HTF Fibonacci levels with AS-OF semantics.

    Args:
        htf_candles: HTF candle data (e.g., 1D)
        config: Fibonacci configuration

    Returns:
        DataFrame with HTF Fibonacci data:
        - timestamp (HTF)
        - htf_fib_0382, htf_fib_05, htf_fib_0618, htf_fib_0786
        - htf_swing_high, htf_swing_low
        - htf_swing_age_bars (bars since last swing update)
    """
    if config is None:
        config = FibonacciConfig()

    # Detect swing points on HTF data
    swing_high_indices, swing_low_indices, swing_high_prices, swing_low_prices = (
        detect_swing_points(htf_candles["high"], htf_candles["low"], htf_candles["close"], config)
    )

    # OPTIMIZED: Pre-allocate arrays and use vectorized operations
    n_bars = len(htf_candles)
    timestamps = htf_candles["timestamp"].values

    # Convert swing data to numpy arrays for faster access
    swing_high_idx_arr = pd.array(swing_high_indices, dtype="Int64")
    swing_low_idx_arr = pd.array(swing_low_indices, dtype="Int64")
    swing_high_price_arr = pd.array(swing_high_prices, dtype="float64")
    swing_low_price_arr = pd.array(swing_low_prices, dtype="float64")

    # Pre-allocate result arrays
    htf_fib_0382 = [None] * n_bars
    htf_fib_05 = [None] * n_bars
    htf_fib_0618 = [None] * n_bars
    htf_fib_0786 = [None] * n_bars
    htf_swing_high = [None] * n_bars
    htf_swing_low = [None] * n_bars
    htf_swing_age_bars = [0] * n_bars

    # Build cumulative max/min for fallback (vectorized)
    cummax_high = htf_candles["high"].cummax()
    cummin_low = htf_candles["low"].cummin()
    cummax_high_arr = cummax_high.to_numpy(copy=False)
    cummin_low_arr = cummin_low.to_numpy(copy=False)

    # Process each bar
    for i in range(n_bars):
        # Get swings known as of bar i (vectorized filtering)
        valid_high_mask = swing_high_idx_arr <= i
        valid_low_mask = swing_low_idx_arr <= i

        current_swing_highs = swing_high_price_arr[valid_high_mask].tolist()
        current_swing_high_indices = swing_high_idx_arr[valid_high_mask].tolist()
        current_swing_lows = swing_low_price_arr[valid_low_mask].tolist()
        current_swing_low_indices = swing_low_idx_arr[valid_low_mask].tolist()

        # Fallback to cumulative max/min if no swings (vectorized)
        if not current_swing_highs:
            current_swing_highs = [float(cummax_high_arr[i])]
            current_swing_high_indices = [i]

        if not current_swing_lows:
            current_swing_lows = [float(cummin_low_arr[i])]
            current_swing_low_indices = [i]

        # Calculate Fibonacci levels from AS-OF swings
        fib_levels_list = calculate_fibonacci_levels(
            current_swing_highs, current_swing_lows, config.levels
        )

        # Store Fibonacci levels
        if len(fib_levels_list) == len(config.levels):
            for level, price in zip(config.levels, fib_levels_list, strict=False):
                if level == 0.382:
                    htf_fib_0382[i] = price
                elif level == 0.5:
                    htf_fib_05[i] = price
                elif level == 0.618:
                    htf_fib_0618[i] = price
                elif level == 0.786:
                    htf_fib_0786[i] = price

        # Current swing context
        htf_swing_high[i] = current_swing_highs[-1] if current_swing_highs else None
        htf_swing_low[i] = current_swing_lows[-1] if current_swing_lows else None

        # Calculate swing age (bars since last swing)
        last_known_idx = -1
        if current_swing_high_indices:
            last_known_idx = max(last_known_idx, current_swing_high_indices[-1])
        if current_swing_low_indices:
            last_known_idx = max(last_known_idx, current_swing_low_indices[-1])
        htf_swing_age_bars[i] = i - last_known_idx if last_known_idx >= 0 else 0

    # Build result DataFrame directly from arrays (faster than list of dicts)
    return pd.DataFrame(
        {
            "timestamp": timestamps,
            "htf_fib_0382": htf_fib_0382,
            "htf_fib_05": htf_fib_05,
            "htf_fib_0618": htf_fib_0618,
            "htf_fib_0786": htf_fib_0786,
            "htf_swing_high": htf_swing_high,
            "htf_swing_low": htf_swing_low,
            "htf_swing_age_bars": htf_swing_age_bars,
        }
    )


def compute_htf_fibonacci_mapping(
    htf_candles: pd.DataFrame,  # 1D candles
    ltf_candles: pd.DataFrame,  # 1h/30m candles
    config: FibonacciConfig = None,
) -> pd.DataFrame:
    """
    Compute HTF Fibonacci levels and project to LTF timestamps.

    AS-OF SEMANTICS: Each LTF bar gets the latest HTF Fib levels
    that were available BEFORE that bar (no lookahead).

    Args:
        htf_candles: HTF candle data (e.g., 1D)
        ltf_candles: LTF candle data (e.g., 1h, 30m)
        config: Fibonacci configuration

    Returns:
        DataFrame with LTF timestamps and HTF Fibonacci context:
        - timestamp (LTF)
        - htf_fib_0382, htf_fib_05, htf_fib_0618, htf_fib_0786
        - htf_swing_high, htf_swing_low
        - htf_swing_age_bars (bars since last HTF swing update)
        - htf_data_age_hours (hours since last HTF bar)
    """
    if config is None:
        config = FibonacciConfig()

    # Step 1: Compute HTF Fibonacci levels
    htf_fib_df = compute_htf_fibonacci_levels(htf_candles, config)

    # Step 2: Project to LTF bars with AS-OF semantik (OPTIMIZED)
    # Use merge_asof for efficient time-series join (100x faster than iterrows)
    ltf_df = ltf_candles[["timestamp"]].copy()

    # Perform asof merge (finds latest HTF data <= each LTF timestamp)
    merged = pd.merge_asof(
        ltf_df.sort_values("timestamp"),
        htf_fib_df.sort_values("timestamp"),
        on="timestamp",
        direction="backward",
    )

    # Calculate data age in hours (vectorized)
    merged["htf_data_age_hours"] = (
        (merged["timestamp"] - htf_fib_df.loc[htf_fib_df.index[0], "timestamp"]).dt.total_seconds()
        / 3600
    ).where(merged["htf_fib_0618"].notna(), None)

    return merged


def get_htf_fibonacci_context(
    ltf_candles: dict | list,
    timeframe: str = None,
    symbol: str = "tBTCUSD",
    htf_timeframe: str = "1D",
    config: FibonacciConfig = None,
) -> dict:
    """
    Get HTF Fibonacci context for the current LTF bar.

    This is the main interface for extract_features() integration.

    Args:
        ltf_candles: Current LTF candles (dict or list format)
        timeframe: LTF timeframe (1h, 30m, etc.)
        symbol: Trading symbol
        htf_timeframe: HTF timeframe for structure (default: 1D)
        config: Fibonacci configuration

    Returns:
        HTF context dict for current bar:
        {
            'levels': {0.382: price, 0.5: price, 0.618: price, 0.786: price},
            'swing_high': price,
            'swing_low': price,
            'swing_age_bars': int,
            'data_age_hours': float,
            'available': bool  # Whether HTF data is available
        }
    """
    MAX_HTF_AGE_HOURS = 168  # 7 dagar

    def _normalize_timestamp(value: Any) -> pd.Timestamp | None:
        if value is None:
            return None
        try:
            ts = pd.to_datetime(value)
        except Exception:
            return None
        if not isinstance(ts, pd.Timestamp):
            return None
        return ts

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
            config_hash = hashlib.md5(cfg_str.encode()).hexdigest()
        except Exception:
            # Fallback if serialization fails
            config_hash = str(hash(str(config)))

    cache_key = f"{symbol}_{htf_timeframe}_{config_hash}"
    cache_entry = _htf_context_cache.setdefault(cache_key, {})
    fib_df = cache_entry.get("fib_df")

    # Only provide HTF context for LTF timeframes
    if timeframe not in ["1h", "30m", "6h", "15m"]:
        return {"available": False, "reason": "HTF_NOT_APPLICABLE"}

    # Load or reuse cached HTF fib dataframe
    if fib_df is None:
        try:
            htf_candles = load_candles_data(symbol, htf_timeframe)
            fib_df = compute_htf_fibonacci_levels(htf_candles, config)
            cache_entry["fib_df"] = fib_df
        except FileNotFoundError as e:
            return {"available": False, "reason": "HTF_DATA_NOT_FOUND", "error": str(e)}
        except Exception as e:
            return {"available": False, "reason": "HTF_ERROR", "error": str(e)}

    if fib_df is None or fib_df.empty:
        return {"available": False, "reason": "NO_HTF_SWINGS"}

    try:
        if reference_ts is not None:
            ref_rows = fib_df[fib_df["timestamp"] <= reference_ts]
            if ref_rows.empty:
                return {"available": False, "reason": "HTF_NO_HISTORY"}
            latest_htf = ref_rows.iloc[-1]
        else:
            latest_htf = fib_df.iloc[-1]

        # Check if levels are valid
        if pd.isna(latest_htf["htf_fib_0618"]):
            return {"available": False, "reason": "NO_HTF_DATA"}

        last_htf_timestamp = _normalize_timestamp(latest_htf["timestamp"])
        data_age_hours = _compute_age_hours(last_htf_timestamp, reference_ts)

        if data_age_hours > MAX_HTF_AGE_HOURS:
            return {"available": False, "reason": "HTF_DATA_STALE"}

        # Return HTF context
        htf_context = {
            "available": True,
            "levels": {
                0.382: float(latest_htf["htf_fib_0382"]),
                0.5: float(latest_htf["htf_fib_05"]),
                0.618: float(latest_htf["htf_fib_0618"]),
                0.786: float(latest_htf["htf_fib_0786"]),
            },
            "swing_high": float(latest_htf["htf_swing_high"]),
            "swing_low": float(latest_htf["htf_swing_low"]),
            "swing_age_bars": int(latest_htf["htf_swing_age_bars"]),
            "data_age_hours": float(data_age_hours),
            "htf_timeframe": htf_timeframe,
            "last_update": last_htf_timestamp,
        }

        return htf_context

    except Exception as e:
        return {"available": False, "reason": "HTF_ERROR", "error": str(e)}


# Convenience functions for different HTF timeframes
def get_1d_fibonacci_context(ltf_candles: dict | list, **kwargs) -> dict:
    """Get 1D Fibonacci context."""
    return get_htf_fibonacci_context(ltf_candles, htf_timeframe="1D", **kwargs)


def get_4h_fibonacci_context(ltf_candles: dict | list, **kwargs) -> dict:
    """Get 4h Fibonacci context (alternative HTF)."""
    return get_htf_fibonacci_context(ltf_candles, htf_timeframe="4h", **kwargs)


def get_ltf_fibonacci_context(
    ltf_candles: dict | list,
    *,
    timeframe: str | None = None,
    config: FibonacciConfig | None = None,
    atr_values: Sequence[float] | None = None,
) -> dict:
    """
    Calculate Fibonacci context on the same timeframe as the candles (LTF).

    Useful when entries/exits should key off intraday swings while still allowing
    HTF context to act as trend filter.

    atr_values lets callers pass precomputed ATR (aligned with candles) to avoid
    recomputing the expensive ATR smoothing inside swing detection.
    """
    try:
        highs, lows, closes, timestamps = _to_series(ltf_candles)
    except Exception as exc:  # pragma: no cover - defensive
        return {"available": False, "reason": "LTF_INVALID_INPUT", "error": str(exc)}

    if highs.empty or lows.empty or closes.empty:
        return {"available": False, "reason": "LTF_NO_DATA"}

    # Use a dedicated config that exposes full spectrum levels (0.0 → 1.0)
    base_cfg = config or FibonacciConfig()
    fib_cfg = FibonacciConfig(
        levels=[0.0, 0.382, 0.5, 0.618, 0.786, 1.0],
        weights={
            0.0: 0.3,
            0.382: 0.6,
            0.5: 1.0,
            0.618: 1.0,
            0.786: 0.7,
            1.0: 0.3,
        },
        atr_depth=base_cfg.atr_depth,
        max_swings=base_cfg.max_swings,
        min_swings=base_cfg.min_swings,
        max_lookback=base_cfg.max_lookback,
    )

    try:
        swing_high_idx, swing_low_idx, swing_high_prices, swing_low_prices = detect_swing_points(
            highs,
            lows,
            closes,
            fib_cfg,
            atr_values=atr_values,
        )
    except Exception as exc:  # pragma: no cover - defensive
        return {"available": False, "reason": "LTF_SWING_ERROR", "error": str(exc)}

    if not swing_high_prices or not swing_low_prices:
        return {"available": False, "reason": "LTF_NO_SWINGS"}

    fib_prices = calculate_fibonacci_levels(swing_high_prices, swing_low_prices, fib_cfg.levels)
    if len(fib_prices) != len(fib_cfg.levels):
        return {"available": False, "reason": "LTF_LEVELS_INCOMPLETE"}

    levels = {level: float(price) for level, price in zip(fib_cfg.levels, fib_prices, strict=False)}
    swing_high = float(swing_high_prices[-1])
    swing_low = float(swing_low_prices[-1])
    swing_range = swing_high - swing_low
    if swing_range == 0:
        return {"available": False, "reason": "LTF_INVALID_SWING"}

    last_timestamp = None
    if timestamps is not None and not timestamps.empty:
        last_timestamp = timestamps.iloc[-1]

    trend = "bullish" if swing_high > swing_low else "bearish"

    return {
        "available": True,
        "levels": levels,
        "swing_high": swing_high,
        "swing_low": swing_low,
        "swing_range": swing_range,
        "trend": trend,
        "timeframe": timeframe,
        "timestamp": last_timestamp,
        "num_swing_highs": len(swing_high_prices),
        "num_swing_lows": len(swing_low_prices),
    }
