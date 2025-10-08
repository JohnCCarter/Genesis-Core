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


def calculate_sma(values: list[float], period: int) -> list[float]:
    """
    Calculate Simple Moving Average.

    Args:
        values: List of prices
        period: Number of periods for SMA

    Returns:
        List of SMA values (NaN for first period-1 values)
    """
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
    """
    Calculate Standard Deviation.

    Args:
        values: List of prices
        period: Number of periods
        sma: Pre-calculated SMA values

    Returns:
        List of standard deviation values
    """
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
    if not close or period <= 0 or len(close) < period:
        return {
            "middle": [],
            "upper": [],
            "lower": [],
            "width": [],
            "position": [],
        }

    # Calculate middle band (SMA)
    middle = calculate_sma(close, period)

    # Calculate standard deviation
    std = calculate_std_dev(close, period, middle)

    # Calculate upper and lower bands
    upper = []
    lower = []
    width = []
    position = []

    for i in range(len(close)):
        if str(middle[i]) == "nan" or str(std[i]) == "nan":
            upper.append(float("nan"))
            lower.append(float("nan"))
            width.append(float("nan"))
            position.append(float("nan"))
        else:
            upper_val = middle[i] + (std_dev * std[i])
            lower_val = middle[i] - (std_dev * std[i])

            upper.append(upper_val)
            lower.append(lower_val)

            # BB Width: (upper - lower) / middle
            # Higher values = higher volatility
            if middle[i] != 0:
                width_val = (upper_val - lower_val) / middle[i]
            else:
                width_val = 0.0
            width.append(width_val)

            # BB Position: (price - lower) / (upper - lower)
            # 0.0 = at lower band, 0.5 = at middle, 1.0 = at upper band
            band_range = upper_val - lower_val
            if band_range != 0:
                pos_val = (close[i] - lower_val) / band_range
                # Clamp between 0 and 1 (price can go outside bands)
                pos_val = max(0.0, min(1.0, pos_val))
            else:
                pos_val = 0.5
            position.append(pos_val)

    return {
        "middle": middle,
        "upper": upper,
        "lower": lower,
        "width": width,
        "position": position,
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
