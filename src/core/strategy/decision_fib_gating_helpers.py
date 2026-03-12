from __future__ import annotations

from collections.abc import Callable
from typing import Any

from core.strategy.decision_gates import Action, compute_percentile, safe_float


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


def _as_float(value: Any) -> float | None:
    try:
        return float(value)
    except Exception:
        return None


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
    nearest = min(levels.keys(), key=lambda key: abs(key - target))
    if abs(nearest - target) <= 1e-6:
        return levels[nearest]
    return None


def _is_context_error_reason(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    return value.strip().upper().endswith("_CONTEXT_ERROR")


def prepare_override_context(
    *,
    ltf_entry_cfg: dict[str, Any],
    confidence: dict[str, float] | None,
    candidate: Action,
    adaptive_cfg: dict[str, Any],
    override_state: dict[str, Any],
    allow_ltf_override_cfg: bool,
    ltf_override_threshold: float,
    regime_str: str,
) -> dict[str, Any]:
    if not ltf_entry_cfg.get("enabled"):
        return {}
    if not confidence or not isinstance(confidence, dict):
        return {}

    conf_key = "buy" if candidate == "LONG" else "sell"
    conf_val = safe_float(confidence.get(conf_key, 0.0), 0.0)
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
            compute_percentile(history, percentile_q) if len(history) >= min_history else None
        )
        fallback = adaptive_cfg.get("fallback_threshold")
        base_threshold = safe_float(
            (
                raw_threshold
                if raw_threshold is not None
                else (fallback if fallback is not None else ltf_override_threshold)
            ),
            ltf_override_threshold,
        )
        multiplier = safe_float(
            (adaptive_cfg.get("regime_multipliers") or {}).get(regime_str, 1.0),
            1.0,
        )
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


def _apply_override(
    *,
    payload: dict[str, Any],
    source: str,
    extra: dict[str, Any],
    conf_val: float,
    state_out: dict[str, Any],
    reasons: list[str],
    logger: Any,
    policy_symbol: str,
    policy_timeframe: str,
    candidate: Action,
) -> bool:
    reason_label = str(payload.get("reason", "HTF_BLOCK"))
    payload_override = dict(payload)
    payload_override["override"] = {
        "source": source,
        "confidence": conf_val,
        **extra,
    }
    payload_override["reason"] = f"{reason_label}_OVERRIDE"
    state_out["htf_fib_entry_debug"] = payload_override
    reasons.append("HTF_OVERRIDE_LTF_CONF")
    logger.info(
        "[OVERRIDE] LTF override triggered source=%s symbol=%s timeframe=%s direction=%s confidence=%.3f details=%s",
        source,
        policy_symbol,
        policy_timeframe,
        candidate,
        conf_val,
        extra,
    )
    return True


def try_override_htf_block(
    *,
    ltf_entry_cfg: dict[str, Any],
    confidence: dict[str, float] | None,
    context: dict[str, Any] | None,
    payload: dict[str, Any],
    allow_ltf_override_cfg: bool,
    ltf_override_threshold: float,
    state_out: dict[str, Any],
    reasons: list[str],
    logger: Any,
    policy_symbol: str,
    policy_timeframe: str,
    candidate: Action,
) -> bool:
    if not ltf_entry_cfg.get("enabled"):
        return False
    if not confidence or not isinstance(confidence, dict):
        return False
    if not isinstance(context, dict):
        return False

    conf_val = safe_float(context.get("conf_val", 0.0), 0.0)
    effective_threshold = safe_float(
        context.get("effective_threshold", ltf_override_threshold),
        ltf_override_threshold,
    )
    adaptive_debug = context.get("adaptive_debug")

    if allow_ltf_override_cfg and conf_val >= effective_threshold:
        return _apply_override(
            payload=payload,
            source="multi_timeframe_threshold",
            extra={
                "threshold": effective_threshold,
                "baseline": ltf_override_threshold,
                "adaptive": adaptive_debug,
            },
            conf_val=conf_val,
            state_out=state_out,
            reasons=reasons,
            logger=logger,
            policy_symbol=policy_symbol,
            policy_timeframe=policy_timeframe,
            candidate=candidate,
        )

    override_cfg = ltf_entry_cfg.get("override_confidence") or {}
    if override_cfg.get("enabled"):
        min_conf = safe_float(override_cfg.get("min", 0.0), 0.0)
        max_conf = safe_float(override_cfg.get("max", 1.0), 1.0)
        if min_conf <= conf_val <= max_conf:
            return _apply_override(
                payload=payload,
                source="ltf_entry_range",
                extra={"min": min_conf, "max": max_conf},
                conf_val=conf_val,
                state_out=state_out,
                reasons=reasons,
                logger=logger,
                policy_symbol=policy_symbol,
                policy_timeframe=policy_timeframe,
                candidate=candidate,
            )
    return False


def apply_htf_fib_gate(
    *,
    policy_symbol: str,
    policy_timeframe: str,
    candidate: Action,
    cfg: dict[str, Any],
    state_in: dict[str, Any],
    state_out: dict[str, Any],
    reasons: list[str],
    versions: dict[str, Any],
    use_htf_block: bool,
    ltf_entry_cfg: dict[str, Any],
    confidence: dict[str, float] | None,
    override_context: dict[str, Any] | None,
    allow_ltf_override_cfg: bool,
    ltf_override_threshold: float,
    logger: Any,
    log_decision_event: Callable[..., None],
    log_fib_flow: Callable[..., None],
) -> tuple[Action | None, dict[str, Any] | None]:
    htf_entry_cfg = (cfg.get("htf_fib") or {}).get("entry") or {}
    log_fib_flow(
        "[FIB-FLOW] HTF gate check: use_htf_block=%s htf_entry_enabled=%s",
        use_htf_block,
        htf_entry_cfg.get("enabled"),
        logger=logger,
    )

    if not (use_htf_block and htf_entry_cfg.get("enabled")):
        if not use_htf_block:
            state_out.setdefault(
                "htf_fib_entry_debug",
                {
                    "reason": "DISABLED_BY_CONFIG",
                    "config": {"use_htf_block": use_htf_block},
                },
            )
        return None, None

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
                        context=override_context,
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
                        context=override_context,
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
                        context=override_context,
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
                        context=override_context,
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

    return None, None
