from __future__ import annotations

from typing import Any, Literal

Action = Literal["LONG", "SHORT", "NONE"]


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
    reasons: list[str] = []
    versions: dict[str, Any] = {"decision": "v1"}
    cfg = dict(cfg or {})
    state_in = dict(state or {})
    state_out: dict[str, Any] = dict(state_in)

    # 1) Fail‑safe & EV‑filter
    if not probas or not isinstance(probas, dict):
        reasons.append("FAIL_SAFE_NULL")
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
    thresholds = (cfg.get("thresholds") or {}).get("regime_proba", {})
    default_thr = float((cfg.get("thresholds") or {}).get("entry_conf_overall", 0.7))
    thr = float(thresholds.get(regime_str, default_thr))

    buy_pass = p_buy >= thr and long_allowed
    sell_pass = p_sell >= thr and short_allowed
    if not buy_pass and not sell_pass:
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
                reasons.append("P_TIE_BREAK")
                return "NONE", {
                    "versions": versions,
                    "reasons": reasons,
                    "state_out": state_out,
                }
        else:
            candidate = "LONG" if p_buy > p_sell else "SHORT"

    # 7) Confidence‑gate (kräv över entry_conf_overall för vald riktning)
    if not confidence or not isinstance(confidence, dict):
        reasons.append("FAIL_SAFE_NULL")
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
        return "NONE", {
            "versions": versions,
            "reasons": reasons,
            "state_out": state_out,
        }
    if candidate == "SHORT" and c_sell < conf_thr:
        reasons.append("CONF_TOO_LOW")
        return "NONE", {
            "versions": versions,
            "reasons": reasons,
            "state_out": state_out,
        }

    # 7b) Edge requirement (probability difference must be significant)
    # Only trade when there's clear directional edge, not just marginal difference
    min_edge = float((cfg.get("thresholds") or {}).get("min_edge", 0.0))
    if min_edge > 0:
        if candidate == "LONG":
            edge = p_buy - p_sell
            if edge < min_edge:
                reasons.append("EDGE_TOO_SMALL")
                return "NONE", {
                    "versions": versions,
                    "reasons": reasons,
                    "state_out": state_out,
                }
        elif candidate == "SHORT":
            edge = p_sell - p_buy
            if edge < min_edge:
                reasons.append("EDGE_TOO_SMALL")
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

    state_out["last_action"] = candidate
    # Starta cooldown efter beslut
    cooldown_bars = int((cfg.get("gates") or {}).get("cooldown_bars") or 0)
    if cooldown_bars > 0:
        state_out["cooldown_remaining"] = cooldown_bars

    meta: dict[str, Any] = {
        "versions": versions,
        "reasons": reasons,
        "size": size,
        "state_out": state_out,
    }
    return candidate, meta
