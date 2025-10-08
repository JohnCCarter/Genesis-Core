"""
Fair Value Gap (FVG) detection and analysis.

A Fair Value Gap is a price imbalance created when price moves so quickly
that it leaves a 'gap' or 'void' in the market structure. These gaps often
act as magnets for price to return and 'fill' the imbalance.

This module implements advanced FVG features that capture:
- Size quality (normalized by ATR)
- Displacement strength (body size + quality)
- Age dynamics (fresh vs old gaps)
- Distance metrics (mean reversion potential)
- Fill ratio (partial fills)
- Volume imbalance (orderflow confirmation)

References:
- ICT (Inner Circle Trader) concepts
- Smart Money Concepts (SMC)
- Liquidity voids and imbalances
"""

import math


def detect_fvg(
    highs: list[float],
    lows: list[float],
    closes: list[float],
    min_gap_pct: float = 0.1,
) -> list[dict | None]:
    """
    Detect Fair Value Gaps (FVG) in price action.

    A Bullish FVG occurs when:
        candle[i+2].low > candle[i].high
        (there's a gap between candle i and i+2)

    A Bearish FVG occurs when:
        candle[i+2].high < candle[i].low
        (there's a gap between candle i and i+2)

    Args:
        highs: High prices
        lows: Low prices
        closes: Close prices
        min_gap_pct: Minimum gap size as % of price (default 0.1%)

    Returns:
        List of FVG dicts or None for each bar:
        {
            'type': 'bullish' or 'bearish',
            'gap_start': float (low/high of gap),
            'gap_end': float (high/low of gap),
            'gap_size': float (absolute),
            'gap_size_pct': float (% of price),
            'created_at': int (index where FVG was created)
        }
    """
    if len(highs) < 3 or len(lows) < 3:
        return [None] * len(highs)

    fvgs = [None, None]  # First 2 candles can't have FVG

    for i in range(len(highs) - 2):
        # Need candles i, i+1, i+2
        if i + 2 >= len(highs):
            fvgs.append(None)
            continue

        high_0 = highs[i]
        low_0 = lows[i]
        # candle i+1 is the "impulse" candle that creates the gap
        high_2 = highs[i + 2]
        low_2 = lows[i + 2]

        current_price = closes[i + 2] if i + 2 < len(closes) else closes[-1]

        # Bullish FVG: gap between candle i high and candle i+2 low
        if low_2 > high_0:
            gap_size = low_2 - high_0
            gap_size_pct = 100 * gap_size / current_price if current_price > 0 else 0

            if gap_size_pct >= min_gap_pct:
                fvgs.append(
                    {
                        "type": "bullish",
                        "gap_start": high_0,
                        "gap_end": low_2,
                        "gap_size": gap_size,
                        "gap_size_pct": gap_size_pct,
                        "created_at": i + 2,
                    }
                )
            else:
                fvgs.append(None)

        # Bearish FVG: gap between candle i low and candle i+2 high
        elif high_2 < low_0:
            gap_size = low_0 - high_2
            gap_size_pct = 100 * gap_size / current_price if current_price > 0 else 0

            if gap_size_pct >= min_gap_pct:
                fvgs.append(
                    {
                        "type": "bearish",
                        "gap_start": low_0,
                        "gap_end": high_2,
                        "gap_size": gap_size,
                        "gap_size_pct": gap_size_pct,
                        "created_at": i + 2,
                    }
                )
            else:
                fvgs.append(None)
        else:
            fvgs.append(None)

    return fvgs


def get_nearest_unfilled_fvg(
    highs: list[float],
    lows: list[float],
    closes: list[float],
    current_index: int,
    lookback: int = 50,
    min_gap_pct: float = 0.1,
) -> dict | None:
    """
    Find the nearest unfilled FVG relative to current price.

    An FVG is considered 'filled' if price has traded through the gap zone.

    Args:
        highs: High prices
        lows: Low prices
        closes: Close prices
        current_index: Current bar index
        lookback: How many bars back to search (default 50)
        min_gap_pct: Minimum gap size threshold

    Returns:
        Dict with FVG info + distance metrics, or None if no unfilled FVG found
    """
    if current_index < 3:
        return None

    current_price = closes[current_index]
    start_idx = max(0, current_index - lookback)

    # Detect all FVGs in lookback period
    fvgs = detect_fvg(highs, lows, closes, min_gap_pct)

    # Find nearest unfilled FVG
    nearest_fvg = None
    min_distance = float("inf")

    for i in range(start_idx, current_index):
        if fvgs[i] is None:
            continue

        fvg = fvgs[i]
        gap_start = fvg["gap_start"]
        gap_end = fvg["gap_end"]

        # Check if FVG has been filled (price traded through the gap)
        filled = False
        for j in range(i + 1, current_index + 1):
            if j >= len(highs):
                break

            bar_high = highs[j]
            bar_low = lows[j]

            # Bullish FVG filled if price came down into the gap
            if fvg["type"] == "bullish" and bar_low <= gap_end:
                filled = True
                break

            # Bearish FVG filled if price came up into the gap
            if fvg["type"] == "bearish" and bar_high >= gap_end:
                filled = True
                break

        # If still unfilled, calculate distance
        if not filled:
            # Distance to gap midpoint
            gap_mid = (gap_start + gap_end) / 2
            distance = abs(current_price - gap_mid)

            if distance < min_distance:
                min_distance = distance
                nearest_fvg = {
                    **fvg,
                    "distance": distance,
                    "distance_pct": 100 * distance / current_price if current_price > 0 else 0,
                    "age": current_index - i,
                    "gap_mid": gap_mid,
                    "above_price": gap_mid > current_price,
                }

    return nearest_fvg


def calculate_htf_regime_slope(
    closes: list[float],
    ema_period: int = 100,
    resample_factor: int = 4,
) -> float:
    """
    Calculate higher timeframe (HTF) regime slope.

    Resamples closes to 4x timeframe and calculates EMA slope z-score.
    Example: 1h data → 4h regime

    Args:
        closes: Close prices
        ema_period: EMA period for regime (default 100)
        resample_factor: Resample ratio (default 4 for 1h→4h)

    Returns:
        Slope z-score (positive = uptrend, negative = downtrend)
    """
    if len(closes) < resample_factor * ema_period:
        return 0.0

    # Resample to HTF (take every Nth close)
    htf_closes = [closes[i] for i in range(0, len(closes), resample_factor)]

    if len(htf_closes) < ema_period + 10:
        return 0.0

    # Calculate EMA on HTF
    from core.indicators.ema import calculate_ema

    htf_ema = calculate_ema(htf_closes, period=ema_period)

    if len(htf_ema) < 10:
        return 0.0

    # Calculate slope over last 10 HTF bars
    recent_ema = htf_ema[-10:]
    slopes = [
        (recent_ema[i] - recent_ema[i - 1]) / recent_ema[i - 1] for i in range(1, len(recent_ema))
    ]

    if not slopes:
        return 0.0

    # Z-score of latest slope
    avg_slope = sum(slopes) / len(slopes)
    std_slope = (
        (sum((s - avg_slope) ** 2 for s in slopes) / len(slopes)) ** 0.5 if len(slopes) > 1 else 1.0
    )

    latest_slope = slopes[-1]
    slope_z = (latest_slope - avg_slope) / std_slope if std_slope > 0 else 0.0

    return slope_z


def calculate_rolling_zscore(
    value: float,
    history: list[float],
    window: int = 240,
) -> float:
    """
    Calculate z-score using rolling window.

    Args:
        value: Current value to normalize
        history: Historical values
        window: Rolling window size (default 240 = 10 days @ 1h)

    Returns:
        Z-score normalized value
    """
    if len(history) < 10:  # Minimum data requirement
        return 0.0

    # Get recent window
    recent = history[-min(window, len(history)) :]

    if len(recent) < 2:
        return 0.0

    mean = sum(recent) / len(recent)
    variance = sum((x - mean) ** 2 for x in recent) / len(recent)
    std = variance**0.5

    if std == 0:
        return 0.0

    return (value - mean) / std


def calculate_advanced_fvg_features(
    highs: list[float],
    lows: list[float],
    opens: list[float],
    closes: list[float],
    volumes: list[float],
    atr_values: list[float],
    fvg: dict,
    current_index: int,
    htf_regime_slope: float = 0.0,
) -> dict[str, float]:
    """
    Calculate advanced FVG quality metrics with proper normalization.

    Features are normalized using:
    - ATR scaling for distance/size metrics
    - Rolling z-score (240 bar window) for displacement, volume, regime
    - Log transform + z-score for age
    - [0,1] range for fill ratio (no transform needed)

    Args:
        highs, lows, opens, closes, volumes: Price/volume data
        atr_values: Pre-calculated ATR values
        fvg: FVG dict from get_nearest_unfilled_fvg
        current_index: Current bar index
        htf_regime_slope: HTF regime (already z-scored)

    Returns:
        Dict with normalized FVG metrics
    """
    created_idx = fvg["created_at"]
    gap_high = max(fvg["gap_start"], fvg["gap_end"])
    gap_low = min(fvg["gap_start"], fvg["gap_end"])
    gap_size = gap_high - gap_low

    # Get ATR at creation bar
    atr_at_creation = atr_values[created_idx] if created_idx < len(atr_values) else 1.0
    atr_current = atr_values[current_index] if current_index < len(atr_values) else 1.0

    # 1. fvg_size_atr: Gap size normalized by ATR at creation
    fvg_size_atr = gap_size / atr_at_creation if atr_at_creation > 0 else 0.0

    # 2. displacement_strength: Quality of the displacement candle
    # Candle B is at created_idx - 1 (the impulse candle)
    impulse_idx = max(0, created_idx - 1)
    if impulse_idx < len(opens):
        open_b = opens[impulse_idx]
        close_b = closes[impulse_idx]
        high_b = highs[impulse_idx]
        low_b = lows[impulse_idx]

        body_size = abs(close_b - open_b)
        true_range = high_b - low_b if high_b > low_b else 0.01
        atr_b = atr_values[impulse_idx] if impulse_idx < len(atr_values) else 1.0

        # (body / ATR) * (body / true_range)
        displacement_strength = (
            (body_size / atr_b) * (body_size / true_range) if atr_b > 0 and true_range > 0 else 0.0
        )
    else:
        displacement_strength = 0.0

    # 3. fvg_age_log: Log-scaled age (fresh gaps behave differently)
    age_bars = current_index - created_idx
    fvg_age_log = math.log1p(age_bars)  # log(1 + age)

    # 4. fvg_distance_atr: Distance normalized by current ATR
    current_price = closes[current_index] if current_index < len(closes) else closes[-1]
    gap_mid = (gap_high + gap_low) / 2
    distance = abs(current_price - gap_mid)
    fvg_distance_atr = distance / atr_current if atr_current > 0 else 0.0

    # 5. fvg_fill_ratio: How much of gap has been filled
    max_high_since = (
        max(highs[created_idx : current_index + 1]) if created_idx < len(highs) else gap_high
    )
    min_low_since = (
        min(lows[created_idx : current_index + 1]) if created_idx < len(lows) else gap_low
    )

    filled_top = min(gap_high, max_high_since)
    filled_bottom = max(gap_low, min_low_since)
    filled_range = max(0, filled_top - filled_bottom)
    fvg_fill_ratio = filled_range / gap_size if gap_size > 0 else 0.0
    fvg_fill_ratio = min(1.0, max(0.0, fvg_fill_ratio))  # Clamp to [0, 1]

    # 6. vol_imbalance_z: Volume z-score at creation + confirmation
    # Simplified: volume at impulse bar vs recent average
    impulse_idx = max(0, created_idx - 1)
    if impulse_idx < len(volumes) and len(volumes) > 30:
        recent_vols = volumes[max(0, impulse_idx - 30) : impulse_idx]
        avg_vol = sum(recent_vols) / len(recent_vols) if recent_vols else 1.0
        std_vol = (
            (sum((v - avg_vol) ** 2 for v in recent_vols) / len(recent_vols)) ** 0.5
            if recent_vols
            else 1.0
        )

        vol_b = volumes[impulse_idx]
        vol_z = (vol_b - avg_vol) / std_vol if std_vol > 0 else 0.0

        # Confirmation from current bar
        vol_current = volumes[current_index] if current_index < len(volumes) else avg_vol
        vol_z_current = (vol_current - avg_vol) / std_vol if std_vol > 0 else 0.0

        vol_imbalance_z = vol_z + 0.5 * vol_z_current
    else:
        vol_imbalance_z = 0.0

    # 7. trend_confluence: FVG aligned with HTF regime
    # +1 = bullish FVG in uptrend (confluence)
    # -1 = bearish FVG in downtrend (confluence)
    # 0 = counter-trend or no regime
    fvg_is_bullish = fvg["type"] == "bullish"
    htf_is_bullish = htf_regime_slope > 0.5  # Strong uptrend threshold
    htf_is_bearish = htf_regime_slope < -0.5  # Strong downtrend threshold

    if fvg_is_bullish and htf_is_bullish:
        trend_confluence = 1.0
    elif not fvg_is_bullish and htf_is_bearish:
        trend_confluence = -1.0
    else:
        trend_confluence = 0.0

    # 8. distance_to_midline_normalized: Entry zone detection
    # Positive = above midline (short opportunity)
    # Negative = below midline (long opportunity)
    # Magnitude = how far (normalized)
    current_price = closes[current_index] if current_index < len(closes) else closes[-1]
    gap_mid = (gap_high + gap_low) / 2
    distance_to_midline = current_price - gap_mid
    distance_to_midline_normalized = distance_to_midline / atr_current if atr_current > 0 else 0.0

    # 9. risk_reward_structure: Natural R:R from gap
    # For bullish FVG (support): risk = distance to gap_low, reward = gap size
    # For bearish FVG (resistance): risk = distance to gap_high, reward = gap size
    if fvg_is_bullish:
        risk_distance = abs(current_price - gap_low)
    else:
        risk_distance = abs(current_price - gap_high)

    reward_potential = gap_size  # Full gap traversal as reward
    risk_reward_ratio = reward_potential / risk_distance if risk_distance > 0 else 0.0

    # Clip to reasonable range (0-5x R:R)
    risk_reward_ratio = min(5.0, max(0.0, risk_reward_ratio))

    return {
        "fvg_size_atr": fvg_size_atr,
        "displacement_strength": displacement_strength,
        "fvg_age_log": fvg_age_log,
        "fvg_distance_atr": fvg_distance_atr,
        "fvg_fill_ratio": fvg_fill_ratio,
        "vol_imbalance_z": vol_imbalance_z,
        "trend_confluence": trend_confluence,
        "distance_to_midline_norm": distance_to_midline_normalized,
        "risk_reward_ratio": risk_reward_ratio,
    }


def extract_fvg_features(
    highs: list[float],
    lows: list[float],
    opens: list[float],
    closes: list[float],
    volumes: list[float],
    atr_values: list[float],
    current_index: int,
    lookback: int = 50,
    htf_resample: int = 4,
) -> dict[str, float]:
    """
    Extract advanced FVG-based features for ML model.

    Features capture:
    - Size quality (fvg_size_atr)
    - Displacement quality (displacement_strength)
    - Age dynamics (fvg_age_log)
    - Distance to gap (fvg_distance_atr)
    - Fill status (fvg_fill_ratio)
    - Volume imbalance (vol_imbalance_z)
    - HTF trend confluence (trend_confluence)
    - Entry zone (distance_to_midline_norm)
    - Risk/Reward structure (risk_reward_ratio)
    - Direction (fvg_bullish)

    Args:
        highs: High prices
        lows: Low prices
        opens: Open prices
        closes: Close prices
        volumes: Volume data
        atr_values: Pre-calculated ATR values
        current_index: Current bar index
        lookback: How many bars back to search
        htf_resample: HTF resample factor (4 = 1h→4h)

    Returns:
        Dict with advanced FVG features (all 0.0 if no FVG found)
    """
    # Calculate HTF regime slope
    htf_regime_slope = calculate_htf_regime_slope(closes, resample_factor=htf_resample)

    fvg = get_nearest_unfilled_fvg(highs, lows, closes, current_index, lookback)

    if fvg is None:
        return {
            "fvg_present": 0.0,
            "fvg_size_atr": 0.0,
            "displacement_strength": 0.0,
            "fvg_age_log": 0.0,
            "fvg_distance_atr": 0.0,
            "fvg_fill_ratio": 0.0,
            "vol_imbalance_z": 0.0,
            "trend_confluence": 0.0,
            "distance_to_midline_norm": 0.0,
            "risk_reward_ratio": 0.0,
            "fvg_bullish": 0.0,
        }

    # Calculate advanced metrics with HTF regime
    advanced = calculate_advanced_fvg_features(
        highs, lows, opens, closes, volumes, atr_values, fvg, current_index, htf_regime_slope
    )

    return {
        "fvg_present": 1.0,
        "fvg_size_atr": advanced["fvg_size_atr"],
        "displacement_strength": advanced["displacement_strength"],
        "fvg_age_log": advanced["fvg_age_log"],
        "fvg_distance_atr": advanced["fvg_distance_atr"],
        "fvg_fill_ratio": advanced["fvg_fill_ratio"],
        "vol_imbalance_z": advanced["vol_imbalance_z"],
        "trend_confluence": advanced["trend_confluence"],
        "distance_to_midline_norm": advanced["distance_to_midline_norm"],
        "risk_reward_ratio": advanced["risk_reward_ratio"],
        "fvg_bullish": 1.0 if fvg["type"] == "bullish" else -1.0,
    }
