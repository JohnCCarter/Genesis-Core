"""
Unified regime detection matching the analysis used for calibration.

This uses EMA-based trend classification (matching analyze_calibration_by_regime.py)
instead of ADX-based classification to ensure consistency between:
- Training/calibration analysis
- Live inference

Regimes:
- bear: Price < EMA by >2% (downtrend)
- bull: Price > EMA by >2% (uptrend)
- ranging: Price within ±2% of EMA (sideways)
"""

from __future__ import annotations

from typing import Literal

Regime = Literal["bear", "bull", "ranging", "balanced"]


def detect_regime_unified(
    candles: dict[str, list[float]],
    ema_period: int = 50,
) -> Regime:
    """
    Detect market regime using EMA-based trend classification.

    This matches the classification used in calibration analysis scripts.

    Args:
        candles: Dictionary with OHLCV lists
        ema_period: EMA period for trend detection (default: 50)

    Returns:
        Regime: "bear", "bull", or "ranging"
    """
    from core.indicators.ema import calculate_ema

    close = candles.get("close")

    # Avoid NumPy truth-value ambiguity: check None/length explicitly
    if close is None or len(close) < ema_period:
        return "balanced"

    # Calculate EMA
    ema = calculate_ema(close, ema_period)

    if not ema or len(ema) == 0:
        return "balanced"

    # Get current values
    current_price = close[-1]
    current_ema = ema[-1]

    if current_ema == 0:
        return "balanced"

    # Calculate trend (price deviation from EMA)
    trend = (current_price - current_ema) / current_ema

    # Classify based on trend thresholds
    # These match analyze_calibration_by_regime.py exactly
    if trend > 0.02:  # +2%
        return "bull"
    elif trend < -0.02:  # -2%
        return "bear"
    else:
        return "ranging"


def detect_volatility_regime(
    candles: dict[str, list[float]],
    atr_period: int = 14,
) -> Literal["highvol", "lowvol"]:
    """
    Detect volatility regime.

    Args:
        candles: Dictionary with OHLCV lists
        atr_period: ATR period (default: 14)

    Returns:
        "highvol" or "lowvol"
    """
    from core.indicators.atr import calculate_atr

    high = candles.get("high", [])
    low = candles.get("low", [])
    close = candles.get("close")

    # Avoid NumPy truth-value ambiguity
    if close is None or len(close) < atr_period + 50:
        return "lowvol"

    # Calculate ATR
    atr = calculate_atr(high, low, close, atr_period)

    if not atr or len(atr) < 50:
        return "lowvol"

    # Get recent volatility
    recent_atr = atr[-50:]  # Last 50 bars
    median_atr = sorted(recent_atr)[len(recent_atr) // 2]  # Median
    current_atr = atr[-1]

    # Classify based on median
    if current_atr > median_atr:
        return "highvol"
    else:
        return "lowvol"
