from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from statistics import fmean, median
from typing import Any

LOCAL_ROOT_DIR = Path(__file__).resolve().parents[2]
if str(LOCAL_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(LOCAL_ROOT_DIR))

from scripts.analyze.ri_policy_router_insufficient_evidence_local_window_20260429 import (
    ACTION_DIFF_ROOT,
    ACTION_DIFF_ROOT_RELATIVE,
    CURATED_CANDLES_PATH,
    CURATED_CANDLES_RELATIVE,
    ROOT_DIR,
    LocalWindowEvidenceError,
    _load_candles,
    _load_json,
    _normalize_timestamp,
    _normalized_constant_timestamps,
    _row_observational_metrics,
    load_subject_rows,
    select_exact_rows,
)

OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = (
    "ri_policy_router_insufficient_evidence_d1_family_survival_"
    "2019_06_vs_2025_03_2026-05-04.json"
)
SUBJECT_SYMBOL = "tBTCUSD"
SUBJECT_TIMEFRAME = "3h"
HARMFUL_YEAR = "2019"
CONTROL_YEAR = "2025"
PACKET_REFERENCE = Path(
    "docs/decisions/regime_intelligence/policy_router/"
    "ri_policy_router_insufficient_evidence_d1_family_survival_"
    "2019_06_vs_2025_03_precode_packet_2026-05-04.md"
)
FIRST_PAIR_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_insufficient_evidence_d1_exact_subject_pair_"
    "2019_06_vs_2022_06_2026-05-04.md"
)
CONTROL_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_positive_year_insufficient_evidence_control_2026-04-29.md"
)
JULY_PARKING_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_insufficient_evidence_july_2024_"
    "within_envelope_falsifier_2026-05-04.md"
)
HARMFUL_TARGET_TIMESTAMPS = (
    "2019-06-13T06:00:00+00:00",
    "2019-06-13T15:00:00+00:00",
    "2019-06-14T00:00:00+00:00",
    "2019-06-14T09:00:00+00:00",
    "2019-06-15T06:00:00+00:00",
)
HARMFUL_CONTEXT_TIMESTAMPS = ("2019-06-12T06:00:00+00:00",)
CONTROL_TARGET_TIMESTAMPS = (
    "2025-03-14T15:00:00+00:00",
    "2025-03-15T00:00:00+00:00",
    "2025-03-15T09:00:00+00:00",
    "2025-03-15T18:00:00+00:00",
    "2025-03-16T03:00:00+00:00",
)
CONTROL_DISPLACEMENT_TIMESTAMPS = (
    "2025-03-13T15:00:00+00:00",
    "2025-03-14T00:00:00+00:00",
)
CONTROL_BLOCKED_CONTEXT_TIMESTAMPS = (
    "2025-03-13T21:00:00+00:00",
    "2025-03-14T06:00:00+00:00",
)
CONTROL_AGED_WEAK_CONTEXT_TIMESTAMPS = ("2025-03-16T12:00:00+00:00",)
SUMMARY_NUMERIC_FIELDS = (
    "bars_since_regime_change",
    "action_edge",
    "confidence_gate",
    "clarity_score",
    "clarity_raw",
    "dwell_duration",
    "fwd_4_close_return_pct",
    "fwd_8_close_return_pct",
    "fwd_16_close_return_pct",
    "mfe_16_pct",
    "mae_16_pct",
)
TARGET_COHORTS = ("harmful_target", "control_target")
FIXED_RULES = (
    {
        "rule_id": "action_edge_gte_0_027801",
        "field_name": "action_edge",
        "operator": ">=",
        "threshold": 0.027801,
        "descriptive_only": False,
    },
    {
        "rule_id": "confidence_gate_gte_0_513901",
        "field_name": "confidence_gate",
        "operator": ">=",
        "threshold": 0.513901,
        "descriptive_only": False,
    },
    {
        "rule_id": "clarity_raw_gte_0_361280",
        "field_name": "clarity_raw",
        "operator": ">=",
        "threshold": 0.361280,
        "descriptive_only": False,
    },
    {
        "rule_id": "bars_since_regime_change_lte_164",
        "field_name": "bars_since_regime_change",
        "operator": "<=",
        "threshold": 164.0,
        "descriptive_only": True,
    },
)


@dataclass(frozen=True)
class FixedThresholdRule:
    rule_id: str
    field_name: str
    operator: str
    threshold: float
    descriptive_only: bool

    def evaluate_row(self, row: dict[str, Any]) -> bool | None:
        value = row.get(self.field_name)
        if isinstance(value, bool) or not isinstance(value, int | float):
            return None
        numeric_value = float(value)
        if self.operator == "<=":
            return numeric_value <= self.threshold
        if self.operator == ">=":
            return numeric_value >= self.threshold
        raise LocalWindowEvidenceError(f"Unsupported operator {self.operator!r}")

    def as_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "field_name": self.field_name,
            "operator": self.operator,
            "threshold": _round_or_none(self.threshold),
            "descriptive_only": self.descriptive_only,
        }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate only the fixed D1 family thresholds on the exact 2019-06 harmful "
            "target versus the exact 2025-03 weak-control target, with context rows "
            "reported descriptively only."
        )
    )
    parser.add_argument(
        "--base-sha",
        required=True,
        help="Exact repository HEAD SHA for provenance in the emitted artifact.",
    )
    parser.add_argument(
        "--output-root-relative",
        default=str(OUTPUT_ROOT_RELATIVE),
        help="Repo-relative output directory for the emitted JSON summary.",
    )
    parser.add_argument(
        "--summary-filename",
        default=OUTPUT_FILENAME,
        help="Filename to use for the emitted JSON summary.",
    )
    return parser.parse_args()


def _round_or_none(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 6)


def _coerce_optional_numeric(value: Any, *, field_name: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise LocalWindowEvidenceError(
            f"Expected numeric optional value for {field_name}, got {value!r}"
        )
    numeric_value = float(value)
    if numeric_value != numeric_value or numeric_value in {float("inf"), float("-inf")}:
        raise LocalWindowEvidenceError(
            f"Expected finite optional value for {field_name}, got {value!r}"
        )
    return _round_or_none(numeric_value)


def _summarize_numeric_values(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {
            "count": 0,
            "min": None,
            "max": None,
            "mean": None,
            "median": None,
            "gt_zero_share": None,
        }
    positive_share = sum(value > 0 for value in values) / len(values)
    return {
        "count": len(values),
        "min": _round_or_none(min(values)),
        "max": _round_or_none(max(values)),
        "mean": _round_or_none(fmean(values)),
        "median": _round_or_none(median(values)),
        "gt_zero_share": _round_or_none(positive_share),
    }


def _load_router_debug_map(diff_path: Path) -> dict[Any, dict[str, Any]]:
    payload = _load_json(diff_path)
    if not isinstance(payload, list):
        raise LocalWindowEvidenceError(f"Expected row list in {diff_path}")

    out: dict[Any, dict[str, Any]] = {}
    for item in payload:
        if not isinstance(item, dict):
            raise LocalWindowEvidenceError(f"Expected object rows in {diff_path}")
        timestamp_value = item.get("timestamp")
        if not isinstance(timestamp_value, str):
            raise LocalWindowEvidenceError("Action-diff row is missing a string timestamp")
        enabled = item.get("enabled") or {}
        router_debug = enabled.get("router_debug")
        if not isinstance(router_debug, dict):
            continue
        timestamp = _normalize_timestamp(timestamp_value)
        if timestamp in out:
            raise LocalWindowEvidenceError(
                f"Duplicate router_debug timestamp detected in {diff_path}: {timestamp.isoformat()}"
            )
        out[timestamp] = router_debug
    return out


def _load_year_surface(year: str) -> tuple[list[Any], dict[Any, dict[str, Any]], Path]:
    diff_path = ACTION_DIFF_ROOT / f"{year}_enabled_vs_absent_action_diffs.json"
    return load_subject_rows(diff_path), _load_router_debug_map(diff_path), diff_path


def _serialize_locked_row(
    row: Any,
    *,
    cohort_name: str,
    row_role: str,
    claim_eligible: bool,
    year: str,
    router_debug_map: dict[Any, dict[str, Any]],
    candles: Any,
    timestamp_to_index: dict[Any, int],
) -> dict[str, Any]:
    router_debug = router_debug_map.get(row.timestamp)
    if not isinstance(router_debug, dict):
        raise LocalWindowEvidenceError(
            f"Router debug surface missing for locked row {row.timestamp.isoformat()}"
        )

    serialized = {
        "cohort_name": cohort_name,
        "row_role": row_role,
        "claim_eligible": claim_eligible,
        "year": year,
        "timestamp": row.timestamp.isoformat(),
        "switch_reason": row.switch_reason,
        "absent_action": row.absent_action,
        "enabled_action": row.enabled_action,
        "action_pair": row.action_pair,
        "selected_policy": row.selected_policy,
        "raw_target_policy": row.raw_target_policy,
        "previous_policy": row.previous_policy,
        "zone": row.zone,
        "candidate": row.candidate,
        "bars_since_regime_change": row.bars_since_regime_change,
        "action_edge": _round_or_none(row.action_edge),
        "confidence_gate": _round_or_none(row.confidence_gate),
        "clarity_score": _round_or_none(row.clarity_score),
        "clarity_raw": _coerce_optional_numeric(
            router_debug.get("clarity_raw"),
            field_name="clarity_raw",
        ),
        "dwell_duration": _coerce_optional_numeric(
            router_debug.get("dwell_duration"),
            field_name="dwell_duration",
        ),
    }
    serialized.update(
        _row_observational_metrics(
            timestamp=row.timestamp,
            candles=candles,
            timestamp_to_index=timestamp_to_index,
        )
    )
    return serialized


def _serialize_rows(
    rows: list[Any],
    *,
    cohort_name: str,
    row_role: str,
    claim_eligible: bool,
    year: str,
    router_debug_map: dict[Any, dict[str, Any]],
    candles: Any,
    timestamp_to_index: dict[Any, int],
) -> list[dict[str, Any]]:
    return [
        _serialize_locked_row(
            row,
            cohort_name=cohort_name,
            row_role=row_role,
            claim_eligible=claim_eligible,
            year=year,
            router_debug_map=router_debug_map,
            candles=candles,
            timestamp_to_index=timestamp_to_index,
        )
        for row in rows
    ]


def _cohort_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    metric_summary = {
        field_name: _summarize_numeric_values(
            [float(row[field_name]) for row in rows if isinstance(row.get(field_name), int | float)]
        )
        for field_name in SUMMARY_NUMERIC_FIELDS
    }
    return {
        "row_count": len(rows),
        "timestamps": [row["timestamp"] for row in rows],
        "metric_summary": metric_summary,
        "rows": rows,
    }


def _assert_row_values(
    rows: list[dict[str, Any]],
    *,
    cohort_name: str,
    expected_values: dict[str, Any],
) -> None:
    for row in rows:
        for field_name, expected_value in expected_values.items():
            if row.get(field_name) != expected_value:
                raise LocalWindowEvidenceError(
                    f"Locked row contract mismatch for {cohort_name} on {row['timestamp']}: "
                    f"expected {field_name}={expected_value!r}, got {row.get(field_name)!r}"
                )


def _assert_row_allowed_values(
    rows: list[dict[str, Any]],
    *,
    cohort_name: str,
    field_name: str,
    allowed_values: set[Any],
) -> None:
    for row in rows:
        if row.get(field_name) not in allowed_values:
            raise LocalWindowEvidenceError(
                f"Locked row contract mismatch for {cohort_name} on {row['timestamp']}: "
                f"expected {field_name} in {sorted(allowed_values)!r}, got {row.get(field_name)!r}"
            )


def _selection_summary(
    rows: list[dict[str, Any]],
    rule: FixedThresholdRule,
) -> dict[str, Any]:
    selected_timestamps: list[str] = []
    rejected_timestamps: list[str] = []
    unavailable_timestamps: list[str] = []

    for row in rows:
        result = rule.evaluate_row(row)
        if result is None:
            unavailable_timestamps.append(row["timestamp"])
        elif result:
            selected_timestamps.append(row["timestamp"])
        else:
            rejected_timestamps.append(row["timestamp"])

    evaluable_count = len(rows) - len(unavailable_timestamps)
    selection_rate = None
    if evaluable_count > 0:
        selection_rate = _round_or_none(len(selected_timestamps) / evaluable_count)
    return {
        "row_count": len(rows),
        "evaluable_count": evaluable_count,
        "selected_count": len(selected_timestamps),
        "selection_rate": selection_rate,
        "selected_timestamps": selected_timestamps,
        "rejected_timestamps": rejected_timestamps,
        "unavailable_timestamps": unavailable_timestamps,
    }


def _mean_gap(left: dict[str, Any], right: dict[str, Any], metric_name: str) -> float | None:
    left_mean = left["metric_summary"][metric_name]["mean"]
    right_mean = right["metric_summary"][metric_name]["mean"]
    if left_mean is None or right_mean is None:
        return None
    return _round_or_none(float(left_mean) - float(right_mean))


def _truth_polarity(
    harmful_target_summary: dict[str, Any],
    control_target_summary: dict[str, Any],
) -> dict[str, Any]:
    harmful_mean = harmful_target_summary["metric_summary"]["fwd_16_close_return_pct"]["mean"]
    control_mean = control_target_summary["metric_summary"]["fwd_16_close_return_pct"]["mean"]
    harmful_proxy = harmful_mean is not None and float(harmful_mean) > 0.0
    control_proxy = control_mean is not None and float(control_mean) < 0.0
    return {
        "harmful_target_fwd_16_mean": harmful_mean,
        "control_target_fwd_16_mean": control_mean,
        "harmful_minus_control_fwd_16_mean_gap": _mean_gap(
            harmful_target_summary,
            control_target_summary,
            "fwd_16_close_return_pct",
        ),
        "harmful_target_harmful_proxy_holds": harmful_proxy,
        "control_target_correct_suppression_proxy_holds": control_proxy,
    }


def _rule_target_evaluability(
    rule: FixedThresholdRule,
    *,
    harmful_target: list[dict[str, Any]],
    control_target: list[dict[str, Any]],
) -> dict[str, Any]:
    missing_timestamps = [
        row["timestamp"]
        for row in (*harmful_target, *control_target)
        if isinstance(row.get(rule.field_name), bool)
        or not isinstance(row.get(rule.field_name), int | float)
    ]
    if missing_timestamps:
        if rule.field_name == "clarity_raw":
            return {
                "status": "not_evaluable",
                "reason": "not_present_on_every_locked_target_row",
                "missing_timestamps": missing_timestamps,
            }
        raise LocalWindowEvidenceError(
            f"Locked target rows are missing direct numeric field {rule.field_name}: "
            f"{missing_timestamps}"
        )
    return {
        "status": "evaluable",
        "reason": None,
        "missing_timestamps": [],
    }


def _evaluate_fixed_rule(
    rule: FixedThresholdRule,
    *,
    cohorts: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    evaluability = _rule_target_evaluability(
        rule,
        harmful_target=cohorts["harmful_target"],
        control_target=cohorts["control_target"],
    )
    if evaluability["status"] != "evaluable":
        return {
            "rule": rule.as_dict(),
            "target_field_evaluability": evaluability,
            "selection_by_cohort": None,
            "all_harmful_targets_selected": None,
            "all_control_targets_rejected": None,
            "perfect_target_control_separation": None,
            "survives_on_target_pair": False,
            "excluded_from_pass_fail": True,
            "claim_status": "not_evaluable",
        }

    selection_by_cohort = {
        cohort_name: _selection_summary(rows, rule) for cohort_name, rows in cohorts.items()
    }
    harmful_summary = selection_by_cohort["harmful_target"]
    control_summary = selection_by_cohort["control_target"]
    all_harmful_targets_selected = harmful_summary["selected_count"] == harmful_summary["row_count"]
    all_control_targets_rejected = control_summary["selected_count"] == 0
    perfect_target_control_separation = (
        all_harmful_targets_selected and all_control_targets_rejected
    )
    survives_on_target_pair = perfect_target_control_separation and not rule.descriptive_only
    claim_status = "descriptive_only" if rule.descriptive_only else "evaluated"
    return {
        "rule": rule.as_dict(),
        "target_field_evaluability": evaluability,
        "selection_by_cohort": selection_by_cohort,
        "all_harmful_targets_selected": all_harmful_targets_selected,
        "all_control_targets_rejected": all_control_targets_rejected,
        "perfect_target_control_separation": perfect_target_control_separation,
        "survives_on_target_pair": survives_on_target_pair,
        "excluded_from_pass_fail": rule.descriptive_only,
        "claim_status": claim_status,
    }


def _build_row_role_registry(cohorts: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    registry: list[dict[str, Any]] = []
    for cohort_name, rows in cohorts.items():
        for row in rows:
            registry.append(
                {
                    "timestamp": row["timestamp"],
                    "cohort_name": cohort_name,
                    "row_role": row["row_role"],
                    "claim_eligible": row["claim_eligible"],
                    "switch_reason": row["switch_reason"],
                    "action_pair": row["action_pair"],
                }
            )
    return sorted(registry, key=lambda item: item["timestamp"])


def load_family_survival_surface() -> dict[str, Any]:
    candles, timestamp_to_index = _load_candles(CURATED_CANDLES_PATH)
    harmful_rows, harmful_router_debug, harmful_diff_path = _load_year_surface(HARMFUL_YEAR)
    control_rows, control_router_debug, control_diff_path = _load_year_surface(CONTROL_YEAR)

    harmful_target_rows = select_exact_rows(
        harmful_rows,
        exact_timestamps=_normalized_constant_timestamps(HARMFUL_TARGET_TIMESTAMPS),
        expected_reason="insufficient_evidence",
        expected_action_pair=("LONG", "NONE"),
    )
    harmful_context_rows = select_exact_rows(
        harmful_rows,
        exact_timestamps=_normalized_constant_timestamps(HARMFUL_CONTEXT_TIMESTAMPS),
        expected_reason="AGED_WEAK_CONTINUATION_GUARD",
        expected_action_pair=("LONG", "NONE"),
    )
    control_target_rows = select_exact_rows(
        control_rows,
        exact_timestamps=_normalized_constant_timestamps(CONTROL_TARGET_TIMESTAMPS),
        expected_reason="insufficient_evidence",
        expected_action_pair=("LONG", "NONE"),
    )
    control_displacement_rows = select_exact_rows(
        control_rows,
        exact_timestamps=_normalized_constant_timestamps(CONTROL_DISPLACEMENT_TIMESTAMPS),
        expected_reason="stable_continuation_state",
        expected_action_pair=("NONE", "LONG"),
    )
    control_blocked_context_rows = select_exact_rows(
        control_rows,
        exact_timestamps=_normalized_constant_timestamps(CONTROL_BLOCKED_CONTEXT_TIMESTAMPS),
        expected_reason="stable_continuation_state",
        expected_action_pair=("LONG", "NONE"),
    )
    control_aged_weak_context_rows = select_exact_rows(
        control_rows,
        exact_timestamps=_normalized_constant_timestamps(CONTROL_AGED_WEAK_CONTEXT_TIMESTAMPS),
        expected_reason="AGED_WEAK_CONTINUATION_GUARD",
        expected_action_pair=("LONG", "NONE"),
    )

    cohorts = {
        "harmful_target": _serialize_rows(
            harmful_target_rows,
            cohort_name="harmful_target",
            row_role="harmful_target",
            claim_eligible=True,
            year=HARMFUL_YEAR,
            router_debug_map=harmful_router_debug,
            candles=candles,
            timestamp_to_index=timestamp_to_index,
        ),
        "harmful_context": _serialize_rows(
            harmful_context_rows,
            cohort_name="harmful_context",
            row_role="context",
            claim_eligible=False,
            year=HARMFUL_YEAR,
            router_debug_map=harmful_router_debug,
            candles=candles,
            timestamp_to_index=timestamp_to_index,
        ),
        "control_target": _serialize_rows(
            control_target_rows,
            cohort_name="control_target",
            row_role="control_target",
            claim_eligible=True,
            year=CONTROL_YEAR,
            router_debug_map=control_router_debug,
            candles=candles,
            timestamp_to_index=timestamp_to_index,
        ),
        "control_displacement_context": _serialize_rows(
            control_displacement_rows,
            cohort_name="control_displacement_context",
            row_role="context",
            claim_eligible=False,
            year=CONTROL_YEAR,
            router_debug_map=control_router_debug,
            candles=candles,
            timestamp_to_index=timestamp_to_index,
        ),
        "control_blocked_context": _serialize_rows(
            control_blocked_context_rows,
            cohort_name="control_blocked_context",
            row_role="context",
            claim_eligible=False,
            year=CONTROL_YEAR,
            router_debug_map=control_router_debug,
            candles=candles,
            timestamp_to_index=timestamp_to_index,
        ),
        "control_aged_weak_context": _serialize_rows(
            control_aged_weak_context_rows,
            cohort_name="control_aged_weak_context",
            row_role="context",
            claim_eligible=False,
            year=CONTROL_YEAR,
            router_debug_map=control_router_debug,
            candles=candles,
            timestamp_to_index=timestamp_to_index,
        ),
    }

    _assert_row_values(
        cohorts["harmful_target"],
        cohort_name="harmful_target",
        expected_values={
            "zone": "low",
            "candidate": "LONG",
            "absent_action": "LONG",
            "enabled_action": "NONE",
            "selected_policy": "RI_no_trade_policy",
            "bars_since_regime_change": 164,
        },
    )
    _assert_row_values(
        cohorts["harmful_context"],
        cohort_name="harmful_context",
        expected_values={
            "zone": "low",
            "candidate": "LONG",
            "absent_action": "LONG",
            "enabled_action": "NONE",
            "selected_policy": "RI_no_trade_policy",
        },
    )
    _assert_row_values(
        cohorts["control_target"],
        cohort_name="control_target",
        expected_values={
            "zone": "low",
            "candidate": "LONG",
            "absent_action": "LONG",
            "enabled_action": "NONE",
            "selected_policy": "RI_no_trade_policy",
            "bars_since_regime_change": 65,
        },
    )
    _assert_row_values(
        cohorts["control_displacement_context"],
        cohort_name="control_displacement_context",
        expected_values={
            "zone": "low",
            "candidate": "LONG",
            "absent_action": "NONE",
            "enabled_action": "LONG",
            "selected_policy": "RI_continuation_policy",
        },
    )
    _assert_row_allowed_values(
        cohorts["control_displacement_context"],
        cohort_name="control_displacement_context",
        field_name="bars_since_regime_change",
        allowed_values={63, 64},
    )
    _assert_row_values(
        cohorts["control_blocked_context"],
        cohort_name="control_blocked_context",
        expected_values={
            "zone": "low",
            "candidate": "LONG",
            "absent_action": "LONG",
            "enabled_action": "NONE",
            "selected_policy": "RI_continuation_policy",
        },
    )
    _assert_row_allowed_values(
        cohorts["control_blocked_context"],
        cohort_name="control_blocked_context",
        field_name="bars_since_regime_change",
        allowed_values={63, 64},
    )
    _assert_row_values(
        cohorts["control_aged_weak_context"],
        cohort_name="control_aged_weak_context",
        expected_values={
            "zone": "low",
            "candidate": "LONG",
            "absent_action": "LONG",
            "enabled_action": "NONE",
            "selected_policy": "RI_no_trade_policy",
            "bars_since_regime_change": 65,
        },
    )

    return {
        "cohorts": cohorts,
        "candles_path": str(CURATED_CANDLES_RELATIVE),
        "input_paths": {
            "harmful_diff": str(ACTION_DIFF_ROOT_RELATIVE / harmful_diff_path.name),
            "control_diff": str(ACTION_DIFF_ROOT_RELATIVE / control_diff_path.name),
        },
    }


def run_family_survival_analysis(base_sha: str) -> dict[str, Any]:
    surface = load_family_survival_surface()
    cohorts = surface["cohorts"]
    cohort_summaries = {cohort_name: _cohort_summary(rows) for cohort_name, rows in cohorts.items()}
    truth_polarity = _truth_polarity(
        cohort_summaries["harmful_target"],
        cohort_summaries["control_target"],
    )
    if not truth_polarity["harmful_target_harmful_proxy_holds"]:
        raise LocalWindowEvidenceError(
            "2019-06 harmful target no longer reads as harmful-looking on the offline proxy"
        )
    if not truth_polarity["control_target_correct_suppression_proxy_holds"]:
        raise LocalWindowEvidenceError(
            "2025-03 control target no longer reads as correct-suppression-looking on the offline proxy"
        )

    rule_evaluations = [
        _evaluate_fixed_rule(FixedThresholdRule(**rule_definition), cohorts=cohorts)
        for rule_definition in FIXED_RULES
    ]
    surviving_non_age_rules = [
        evaluation for evaluation in rule_evaluations if evaluation["survives_on_target_pair"]
    ]
    descriptive_age_only_rule = next(
        (
            evaluation
            for evaluation in rule_evaluations
            if evaluation["rule"]["field_name"] == "bars_since_regime_change"
        ),
        None,
    )
    clarity_raw_evaluability = next(
        (
            evaluation["target_field_evaluability"]
            for evaluation in rule_evaluations
            if evaluation["rule"]["field_name"] == "clarity_raw"
        ),
        None,
    )

    status = "fixed_non_age_family_survives"
    if not surviving_non_age_rules:
        status = "fixed_non_age_family_does_not_survive"

    return {
        "audit_version": (
            "ri-policy-router-insufficient-evidence-d1-family-survival-"
            "2019-06-vs-2025-03-2026-05-04"
        ),
        "base_sha": base_sha,
        "status": status,
        "observational_only": True,
        "non_authoritative": True,
        "context_rows_excluded_from_selection": True,
        "family_survival_summary": {
            "non_age_family_survives": bool(surviving_non_age_rules),
            "surviving_non_age_rule_ids": [
                evaluation["rule"]["rule_id"] for evaluation in surviving_non_age_rules
            ],
            "surviving_non_age_rules": surviving_non_age_rules,
            "descriptive_age_only_rule_id": (
                None
                if descriptive_age_only_rule is None
                else descriptive_age_only_rule["rule"]["rule_id"]
            ),
            "age_only_rule_excluded_from_pass_fail": (
                None
                if descriptive_age_only_rule is None
                else descriptive_age_only_rule["excluded_from_pass_fail"]
            ),
        },
        "clarity_raw_evaluability": clarity_raw_evaluability,
        "subject": {
            "symbol": SUBJECT_SYMBOL,
            "timeframe": SUBJECT_TIMEFRAME,
            "harmful_year": HARMFUL_YEAR,
            "control_year": CONTROL_YEAR,
            "packet_reference": str(PACKET_REFERENCE),
            "first_pair_reference": str(FIRST_PAIR_REFERENCE),
            "control_reference": str(CONTROL_REFERENCE),
            "july_parking_reference": str(JULY_PARKING_REFERENCE),
        },
        "skill_usage": ["decision_gate_debug", "python_engineering"],
        "fail_closed_contract": {
            "statement": (
                "The helper reads only the exact locked 2019 and 2025 annual enabled-vs-absent "
                "action-diff rows plus curated candles, aborts on any row-lock or truth-polarity drift, "
                "evaluates only the pre-registered fixed thresholds, excludes context rows from PASS/FAIL "
                "adjudication, and keeps every outcome descriptive only with zero runtime, policy, "
                "promotion, or readiness authority."
            )
        },
        "search_boundary": {
            "statement": (
                "No threshold search, conjunction search, optimizer, grid search, cross-window tuning, "
                "backfilled features, reconstructed fields, or substitute fields are allowed. This slice "
                "tests fixed-family survival only."
            )
        },
        "inputs": {
            "action_diff_root": str(ACTION_DIFF_ROOT_RELATIVE),
            "harmful_diff": surface["input_paths"]["harmful_diff"],
            "control_diff": surface["input_paths"]["control_diff"],
            "curated_candles": surface["candles_path"],
        },
        "artifact_row_lock": {
            "harmful_target_timestamps": [row["timestamp"] for row in cohorts["harmful_target"]],
            "harmful_context_timestamps": [row["timestamp"] for row in cohorts["harmful_context"]],
            "control_target_timestamps": [row["timestamp"] for row in cohorts["control_target"]],
            "control_displacement_context_timestamps": [
                row["timestamp"] for row in cohorts["control_displacement_context"]
            ],
            "control_blocked_context_timestamps": [
                row["timestamp"] for row in cohorts["control_blocked_context"]
            ],
            "control_aged_weak_context_timestamps": [
                row["timestamp"] for row in cohorts["control_aged_weak_context"]
            ],
            "fixed_rules_tested": [
                FixedThresholdRule(**rule_definition).as_dict() for rule_definition in FIXED_RULES
            ],
            "clarity_raw_evaluability": clarity_raw_evaluability,
            "row_role_registry": _build_row_role_registry(cohorts),
            "context_rows_excluded_from_selection": True,
            "observational_only_authority": True,
        },
        "truth_polarity": truth_polarity,
        "cohorts": cohort_summaries,
        "fixed_rule_evaluations": rule_evaluations,
    }


def main() -> int:
    args = _parse_args()
    output_root = ROOT_DIR / Path(args.output_root_relative)
    output_json = output_root / args.summary_filename
    result = run_family_survival_analysis(base_sha=args.base_sha)

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "summary_artifact": str(output_json),
                "status": result["status"],
                "surviving_non_age_rule_ids": result["family_survival_summary"][
                    "surviving_non_age_rule_ids"
                ],
                "clarity_raw_evaluability": result["clarity_raw_evaluability"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
