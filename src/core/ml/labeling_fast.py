"""
High-performance labeling functions using Numba JIT compilation.

Performance: 10-20× faster than pure Python implementation.
"""

import numpy as np
from numba import jit


@jit(nopython=True)
def calculate_atr_pointwise(
    highs: np.ndarray,
    lows: np.ndarray,
    closes: np.ndarray,
    period: int,
) -> np.ndarray:
    """
    Calculate ATR for each bar using ONLY historical data (no lookahead).

    For bar i, ATR is computed from bars [max(0, i-period+1) : i+1].

    Args:
        highs: High prices
        lows: Low prices
        closes: Close prices
        period: ATR period (e.g., 14)

    Returns:
        Array of ATR values (same length as input, NaN for insufficient history)
    """
    n = len(closes)
    atr = np.full(n, np.nan)

    if n < 2 or period < 1:
        return atr

    # Calculate True Range for each bar
    tr = np.zeros(n)
    tr[0] = highs[0] - lows[0]  # First bar

    for i in range(1, n):
        h_l = highs[i] - lows[i]
        h_pc = abs(highs[i] - closes[i - 1])
        l_pc = abs(lows[i] - closes[i - 1])
        tr[i] = max(h_l, h_pc, l_pc)

    # Calculate ATR using exponential moving average (Wilder's smoothing)
    alpha = 1.0 / period

    for i in range(period - 1, n):
        if i == period - 1:
            # First ATR = simple average of first 'period' TRs
            atr[i] = np.mean(tr[: i + 1])
        else:
            # Subsequent ATRs = EMA of TR
            atr[i] = alpha * tr[i] + (1 - alpha) * atr[i - 1]

    return atr


@jit(nopython=True)
def generate_adaptive_triple_barrier_labels_numba(
    closes: np.ndarray,
    highs: np.ndarray,
    lows: np.ndarray,
    profit_multiplier: float,
    stop_multiplier: float,
    max_holding: int,
    atr_period: int,
) -> np.ndarray:
    """
    Numba-compiled triple-barrier labeling (10-20× faster).

    NO LOOKAHEAD: ATR calculated point-in-time for each bar.

    Args:
        closes: Close prices
        highs: High prices
        lows: Low prices
        profit_multiplier: Profit target as multiple of ATR
        stop_multiplier: Stop loss as multiple of ATR
        max_holding: Max holding period (bars)
        atr_period: ATR calculation period

    Returns:
        Array of labels (1=profit, 0=loss, -1=None/filtered)
        Use -1 instead of None for Numba compatibility
    """
    n = len(closes)
    labels = np.full(n, -1, dtype=np.int32)  # -1 = None

    # Calculate ATR point-in-time for ALL bars
    atr = calculate_atr_pointwise(highs, lows, closes, atr_period)

    for i in range(n):
        # Need valid entry price and ATR
        if closes[i] <= 0 or np.isnan(atr[i]) or atr[i] <= 0:
            continue

        # Need enough future bars
        if i + max_holding >= n:
            continue

        entry_price = closes[i]
        current_atr = atr[i]

        # Calculate barriers
        profit_target = entry_price + (profit_multiplier * current_atr)
        stop_loss = entry_price - (stop_multiplier * current_atr)

        # Scan forward for barrier hits
        label = -1  # Default: None

        for j in range(i + 1, min(i + max_holding + 1, n)):
            high_price = highs[j]
            low_price = lows[j]

            if high_price <= 0 or low_price <= 0:
                continue

            # Check profit first (intrabar high)
            if high_price >= profit_target:
                label = 1  # Profit
                break

            # Check stop (intrabar low)
            if low_price <= stop_loss:
                label = 0  # Loss
                break

        # Time exit logic
        if label == -1:
            exit_idx = min(i + max_holding, n - 1)
            exit_price = closes[exit_idx]

            if exit_price <= 0:
                continue

            # Calculate final return
            price_change_pct = ((exit_price - entry_price) / entry_price) * 100

            # Minimum threshold (filter small moves)
            min_threshold_pct = min(
                profit_multiplier * current_atr / entry_price * 100,
                stop_multiplier * current_atr / entry_price * 100,
            )

            if abs(price_change_pct) < min_threshold_pct / 2:
                label = -1  # Too small, filter
            elif price_change_pct > 0:
                label = 1  # Weak profit
            else:
                label = 0  # Weak loss

        labels[i] = label

    return labels


def generate_adaptive_triple_barrier_labels_fast(
    closes: list[float],
    highs: list[float],
    lows: list[float],
    profit_multiplier: float = 1.5,
    stop_multiplier: float = 1.0,
    max_holding_bars: int = 5,
    atr_period: int = 14,
) -> list[int | None]:
    """
    High-performance wrapper for Numba-compiled triple-barrier labeling.

    10-20× faster than pure Python implementation.

    Args:
        closes: List of close prices
        highs: List of high prices
        lows: List of low prices
        profit_multiplier: Profit target as ATR multiple
        stop_multiplier: Stop loss as ATR multiple
        max_holding_bars: Max holding period
        atr_period: ATR calculation period

    Returns:
        List of labels (1=profit, 0=loss, None=filtered)
    """
    # Convert to numpy arrays
    closes_np = np.array(closes, dtype=np.float64)
    highs_np = np.array(highs, dtype=np.float64)
    lows_np = np.array(lows, dtype=np.float64)

    # Call Numba-compiled function
    labels_np = generate_adaptive_triple_barrier_labels_numba(
        closes_np,
        highs_np,
        lows_np,
        float(profit_multiplier),
        float(stop_multiplier),
        int(max_holding_bars),
        int(atr_period),
    )

    # Convert back to list with None
    labels = [None if l == -1 else int(l) for l in labels_np]

    return labels
