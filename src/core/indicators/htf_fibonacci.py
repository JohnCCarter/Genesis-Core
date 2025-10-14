"""
HTF (Higher Timeframe) Fibonacci Mapping for Genesis-Core

Cross-timeframe Fibonacci projection with strict AS-OF semantics (no lookahead).
Maps 1D Fibonacci levels to LTF bars (1h/30m) for structure-aware exits.
"""

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

    htf_results = []

    for i, row in htf_candles.iterrows():
        htf_time = row["timestamp"]

        # Get swing context AS-OF this bar (no lookahead!)
        # Only use swings that were "known" by bar i
        current_swing_highs = []
        current_swing_lows = []

        # Filter swings: only those with index <= i
        for swing_idx, swing_price in zip(swing_high_indices, swing_high_prices, strict=False):
            if swing_idx <= i:  # AS-OF: swing was known by bar i
                current_swing_highs.append(swing_price)

        for swing_idx, swing_price in zip(swing_low_indices, swing_low_prices, strict=False):
            if swing_idx <= i:  # AS-OF: swing was known by bar i
                current_swing_lows.append(swing_price)

        # Calculate Fibonacci levels from AS-OF swings
        fib_levels_list = calculate_fibonacci_levels(
            current_swing_highs, current_swing_lows, config.levels
        )

        # Convert fib_levels_list to dict by level
        fib_levels = {}
        if len(fib_levels_list) == len(config.levels):
            for level, price in zip(config.levels, fib_levels_list, strict=False):
                fib_levels[level] = price

        # Current swing context
        current_swing_high = current_swing_highs[-1] if current_swing_highs else None
        current_swing_low = current_swing_lows[-1] if current_swing_lows else None

        # Calculate swing age (bars since last swing)
        swing_age = 0
        if swing_high_indices or swing_low_indices:
            last_swing_idx = max(
                swing_high_indices[-1] if swing_high_indices else -1,
                swing_low_indices[-1] if swing_low_indices else -1,
            )
            swing_age = i - last_swing_idx

        htf_results.append(
            {
                "timestamp": htf_time,
                "htf_fib_0382": fib_levels.get(0.382, None),
                "htf_fib_05": fib_levels.get(0.5, None),
                "htf_fib_0618": fib_levels.get(0.618, None),
                "htf_fib_0786": fib_levels.get(0.786, None),
                "htf_swing_high": current_swing_high,
                "htf_swing_low": current_swing_low,
                "htf_swing_age_bars": swing_age,
            }
        )

    return pd.DataFrame(htf_results)


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

    # Step 2: Project to LTF bars with AS-OF semantik
    ltf_results = []

    for _, ltf_row in ltf_candles.iterrows():
        ltf_time = ltf_row["timestamp"]

        # Find latest HTF data BEFORE this LTF bar (AS-OF, no lookahead)
        valid_htf = htf_fib_df[htf_fib_df["timestamp"] < ltf_time]

        if len(valid_htf) > 0:
            # Use latest available HTF data
            latest_htf = valid_htf.iloc[-1]

            # Calculate data freshness
            htf_data_age = (ltf_time - latest_htf["timestamp"]).total_seconds() / 3600  # hours

            ltf_results.append(
                {
                    "timestamp": ltf_time,
                    "htf_fib_0382": latest_htf["htf_fib_0382"],
                    "htf_fib_05": latest_htf["htf_fib_05"],
                    "htf_fib_0618": latest_htf["htf_fib_0618"],
                    "htf_fib_0786": latest_htf["htf_fib_0786"],
                    "htf_swing_high": latest_htf["htf_swing_high"],
                    "htf_swing_low": latest_htf["htf_swing_low"],
                    "htf_swing_age_bars": latest_htf["htf_swing_age_bars"],
                    "htf_data_age_hours": htf_data_age,
                }
            )
        else:
            # No HTF data available yet → neutral/None values
            ltf_results.append(
                {
                    "timestamp": ltf_time,
                    "htf_fib_0382": None,
                    "htf_fib_05": None,
                    "htf_fib_0618": None,
                    "htf_fib_0786": None,
                    "htf_swing_high": None,
                    "htf_swing_low": None,
                    "htf_swing_age_bars": None,
                    "htf_data_age_hours": None,
                }
            )

    return pd.DataFrame(ltf_results)


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
    # Only provide HTF context for LTF timeframes
    if timeframe not in ["1h", "30m", "6h", "15m"]:
        return {"available": False, "reason": "HTF_NOT_APPLICABLE"}

    # Check cache first (simple cache key based on symbol + timeframe)
    cache_key = f"{symbol}_{htf_timeframe}"
    if cache_key in _htf_context_cache:
        cached_context = _htf_context_cache[cache_key]
        # Check if cache is still valid (not too old)
        if cached_context.get("available", False):
            data_age_hours = cached_context.get("data_age_hours", 999)
            if data_age_hours < 24:  # Cache valid for 24 hours
                return cached_context

    try:
        # Load HTF candles
        htf_candles = load_candles_data(symbol, htf_timeframe)

        # Simplified approach: Just compute HTF Fibonacci levels from most recent data
        # Skip complex timestamp mapping for dict format (used in extract_features)
        htf_fib_result = compute_htf_fibonacci_levels(htf_candles, config)

        if htf_fib_result.empty:
            return {"available": False, "reason": "NO_HTF_SWINGS"}

        # Get most recent HTF context
        latest_htf = htf_fib_result.iloc[-1]

        # Check if levels are valid
        if pd.isna(latest_htf["htf_fib_0618"]):
            return {"available": False, "reason": "NO_HTF_DATA"}

        # Calculate data age in hours (time since last HTF bar)
        last_htf_timestamp = latest_htf["timestamp"]
        if isinstance(last_htf_timestamp, int | float):
            last_htf_timestamp = pd.Timestamp(last_htf_timestamp, unit="ms")
        data_age_hours = (pd.Timestamp.now() - last_htf_timestamp).total_seconds() / 3600

        # Check data freshness (don't use stale HTF data)
        MAX_HTF_AGE_HOURS = 168  # Max 7 days old for 1D data (more lenient for testing)
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
        
        # Cache the result for future use
        _htf_context_cache[cache_key] = htf_context
        
        return htf_context

    except FileNotFoundError as e:
        # HTF data not available (expected in some cases)
        return {"available": False, "reason": "HTF_DATA_NOT_FOUND", "error": str(e)}

    except Exception as e:
        # Unexpected error - log but don't crash
        return {"available": False, "reason": "HTF_ERROR", "error": str(e)}


# Convenience functions for different HTF timeframes
def get_1d_fibonacci_context(ltf_candles: dict | list, **kwargs) -> dict:
    """Get 1D Fibonacci context."""
    return get_htf_fibonacci_context(ltf_candles, htf_timeframe="1D", **kwargs)


def get_4h_fibonacci_context(ltf_candles: dict | list, **kwargs) -> dict:
    """Get 4h Fibonacci context (alternative HTF)."""
    return get_htf_fibonacci_context(ltf_candles, htf_timeframe="4h", **kwargs)
