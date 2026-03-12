from __future__ import annotations


def calculate_trailing_stop(
    *,
    position_side: str,
    current_price: float,
    ema50: float,
    atr: float,
    htf_levels: dict[float, float],
    trail_atr_multiplier: float,
) -> float:
    """Calculate dynamic trailing stop with HTF promotion semantics preserved."""
    if position_side == "LONG":
        base_trail = ema50 - (trail_atr_multiplier * atr)
        fib_05 = htf_levels.get(0.5)
        fib_0618 = htf_levels.get(0.618)
        if fib_05 and fib_0618 and current_price > fib_0618:
            return max(base_trail, fib_05)
        return base_trail

    base_trail = ema50 + (trail_atr_multiplier * atr)
    fib_05 = htf_levels.get(0.5)
    fib_0382 = htf_levels.get(0.382)
    if fib_05 and fib_0382 and current_price < fib_0382:
        return min(base_trail, fib_05)
    return base_trail


def calculate_fallback_trailing_stop(
    *, position_side: str, ema50: float, atr: float, trail_atr_multiplier: float
) -> float:
    """Calculate the fallback EMA-based trailing stop."""
    if position_side == "LONG":
        return ema50 - (trail_atr_multiplier * atr)
    return ema50 + (trail_atr_multiplier * atr)
