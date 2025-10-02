from __future__ import annotations

from typing import Any, Dict, Tuple


def _clamp01(x: float) -> float:
    if x != x:  # NaN
        return 0.0
    if x == float("inf"):
        return 1.0
    if x == float("-inf"):
        return 0.0
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


def compute_confidence(
    probas: Dict[str, float],
    *,
    atr_pct: float | None = None,
    spread_bp: float | None = None,
    volume_score: float | None = None,
    data_quality: float | None = None,
    config: Dict[str, Any] | None = None,
) -> Tuple[Dict[str, float], Dict[str, Any]]:
    """Beräkna konfidenser (pure) från sannolikheter och kvalitetsmått.

    - Monotoni: rangordning mellan p_long/p_short ska bevaras
    - Clamp till [0, 1]
    - Returnera (confidences, meta) där meta innehåller versions och reasons
    """
    # Basal kvalitetsscore (om ej given): 1.0
    quality = 1.0
    if data_quality is not None:
        try:
            quality = float(data_quality)
        except Exception:
            quality = 1.0
    # Enkel spread/vol-penalty kan bakas i quality, men undvik dubbeljustering
    # Här låter vi quality vara inputen (policy bestämmer hur den räknas ut).

    p_buy = float(probas.get("buy", 0.0)) if probas else 0.0
    p_sell = float(probas.get("sell", 0.0)) if probas else 0.0

    # Bevara rangordning: multiplicera båda med samma quality‑faktor
    c_buy = _clamp01(p_buy * quality)
    c_sell = _clamp01(p_sell * quality)

    confidences: Dict[str, float] = {"buy": c_buy, "sell": c_sell}
    meta: Dict[str, Any] = {"versions": {"confidence": "v1"}, "reasons": []}
    return confidences, meta
