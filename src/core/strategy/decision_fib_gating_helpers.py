from __future__ import annotations

from typing import Any

from core.strategy.decision_gates import Action


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
