from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ConstraintResult:
    ok: bool
    reasons: list[str]


def enforce_constraints(score_obj: dict[str, Any], config: dict[str, Any]) -> ConstraintResult:
    reasons: list[str] = []
    hard_failures = score_obj.get("hard_failures") or []

    if hard_failures:
        reasons.extend([f"hard_fail:{failure}" for failure in hard_failures])

    zone_consistency = config.get("zone_consistency") or {}
    if zone_consistency.get("enforce"):
        allowed_diff = float(zone_consistency.get("allowed_diff", 0.1))
        thresholds_cfg = (config.get("thresholds") or {}).get("signal_adaptation") or {}
        zones = thresholds_cfg.get("zones") or {}
        base = config.get("thresholds") or {}
        base_entry = float(base.get("entry_conf_overall", 0.0))
        for name, zone_cfg in zones.items():
            entry = float(zone_cfg.get("entry_conf_overall", base_entry))
            if abs(entry - base_entry) > allowed_diff:
                reasons.append(f"zone:{name}:entry_diff>{allowed_diff}")

    ok = not reasons
    return ConstraintResult(ok=ok, reasons=reasons)
