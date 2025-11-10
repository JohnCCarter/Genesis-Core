"""
Fibonacci Retracement Features for Genesis-Core
Implements professional-grade Fibonacci analysis with adaptive swing detection.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class FibonacciConfig:
    """Configuration for Fibonacci analysis."""

    levels: list[float] = None
    weights: dict[float, float] = None
    atr_depth: float = 6.0  # ATR multiplier for swing detection
    max_swings: int = 8
    min_swings: int = 3
    max_lookback: int = 250
    swing_threshold_multiple: float = 1.1  # Base ATR multiple required for a swing
    swing_threshold_min: float = 0.45  # Lowest ATR multiple when relaxing detection
    swing_threshold_step: float = 0.2  # Step to relax threshold when no swings

    def __post_init__(self):
        if self.levels is None:
            self.levels = [0.382, 0.5, 0.618, 0.786]
        if self.weights is None:
            self.weights = {0.382: 0.6, 0.5: 1.0, 0.618: 1.0, 0.786: 0.7}
        # Clamp swing detection parameters to sensible ranges
        if self.swing_threshold_step <= 0:
            self.swing_threshold_step = 0.0
        if self.swing_threshold_min > self.swing_threshold_multiple:
            self.swing_threshold_min = self.swing_threshold_multiple


def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Calculate ATR using Wilder's smoothing."""
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / period, adjust=False).mean()
    return atr


def detect_swing_points(
    high: pd.Series, low: pd.Series, close: pd.Series, config: FibonacciConfig
) -> tuple[list[int], list[int], list[float], list[float]]:
    """
    Detect swing highs and lows using ATR-based pivot detection.

    Args:
        high, low, close: Price series
        config: Fibonacci configuration

    Returns:
        swing_high_indices, swing_low_indices, swing_high_prices, swing_low_prices
    """
    atr = calculate_atr(high, low, close)

    atr_depth_int = max(1, int(config.atr_depth))

    # OPTIMIZATION: Convert to numpy arrays once to avoid repeated .iloc[] overhead
    high_arr = high.values
    low_arr = low.values
    atr_arr = atr.values

    def _detect(
        threshold_multiple: float,
    ) -> tuple[list[tuple[int, float]], list[tuple[int, float]]]:
        candidate_highs: list[tuple[int, float]] = []
        candidate_lows: list[tuple[int, float]] = []

        for i in range(atr_depth_int, len(close) - atr_depth_int):
            window_high = high_arr[i]
            window_low = low_arr[i]

            is_swing_high = True
            for j in range(i - atr_depth_int, i + atr_depth_int + 1):
                if j != i and high_arr[j] >= window_high:
                    is_swing_high = False
                    break

            is_swing_low = True
            for j in range(i - atr_depth_int, i + atr_depth_int + 1):
                if j != i and low_arr[j] <= window_low:
                    is_swing_low = False
                    break

            atr_value = atr_arr[i]
            threshold_value = float(atr_value) * threshold_multiple if not np.isnan(atr_value) else 0.0
            range_ok = (high_arr[i] - low_arr[i]) >= threshold_value

            if is_swing_high and range_ok:
                candidate_highs.append((i, float(window_high)))

            if is_swing_low and range_ok:
                candidate_lows.append((i, float(window_low)))

        cleaned_highs = _clean_swing_points(candidate_highs, config.max_lookback)
        cleaned_lows = _clean_swing_points(candidate_lows, config.max_lookback)

        cleaned_highs = cleaned_highs[-config.max_swings :] if cleaned_highs else []
        cleaned_lows = cleaned_lows[-config.max_swings :] if cleaned_lows else []

        return cleaned_highs, cleaned_lows

    threshold_multiple = max(config.swing_threshold_multiple, 0.0)
    min_threshold = max(0.0, config.swing_threshold_min)
    step = config.swing_threshold_step if config.swing_threshold_step >= 0 else 0.0

    swing_highs: list[tuple[int, float]] = []
    swing_lows: list[tuple[int, float]] = []
    attempted_min = False

    while threshold_multiple >= min_threshold - 1e-9:
        swing_highs, swing_lows = _detect(threshold_multiple)

        if swing_highs and swing_lows:
            # Found at least one of each, acceptable for Fibonacci projection
            break

        if step == 0:
            break

        if threshold_multiple <= min_threshold:
            if attempted_min:
                break
            attempted_min = True

        next_threshold = max(min_threshold, threshold_multiple - step)

        if next_threshold == threshold_multiple:
            break

        threshold_multiple = next_threshold

    if not swing_highs and len(high) > 0:
        fallback_idx = int(high.idxmax())
        fallback_price = float(high.iloc[fallback_idx])
        swing_highs = [(fallback_idx, fallback_price)]

    if not swing_lows and len(low) > 0:
        fallback_idx = int(low.idxmin())
        fallback_price = float(low.iloc[fallback_idx])
        swing_lows = [(fallback_idx, fallback_price)]

    # Extract indices and prices
    high_indices = [idx for idx, _ in swing_highs]
    low_indices = [idx for idx, _ in swing_lows]
    high_prices = [price for _, price in swing_highs]
    low_prices = [price for _, price in swing_lows]

    return high_indices, low_indices, high_prices, low_prices


def _clean_swing_points(
    swing_points: list[tuple[int, float]], max_lookback: int
) -> list[tuple[int, float]]:
    """Remove overlapping swing points, keeping the most recent."""
    if not swing_points:
        return []

    # Sort by index
    swing_points = sorted(swing_points, key=lambda x: x[0])

    # Remove points outside lookback window
    latest_idx = swing_points[-1][0]
    swing_points = [(idx, price) for idx, price in swing_points if latest_idx - idx <= max_lookback]

    # Remove overlaps (keep most recent)
    cleaned = []
    for idx, price in swing_points:
        if not cleaned or idx - cleaned[-1][0] > 10:  # Minimum 10 bars apart
            cleaned.append((idx, price))

    return cleaned


def calculate_fibonacci_levels(
    swing_highs: list[float], swing_lows: list[float], levels: list[float]
) -> list[float]:
    """Calculate Fibonacci retracement levels from swing points."""
    fib_levels = []

    # Use most recent swing high and low
    if len(swing_highs) >= 1 and len(swing_lows) >= 1:
        swing_high = swing_highs[-1]
        swing_low = swing_lows[-1]

        swing_range = swing_high - swing_low

        for level in levels:
            fib_price = swing_high - (swing_range * level)
            fib_levels.append(fib_price)

    return fib_levels


def calculate_fibonacci_features(
    price: float,
    fib_levels: list[float],
    atr: float,
    config: FibonacciConfig,
    swing_high: float = None,
    swing_low: float = None,
) -> dict[str, float]:
    """
    Calculate Fibonacci-based features for a given price point.

    Args:
        price: Current price
        fib_levels: List of Fibonacci retracement levels
        atr: Current ATR value
        config: Fibonacci configuration
        swing_high, swing_low: Current swing points

    Returns:
        Dictionary of Fibonacci features
    """
    features = {}

    if not fib_levels or atr <= 0:
        # Return neutral values if no valid data
        features.update(
            {
                "fib_dist_min_atr": 0.0,
                "fib_dist_signed_atr": 0.0,
                "fib_prox_score": 0.0,
                "fib0618_prox_atr": 0.0,
                "fib05_prox_atr": 0.0,
                "swing_retrace_depth": 0.0,
            }
        )
        return features

    # 1. Minimum distance to any Fibonacci level (normalized by ATR)
    distances = [abs(price - fib_level) for fib_level in fib_levels]
    min_distance = min(distances)
    features["fib_dist_min_atr"] = min_distance / atr if atr > 0 else 0.0

    # 2. Signed distance to nearest Fibonacci level
    nearest_fib_idx = distances.index(min_distance)
    nearest_fib = fib_levels[nearest_fib_idx]
    signed_distance = (price - nearest_fib) / atr if atr > 0 else 0.0
    features["fib_dist_signed_atr"] = signed_distance

    # 3. Proximity score (weighted sum of exponential distances)
    prox_score = 0.0
    total_weight = 0.0

    for i, fib_level in enumerate(fib_levels):
        if i < len(config.levels):
            level = config.levels[i]
            weight = config.weights.get(level, 1.0)
            distance = abs(price - fib_level)
            exp_distance = np.exp(-distance / (0.6 * atr)) if atr > 0 else 0.0
            prox_score += weight * exp_distance
            total_weight += weight

    features["fib_prox_score"] = prox_score / total_weight if total_weight > 0 else 0.0

    # 4. Specific proximity to key levels
    fib_618_idx = config.levels.index(0.618) if 0.618 in config.levels else -1
    fib_05_idx = config.levels.index(0.5) if 0.5 in config.levels else -1

    if fib_618_idx >= 0 and fib_618_idx < len(fib_levels):
        fib_618_dist = abs(price - fib_levels[fib_618_idx])
        features["fib0618_prox_atr"] = np.exp(-fib_618_dist / (0.6 * atr)) if atr > 0 else 0.0
    else:
        features["fib0618_prox_atr"] = 0.0

    if fib_05_idx >= 0 and fib_05_idx < len(fib_levels):
        fib_05_dist = abs(price - fib_levels[fib_05_idx])
        features["fib05_prox_atr"] = np.exp(-fib_05_dist / (0.6 * atr)) if atr > 0 else 0.0
    else:
        features["fib05_prox_atr"] = 0.0

    # 5. Swing retracement depth (position within current swing)
    if swing_high is not None and swing_low is not None and swing_high > swing_low:
        swing_range = swing_high - swing_low
        retrace_depth = (swing_high - price) / swing_range
        features["swing_retrace_depth"] = np.clip(retrace_depth, 0.0, 1.0)
    else:
        features["swing_retrace_depth"] = 0.0

    return features


def calculate_fibonacci_features_vectorized(
    df: pd.DataFrame, config: FibonacciConfig = None
) -> pd.DataFrame:
    """
    Calculate Fibonacci features for entire DataFrame (vectorized).

    Args:
        df: DataFrame with OHLC data
        config: Fibonacci configuration

    Returns:
        DataFrame with Fibonacci features
    """
    if config is None:
        config = FibonacciConfig()

    features_df = pd.DataFrame(index=df.index)

    # Calculate ATR
    atr = calculate_atr(df["high"], df["low"], df["close"])

    # Detect swing points
    swing_high_indices, swing_low_indices, swing_high_prices, swing_low_prices = (
        detect_swing_points(df["high"], df["low"], df["close"], config)
    )

    # Initialize feature columns
    feature_names = [
        "fib_dist_min_atr",
        "fib_dist_signed_atr",
        "fib_prox_score",
        "fib0618_prox_atr",
        "fib05_prox_atr",
        "swing_retrace_depth",
    ]

    for feature_name in feature_names:
        features_df[feature_name] = 0.0

    # Calculate features for each row
    for i in range(len(df)):
        # Get current swing context
        current_swing_high = swing_high_prices[-1] if swing_high_prices else None
        current_swing_low = swing_low_prices[-1] if swing_low_prices else None

        # Calculate Fibonacci levels
        fib_levels = calculate_fibonacci_levels(swing_high_prices, swing_low_prices, config.levels)

        # Calculate features
        features = calculate_fibonacci_features(
            df["close"].iloc[i],
            fib_levels,
            atr.iloc[i],
            config,
            current_swing_high,
            current_swing_low,
        )

        # Store features
        for feature_name, value in features.items():
            features_df.loc[df.index[i], feature_name] = value

    return features_df
