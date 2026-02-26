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
    """Compute regime from HTF (1D) Fibonacci context for defensive sizing."""
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
    elif position_in_range <= 0.382:
        return "bear"
    else:
        return "ranging"


def detect_shadow_regime_from_regime_module(candles: dict[str, Any]) -> str | None:
    """Compute regime.py observer value in shadow-only mode."""
    try:
        from core.strategy.regime import detect_regime_from_candles

        return str(detect_regime_from_candles(candles))
    except Exception:
        return None


def detect_authoritative_regime(
    candles: dict[str, Any],
    configs: dict[str, Any],
) -> str:
    """Return authoritative regime for evaluate decision path.

    Authority remains `regime_unified.detect_regime_unified`.
    """
    pre = dict(configs.get("precomputed_features") or {})
    ema50 = pre.get("ema_50")
    closes = candles.get("close") if isinstance(candles, dict) else None

    ema_idx: int | None = None
    if "_global_index" in configs:
        try:
            ema_idx = int(configs.get("_global_index"))
        except (TypeError, ValueError):
            ema_idx = None
    if ema_idx is None and closes is not None:
        ema_idx = len(closes) - 1

    if (
        isinstance(ema50, list | tuple)
        and (closes is not None)
        and (ema_idx is not None)
        and 0 <= ema_idx < len(ema50)
    ):
        current_price = float(closes[-1])
        current_ema = float(ema50[ema_idx])
        if current_ema != 0:
            trend = (current_price - current_ema) / current_ema
            if trend > 0.02:
                return "bull"
            elif trend < -0.02:
                return "bear"
            else:
                return "ranging"
        return "balanced"

    from core.strategy import regime_unified as _regime_unified

    return _regime_unified.detect_regime_unified(candles, ema_period=50)
