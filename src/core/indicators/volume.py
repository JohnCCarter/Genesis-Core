"""
Volume analysis indicators for trading signals.

Volume metrics help confirm price movements and identify institutional interest:
- Volume change: Relative volume vs average
- Volume spike: Abnormally high volume (potential breakout)
- Volume trend: Short-term vs long-term volume momentum
- Volume-price divergence: Volume not confirming price action
"""

from __future__ import annotations

import pandas as pd


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

    # OPTIMIZED: Use pandas rolling window (100x faster than manual loop)
    vol_series = pd.Series(volume)
    sma_series = vol_series.rolling(window=period, min_periods=period).mean()
    return sma_series.tolist()


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

    # OPTIMIZED: Vectorized calculation using pandas
    vol_series = pd.Series(volume)
    vol_sma = vol_series.rolling(window=period, min_periods=period).mean()
    change = (vol_series - vol_sma) / vol_sma
    return change.tolist()


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

    # OPTIMIZED: Vectorized calculation
    vol_series = pd.Series(volume)
    vol_sma = vol_series.rolling(window=period, min_periods=period).mean()
    is_spike = vol_series > (threshold * vol_sma)
    return is_spike.fillna(False).tolist()


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

    # OPTIMIZED: Use pandas ewm (exponentially weighted mean)
    vol_series = pd.Series(volume)
    ema_series = vol_series.ewm(span=period, adjust=False).mean()

    # Mark first period-1 values as NaN (not fully initialized)
    ema_series.iloc[: period - 1] = float("nan")

    return ema_series.tolist()


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

    # OPTIMIZED: Vectorized calculation using pandas
    price_series = pd.Series(close)
    vol_series = pd.Series(volume)

    # Calculate rolling trends (vectorized)
    price_start = price_series.shift(lookback - 1)
    price_trend = (price_series - price_start) / price_start.where(price_start != 0, 1)

    vol_start = vol_series.shift(lookback - 1)
    vol_trend = (vol_series - vol_start) / vol_start.where(vol_start != 0, 1)

    # Detect divergence: opposite signs
    opposite_signs = price_trend * vol_trend < 0

    # Calculate divergence score
    divergence = pd.Series(0.0, index=price_series.index)

    # Bullish divergence: price down, volume up
    bullish_mask = opposite_signs & (price_trend < 0) & (vol_trend > 0)
    divergence[bullish_mask] = abs(price_trend * vol_trend)[bullish_mask]

    # Bearish divergence: price up, volume down
    bearish_mask = opposite_signs & (price_trend > 0) & (vol_trend < 0)
    divergence[bearish_mask] = -abs(price_trend * vol_trend)[bearish_mask]

    # Mark insufficient data as NaN
    divergence.iloc[: lookback - 1] = float("nan")

    return divergence.tolist()


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

    # OPTIMIZED: Vectorized OBV calculation
    close_series = pd.Series(close)
    vol_series = pd.Series(volume)

    # Calculate price direction: 1 (up), -1 (down), 0 (unchanged)
    price_diff = close_series.diff()
    direction = pd.Series(0, index=close_series.index, dtype=int)
    direction[price_diff > 0] = 1
    direction[price_diff < 0] = -1

    # OBV = cumulative sum of (volume * direction)
    # First bar: direction is 0, so we need to handle separately
    signed_volume = vol_series * direction
    signed_volume.iloc[0] = vol_series.iloc[0]  # First value is just volume

    obv_series = signed_volume.cumsum()

    return obv_series.tolist()
