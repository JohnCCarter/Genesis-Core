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
    _normalize_timestamp,
    _normalized_constant_timestamps,
    _row_observational_metrics,
    load_subject_rows,
    select_exact_rows,
)

OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = (
    "ri_policy_router_insufficient_evidence_2022_06_weak_signal_holdout_2026-05-04.json"
)
SUBJECT_SYMBOL = "tBTCUSD"
SUBJECT_TIMEFRAME = "3h"
SUBJECT_YEAR = "2022"
PACKET_REFERENCE = Path(
    "docs/decisions/regime_intelligence/policy_router/"
    "ri_policy_router_insufficient_evidence_2022_06_weak_signal_holdout_precode_packet_2026-05-04.md"
)
JULY_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_insufficient_evidence_july_2024_within_envelope_falsifier_2026-05-04.md"
)
LATE_2024_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_insufficient_evidence_late_2024_recurrence_falsifier_2026-05-04.md"
)
TARGET_TIMESTAMPS = (
    "2022-06-24T03:00:00+00:00",
    "2022-06-24T21:00:00+00:00",
    "2022-06-25T06:00:00+00:00",
    "2022-06-25T15:00:00+00:00",
    "2022-06-26T00:00:00+00:00",
)
STABLE_DISPLACEMENT_TIMESTAMPS = (
    "2022-06-23T03:00:00+00:00",
    "2022-06-23T12:00:00+00:00",
)
STABLE_BLOCKED_CONTEXT_TIMESTAMPS = (
    "2022-06-23T09:00:00+00:00",
    "2022-06-23T18:00:00+00:00",
)
EXPECTED_TARGET_COUNT = 5
EXPECTED_ANTI_TARGET_COUNT = 4
EXPECTED_TOTAL_COUNT = 9
OFFLINE_METRIC_FIELDS = (
    "fwd_4_close_return_pct",
    "fwd_8_close_return_pct",
    "fwd_16_close_return_pct",
    "mfe_16_pct",
    "mae_16_pct",
)
SUMMARY_NUMERIC_FIELDS = (
    "bars_since_regime_change",
    "action_edge",
    "confidence_gate",
    "clarity_score",
    *OFFLINE_METRIC_FIELDS,
)
TRANSPORT_REQUIRED_TARGET_SELECTION_COUNT = 4
TRANSPORT_MAX_ANTI_TARGET_SELECTION_COUNT = 1


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
        raise LocalWindowEvidenceError(f"Unsupported operator {self.operator!r}")

    def as_dict(self) -> dict[str, Any]:
        return {
            "field_name": self.field_name,
            "operator": self.operator,
            "threshold": _round_or_none(self.threshold),
        }


@dataclass(frozen=True)
class RuleVariant:
    variant_id: str
    label: str
    rules: tuple[ThresholdRule, ...]

    def matches(self, row: dict[str, Any]) -> bool:
        return all(rule.matches(row) for rule in self.rules)

    def as_dict(self) -> dict[str, Any]:
        return {
            "variant_id": self.variant_id,
            "label": self.label,
            "rules": [rule.as_dict() for rule in self.rules],
        }


TRANSPORT_VARIANTS = (
    RuleVariant(
        variant_id="transport_action_edge",
        label="bars<=166_and_action_edge<=0.034334",
        rules=(
            ThresholdRule("bars_since_regime_change", "<=", 166.0),
            ThresholdRule("action_edge", "<=", 0.034334),
        ),
    ),
    RuleVariant(
        variant_id="transport_confidence_gate",
        label="bars<=166_and_confidence_gate<=0.517167",
        rules=(
            ThresholdRule("bars_since_regime_change", "<=", 166.0),
            ThresholdRule("confidence_gate", "<=", 0.517167),
        ),
    ),
    RuleVariant(
        variant_id="transport_clarity_score",
        label="bars<=166_and_clarity_score<=37",
        rules=(
            ThresholdRule("bars_since_regime_change", "<=", 166.0),
            ThresholdRule("clarity_score", "<=", 37.0),
        ),
    ),
)

WEAK_SIGNAL_VARIANTS = (
    RuleVariant(
        variant_id="weak_signal_action_edge",
        label="action_edge<=0.034334",
        rules=(ThresholdRule("action_edge", "<=", 0.034334),),
    ),
    RuleVariant(
        variant_id="weak_signal_confidence_gate",
        label="confidence_gate<=0.517167",
        rules=(ThresholdRule("confidence_gate", "<=", 0.517167),),
    ),
    RuleVariant(
        variant_id="weak_signal_clarity_score",
        label="clarity_score<=37",
        rules=(ThresholdRule("clarity_score", "<=", 37.0),),
    ),
    RuleVariant(
        variant_id="weak_signal_three_way_intersection",
        label="action_edge<=0.034334_and_confidence_gate<=0.517167_and_clarity_score<=37",
        rules=(
            ThresholdRule("action_edge", "<=", 0.034334),
            ThresholdRule("confidence_gate", "<=", 0.517167),
            ThresholdRule("clarity_score", "<=", 37.0),
        ),
    ),
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Materialize one bounded 2022-06 weak-signal holdout using the exact five-row "
            "insufficient-evidence target cluster and the fixed four-row stable anti-target "
            "surface from the 2022 annual action-diff evidence."
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


def _assert_exact_2022_06_envelope(rows: list[Any]) -> dict[str, Any]:
    expected_all = {
        *[ts.isoformat() for ts in _normalized_constant_timestamps(TARGET_TIMESTAMPS)],
        *[ts.isoformat() for ts in _normalized_constant_timestamps(STABLE_DISPLACEMENT_TIMESTAMPS)],
        *[
            ts.isoformat()
            for ts in _normalized_constant_timestamps(STABLE_BLOCKED_CONTEXT_TIMESTAMPS)
        ],
    }
    start = min(_normalize_timestamp(value) for value in expected_all)
    end = max(_normalize_timestamp(value) for value in expected_all)
    local_rows = [row for row in rows if start <= row.timestamp <= end]
    if len(local_rows) != EXPECTED_TOTAL_COUNT:
        raise LocalWindowEvidenceError(
            f"2022-06 local envelope count mismatch: expected {EXPECTED_TOTAL_COUNT}, got {len(local_rows)}"
        )

    actual_all = {row.timestamp.isoformat() for row in local_rows}
    if actual_all != expected_all:
        missing = sorted(expected_all - actual_all)
        extra = sorted(actual_all - expected_all)
        raise LocalWindowEvidenceError(
            f"2022-06 local envelope membership mismatch; missing={missing}, extra={extra}"
        )

    return {
        "envelope_start": start.isoformat(),
        "envelope_end": end.isoformat(),
        "local_row_count": len(local_rows),
        "local_row_timestamps": sorted(actual_all),
        "additional_unlabeled_rows": 0,
    }


def load_2022_06_surface() -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    candles, timestamp_to_index = _load_candles(CURATED_CANDLES_PATH)
    diff_path = ACTION_DIFF_ROOT / f"{SUBJECT_YEAR}_enabled_vs_absent_action_diffs.json"
    rows = load_subject_rows(diff_path)
    envelope_metadata = _assert_exact_2022_06_envelope(rows)

    target_rows = select_exact_rows(
        rows,
        exact_timestamps=_normalized_constant_timestamps(TARGET_TIMESTAMPS),
        expected_reason="insufficient_evidence",
        expected_action_pair=("LONG", "NONE"),
    )
    stable_displacement_rows = select_exact_rows(
        rows,
        exact_timestamps=_normalized_constant_timestamps(STABLE_DISPLACEMENT_TIMESTAMPS),
        expected_reason="stable_continuation_state",
        expected_action_pair=("NONE", "LONG"),
    )
    stable_blocked_context_rows = select_exact_rows(
        rows,
        exact_timestamps=_normalized_constant_timestamps(STABLE_BLOCKED_CONTEXT_TIMESTAMPS),
        expected_reason="stable_continuation_state",
        expected_action_pair=("LONG", "NONE"),
    )

    target_serialized = _serialize_rows(
        target_rows,
        cohort_name="holdout_2022_06_target",
        year=SUBJECT_YEAR,
        candles=candles,
        timestamp_to_index=timestamp_to_index,
    )
    stable_displacement_serialized = _serialize_rows(
        stable_displacement_rows,
        cohort_name="holdout_2022_06_stable_displacement",
        year=SUBJECT_YEAR,
        candles=candles,
        timestamp_to_index=timestamp_to_index,
    )
    stable_blocked_context_serialized = _serialize_rows(
        stable_blocked_context_rows,
        cohort_name="holdout_2022_06_stable_blocked_context",
        year=SUBJECT_YEAR,
        candles=candles,
        timestamp_to_index=timestamp_to_index,
    )
    antitarget_serialized = sorted(
        stable_displacement_serialized + stable_blocked_context_serialized,
        key=lambda row: row["timestamp"],
    )
    full_surface_serialized = sorted(
        target_serialized + antitarget_serialized,
        key=lambda row: row["timestamp"],
    )

    if len(target_serialized) != EXPECTED_TARGET_COUNT:
        raise LocalWindowEvidenceError(
            f"Expected {EXPECTED_TARGET_COUNT} target rows, got {len(target_serialized)}"
        )
    if len(antitarget_serialized) != EXPECTED_ANTI_TARGET_COUNT:
        raise LocalWindowEvidenceError(
            f"Expected {EXPECTED_ANTI_TARGET_COUNT} anti-target rows, got {len(antitarget_serialized)}"
        )
    if len(full_surface_serialized) != EXPECTED_TOTAL_COUNT:
        raise LocalWindowEvidenceError(
            f"Expected {EXPECTED_TOTAL_COUNT} total rows, got {len(full_surface_serialized)}"
        )

    return (
        {
            "holdout_2022_06_target": target_serialized,
            "holdout_2022_06_stable_displacement": stable_displacement_serialized,
            "holdout_2022_06_stable_blocked_context": stable_blocked_context_serialized,
            "holdout_2022_06_antitarget": antitarget_serialized,
            "holdout_2022_06_full_surface": full_surface_serialized,
        },
        {
            "target_count": len(target_serialized),
            "antitarget_count": len(antitarget_serialized),
            "total_count": len(full_surface_serialized),
            "target_timestamps": [row["timestamp"] for row in target_serialized],
            "antitarget_timestamps": [row["timestamp"] for row in antitarget_serialized],
            "full_surface_timestamps": [row["timestamp"] for row in full_surface_serialized],
            "additional_unlabeled_rows": envelope_metadata["additional_unlabeled_rows"],
            "envelope": envelope_metadata,
        },
    )


def _evaluate_variant(
    variant: RuleVariant,
    *,
    cohorts: dict[str, list[dict[str, Any]]],
    descriptive_only: bool,
) -> dict[str, Any]:
    selection_by_cohort: dict[str, dict[str, Any]] = {}
    for cohort_name, cohort_rows in cohorts.items():
        selected_rows = [row for row in cohort_rows if variant.matches(row)]
        selection_by_cohort[cohort_name] = _selection_summary(cohort_rows, selected_rows)

    target_count = selection_by_cohort["holdout_2022_06_target"]["selected_count"]
    anti_target_count = selection_by_cohort["holdout_2022_06_antitarget"]["selected_count"]
    transport_survives = bool(
        not descriptive_only
        and target_count >= TRANSPORT_REQUIRED_TARGET_SELECTION_COUNT
        and anti_target_count <= TRANSPORT_MAX_ANTI_TARGET_SELECTION_COUNT
    )

    return {
        **variant.as_dict(),
        "selection_by_cohort": selection_by_cohort,
        "selected_target_count": target_count,
        "selected_antitarget_count": anti_target_count,
        "transport_survives": transport_survives,
        "descriptive_only": descriptive_only,
    }


def _sorted_transport_evaluations(evaluations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        evaluations,
        key=lambda item: (
            0 if item["transport_survives"] else 1,
            -int(item["selected_target_count"]),
            int(item["selected_antitarget_count"]),
            item["variant_id"],
        ),
    )


def _sorted_weak_signal_evaluations(evaluations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        evaluations,
        key=lambda item: (
            -int(item["selected_target_count"]),
            int(item["selected_antitarget_count"]),
            item["variant_id"],
        ),
    )


def run_2022_06_weak_signal_holdout(base_sha: str) -> dict[str, Any]:
    cohorts, row_lock = load_2022_06_surface()
    cohort_summaries = {cohort_name: _cohort_summary(rows) for cohort_name, rows in cohorts.items()}

    transport_evaluations = _sorted_transport_evaluations(
        [
            _evaluate_variant(variant, cohorts=cohorts, descriptive_only=False)
            for variant in TRANSPORT_VARIANTS
        ]
    )
    weak_signal_evaluations = _sorted_weak_signal_evaluations(
        [
            _evaluate_variant(variant, cohorts=cohorts, descriptive_only=True)
            for variant in WEAK_SIGNAL_VARIANTS
        ]
    )

    best_transport_variant = next(
        (evaluation for evaluation in transport_evaluations if evaluation["transport_survives"]),
        None,
    )
    best_weak_signal_variant = weak_signal_evaluations[0] if weak_signal_evaluations else None
    status = "transport_survivor" if best_transport_variant is not None else "transport_falsified"

    return {
        "audit_version": "ri-policy-router-insufficient-evidence-2022-06-weak-signal-holdout-2026-05-04",
        "base_sha": base_sha,
        "status": status,
        "observational_only": True,
        "non_authoritative": True,
        "subject": {
            "symbol": SUBJECT_SYMBOL,
            "timeframe": SUBJECT_TIMEFRAME,
            "year": SUBJECT_YEAR,
            "packet_reference": str(PACKET_REFERENCE),
            "july_reference": str(JULY_REFERENCE),
            "late_2024_reference": str(LATE_2024_REFERENCE),
        },
        "skill_usage": ["python_engineering"],
        "fail_closed_contract": {
            "statement": (
                "The helper reads only the existing 2022 annual enabled-vs-absent action-diff surface plus curated candles, aborts on any 5/4/9 selector drift, evaluates only the three fixed July transport variants plus the fixed weak-signal holdout variants, and treats weak-signal recurrence as descriptive only that cannot rescue a failed transport result."
            )
        },
        "transport_rubric": {
            "required_target_selection_count": TRANSPORT_REQUIRED_TARGET_SELECTION_COUNT,
            "target_row_count": EXPECTED_TARGET_COUNT,
            "max_antitarget_selection_count": TRANSPORT_MAX_ANTI_TARGET_SELECTION_COUNT,
            "antitarget_row_count": EXPECTED_ANTI_TARGET_COUNT,
            "statement": (
                "The 4/5 target and 1/4 anti-target rubric is a slice-local observational transport rubric only; it is not a proposed screening threshold."
            ),
        },
        "inputs": {
            "action_diff_root": str(ACTION_DIFF_ROOT_RELATIVE),
            "source_diff": str(
                ACTION_DIFF_ROOT_RELATIVE / f"{SUBJECT_YEAR}_enabled_vs_absent_action_diffs.json"
            ),
            "curated_candles": str(CURATED_CANDLES_RELATIVE),
        },
        "artifact_row_lock": row_lock,
        "cohorts": cohort_summaries,
        "transport_variants": [variant.as_dict() for variant in TRANSPORT_VARIANTS],
        "transport_evaluations": transport_evaluations,
        "best_transport_variant": best_transport_variant,
        "weak_signal_holdout": {
            "descriptive_only": True,
            "statement": (
                "Weak-signal holdout counts are descriptive only, cannot rescue a failed transport result, and do not authorize new thresholds, new fields, runtime/default changes, or promotion claims."
            ),
            "variants": [variant.as_dict() for variant in WEAK_SIGNAL_VARIANTS],
            "evaluations": weak_signal_evaluations,
            "best_descriptive_variant": best_weak_signal_variant,
        },
    }


def main() -> int:
    args = _parse_args()
    output_root = ROOT_DIR / Path(args.output_root_relative)
    output_json = output_root / args.summary_filename
    result = run_2022_06_weak_signal_holdout(base_sha=args.base_sha)

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "summary_artifact": str(output_json),
                "status": result["status"],
                "best_transport_variant": result["best_transport_variant"],
                "best_weak_signal_variant": result["weak_signal_holdout"][
                    "best_descriptive_variant"
                ],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
