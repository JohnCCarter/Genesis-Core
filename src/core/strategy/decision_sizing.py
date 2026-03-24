from __future__ import annotations

from collections.abc import Callable
from typing import Any

from core.config.authority_mode_resolver import (
    resolve_authority_mode_with_source_permissive as _resolve_authority_mode_with_source,
)
from core.intelligence.regime.clarity import (
    compute_clarity_score_v1 as _compute_clarity_score_v1,
)
from core.intelligence.regime.risk_state import (
    compute_risk_state_multiplier as _compute_risk_state_multiplier,
)
from core.strategy.decision_gates import Action, safe_float


def _build_regime_transition_state(
    *,
    regime: str | None,
    state_in: dict[str, Any],
) -> dict[str, Any]:
    _last_regime = state_in.get("last_regime")
    _cur_regime = str(regime or "")
    if _last_regime is None or _last_regime == _cur_regime:
        _bars_since_change = int(state_in.get("bars_since_regime_change", 0))
    else:
        _bars_since_change = 0
    return {
        "last_regime": _cur_regime,
        "bars_since_regime_change": _bars_since_change + 1,
    }


def _build_sizing_state_updates(
    *,
    regime: str | None,
    state_in: dict[str, Any],
    conf_val_gate: float,
    size_base: float,
    size_scale: float,
    regime_mult: float,
    htf_regime_mult: float,
    vol_size_mult: float,
    combined_mult: float,
    ri_enabled: bool,
    ri_version: str,
    authority_mode: str,
    authority_mode_source: str,
    clarity_payload: dict[str, Any],
    risk_state_payload: dict[str, Any],
) -> dict[str, Any]:
    state_updates = {
        "confidence_gate": conf_val_gate,
        "size_base": size_base,
        "size_scale": size_scale,
        "size_regime_mult": regime_mult,
        "size_htf_regime_mult": htf_regime_mult,
        "size_vol_mult": vol_size_mult,
        "size_combined_mult": combined_mult,
        "ri_flag_enabled": ri_enabled,
        "ri_version": ri_version,
        "authority_mode": authority_mode,
        "authority_mode_source": authority_mode_source,
        "ri_clarity_enabled": bool(clarity_payload.get("enabled")),
        "ri_clarity_apply": clarity_payload.get("apply"),
        "ri_clarity_multiplier": clarity_payload.get("multiplier"),
        "ri_clarity_score": clarity_payload.get("score"),
        "ri_clarity_raw": clarity_payload.get("raw"),
        "ri_clarity_components": clarity_payload.get("components"),
        "ri_clarity_weights": clarity_payload.get("weights"),
        "ri_clarity_weights_version": clarity_payload.get("weights_version"),
        "ri_clarity_round_policy": clarity_payload.get("round_policy"),
        "size_before_ri_clarity": clarity_payload.get("size_before"),
        "size_after_ri_clarity": clarity_payload.get("size_after"),
        "ri_risk_state_enabled": bool(risk_state_payload.get("enabled")),
        "ri_risk_state_multiplier": risk_state_payload.get("multiplier"),
        "ri_risk_state_drawdown_mult": risk_state_payload.get("drawdown_mult"),
        "ri_risk_state_transition_mult": risk_state_payload.get("transition_mult"),
    }
    state_updates.update(_build_regime_transition_state(regime=regime, state_in=state_in))
    return state_updates


def _build_default_clarity_payload(
    *,
    clarity_enabled: bool,
    ri_version: str,
    clarity_multiplier: float,
    size_pre_clarity: float,
    size: float,
) -> dict[str, Any]:
    return {
        "enabled": clarity_enabled,
        "apply": "sizing_only",
        "version": ri_version,
        "score": None,
        "raw": None,
        "components": None,
        "weights": None,
        "weights_version": None,
        "round_policy": None,
        "multiplier": clarity_multiplier,
        "size_before": size_pre_clarity,
        "size_after": size,
    }


def _apply_clarity_sizing(
    *,
    conf_val_gate: float,
    p_buy: float,
    p_sell: float,
    max_ev: float,
    r_default: float,
    candidate: Action,
    regime: str | None,
    ri_version: str,
    clarity_cfg: dict[str, Any],
    ri_cfg: dict[str, Any],
    size: float,
    size_pre_clarity: float,
) -> tuple[float, dict[str, Any]]:
    _sm_cfg = dict(ri_cfg.get("size_multiplier") or {})
    min_mult = safe_float(_sm_cfg.get("min", 0.5), 0.5)
    max_mult = safe_float(_sm_cfg.get("max", 1.0), 1.0)
    if max_mult < min_mult:
        min_mult, max_mult = max_mult, min_mult
    min_mult = max(0.0, min(1.0, min_mult))
    max_mult = max(0.0, min(1.0, max_mult))

    clarity = _compute_clarity_score_v1(
        confidence_gate=conf_val_gate,
        edge=abs(p_buy - p_sell),
        max_ev=max_ev,
        r_default=r_default,
        candidate=candidate,
        regime=str(regime or "balanced"),
        weights=clarity_cfg.get("weights") or clarity_cfg.get("weights_v1"),
        weights_version=str(clarity_cfg.get("weights_version") or "weights_v1"),
    ).to_legacy_payload()
    clarity_score = int(clarity["clarity_score"])
    clarity_multiplier = min_mult + ((max_mult - min_mult) * (clarity_score / 100.0))
    clarity_multiplier = max(0.0, min(1.0, clarity_multiplier))
    size = float(size * clarity_multiplier)

    clarity_payload = {
        "enabled": True,
        "apply": "sizing_only",
        "version": ri_version,
        "score": clarity_score,
        "raw": float(clarity["clarity_raw"]),
        "components": dict(clarity["components"]),
        "weights": dict(clarity["weights"]),
        "weights_version": str(clarity["weights_version"]),
        "round_policy": str(clarity["round_policy"]),
        "multiplier": clarity_multiplier,
        "size_before": size_pre_clarity,
        "size_after": size,
        "multiplier_min": min_mult,
        "multiplier_max": max_mult,
    }
    return size, clarity_payload


def apply_sizing(
    *,
    candidate: Action,
    confidence: dict[str, float],
    regime: str | None,
    htf_regime: str | None,
    state_in: dict[str, Any],
    state_out: dict[str, Any],
    cfg: dict[str, Any],
    p_buy: float,
    p_sell: float,
    r_default: float,
    max_ev: float,
    logger: Any,
    sanitize_context: Callable[[Any], Any],
) -> tuple[float, float]:
    ri_cfg = dict((cfg.get("multi_timeframe") or {}).get("regime_intelligence") or {})
    clarity_cfg = dict(ri_cfg.get("clarity_score") or {})
    ri_enabled = bool(ri_cfg.get("enabled", False))
    ri_version = str(ri_cfg.get("version") or "legacy")
    clarity_enabled = (
        ri_enabled and ri_version.lower() == "v2" and bool(clarity_cfg.get("enabled", False))
    )
    authority_mode, authority_mode_source = _resolve_authority_mode_with_source(cfg)

    risk_map = (cfg.get("risk") or {}).get("risk_map", [])
    c_buy = safe_float(confidence.get("buy", 0.0), 0.0)
    c_sell = safe_float(confidence.get("sell", 0.0), 0.0)
    conf_val_gate = c_buy if candidate == "LONG" else c_sell

    size_base = 0.0
    try:
        for thr_v, sz in sorted(risk_map, key=lambda item: float(item[0])):
            if conf_val_gate >= float(thr_v):
                size_base = float(sz)
    except Exception as exc:
        logger.exception(
            "[DECISION] SIZING_RISK_MAP_ERROR candidate=%s confidence=%.6f risk_map=%s",
            candidate,
            conf_val_gate,
            sanitize_context(risk_map),
        )
        raise RuntimeError("Failed to compute size_base from risk_map") from exc

    size_scale = 1.0
    try:
        if conf_val_gate > 0.0:
            if candidate == "LONG" and "buy_scaled" in confidence:
                c_scaled = safe_float(confidence.get("buy_scaled") or conf_val_gate, conf_val_gate)
                size_scale = c_scaled / conf_val_gate
            elif candidate == "SHORT" and "sell_scaled" in confidence:
                c_scaled = safe_float(
                    confidence.get("sell_scaled") or conf_val_gate,
                    conf_val_gate,
                )
                size_scale = c_scaled / conf_val_gate
    except Exception:
        size_scale = 1.0
    size_scale = max(0.0, min(1.0, size_scale))

    regime_mult = 1.0
    try:
        rm = (cfg.get("risk") or {}).get("regime_size_multipliers") or {}
        if isinstance(rm, dict):
            regime_key = str(regime or "").strip()
            regime_mult = float(
                rm.get(regime_key)
                if regime_key in rm
                else (
                    rm.get(regime_key.lower())
                    if regime_key.lower() in rm
                    else rm.get(regime_key.upper()) if regime_key.upper() in rm else 1.0
                )
            )
    except Exception:
        regime_mult = 1.0
    regime_mult = max(0.0, min(1.0, regime_mult))

    htf_regime_mult = 1.0
    try:
        hrm = (cfg.get("risk") or {}).get("htf_regime_size_multipliers") or {}
        if isinstance(hrm, dict) and htf_regime:
            htf_key = str(htf_regime).strip().lower()
            htf_regime_mult = float(hrm.get(htf_key, 1.0))
    except Exception:
        htf_regime_mult = 1.0
    htf_regime_mult = max(0.0, min(1.0, htf_regime_mult))

    vol_size_mult = 1.0
    try:
        vol_cfg = (cfg.get("risk") or {}).get("volatility_sizing") or {}
        if vol_cfg.get("enabled"):
            threshold = float(vol_cfg.get("high_vol_threshold", 80))
            multiplier = float(vol_cfg.get("high_vol_multiplier", 0.7))
            atr_period = str(vol_cfg.get("atr_period", 14))
            atr_pct = state_in.get("atr_percentiles", {})
            current_p = atr_pct.get(atr_period, {})
            current_atr = state_in.get("current_atr")
            p_threshold = current_p.get("p80") if threshold >= 80 else current_p.get("p40")
            if current_atr is not None and p_threshold is not None and current_atr > p_threshold:
                vol_size_mult = multiplier
    except Exception:
        vol_size_mult = 1.0
    vol_size_mult = max(0.0, min(1.0, vol_size_mult))

    risk_state_mult = 1.0
    risk_state_payload: dict[str, Any] = {"enabled": False, "multiplier": 1.0}
    risk_state_cfg = dict(ri_cfg.get("risk_state") or {})
    if ri_enabled and bool(risk_state_cfg.get("enabled", False)):
        _eq_dd = float(state_in.get("equity_drawdown_pct", 0.0))
        _bars_rc = int(state_in.get("bars_since_regime_change", 99))
        risk_state_payload = _compute_risk_state_multiplier(
            cfg=risk_state_cfg,
            equity_drawdown_pct=_eq_dd,
            bars_since_regime_change=_bars_rc,
        )
        risk_state_mult = float(risk_state_payload.get("multiplier", 1.0))
    risk_state_mult = max(0.0, min(1.0, risk_state_mult))

    min_size_mult = float((cfg.get("risk") or {}).get("min_combined_multiplier", 0.1))
    combined_mult = size_scale * regime_mult * htf_regime_mult * vol_size_mult * risk_state_mult
    combined_mult = max(min_size_mult, combined_mult)
    size = float(size_base * combined_mult)
    size_pre_clarity = size

    clarity_multiplier = 1.0
    clarity_payload = _build_default_clarity_payload(
        clarity_enabled=clarity_enabled,
        ri_version=ri_version,
        clarity_multiplier=clarity_multiplier,
        size_pre_clarity=size_pre_clarity,
        size=size,
    )
    if clarity_enabled:
        size, clarity_payload = _apply_clarity_sizing(
            conf_val_gate=conf_val_gate,
            p_buy=p_buy,
            p_sell=p_sell,
            max_ev=max_ev,
            r_default=r_default,
            candidate=candidate,
            regime=regime,
            ri_version=ri_version,
            clarity_cfg=clarity_cfg,
            ri_cfg=ri_cfg,
            size=size,
            size_pre_clarity=size_pre_clarity,
        )

    state_out.update(
        _build_sizing_state_updates(
            regime=regime,
            state_in=state_in,
            conf_val_gate=conf_val_gate,
            size_base=size_base,
            size_scale=size_scale,
            regime_mult=regime_mult,
            htf_regime_mult=htf_regime_mult,
            vol_size_mult=vol_size_mult,
            combined_mult=combined_mult,
            ri_enabled=ri_enabled,
            ri_version=ri_version,
            authority_mode=authority_mode,
            authority_mode_source=authority_mode_source,
            clarity_payload=clarity_payload,
            risk_state_payload=risk_state_payload,
        )
    )

    return size, conf_val_gate
