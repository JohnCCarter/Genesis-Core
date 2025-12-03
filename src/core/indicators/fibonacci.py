"""
Fibonacci Retracement Features for Genesis-Core
Implements professional-grade Fibonacci analysis with adaptive swing detection.
"""

from collections.abc import Sequence
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
    high: pd.Series | Sequence[float],
    low: pd.Series | Sequence[float],
    close: pd.Series | Sequence[float],
    config: FibonacciConfig,
    atr_values: Sequence[float] | None = None,
) -> tuple[list[int], list[int], list[float], list[float]]:
    """
    Detect swing highs and lows using ATR-based pivot detection.

    Performance: Optimized using numpy arrays for ~80% speedup in nested loops.

    Args:
        high, low, close: Price series (pandas) or raw sequences
        config: Fibonacci configuration
        atr_values: Optional precomputed ATR values aligned with inputs

    Returns:
        swing_high_indices, swing_low_indices, swing_high_prices, swing_low_prices
    """

    def _as_array(
        series_or_seq: pd.Series | Sequence[float],
    ) -> tuple[np.ndarray, pd.Series | None]:
        if isinstance(series_or_seq, pd.Series):
            return series_or_seq.to_numpy(copy=False), series_or_seq
        return np.asarray(series_or_seq, dtype=float), None

    high_arr, high_series = _as_array(high)
    low_arr, low_series = _as_array(low)
    close_arr, close_series = _as_array(close)

    if atr_values is None:
        if high_series is None:
            high_series = pd.Series(high_arr, dtype=float)
        if low_series is None:
            low_series = pd.Series(low_arr, dtype=float)
        if close_series is None:
            close_series = pd.Series(close_arr, dtype=float)
        atr_series = calculate_atr(high_series, low_series, close_series)
        atr_arr = atr_series.to_numpy(copy=False)
    else:
        atr_arr = np.asarray(atr_values, dtype=float)
        if atr_arr.size == 0:
            return [], [], [], []
        min_len = min(len(high_arr), len(low_arr), len(close_arr), atr_arr.size)
        if min_len == 0:
            return [], [], [], []
        if not (len(high_arr) == len(low_arr) == len(close_arr) == atr_arr.size):
            high_arr = high_arr[-min_len:]
            low_arr = low_arr[-min_len:]
            close_arr = close_arr[-min_len:]
            atr_arr = atr_arr[-min_len:]

    atr_depth_int = max(1, int(config.atr_depth))

    # OPTIMIZATION: Arrays already prepared above; reuse directly
    range_span = high_arr - low_arr

    def _local_extrema_masks() -> tuple[np.ndarray, np.ndarray]:
        window = 2 * atr_depth_int + 1
        n = len(high_arr)
        if window > n:
            return np.zeros(n, dtype=bool), np.zeros(n, dtype=bool)

        high_windows = np.lib.stride_tricks.sliding_window_view(high_arr, window)
        low_windows = np.lib.stride_tricks.sliding_window_view(low_arr, window)
        center_idx = atr_depth_int

        max_vals = high_windows.max(axis=1)
        max_counts = (high_windows == max_vals[:, None]).sum(axis=1)
        center_vals_high = high_windows[:, center_idx]
        local_high_core = (center_vals_high == max_vals) & (max_counts == 1)

        min_vals = low_windows.min(axis=1)
        min_counts = (low_windows == min_vals[:, None]).sum(axis=1)
        center_vals_low = low_windows[:, center_idx]
        local_low_core = (center_vals_low == min_vals) & (min_counts == 1)

        high_mask = np.zeros(n, dtype=bool)
        low_mask = np.zeros(n, dtype=bool)
        idx_range = np.arange(atr_depth_int, n - atr_depth_int)
        high_mask[idx_range] = local_high_core
        low_mask[idx_range] = local_low_core
        return high_mask, low_mask

    local_high_mask, local_low_mask = _local_extrema_masks()

    # --- Vectorized Threshold Calculation ---
    # Calculate strength for all points: strength = range_span / atr
    # Handle ATR=0 -> inf (passes any threshold), ATR=NaN -> -inf (fails)
    with np.errstate(divide="ignore", invalid="ignore"):
        strength = np.divide(range_span, atr_arr)

    # Fix non-finite values
    # If ATR was 0, strength is inf. This is correct (infinite strength).
    # If ATR was NaN, strength is NaN. We replace with -inf to ensure it fails comparisons.
    strength = np.nan_to_num(strength, nan=-np.inf)

    # Get max strength for valid local extrema
    # We use the masks to select only local highs/lows
    high_strengths = strength[local_high_mask]
    low_strengths = strength[local_low_mask]

    max_h = np.max(high_strengths) if high_strengths.size > 0 else -np.inf
    max_l = np.max(low_strengths) if low_strengths.size > 0 else -np.inf

    # We want a threshold t such that we find at least one high and one low.
    # So t <= max_h AND t <= max_l.
    limit = min(max_h, max_l)

    # Determine the optimal threshold on the grid defined by start/step
    # We want the highest t in (start, start-step, ...) such that t <= limit.
    start = max(config.swing_threshold_multiple, 0.0)
    min_t = max(0.0, config.swing_threshold_min)
    step = config.swing_threshold_step

    if limit < min_t:
        # Even the minimum threshold is too high for the data
        best_threshold = min_t
    elif step <= 0:
        best_threshold = start
    else:
        # t = start - k * step <= limit
        # k * step >= start - limit
        # k >= (start - limit) / step
        k = np.ceil((start - limit) / step)
        k = max(0.0, k)
        best_threshold = start - k * step
        # Clamp to min_t
        if best_threshold < min_t:
            best_threshold = min_t

    # --- Single Detection Pass ---

    def _extract_swings(mask_type, threshold_val):
        """Extract and filter swings using vectorized operations."""
        # 1. Filter by threshold and extrema type
        valid_mask = (strength >= threshold_val) & mask_type
        indices = np.where(valid_mask)[0]

        if indices.size == 0:
            return []

        # 2. Filter by lookback (vectorized)
        # Lookback is relative to the most recent swing found
        last_idx = indices[-1]
        lookback_mask = (last_idx - indices) <= config.max_lookback
        indices = indices[lookback_mask]

        if indices.size == 0:
            return []

        # 3. Retrieve prices
        if mask_type is local_high_mask:
            prices = high_arr[indices]
        else:
            prices = low_arr[indices]

        # 4. Convert to list for overlap cleaning
        candidates = list(zip(indices, prices, strict=False))

        # 5. Remove overlaps (iterative, but on small dataset)
        cleaned = []
        for idx, price in candidates:
            if not cleaned or idx - cleaned[-1][0] > 10:  # Minimum 10 bars apart
                cleaned.append((idx, price))

        # 6. Keep max swings
        return cleaned[-config.max_swings :]

    swing_highs = _extract_swings(local_high_mask, best_threshold)
    swing_lows = _extract_swings(local_low_mask, best_threshold)

    # --- Fallback Logic ---
    if not swing_highs and high_arr.size > 0:
        fallback_idx = int(np.argmax(high_arr))
        fallback_price = float(high_arr[fallback_idx])
        swing_highs = [(fallback_idx, fallback_price)]

    if not swing_lows and low_arr.size > 0:
        fallback_idx = int(np.argmin(low_arr))
        fallback_price = float(low_arr[fallback_idx])
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
    """
    Remove overlapping swing points, keeping the most recent.

    NOTE: This function is kept for backward compatibility or external usage,
    but detect_swing_points now uses inline optimized logic.
    """
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

    # Calculate ATR (Series → numpy for fast indexing)
    atr_series = calculate_atr(df["high"], df["low"], df["close"])
    atr_arr = atr_series.to_numpy(copy=False)

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

    # Convert close to numpy once
    close_arr = df["close"].to_numpy(copy=False)

    # Compute Fibonacci levels once (based on latest swings)
    fib_levels_once = calculate_fibonacci_levels(swing_high_prices, swing_low_prices, config.levels)
    swing_high_latest = swing_high_prices[-1] if swing_high_prices else None
    swing_low_latest = swing_low_prices[-1] if swing_low_prices else None

    # Calculate features for each row (numpy indexing; no pandas .iloc inside loop)
    for i in range(len(df)):
        # Calculate features
        features = calculate_fibonacci_features(
            float(close_arr[i]),
            fib_levels_once,
            float(atr_arr[i]) if i < len(atr_arr) else 0.0,
            config,
            swing_high_latest,
            swing_low_latest,
        )

        # Store features
        for feature_name, value in features.items():
            features_df.loc[df.index[i], feature_name] = value

    return features_df
