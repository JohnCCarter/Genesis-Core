from __future__ import annotations

from collections.abc import Callable
from typing import Any

from core.strategy.decision_fib_gating_helpers import (
    _as_float,
    _is_context_error_reason,
    _level_price,
    _levels_to_lookup,
    _none_result,
    _summarize_fib_debug,
    prepare_override_context,
    try_override_htf_block,
)
from core.strategy.decision_gates import Action, safe_float


def apply_fib_gating(
    *,
    policy_symbol: str,
    policy_timeframe: str,
    candidate: Action,
    confidence: dict[str, float] | None,
    cfg: dict[str, Any],
    state_in: dict[str, Any],
    state_out: dict[str, Any],
    reasons: list[str],
    versions: dict[str, Any],
    regime_str: str,
    use_htf_block: bool,
    allow_ltf_override_cfg: bool,
    ltf_override_threshold: float,
    adaptive_cfg: dict[str, Any],
    override_state: dict[str, Any],
    logger: Any,
    log_decision_event: Callable[..., None],
    log_fib_flow: Callable[..., None],
) -> tuple[Action | None, dict[str, Any] | None]:
    ltf_entry_cfg = (cfg.get("ltf_fib") or {}).get("entry") or {}
    override_context_ref: dict[str, Any | None] = {"data": None}

    override_context = prepare_override_context(
        ltf_entry_cfg=ltf_entry_cfg,
        confidence=confidence,
        candidate=candidate,
        adaptive_cfg=adaptive_cfg,
        override_state=override_state,
        allow_ltf_override_cfg=allow_ltf_override_cfg,
        ltf_override_threshold=ltf_override_threshold,
        regime_str=regime_str,
    )
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
            fallback_conf = safe_float(
                confidence.get("buy" if candidate == "LONG" else "sell", 0.0),
                0.0,
            )
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

    htf_entry_cfg = (cfg.get("htf_fib") or {}).get("entry") or {}
    log_fib_flow(
        "[FIB-FLOW] HTF gate check: use_htf_block=%s htf_entry_enabled=%s",
        use_htf_block,
        htf_entry_cfg.get("enabled"),
        logger=logger,
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
            logger=logger,
        )
        price_now = state_in.get("last_close")
        atr_now = float(state_in.get("current_atr") or 0.0)
        tolerance = float(htf_entry_cfg.get("tolerance_atr", 0.5)) * atr_now if atr_now > 0 else 0.0

        missing_allowed = False
        if not htf_ctx.get("available"):
            unavailable_reason = htf_ctx.get("reason")
            if _is_context_error_reason(unavailable_reason):
                state_out["htf_fib_entry_debug"] = {
                    "reason": "CONTEXT_ERROR_BLOCK",
                    "raw": htf_ctx,
                }
                reasons.append("HTF_FIB_CONTEXT_ERROR")
                log_decision_event(
                    "HTF_FIB_BLOCK",
                    reason="CONTEXT_ERROR",
                    context_reason=unavailable_reason,
                    candidate=candidate,
                )
                return _none_result(versions, reasons, state_out)
            missing_policy = str(htf_entry_cfg.get("missing_policy") or "pass").lower()
            state_out["htf_fib_entry_debug"] = {
                "reason": "UNAVAILABLE",
                "raw": htf_ctx,
                "policy": missing_policy,
            }
            if missing_policy != "pass":
                reasons.append("HTF_FIB_UNAVAILABLE")
                log_decision_event(
                    "HTF_FIB_BLOCK",
                    reason="UNAVAILABLE",
                    policy=missing_policy,
                    candidate=candidate,
                )
                return _none_result(versions, reasons, state_out)
            missing_allowed = True
            state_out["htf_fib_entry_debug"]["reason"] = "UNAVAILABLE_PASS"

        if price_now is None:
            state_out["htf_fib_entry_debug"] = {
                "reason": "NO_PRICE",
                "raw": htf_ctx,
            }
            reasons.append("HTF_FIB_NO_PRICE")
            log_decision_event("HTF_FIB_BLOCK", reason="NO_PRICE", candidate=candidate)
            return _none_result(versions, reasons, state_out)

        htf_levels = _levels_to_lookup(htf_ctx.get("levels"))
        base_debug = {
            "price": price_now,
            "atr": atr_now,
            "tolerance": tolerance,
            "levels": {str(key): htf_levels[key] for key in htf_levels},
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
                        htf_levels,
                        float(min_level) if min_level is not None else None,
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
                        if not try_override_htf_block(
                            ltf_entry_cfg=ltf_entry_cfg,
                            confidence=confidence,
                            context=override_context_ref.get("data"),
                            payload=payload,
                            allow_ltf_override_cfg=allow_ltf_override_cfg,
                            ltf_override_threshold=ltf_override_threshold,
                            state_out=state_out,
                            reasons=reasons,
                            logger=logger,
                            policy_symbol=policy_symbol,
                            policy_timeframe=policy_timeframe,
                            candidate=candidate,
                        ):
                            state_out["htf_fib_entry_debug"] = payload
                            reasons.append("HTF_FIB_LONG_BLOCK")
                            log_decision_event(
                                "HTF_FIB_BLOCK",
                                reason=payload.get("reason"),
                                price=payload.get("price"),
                                tolerance=payload.get("tolerance"),
                            )
                            return _none_result(versions, reasons, state_out)
                    elif target_debug and not matched:
                        payload = {
                            **base_debug,
                            "reason": "LONG_OFF_TARGET",
                        }
                        if not try_override_htf_block(
                            ltf_entry_cfg=ltf_entry_cfg,
                            confidence=confidence,
                            context=override_context_ref.get("data"),
                            payload=payload,
                            allow_ltf_override_cfg=allow_ltf_override_cfg,
                            ltf_override_threshold=ltf_override_threshold,
                            state_out=state_out,
                            reasons=reasons,
                            logger=logger,
                            policy_symbol=policy_symbol,
                            policy_timeframe=policy_timeframe,
                            candidate=candidate,
                        ):
                            state_out["htf_fib_entry_debug"] = payload
                            reasons.append("HTF_FIB_LONG_BLOCK")
                            log_decision_event(
                                "HTF_FIB_BLOCK",
                                reason=payload.get("reason"),
                                targets=payload.get("targets"),
                            )
                            return _none_result(versions, reasons, state_out)
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
                        htf_levels,
                        float(max_level) if max_level is not None else None,
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
                        if not try_override_htf_block(
                            ltf_entry_cfg=ltf_entry_cfg,
                            confidence=confidence,
                            context=override_context_ref.get("data"),
                            payload=payload,
                            allow_ltf_override_cfg=allow_ltf_override_cfg,
                            ltf_override_threshold=ltf_override_threshold,
                            state_out=state_out,
                            reasons=reasons,
                            logger=logger,
                            policy_symbol=policy_symbol,
                            policy_timeframe=policy_timeframe,
                            candidate=candidate,
                        ):
                            state_out["htf_fib_entry_debug"] = payload
                            reasons.append("HTF_FIB_SHORT_BLOCK")
                            log_decision_event(
                                "HTF_FIB_BLOCK",
                                reason=payload.get("reason"),
                                price=payload.get("price"),
                                tolerance=payload.get("tolerance"),
                            )
                            return _none_result(versions, reasons, state_out)
                    elif target_debug and not matched:
                        payload = {
                            **base_debug,
                            "reason": "SHORT_OFF_TARGET",
                        }
                        if not try_override_htf_block(
                            ltf_entry_cfg=ltf_entry_cfg,
                            confidence=confidence,
                            context=override_context_ref.get("data"),
                            payload=payload,
                            allow_ltf_override_cfg=allow_ltf_override_cfg,
                            ltf_override_threshold=ltf_override_threshold,
                            state_out=state_out,
                            reasons=reasons,
                            logger=logger,
                            policy_symbol=policy_symbol,
                            policy_timeframe=policy_timeframe,
                            candidate=candidate,
                        ):
                            state_out["htf_fib_entry_debug"] = payload
                            reasons.append("HTF_FIB_SHORT_BLOCK")
                            log_decision_event(
                                "HTF_FIB_BLOCK",
                                reason=payload.get("reason"),
                                targets=payload.get("targets"),
                            )
                            return _none_result(versions, reasons, state_out)

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

    if ltf_entry_cfg.get("enabled"):
        ltf_ctx = state_in.get("ltf_fib") or {}
        log_fib_flow(
            "[FIB-FLOW] LTF gate active: symbol=%s timeframe=%s enabled=%s ltf_ctx_keys=%s available=%s",
            policy_symbol,
            policy_timeframe,
            ltf_entry_cfg.get("enabled"),
            list(ltf_ctx.keys()) if isinstance(ltf_ctx, dict) else [],
            ltf_ctx.get("available") if isinstance(ltf_ctx, dict) else None,
            logger=logger,
        )
        price_now = state_in.get("last_close")
        atr_now = float(state_in.get("current_atr") or 0.0)
        tolerance = float(ltf_entry_cfg.get("tolerance_atr", 0.5)) * atr_now if atr_now > 0 else 0.0

        missing_allowed_ltf = False
        if not ltf_ctx.get("available"):
            unavailable_reason = ltf_ctx.get("reason")
            if _is_context_error_reason(unavailable_reason):
                state_out["ltf_fib_entry_debug"] = {
                    "reason": "CONTEXT_ERROR_BLOCK",
                    "raw": ltf_ctx,
                }
                reasons.append("LTF_FIB_CONTEXT_ERROR")
                log_decision_event(
                    "LTF_FIB_BLOCK",
                    reason="CONTEXT_ERROR",
                    context_reason=unavailable_reason,
                    candidate=candidate,
                )
                return _none_result(versions, reasons, state_out)
            missing_policy = str(ltf_entry_cfg.get("missing_policy") or "pass").lower()
            state_out["ltf_fib_entry_debug"] = {
                "reason": "UNAVAILABLE",
                "raw": ltf_ctx,
                "policy": missing_policy,
            }
            if missing_policy != "pass":
                reasons.append("LTF_FIB_UNAVAILABLE")
                log_decision_event(
                    "LTF_FIB_BLOCK",
                    reason="UNAVAILABLE",
                    policy=missing_policy,
                    candidate=candidate,
                )
                return _none_result(versions, reasons, state_out)
            missing_allowed_ltf = True
            state_out["ltf_fib_entry_debug"]["reason"] = "UNAVAILABLE_PASS"

        levels = _levels_to_lookup(ltf_ctx.get("levels"))
        if price_now is None:
            state_out["ltf_fib_entry_debug"] = {
                "reason": "NO_PRICE",
                "raw": ltf_ctx,
            }
            reasons.append("LTF_FIB_NO_PRICE")
            log_decision_event("LTF_FIB_BLOCK", reason="NO_PRICE", candidate=candidate)
            return _none_result(versions, reasons, state_out)

        ltf_base_debug = {
            "price": price_now,
            "atr": atr_now,
            "tolerance": tolerance,
            "levels": {str(key): levels[key] for key in levels},
            "config": {
                "long_max_level": ltf_entry_cfg.get("long_max_level"),
                "short_min_level": ltf_entry_cfg.get("short_min_level"),
            },
        }

        if not missing_allowed_ltf:
            if candidate == "LONG":
                max_level = ltf_entry_cfg.get("long_max_level")
                level_price = _level_price(
                    levels,
                    float(max_level) if max_level is not None else None,
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
                    log_decision_event(
                        "LTF_FIB_BLOCK",
                        reason="LONG_ABOVE_LEVEL",
                        price=p_val,
                        level=lp_val,
                        tolerance=tol_val,
                    )
                    return _none_result(versions, reasons, state_out)
            elif candidate == "SHORT":
                min_level = ltf_entry_cfg.get("short_min_level")
                level_price = _level_price(
                    levels,
                    float(min_level) if min_level is not None else None,
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
                    log_decision_event(
                        "LTF_FIB_BLOCK",
                        reason="SHORT_BELOW_LEVEL",
                        price=p_val,
                        level=lp_val,
                        tolerance=tol_val,
                    )
                    return _none_result(versions, reasons, state_out)

        state_out["ltf_fib_entry_debug"] = {
            **ltf_base_debug,
            "reason": "PASS",
        }

    state_out["fib_gate_summary"] = {
        "candidate": candidate,
        "htf": _summarize_fib_debug(state_out.get("htf_fib_entry_debug")),
        "ltf": _summarize_fib_debug(state_out.get("ltf_fib_entry_debug")),
    }
    return None, None
