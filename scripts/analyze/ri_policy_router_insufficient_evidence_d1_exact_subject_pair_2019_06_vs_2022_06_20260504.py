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
    "ri_policy_router_insufficient_evidence_d1_exact_subject_pair_"
    "2019_06_vs_2022_06_2026-05-04.json"
)
SUBJECT_SYMBOL = "tBTCUSD"
SUBJECT_TIMEFRAME = "3h"
HARMFUL_YEAR = "2019"
CONTROL_YEAR = "2022"
PACKET_REFERENCE = Path(
    "docs/decisions/regime_intelligence/policy_router/"
    "ri_policy_router_insufficient_evidence_d1_exact_subject_pair_precode_packet_2026-05-04.md"
)
CONTROL_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_insufficient_evidence_2022_06_weak_signal_holdout_2026-05-04.md"
)
PARKING_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_insufficient_evidence_translation_parking_synthesis_2026-05-04.md"
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
    "2022-06-24T03:00:00+00:00",
    "2022-06-24T21:00:00+00:00",
    "2022-06-25T06:00:00+00:00",
    "2022-06-25T15:00:00+00:00",
    "2022-06-26T00:00:00+00:00",
)
CONTROL_DISPLACEMENT_TIMESTAMPS = (
    "2022-06-23T03:00:00+00:00",
    "2022-06-23T12:00:00+00:00",
)
CONTROL_BLOCKED_CONTEXT_TIMESTAMPS = (
    "2022-06-23T09:00:00+00:00",
    "2022-06-23T18:00:00+00:00",
)
MINIMUM_DECISION_FIELDS = (
    "bars_since_regime_change",
    "action_edge",
    "confidence_gate",
    "clarity_score",
)
OPTIONAL_DECISION_FIELDS = ("clarity_raw", "dwell_duration")
DESCRIPTIVE_ONLY_FIELDS = frozenset({"bars_since_regime_change"})
OFFLINE_METRIC_FIELDS = (
    "fwd_4_close_return_pct",
    "fwd_8_close_return_pct",
    "fwd_16_close_return_pct",
    "mfe_16_pct",
    "mae_16_pct",
)
SUMMARY_NUMERIC_FIELDS = (
    *MINIMUM_DECISION_FIELDS,
    *OPTIONAL_DECISION_FIELDS,
    *OFFLINE_METRIC_FIELDS,
)
TARGET_COHORTS = ("harmful_target", "control_target")
CONTEXT_COHORTS = ("harmful_context", "control_context")


@dataclass(frozen=True)
class ThresholdRule:
    field_name: str
    operator: str
    threshold: float

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
            "field_name": self.field_name,
            "operator": self.operator,
            "threshold": _round_or_none(self.threshold),
        }


@dataclass(frozen=True)
class ConjunctionRule:
    left: ThresholdRule
    right: ThresholdRule

    def evaluate_row(self, row: dict[str, Any]) -> bool | None:
        left_result = self.left.evaluate_row(row)
        right_result = self.right.evaluate_row(row)
        if left_result is None or right_result is None:
            return None
        return left_result and right_result

    def as_dict(self) -> dict[str, Any]:
        return {
            "rules": [self.left.as_dict(), self.right.as_dict()],
        }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Materialize one bounded D1 subject-pair comparison between the exact 2019-06 "
            "harmful insufficient-evidence pocket and the exact 2022-06 weak-control "
            "insufficient-evidence pocket."
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
    year: str,
    router_debug_map: dict[Any, dict[str, Any]],
    candles: Any,
    timestamp_to_index: dict[Any, int],
) -> list[dict[str, Any]]:
    return [
        _serialize_locked_row(
            row,
            cohort_name=cohort_name,
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


def _require_target_field_availability(
    field_name: str,
    *,
    harmful_target: list[dict[str, Any]],
    control_target: list[dict[str, Any]],
) -> None:
    missing_timestamps = [
        row["timestamp"]
        for row in (*harmful_target, *control_target)
        if isinstance(row.get(field_name), bool) or not isinstance(row.get(field_name), int | float)
    ]
    if missing_timestamps:
        raise LocalWindowEvidenceError(
            f"Locked target rows are missing direct numeric field {field_name}: {missing_timestamps}"
        )


def _resolve_candidate_fields(
    *,
    harmful_target: list[dict[str, Any]],
    control_target: list[dict[str, Any]],
) -> dict[str, Any]:
    available_optional_fields: list[str] = []
    skipped_optional_fields: list[dict[str, Any]] = []

    for field_name in MINIMUM_DECISION_FIELDS:
        _require_target_field_availability(
            field_name,
            harmful_target=harmful_target,
            control_target=control_target,
        )

    for field_name in OPTIONAL_DECISION_FIELDS:
        missing_timestamps = [
            row["timestamp"]
            for row in (*harmful_target, *control_target)
            if row.get(field_name) is None
        ]
        invalid_timestamps = [
            row["timestamp"]
            for row in (*harmful_target, *control_target)
            if row.get(field_name) is not None
            and (
                isinstance(row.get(field_name), bool)
                or not isinstance(row.get(field_name), int | float)
            )
        ]
        if invalid_timestamps:
            raise LocalWindowEvidenceError(
                f"Optional field {field_name} is non-numeric on locked targets: {invalid_timestamps}"
            )
        if missing_timestamps:
            skipped_optional_fields.append(
                {
                    "field_name": field_name,
                    "reason": "not_present_on_every_locked_target_row",
                    "missing_timestamps": missing_timestamps,
                }
            )
            continue
        available_optional_fields.append(field_name)

    return {
        "candidate_fields_used_for_selection": [
            *MINIMUM_DECISION_FIELDS,
            *available_optional_fields,
        ],
        "available_optional_fields": available_optional_fields,
        "skipped_optional_fields": skipped_optional_fields,
    }


def _selection_summary(
    rows: list[dict[str, Any]],
    rule: ThresholdRule | ConjunctionRule,
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


def _single_field_sort_key(evaluation: dict[str, Any]) -> tuple[Any, ...]:
    threshold = float(evaluation["rule"]["threshold"])
    operator = str(evaluation["rule"]["operator"])
    return (
        0 if evaluation["perfect_target_control_separation"] else 1,
        -int(evaluation["selected_harmful_target_count"]),
        int(evaluation["selected_control_target_count"]),
        0 if operator == "<=" else 1,
        threshold,
    )


def _evaluate_threshold_rule(
    rule: ThresholdRule,
    *,
    field_name: str,
    cohorts: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    selection_by_cohort = {
        cohort_name: _selection_summary(rows, rule) for cohort_name, rows in cohorts.items()
    }
    for cohort_name in TARGET_COHORTS:
        unavailable_count = (
            selection_by_cohort[cohort_name]["row_count"]
            - selection_by_cohort[cohort_name]["evaluable_count"]
        )
        if unavailable_count != 0:
            raise LocalWindowEvidenceError(
                f"Selection field {field_name} was unavailable on locked target cohort {cohort_name}"
            )

    harmful_selected = selection_by_cohort["harmful_target"]["selected_count"]
    control_selected = selection_by_cohort["control_target"]["selected_count"]
    perfect_target_control_separation = (
        harmful_selected == selection_by_cohort["harmful_target"]["row_count"]
        and control_selected == 0
    )
    descriptive_only_reason = None
    accepted_as_d1_answer = perfect_target_control_separation
    if perfect_target_control_separation and field_name in DESCRIPTIVE_ONLY_FIELDS:
        descriptive_only_reason = "pure_cross_envelope_age_split_not_accepted"
        accepted_as_d1_answer = False

    return {
        "search_shape": "single_threshold",
        "rule": rule.as_dict(),
        "selection_by_cohort": selection_by_cohort,
        "selected_harmful_target_count": harmful_selected,
        "selected_control_target_count": control_selected,
        "perfect_target_control_separation": perfect_target_control_separation,
        "accepted_as_d1_answer": accepted_as_d1_answer,
        "descriptive_only_reason": descriptive_only_reason,
    }


def _best_single_field_evaluation(
    field_name: str,
    *,
    cohorts: dict[str, list[dict[str, Any]]],
) -> tuple[ThresholdRule, dict[str, Any]]:
    target_rows = [*cohorts["harmful_target"], *cohorts["control_target"]]
    thresholds = sorted({float(row[field_name]) for row in target_rows})
    evaluations: list[tuple[ThresholdRule, dict[str, Any]]] = []
    for operator in ("<=", ">="):
        for threshold in thresholds:
            rule = ThresholdRule(field_name=field_name, operator=operator, threshold=threshold)
            evaluation = _evaluate_threshold_rule(rule, field_name=field_name, cohorts=cohorts)
            evaluations.append((rule, evaluation))

    best_rule, best_evaluation = min(evaluations, key=lambda item: _single_field_sort_key(item[1]))
    return best_rule, best_evaluation


def _best_non_age_fields(
    best_single_field_evaluations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    eligible = [
        evaluation
        for evaluation in best_single_field_evaluations
        if evaluation["field_name"] not in DESCRIPTIVE_ONLY_FIELDS
    ]
    return sorted(
        eligible,
        key=lambda evaluation: (
            0 if evaluation["accepted_as_d1_answer"] else 1,
            0 if evaluation["perfect_target_control_separation"] else 1,
            -int(evaluation["selected_harmful_target_count"]),
            int(evaluation["selected_control_target_count"]),
            evaluation["field_name"],
        ),
    )


def _evaluate_conjunction_rule(
    rule: ConjunctionRule,
    *,
    cohorts: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    selection_by_cohort = {
        cohort_name: _selection_summary(rows, rule) for cohort_name, rows in cohorts.items()
    }
    for cohort_name in TARGET_COHORTS:
        unavailable_count = (
            selection_by_cohort[cohort_name]["row_count"]
            - selection_by_cohort[cohort_name]["evaluable_count"]
        )
        if unavailable_count != 0:
            raise LocalWindowEvidenceError(
                f"Conjunction field set was unavailable on locked target cohort {cohort_name}"
            )

    harmful_selected = selection_by_cohort["harmful_target"]["selected_count"]
    control_selected = selection_by_cohort["control_target"]["selected_count"]
    perfect_target_control_separation = (
        harmful_selected == selection_by_cohort["harmful_target"]["row_count"]
        and control_selected == 0
    )
    return {
        "search_shape": "two_field_conjunction",
        "rule": rule.as_dict(),
        "selection_by_cohort": selection_by_cohort,
        "selected_harmful_target_count": harmful_selected,
        "selected_control_target_count": control_selected,
        "perfect_target_control_separation": perfect_target_control_separation,
        "accepted_as_d1_answer": perfect_target_control_separation,
        "descriptive_only_reason": None,
    }


def _build_two_field_conjunction(
    best_single_field_evaluations: list[dict[str, Any]],
    *,
    cohorts: dict[str, list[dict[str, Any]]],
) -> dict[str, Any] | None:
    eligible = _best_non_age_fields(best_single_field_evaluations)
    if len(eligible) < 2:
        return None

    left_rule = ThresholdRule(**eligible[0]["rule"])
    right_rule = ThresholdRule(**eligible[1]["rule"])
    conjunction_rule = ConjunctionRule(left=left_rule, right=right_rule)
    evaluation = _evaluate_conjunction_rule(conjunction_rule, cohorts=cohorts)
    evaluation["basis"] = {
        "left_field": eligible[0]["field_name"],
        "right_field": eligible[1]["field_name"],
        "left_rule": eligible[0]["rule"],
        "right_rule": eligible[1]["rule"],
    }
    return evaluation


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


def load_exact_subject_pair() -> dict[str, Any]:
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
    control_context_rows = sorted(
        [*control_displacement_rows, *control_blocked_context_rows],
        key=lambda row: row.timestamp,
    )

    cohorts = {
        "harmful_target": _serialize_rows(
            harmful_target_rows,
            cohort_name="harmful_target",
            year=HARMFUL_YEAR,
            router_debug_map=harmful_router_debug,
            candles=candles,
            timestamp_to_index=timestamp_to_index,
        ),
        "harmful_context": _serialize_rows(
            harmful_context_rows,
            cohort_name="harmful_context",
            year=HARMFUL_YEAR,
            router_debug_map=harmful_router_debug,
            candles=candles,
            timestamp_to_index=timestamp_to_index,
        ),
        "control_target": _serialize_rows(
            control_target_rows,
            cohort_name="control_target",
            year=CONTROL_YEAR,
            router_debug_map=control_router_debug,
            candles=candles,
            timestamp_to_index=timestamp_to_index,
        ),
        "control_context": _serialize_rows(
            control_context_rows,
            cohort_name="control_context",
            year=CONTROL_YEAR,
            router_debug_map=control_router_debug,
            candles=candles,
            timestamp_to_index=timestamp_to_index,
        ),
    }

    field_metadata = _resolve_candidate_fields(
        harmful_target=cohorts["harmful_target"],
        control_target=cohorts["control_target"],
    )

    return {
        "cohorts": cohorts,
        "candles_path": str(CURATED_CANDLES_RELATIVE),
        "input_paths": {
            "harmful_diff": str(ACTION_DIFF_ROOT_RELATIVE / harmful_diff_path.name),
            "control_diff": str(ACTION_DIFF_ROOT_RELATIVE / control_diff_path.name),
        },
        "field_metadata": field_metadata,
    }


def run_d1_exact_subject_pair_analysis(base_sha: str) -> dict[str, Any]:
    surface = load_exact_subject_pair()
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
            "2022-06 control target no longer reads as correct-suppression-looking on the offline proxy"
        )

    best_single_field_evaluations: list[dict[str, Any]] = []
    for field_name in surface["field_metadata"]["candidate_fields_used_for_selection"]:
        rule, evaluation = _best_single_field_evaluation(field_name, cohorts=cohorts)
        best_single_field_evaluations.append(
            {
                "field_name": field_name,
                **evaluation,
            }
        )

    best_single_field_evaluations = sorted(
        best_single_field_evaluations,
        key=lambda evaluation: (
            0 if evaluation["accepted_as_d1_answer"] else 1,
            0 if evaluation["perfect_target_control_separation"] else 1,
            -int(evaluation["selected_harmful_target_count"]),
            int(evaluation["selected_control_target_count"]),
            evaluation["field_name"],
        ),
    )
    accepted_single_field = next(
        (
            evaluation
            for evaluation in best_single_field_evaluations
            if evaluation["accepted_as_d1_answer"]
        ),
        None,
    )
    descriptive_age_only_rule = next(
        (
            evaluation
            for evaluation in best_single_field_evaluations
            if evaluation["field_name"] in DESCRIPTIVE_ONLY_FIELDS
            and evaluation["perfect_target_control_separation"]
        ),
        None,
    )
    tested_two_field_conjunction = None
    accepted_separator = accepted_single_field
    status = (
        "accepted_single_threshold_separator" if accepted_single_field else "no_accepted_separator"
    )
    if accepted_single_field is None:
        tested_two_field_conjunction = _build_two_field_conjunction(
            best_single_field_evaluations,
            cohorts=cohorts,
        )
        if tested_two_field_conjunction and tested_two_field_conjunction["accepted_as_d1_answer"]:
            accepted_separator = tested_two_field_conjunction
            status = "accepted_two_field_conjunction_separator"
        elif descriptive_age_only_rule is not None:
            status = "descriptive_age_only_split_no_accepted_d1_separator"

    return {
        "audit_version": (
            "ri-policy-router-insufficient-evidence-d1-exact-subject-pair-"
            "2019-06-vs-2022-06-2026-05-04"
        ),
        "base_sha": base_sha,
        "status": status,
        "observational_only": True,
        "non_authoritative": True,
        "context_rows_excluded_from_selection": True,
        "selected_rule_search_shape": (
            None if accepted_separator is None else accepted_separator["search_shape"]
        ),
        "selected_rule": accepted_separator,
        "subject": {
            "symbol": SUBJECT_SYMBOL,
            "timeframe": SUBJECT_TIMEFRAME,
            "harmful_year": HARMFUL_YEAR,
            "control_year": CONTROL_YEAR,
            "packet_reference": str(PACKET_REFERENCE),
            "control_reference": str(CONTROL_REFERENCE),
            "parking_reference": str(PARKING_REFERENCE),
        },
        "skill_usage": ["decision_gate_debug", "python_engineering"],
        "fail_closed_contract": {
            "statement": (
                "The helper reads only the exact locked 2019 and 2022 annual enabled-vs-absent "
                "action-diff rows plus curated candles, aborts on any row-lock or truth-polarity drift, "
                "uses only direct decision-time fields on the locked target rows, excludes context rows "
                "from separator fitting and selection, and keeps every outcome descriptive only with zero "
                "runtime, policy, promotion, or readiness authority."
            )
        },
        "search_boundary": {
            "statement": (
                "Permitted search is capped at best single-threshold evaluation per admitted field and, "
                "if no accepted non-age single-field separator exists, one two-field conjunction built from "
                "the two strongest non-age single-field rules. No optimizer, grid search, cross-window tuning, "
                "backfilled features, or reconstructed fields are allowed."
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
            "control_context_timestamps": [row["timestamp"] for row in cohorts["control_context"]],
            "candidate_fields_used_for_selection": surface["field_metadata"][
                "candidate_fields_used_for_selection"
            ],
            "available_optional_fields": surface["field_metadata"]["available_optional_fields"],
            "skipped_optional_fields": surface["field_metadata"]["skipped_optional_fields"],
            "search_shapes_considered": ["single_threshold", "two_field_conjunction"],
            "context_rows_excluded_from_selection": True,
            "observational_only_authority": True,
        },
        "truth_polarity": truth_polarity,
        "cohorts": cohort_summaries,
        "best_single_field_by_field": best_single_field_evaluations,
        "descriptive_age_only_rule": descriptive_age_only_rule,
        "tested_two_field_conjunction": tested_two_field_conjunction,
    }


def main() -> int:
    args = _parse_args()
    output_root = ROOT_DIR / Path(args.output_root_relative)
    output_json = output_root / args.summary_filename
    result = run_d1_exact_subject_pair_analysis(base_sha=args.base_sha)

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "summary_artifact": str(output_json),
                "status": result["status"],
                "selected_rule_search_shape": result["selected_rule_search_shape"],
                "selected_rule": result["selected_rule"],
                "descriptive_age_only_rule": result["descriptive_age_only_rule"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
