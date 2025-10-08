"""
Volume analysis indicators for trading signals.

Volume metrics help confirm price movements and identify institutional interest:
- Volume change: Relative volume vs average
- Volume spike: Abnormally high volume (potential breakout)
- Volume trend: Short-term vs long-term volume momentum
- Volume-price divergence: Volume not confirming price action
"""

from __future__ import annotations


def calculate_volume_sma(volume: list[float], period: int) -> list[float]:
    """
    Calculate Simple Moving Average of volume.

    Args:
        volume: List of volume values
        period: Number of periods for SMA

    Returns:
        List of volume SMA values (NaN for first period-1 values)
    """
    if not volume or period <= 0:
        return []

    result = []
    for i in range(len(volume)):
        if i < period - 1:
            result.append(float("nan"))
        else:
            window = volume[i - period + 1 : i + 1]
            result.append(sum(window) / period)

    return result


def volume_change(
    volume: list[float],
    period: int = 20,
) -> list[float]:
    """
    Calculate volume change relative to average volume.

    Positive values indicate above-average volume.
    Negative values indicate below-average volume.

    Args:
        volume: List of volume values
        period: Lookback period for average (default 20)

    Returns:
        List of volume change percentages

    Example:
        >>> volume = [1000, 1100, 1200, 1500, 2000]
        >>> vc = volume_change(volume, period=3)
        >>> vc[-1]  # 2000 vs avg(1200,1500,2000) = 0.32
        0.32
    """
    if not volume or period <= 0 or len(volume) < period:
        return []

    vol_sma = calculate_volume_sma(volume, period)
    result = []

    for i in range(len(volume)):
        if str(vol_sma[i]) == "nan" or vol_sma[i] == 0:
            result.append(float("nan"))
        else:
            change = (volume[i] - vol_sma[i]) / vol_sma[i]
            result.append(change)

    return result


def volume_spike(
    volume: list[float],
    period: int = 20,
    threshold: float = 2.0,
) -> list[bool]:
    """
    Detect volume spikes (abnormally high volume).

    A spike occurs when current volume exceeds threshold × average volume.
    Often indicates strong institutional interest or breakout potential.

    Args:
        volume: List of volume values
        period: Lookback period for average (default 20)
        threshold: Multiplier for spike detection (default 2.0)

    Returns:
        List of boolean values (True = spike detected)

    Example:
        >>> volume = [1000, 1000, 1000, 1000, 3000]  # Last bar is spike
        >>> spikes = volume_spike(volume, period=4, threshold=2.0)
        >>> spikes[-1]
        True
    """
    if not volume or period <= 0 or threshold <= 0:
        return []

    vol_sma = calculate_volume_sma(volume, period)
    result = []

    for i in range(len(volume)):
        if str(vol_sma[i]) == "nan":
            result.append(False)
        else:
            is_spike = volume[i] > (threshold * vol_sma[i])
            result.append(is_spike)

    return result


def volume_trend(
    volume: list[float],
    fast_period: int = 10,
    slow_period: int = 50,
) -> list[float]:
    """
    Calculate volume trend (fast EMA / slow EMA).

    Values > 1.0 indicate increasing volume (bullish)
    Values < 1.0 indicate decreasing volume (bearish)

    Args:
        volume: List of volume values
        fast_period: Fast EMA period (default 10)
        slow_period: Slow EMA period (default 50)

    Returns:
        List of volume trend ratios

    Example:
        >>> volume = [1000] * 30 + [2000] * 30  # Volume doubles
        >>> trend = volume_trend(volume, fast_period=10, slow_period=30)
        >>> trend[-1] > 1.0  # Fast EMA > Slow EMA
        True
    """
    if not volume or fast_period <= 0 or slow_period <= 0:
        return []

    if len(volume) < slow_period:
        return [float("nan")] * len(volume)

    # Calculate EMAs
    fast_ema = calculate_volume_ema(volume, fast_period)
    slow_ema = calculate_volume_ema(volume, slow_period)

    result = []
    for i in range(len(volume)):
        if str(fast_ema[i]) == "nan" or str(slow_ema[i]) == "nan" or slow_ema[i] == 0:
            result.append(float("nan"))
        else:
            ratio = fast_ema[i] / slow_ema[i]
            result.append(ratio)

    return result


def calculate_volume_ema(volume: list[float], period: int) -> list[float]:
    """
    Calculate Exponential Moving Average of volume.

    Args:
        volume: List of volume values
        period: EMA period

    Returns:
        List of volume EMA values
    """
    if not volume or period <= 0:
        return []

    result = []
    multiplier = 2.0 / (period + 1)

    for i in range(len(volume)):
        if i == 0:
            result.append(volume[i])
        else:
            ema_val = (volume[i] * multiplier) + (result[i - 1] * (1 - multiplier))
            result.append(ema_val)

    # Mark first period-1 values as NaN (not fully initialized)
    for i in range(min(period - 1, len(result))):
        result[i] = float("nan")

    return result


def volume_price_divergence(
    close: list[float],
    volume: list[float],
    lookback: int = 14,
) -> list[float]:
    """
    Detect volume-price divergence.

    Bullish divergence: Price declining but volume increasing (potential reversal up)
    Bearish divergence: Price rising but volume declining (potential reversal down)

    Args:
        close: List of closing prices
        volume: List of volume values
        lookback: Period for trend comparison (default 14)

    Returns:
        List of divergence scores:
        - Positive: Bullish divergence (buy signal)
        - Negative: Bearish divergence (sell signal)
        - Near zero: No divergence

    Example:
        >>> close = [100, 99, 98, 97, 96]  # Price declining
        >>> volume = [1000, 1100, 1200, 1300, 1400]  # Volume increasing
        >>> div = volume_price_divergence(close, volume, lookback=5)
        >>> div[-1] > 0  # Bullish divergence
        True
    """
    if not close or not volume or len(close) != len(volume):
        return []

    if lookback <= 0 or len(close) < lookback:
        return []

    result = []

    for i in range(len(close)):
        if i < lookback - 1:
            result.append(float("nan"))
        else:
            # Calculate price trend (positive = rising, negative = falling)
            price_start = close[i - lookback + 1]
            price_end = close[i]
            if price_start != 0:
                price_trend = (price_end - price_start) / price_start
            else:
                price_trend = 0.0

            # Calculate volume trend
            vol_start = volume[i - lookback + 1]
            vol_end = volume[i]
            if vol_start != 0:
                vol_trend = (vol_end - vol_start) / vol_start
            else:
                vol_trend = 0.0

            # Divergence = opposite directions
            # If price down (-) and volume up (+) = bullish divergence (+)
            # If price up (+) and volume down (-) = bearish divergence (-)
            # Check if trends are opposite signs
            if price_trend * vol_trend < 0:
                # Opposite directions - divergence exists
                if price_trend < 0 and vol_trend > 0:
                    # Bullish divergence
                    divergence = abs(price_trend * vol_trend)
                else:
                    # Bearish divergence
                    divergence = -abs(price_trend * vol_trend)
            else:
                # Same direction - no divergence
                divergence = 0.0

            result.append(divergence)

    return result


def obv(close: list[float], volume: list[float]) -> list[float]:
    """
    Calculate On-Balance Volume (OBV).

    OBV accumulates volume based on price direction:
    - Price up: Add volume to OBV
    - Price down: Subtract volume from OBV
    - Price unchanged: OBV unchanged

    Args:
        close: List of closing prices
        volume: List of volume values

    Returns:
        List of OBV values

    Example:
        >>> close = [100, 101, 102, 101, 103]
        >>> volume = [1000, 1000, 1000, 1000, 1000]
        >>> obv_vals = obv(close, volume)
        >>> obv_vals[-1] > obv_vals[0]  # Net accumulation
        True
    """
    if not close or not volume or len(close) != len(volume):
        return []

    result = []
    obv_val = 0.0

    for i in range(len(close)):
        if i == 0:
            obv_val = volume[i]
        else:
            if close[i] > close[i - 1]:
                obv_val += volume[i]
            elif close[i] < close[i - 1]:
                obv_val -= volume[i]
            # Unchanged price: OBV stays same

        result.append(obv_val)

    return result
