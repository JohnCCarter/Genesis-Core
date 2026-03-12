from __future__ import annotations

from typing import Any


def build_feature_meta(
    features: dict[str, float],
    fib_feature_status: dict[str, Any],
    htf_fibonacci_context: dict[str, Any],
    ltf_fibonacci_context: dict[str, Any],
    htf_selector_meta: dict[str, Any] | None,
    asof_bar: int,
    total_bars: int,
    atr14_current: float | None,
    atr_vals: list[float] | None,
    atr_period: int,
    atr_percentiles: dict[str, dict[str, float]],
) -> dict[str, Any]:
    meta_reasons: list[str] = []
    if not bool(fib_feature_status.get("available", True)):
        meta_reasons.append(str(fib_feature_status.get("reason") or "FIB_FEATURES_CONTEXT_ERROR"))

    return {
        "versions": {
            "features_v15_highvol_optimized": True,
            "features_v16_fibonacci": True,
            "features_v17_fibonacci_combinations": True,
            "htf_fibonacci_symmetric_chamoun": True,
        },
        "reasons": meta_reasons,
        "feature_count": len(features),
        "asof_bar": asof_bar,
        "uses_bars": [0, asof_bar],
        "total_bars_available": total_bars,
        "fibonacci_features": fib_feature_status,
        "htf_fibonacci": htf_fibonacci_context,
        "ltf_fibonacci": ltf_fibonacci_context,
        "current_atr": float(atr14_current) if atr14_current is not None else None,
        "current_atr_used": float(atr_vals[-1]) if atr_vals else None,
        "atr_period_used": atr_period,
        "atr_percentiles": atr_percentiles,
        "htf_selector": htf_selector_meta,
    }
