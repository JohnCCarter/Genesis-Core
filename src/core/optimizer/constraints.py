from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ConstraintResult:
    ok: bool
    reasons: list[str]


def enforce_constraints(
    score_obj: dict[str, Any],
    config: dict[str, Any],
    *,
    constraints_cfg: dict[str, Any] | None = None,
) -> ConstraintResult:
    reasons: list[str] = []
    cfg = constraints_cfg if constraints_cfg is not None else config.get("constraints") or {}

    # Optional: include scoring-level hard failures as constraint reasons
    include_scoring_failures = bool(cfg.get("include_scoring_failures", False))
    if include_scoring_failures:
        hard_failures = score_obj.get("hard_failures") or []
        if hard_failures:
            reasons.extend([f"hard_fail:{failure}" for failure in hard_failures])

    min_trades = cfg.get("min_trades")
    if isinstance(min_trades, (int | float)):
        trades = float(score_obj.get("metrics", {}).get("num_trades", 0))
        if trades < float(min_trades):
            reasons.append(f"min_trades:{trades}<{min_trades}")

    min_profit_factor = cfg.get("min_profit_factor")
    if isinstance(min_profit_factor, (int | float)):
        pf = float(score_obj.get("metrics", {}).get("profit_factor", 0))
        if pf < float(min_profit_factor):
            reasons.append(f"min_profit_factor:{pf}<{min_profit_factor}")

    max_max_dd = cfg.get("max_max_dd")
    if isinstance(max_max_dd, (int | float)):
        dd = float(score_obj.get("metrics", {}).get("max_drawdown", 0))
        if dd > float(max_max_dd):
            reasons.append(f"max_max_dd:{dd}>{max_max_dd}")

    zone_consistency = cfg.get("zone_consistency") or {}
    if zone_consistency.get("enforce"):
        allowed_diff = float(zone_consistency.get("allowed_diff", 0.1))
        thresholds_section = config.get("thresholds") or {}
        base_entry_value = thresholds_section.get("entry_conf_overall", 0.0)
        if isinstance(base_entry_value, dict):
            base_entry_value = base_entry_value.get("value", 0.0)
        try:
            base_entry = float(base_entry_value)
        except (TypeError, ValueError):
            base_entry = 0.0
        adaptation_cfg = thresholds_section.get("signal_adaptation") or {}
        zones = adaptation_cfg.get("zones") or {}
        for name, zone_cfg in zones.items():
            entry_value = None
            if isinstance(zone_cfg, dict):
                entry_value = zone_cfg.get("entry_conf_overall")
                if isinstance(entry_value, dict):
                    entry_value = entry_value.get("value")
            if entry_value is None:
                continue
            try:
                entry = float(entry_value)
            except (TypeError, ValueError):
                continue
            if abs(entry - base_entry) > allowed_diff:
                reasons.append(f"zone:{name}:entry_diff>{allowed_diff}")

    ok = not reasons
    return ConstraintResult(ok=ok, reasons=reasons)
