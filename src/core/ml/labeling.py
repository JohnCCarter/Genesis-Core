"""
Label generation for ML training.

Generates forward-looking labels from historical price data for supervised learning.
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
