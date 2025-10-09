"""
Derived features extracted from FVG concepts.

These features capture the STATISTICAL ESSENCE of FVG patterns
without the non-stationary visual pattern recognition:

1. momentum_displacement_z: Surge detection (like FVG formation)
2. price_stretch_z: Mean reversion potential (like distance to midline)
3. trend_confluence: Multi-timeframe alignment (like HTF filter)
4. volatility_shift: Regime change detection
5. volume_anomaly_z: Orderflow confirmation
6. regime_persistence: Trend stability
7. price_reversion_potential: Inverted stretch signal
"""


def calculate_momentum_displacement_z(
    closes: list[float],
    atr_values: list[float],
    period: int = 3,
    window: int = 240,
) -> list[float]:
    """
    Momentum surge detector (FVG displacement concept).

    Measures: Δclose(period) / ATR
    Z-scored over rolling window for stationarity.

    Args:
        closes: Close prices
        atr_values: ATR values
        period: Lookback for delta (default 3)
        window: Rolling window for z-score (default 240 = 10 days @ 1h)

    Returns:
        Z-scored momentum displacement
    """
    if len(closes) < period + 1:
        return [0.0] * len(closes)

    # Calculate raw displacement
    displacement = []
    for i in range(len(closes)):
        if i < period:
            displacement.append(0.0)
            continue

        delta_close = closes[i] - closes[i - period]
        atr = atr_values[i] if i < len(atr_values) else 1.0

        if atr > 0:
            displacement.append(delta_close / atr)
        else:
            displacement.append(0.0)

    # Rolling z-score
    result = []
    for i in range(len(displacement)):
        if i < 10:  # Minimum data
            result.append(0.0)
            continue

        window_data = displacement[max(0, i - window + 1) : i + 1]
        mean = sum(window_data) / len(window_data)
        variance = sum((x - mean) ** 2 for x in window_data) / len(window_data)
        std = variance**0.5

        if std > 0:
            result.append((displacement[i] - mean) / std)
        else:
            result.append(0.0)

    return result


def calculate_price_stretch_z(
    closes: list[float],
    ema_values: list[float],
    atr_values: list[float],
    window: int = 240,
) -> list[float]:
    """
    Mean reversion detector (FVG midline distance concept).

    Measures: (close - EMA) / ATR
    Z-scored over rolling window.

    Args:
        closes: Close prices
        ema_values: EMA (e.g., EMA50)
        atr_values: ATR values
        window: Rolling window for z-score

    Returns:
        Z-scored price stretch
    """
    if len(closes) != len(ema_values):
        return [0.0] * len(closes)

    # Calculate raw stretch
    stretch = []
    for i in range(len(closes)):
        if i >= len(ema_values) or i >= len(atr_values):
            stretch.append(0.0)
            continue

        price_diff = closes[i] - ema_values[i]
        atr = atr_values[i] if atr_values[i] > 0 else 1.0

        stretch.append(price_diff / atr)

    # Rolling z-score
    result = []
    for i in range(len(stretch)):
        if i < 10:
            result.append(0.0)
            continue

        window_data = stretch[max(0, i - window + 1) : i + 1]
        mean = sum(window_data) / len(window_data)
        variance = sum((x - mean) ** 2 for x in window_data) / len(window_data)
        std = variance**0.5

        if std > 0:
            result.append((stretch[i] - mean) / std)
        else:
            result.append(0.0)

    return result


def calculate_trend_confluence(
    ema_fast: list[float],
    ema_slow: list[float],
    window: int = 20,
) -> list[float]:
    """
    Multi-timeframe trend alignment (FVG HTF confluence concept).

    Measures: correlation(slope_fast, slope_slow)

    Args:
        ema_fast: Fast EMA (e.g., EMA20)
        ema_slow: Slow EMA (e.g., EMA100)
        window: Window for slope calculation

    Returns:
        Correlation coefficient [-1, 1]
    """
    if len(ema_fast) != len(ema_slow) or len(ema_fast) < window + 1:
        return [0.0] * len(ema_fast)

    result = []

    for i in range(len(ema_fast)):
        if i < window:
            result.append(0.0)
            continue

        # OPTIMIZED: Simple slope alignment instead of full correlation
        # 100x faster, captures same concept
        fast_start = ema_fast[i - window]
        fast_end = ema_fast[i]
        slow_start = ema_slow[i - window]
        slow_end = ema_slow[i]

        if fast_start == 0 or slow_start == 0:
            result.append(0.0)
            continue

        fast_slope = (fast_end - fast_start) / fast_start
        slow_slope = (slow_end - slow_start) / slow_start

        # Alignment score: positive if same direction
        if fast_slope > 0 and slow_slope > 0:
            # Both uptrending
            confluence = min(abs(fast_slope), abs(slow_slope))
        elif fast_slope < 0 and slow_slope < 0:
            # Both downtrending
            confluence = -min(abs(fast_slope), abs(slow_slope))
        else:
            # Diverging
            confluence = 0.0

        # Normalize (typical slope ~0.01-0.10)
        confluence = max(-1.0, min(1.0, confluence * 10))

        result.append(confluence)

    return result


def calculate_volatility_shift(
    atr_short: list[float],
    atr_long: list[float],
) -> list[float]:
    """
    Volatility regime change detector.

    Measures: ATR(short) / ATR(long)

    Args:
        atr_short: Short-term ATR (e.g., ATR14)
        atr_long: Long-term ATR (e.g., ATR50)

    Returns:
        Volatility shift ratio
    """
    if len(atr_short) != len(atr_long):
        return [0.0] * min(len(atr_short), len(atr_long))

    result = []
    for i in range(len(atr_short)):
        if atr_long[i] > 0:
            result.append(atr_short[i] / atr_long[i])
        else:
            result.append(1.0)  # Neutral

    return result


def calculate_volume_anomaly_z(
    volumes: list[float],
    window: int = 240,
) -> list[float]:
    """
    Orderflow anomaly detector (FVG volume confirmation concept).

    Measures: z-score of volume over rolling window

    Args:
        volumes: Volume data
        window: Rolling window for z-score

    Returns:
        Z-scored volume
    """
    result = []

    for i in range(len(volumes)):
        if i < 10:
            result.append(0.0)
            continue

        window_data = volumes[max(0, i - window + 1) : i + 1]
        mean = sum(window_data) / len(window_data)
        variance = sum((x - mean) ** 2 for x in window_data) / len(window_data)
        std = variance**0.5

        if std > 0:
            result.append((volumes[i] - mean) / std)
        else:
            result.append(0.0)

    return result


def calculate_regime_persistence(
    ema_values: list[float],
    window: int = 24,
) -> list[float]:
    """
    Trend stability indicator.

    Measures: rolling mean of sign(EMA_slope)

    Args:
        ema_values: EMA values
        window: Rolling window (default 24 = 1 day @ 1h)

    Returns:
        Persistence score [-1, 1]
    """
    if len(ema_values) < window + 1:
        return [0.0] * len(ema_values)

    # Calculate slope signs
    signs = [0.0]  # First bar has no slope
    for i in range(1, len(ema_values)):
        if ema_values[i - 1] != 0:
            slope = (ema_values[i] - ema_values[i - 1]) / ema_values[i - 1]
            signs.append(1.0 if slope > 0 else -1.0 if slope < 0 else 0.0)
        else:
            signs.append(0.0)

    # Rolling mean of signs
    result = []
    for i in range(len(signs)):
        if i < window:
            result.append(0.0)
            continue

        window_signs = signs[i - window + 1 : i + 1]
        persistence = sum(window_signs) / len(window_signs)
        result.append(persistence)

    return result


def calculate_price_reversion_potential(
    price_stretch_z: list[float],
) -> list[float]:
    """
    Inverted stretch signal (higher = more reversion potential).

    Measures: -abs(price_stretch_z)

    Args:
        price_stretch_z: Z-scored price stretch

    Returns:
        Reversion potential (higher value = stronger mean reversion setup)
    """
    return [-abs(x) for x in price_stretch_z]
