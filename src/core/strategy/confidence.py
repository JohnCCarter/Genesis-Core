from __future__ import annotations

from typing import Any


def _clamp01(x: float) -> float:
    if x != x:  # NaN
        return 0.0
    if x == float("inf"):
        return 1.0
    if x == float("-inf"):
        return 0.0
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


def _as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def _clamp(x: float, lo: float, hi: float) -> float:
    if x != x:  # NaN
        return lo
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x


def _linear_penalty(
    x: float,
    *,
    ref: float,
    max_x: float,
    floor: float,
) -> float:
    """Monoton penalty factor in [floor, 1].

    - x <= ref  => 1
    - x >= max  => floor
    - otherwise linear interpolation
    """
    if max_x <= ref:
        return 1.0
    if x <= ref:
        return 1.0
    if x >= max_x:
        return float(_clamp(floor, 0.0, 1.0))
    t = (x - ref) / (max_x - ref)
    t = _clamp(t, 0.0, 1.0)
    return float(1.0 - (1.0 - floor) * t)


def _soft_floor(base_01: float, *, floor: float, exponent: float = 1.0) -> float:
    """Map base in [0,1] into [floor,1] (then exponentiate)."""
    floor = float(_clamp(floor, 0.0, 1.0))
    exponent = float(exponent) if exponent is not None else 1.0
    exponent = 1.0 if exponent <= 0 else exponent
    base_01 = _clamp01(base_01)
    val = floor + (1.0 - floor) * base_01
    return float(_clamp(val, 0.0, 1.0) ** exponent)


def _compute_quality_factor(
    *,
    atr_pct: float | None,
    spread_bp: float | None,
    volume_score: float | None,
    data_quality: float | None,
    config: dict[str, Any] | None,
) -> tuple[float, dict[str, Any]]:
    cfg = dict(config or {})
    enabled = bool(cfg.get("enabled"))
    if not enabled:
        # v1 behavior: only honor data_quality if provided.
        dq = _as_float(data_quality)
        q = _clamp01(dq if dq is not None else 1.0)
        return q, {
            "version": "v1",
            "enabled": False,
            "quality_factor": q,
            "components": {"data_quality": q},
        }

    # v2 behavior: multiply stable component factors into overall quality factors.
    # We support per-component scopes:
    # - gate: affects entry gating confidence
    # - sizing: affects sizing confidence (position size scaling)
    # - both (default): affects both
    clamp_cfg = dict(cfg.get("clamp") or {})
    min_quality = float(clamp_cfg.get("min_quality", 0.20))
    min_quality = float(_clamp(min_quality, 0.0, 1.0))

    components_cfg = dict(cfg.get("components") or {})

    def _norm_scope(scope: Any) -> str:
        s = str(scope or "both").strip().lower()
        if s in {"gate", "gating", "entry"}:
            return "gate"
        if s in {"sizing", "size", "risk"}:
            return "sizing"
        if s in {"both", "all", "gate+sizing", "gating+sizing"}:
            return "both"
        return "both"

    reasons: list[str] = []
    components_gate: dict[str, float] = {}
    components_size: dict[str, float] = {}
    component_scopes: dict[str, str] = {}

    q_gate = 1.0
    q_size = 1.0

    def _apply_component(name: str, factor: float, scope: str) -> None:
        nonlocal q_gate, q_size
        component_scopes[name] = scope
        if scope in {"both", "gate"}:
            components_gate[name] = float(factor)
            q_gate *= float(factor)
        if scope in {"both", "sizing"}:
            components_size[name] = float(factor)
            q_size *= float(factor)

    # data_quality in [0,1]
    dq_cfg = dict(components_cfg.get("data_quality") or {})
    if dq_cfg.get("enabled", True):
        scope = _norm_scope(dq_cfg.get("scope"))
        dq = _as_float(data_quality)
        if dq is None:
            factor = 1.0
            reasons.append("Q_DATA_QUALITY_MISSING")
        else:
            factor = _soft_floor(
                _clamp01(dq),
                floor=float(dq_cfg.get("floor", 0.50)),
                exponent=float(dq_cfg.get("exponent", 1.0)),
            )
        _apply_component("data_quality", float(factor), scope)

    # spread_bp in basis points
    spread_cfg = dict(components_cfg.get("spread") or {})
    if spread_cfg.get("enabled", True):
        scope = _norm_scope(spread_cfg.get("scope"))
        sp = _as_float(spread_bp)
        if sp is None:
            factor = 1.0
            reasons.append("Q_SPREAD_MISSING")
        else:
            sp = max(0.0, sp)
            factor = _linear_penalty(
                sp,
                ref=float(spread_cfg.get("ref_bp", 5.0)),
                max_x=float(spread_cfg.get("max_bp", 50.0)),
                floor=float(spread_cfg.get("floor", 0.25)),
            )
            exponent = float(spread_cfg.get("exponent", 1.0))
            exponent = 1.0 if exponent <= 0 else exponent
            factor = float(_clamp(factor, 0.0, 1.0) ** exponent)
        _apply_component("spread", float(factor), scope)

    # atr_pct in [0, inf)
    atr_cfg = dict(components_cfg.get("atr") or {})
    if atr_cfg.get("enabled", True):
        scope = _norm_scope(atr_cfg.get("scope"))
        ap = _as_float(atr_pct)
        if ap is None:
            factor = 1.0
            reasons.append("Q_ATR_PCT_MISSING")
        else:
            ap = max(0.0, ap)
            factor = _linear_penalty(
                ap,
                ref=float(atr_cfg.get("ref_pct", 0.008)),
                max_x=float(atr_cfg.get("max_pct", 0.04)),
                floor=float(atr_cfg.get("floor", 0.40)),
            )
            exponent = float(atr_cfg.get("exponent", 1.0))
            exponent = 1.0 if exponent <= 0 else exponent
            factor = float(_clamp(factor, 0.0, 1.0) ** exponent)
        _apply_component("atr", float(factor), scope)

    # volume_score in [0,1]
    vol_cfg = dict(components_cfg.get("volume") or {})
    if vol_cfg.get("enabled", True):
        scope = _norm_scope(vol_cfg.get("scope"))
        vs = _as_float(volume_score)
        if vs is None:
            factor = 1.0
            reasons.append("Q_VOLUME_MISSING")
        else:
            factor = _soft_floor(
                _clamp01(vs),
                floor=float(vol_cfg.get("floor", 0.40)),
                exponent=float(vol_cfg.get("exponent", 0.8)),
            )
        _apply_component("volume", float(factor), scope)

    q_gate = float(_clamp(q_gate, min_quality, 1.0))
    q_size = float(_clamp(q_size, min_quality, 1.0))
    return q_gate, {
        "version": "v2",
        "enabled": True,
        # Backward compatible: quality_factor == gating factor.
        "quality_factor": q_gate,
        "quality_factor_gate": q_gate,
        "quality_factor_size": q_size,
        "min_quality": min_quality,
        # Backward compatible: components == gate components.
        "components": components_gate,
        "components_size": components_size,
        "component_scopes": component_scopes,
        "reasons": reasons,
    }


def compute_confidence(
    probas: dict[str, float],
    *,
    atr_pct: float | None = None,
    spread_bp: float | None = None,
    volume_score: float | None = None,
    data_quality: float | None = None,
    config: dict[str, Any] | None = None,
) -> tuple[dict[str, float], dict[str, Any]]:
    """Beräkna konfidenser (pure) från sannolikheter och kvalitetsmått.

    - Monotoni: rangordning mellan p_long/p_short ska bevaras
    - Clamp till [0, 1]
    - Returnera (confidences, meta) där meta innehåller versions och reasons
    """
    p_buy = float(probas.get("buy", 0.0)) if probas else 0.0
    p_sell = float(probas.get("sell", 0.0)) if probas else 0.0

    quality, quality_meta = _compute_quality_factor(
        atr_pct=atr_pct,
        spread_bp=spread_bp,
        volume_score=volume_score,
        data_quality=data_quality,
        config=config,
    )

    quality_gate = float(quality)
    quality_size = float(
        quality_meta.get("quality_factor_size", quality_gate)
        if isinstance(quality_meta, dict)
        else quality_gate
    )

    # Bevara rangordning: multiplicera buy/sell med samma gate‑faktor.
    c_buy = _clamp01(p_buy * quality_gate)
    c_sell = _clamp01(p_sell * quality_gate)
    c_overall = max(c_buy, c_sell)

    confidences: dict[str, float] = {"buy": c_buy, "sell": c_sell, "overall": c_overall}

    # If sizing-quality differs from gate-quality (e.g. component scopes), expose scaled confidences.
    if abs(quality_size - quality_gate) > 1e-12:
        c_buy_s = _clamp01(p_buy * quality_size)
        c_sell_s = _clamp01(p_sell * quality_size)
        confidences["buy_scaled"] = c_buy_s
        confidences["sell_scaled"] = c_sell_s
        confidences["overall_scaled"] = max(c_buy_s, c_sell_s)
    meta: dict[str, Any] = {
        "versions": {"confidence": str(quality_meta.get("version", "v1"))},
        "reasons": list(quality_meta.get("reasons", [])) if isinstance(quality_meta, dict) else [],
        "quality": quality_meta,
    }
    return confidences, meta
