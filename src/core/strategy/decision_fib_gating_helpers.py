from __future__ import annotations

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
