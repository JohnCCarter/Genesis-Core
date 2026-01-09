"""
Bollinger Bands indicator for volatility analysis.

Bollinger Bands consist of:
- Middle band: Simple Moving Average (SMA)
- Upper band: SMA + (standard deviation × multiplier)
- Lower band: SMA - (standard deviation × multiplier)

Additional metrics:
- BB Width: (upper - lower) / middle (volatility indicator)
- BB Position: (price - lower) / (upper - lower) (price position in bands)
"""

from __future__ import annotations

import numpy as np


def _empty_response() -> dict[str, list[float]]:
    return {
        "middle": [],
        "upper": [],
        "lower": [],
        "width": [],
        "position": [],
    }


def calculate_sma(values: list[float], period: int) -> list[float]:
    """Historical helper kept for compatibility (used in tests/debug tooling)."""
    if not values or period <= 0:
        return []

    result = []
    for i in range(len(values)):
        if i < period - 1:
            result.append(float("nan"))
        else:
            window = values[i - period + 1 : i + 1]
            result.append(sum(window) / period)
    return result


def calculate_std_dev(values: list[float], period: int, sma: list[float]) -> list[float]:
    """Historical helper kept for compatibility (used in tests/debug tooling)."""
    if not values or period <= 0 or len(values) != len(sma):
        return []

    result = []
    for i in range(len(values)):
        if i < period - 1 or str(sma[i]) == "nan":
            result.append(float("nan"))
        else:
            window = values[i - period + 1 : i + 1]
            mean = sma[i]
            variance = sum((x - mean) ** 2 for x in window) / period
            result.append(variance**0.5)
    return result


def bollinger_bands(
    close: list[float],
    period: int = 20,
    std_dev: float = 2.0,
) -> dict[str, list[float]]:
    """
    Calculate Bollinger Bands.

    Args:
        close: List of closing prices
        period: Number of periods for SMA (default 20)
        std_dev: Standard deviation multiplier (default 2.0)

    Returns:
        Dictionary with:
        - middle: Middle band (SMA)
        - upper: Upper band (SMA + std_dev * std)
        - lower: Lower band (SMA - std_dev * std)
        - width: Band width (volatility indicator)
        - position: Price position within bands (0-1)

    Example:
        >>> close = [100, 102, 101, 103, 104, 102, 105, 107, 106, 108]
        >>> bb = bollinger_bands(close, period=5, std_dev=2.0)
        >>> bb["middle"][-1]  # Latest middle band
        105.6
    """
    if not close or period <= 0:
        return _empty_response()

    close_arr = np.asarray(close, dtype=float)
    n = close_arr.size
    if n < period:
        return _empty_response()

    windows = np.lib.stride_tricks.sliding_window_view(close_arr, period)
    sma_core = windows.mean(axis=1)
    std_core = windows.std(axis=1, ddof=0)

    pad = np.full(period - 1, np.nan, dtype=float)
    middle = np.concatenate((pad, sma_core))
    std_full = np.concatenate((pad, std_core))

    upper = middle + (std_dev * std_full)
    lower = middle - (std_dev * std_full)

    width = np.full(n, np.nan, dtype=float)
    valid = ~np.isnan(middle) & ~np.isnan(std_full)
    nonzero_middle = valid & (middle != 0.0)
    width[nonzero_middle] = (upper[nonzero_middle] - lower[nonzero_middle]) / middle[nonzero_middle]
    width[valid & ~nonzero_middle] = 0.0

    position = np.full(n, np.nan, dtype=float)
    band_range = upper - lower
    valid_range = valid & (band_range != 0.0)
    position[valid_range] = np.clip(
        (close_arr[valid_range] - lower[valid_range]) / band_range[valid_range], 0.0, 1.0
    )
    position[valid & ~valid_range] = 0.5

    return {
        "middle": middle.tolist(),
        "upper": upper.tolist(),
        "lower": lower.tolist(),
        "width": width.tolist(),
        "position": position.tolist(),
    }


def bb_squeeze(
    bb_width: list[float],
    lookback: int = 20,
) -> list[bool]:
    """
    Detect Bollinger Band squeeze (low volatility period).

    A squeeze occurs when BB width is at its lowest in the lookback period.
    Often precedes volatility expansion.

    Args:
        bb_width: Bollinger Band width values
        lookback: Number of periods to check (default 20)

    Returns:
        List of boolean values (True = squeeze detected)

    Example:
        >>> bb = bollinger_bands(close, period=20)
        >>> squeeze = bb_squeeze(bb["width"], lookback=20)
        >>> squeeze[-1]  # Is current candle in squeeze?
        True
    """
    if not bb_width or lookback <= 0:
        return []

    result = []
    for i in range(len(bb_width)):
        if i < lookback - 1 or str(bb_width[i]) == "nan":
            result.append(False)
        else:
            window = bb_width[i - lookback + 1 : i + 1]
            # Filter out NaN values
            valid_window = [x for x in window if str(x) != "nan"]
            if valid_window:
                # Current width is minimum in window = squeeze
                is_squeeze = bb_width[i] == min(valid_window)
                result.append(is_squeeze)
            else:
                result.append(False)

    return result
