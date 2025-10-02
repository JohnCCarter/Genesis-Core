from __future__ import annotations

from typing import Iterable, List


def calculate_ema(values: Iterable[float], period: int) -> List[float]:
    """Beräkna Exponential Moving Average.

    Returnerar lista med samma längd som input. Första EMA sätts till första värdet.
    """
    vals = [float(v) for v in values]
    n = int(period)
    if n <= 0:
        raise ValueError("period must be > 0")
    if not vals:
        return []
    k = 2.0 / (n + 1.0)
    ema: List[float] = [vals[0]]
    for v in vals[1:]:
        ema.append(v * k + ema[-1] * (1.0 - k))
    return ema
