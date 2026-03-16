from __future__ import annotations

from typing import Any


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def compute_htf_regime(
    htf_fib_data: dict[str, Any] | None,
    current_price: float | None = None,
) -> str:
    if not htf_fib_data or not isinstance(htf_fib_data, dict):
        return "unknown"

    if not htf_fib_data.get("available"):
        return "unknown"

    if current_price is None or current_price <= 0:
        return "unknown"

    swing_high = _safe_float(htf_fib_data.get("swing_high"))
    swing_low = _safe_float(htf_fib_data.get("swing_low"))

    if swing_high is None or swing_low is None:
        return "unknown"

    if swing_high <= swing_low:
        return "unknown"

    swing_range = swing_high - swing_low
    position_in_range = (current_price - swing_low) / swing_range

    if position_in_range >= 0.618:
        return "bull"
    if position_in_range <= 0.382:
        return "bear"
    return "ranging"
