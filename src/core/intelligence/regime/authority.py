from __future__ import annotations

from collections.abc import Callable
from typing import Any

_ALLOWED_AUTHORITATIVE_REGIMES = {"bull", "bear", "ranging", "balanced"}


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def normalize_authoritative_regime(observed: Any) -> str:
    normalized = str(observed).strip().lower() if observed is not None else ""
    if normalized in _ALLOWED_AUTHORITATIVE_REGIMES:
        return normalized
    return "balanced"


def detect_authoritative_regime_from_precomputed_ema50(
    candles: dict[str, Any],
    configs: dict[str, Any],
) -> str | None:
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

    if not (
        isinstance(ema50, list | tuple)
        and (closes is not None)
        and (ema_idx is not None)
        and 0 <= ema_idx < len(ema50)
    ):
        return None

    current_price = _safe_float(closes[-1])
    current_ema = _safe_float(ema50[ema_idx])
    if current_price is None or current_ema is None:
        return None
    if current_ema == 0:
        return "balanced"

    trend = (current_price - current_ema) / current_ema
    if trend > 0.02:
        return "bull"
    if trend < -0.02:
        return "bear"
    return "ranging"


def detect_authoritative_regime_legacy(
    candles: dict[str, Any],
    configs: dict[str, Any],
    *,
    fallback_detect_regime_unified: Callable[[dict[str, Any]], str],
) -> str:
    precomputed_regime = detect_authoritative_regime_from_precomputed_ema50(candles, configs)
    if precomputed_regime is not None:
        return precomputed_regime
    return str(fallback_detect_regime_unified(candles))
