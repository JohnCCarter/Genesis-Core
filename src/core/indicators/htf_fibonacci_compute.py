"""HTF Fibonacci computation helpers."""

from typing import Any

import pandas as pd

from core.indicators.fibonacci import (
    FibonacciConfig,
    calculate_atr,
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
    """Get the most recent valid swings as of a specific index."""
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
    """Compute 1D Fibonacci levels for each bar in the HTF DataFrame."""
    if not pd.api.types.is_datetime64_any_dtype(htf_candles["timestamp"]):
        htf_candles["timestamp"] = pd.to_datetime(htf_candles["timestamp"])

    atr_series = calculate_atr(htf_candles["high"], htf_candles["low"], htf_candles["close"])
    atr_arr = atr_series.to_numpy(copy=False)

    htf_results: list[dict[str, Any]] = []
    n = int(len(htf_candles))
    lookback = int(getattr(config, "max_lookback", 250) or 250)

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
