from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import timedelta
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
    _normalize_timestamp,
    _normalized_constant_timestamps,
    _row_observational_metrics,
    load_subject_rows,
    select_exact_rows,
)

OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = (
    "ri_policy_router_insufficient_evidence_july_2024_within_envelope_falsifier_2026-05-04.json"
)
SUBJECT_SYMBOL = "tBTCUSD"
SUBJECT_TIMEFRAME = "3h"
TARGET_YEAR = "2024"
CONTROL_YEAR = "2020"
PACKET_REFERENCE = Path(
    "docs/decisions/regime_intelligence/policy_router/"
    "ri_policy_router_insufficient_evidence_july_2024_within_envelope_falsifier_precode_packet_2026-05-04.md"
)
BASELINE_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_insufficient_evidence_truth_surface_correction_2026-04-30.md"
)
TARGET_TIMESTAMPS = (
    "2024-07-13T09:00:00+00:00",
    "2024-07-14T09:00:00+00:00",
    "2024-07-14T18:00:00+00:00",
)
JULY_DISPLACEMENT_TIMESTAMPS = (
    "2024-07-12T09:00:00+00:00",
    "2024-07-12T18:00:00+00:00",
)
JULY_BLOCKED_CONTEXT_TIMESTAMPS = (
    "2024-07-12T15:00:00+00:00",
    "2024-07-13T00:00:00+00:00",
)
CONTROL_TARGET_TIMESTAMPS = (
    "2020-10-31T21:00:00+00:00",
    "2020-11-01T06:00:00+00:00",
    "2020-11-01T15:00:00+00:00",
    "2020-11-02T00:00:00+00:00",
)
CONTROL_DISPLACEMENT_TIMESTAMPS = (
    "2020-11-02T03:00:00+00:00",
    "2020-11-02T21:00:00+00:00",
)
CONTROL_BLOCKED_CONTEXT_TIMESTAMPS = (
    "2020-11-02T09:00:00+00:00",
    "2020-11-03T03:00:00+00:00",
)
EXPECTED_JULY_ENVELOPE_COUNT = 7
CANDIDATE_FIELDS = (
    "bars_since_regime_change",
    "action_edge",
    "confidence_gate",
    "clarity_score",
)
OFFLINE_METRIC_FIELDS = (
    "fwd_4_close_return_pct",
    "fwd_8_close_return_pct",
    "fwd_16_close_return_pct",
    "mfe_16_pct",
    "mae_16_pct",
)
SUMMARY_NUMERIC_FIELDS = (*CANDIDATE_FIELDS, *OFFLINE_METRIC_FIELDS)
NUMERIC_OPERATORS = ("<=", ">=")
REQUIRED_TARGET_SELECTION_RATE = 1.0
MAX_ANTITARGET_SELECTION_RATE = 0.25
MAX_CONTROL_SELECTION_RATE = 0.25


@dataclass(frozen=True)
class ThresholdRule:
    field_name: str
    operator: str
    threshold: float

    def matches(self, row: dict[str, Any]) -> bool:
        value = row.get(self.field_name)
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise LocalWindowEvidenceError(
                f"Expected numeric value for {self.field_name}, got {value!r}"
            )
        if self.operator == "<=":
            return float(value) <= self.threshold
        if self.operator == ">=":
            return float(value) >= self.threshold
        raise LocalWindowEvidenceError(f"Unsupported operator {self.operator!r}")

    def as_dict(self) -> dict[str, Any]:
        return {
            "field_name": self.field_name,
            "operator": self.operator,
            "threshold": _round_or_none(self.threshold),
        }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Materialize one bounded within-envelope falsifier on the exact July 2024 "
            "insufficient-evidence correction surface versus the frozen 2020 control."
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


def _coerce_float(value: Any, *, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise LocalWindowEvidenceError(f"Expected numeric value for {field_name}, got {value!r}")
    out = float(value)
    if out != out or out in {float("inf"), float("-inf")}:
        raise LocalWindowEvidenceError(f"Expected finite value for {field_name}, got {value!r}")
    return out


def _coerce_int(value: Any, *, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise LocalWindowEvidenceError(f"Expected integer value for {field_name}, got {value!r}")
    return value


def _coerce_str(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise LocalWindowEvidenceError(f"Expected non-empty string for {field_name}, got {value!r}")
    return value


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


def _value_counts(rows: list[dict[str, Any]], field_name: str) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    for row in rows:
        value = json.dumps(row[field_name], sort_keys=True)
        counts[value] = counts.get(value, 0) + 1
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [{"value": json.loads(value), "count": count} for value, count in ordered]


def _cohort_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "row_count": len(rows),
        "timestamps": [row["timestamp"] for row in rows],
        "action_pair_counts": _value_counts(rows, "action_pair"),
        "switch_reason_counts": _value_counts(rows, "switch_reason"),
        "selected_policy_counts": _value_counts(rows, "selected_policy"),
        "metric_summary": {
            field_name: _summarize_numeric_values(
                [
                    float(row[field_name])
                    for row in rows
                    if isinstance(row.get(field_name), int | float)
                ]
            )
            for field_name in SUMMARY_NUMERIC_FIELDS
        },
        "rows": rows,
    }


def _descriptive_gap(
    left_summary: dict[str, Any],
    right_summary: dict[str, Any],
    field_name: str,
) -> dict[str, float | None]:
    left_metric = left_summary["metric_summary"][field_name]
    right_metric = right_summary["metric_summary"][field_name]
    left_mean = left_metric["mean"]
    right_mean = right_metric["mean"]
    left_median = left_metric["median"]
    right_median = right_metric["median"]
    return {
        "mean_gap_left_minus_right": (
            None
            if left_mean is None or right_mean is None
            else _round_or_none(float(left_mean) - float(right_mean))
        ),
        "median_gap_left_minus_right": (
            None
            if left_median is None or right_median is None
            else _round_or_none(float(left_median) - float(right_median))
        ),
    }


def _serialize_subject_row(
    row: Any,
    *,
    cohort_name: str,
    year: str,
    candles: Any,
    timestamp_to_index: dict[Any, int],
) -> dict[str, Any]:
    serialized = {
        "cohort_name": cohort_name,
        "year": year,
        "timestamp": row.timestamp.isoformat(),
        "absent_action": _coerce_str(row.absent_action, field_name="absent_action"),
        "enabled_action": _coerce_str(row.enabled_action, field_name="enabled_action"),
        "action_pair": _coerce_str(row.action_pair, field_name="action_pair"),
        "switch_reason": _coerce_str(row.switch_reason, field_name="switch_reason"),
        "selected_policy": _coerce_str(row.selected_policy, field_name="selected_policy"),
        "raw_target_policy": _coerce_str(row.raw_target_policy, field_name="raw_target_policy"),
        "previous_policy": _coerce_str(row.previous_policy, field_name="previous_policy"),
        "zone": _coerce_str(row.zone, field_name="zone"),
        "candidate": _coerce_str(row.candidate, field_name="candidate"),
        "bars_since_regime_change": _coerce_int(
            row.bars_since_regime_change, field_name="bars_since_regime_change"
        ),
        "action_edge": _round_or_none(_coerce_float(row.action_edge, field_name="action_edge")),
        "confidence_gate": _round_or_none(
            _coerce_float(row.confidence_gate, field_name="confidence_gate")
        ),
        "clarity_score": _round_or_none(
            _coerce_float(row.clarity_score, field_name="clarity_score")
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
    candles: Any,
    timestamp_to_index: dict[Any, int],
) -> list[dict[str, Any]]:
    return [
        _serialize_subject_row(
            row,
            cohort_name=cohort_name,
            year=year,
            candles=candles,
            timestamp_to_index=timestamp_to_index,
        )
        for row in rows
    ]


def _load_year_context(year: str) -> tuple[list[Any], Any, dict[Any, int]]:
    candles, timestamp_to_index = _load_candles(CURATED_CANDLES_PATH)
    diff_path = ACTION_DIFF_ROOT / f"{year}_enabled_vs_absent_action_diffs.json"
    rows = load_subject_rows(diff_path)
    return rows, candles, timestamp_to_index


def _assert_exact_july_envelope(rows: list[Any]) -> dict[str, Any]:
    target_ts = _normalized_constant_timestamps(TARGET_TIMESTAMPS)
    start = min(target_ts) - timedelta(hours=24)
    end = max(target_ts) + timedelta(hours=24)
    local_rows = [row for row in rows if start <= row.timestamp <= end]
    if len(local_rows) != EXPECTED_JULY_ENVELOPE_COUNT:
        raise LocalWindowEvidenceError(
            "July 2024 local envelope count mismatch: "
            f"expected {EXPECTED_JULY_ENVELOPE_COUNT}, got {len(local_rows)}"
        )

    expected_all = {
        *[ts.isoformat() for ts in _normalized_constant_timestamps(TARGET_TIMESTAMPS)],
        *[ts.isoformat() for ts in _normalized_constant_timestamps(JULY_DISPLACEMENT_TIMESTAMPS)],
        *[
            ts.isoformat()
            for ts in _normalized_constant_timestamps(JULY_BLOCKED_CONTEXT_TIMESTAMPS)
        ],
    }
    actual_all = {row.timestamp.isoformat() for row in local_rows}
    if actual_all != expected_all:
        missing = sorted(expected_all - actual_all)
        extra = sorted(actual_all - expected_all)
        raise LocalWindowEvidenceError(
            "July 2024 local envelope membership mismatch; " f"missing={missing}, extra={extra}"
        )

    return {
        "envelope_start": start.isoformat(),
        "envelope_end": end.isoformat(),
        "local_row_count": len(local_rows),
        "local_row_timestamps": sorted(actual_all),
        "additional_unlabeled_rows": 0,
    }


def load_july_2024_cohorts() -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    rows, candles, timestamp_to_index = _load_year_context(TARGET_YEAR)
    envelope_metadata = _assert_exact_july_envelope(rows)

    target_rows = select_exact_rows(
        rows,
        exact_timestamps=_normalized_constant_timestamps(TARGET_TIMESTAMPS),
        expected_reason="insufficient_evidence",
        expected_action_pair=("LONG", "NONE"),
    )
    displacement_rows = select_exact_rows(
        rows,
        exact_timestamps=_normalized_constant_timestamps(JULY_DISPLACEMENT_TIMESTAMPS),
        expected_reason="stable_continuation_state",
        expected_action_pair=("NONE", "LONG"),
    )
    blocked_context_rows = select_exact_rows(
        rows,
        exact_timestamps=_normalized_constant_timestamps(JULY_BLOCKED_CONTEXT_TIMESTAMPS),
        expected_reason="stable_continuation_state",
        expected_action_pair=("LONG", "NONE"),
    )

    target_serialized = _serialize_rows(
        target_rows,
        cohort_name="july_2024_target",
        year=TARGET_YEAR,
        candles=candles,
        timestamp_to_index=timestamp_to_index,
    )
    displacement_serialized = _serialize_rows(
        displacement_rows,
        cohort_name="july_2024_nearby_displacement",
        year=TARGET_YEAR,
        candles=candles,
        timestamp_to_index=timestamp_to_index,
    )
    blocked_context_serialized = _serialize_rows(
        blocked_context_rows,
        cohort_name="july_2024_nearby_blocked_context",
        year=TARGET_YEAR,
        candles=candles,
        timestamp_to_index=timestamp_to_index,
    )
    antitarget_serialized = sorted(
        displacement_serialized + blocked_context_serialized,
        key=lambda row: row["timestamp"],
    )

    cohorts = {
        "july_2024_target": target_serialized,
        "july_2024_nearby_displacement": displacement_serialized,
        "july_2024_nearby_blocked_context": blocked_context_serialized,
        "july_2024_antitarget": antitarget_serialized,
    }
    return cohorts, envelope_metadata


def load_control_2020_cohorts() -> dict[str, list[dict[str, Any]]]:
    rows, candles, timestamp_to_index = _load_year_context(CONTROL_YEAR)

    target_rows = select_exact_rows(
        rows,
        exact_timestamps=_normalized_constant_timestamps(CONTROL_TARGET_TIMESTAMPS),
        expected_reason="insufficient_evidence",
        expected_action_pair=("LONG", "NONE"),
    )
    displacement_rows = select_exact_rows(
        rows,
        exact_timestamps=_normalized_constant_timestamps(CONTROL_DISPLACEMENT_TIMESTAMPS),
        expected_reason="stable_continuation_state",
        expected_action_pair=("NONE", "LONG"),
    )
    blocked_context_rows = select_exact_rows(
        rows,
        exact_timestamps=_normalized_constant_timestamps(CONTROL_BLOCKED_CONTEXT_TIMESTAMPS),
        expected_reason="stable_continuation_state",
        expected_action_pair=("LONG", "NONE"),
    )

    return {
        "control_2020_target": _serialize_rows(
            target_rows,
            cohort_name="control_2020_target",
            year=CONTROL_YEAR,
            candles=candles,
            timestamp_to_index=timestamp_to_index,
        ),
        "control_2020_nearby_displacement": _serialize_rows(
            displacement_rows,
            cohort_name="control_2020_nearby_displacement",
            year=CONTROL_YEAR,
            candles=candles,
            timestamp_to_index=timestamp_to_index,
        ),
        "control_2020_nearby_blocked_context": _serialize_rows(
            blocked_context_rows,
            cohort_name="control_2020_nearby_blocked_context",
            year=CONTROL_YEAR,
            candles=candles,
            timestamp_to_index=timestamp_to_index,
        ),
    }


def _bounded_selectivity_score(
    target_selection_rate: float | None,
    antitarget_selection_rate: float | None,
    control_selection_rate: float | None,
) -> float | None:
    if (
        target_selection_rate is None
        or antitarget_selection_rate is None
        or control_selection_rate is None
    ):
        return None
    return _round_or_none(
        (
            float(target_selection_rate)
            + (1.0 - float(antitarget_selection_rate))
            + (1.0 - float(control_selection_rate))
        )
        / 3.0
    )


def _truth_surface_check(cohort_summaries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    target_mean = cohort_summaries["july_2024_target"]["metric_summary"]["fwd_16_close_return_pct"][
        "mean"
    ]
    control_mean = cohort_summaries["control_2020_target"]["metric_summary"][
        "fwd_16_close_return_pct"
    ]["mean"]
    target_positive = bool(target_mean is not None and float(target_mean) > 0.0)
    control_negative = bool(control_mean is not None and float(control_mean) < 0.0)
    target_exceeds_control = bool(
        target_mean is not None
        and control_mean is not None
        and float(target_mean) > float(control_mean)
    )
    return {
        "july_2024_target_fwd16_mean": target_mean,
        "control_2020_target_fwd16_mean": control_mean,
        "july_2024_target_positive_on_fwd16_mean": target_positive,
        "control_2020_target_negative_on_fwd16_mean": control_negative,
        "july_2024_target_exceeds_control_2020_on_fwd16_mean": target_exceeds_control,
        "truth_surface_is_opposed": target_positive and control_negative and target_exceeds_control,
    }


def _selection_summary(
    rows: list[dict[str, Any]], selected_rows: list[dict[str, Any]]
) -> dict[str, Any]:
    row_count = len(rows)
    selected_count = len(selected_rows)
    return {
        "row_count": row_count,
        "selected_count": selected_count,
        "selection_rate": (None if row_count == 0 else _round_or_none(selected_count / row_count)),
        "selected_timestamps": [row["timestamp"] for row in selected_rows],
    }


def _evaluate_rules(
    rules: list[tuple[ThresholdRule, ...]],
    *,
    cohorts: dict[str, list[dict[str, Any]]],
    stage: str,
) -> list[dict[str, Any]]:
    evaluations: list[dict[str, Any]] = []
    for rule_group in rules:
        selection_by_cohort: dict[str, dict[str, Any]] = {}
        for cohort_name, cohort_rows in cohorts.items():
            selected_rows = [
                row for row in cohort_rows if all(rule.matches(row) for rule in rule_group)
            ]
            selection_by_cohort[cohort_name] = _selection_summary(cohort_rows, selected_rows)

        target_rate = selection_by_cohort["july_2024_target"]["selection_rate"]
        antitarget_rate = selection_by_cohort["july_2024_antitarget"]["selection_rate"]
        control_rate = selection_by_cohort["control_2020_target"]["selection_rate"]
        survives = bool(
            target_rate is not None
            and antitarget_rate is not None
            and control_rate is not None
            and float(target_rate) >= REQUIRED_TARGET_SELECTION_RATE
            and float(antitarget_rate) <= MAX_ANTITARGET_SELECTION_RATE
            and float(control_rate) <= MAX_CONTROL_SELECTION_RATE
        )
        evaluations.append(
            {
                "stage": stage,
                "rules": [rule.as_dict() for rule in rule_group],
                "rule_count": len(rule_group),
                "selection_by_cohort": selection_by_cohort,
                "target_selection_rate": target_rate,
                "antitarget_selection_rate": antitarget_rate,
                "control_selection_rate": control_rate,
                "bounded_selectivity_score": _bounded_selectivity_score(
                    target_rate,
                    antitarget_rate,
                    control_rate,
                ),
                "survives": survives,
            }
        )

    return sorted(
        evaluations,
        key=lambda item: (
            0 if item["survives"] else 1,
            -float(item["bounded_selectivity_score"] or 0.0),
            float(item["antitarget_selection_rate"] or 1.0),
            float(item["control_selection_rate"] or 1.0),
            -float(item["target_selection_rate"] or 0.0),
            item["rule_count"],
            json.dumps(item["rules"], sort_keys=True),
        ),
    )


def _build_single_field_rules(rows: list[dict[str, Any]]) -> list[tuple[ThresholdRule, ...]]:
    rules: list[tuple[ThresholdRule, ...]] = []
    for field_name in CANDIDATE_FIELDS:
        unique_values = sorted(
            {float(row[field_name]) for row in rows if isinstance(row.get(field_name), int | float)}
        )
        for value in unique_values:
            for operator in NUMERIC_OPERATORS:
                rules.append(
                    (ThresholdRule(field_name=field_name, operator=operator, threshold=value),)
                )
    return rules


def _build_two_field_rules(
    single_field_rules: list[tuple[ThresholdRule, ...]],
) -> list[tuple[ThresholdRule, ...]]:
    pair_rules: list[tuple[ThresholdRule, ...]] = []
    flattened = [rule_group[0] for rule_group in single_field_rules]
    for index, first_rule in enumerate(flattened):
        for second_rule in flattened[index + 1 :]:
            if first_rule.field_name == second_rule.field_name:
                continue
            pair_rules.append((first_rule, second_rule))
    return pair_rules


def _find_rule_evaluation(
    evaluations: list[dict[str, Any]], *, field_name: str, operator: str, threshold: float
) -> dict[str, Any] | None:
    for evaluation in evaluations:
        rules = evaluation["rules"]
        if len(rules) != 1:
            continue
        rule = rules[0]
        if (
            rule["field_name"] == field_name
            and rule["operator"] == operator
            and float(rule["threshold"]) == threshold
        ):
            return evaluation
    return None


def run_within_envelope_falsifier(base_sha: str) -> dict[str, Any]:
    july_2024_cohorts, july_envelope = load_july_2024_cohorts()
    control_2020_cohorts = load_control_2020_cohorts()
    cohorts = {**july_2024_cohorts, **control_2020_cohorts}

    cohort_summaries = {cohort_name: _cohort_summary(rows) for cohort_name, rows in cohorts.items()}
    truth_surface = _truth_surface_check(cohort_summaries)

    active_search_rows = (
        cohorts["july_2024_target"]
        + cohorts["july_2024_antitarget"]
        + cohorts["control_2020_target"]
    )
    single_field_rules = _build_single_field_rules(active_search_rows)
    single_field_evaluations = _evaluate_rules(
        single_field_rules,
        cohorts=cohorts,
        stage="single_field_inequality",
    )
    inherited_candidate = _find_rule_evaluation(
        single_field_evaluations,
        field_name="bars_since_regime_change",
        operator="<=",
        threshold=166.0,
    )
    surviving_single_field = [item for item in single_field_evaluations if item["survives"]]

    two_field_evaluations: list[dict[str, Any]] = []
    surviving_two_field: list[dict[str, Any]] = []
    best_surviving_candidate: dict[str, Any] | None = None
    descriptive_best_candidate = single_field_evaluations[0] if single_field_evaluations else None

    if not truth_surface["truth_surface_is_opposed"]:
        result_state = "truth_surface_prerequisite_failed"
    elif surviving_single_field:
        result_state = "bounded_within_envelope_single_field_survivor"
        best_surviving_candidate = surviving_single_field[0]
    else:
        two_field_rules = _build_two_field_rules(single_field_rules)
        two_field_evaluations = _evaluate_rules(
            two_field_rules,
            cohorts=cohorts,
            stage="ordered_two_field_inequality",
        )
        surviving_two_field = [item for item in two_field_evaluations if item["survives"]]
        if surviving_two_field:
            result_state = "bounded_within_envelope_two_field_survivor"
            best_surviving_candidate = surviving_two_field[0]
        else:
            result_state = "envelope_only_no_survivor"

    return {
        "audit_version": (
            "ri-policy-router-insufficient-evidence-july-2024-within-envelope-falsifier-2026-05-04"
        ),
        "base_sha": base_sha,
        "status": result_state,
        "observational_only": True,
        "non_authoritative": True,
        "subject": {
            "symbol": SUBJECT_SYMBOL,
            "timeframe": SUBJECT_TIMEFRAME,
            "target_year": TARGET_YEAR,
            "control_year": CONTROL_YEAR,
            "packet_reference": str(PACKET_REFERENCE),
            "baseline_reference": str(BASELINE_REFERENCE),
        },
        "skill_usage": ["python_engineering"],
        "fail_closed_contract": {
            "statement": (
                "Inputs are restricted to the exact July 2024 target rows, the exact July 2024 "
                "anti-target rows, the frozen 2020 control rows, and the frozen 2020 nearby "
                "descriptive rows on the annual action-diff surface plus curated candles for "
                "observational metrics only. Equality matching, selector/count drift, truth-"
                "surface failure, or widening beyond ordered one-field and two-field inequality "
                "screens is FAIL, and nearby descriptive rows cannot rescue acceptance."
            )
        },
        "candidate_screen_contract": {
            "candidate_fields": list(CANDIDATE_FIELDS),
            "operators": list(NUMERIC_OPERATORS),
            "single_field_first": True,
            "two_field_only_if_no_single_field_survives": True,
            "equality_matching_forbidden": True,
            "truth_surface_prerequisite": (
                "The fixed July 2024 target side must remain positive on mean fwd_16, the fixed "
                "2020 control side must remain negative on mean fwd_16, and the July 2024 target "
                "mean must exceed the 2020 control mean; otherwise no candidate survives."
            ),
            "survival_rule": {
                "required_target_selection_rate": REQUIRED_TARGET_SELECTION_RATE,
                "max_july_antitarget_selection_rate": MAX_ANTITARGET_SELECTION_RATE,
                "max_control_2020_selection_rate": MAX_CONTROL_SELECTION_RATE,
            },
        },
        "inputs": {
            "action_diff_root": str(ACTION_DIFF_ROOT_RELATIVE),
            "target_2024_diff": str(
                ACTION_DIFF_ROOT_RELATIVE / f"{TARGET_YEAR}_enabled_vs_absent_action_diffs.json"
            ),
            "control_2020_diff": str(
                ACTION_DIFF_ROOT_RELATIVE / f"{CONTROL_YEAR}_enabled_vs_absent_action_diffs.json"
            ),
            "curated_candles": str(CURATED_CANDLES_RELATIVE),
        },
        "artifact_row_lock": {
            "july_2024_target_timestamps": [
                _normalize_timestamp(value).isoformat() for value in TARGET_TIMESTAMPS
            ],
            "july_2024_nearby_displacement_timestamps": [
                _normalize_timestamp(value).isoformat() for value in JULY_DISPLACEMENT_TIMESTAMPS
            ],
            "july_2024_nearby_blocked_context_timestamps": [
                _normalize_timestamp(value).isoformat() for value in JULY_BLOCKED_CONTEXT_TIMESTAMPS
            ],
            "control_2020_target_timestamps": [
                _normalize_timestamp(value).isoformat() for value in CONTROL_TARGET_TIMESTAMPS
            ],
            "control_2020_nearby_displacement_timestamps": [
                _normalize_timestamp(value).isoformat() for value in CONTROL_DISPLACEMENT_TIMESTAMPS
            ],
            "control_2020_nearby_blocked_context_timestamps": [
                _normalize_timestamp(value).isoformat()
                for value in CONTROL_BLOCKED_CONTEXT_TIMESTAMPS
            ],
            "july_2024_envelope": july_envelope,
        },
        "cohorts": cohort_summaries,
        "truth_surface_check": truth_surface,
        "descriptive_comparison": {
            "target_vs_july_displacement": _descriptive_gap(
                cohort_summaries["july_2024_target"],
                cohort_summaries["july_2024_nearby_displacement"],
                "fwd_16_close_return_pct",
            ),
            "target_vs_july_blocked_context": _descriptive_gap(
                cohort_summaries["july_2024_target"],
                cohort_summaries["july_2024_nearby_blocked_context"],
                "fwd_16_close_return_pct",
            ),
            "target_vs_july_antitarget": _descriptive_gap(
                cohort_summaries["july_2024_target"],
                cohort_summaries["july_2024_antitarget"],
                "fwd_16_close_return_pct",
            ),
            "target_vs_control_2020": _descriptive_gap(
                cohort_summaries["july_2024_target"],
                cohort_summaries["control_2020_target"],
                "fwd_16_close_return_pct",
            ),
        },
        "candidate_search": {
            "single_field_evaluated_count": len(single_field_evaluations),
            "single_field_ranked": single_field_evaluations[:20],
            "two_field_evaluated_count": len(two_field_evaluations),
            "two_field_ranked": two_field_evaluations[:20],
            "inherited_candidate": inherited_candidate,
            "best_surviving_candidate": best_surviving_candidate,
            "best_descriptive_candidate": descriptive_best_candidate,
        },
    }


def main() -> int:
    args = _parse_args()
    output_root = ROOT_DIR / Path(args.output_root_relative)
    output_json = output_root / args.summary_filename
    result = run_within_envelope_falsifier(base_sha=args.base_sha)

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "summary_artifact": str(output_json),
                "status": result["status"],
                "inherited_candidate": result["candidate_search"]["inherited_candidate"],
                "best_surviving_candidate": result["candidate_search"]["best_surviving_candidate"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
