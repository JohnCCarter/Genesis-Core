from __future__ import annotations

from typing import Iterable, Literal

from core.indicators.ema import calculate_ema

Signal = Literal["buy", "sell", "hold"]


def ema_cross_signal(closes: Iterable[float], fast: int = 12, slow: int = 26) -> Signal:
    """Minimal EMA-cross.

    - Returnerar "buy" när senaste fast EMA korsar upp över slow EMA
    - Returnerar "sell" när senaste fast EMA korsar ned under slow EMA
    - Annars "hold"
    """
    prices = [float(x) for x in closes]
    if len(prices) < max(fast, slow) + 1:
        return "hold"
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    # Korsa upp/ned mellan senaste två punkter
    f_prev, f_now = ema_fast[-2], ema_fast[-1]
    s_prev, s_now = ema_slow[-2], ema_slow[-1]
    if f_prev <= s_prev and f_now > s_now:
        return "buy"
    if f_prev >= s_prev and f_now < s_now:
        return "sell"
    return "hold"
