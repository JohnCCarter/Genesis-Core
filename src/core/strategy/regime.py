"""
Regime detection and classification for trading strategy.

Classifies market conditions into:
- Bull: Strong uptrend (ADX > 25, price > EMA, positive slope)
- Bear: Strong downtrend (ADX > 25, price < EMA, negative slope)
- Ranging: Consolidation (ADX < 20, low volatility)
- Balanced: Transitional state
"""

from __future__ import annotations

from typing import Any, Literal

# Regime types: bull/bear (trending), ranging (sideways), balanced (transition)
Regime = Literal["bull", "bear", "ranging", "balanced"]


def classify_regime(
    htf_features: dict[str, float],
    *,
    prev_state: dict[str, Any] | None = None,
    config: dict[str, Any] | None = None,
) -> tuple[Regime, dict[str, Any]]:
    """
    Classify market regime based on HTF features with hysteresis.

    Args:
        htf_features: Dictionary with:
            - adx: Trend strength (0-100, >25 = trending)
            - ema_slope: Price trend direction (positive = up, negative = down)
            - price_vs_ema: Price position relative to EMA (positive = above)
            - volatility: ATR-based volatility measure
        prev_state: Previous regime state for hysteresis
        config: Configuration with hysteresis_steps

    Returns:
        Tuple of (regime, state) where state contains regime and steps counter

    Regime Logic:
        - Bull: ADX > 25, price > EMA, positive slope
        - Bear: ADX > 25, price < EMA, negative slope
        - Ranging: ADX < 20, low volatility
        - Balanced: Transitional state
    """
    # Extract features
    adx = float(htf_features.get("adx", 0.0))
    ema_slope = float(htf_features.get("ema_slope", 0.0))
    price_vs_ema = float(htf_features.get("price_vs_ema", 0.0))
    volatility = float(htf_features.get("volatility", 0.0))

    # Configuration
    cfg = dict(config or {})
    hysteresis_steps = int((cfg.get("gates") or {}).get("hysteresis_steps") or 2)

    # Thresholds
    adx_trend_threshold = 25.0  # ADX > 25 = trending
    adx_range_threshold = 20.0  # ADX < 20 = ranging
    slope_threshold = 0.001  # Minimum slope for trend detection
    volatility_threshold = 0.05  # Low volatility for ranging (5%)

    # Determine candidate regime
    candidate: Regime

    # Bull: Strong uptrend (require ADX + either price above EMA OR positive slope)
    if adx > adx_trend_threshold and (price_vs_ema > 0 or ema_slope > slope_threshold):
        candidate = "bull"

    # Bear: Strong downtrend (require ADX + either price below EMA OR negative slope)
    elif adx > adx_trend_threshold and (price_vs_ema < 0 or ema_slope < -slope_threshold):
        candidate = "bear"

    # Ranging: Low ADX and low volatility
    elif adx < adx_range_threshold and volatility < volatility_threshold:
        candidate = "ranging"

    # Balanced: Transitional state
    else:
        candidate = "balanced"

    # Hysteresis: Require N consecutive observations before regime change
    ps = dict(prev_state or {})
    current = ps.get("regime", "balanced")
    steps = int(ps.get("steps", 0))

    if candidate == current:
        # Same regime: reset counter
        steps = 0
        regime = current  # type: ignore[assignment]
    else:
        # Different regime: increment counter
        steps += 1
        if steps >= hysteresis_steps:
            # Enough confirmation: change regime
            regime = candidate
            steps = 0
        else:
            # Not enough confirmation: hold current regime
            regime = current  # type: ignore[assignment]

    # Build state
    state: dict[str, Any] = {
        "regime": regime,
        "steps": steps,
        "candidate": candidate,
        "features": {
            "adx": adx,
            "ema_slope": ema_slope,
            "price_vs_ema": price_vs_ema,
            "volatility": volatility,
        },
    }

    return regime, state


def detect_regime_from_candles(
    candles: dict[str, list[float]],
    ema_period: int = 50,
    adx_period: int = 14,
) -> Regime:
    """
    Convenience function to detect regime directly from candle data.

    Args:
        candles: Dictionary with OHLCV lists
        ema_period: Period for EMA calculation (default 50)
        adx_period: Period for ADX calculation (default 14)

    Returns:
        Detected regime

    Example:
        >>> candles = {"close": [...], "high": [...], "low": [...]}
        >>> regime = detect_regime_from_candles(candles)
        >>> print(regime)  # "bull", "bear", "ranging", or "balanced"
    """
    from core.indicators.adx import calculate_adx
    from core.indicators.atr import calculate_atr
    from core.indicators.ema import calculate_ema

    close = candles.get("close", [])
    high = candles.get("high", [])
    low = candles.get("low", [])

    if not close or len(close) < max(ema_period, adx_period):
        return "balanced"

    # Calculate indicators
    ema = calculate_ema(close, ema_period)
    adx_list = calculate_adx(high, low, close, adx_period)
    atr = calculate_atr(high, low, close, adx_period)

    # Get latest values
    current_price = close[-1]
    current_ema = ema[-1] if ema else current_price
    current_adx = adx_list[-1] if adx_list else 0.0
    current_atr = atr[-1] if atr else 0.0

    # Calculate features
    price_vs_ema = (current_price - current_ema) / current_ema if current_ema > 0 else 0.0

    # EMA slope (last 5 bars)
    if len(ema) >= 5:
        ema_start = ema[-5]
        ema_end = ema[-1]
        ema_slope = (ema_end - ema_start) / ema_start if ema_start > 0 else 0.0
    else:
        ema_slope = 0.0

    # Volatility (ATR as % of price)
    volatility = current_atr / current_price if current_price > 0 else 0.0

    # Build features dict
    htf_features = {
        "adx": current_adx,
        "ema_slope": ema_slope,
        "price_vs_ema": price_vs_ema,
        "volatility": volatility,
    }

    # Classify without hysteresis
    regime, _ = classify_regime(htf_features)
    return regime
