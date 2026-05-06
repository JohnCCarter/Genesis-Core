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
    ROOT_DIR,
    LocalWindowEvidenceError,
    _load_json,
    _normalize_timestamp,
)

OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = (
    "ri_policy_router_insufficient_evidence_d1_late_2024_external_surface_falsifier_"
    "2026-05-06.json"
)
CONTEXT_CLEAN_ARTIFACT_RELATIVE = Path(
    "results/evaluation/"
    "ri_policy_router_insufficient_evidence_d1_context_clean_selectivity_falsifier_"
    "2026-05-05.json"
)
LATE_2024_SOURCE_ARTIFACT_RELATIVE = Path(
    "results/evaluation/ri_policy_router_2024_regression_pocket_isolation_2026-04-30.json"
)
PACKET_REFERENCE = Path(
    "docs/decisions/regime_intelligence/policy_router/"
    "ri_policy_router_insufficient_evidence_d1_late_2024_external_surface_falsifier_"
    "precode_packet_2026-05-06.md"
)
CONTEXT_CLEAN_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_insufficient_evidence_d1_context_clean_selectivity_falsifier_"
    "2026-05-05.md"
)
LATE_2024_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_insufficient_evidence_late_2024_recurrence_falsifier_2026-05-04.md"
)
REASON_SPLIT_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_2024_regression_pocket_reason_split_2026-04-30.md"
)
WORKING_CONTRACT_REFERENCE = Path("GENESIS_WORKING_CONTRACT.md")
SUBJECT_SYMBOL = "tBTCUSD"
SUBJECT_TIMEFRAME = "3h"
SUBJECT_YEAR = "2024"
TARGET_TIMESTAMPS = (
    "2024-11-29T09:00:00+00:00",
    "2024-11-29T18:00:00+00:00",
    "2024-11-30T03:00:00+00:00",
    "2024-12-01T15:00:00+00:00",
    "2024-12-02T00:00:00+00:00",
)
AGED_WEAK_SIBLING_TIMESTAMPS = (
    "2024-11-28T15:00:00+00:00",
    "2024-11-29T00:00:00+00:00",
    "2024-11-30T12:00:00+00:00",
    "2024-11-30T21:00:00+00:00",
)
STABLE_DISPLACEMENT_TIMESTAMPS = ("2024-12-01T00:00:00+00:00",)
STABLE_BLOCKED_CONTEXT_TIMESTAMPS = ("2024-12-01T06:00:00+00:00",)
EXPECTED_TARGET_COUNT = 5
EXPECTED_ANTITARGET_COUNT = 6
EXPECTED_TOTAL_COUNT = 11
EXPECTED_REGRESSION_TARGET_COUNT = 9
EXPECTED_COMPARISON_COUNT = 1
EXPECTED_STABLE_CONTEXT_COUNT = 1
EXPECTED_REASON_COUNTS = {
    "AGED_WEAK_CONTINUATION_GUARD": 4,
    "insufficient_evidence": 5,
}
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
    "clarity_raw",
    "clarity_score",
    *OFFLINE_METRIC_FIELDS,
)


@dataclass(frozen=True)
class FieldTransportDefinition:
    field_name: str
    descriptive_only: bool


FIELD_TRANSPORT_DEFINITIONS = (
    FieldTransportDefinition(field_name="action_edge", descriptive_only=False),
    FieldTransportDefinition(field_name="confidence_gate", descriptive_only=False),
    FieldTransportDefinition(field_name="clarity_raw", descriptive_only=False),
    FieldTransportDefinition(field_name="clarity_score", descriptive_only=True),
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Materialize one exact late-2024 external-surface falsifier by transporting the "
            "fixed D1 bank ceilings from the completed context-clean bank reread."
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


def _coerce_optional_float(value: Any, *, field_name: str) -> float | None:
    if value is None:
        return None
    return _round_or_none(_coerce_float(value, field_name=field_name))


def _coerce_int(value: Any, *, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise LocalWindowEvidenceError(f"Expected integer value for {field_name}, got {value!r}")
    return value


def _coerce_str(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise LocalWindowEvidenceError(f"Expected non-empty string for {field_name}, got {value!r}")
    return value


def _coerce_str_list(value: Any, *, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise LocalWindowEvidenceError(f"Expected list for {field_name}, got {value!r}")
    return [_coerce_str(item, field_name=field_name) for item in value]


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


def _field_admission(rows: list[dict[str, Any]], field_name: str) -> dict[str, Any]:
    missing_timestamps = [
        row["timestamp"]
        for row in rows
        if isinstance(row.get(field_name), bool) or not isinstance(row.get(field_name), int | float)
    ]
    return {
        "status": "evaluable" if not missing_timestamps else "missing",
        "missing_timestamps": missing_timestamps,
        "row_count_checked": len(rows),
    }


def _normalize_external_row(row: dict[str, Any], *, cohort_name: str) -> dict[str, Any]:
    required_fields = (
        "timestamp",
        "absent_action",
        "enabled_action",
        "action_pair",
        "switch_reason",
        "selected_policy",
        "raw_target_policy",
        "previous_policy",
        "zone",
        "candidate",
        "bars_since_regime_change",
        "action_edge",
        "confidence_gate",
        "clarity_score",
        *OFFLINE_METRIC_FIELDS,
    )
    missing = [field_name for field_name in required_fields if field_name not in row]
    if missing:
        raise LocalWindowEvidenceError(f"Artifact row is missing required fields: {missing}")

    return {
        "cohort_name": cohort_name,
        "year": SUBJECT_YEAR,
        "timestamp": _normalize_timestamp(row["timestamp"]).isoformat(),
        "absent_action": _coerce_str(row["absent_action"], field_name="absent_action"),
        "enabled_action": _coerce_str(row["enabled_action"], field_name="enabled_action"),
        "action_pair": _coerce_str(row["action_pair"], field_name="action_pair"),
        "switch_reason": _coerce_str(row["switch_reason"], field_name="switch_reason"),
        "selected_policy": _coerce_str(row["selected_policy"], field_name="selected_policy"),
        "raw_target_policy": _coerce_str(row["raw_target_policy"], field_name="raw_target_policy"),
        "previous_policy": _coerce_str(row["previous_policy"], field_name="previous_policy"),
        "zone": _coerce_str(row["zone"], field_name="zone"),
        "candidate": _coerce_str(row["candidate"], field_name="candidate"),
        "bars_since_regime_change": _coerce_int(
            row["bars_since_regime_change"], field_name="bars_since_regime_change"
        ),
        "action_edge": _round_or_none(_coerce_float(row["action_edge"], field_name="action_edge")),
        "confidence_gate": _round_or_none(
            _coerce_float(row["confidence_gate"], field_name="confidence_gate")
        ),
        "clarity_raw": _coerce_optional_float(row.get("clarity_raw"), field_name="clarity_raw"),
        "clarity_score": _round_or_none(
            _coerce_float(row["clarity_score"], field_name="clarity_score")
        ),
        "fwd_4_close_return_pct": _round_or_none(
            _coerce_float(row["fwd_4_close_return_pct"], field_name="fwd_4_close_return_pct")
        ),
        "fwd_8_close_return_pct": _round_or_none(
            _coerce_float(row["fwd_8_close_return_pct"], field_name="fwd_8_close_return_pct")
        ),
        "fwd_16_close_return_pct": _round_or_none(
            _coerce_float(row["fwd_16_close_return_pct"], field_name="fwd_16_close_return_pct")
        ),
        "mfe_16_pct": _round_or_none(_coerce_float(row["mfe_16_pct"], field_name="mfe_16_pct")),
        "mae_16_pct": _round_or_none(_coerce_float(row["mae_16_pct"], field_name="mae_16_pct")),
    }


def _select_exact_serialized_rows(
    rows: list[dict[str, Any]],
    *,
    exact_timestamps: tuple[str, ...],
    expected_switch_reason: str,
    expected_action_pair: tuple[str, str],
) -> list[dict[str, Any]]:
    expected_set = {_normalize_timestamp(ts).isoformat() for ts in exact_timestamps}
    matched = [row for row in rows if row["timestamp"] in expected_set]
    matched_set = {row["timestamp"] for row in matched}
    if matched_set != expected_set:
        missing = sorted(expected_set - matched_set)
        extra = sorted(matched_set - expected_set)
        raise LocalWindowEvidenceError(
            f"Exact serialized rows did not materialize cleanly; missing={missing}, extra={extra}"
        )

    invalid_rows = [
        row
        for row in matched
        if row["switch_reason"] != expected_switch_reason
        or (row["absent_action"], row["enabled_action"]) != expected_action_pair
    ]
    if invalid_rows:
        invalid_payload = [
            {
                "timestamp": row["timestamp"],
                "switch_reason": row["switch_reason"],
                "action_pair": row["action_pair"],
            }
            for row in invalid_rows
        ]
        raise LocalWindowEvidenceError(
            f"Serialized rows failed reason/action validation: {invalid_payload}"
        )
    return sorted(matched, key=lambda row: row["timestamp"])


def _validate_source_artifact_lock(payload: dict[str, Any]) -> None:
    artifact_row_lock = payload.get("artifact_row_lock")
    if not isinstance(artifact_row_lock, dict):
        raise LocalWindowEvidenceError("Source artifact is missing artifact_row_lock payload")

    if artifact_row_lock.get("target_timestamp_count") != EXPECTED_REGRESSION_TARGET_COUNT:
        raise LocalWindowEvidenceError(
            "Unexpected regression-target count in source artifact_row_lock"
        )
    if artifact_row_lock.get("comparison_timestamp_count") != EXPECTED_COMPARISON_COUNT:
        raise LocalWindowEvidenceError("Unexpected comparison count in source artifact_row_lock")
    if artifact_row_lock.get("stable_context_timestamp_count") != EXPECTED_STABLE_CONTEXT_COUNT:
        raise LocalWindowEvidenceError(
            "Unexpected stable-context count in source artifact_row_lock"
        )
    if artifact_row_lock.get("target_reason_counts") != EXPECTED_REASON_COUNTS:
        raise LocalWindowEvidenceError(
            "Unexpected target reason counts in source artifact_row_lock: "
            f"{artifact_row_lock.get('target_reason_counts')!r}"
        )


def load_late_2024_external_surface() -> (
    tuple[dict[str, list[dict[str, Any]]], dict[str, Any], dict[str, Any]]
):
    payload = _load_json(ROOT_DIR / LATE_2024_SOURCE_ARTIFACT_RELATIVE)
    if not isinstance(payload, dict):
        raise LocalWindowEvidenceError("Expected object payload in source late-2024 artifact")
    _validate_source_artifact_lock(payload)

    cohorts = payload.get("cohorts")
    if not isinstance(cohorts, dict):
        raise LocalWindowEvidenceError("Source artifact is missing cohorts payload")

    regression_target_payload = cohorts.get("regression_target")
    displacement_payload = cohorts.get("stable_continuation_displacement_comparison")
    stable_blocked_payload = cohorts.get("stable_continuation_blocked_context")
    if not isinstance(regression_target_payload, dict):
        raise LocalWindowEvidenceError("Source artifact is missing regression_target cohort")
    if not isinstance(displacement_payload, dict):
        raise LocalWindowEvidenceError(
            "Source artifact is missing stable_continuation_displacement_comparison cohort"
        )
    if not isinstance(stable_blocked_payload, dict):
        raise LocalWindowEvidenceError(
            "Source artifact is missing stable_continuation_blocked_context cohort"
        )

    regression_rows_raw = regression_target_payload.get("rows")
    displacement_rows_raw = displacement_payload.get("rows")
    stable_blocked_rows_raw = stable_blocked_payload.get("rows")
    if not isinstance(regression_rows_raw, list):
        raise LocalWindowEvidenceError("Source artifact regression_target.rows missing")
    if not isinstance(displacement_rows_raw, list):
        raise LocalWindowEvidenceError("Source artifact stable displacement rows missing")
    if not isinstance(stable_blocked_rows_raw, list):
        raise LocalWindowEvidenceError("Source artifact stable blocked context rows missing")

    regression_rows = [
        _normalize_external_row(row, cohort_name="late_2024_regression_target")
        for row in regression_rows_raw
        if isinstance(row, dict)
    ]
    displacement_rows = [
        _normalize_external_row(row, cohort_name="late_2024_stable_displacement")
        for row in displacement_rows_raw
        if isinstance(row, dict)
    ]
    stable_blocked_rows = [
        _normalize_external_row(row, cohort_name="late_2024_stable_blocked_context")
        for row in stable_blocked_rows_raw
        if isinstance(row, dict)
    ]

    target_rows = _select_exact_serialized_rows(
        regression_rows,
        exact_timestamps=TARGET_TIMESTAMPS,
        expected_switch_reason="insufficient_evidence",
        expected_action_pair=("LONG", "NONE"),
    )
    aged_weak_sibling_rows = _select_exact_serialized_rows(
        regression_rows,
        exact_timestamps=AGED_WEAK_SIBLING_TIMESTAMPS,
        expected_switch_reason="AGED_WEAK_CONTINUATION_GUARD",
        expected_action_pair=("LONG", "NONE"),
    )
    stable_displacement_rows = _select_exact_serialized_rows(
        displacement_rows,
        exact_timestamps=STABLE_DISPLACEMENT_TIMESTAMPS,
        expected_switch_reason="stable_continuation_state",
        expected_action_pair=("NONE", "LONG"),
    )
    stable_blocked_context_rows = _select_exact_serialized_rows(
        stable_blocked_rows,
        exact_timestamps=STABLE_BLOCKED_CONTEXT_TIMESTAMPS,
        expected_switch_reason="stable_continuation_state",
        expected_action_pair=("LONG", "NONE"),
    )

    antitarget_rows = sorted(
        aged_weak_sibling_rows + stable_displacement_rows + stable_blocked_context_rows,
        key=lambda row: row["timestamp"],
    )
    full_surface_rows = sorted(target_rows + antitarget_rows, key=lambda row: row["timestamp"])

    if len(target_rows) != EXPECTED_TARGET_COUNT:
        raise LocalWindowEvidenceError(
            f"Expected {EXPECTED_TARGET_COUNT} target rows, got {len(target_rows)}"
        )
    if len(antitarget_rows) != EXPECTED_ANTITARGET_COUNT:
        raise LocalWindowEvidenceError(
            f"Expected {EXPECTED_ANTITARGET_COUNT} anti-target rows, got {len(antitarget_rows)}"
        )
    if len(full_surface_rows) != EXPECTED_TOTAL_COUNT:
        raise LocalWindowEvidenceError(
            f"Expected {EXPECTED_TOTAL_COUNT} total rows, got {len(full_surface_rows)}"
        )

    expected_surface = {
        *[_normalize_timestamp(ts).isoformat() for ts in TARGET_TIMESTAMPS],
        *[_normalize_timestamp(ts).isoformat() for ts in AGED_WEAK_SIBLING_TIMESTAMPS],
        *[_normalize_timestamp(ts).isoformat() for ts in STABLE_DISPLACEMENT_TIMESTAMPS],
        *[_normalize_timestamp(ts).isoformat() for ts in STABLE_BLOCKED_CONTEXT_TIMESTAMPS],
    }
    actual_surface = {row["timestamp"] for row in full_surface_rows}
    if actual_surface != expected_surface:
        missing = sorted(expected_surface - actual_surface)
        extra = sorted(actual_surface - expected_surface)
        raise LocalWindowEvidenceError(
            f"Late-2024 full-surface membership mismatch; missing={missing}, extra={extra}"
        )

    return (
        {
            "late_2024_target": target_rows,
            "late_2024_aged_weak_siblings": aged_weak_sibling_rows,
            "late_2024_stable_displacement": stable_displacement_rows,
            "late_2024_stable_blocked_context": stable_blocked_context_rows,
            "late_2024_antitarget": antitarget_rows,
            "late_2024_full_surface": full_surface_rows,
        },
        {
            "target_count": len(target_rows),
            "antitarget_count": len(antitarget_rows),
            "total_count": len(full_surface_rows),
            "target_timestamps": [row["timestamp"] for row in target_rows],
            "antitarget_timestamps": [row["timestamp"] for row in antitarget_rows],
            "full_surface_timestamps": [row["timestamp"] for row in full_surface_rows],
            "additional_unlabeled_rows": 0,
        },
        {
            "path": str(LATE_2024_SOURCE_ARTIFACT_RELATIVE),
            "audit_version": payload.get("audit_version"),
            "status": payload.get("status"),
            "base_sha": payload.get("base_sha"),
        },
    )


def _load_context_clean_transport_fields() -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    payload = _load_json(ROOT_DIR / CONTEXT_CLEAN_ARTIFACT_RELATIVE)
    if not isinstance(payload, dict):
        raise LocalWindowEvidenceError("Expected object payload in D1 context-clean artifact")
    if payload.get("status") != "bounded_context_clean_selectivity_present":
        raise LocalWindowEvidenceError(
            "D1 context-clean artifact must keep bounded_context_clean_selectivity_present"
        )

    evaluations = payload.get("field_context_clean_evaluations")
    if not isinstance(evaluations, list):
        raise LocalWindowEvidenceError(
            "D1 context-clean artifact is missing field_context_clean_evaluations"
        )

    field_map: dict[str, dict[str, Any]] = {}
    for item in evaluations:
        if not isinstance(item, dict):
            raise LocalWindowEvidenceError(
                "Malformed field evaluation in D1 context-clean artifact"
            )
        field_name = _coerce_str(item.get("field_name"), field_name="field_name")
        admission = item.get("admission")
        if not isinstance(admission, dict):
            raise LocalWindowEvidenceError(f"Admission payload missing for {field_name}")
        field_map[field_name] = {
            "field_name": field_name,
            "descriptive_only": bool(item.get("descriptive_only")),
            "excluded_from_pass_fail": bool(item.get("excluded_from_pass_fail")),
            "claim_status": _coerce_str(
                item.get("claim_status"), field_name=f"{field_name}.claim_status"
            ),
            "passes_context_clean_test": bool(item.get("passes_context_clean_test")),
            "target_bank_ceiling": _coerce_optional_float(
                item.get("target_bank_ceiling"), field_name=f"{field_name}.target_bank_ceiling"
            ),
            "target_bank_ceiling_source_timestamps": _coerce_str_list(
                item.get("target_bank_ceiling_source_timestamps"),
                field_name=f"{field_name}.target_bank_ceiling_source_timestamps",
            ),
            "context_bank_min": _coerce_optional_float(
                item.get("context_bank_min"), field_name=f"{field_name}.context_bank_min"
            ),
            "global_separation_margin": _coerce_optional_float(
                item.get("global_separation_margin"),
                field_name=f"{field_name}.global_separation_margin",
            ),
            "admission": {
                "status": _coerce_str(
                    admission.get("status"), field_name=f"{field_name}.admission.status"
                ),
                "row_count_checked": _coerce_int(
                    admission.get("row_count_checked"),
                    field_name=f"{field_name}.admission.row_count_checked",
                ),
                "missing_timestamps": _coerce_str_list(
                    admission.get("missing_timestamps"),
                    field_name=f"{field_name}.admission.missing_timestamps",
                ),
            },
        }

    required_field_names = {field.field_name for field in FIELD_TRANSPORT_DEFINITIONS}
    missing_required_fields = sorted(required_field_names - set(field_map))
    if missing_required_fields:
        raise LocalWindowEvidenceError(
            f"D1 context-clean artifact is missing required field evaluations: {missing_required_fields}"
        )

    for field_definition in FIELD_TRANSPORT_DEFINITIONS:
        bank_field = field_map[field_definition.field_name]
        if bank_field["target_bank_ceiling"] is None:
            raise LocalWindowEvidenceError(
                f"Transport field {field_definition.field_name} is missing a target-bank ceiling"
            )
        if bank_field["claim_status"] != "evaluated":
            raise LocalWindowEvidenceError(
                f"Transport field {field_definition.field_name} must remain evaluated in the D1 bank artifact"
            )
        if field_definition.descriptive_only:
            if not bank_field["descriptive_only"]:
                raise LocalWindowEvidenceError(
                    f"Transport field {field_definition.field_name} must remain descriptive-only"
                )
        else:
            if bank_field["descriptive_only"]:
                raise LocalWindowEvidenceError(
                    f"Transport field {field_definition.field_name} unexpectedly became descriptive-only"
                )
            if not bank_field["passes_context_clean_test"]:
                raise LocalWindowEvidenceError(
                    f"Transport field {field_definition.field_name} no longer passes the frozen D1 bank test"
                )

    return (
        field_map,
        {
            "path": str(CONTEXT_CLEAN_ARTIFACT_RELATIVE),
            "audit_version": payload.get("audit_version"),
            "status": payload.get("status"),
            "base_sha": payload.get("base_sha"),
        },
    )


def _evaluate_transport_field(
    field_definition: FieldTransportDefinition,
    *,
    bank_field: dict[str, Any],
    cohorts: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    target_rows = cohorts["late_2024_target"]
    antitarget_rows = cohorts["late_2024_antitarget"]
    full_surface_rows = cohorts["late_2024_full_surface"]
    field_name = field_definition.field_name
    transport_ceiling = float(bank_field["target_bank_ceiling"])
    external_admission = _field_admission(full_surface_rows, field_name)

    if external_admission["status"] != "evaluable":
        return {
            "field_name": field_name,
            "descriptive_only": field_definition.descriptive_only,
            "excluded_from_pass_fail": field_definition.descriptive_only,
            "bank_admission": bank_field["admission"],
            "bank_claim_status": bank_field["claim_status"],
            "bank_passes_context_clean_test": bank_field["passes_context_clean_test"],
            "transport_ceiling": _round_or_none(transport_ceiling),
            "transport_ceiling_source_timestamps": bank_field[
                "target_bank_ceiling_source_timestamps"
            ],
            "context_bank_min": bank_field["context_bank_min"],
            "global_separation_margin": bank_field["global_separation_margin"],
            "external_surface_admission": external_admission,
            "claim_status": "not_evaluable",
            "passes_transport_test": False,
            "exact_transport_shape_match": False,
            "selected_target_summary": None,
            "selected_antitarget_summary": None,
            "missed_target_rows": [],
            "leaky_antitarget_rows": [],
            "target_value_summary": None,
            "antitarget_value_summary": None,
        }

    selected_target_rows = [
        row for row in target_rows if float(row[field_name]) <= transport_ceiling
    ]
    selected_antitarget_rows = [
        row for row in antitarget_rows if float(row[field_name]) <= transport_ceiling
    ]
    exact_transport_shape_match = bool(
        len(selected_target_rows) == EXPECTED_TARGET_COUNT and not selected_antitarget_rows
    )
    passes_transport_test = bool(
        exact_transport_shape_match and not field_definition.descriptive_only
    )
    claim_status = (
        "descriptive_only"
        if field_definition.descriptive_only
        else ("transport_survivor" if passes_transport_test else "transport_falsified")
    )

    missed_target_rows = [
        {
            "timestamp": row["timestamp"],
            "value": row[field_name],
            "switch_reason": row["switch_reason"],
        }
        for row in target_rows
        if row not in selected_target_rows
    ]
    leaky_antitarget_rows = [
        {
            "timestamp": row["timestamp"],
            "value": row[field_name],
            "switch_reason": row["switch_reason"],
            "cohort_name": row["cohort_name"],
        }
        for row in selected_antitarget_rows
    ]

    return {
        "field_name": field_name,
        "descriptive_only": field_definition.descriptive_only,
        "excluded_from_pass_fail": field_definition.descriptive_only,
        "bank_admission": bank_field["admission"],
        "bank_claim_status": bank_field["claim_status"],
        "bank_passes_context_clean_test": bank_field["passes_context_clean_test"],
        "transport_ceiling": _round_or_none(transport_ceiling),
        "transport_ceiling_source_timestamps": bank_field["target_bank_ceiling_source_timestamps"],
        "context_bank_min": bank_field["context_bank_min"],
        "global_separation_margin": bank_field["global_separation_margin"],
        "external_surface_admission": external_admission,
        "claim_status": claim_status,
        "passes_transport_test": passes_transport_test,
        "exact_transport_shape_match": exact_transport_shape_match,
        "selected_target_summary": _selection_summary(target_rows, selected_target_rows),
        "selected_antitarget_summary": _selection_summary(
            antitarget_rows, selected_antitarget_rows
        ),
        "missed_target_rows": missed_target_rows,
        "leaky_antitarget_rows": leaky_antitarget_rows,
        "target_value_summary": _summarize_numeric_values(
            [float(row[field_name]) for row in target_rows]
        ),
        "antitarget_value_summary": _summarize_numeric_values(
            [float(row[field_name]) for row in antitarget_rows]
        ),
    }


def _sorted_field_transport_evaluations(
    evaluations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return sorted(
        evaluations,
        key=lambda item: (
            0 if item["passes_transport_test"] else 1,
            0 if not item["descriptive_only"] else 1,
            0 if item["claim_status"] != "not_evaluable" else 1,
            (
                -1
                if item["selected_target_summary"] is None
                else -int(item["selected_target_summary"]["selected_count"])
            ),
            (
                999
                if item["selected_antitarget_summary"] is None
                else int(item["selected_antitarget_summary"]["selected_count"])
            ),
            item["field_name"],
        ),
    )


def run_late_2024_external_surface_falsifier(base_sha: str) -> dict[str, Any]:
    bank_fields, bank_input = _load_context_clean_transport_fields()
    cohorts, row_lock, late_2024_input = load_late_2024_external_surface()
    cohort_summaries = {cohort_name: _cohort_summary(rows) for cohort_name, rows in cohorts.items()}

    field_evaluations = _sorted_field_transport_evaluations(
        [
            _evaluate_transport_field(
                field_definition,
                bank_field=bank_fields[field_definition.field_name],
                cohorts=cohorts,
            )
            for field_definition in FIELD_TRANSPORT_DEFINITIONS
        ]
    )

    admitted_survivor_field_names = [
        evaluation["field_name"]
        for evaluation in field_evaluations
        if not evaluation["descriptive_only"] and evaluation["passes_transport_test"]
    ]
    admitted_falsified_field_names = [
        evaluation["field_name"]
        for evaluation in field_evaluations
        if not evaluation["descriptive_only"]
        and evaluation["claim_status"] == "transport_falsified"
    ]
    not_evaluable_claim_field_names = [
        evaluation["field_name"]
        for evaluation in field_evaluations
        if not evaluation["descriptive_only"] and evaluation["claim_status"] == "not_evaluable"
    ]
    descriptive_shape_match_field_names = [
        evaluation["field_name"]
        for evaluation in field_evaluations
        if evaluation["descriptive_only"] and evaluation["exact_transport_shape_match"]
    ]
    best_partial_claim_field = next(
        (
            evaluation
            for evaluation in field_evaluations
            if not evaluation["descriptive_only"]
            and evaluation["claim_status"] == "transport_falsified"
        ),
        None,
    )
    status = (
        "external_surface_survivor"
        if admitted_survivor_field_names
        else "external_surface_falsified"
    )

    return {
        "audit_version": (
            "ri-policy-router-insufficient-evidence-d1-late-2024-external-surface-falsifier-"
            "2026-05-06"
        ),
        "base_sha": base_sha,
        "status": status,
        "observational_only": True,
        "non_authoritative": True,
        "skill_usage": ["python_engineering"],
        "subject": {
            "symbol": SUBJECT_SYMBOL,
            "timeframe": SUBJECT_TIMEFRAME,
            "year": SUBJECT_YEAR,
            "packet_reference": str(PACKET_REFERENCE),
            "context_clean_reference": str(CONTEXT_CLEAN_REFERENCE),
            "late_2024_reference": str(LATE_2024_REFERENCE),
            "reason_split_reference": str(REASON_SPLIT_REFERENCE),
            "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
        },
        "fail_closed_contract": {
            "statement": (
                "The helper reads only the frozen D1 context-clean artifact and the frozen late-2024 "
                "regression-pocket artifact, aborts on any 5+6 row-lock drift, transports only the "
                "unchanged D1 bank ceilings field-by-field, treats missing clarity_raw as not_evaluable "
                "without backfill/substitute/inference, and keeps clarity_score descriptive-only with no "
                "PASS/FAIL authority."
            )
        },
        "transport_rubric": {
            "required_target_selection_count": EXPECTED_TARGET_COUNT,
            "max_antitarget_selection_count": 0,
            "statement": (
                "Each admitted claim field is evaluated independently on the unchanged 5/5 target and 0/6 "
                "anti-target transport rubric. Overall slice status is external_surface_falsified only if "
                "no admitted claim field survives that exact transport test."
            ),
        },
        "inputs": {
            "context_clean_artifact": bank_input,
            "late_2024_source_artifact": late_2024_input,
        },
        "artifact_row_lock": row_lock,
        "transport_ceiling_registry": {
            field_name: {
                "descriptive_only": bank_field["descriptive_only"],
                "target_bank_ceiling": bank_field["target_bank_ceiling"],
                "target_bank_ceiling_source_timestamps": bank_field[
                    "target_bank_ceiling_source_timestamps"
                ],
                "context_bank_min": bank_field["context_bank_min"],
                "global_separation_margin": bank_field["global_separation_margin"],
            }
            for field_name, bank_field in sorted(bank_fields.items())
        },
        "cohorts": cohort_summaries,
        "transport_summary": {
            "admitted_survivor_field_names": admitted_survivor_field_names,
            "admitted_falsified_field_names": admitted_falsified_field_names,
            "not_evaluable_claim_field_names": not_evaluable_claim_field_names,
            "descriptive_shape_match_field_names": descriptive_shape_match_field_names,
            "best_partial_claim_field": best_partial_claim_field,
            "bounded_signal_present": bool(admitted_survivor_field_names),
        },
        "field_transport_evaluations": field_evaluations,
    }


def main() -> int:
    args = _parse_args()
    output_root = ROOT_DIR / Path(args.output_root_relative)
    output_json = output_root / args.summary_filename
    result = run_late_2024_external_surface_falsifier(base_sha=args.base_sha)

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "summary_artifact": str(output_json),
                "status": result["status"],
                "admitted_survivor_field_names": result["transport_summary"][
                    "admitted_survivor_field_names"
                ],
                "not_evaluable_claim_field_names": result["transport_summary"][
                    "not_evaluable_claim_field_names"
                ],
                "best_partial_claim_field": result["transport_summary"]["best_partial_claim_field"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
