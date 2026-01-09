"""
Label generation for ML training.

Generates forward-looking labels from historical price data for supervised learning.

Labeling strategies:
- Binary: Simple up/down based on lookahead
- Multiclass: Up/neutral/down with thresholds
- Triple-Barrier: Realistic profit target, stop loss, and time exit
"""

from __future__ import annotations


def generate_labels(
    prices: list[float],
    lookahead_bars: int = 10,
    threshold_pct: float = 0.0,
) -> list[int | None]:
    """
    Generate binary labels based on forward-looking price movement.

    Label = 1 if price increases by > threshold_pct% in lookahead_bars
    Label = 0 if price decreases or stays flat
    Label = None if not enough future data available

    Args:
        prices: List of close prices (chronological order)
        lookahead_bars: Number of bars to look ahead for price movement
        threshold_pct: Minimum price change % to label as "up" (default: 0.0)

    Returns:
        List of labels (1, 0, or None) aligned with input prices

    Example:
        >>> prices = [100, 102, 105, 103, 101]
        >>> generate_labels(prices, lookahead_bars=2)
        [1, 1, 0, None, None]  # First increases, second increases, third drops

    Notes:
        - Uses close[i] -> close[i + lookahead_bars] for label
        - Last lookahead_bars entries will have None labels
        - No lookahead bias: label[i] only uses prices[i:i+lookahead_bars+1]
    """
    if not prices:
        return []

    if lookahead_bars <= 0:
        raise ValueError("lookahead_bars must be positive")

    labels: list[int | None] = []

    for i in range(len(prices)):
        future_idx = i + lookahead_bars

        # Not enough future data
        if future_idx >= len(prices):
            labels.append(None)
            continue

        current_price = prices[i]
        future_price = prices[future_idx]

        # Handle zero/invalid prices (current or future)
        if current_price <= 0 or future_price <= 0:
            labels.append(None)
            continue

        # Calculate percentage change
        pct_change = ((future_price - current_price) / current_price) * 100.0

        # Binary label: 1 if up, 0 if down/flat
        label = 1 if pct_change > threshold_pct else 0
        labels.append(label)

    return labels


def generate_multiclass_labels(
    prices: list[float],
    lookahead_bars: int = 10,
    up_threshold_pct: float = 0.5,
    down_threshold_pct: float = -0.5,
) -> list[int | None]:
    """
    Generate 3-class labels based on forward-looking price movement.

    Label = 2 if price increases by > up_threshold_pct%
    Label = 1 if price stays within thresholds (neutral/hold)
    Label = 0 if price decreases by < down_threshold_pct%
    Label = None if not enough future data available

    Args:
        prices: List of close prices (chronological order)
        lookahead_bars: Number of bars to look ahead
        up_threshold_pct: Minimum % increase to label as "up" (default: 0.5%)
        down_threshold_pct: Maximum % decrease to label as "down" (default: -0.5%)

    Returns:
        List of labels (2, 1, 0, or None) aligned with input prices

    Example:
        >>> prices = [100, 102, 105, 103, 99]
        >>> generate_multiclass_labels(prices, lookahead_bars=2, up_threshold_pct=0.5, down_threshold_pct=-0.5)
        [2, 1, 0, None, None]  # Up 5%, neutral 1%, down 4%
    """
    if not prices:
        return []

    if lookahead_bars <= 0:
        raise ValueError("lookahead_bars must be positive")

    if up_threshold_pct <= down_threshold_pct:
        raise ValueError("up_threshold_pct must be > down_threshold_pct")

    labels: list[int | None] = []

    for i in range(len(prices)):
        future_idx = i + lookahead_bars

        # Not enough future data
        if future_idx >= len(prices):
            labels.append(None)
            continue

        current_price = prices[i]
        future_price = prices[future_idx]

        # Handle zero/invalid prices (current or future)
        if current_price <= 0 or future_price <= 0:
            labels.append(None)
            continue

        # Calculate percentage change
        pct_change = ((future_price - current_price) / current_price) * 100.0

        # 3-class label
        if pct_change > up_threshold_pct:
            label = 2  # Strong up
        elif pct_change < down_threshold_pct:
            label = 0  # Strong down
        else:
            label = 1  # Neutral/hold

        labels.append(label)

    return labels


def align_features_with_labels(
    features_count: int,
    labels: list[int | None],
) -> tuple[int, int]:
    """
    Calculate valid range for features-labels alignment.

    Returns indices [start, end) where both features and labels are valid.
    Excludes rows where label is None.

    Args:
        features_count: Number of feature rows
        labels: List of labels (may contain None)

    Returns:
        Tuple of (start_idx, end_idx) for valid data

    Example:
        >>> features_count = 100
        >>> labels = [1, 0, 1, ..., None, None]  # Last 10 are None
        >>> align_features_with_labels(features_count, labels)
        (0, 90)  # First 90 rows have valid labels
    """
    if features_count != len(labels):
        raise ValueError(
            f"Features count ({features_count}) must match labels length ({len(labels)})"
        )

    # Find first valid label
    start_idx = 0
    for i, label in enumerate(labels):
        if label is not None:
            start_idx = i
            break
    else:
        # No valid labels found
        return 0, 0

    # Find last valid label
    end_idx = len(labels)
    for i in range(len(labels) - 1, -1, -1):
        if labels[i] is not None:
            end_idx = i + 1
            break

    return start_idx, end_idx


def generate_triple_barrier_labels(
    prices: list[float],
    profit_threshold_pct: float = 0.3,
    stop_threshold_pct: float = 0.2,
    max_holding_bars: int = 5,
) -> list[int | None]:
    """
    Generate triple-barrier labels for realistic trading scenarios.

    Uses three barriers:
    1. Profit target: Exit when price moves up by profit_threshold_pct%
    2. Stop loss: Exit when price moves down by stop_threshold_pct%
    3. Time exit: Exit after max_holding_bars if neither barrier hit

    Label = 1 if profit target hit first (profitable trade)
    Label = 0 if stop loss hit first (losing trade)
    Label = None if time exit with small move (< min of thresholds)

    Args:
        prices: List of close prices (chronological order)
        profit_threshold_pct: Profit target in % (e.g., 0.3 for +0.3%)
        stop_threshold_pct: Stop loss in % (e.g., 0.2 for -0.2%)
        max_holding_bars: Maximum bars to hold position

    Returns:
        List of labels (1=profitable, 0=loss, None=neutral/timeout)

    Example:
        >>> prices = [100, 100.5, 101, 100.3, 99.5, 99]
        >>> labels = generate_triple_barrier_labels(
        ...     prices, profit_threshold_pct=0.3, stop_threshold_pct=0.2,
        ...     max_holding_bars=5
        ... )

    Notes:
        - More realistic than simple binary labels
        - Filters noisy trades (small moves → None)
        - Asymmetric R:R ratio possible (profit != stop)
        - No lookahead bias: evaluates bar-by-bar
    """
    if not prices:
        return []

    if profit_threshold_pct <= 0 or stop_threshold_pct <= 0:
        raise ValueError("Thresholds must be positive")

    if max_holding_bars <= 0:
        raise ValueError("max_holding_bars must be positive")

    labels: list[int | None] = []

    for i in range(len(prices)):
        entry_price = prices[i]

        # Invalid entry price
        if entry_price <= 0:
            labels.append(None)
            continue

        # Not enough future bars for evaluation
        if i + max_holding_bars >= len(prices):
            labels.append(None)
            continue

        # Calculate barrier levels
        profit_target = entry_price * (1 + profit_threshold_pct / 100)
        stop_loss = entry_price * (1 - stop_threshold_pct / 100)

        # Scan forward bars to find which barrier hit first
        label = None
        for j in range(i + 1, min(i + max_holding_bars + 1, len(prices))):
            current_price = prices[j]

            # Check if invalid price
            if current_price <= 0:
                continue

            # Check profit target (hit first = profitable)
            if current_price >= profit_target:
                label = 1  # Profitable trade
                break

            # Check stop loss (hit first = loss)
            if current_price <= stop_loss:
                label = 0  # Losing trade
                break

        # If we reach here without hitting barriers, check time exit
        if label is None:
            # Get exit price at max holding period
            exit_idx = min(i + max_holding_bars, len(prices) - 1)
            exit_price = prices[exit_idx]

            if exit_price <= 0:
                labels.append(None)
                continue

            # Calculate final return
            price_change_pct = ((exit_price - entry_price) / entry_price) * 100

            # Significant move = use direction, else None
            min_threshold = min(profit_threshold_pct, stop_threshold_pct)
            if abs(price_change_pct) < min_threshold / 2:
                # Too small move, label as None (not tradeable)
                label = None
            elif price_change_pct > 0:
                # Positive but didn't hit target - weak profitable
                label = 1
            else:
                # Negative but didn't hit stop - weak loss
                label = 0

        labels.append(label)

    return labels


def generate_adaptive_triple_barrier_labels(
    closes: list[float],
    highs: list[float],
    lows: list[float],
    profit_multiplier: float = 1.5,
    stop_multiplier: float = 1.0,
    max_holding_bars: int = 5,
    atr_period: int = 14,
) -> list[int | None]:
    """
    Generate triple-barrier labels with ATR-adaptive thresholds (NO LOOKAHEAD).

    **CRITICAL:** Calculates ATR point-in-time at each bar to prevent lookahead bias.
    For bar i, ATR is computed ONLY from historical data (bars 0 to i).

    profit_target = entry_price + (profit_multiplier × ATR_at_i)
    stop_loss = entry_price - (stop_multiplier × ATR_at_i)

    Args:
        closes: List of close prices
        highs: List of high prices
        lows: List of low prices
        profit_multiplier: ATR multiplier for profit target (e.g., 1.5)
        stop_multiplier: ATR multiplier for stop loss (e.g., 1.0)
        max_holding_bars: Maximum holding period
        atr_period: ATR calculation period (default 14)

    Returns:
        List of labels (1=profitable, 0=loss, None=neutral)

    Example:
        >>> closes = [100, 102, 101, 103, 104]
        >>> highs = [102, 104, 103, 105, 106]
        >>> lows = [99, 101, 100, 102, 103]
        >>> labels = generate_adaptive_triple_barrier_labels(
        ...     closes, highs, lows, profit_multiplier=1.5, stop_multiplier=1.0
        ... )

    Notes:
        - **NO LOOKAHEAD BIAS:** ATR at bar i uses ONLY bars 0:i+1
        - Adapts to market volatility
        - High volatility → wider barriers
        - Low volatility → tighter barriers
        - More realistic than fixed % thresholds
    """
    from core.indicators.atr import calculate_atr

    if not closes or not highs or not lows:
        return []

    if len(closes) != len(highs) or len(closes) != len(lows):
        raise ValueError("closes, highs, lows must have same length")

    if profit_multiplier <= 0 or stop_multiplier <= 0:
        raise ValueError("Multipliers must be positive")

    if max_holding_bars <= 0:
        raise ValueError("max_holding_bars must be positive")

    if atr_period <= 0:
        raise ValueError("atr_period must be positive")

    labels: list[int | None] = []

    for i in range(len(closes)):
        entry_price = closes[i]

        # Invalid entry price
        if entry_price <= 0:
            labels.append(None)
            continue

        # Not enough future bars for holding period
        if i + max_holding_bars >= len(closes):
            labels.append(None)
            continue

        # **CRITICAL: Point-in-time ATR calculation (NO LOOKAHEAD)**
        # Only use data available up to bar i (inclusive)
        if i < atr_period:
            # Not enough history for ATR, skip
            labels.append(None)
            continue

        # Calculate ATR using ONLY historical data (bars 0 to i)
        atr_values = calculate_atr(
            highs[: i + 1], lows[: i + 1], closes[: i + 1], period=atr_period
        )

        if not atr_values:
            labels.append(None)
            continue

        current_atr = atr_values[-1]  # Latest ATR value at bar i

        # Invalid ATR
        if current_atr <= 0 or str(current_atr) == "nan":
            labels.append(None)
            continue

        # Calculate ATR-based barriers
        profit_target = entry_price + (profit_multiplier * current_atr)
        stop_loss = entry_price - (stop_multiplier * current_atr)

        # Scan forward for barrier hits
        label = None
        for j in range(i + 1, min(i + max_holding_bars + 1, len(closes))):
            # Use highs/lows for intrabar price action
            high_price = highs[j]
            low_price = lows[j]

            if high_price <= 0 or low_price <= 0:
                continue

            # Check profit target hit FIRST (intrabar high)
            if high_price >= profit_target:
                label = 1  # Profitable trade
                break

            # Check stop loss hit (intrabar low)
            if low_price <= stop_loss:
                label = 0  # Losing trade
                break

        # Time exit logic
        if label is None:
            exit_idx = min(i + max_holding_bars, len(closes) - 1)
            exit_price = closes[exit_idx]

            if exit_price <= 0:
                labels.append(None)
                continue

            # Compare to half of stop distance
            half_stop_distance = (stop_multiplier * current_atr) / 2

            price_change = exit_price - entry_price

            if abs(price_change) < half_stop_distance:
                label = None  # Too small
            elif price_change > 0:
                label = 1  # Weak profit
            else:
                label = 0  # Weak loss

        labels.append(label)

    return labels
