from __future__ import annotations

from collections.abc import Iterable

import numpy as np


def calculate_rsi(values: Iterable[float], period: int = 14) -> list[float]:
    """Beräkna RSI (Wilder's smoothing) med vektoriserad NumPy.

    Returnerar lista med samma längd som input.
    """
    prices = np.asarray(values, dtype=float)
    n = int(period)
    if n <= 0:
        raise ValueError("period must be > 0")
    if len(prices) == 0:
        return []

    # Calculate differences
    deltas = np.diff(prices)
    gains = np.maximum(deltas, 0.0)
    losses = np.maximum(-deltas, 0.0)

    # Initialize result array
    rsi = np.full_like(prices, 50.0)

    if len(prices) < n + 1:
        return rsi.tolist()

    # Wilder's Smoothing using optimized loop (Numba-friendly structure)
    # First value is simple average
    avg_gain = np.mean(gains[:n])
    avg_loss = np.mean(losses[:n])

    # Calculate first RSI
    if avg_loss == 0:
        rsi[n] = 100.0
    else:
        rs = avg_gain / avg_loss
        rsi[n] = 100.0 - (100.0 / (1.0 + rs))

    # Subsequent values
    # Note: Pure numpy vectorization of recursive Wilder's is hard without ufunc/numba.
    # We use a tight loop which is faster than the previous list operations.
    # For maximum speed, we could use Numba, but this is a good middle ground.

    # Pre-calculate alpha
    alpha = 1.0 / n

    # We can use a simple loop here. For very large arrays, Numba is better.
    # But compared to the previous implementation with list appends, this avoids memory reallocations.

    current_gain = avg_gain
    current_loss = avg_loss

    # Optimization: Access numpy array buffers directly
    gains_view = gains[n:]
    losses_view = losses[n:]
    rsi_view = rsi[n + 1 :]

    for i in range(len(gains_view)):
        current_gain = (current_gain * (n - 1) + gains_view[i]) * alpha
        current_loss = (current_loss * (n - 1) + losses_view[i]) * alpha

        if current_loss == 0:
            rsi_view[i] = 100.0
        else:
            rs = current_gain / current_loss
            rsi_view[i] = 100.0 - (100.0 / (1.0 + rs))

    return rsi.tolist()
