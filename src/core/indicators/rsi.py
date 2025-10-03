from __future__ import annotations

from collections.abc import Iterable


def calculate_rsi(values: Iterable[float], period: int = 14) -> list[float]:
    """Beräkna RSI (Wilder's smoothing) som ren funktion.

    Returnerar lista med samma längd som input. För de första N-1 värdena
    används glidande init, sedan Wilder-smoothing.
    """
    prices = [float(v) for v in values]
    n = int(period)
    if n <= 0:
        raise ValueError("period must be > 0")
    if not prices:
        return []
    gains: list[float] = [0.0]
    losses: list[float] = [0.0]
    for i in range(1, len(prices)):
        delta = prices[i] - prices[i - 1]
        gains.append(max(delta, 0.0))
        losses.append(max(-delta, 0.0))
    rsi: list[float] = []
    if len(prices) < n + 1:
        # för kort serie: enkel fallback
        return [50.0 for _ in prices]
    avg_gain = sum(gains[1 : n + 1]) / n
    avg_loss = sum(losses[1 : n + 1]) / n
    # Första RSI värde efter init
    rs = (avg_gain / avg_loss) if avg_loss > 0 else float("inf")
    rsi.extend([50.0] * (n - 1))
    rsi.append(100.0 - (100.0 / (1.0 + rs)))
    # Fortsatt smoothing
    for i in range(n + 1, len(prices)):
        avg_gain = (avg_gain * (n - 1) + gains[i]) / n
        avg_loss = (avg_loss * (n - 1) + losses[i]) / n
        rs = (avg_gain / avg_loss) if avg_loss > 0 else float("inf")
        rsi.append(100.0 - (100.0 / (1.0 + rs)))
    # Pad om vi har färre rsi än priser (bör ej ske med logiken ovan)
    while len(rsi) < len(prices):
        rsi.insert(0, 50.0)
    return rsi
