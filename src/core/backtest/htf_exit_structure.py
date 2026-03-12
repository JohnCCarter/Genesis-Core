from __future__ import annotations


def detect_structure_break(
    *,
    position_side: str,
    current_price: float,
    htf_levels: dict[float, float],
    ema_slope50_z: float,
) -> str | None:
    """Return the preserved structure-break reason string when a full exit should trigger."""
    if position_side == "LONG":
        fib_0618 = htf_levels.get(0.618)
        if fib_0618 and current_price < fib_0618 and ema_slope50_z < -0.5:
            return "STRUCTURE_BREAK_DOWN"
        return None

    fib_0382 = htf_levels.get(0.382)
    if fib_0382 and current_price > fib_0382 and ema_slope50_z > 0.5:
        return "STRUCTURE_BREAK_UP"
    return None
