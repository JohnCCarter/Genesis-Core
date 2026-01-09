from __future__ import annotations

from collections.abc import Mapping
from typing import Any

TIMEFRAME_TO_MINUTES: dict[str, int] = {
    "1m": 1,
    "5m": 5,
    "15m": 15,
    "30m": 30,
    "1h": 60,
    "3h": 180,
    "6h": 360,
    "12h": 720,
    "1D": 1440,
    "2D": 2880,
    "1W": 10080,
}
MINUTES_TO_TIMEFRAME = {minutes: tf for tf, minutes in TIMEFRAME_TO_MINUTES.items()}
DEFAULT_HTF_MAP = {
    "1h": "6h",
}


def _to_dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if hasattr(value, "model_dump"):
        try:
            return dict(value.model_dump())  # type: ignore[return-value]
        except Exception:
            return {}
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def _apply_multiplier(base_timeframe: str, multiplier: Any) -> str | None:
    if multiplier is None:
        return None
    try:
        mult = float(multiplier)
    except (TypeError, ValueError):
        return None
    if mult <= 0:
        return None
    base_minutes = TIMEFRAME_TO_MINUTES.get(base_timeframe)
    if base_minutes is None:
        return None
    total_minutes = base_minutes * mult
    rounded = int(round(total_minutes))
    if abs(total_minutes - rounded) > 1e-6:
        return None
    return MINUTES_TO_TIMEFRAME.get(rounded)


def _resolve_rule(rule: Any, ltf_timeframe: str, source: str) -> tuple[str | None, dict[str, Any]]:
    step = {"source": source, "success": False}
    rule_dict = _to_dict(rule)
    if not rule_dict:
        return None, step
    explicit_tf = rule_dict.get("timeframe")
    if isinstance(explicit_tf, str):
        step.update({"success": True, "timeframe": explicit_tf})
        return explicit_tf, step
    candidate = _apply_multiplier(ltf_timeframe, rule_dict.get("multiplier"))
    if candidate:
        step.update(
            {
                "success": True,
                "timeframe": candidate,
                "multiplier": float(rule_dict.get("multiplier")),
            }
        )
        return candidate, step
    return None, step


def select_htf_timeframe(
    ltf_timeframe: str,
    selector_cfg: Any = None,
) -> tuple[str, dict[str, Any]]:
    selector = _to_dict(selector_cfg)
    mode = str(selector.get("mode") or "fixed").lower()
    decision_path: list[dict[str, Any]] = []
    selected: str | None = None

    if mode == "fixed":
        per_tf = _to_dict(selector.get("per_timeframe"))
        rule = per_tf.get(ltf_timeframe)
        cand, step = _resolve_rule(rule, ltf_timeframe, "per_timeframe")
        decision_path.append(step)
        if cand:
            selected = cand
        if selected is None:
            default_rule = {
                "timeframe": selector.get("default_timeframe"),
                "multiplier": selector.get("default_multiplier"),
            }
            cand, step = _resolve_rule(default_rule, ltf_timeframe, "default")
            decision_path.append(step)
            if cand:
                selected = cand
    else:
        decision_path.append({"source": mode, "success": False, "reason": "mode_unimplemented"})

    fallback_tf = selector.get("fallback_timeframe")
    if selected is None and isinstance(fallback_tf, str):
        selected = fallback_tf
        decision_path.append({"source": "fallback", "success": True, "timeframe": fallback_tf})

    if selected is None:
        default_tf = DEFAULT_HTF_MAP.get(ltf_timeframe) or "1D"
        selected = default_tf
        decision_path.append({"source": "static_default", "success": True, "timeframe": default_tf})

    meta = {
        "mode": mode,
        "selected": selected,
        "decision_path": decision_path,
    }
    return selected, meta
