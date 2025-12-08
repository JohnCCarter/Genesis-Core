from __future__ import annotations

import copy
from typing import Any

# Champion baseline risk map (kept in ascending order)
BASE_RISK_MAP: list[tuple[float, float]] = [
    (0.48, 0.01),
    (0.59, 0.015),
    (0.70, 0.07),
]


def _safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float, handling dicts/None."""
    if value is None:
        return default
    if isinstance(value, dict):
        # Handle case where parameter expansion created a dict (e.g. nested keys)
        # If the dict has a 'value' key, use it, otherwise default
        return float(value.get("value", default))
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _build_risk_map_from_deltas(deltas: dict[str, Any]) -> list[list[float]]:
    """Construct risk map points by applying deltas to the champion baseline."""
    points: list[tuple[float, float]] = []
    for idx, (base_conf, base_size) in enumerate(BASE_RISK_MAP):
        conf_delta = _safe_float(deltas.get(f"conf_{idx}"))
        size_delta = _safe_float(deltas.get(f"size_{idx}"))
        conf = max(0.05, min(0.95, base_conf + conf_delta))
        size = max(0.0, base_size + size_delta)
        points.append((conf, size))

    # Sort by confidence and enforce monotonic increasing sizes
    points.sort(key=lambda item: item[0])
    result: list[list[float]] = []
    last_size = 0.0
    for conf, size in points:
        size = max(size, last_size)
        last_size = size
        result.append([round(conf, 6), round(size, 6)])

    return result


def _expand_dot_notation(params: dict[str, Any]) -> dict[str, Any]:
    """Expand dot-notation keys into nested dictionaries."""
    expanded: dict[str, Any] = {}
    for key, value in params.items():
        if "." in key:
            parts = key.split(".")
            current = expanded
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
                if not isinstance(current, dict):
                    # Should not happen in valid config, but handle gracefully
                    continue
            current[parts[-1]] = value
        else:
            if key in expanded and isinstance(expanded[key], dict) and isinstance(value, dict):
                expanded[key].update(value)
            else:
                expanded[key] = value
    return expanded


def transform_parameters(parameters: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Apply optimizer parameter transforms (risk map construction, etc.).

    Returns a tuple of:
        transformed_parameters: dict ready to merge into runtime config
        derived_values: dict with helpful derived structures (for logging/debug)
    """
    # Expand dot-notation keys first (e.g. "thresholds.entry_conf" -> {"thresholds": {"entry_conf": ...}})
    params = _expand_dot_notation(parameters)
    params = copy.deepcopy(params)
    derived: dict[str, Any] = {}

    risk_cfg = params.get("risk")
    if isinstance(risk_cfg, dict):
        deltas = risk_cfg.pop("risk_map_deltas", None)
        if isinstance(deltas, dict):
            risk_map = _build_risk_map_from_deltas(deltas)
            risk_cfg["risk_map"] = risk_map
            derived.setdefault("risk", {})["risk_map"] = risk_map
        elif "risk_map" not in risk_cfg:
            risk_cfg["risk_map"] = [
                [round(conf, 6), round(size, 6)] for conf, size in BASE_RISK_MAP
            ]

    return params, derived
