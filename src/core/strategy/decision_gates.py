from __future__ import annotations

import math
from collections.abc import Callable
from typing import Any, Literal

Action = Literal["LONG", "SHORT", "NONE"]

_RESEARCH_BULL_HIGH_PERSISTENCE_REASON = "RESEARCH_BULL_HIGH_PERSISTENCE_OVERRIDE"
_RESEARCH_BULL_HIGH_PERSISTENCE_STATE_KEY = "research_bull_high_persistence_state"
_RESEARCH_BULL_HIGH_PERSISTENCE_DEBUG_KEY = "research_bull_high_persistence_debug"
_RESEARCH_DEFENSIVE_TRANSITION_REASON = "RESEARCH_DEFENSIVE_TRANSITION_OVERRIDE"
_RESEARCH_DEFENSIVE_TRANSITION_DEBUG_KEY = "research_defensive_transition_debug"


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float, handling None and invalid types."""
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def compute_percentile(values: list[float], q: float) -> float:
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


def _none_result(
    versions: dict[str, Any],
    reasons: list[str],
    state_out: dict[str, Any],
) -> tuple[Action, dict[str, Any]]:
    return "NONE", {
        "versions": versions,
        "reasons": reasons,
        "state_out": state_out,
    }


def _get_research_bull_high_persistence_prev_streak(state_in: dict[str, Any]) -> int:
    raw_state = state_in.get(_RESEARCH_BULL_HIGH_PERSISTENCE_STATE_KEY)
    if not isinstance(raw_state, dict):
        return 0
    return max(0, int(safe_float(raw_state.get("near_miss_streak"), 0.0)))


def _set_research_bull_high_persistence_state(state_out: dict[str, Any], streak: int) -> None:
    state_out[_RESEARCH_BULL_HIGH_PERSISTENCE_STATE_KEY] = {
        "near_miss_streak": max(0, int(streak)),
    }


def _set_research_bull_high_persistence_debug(
    state_out: dict[str, Any],
    *,
    streak: int,
    min_persistence: int,
    max_probability_gap: float,
    threshold: float,
    threshold_gap: float,
    p_buy: float,
    p_sell: float,
    regime: str,
    zone: str,
) -> None:
    state_out[_RESEARCH_BULL_HIGH_PERSISTENCE_DEBUG_KEY] = {
        "applied": True,
        "reason": _RESEARCH_BULL_HIGH_PERSISTENCE_REASON,
        "near_miss_streak": max(0, int(streak)),
        "min_persistence": int(min_persistence),
        "max_probability_gap": float(max_probability_gap),
        "threshold": float(threshold),
        "threshold_gap": float(threshold_gap),
        "buy": float(p_buy),
        "sell": float(p_sell),
        "regime": regime,
        "zone": zone,
    }


def _set_research_defensive_transition_debug(
    state_out: dict[str, Any],
    *,
    candidate: Action,
    bars_since_regime_change: int,
    guard_bars: int,
    max_probability_gap: float,
    threshold: float,
    threshold_gap: float,
    p_buy: float,
    p_sell: float,
    regime: str,
    zone: str,
) -> None:
    state_out[_RESEARCH_DEFENSIVE_TRANSITION_DEBUG_KEY] = {
        "applied": True,
        "reason": _RESEARCH_DEFENSIVE_TRANSITION_REASON,
        "candidate": candidate,
        "bars_since_regime_change": max(0, int(bars_since_regime_change)),
        "guard_bars": max(1, int(guard_bars)),
        "max_probability_gap": float(max_probability_gap),
        "threshold": float(threshold),
        "threshold_gap": float(threshold_gap),
        "buy": float(p_buy),
        "sell": float(p_sell),
        "regime": regime,
        "zone": zone,
    }


def select_candidate(
    *,
    policy: dict[str, Any],
    probas: dict[str, float] | None,
    regime: str | None,
    risk_ctx: dict[str, Any] | None,
    cfg: dict[str, Any],
    state_in: dict[str, Any],
    state_out: dict[str, Any],
    reasons: list[str],
    versions: dict[str, Any],
    log_decision_event: Callable[..., None],
) -> tuple[Action | None, dict[str, Any] | None, dict[str, Any]]:
    mtf_cfg = cfg.get("multi_timeframe") or {}
    research_override_cfg = dict(mtf_cfg.get("research_bull_high_persistence_override") or {})
    research_override_enabled = bool(research_override_cfg.get("enabled", False))
    research_min_persistence = max(
        1,
        int(safe_float(research_override_cfg.get("min_persistence", 2), 2.0)),
    )
    research_max_probability_gap = safe_float(
        research_override_cfg.get("max_probability_gap", 0.06),
        0.06,
    )
    research_prev_streak = _get_research_bull_high_persistence_prev_streak(state_in)
    research_defensive_transition_cfg = dict(
        mtf_cfg.get("research_defensive_transition_override") or {}
    )
    research_defensive_transition_enabled = bool(
        research_defensive_transition_cfg.get("enabled", False)
    )
    research_defensive_transition_guard_bars = max(
        1,
        int(safe_float(research_defensive_transition_cfg.get("guard_bars", 3), 3.0)),
    )
    research_defensive_transition_max_probability_gap = safe_float(
        research_defensive_transition_cfg.get("max_probability_gap", 0.06),
        0.06,
    )
    bars_since_regime_change = max(
        0,
        int(safe_float(state_in.get("bars_since_regime_change", 0.0), 0.0)),
    )

    if not probas or not isinstance(probas, dict):
        if research_override_enabled and research_prev_streak > 0:
            _set_research_bull_high_persistence_state(state_out, 0)
        reasons.append("FAIL_SAFE_NULL")
        log_decision_event("FAIL_SAFE_NO_PROBAS", probas=probas)
        action, meta = _none_result(versions, reasons, state_out)
        return action, meta, {}

    p_buy = safe_float(probas.get("buy", 0.0), 0.0)
    p_sell = safe_float(probas.get("sell", 0.0), 0.0)
    r_default = safe_float((cfg.get("ev") or {}).get("R_default") or 1.0, 1.0)

    ev_long = p_buy * r_default - p_sell
    ev_short = p_sell * r_default - p_buy
    max_ev = max(ev_long, ev_short)

    if max_ev <= 0.0:
        if research_override_enabled and research_prev_streak > 0:
            _set_research_bull_high_persistence_state(state_out, 0)
        reasons.append("EV_NEG")
        log_decision_event(
            "EV_NEGATIVE",
            p_buy=p_buy,
            p_sell=p_sell,
            ev_long=ev_long,
            ev_short=ev_short,
            R=r_default,
        )
        action, meta = _none_result(versions, reasons, state_out)
        return action, meta, {}

    if (risk_ctx or {}).get("event_block"):
        if research_override_enabled and research_prev_streak > 0:
            _set_research_bull_high_persistence_state(state_out, 0)
        reasons.append("R_EVENT_BLOCK")
        action, meta = _none_result(versions, reasons, state_out)
        return action, meta, {}

    if (risk_ctx or {}).get("risk_cap_breached"):
        if research_override_enabled and research_prev_streak > 0:
            _set_research_bull_high_persistence_state(state_out, 0)
        reasons.append("RISK_CAP")
        action, meta = _none_result(versions, reasons, state_out)
        return action, meta, {}

    regime_str = str(regime or "balanced")
    long_allowed = True
    short_allowed = True
    if regime_str == "trend":
        if policy.get("trend_long_only"):
            short_allowed = False
        if policy.get("trend_short_only"):
            long_allowed = False

    thresholds_cfg = cfg.get("thresholds") or {}
    adaptation_cfg_raw = thresholds_cfg.get("signal_adaptation") or {}
    adaptation_cfg = (
        adaptation_cfg_raw
        if not (isinstance(adaptation_cfg_raw, dict) and adaptation_cfg_raw.get("enabled") is False)
        else {}
    )
    default_thr = safe_float(thresholds_cfg.get("entry_conf_overall", 0.7), 0.7)

    atr = state_in.get("current_atr") if adaptation_cfg else None
    atr_percentiles = state_in.get("atr_percentiles") if adaptation_cfg else None

    zone_name = None
    zone_debug: dict[str, Any] = {}
    if adaptation_cfg and atr_percentiles:
        zones = adaptation_cfg.get("zones", {})
        atr_period = int(adaptation_cfg.get("atr_period", 14))
        if atr is not None:
            atr_p = atr_percentiles.get(str(atr_period)) or atr_percentiles.get(atr_period) or {}
            atr_safe = safe_float(atr, 0.0)
            p40 = safe_float(atr_p.get("p40", atr_safe), atr_safe)
            p80 = safe_float(atr_p.get("p80", atr_safe), atr_safe)
            if atr <= p40:
                zone_name = "low"
            elif atr <= p80:
                zone_name = "mid"
            else:
                zone_name = "high"

        zone_cfg = zones.get(zone_name or "") or {}
        zone_entry = zone_cfg.get("entry_conf_overall")
        if zone_entry is not None:
            default_thr = safe_float(zone_entry, default_thr)
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
    if isinstance(thresholds, float | int):
        threshold = safe_float(thresholds, default_thr)
    else:
        threshold = safe_float(thresholds.get(regime_str, default_thr), default_thr)

    buy_pass = p_buy >= threshold and long_allowed
    sell_pass = p_sell >= threshold and short_allowed
    research_family_active = False
    if not buy_pass and not sell_pass:
        threshold_gap = threshold - p_buy
        buy_threshold_gap = threshold - p_buy
        sell_threshold_gap = threshold - p_sell
        research_family = (
            research_override_enabled
            and regime_str == "bull"
            and zone_name == "high"
            and p_buy > p_sell
            and threshold_gap >= 0.0
            and threshold_gap <= research_max_probability_gap
        )
        research_family_active = research_family
        research_streak = research_prev_streak + 1 if research_family else 0
        defensive_transition_candidate: Action | None = None
        defensive_transition_threshold_gap: float | None = None
        if (
            research_defensive_transition_enabled
            and zone_name == "high"
            and 0 < bars_since_regime_change <= research_defensive_transition_guard_bars
        ):
            if (
                long_allowed
                and p_buy > p_sell
                and buy_threshold_gap >= 0.0
                and buy_threshold_gap <= research_defensive_transition_max_probability_gap
            ):
                defensive_transition_candidate = "LONG"
                defensive_transition_threshold_gap = buy_threshold_gap
            elif (
                short_allowed
                and p_sell > p_buy
                and sell_threshold_gap >= 0.0
                and sell_threshold_gap <= research_defensive_transition_max_probability_gap
            ):
                defensive_transition_candidate = "SHORT"
                defensive_transition_threshold_gap = sell_threshold_gap
        if research_override_enabled and (research_family or research_prev_streak > 0):
            _set_research_bull_high_persistence_state(state_out, research_streak)
        if research_family and research_streak >= research_min_persistence:
            reasons.append(_RESEARCH_BULL_HIGH_PERSISTENCE_REASON)
            _set_research_bull_high_persistence_debug(
                state_out,
                streak=research_streak,
                min_persistence=research_min_persistence,
                max_probability_gap=research_max_probability_gap,
                threshold=threshold,
                threshold_gap=threshold_gap,
                p_buy=p_buy,
                p_sell=p_sell,
                regime=regime_str,
                zone=zone_name or "base",
            )
            buy_pass = True
            log_decision_event(
                "RESEARCH_BULL_HIGH_PERSISTENCE_OVERRIDE",
                threshold=threshold,
                threshold_gap=threshold_gap,
                streak=research_streak,
                min_persistence=research_min_persistence,
                regime=regime_str,
                zone=zone_name,
                p_buy=p_buy,
                p_sell=p_sell,
            )
        elif (
            defensive_transition_candidate is not None
            and defensive_transition_threshold_gap is not None
        ):
            reasons.append(_RESEARCH_DEFENSIVE_TRANSITION_REASON)
            _set_research_defensive_transition_debug(
                state_out,
                candidate=defensive_transition_candidate,
                bars_since_regime_change=bars_since_regime_change,
                guard_bars=research_defensive_transition_guard_bars,
                max_probability_gap=research_defensive_transition_max_probability_gap,
                threshold=threshold,
                threshold_gap=defensive_transition_threshold_gap,
                p_buy=p_buy,
                p_sell=p_sell,
                regime=regime_str,
                zone=zone_name or "base",
            )
            if defensive_transition_candidate == "LONG":
                buy_pass = True
            else:
                sell_pass = True
            log_decision_event(
                "RESEARCH_DEFENSIVE_TRANSITION_OVERRIDE",
                candidate=defensive_transition_candidate,
                threshold=threshold,
                threshold_gap=defensive_transition_threshold_gap,
                bars_since_regime_change=bars_since_regime_change,
                guard_bars=research_defensive_transition_guard_bars,
                max_probability_gap=research_defensive_transition_max_probability_gap,
                regime=regime_str,
                zone=zone_name,
                p_buy=p_buy,
                p_sell=p_sell,
            )
        else:
            log_decision_event(
                "PROBA_THRESHOLD_FAIL",
                buy_pass=buy_pass,
                sell_pass=sell_pass,
                threshold=threshold,
                regime=regime_str,
                p_buy=p_buy,
                p_sell=p_sell,
            )
            action, meta = _none_result(versions, reasons, state_out)
            return action, meta, {}

    if research_override_enabled and research_prev_streak > 0 and not research_family_active:
        _set_research_bull_high_persistence_state(state_out, 0)

    if not buy_pass and not sell_pass:
        log_decision_event(
            "PROBA_THRESHOLD_FAIL",
            buy_pass=buy_pass,
            sell_pass=sell_pass,
            threshold=threshold,
            regime=regime_str,
            p_buy=p_buy,
            p_sell=p_sell,
        )
        action, meta = _none_result(versions, reasons, state_out)
        return action, meta, {}

    candidate: Action
    if buy_pass and not sell_pass:
        candidate = "LONG"
    elif sell_pass and not buy_pass:
        candidate = "SHORT"
    else:
        if abs(p_buy - p_sell) < 1e-12:
            last_action = state_in.get("last_action")
            if last_action in ("LONG", "SHORT"):
                candidate = last_action
            else:
                if regime_str in ("bull", "trend"):
                    candidate = "LONG"
                elif regime_str == "bear":
                    candidate = "SHORT"
                else:
                    reasons.append("P_TIE_BREAK")
                    log_decision_event(
                        "P_TIE_BREAK",
                        p_buy=p_buy,
                        p_sell=p_sell,
                        regime=regime_str,
                    )
                    action, meta = _none_result(versions, reasons, state_out)
                    return action, meta, {}
        else:
            candidate = "LONG" if p_buy > p_sell else "SHORT"

    log_decision_event(
        "CANDIDATE_SELECTED",
        candidate=candidate,
        buy_pass=buy_pass,
        sell_pass=sell_pass,
        p_buy=p_buy,
        p_sell=p_sell,
        zone=zone_label,
    )

    return (
        None,
        None,
        {
            "candidate": candidate,
            "p_buy": p_buy,
            "p_sell": p_sell,
            "R": r_default,
            "max_ev": max_ev,
            "regime_str": regime_str,
            "default_thr": default_thr,
            "zone_debug": zone_debug,
        },
    )


def apply_post_fib_gates(
    *,
    candidate: Action,
    confidence: dict[str, float] | None,
    cfg: dict[str, Any],
    state_in: dict[str, Any],
    state_out: dict[str, Any],
    reasons: list[str],
    versions: dict[str, Any],
    default_thr: float,
    p_buy: float,
    p_sell: float,
    log_decision_event: Callable[..., None],
) -> tuple[Action | None, dict[str, Any] | None, dict[str, Any]]:
    if not confidence or not isinstance(confidence, dict):
        reasons.append("FAIL_SAFE_NULL")
        log_decision_event("FAIL_SAFE_NO_CONFIDENCE", confidence=confidence)
        action, meta = _none_result(versions, reasons, state_out)
        return action, meta, {}

    c_buy = safe_float(confidence.get("buy", 0.0), 0.0)
    c_sell = safe_float(confidence.get("sell", 0.0), 0.0)
    conf_thr = default_thr

    if candidate == "LONG" and c_buy < conf_thr:
        reasons.append("CONF_TOO_LOW")
        log_decision_event(
            "CONF_TOO_LOW",
            candidate=candidate,
            confidence=c_buy,
            threshold=conf_thr,
        )
        action, meta = _none_result(versions, reasons, state_out)
        return action, meta, {}

    if candidate == "SHORT" and c_sell < conf_thr:
        reasons.append("CONF_TOO_LOW")
        log_decision_event(
            "CONF_TOO_LOW",
            candidate=candidate,
            confidence=c_sell,
            threshold=conf_thr,
        )
        action, meta = _none_result(versions, reasons, state_out)
        return action, meta, {}

    min_edge = safe_float((cfg.get("thresholds") or {}).get("min_edge"), 0.0)
    if min_edge > 0:
        if candidate == "LONG":
            edge = p_buy - p_sell
            if edge < min_edge:
                reasons.append("EDGE_TOO_SMALL")
                log_decision_event(
                    "EDGE_TOO_SMALL",
                    candidate=candidate,
                    edge=edge,
                    min_edge=min_edge,
                )
                action, meta = _none_result(versions, reasons, state_out)
                return action, meta, {}
        elif candidate == "SHORT":
            edge = p_sell - p_buy
            if edge < min_edge:
                reasons.append("EDGE_TOO_SMALL")
                log_decision_event(
                    "EDGE_TOO_SMALL",
                    candidate=candidate,
                    edge=edge,
                    min_edge=min_edge,
                )
                action, meta = _none_result(versions, reasons, state_out)
                return action, meta, {}

    hysteresis_steps = int((cfg.get("gates") or {}).get("hysteresis_steps") or 2)
    last_action = state_in.get("last_action")
    decision_steps = int(state_in.get("decision_steps", 0))
    if last_action in ("LONG", "SHORT") and candidate != last_action:
        decision_steps += 1
        if decision_steps < hysteresis_steps:
            reasons.append("HYST_WAIT")
            state_out["decision_steps"] = decision_steps
            log_decision_event(
                "HYSTERESIS_BLOCK",
                last_action=last_action,
                candidate=candidate,
                steps=decision_steps,
                hysteresis=hysteresis_steps,
            )
            action, meta = _none_result(versions, reasons, state_out)
            return action, meta, {}
    else:
        decision_steps = 0
    state_out["decision_steps"] = decision_steps

    cooldown_left = int(state_in.get("cooldown_remaining", 0))
    if cooldown_left > 0:
        reasons.append("COOLDOWN_ACTIVE")
        log_decision_event("COOLDOWN_ACTIVE", remaining=cooldown_left)
        state_out["cooldown_remaining"] = max(0, cooldown_left - 1)
        action, meta = _none_result(versions, reasons, state_out)
        return action, meta, {}

    conf_val_gate = c_buy if candidate == "LONG" else c_sell
    return (
        None,
        None,
        {
            "c_buy": c_buy,
            "c_sell": c_sell,
            "conf_val_gate": conf_val_gate,
        },
    )
