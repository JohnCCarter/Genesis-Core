from __future__ import annotations

import logging
import math
from typing import Any, Literal

from core.strategy.fib_logging import log_fib_flow
from core.utils.logging_redaction import get_logger

Action = Literal["LONG", "SHORT", "NONE"]

_LOG = get_logger(__name__)


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float, handling None and invalid types.

    Args:
        value: Value to convert (can be None, str, int, float, etc.)
        default: Default value if conversion fails

    Returns:
        Float value or default

    Note:
        Created to fix critical bug where float(None) caused TypeError,
        blocking all trades. See docs/bugs/FLOAT_NONE_BUG_20251120.md
    """
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _sanitize_context(value: Any) -> Any:
    if isinstance(value, str | int | float | bool) or value is None:
        return value
    if isinstance(value, list | tuple):
        return [_sanitize_context(v) for v in value[:5]]
    if isinstance(value, dict):
        return {str(k): _sanitize_context(v) for k, v in list(value.items())[:8]}
    return str(value)


def _log_decision_event(event: str, **context: Any) -> None:
    # Optimization: Only sanitize and log if DEBUG is enabled
    # This prevents massive IO overhead during backtesting/optimization
    if not _LOG.isEnabledFor(logging.DEBUG):
        return

    try:
        payload = {k: _sanitize_context(v) for k, v in context.items()}
        _LOG.debug("[DECISION] %s %s", event, payload)
    except Exception:  # pragma: no cover
        _LOG.debug("[DECISION] %s", event)


def _summarize_fib_debug(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {"status": "missing"}
    summary = {
        "reason": data.get("reason"),
        "tolerance": data.get("tolerance"),
        "level_price": data.get("level_price"),
        "config": data.get("config"),
    }
    override = data.get("override")
    if isinstance(override, dict):
        summary["override"] = {
            "source": override.get("source"),
            "confidence": override.get("confidence"),
            "threshold": override.get("threshold"),
        }
    targets = data.get("targets")
    if isinstance(targets, list):
        summary["targets"] = targets
    return summary


def _compute_percentile(values: list[float], q: float) -> float:
    if not values:
        raise ValueError("values in percentile computation must not be empty")
    if q <= 0:
        return min(values)
    if q >= 1:
        return max(values)
    sorted_vals = sorted(values)
    k = (len(sorted_vals) - 1) * q
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return float(sorted_vals[int(k)])
    d0 = sorted_vals[f] * (c - k)
    d1 = sorted_vals[c] * (k - f)
    return float(d0 + d1)


def _as_float(value: Any) -> float | None:
    """Best‑effort conversion; returns None if not convertible."""
    try:
        return float(value)  # type: ignore[arg-type]
    except Exception:
        return None


def decide(
    policy: dict[str, Any],
    *,
    probas: dict[str, float] | None,
    confidence: dict[str, float] | None,
    regime: str | None,
    state: dict[str, Any] | None,
    risk_ctx: dict[str, Any] | None,
    cfg: dict[str, Any] | None,
) -> tuple[Action, dict[str, Any]]:
    """Beslutsfunktion (pure) med strikt gate‑ordning.

    Ordning:
    1) Fail‑safe & EV‑filter
    2) Event
    3) Risk caps
    4) Regim‑riktning
    5) Proba‑tröskel
    6) Tie‑break
    7) Confidence‑gate
    8) Hysteresis
    9) Cooldown
    10) Sizing
    """
    log_fib_flow(
        "[FIB-FLOW] decide() called with cfg keys: %s",
        list((cfg or {}).keys())[:15],
        logger=_LOG,
    )

    reasons: list[str] = []
    versions: dict[str, Any] = {"decision": "v1"}
    cfg = dict(cfg or {})
    mtf_cfg = dict(cfg.get("multi_timeframe") or {})
    policy_symbol = str(policy.get("symbol") or "UNKNOWN")
    policy_timeframe = str(policy.get("timeframe") or "UNKNOWN")
    use_htf_block = bool(mtf_cfg.get("use_htf_block", True))
    allow_ltf_override_cfg = bool(mtf_cfg.get("allow_ltf_override"))
    ltf_override_threshold = float(mtf_cfg.get("ltf_override_threshold", 0.85))
    adaptive_cfg = dict(mtf_cfg.get("ltf_override_adaptive") or {})
    state_in = dict(state or {})
    state_out: dict[str, Any] = dict(state_in)
    override_state_in = state_in.get("ltf_override_state")
    override_state: dict[str, Any] = {}
    if isinstance(override_state_in, dict):
        for key, value in override_state_in.items():
            if isinstance(value, list):
                override_state[key] = list(value)
            else:
                override_state[key] = value
    state_out["ltf_override_state"] = override_state
    override_context_ref: dict[str, Any | None] = {"data": None}

    # 1) Fail‑safe & EV‑filter
    if not probas or not isinstance(probas, dict):
        reasons.append("FAIL_SAFE_NULL")
        _log_decision_event("FAIL_SAFE_NO_PROBAS", probas=probas)
        return "NONE", {
            "versions": versions,
            "reasons": reasons,
            "state_out": state_out,
        }
    p_buy = float(probas.get("buy", 0.0))
    p_sell = float(probas.get("sell", 0.0))
    R = float((cfg.get("ev") or {}).get("R_default") or 1.0)

    # EV check: Must have positive EV for EITHER long or short
    # (Don't block shorts just because long EV is negative!)
    ev_long = p_buy * R - p_sell
    ev_short = p_sell * R - p_buy
    max_ev = max(ev_long, ev_short)

    if max_ev <= 0.0:
        reasons.append("EV_NEG")
        _log_decision_event(
            "EV_NEGATIVE",
            p_buy=p_buy,
            p_sell=p_sell,
            ev_long=ev_long,
            ev_short=ev_short,
            R=R,
        )
        return "NONE", {
            "versions": versions,
            "reasons": reasons,
            "state_out": state_out,
        }

    # 2) Event gate
    if (risk_ctx or {}).get("event_block"):
        reasons.append("R_EVENT_BLOCK")
        return "NONE", {
            "versions": versions,
            "reasons": reasons,
            "state_out": state_out,
        }

    # 3) Risk caps
    if (risk_ctx or {}).get("risk_cap_breached"):
        reasons.append("RISK_CAP")
        return "NONE", {
            "versions": versions,
            "reasons": reasons,
            "state_out": state_out,
        }

    # 4) Regim‑riktning
    # Om policy indikerar ensidig riktning under trend, respektera det.
    regime_str = str(regime or "balanced")
    long_allowed = True
    short_allowed = True
    if regime_str == "trend":
        if policy.get("trend_long_only"):
            short_allowed = False
        if policy.get("trend_short_only"):
            long_allowed = False

    # 5) Proba‑tröskel (regim‑specifik)
    thresholds_cfg = cfg.get("thresholds") or {}

    # Determine ATR-adapted thresholds if available
    adaptation_cfg = thresholds_cfg.get("signal_adaptation") or {}
    default_thr = float(thresholds_cfg.get("entry_conf_overall", 0.7))

    atr = state_in.get("current_atr") if adaptation_cfg else None
    atr_percentiles = state_in.get("atr_percentiles") if adaptation_cfg else None

    zone_name = None
    zone_debug: dict[str, Any] = {}
    if adaptation_cfg and atr_percentiles:
        zones = adaptation_cfg.get("zones", {})
        atr_period = int(adaptation_cfg.get("atr_period", 14))
        # Zone determination: use percentiles thresholds stored in state
        if atr is not None:
            atr_p = atr_percentiles.get(str(atr_period)) or atr_percentiles.get(atr_period) or {}
            p40 = float(atr_p.get("p40", atr))
            p80 = float(atr_p.get("p80", atr))
            if atr <= p40:
                zone_name = "low"
            elif atr <= p80:
                zone_name = "mid"
            else:
                zone_name = "high"

        zone_cfg = zones.get(zone_name or "") or {}
        zone_entry = zone_cfg.get("entry_conf_overall")
        if zone_entry is not None:
            default_thr = float(zone_entry)
        zone_regime = zone_cfg.get("regime_proba") or {}

        zone_meta = atr_percentiles.get(str(atr_period)) or atr_percentiles.get(atr_period) or {}
        zone_debug = {
            "atr": atr,
            "zone": zone_name or "base",
            "thr": default_thr,
            "p40": zone_meta.get("p40"),
            "p80": zone_meta.get("p80"),
            "period": atr_period,
        }
    else:
        zone_regime = {}
        zone_debug = {
            "atr": atr,
            "zone": zone_name or "base",
            "thr": default_thr,
        }

    zone_label = f"ZONE:{zone_name or 'base'}@{default_thr:.3f}"
    reasons.append(zone_label)

    thresholds = zone_regime or thresholds_cfg.get("regime_proba", {})
    thr = float(thresholds.get(regime_str, default_thr))

    buy_pass = p_buy >= thr and long_allowed
    sell_pass = p_sell >= thr and short_allowed
    if not buy_pass and not sell_pass:
        _log_decision_event(
            "PROBA_THRESHOLD_FAIL",
            buy_pass=buy_pass,
            sell_pass=sell_pass,
            threshold=thr,
            regime=regime_str,
            p_buy=p_buy,
            p_sell=p_sell,
        )
        return "NONE", {
            "versions": versions,
            "reasons": reasons,
            "state_out": state_out,
        }

    # 6) Tie‑break (högst sannolikhet vinner; lika ⇒ föregående riktning om finns)
    candidate: Action
    if buy_pass and not sell_pass:
        candidate = "LONG"
    elif sell_pass and not buy_pass:
        candidate = "SHORT"
    else:
        if abs(p_buy - p_sell) < 1e-12:
            last_action = state_in.get("last_action")
            if last_action in ("LONG", "SHORT"):
                candidate = last_action  # type: ignore[assignment]
            else:
                # Regime-based fallback to avoid permanent no-trade degeneracy when model defaults to 0.5/0.5
                if regime_str in ("bull", "trend"):
                    candidate = "LONG"
                elif regime_str == "bear":
                    candidate = "SHORT"
                else:
                    reasons.append("P_TIE_BREAK")
                    _log_decision_event(
                        "P_TIE_BREAK",
                        p_buy=p_buy,
                        p_sell=p_sell,
                        regime=regime_str,
                    )
                    return "NONE", {
                        "versions": versions,
                        "reasons": reasons,
                        "state_out": state_out,
                    }
        else:
            candidate = "LONG" if p_buy > p_sell else "SHORT"

    _log_decision_event(
        "CANDIDATE_SELECTED",
        candidate=candidate,
        buy_pass=buy_pass,
        sell_pass=sell_pass,
        p_buy=p_buy,
        p_sell=p_sell,
        zone=zone_label,
    )

    # Helper utilities for Fibonacci-based gating
    def _levels_to_lookup(levels_dict: Any | None) -> dict[float, float]:
        if not isinstance(levels_dict, dict):
            return {}
        lookup: dict[float, float] = {}
        for key, value in levels_dict.items():
            try:
                lookup[float(key)] = float(value)
            except (TypeError, ValueError):
                continue
        return lookup

    def _level_price(levels: dict[float, float], target: float | None) -> float | None:
        if target is None or not levels:
            return None
        if target in levels:
            return levels[target]
        nearest = min(levels.keys(), key=lambda k: abs(k - target))
        if abs(nearest - target) <= 1e-6:
            return levels[nearest]
        return None

    ltf_entry_cfg = (cfg.get("ltf_fib") or {}).get("entry") or {}

    def _prepare_override_context() -> dict[str, Any]:
        if not ltf_entry_cfg.get("enabled"):
            return {}
        if not confidence or not isinstance(confidence, dict):
            return {}
        conf_key = "buy" if candidate == "LONG" else "sell"
        conf_val = float(confidence.get(conf_key, 0.0))
        history_window = max(1, int(adaptive_cfg.get("window", 120)))
        history_key = f"{conf_key.lower()}_history"
        history = list(override_state.get(history_key) or [])
        history.append(conf_val)
        if len(history) > history_window:
            history = history[-history_window:]
        override_state[history_key] = history

        effective_threshold = ltf_override_threshold
        adaptive_debug: dict[str, Any] | None = None
        if allow_ltf_override_cfg and adaptive_cfg.get("enabled"):
            min_history = max(1, int(adaptive_cfg.get("min_history", min(history_window, 30))))
            percentile_q = float(adaptive_cfg.get("percentile", 0.85))
            percentile_q = max(0.0, min(1.0, percentile_q))
            raw_threshold = (
                _compute_percentile(history, percentile_q) if len(history) >= min_history else None
            )
            fallback = adaptive_cfg.get("fallback_threshold")
            base_threshold = float(
                raw_threshold
                if raw_threshold is not None
                else (fallback if fallback is not None else ltf_override_threshold)
            )
            multiplier = float((adaptive_cfg.get("regime_multipliers") or {}).get(regime_str, 1.0))
            effective_threshold = base_threshold * multiplier
            min_floor = adaptive_cfg.get("min_floor")
            max_ceiling = adaptive_cfg.get("max_ceiling")
            if min_floor is not None:
                effective_threshold = max(effective_threshold, float(min_floor))
            if max_ceiling is not None:
                effective_threshold = min(effective_threshold, float(max_ceiling))
            effective_threshold = min(max(effective_threshold, 0.0), 1.0)
            adaptive_debug = {
                "window": history_window,
                "history_len": len(history),
                "min_history": min_history,
                "percentile": percentile_q,
                "raw_threshold": raw_threshold,
                "fallback": float(fallback if fallback is not None else ltf_override_threshold),
                "multiplier": multiplier,
                "min_floor": min_floor,
                "max_ceiling": max_ceiling,
                "effective_threshold": effective_threshold,
            }
        else:
            effective_threshold = min(max(effective_threshold, 0.0), 1.0)

        return {
            "conf_key": conf_key,
            "conf_val": conf_val,
            "history_key": history_key,
            "history_window": history_window,
            "history_len": len(history),
            "effective_threshold": effective_threshold,
            "adaptive_debug": adaptive_debug,
        }

    def _try_override_htf_block(payload: dict[str, Any]) -> bool:
        if not ltf_entry_cfg.get("enabled"):
            return False
        if not confidence or not isinstance(confidence, dict):
            return False

        context = override_context_ref.get("data")
        if not isinstance(context, dict):
            return False

        conf_val = float(context.get("conf_val", 0.0))
        reason_label = str(payload.get("reason", "HTF_BLOCK"))

        def _apply_override(source: str, extra: dict[str, Any]) -> bool:
            payload_override = dict(payload)
            payload_override["override"] = {
                "source": source,
                "confidence": conf_val,
                **extra,
            }
            payload_override["reason"] = f"{reason_label}_OVERRIDE"
            state_out["htf_fib_entry_debug"] = payload_override
            reasons.append("HTF_OVERRIDE_LTF_CONF")
            _LOG.info(
                "[OVERRIDE] LTF override triggered source=%s symbol=%s timeframe=%s direction=%s confidence=%.3f details=%s",
                source,
                policy_symbol,
                policy_timeframe,
                candidate,
                conf_val,
                extra,
            )
            return True

        effective_threshold = float(context.get("effective_threshold", ltf_override_threshold))
        adaptive_debug = context.get("adaptive_debug")

        if allow_ltf_override_cfg and conf_val >= effective_threshold:
            return _apply_override(
                "multi_timeframe_threshold",
                {
                    "threshold": effective_threshold,
                    "baseline": ltf_override_threshold,
                    "adaptive": adaptive_debug,
                },
            )

        override_cfg = ltf_entry_cfg.get("override_confidence") or {}
        if override_cfg.get("enabled"):
            min_conf = float(override_cfg.get("min", 0.0))
            max_conf = float(override_cfg.get("max", 1.0))
            if min_conf <= conf_val <= max_conf:
                return _apply_override(
                    "ltf_entry_range",
                    {"min": min_conf, "max": max_conf},
                )
        return False

    override_context = _prepare_override_context()
    override_context_ref["data"] = override_context if override_context else {}
    if override_context:
        state_out["ltf_override_debug"] = {
            "candidate": candidate,
            "confidence": override_context["conf_val"],
            "history_key": override_context["history_key"],
            "history_len": override_context["history_len"],
            "history_window": override_context["history_window"],
            "baseline_threshold": ltf_override_threshold,
            "effective_threshold": override_context["effective_threshold"],
            "adaptive_enabled": bool(adaptive_cfg.get("enabled")),
            "regime": regime_str,
            "details": override_context.get("adaptive_debug"),
        }
    else:
        fallback_conf = None
        if confidence and isinstance(confidence, dict):
            fallback_conf = float(confidence.get("buy" if candidate == "LONG" else "sell", 0.0))
        state_out["ltf_override_debug"] = {
            "candidate": candidate,
            "confidence": fallback_conf,
            "history_key": None,
            "history_len": 0,
            "history_window": int(adaptive_cfg.get("window", 120)),
            "baseline_threshold": ltf_override_threshold,
            "effective_threshold": ltf_override_threshold,
            "adaptive_enabled": bool(adaptive_cfg.get("enabled")),
            "regime": regime_str,
            "details": None,
        }

    # HTF Fibonacci confirmation (trend filter)
    htf_entry_cfg = (cfg.get("htf_fib") or {}).get("entry") or {}
    log_fib_flow(
        "[FIB-FLOW] HTF gate check: use_htf_block=%s htf_entry_enabled=%s",
        use_htf_block,
        htf_entry_cfg.get("enabled"),
        logger=_LOG,
    )
    if use_htf_block and htf_entry_cfg.get("enabled"):
        htf_ctx = state_in.get("htf_fib") or {}
        log_fib_flow(
            "[FIB-FLOW] HTF gate active: symbol=%s timeframe=%s enabled=%s htf_ctx_keys=%s available=%s",
            policy_symbol,
            policy_timeframe,
            htf_entry_cfg.get("enabled"),
            list(htf_ctx.keys()) if isinstance(htf_ctx, dict) else [],
            htf_ctx.get("available") if isinstance(htf_ctx, dict) else None,
            logger=_LOG,
        )
        price_now = state_in.get("last_close")
        atr_now = float(state_in.get("current_atr") or 0.0)
        tolerance = float(htf_entry_cfg.get("tolerance_atr", 0.5)) * atr_now if atr_now > 0 else 0.0

        missing_allowed = False
        if not htf_ctx.get("available"):
            missing_policy = str(htf_entry_cfg.get("missing_policy", "block")).lower()
            state_out["htf_fib_entry_debug"] = {
                "reason": "UNAVAILABLE",
                "raw": htf_ctx,
                "policy": missing_policy,
            }
            if missing_policy != "pass":
                reasons.append("HTF_FIB_UNAVAILABLE")
                _log_decision_event(
                    "HTF_FIB_BLOCK",
                    reason="UNAVAILABLE",
                    policy=missing_policy,
                    candidate=candidate,
                )
                return "NONE", {
                    "versions": versions,
                    "reasons": reasons,
                    "state_out": state_out,
                }
            missing_allowed = True
            state_out["htf_fib_entry_debug"]["reason"] = "UNAVAILABLE_PASS"

        if price_now is None:
            state_out["htf_fib_entry_debug"] = {
                "reason": "NO_PRICE",
                "raw": htf_ctx,
            }
            reasons.append("HTF_FIB_NO_PRICE")
            _log_decision_event("HTF_FIB_BLOCK", reason="NO_PRICE", candidate=candidate)
            return "NONE", {
                "versions": versions,
                "reasons": reasons,
                "state_out": state_out,
            }

        htf_levels = _levels_to_lookup(htf_ctx.get("levels"))
        base_debug = {
            "price": price_now,
            "atr": atr_now,
            "tolerance": tolerance,
            "levels": {str(k): htf_levels[k] for k in htf_levels},
            "config": {
                "long_min_level": htf_entry_cfg.get("long_min_level"),
                "short_max_level": htf_entry_cfg.get("short_max_level"),
                "long_target_levels": htf_entry_cfg.get("long_target_levels"),
                "short_target_levels": htf_entry_cfg.get("short_target_levels"),
            },
            "targets": [],
        }

        if not missing_allowed:
            if candidate == "LONG":
                target_levels = htf_entry_cfg.get("long_target_levels")
                matched = False
                target_debug: list[dict[str, float]] = []
                if isinstance(target_levels, list | tuple):
                    for lvl in target_levels:
                        try:
                            target = float(lvl)
                        except (TypeError, ValueError):
                            continue
                        lvl_price = _level_price(htf_levels, target)
                        if lvl_price is None:
                            continue
                        distance = abs(price_now - lvl_price)
                        target_debug.append(
                            {
                                "level": target,
                                "level_price": lvl_price,
                                "distance": distance,
                            }
                        )
                        if distance <= tolerance:
                            matched = True
                            break
                    base_debug["targets"] = target_debug
                if matched:
                    state_out["htf_fib_entry_debug"] = {**base_debug, "reason": "TARGET_MATCH"}
                else:
                    min_level = htf_entry_cfg.get("long_min_level")
                    level_price = _level_price(
                        htf_levels, float(min_level) if min_level is not None else None
                    )
                    p_val = _as_float(price_now)
                    lp_val = _as_float(level_price) if level_price is not None else None
                    tol_val = _as_float(tolerance)
                    if (
                        lp_val is not None
                        and p_val is not None
                        and tol_val is not None
                        and p_val < (lp_val - tol_val)
                    ):
                        payload = {
                            **base_debug,
                            "reason": "LONG_BELOW_LEVEL",
                            "level_price": lp_val,
                        }
                        if not _try_override_htf_block(payload):
                            state_out["htf_fib_entry_debug"] = payload
                            reasons.append("HTF_FIB_LONG_BLOCK")
                            _log_decision_event(
                                "HTF_FIB_BLOCK",
                                reason=payload.get("reason"),
                                price=payload.get("price"),
                                tolerance=payload.get("tolerance"),
                            )
                            return "NONE", {
                                "versions": versions,
                                "reasons": reasons,
                                "state_out": state_out,
                            }
                    elif target_debug and not matched:
                        payload = {
                            **base_debug,
                            "reason": "LONG_OFF_TARGET",
                        }
                        if not _try_override_htf_block(payload):
                            state_out["htf_fib_entry_debug"] = payload
                            reasons.append("HTF_FIB_LONG_BLOCK")
                            _log_decision_event(
                                "HTF_FIB_BLOCK",
                                reason=payload.get("reason"),
                                targets=payload.get("targets"),
                            )
                            return "NONE", {
                                "versions": versions,
                                "reasons": reasons,
                                "state_out": state_out,
                            }
            elif candidate == "SHORT":
                target_levels = htf_entry_cfg.get("short_target_levels")
                matched = False
                target_debug = []
                if isinstance(target_levels, list | tuple):
                    for lvl in target_levels:
                        try:
                            target = float(lvl)
                        except (TypeError, ValueError):
                            continue
                        lvl_price = _level_price(htf_levels, target)
                        if lvl_price is None:
                            continue
                        distance = abs(price_now - lvl_price)
                        target_debug.append(
                            {
                                "level": target,
                                "level_price": lvl_price,
                                "distance": distance,
                            }
                        )
                        if distance <= tolerance:
                            matched = True
                            break
                    base_debug["targets"] = target_debug
                if matched:
                    state_out["htf_fib_entry_debug"] = {**base_debug, "reason": "TARGET_MATCH"}
                else:
                    max_level = htf_entry_cfg.get("short_max_level")
                    level_price = _level_price(
                        htf_levels, float(max_level) if max_level is not None else None
                    )
                    p_val = _as_float(price_now)
                    lp_val = _as_float(level_price) if level_price is not None else None
                    tol_val = _as_float(tolerance)
                    if (
                        lp_val is not None
                        and p_val is not None
                        and tol_val is not None
                        and p_val > (lp_val + tol_val)
                    ):
                        payload = {
                            **base_debug,
                            "reason": "SHORT_ABOVE_LEVEL",
                            "level_price": lp_val,
                        }
                        if not _try_override_htf_block(payload):
                            state_out["htf_fib_entry_debug"] = payload
                            reasons.append("HTF_FIB_SHORT_BLOCK")
                            _log_decision_event(
                                "HTF_FIB_BLOCK",
                                reason=payload.get("reason"),
                                price=payload.get("price"),
                                tolerance=payload.get("tolerance"),
                            )
                            return "NONE", {
                                "versions": versions,
                                "reasons": reasons,
                                "state_out": state_out,
                            }
                    elif target_debug and not matched:
                        payload = {
                            **base_debug,
                            "reason": "SHORT_OFF_TARGET",
                        }
                        if not _try_override_htf_block(payload):
                            state_out["htf_fib_entry_debug"] = payload
                            reasons.append("HTF_FIB_SHORT_BLOCK")
                            _log_decision_event(
                                "HTF_FIB_BLOCK",
                                reason=payload.get("reason"),
                                targets=payload.get("targets"),
                            )
                            return "NONE", {
                                "versions": versions,
                                "reasons": reasons,
                                "state_out": state_out,
                            }

        if "htf_fib_entry_debug" not in state_out:
            state_out["htf_fib_entry_debug"] = {
                **base_debug,
                "reason": "PASS",
            }
    elif not use_htf_block:
        state_out.setdefault(
            "htf_fib_entry_debug",
            {
                "reason": "DISABLED_BY_CONFIG",
                "config": {"use_htf_block": use_htf_block},
            },
        )

    # LTF Fibonacci entry gating (same-timeframe fib context)
    if ltf_entry_cfg.get("enabled"):
        ltf_ctx = state_in.get("ltf_fib") or {}
        log_fib_flow(
            "[FIB-FLOW] LTF gate active: symbol=%s timeframe=%s enabled=%s ltf_ctx_keys=%s available=%s",
            policy_symbol,
            policy_timeframe,
            ltf_entry_cfg.get("enabled"),
            list(ltf_ctx.keys()) if isinstance(ltf_ctx, dict) else [],
            ltf_ctx.get("available") if isinstance(ltf_ctx, dict) else None,
            logger=_LOG,
        )
        price_now = state_in.get("last_close")
        atr_now = float(state_in.get("current_atr") or 0.0)
        tol_atr = float(ltf_entry_cfg.get("tolerance_atr", 0.5))
        tolerance = tol_atr * atr_now if atr_now > 0 else 0.0

        missing_allowed_ltf = False
        if not ltf_ctx.get("available"):
            missing_policy = str(ltf_entry_cfg.get("missing_policy", "block")).lower()
            state_out["ltf_fib_entry_debug"] = {
                "reason": "UNAVAILABLE",
                "raw": ltf_ctx,
                "policy": missing_policy,
            }
            if missing_policy != "pass":
                reasons.append("LTF_FIB_UNAVAILABLE")
                _log_decision_event(
                    "LTF_FIB_BLOCK",
                    reason="UNAVAILABLE",
                    policy=missing_policy,
                    candidate=candidate,
                )
                return "NONE", {
                    "versions": versions,
                    "reasons": reasons,
                    "state_out": state_out,
                }
            missing_allowed_ltf = True
            state_out["ltf_fib_entry_debug"]["reason"] = "UNAVAILABLE_PASS"
        levels = _levels_to_lookup(ltf_ctx.get("levels"))

        if price_now is None:
            state_out["ltf_fib_entry_debug"] = {
                "reason": "NO_PRICE",
                "raw": ltf_ctx,
            }
            reasons.append("LTF_FIB_NO_PRICE")
            _log_decision_event("LTF_FIB_BLOCK", reason="NO_PRICE", candidate=candidate)
            return "NONE", {
                "versions": versions,
                "reasons": reasons,
                "state_out": state_out,
            }

        ltf_base_debug = {
            "price": price_now,
            "atr": atr_now,
            "tolerance": tolerance,
            "levels": {str(k): levels[k] for k in levels},
            "config": {
                "long_max_level": ltf_entry_cfg.get("long_max_level"),
                "short_min_level": ltf_entry_cfg.get("short_min_level"),
            },
        }

        if not missing_allowed_ltf:
            if candidate == "LONG":
                max_level = ltf_entry_cfg.get("long_max_level")

                level_price = _level_price(
                    levels, float(max_level) if max_level is not None else None
                )
                p_val = _as_float(price_now)
                lp_val = _as_float(level_price) if level_price is not None else None
                tol_val = _as_float(tolerance)
                if (
                    lp_val is not None
                    and p_val is not None
                    and tol_val is not None
                    and p_val > (lp_val + tol_val)
                ):
                    state_out["ltf_fib_entry_debug"] = {
                        **ltf_base_debug,
                        "reason": "LONG_ABOVE_LEVEL",
                        "level_price": lp_val,
                    }
                    reasons.append("LTF_FIB_LONG_BLOCK")
                    _log_decision_event(
                        "LTF_FIB_BLOCK",
                        reason="LONG_ABOVE_LEVEL",
                        price=p_val,
                        level=lp_val,
                        tolerance=tol_val,
                    )
                    return "NONE", {
                        "versions": versions,
                        "reasons": reasons,
                        "state_out": state_out,
                    }
            elif candidate == "SHORT":
                min_level = ltf_entry_cfg.get("short_min_level")
                level_price = _level_price(
                    levels, float(min_level) if min_level is not None else None
                )
                p_val = _as_float(price_now)
                lp_val = _as_float(level_price) if level_price is not None else None
                tol_val = _as_float(tolerance)
                if (
                    lp_val is not None
                    and p_val is not None
                    and tol_val is not None
                    and p_val < (lp_val - tol_val)
                ):
                    state_out["ltf_fib_entry_debug"] = {
                        **ltf_base_debug,
                        "reason": "SHORT_BELOW_LEVEL",
                        "level_price": lp_val,
                    }
                    reasons.append("LTF_FIB_SHORT_BLOCK")
                    _log_decision_event(
                        "LTF_FIB_BLOCK",
                        reason="SHORT_BELOW_LEVEL",
                        price=p_val,
                        level=lp_val,
                        tolerance=tol_val,
                    )
                    return "NONE", {
                        "versions": versions,
                        "reasons": reasons,
                        "state_out": state_out,
                    }

        state_out["ltf_fib_entry_debug"] = {
            **ltf_base_debug,
            "reason": "PASS",
        }

    state_out["fib_gate_summary"] = {
        "candidate": candidate,
        "htf": _summarize_fib_debug(state_out.get("htf_fib_entry_debug")),
        "ltf": _summarize_fib_debug(state_out.get("ltf_fib_entry_debug")),
    }

    # 7) Confidence‑gate (kräv över entry_conf_overall för vald riktning)
    if not confidence or not isinstance(confidence, dict):
        reasons.append("FAIL_SAFE_NULL")
        _log_decision_event("FAIL_SAFE_NO_CONFIDENCE", confidence=confidence)
        return "NONE", {
            "versions": versions,
            "reasons": reasons,
            "state_out": state_out,
        }
    c_buy = float(confidence.get("buy", 0.0))
    c_sell = float(confidence.get("sell", 0.0))
    conf_thr = default_thr

    # Check confidence threshold
    if candidate == "LONG" and c_buy < conf_thr:
        reasons.append("CONF_TOO_LOW")
        _log_decision_event(
            "CONF_TOO_LOW",
            candidate=candidate,
            confidence=c_buy,
            threshold=conf_thr,
        )
        return "NONE", {
            "versions": versions,
            "reasons": reasons,
            "state_out": state_out,
        }
    if candidate == "SHORT" and c_sell < conf_thr:
        reasons.append("CONF_TOO_LOW")
        _log_decision_event(
            "CONF_TOO_LOW",
            candidate=candidate,
            confidence=c_sell,
            threshold=conf_thr,
        )
        return "NONE", {
            "versions": versions,
            "reasons": reasons,
            "state_out": state_out,
        }

    # 7b) Edge requirement (probability difference must be significant)
    # Only trade when there's clear directional edge, not just marginal difference
    min_edge = safe_float((cfg.get("thresholds") or {}).get("min_edge"), 0.0)
    if min_edge > 0:
        if candidate == "LONG":
            edge = p_buy - p_sell
            if edge < min_edge:
                reasons.append("EDGE_TOO_SMALL")
                _log_decision_event(
                    "EDGE_TOO_SMALL", candidate=candidate, edge=edge, min_edge=min_edge
                )
                return "NONE", {
                    "versions": versions,
                    "reasons": reasons,
                    "state_out": state_out,
                }
        elif candidate == "SHORT":
            edge = p_sell - p_buy
            if edge < min_edge:
                reasons.append("EDGE_TOO_SMALL")
                _log_decision_event(
                    "EDGE_TOO_SMALL", candidate=candidate, edge=edge, min_edge=min_edge
                )
                return "NONE", {
                    "versions": versions,
                    "reasons": reasons,
                    "state_out": state_out,
                }

    # 8) Hysteresis (håll kvar föregående riktning tills N steg bekräftar byte)
    hysteresis_steps = int((cfg.get("gates") or {}).get("hysteresis_steps") or 2)
    last_action = state_in.get("last_action")
    d_steps = int(state_in.get("decision_steps", 0))
    if last_action in ("LONG", "SHORT") and candidate != last_action:
        d_steps += 1
        if d_steps < hysteresis_steps:
            reasons.append("HYST_WAIT")
            state_out["decision_steps"] = d_steps
            _log_decision_event(
                "HYSTERESIS_BLOCK",
                last_action=last_action,
                candidate=candidate,
                steps=d_steps,
                hysteresis=hysteresis_steps,
            )
            return "NONE", {
                "versions": versions,
                "reasons": reasons,
                "state_out": state_out,
            }
        # annars skifta och reset
    else:
        d_steps = 0
    state_out["decision_steps"] = d_steps

    # 9) Cooldown
    cooldown_left = int(state_in.get("cooldown_remaining", 0))
    if cooldown_left > 0:
        reasons.append("COOLDOWN_ACTIVE")
        _log_decision_event("COOLDOWN_ACTIVE", remaining=cooldown_left)
        state_out["cooldown_remaining"] = max(0, cooldown_left - 1)
        return "NONE", {
            "versions": versions,
            "reasons": reasons,
            "state_out": state_out,
        }

    # 10) Sizing (baserat på risk_map och vald confidence)
    risk_map = (cfg.get("risk") or {}).get("risk_map", [])
    conf_val = c_buy if candidate == "LONG" else c_sell
    size = 0.0
    try:
        for thr_v, sz in sorted(risk_map, key=lambda x: float(x[0])):
            if conf_val >= float(thr_v):
                size = float(sz)
    except Exception:
        size = 0.0

    if size <= 0.0:
        _log_decision_event(
            "SIZE_ZERO",
            candidate=candidate,
            confidence=conf_val,
            risk_map=risk_map,
        )

    state_out["last_action"] = candidate
    # Starta cooldown efter beslut
    cooldown_bars = int((cfg.get("gates") or {}).get("cooldown_bars") or 0)
    if cooldown_bars > 0:
        state_out["cooldown_remaining"] = cooldown_bars

    state_out["zone_debug"] = zone_debug

    reasons.append("ENTRY_LONG" if candidate == "LONG" else "ENTRY_SHORT")

    meta: dict[str, Any] = {
        "versions": versions,
        "reasons": reasons,
        "size": size,
        "state_out": state_out,
    }

    # FORENSIC DEBUG - verify function returns expected values
    _LOG.info(
        "[FORENSIC] About to return: candidate=%s, size=%.4f, conf=%.4f, zone=%s",
        candidate,
        size,
        conf_val,
        zone_debug.get("current_zone"),
    )

    _log_decision_event(
        "ENTRY",
        candidate=candidate,
        size=size,
        confidence=conf_val,
        cooldown=state_out.get("cooldown_remaining"),
    )
    return candidate, meta
