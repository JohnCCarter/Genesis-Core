from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from statistics import fmean, median
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = (
    "ri_policy_router_insufficient_evidence_d1_context_clean_selectivity_falsifier_"
    "2026-05-05.json"
)
FIRST_PAIR_ARTIFACT = Path(
    "results/evaluation/"
    "ri_policy_router_insufficient_evidence_d1_exact_subject_pair_"
    "2019_06_vs_2022_06_2026-05-04.json"
)
SECOND_PAIR_ARTIFACT = Path(
    "results/evaluation/"
    "ri_policy_router_insufficient_evidence_d1_family_survival_"
    "2019_06_vs_2025_03_2026-05-04.json"
)
TRANSPORT_ARTIFACT = Path(
    "results/evaluation/"
    "ri_policy_router_insufficient_evidence_d1_boundary_gap_transport_check_"
    "2019_06_vs_2020_10_11_2026-05-04.json"
)
PACKET_REFERENCE = Path(
    "docs/decisions/regime_intelligence/policy_router/"
    "ri_policy_router_insufficient_evidence_d1_context_clean_selectivity_falsifier_"
    "precode_packet_2026-05-05.md"
)
FIRST_PAIR_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_insufficient_evidence_d1_exact_subject_pair_"
    "2019_06_vs_2022_06_2026-05-04.md"
)
SECOND_PAIR_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_insufficient_evidence_d1_family_survival_"
    "2019_06_vs_2025_03_2026-05-04.md"
)
BOUNDARY_GAP_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_insufficient_evidence_d1_boundary_gap_to_local_context_floor_"
    "2026-05-04.md"
)
TRANSPORT_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_insufficient_evidence_d1_boundary_gap_transport_check_"
    "2019_06_vs_2020_10_11_2026-05-04.md"
)
SYNTHESIS_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_insufficient_evidence_d1_four_surface_synthesis_2026-05-05.md"
)
WORKING_CONTRACT_REFERENCE = Path("GENESIS_WORKING_CONTRACT.md")
SUBJECT_SYMBOL = "tBTCUSD"
SUBJECT_TIMEFRAME = "3h"
HARMFUL_TARGET_TIMESTAMPS = (
    "2019-06-13T06:00:00+00:00",
    "2019-06-13T15:00:00+00:00",
    "2019-06-14T00:00:00+00:00",
    "2019-06-14T09:00:00+00:00",
    "2019-06-15T06:00:00+00:00",
)
HARMFUL_CONTEXT_TIMESTAMPS = ("2019-06-12T06:00:00+00:00",)
CONTROL_2022_TARGET_TIMESTAMPS = (
    "2022-06-24T03:00:00+00:00",
    "2022-06-24T21:00:00+00:00",
    "2022-06-25T06:00:00+00:00",
    "2022-06-25T15:00:00+00:00",
    "2022-06-26T00:00:00+00:00",
)
CONTROL_2022_CONTEXT_TIMESTAMPS = (
    "2022-06-23T03:00:00+00:00",
    "2022-06-23T09:00:00+00:00",
    "2022-06-23T12:00:00+00:00",
    "2022-06-23T18:00:00+00:00",
)
CONTROL_2025_TARGET_TIMESTAMPS = (
    "2025-03-14T15:00:00+00:00",
    "2025-03-15T00:00:00+00:00",
    "2025-03-15T09:00:00+00:00",
    "2025-03-15T18:00:00+00:00",
    "2025-03-16T03:00:00+00:00",
)
CONTROL_2025_DISPLACEMENT_CONTEXT_TIMESTAMPS = (
    "2025-03-13T15:00:00+00:00",
    "2025-03-14T00:00:00+00:00",
)
CONTROL_2025_BLOCKED_CONTEXT_TIMESTAMPS = (
    "2025-03-13T21:00:00+00:00",
    "2025-03-14T06:00:00+00:00",
)
CONTROL_2025_AGED_WEAK_CONTEXT_TIMESTAMPS = ("2025-03-16T12:00:00+00:00",)
CONTROL_2020_TARGET_TIMESTAMPS = (
    "2020-10-31T21:00:00+00:00",
    "2020-11-01T06:00:00+00:00",
    "2020-11-01T15:00:00+00:00",
    "2020-11-02T00:00:00+00:00",
)
CONTROL_2020_CONTEXT_TIMESTAMPS = (
    "2020-11-02T03:00:00+00:00",
    "2020-11-02T09:00:00+00:00",
    "2020-11-02T21:00:00+00:00",
    "2020-11-03T03:00:00+00:00",
)
PRIMARY_FIELD_NAMES = ("action_edge", "confidence_gate", "clarity_raw")
DESCRIPTIVE_FIELD_NAMES = ("clarity_score",)
SUMMARY_FIELDS = (
    "action_edge",
    "confidence_gate",
    "clarity_raw",
    "clarity_score",
    "bars_since_regime_change",
    "fwd_16_close_return_pct",
)


class ContextCleanSelectivityError(RuntimeError):
    """Raised when the fixed four-surface context-clean contract drifts."""


@dataclass(frozen=True)
class FieldDefinition:
    field_name: str
    descriptive_only: bool


FIELD_DEFINITIONS = (
    FieldDefinition(field_name="action_edge", descriptive_only=False),
    FieldDefinition(field_name="confidence_gate", descriptive_only=False),
    FieldDefinition(field_name="clarity_raw", descriptive_only=False),
    FieldDefinition(field_name="clarity_score", descriptive_only=True),
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Materialize one artifact-only D1 context-clean selectivity falsifier on the fixed "
            "2019-06 / 2022-06 / 2025-03 / 2020-10/11 bank."
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
        raise ContextCleanSelectivityError(
            f"Expected numeric optional value for {field_name}, got {value!r}"
        )
    numeric_value = float(value)
    if numeric_value != numeric_value or numeric_value in {float("inf"), float("-inf")}:
        raise ContextCleanSelectivityError(
            f"Expected finite optional value for {field_name}, got {value!r}"
        )
    return _round_or_none(numeric_value)


def _coerce_required_int(value: Any, *, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ContextCleanSelectivityError(
            f"Expected integer value for {field_name}, got {value!r}"
        )
    return int(value)


def _coerce_required_str(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ContextCleanSelectivityError(f"Expected string value for {field_name}, got {value!r}")
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
    gt_zero_share = sum(value > 0 for value in values) / len(values)
    return {
        "count": len(values),
        "min": _round_or_none(min(values)),
        "max": _round_or_none(max(values)),
        "mean": _round_or_none(fmean(values)),
        "median": _round_or_none(median(values)),
        "gt_zero_share": _round_or_none(gt_zero_share),
    }


def _load_json_file(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContextCleanSelectivityError(f"Required JSON input not found: {path}") from exc


def _assert_top_level_true(payload: dict[str, Any], *, field_name: str, label: str) -> None:
    if payload.get(field_name) is not True:
        raise ContextCleanSelectivityError(
            f"Artifact {label} must keep {field_name}=true for this slice"
        )


def _assert_exact_timestamps(
    rows: list[dict[str, Any]],
    *,
    cohort_name: str,
    expected_timestamps: tuple[str, ...],
) -> None:
    actual_timestamps = tuple(row["timestamp"] for row in rows)
    if actual_timestamps != expected_timestamps:
        raise ContextCleanSelectivityError(
            f"Timestamp drift for {cohort_name}: expected {expected_timestamps!r}, got {actual_timestamps!r}"
        )


def _assert_row_values(
    rows: list[dict[str, Any]],
    *,
    cohort_name: str,
    expected_values: dict[str, Any],
) -> None:
    for row in rows:
        for field_name, expected_value in expected_values.items():
            if row.get(field_name) != expected_value:
                raise ContextCleanSelectivityError(
                    f"Locked row contract mismatch for {cohort_name} on {row['timestamp']}: "
                    f"expected {field_name}={expected_value!r}, got {row.get(field_name)!r}"
                )


def _normalize_artifact_row(
    row: dict[str, Any],
    *,
    cohort_name: str,
    row_role: str,
    claim_eligible: bool,
    expected_year: str,
) -> dict[str, Any]:
    timestamp = _coerce_required_str(row.get("timestamp"), field_name="timestamp")
    if row.get("year") != expected_year:
        raise ContextCleanSelectivityError(
            f"Expected year={expected_year!r} for {timestamp}, got {row.get('year')!r}"
        )
    return {
        "timestamp": timestamp,
        "cohort_name": cohort_name,
        "row_role": row_role,
        "claim_eligible": claim_eligible,
        "year": expected_year,
        "switch_reason": row.get("switch_reason"),
        "absent_action": row.get("absent_action"),
        "enabled_action": row.get("enabled_action"),
        "action_pair": row.get("action_pair"),
        "selected_policy": row.get("selected_policy"),
        "raw_target_policy": row.get("raw_target_policy"),
        "previous_policy": row.get("previous_policy"),
        "zone": row.get("zone"),
        "candidate": row.get("candidate"),
        "bars_since_regime_change": row.get("bars_since_regime_change"),
        "action_edge": _coerce_optional_numeric(row.get("action_edge"), field_name="action_edge"),
        "confidence_gate": _coerce_optional_numeric(
            row.get("confidence_gate"), field_name="confidence_gate"
        ),
        "clarity_score": _coerce_optional_numeric(
            row.get("clarity_score"), field_name="clarity_score"
        ),
        "clarity_raw": _coerce_optional_numeric(row.get("clarity_raw"), field_name="clarity_raw"),
        "dwell_duration": _coerce_optional_numeric(
            row.get("dwell_duration"), field_name="dwell_duration"
        ),
        "fwd_16_close_return_pct": _coerce_optional_numeric(
            row.get("fwd_16_close_return_pct"), field_name="fwd_16_close_return_pct"
        ),
    }


def _extract_rows_from_cohort(
    artifact: dict[str, Any],
    *,
    cohort_name: str,
    row_role: str,
    claim_eligible: bool,
    expected_year: str,
) -> list[dict[str, Any]]:
    cohorts = artifact.get("cohorts")
    if not isinstance(cohorts, dict):
        raise ContextCleanSelectivityError("Artifact is missing a cohort registry")
    cohort_summary = cohorts.get(cohort_name)
    if not isinstance(cohort_summary, dict):
        raise ContextCleanSelectivityError(f"Artifact is missing cohort {cohort_name!r}")
    rows = cohort_summary.get("rows")
    if not isinstance(rows, list):
        raise ContextCleanSelectivityError(f"Cohort {cohort_name!r} is missing row payloads")
    normalized_rows = [
        _normalize_artifact_row(
            row,
            cohort_name=cohort_name,
            row_role=row_role,
            claim_eligible=claim_eligible,
            expected_year=expected_year,
        )
        for row in rows
        if isinstance(row, dict)
    ]
    return sorted(normalized_rows, key=lambda item: item["timestamp"])


def _assert_same_rows(
    primary_rows: list[dict[str, Any]],
    secondary_rows: list[dict[str, Any]],
    *,
    cohort_name: str,
) -> None:
    if len(primary_rows) != len(secondary_rows):
        raise ContextCleanSelectivityError(f"Shared row-count drift for {cohort_name}")
    secondary_by_timestamp = {row["timestamp"]: row for row in secondary_rows}
    for primary_row in primary_rows:
        secondary_row = secondary_by_timestamp.get(primary_row["timestamp"])
        if secondary_row is None:
            raise ContextCleanSelectivityError(
                f"Shared surface missing timestamp {primary_row['timestamp']} in comparison artifact for {cohort_name}"
            )
        for field_name, primary_value in primary_row.items():
            if secondary_row.get(field_name) != primary_value:
                raise ContextCleanSelectivityError(
                    f"Shared surface mismatch for {cohort_name} at {primary_row['timestamp']}: "
                    f"field {field_name!r} differs"
                )


def _build_surface_summary(
    target_rows: list[dict[str, Any]],
    context_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "target_row_count": len(target_rows),
        "context_row_count": len(context_rows),
        "target_timestamps": [row["timestamp"] for row in target_rows],
        "context_timestamps": [row["timestamp"] for row in context_rows],
        "target_metric_summary": {
            field_name: _summarize_numeric_values(
                [
                    float(row[field_name])
                    for row in target_rows
                    if isinstance(row.get(field_name), int | float)
                ]
            )
            for field_name in SUMMARY_FIELDS
        },
        "context_metric_summary": {
            field_name: _summarize_numeric_values(
                [
                    float(row[field_name])
                    for row in context_rows
                    if isinstance(row.get(field_name), int | float)
                ]
            )
            for field_name in SUMMARY_FIELDS
        },
    }


def _assert_summary_matches(
    *,
    actual_summary: dict[str, Any],
    expected_summary: dict[str, Any],
    surface_id: str,
) -> None:
    for summary_name in ("target_metric_summary", "context_metric_summary"):
        for field_name in SUMMARY_FIELDS:
            expected_field_summary = expected_summary[summary_name].get(field_name)
            actual_field_summary = actual_summary.get(summary_name, {}).get(field_name)
            if actual_field_summary != expected_field_summary:
                raise ContextCleanSelectivityError(
                    f"Transport summary mismatch for {surface_id} / {summary_name} / {field_name}"
                )


def _build_row_role_registry(surfaces: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    registry: list[dict[str, Any]] = []
    for surface_id, surface in surfaces.items():
        for row in surface["target_rows"] + surface["context_rows"]:
            registry.append(
                {
                    "timestamp": row["timestamp"],
                    "surface_id": surface_id,
                    "cohort_name": row["cohort_name"],
                    "row_role": row["row_role"],
                    "claim_eligible": row["claim_eligible"],
                    "switch_reason": row["switch_reason"],
                    "action_pair": row["action_pair"],
                }
            )
    return sorted(registry, key=lambda item: (item["timestamp"], item["surface_id"]))


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


def _load_transport_rows(
    transport_artifact: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    registry = transport_artifact.get("artifact_row_lock", {}).get("row_role_registry")
    proof_rows = transport_artifact.get("control_2020_source_backed_field_proof", {}).get("rows")
    if not isinstance(registry, list) or not isinstance(proof_rows, list):
        raise ContextCleanSelectivityError(
            "Transport artifact is missing 2020 row-role or proof rows"
        )

    registry_by_timestamp: dict[str, dict[str, Any]] = {}
    harmful_2019_registry_rows: list[dict[str, Any]] = []
    for item in registry:
        if not isinstance(item, dict):
            raise ContextCleanSelectivityError(
                "Malformed row-role registry entry in transport artifact"
            )
        timestamp = _coerce_required_str(item.get("timestamp"), field_name="registry.timestamp")
        if item.get("surface_id") == "harmful_2019":
            harmful_2019_registry_rows.append(item)
            continue
        registry_by_timestamp[timestamp] = item

    harmful_target_registry = [
        row for row in harmful_2019_registry_rows if row.get("row_role") == "harmful_target"
    ]
    harmful_context_registry = [
        row for row in harmful_2019_registry_rows if row.get("row_role") == "context"
    ]
    if (
        tuple(sorted(row["timestamp"] for row in harmful_target_registry))
        != HARMFUL_TARGET_TIMESTAMPS
    ):
        raise ContextCleanSelectivityError("Transport artifact harmful target registry drifted")
    if (
        tuple(sorted(row["timestamp"] for row in harmful_context_registry))
        != HARMFUL_CONTEXT_TIMESTAMPS
    ):
        raise ContextCleanSelectivityError("Transport artifact harmful context registry drifted")

    target_rows: list[dict[str, Any]] = []
    context_rows: list[dict[str, Any]] = []
    for row in proof_rows:
        if not isinstance(row, dict):
            raise ContextCleanSelectivityError("Malformed control_2020 proof row")
        timestamp = _coerce_required_str(row.get("timestamp"), field_name="proof.timestamp")
        registry_row = registry_by_timestamp.get(timestamp)
        if registry_row is None:
            raise ContextCleanSelectivityError(
                f"Transport proof row {timestamp} is missing from the row-role registry"
            )
        normalized_row = {
            "timestamp": timestamp,
            "cohort_name": _coerce_required_str(
                registry_row.get("cohort_name"), field_name="registry.cohort_name"
            ),
            "row_role": _coerce_required_str(
                registry_row.get("row_role"), field_name="registry.row_role"
            ),
            "claim_eligible": bool(registry_row.get("claim_eligible")),
            "year": "2020",
            "switch_reason": _coerce_required_str(
                row.get("switch_reason"), field_name="switch_reason"
            ),
            "absent_action": None,
            "enabled_action": None,
            "action_pair": _coerce_required_str(row.get("action_pair"), field_name="action_pair"),
            "selected_policy": _coerce_required_str(
                row.get("selected_policy"), field_name="selected_policy"
            ),
            "raw_target_policy": None,
            "previous_policy": None,
            "zone": None,
            "candidate": None,
            "bars_since_regime_change": _coerce_required_int(
                row.get("bars_since_regime_change"), field_name="bars_since_regime_change"
            ),
            "action_edge": _coerce_optional_numeric(
                row.get("action_edge"), field_name="action_edge"
            ),
            "confidence_gate": _coerce_optional_numeric(
                row.get("confidence_gate"), field_name="confidence_gate"
            ),
            "clarity_score": _coerce_optional_numeric(
                row.get("clarity_score"), field_name="clarity_score"
            ),
            "clarity_raw": _coerce_optional_numeric(
                row.get("clarity_raw"), field_name="clarity_raw"
            ),
            "dwell_duration": None,
            "fwd_16_close_return_pct": None,
        }
        if normalized_row["claim_eligible"]:
            target_rows.append(normalized_row)
        else:
            context_rows.append(normalized_row)

    target_rows = sorted(target_rows, key=lambda item: item["timestamp"])
    context_rows = sorted(context_rows, key=lambda item: item["timestamp"])
    _assert_exact_timestamps(
        target_rows,
        cohort_name="control_2020_target",
        expected_timestamps=CONTROL_2020_TARGET_TIMESTAMPS,
    )
    _assert_exact_timestamps(
        context_rows,
        cohort_name="control_2020_context",
        expected_timestamps=CONTROL_2020_CONTEXT_TIMESTAMPS,
    )
    _assert_row_values(
        target_rows,
        cohort_name="control_2020_target",
        expected_values={
            "row_role": "control_target",
            "claim_eligible": True,
            "switch_reason": "insufficient_evidence",
            "selected_policy": "RI_no_trade_policy",
            "bars_since_regime_change": 302,
        },
    )
    return target_rows, context_rows


def _load_four_surface_bank() -> dict[str, Any]:
    first_pair_artifact = _load_json_file(ROOT_DIR / FIRST_PAIR_ARTIFACT)
    second_pair_artifact = _load_json_file(ROOT_DIR / SECOND_PAIR_ARTIFACT)
    transport_artifact = _load_json_file(ROOT_DIR / TRANSPORT_ARTIFACT)

    if not isinstance(first_pair_artifact, dict):
        raise ContextCleanSelectivityError("First pair artifact must be a JSON object")
    if not isinstance(second_pair_artifact, dict):
        raise ContextCleanSelectivityError("Second pair artifact must be a JSON object")
    if not isinstance(transport_artifact, dict):
        raise ContextCleanSelectivityError("Transport artifact must be a JSON object")

    _assert_top_level_true(
        first_pair_artifact,
        field_name="context_rows_excluded_from_selection",
        label="first_pair",
    )
    _assert_top_level_true(
        second_pair_artifact,
        field_name="context_rows_excluded_from_selection",
        label="second_pair",
    )
    _assert_top_level_true(
        transport_artifact,
        field_name="context_rows_excluded_from_selection",
        label="transport",
    )

    harmful_target = _extract_rows_from_cohort(
        first_pair_artifact,
        cohort_name="harmful_target",
        row_role="harmful_target",
        claim_eligible=True,
        expected_year="2019",
    )
    harmful_context = _extract_rows_from_cohort(
        first_pair_artifact,
        cohort_name="harmful_context",
        row_role="context",
        claim_eligible=False,
        expected_year="2019",
    )
    control_2022_target = _extract_rows_from_cohort(
        first_pair_artifact,
        cohort_name="control_target",
        row_role="control_target",
        claim_eligible=True,
        expected_year="2022",
    )
    control_2022_context = _extract_rows_from_cohort(
        first_pair_artifact,
        cohort_name="control_context",
        row_role="context",
        claim_eligible=False,
        expected_year="2022",
    )
    harmful_target_second = _extract_rows_from_cohort(
        second_pair_artifact,
        cohort_name="harmful_target",
        row_role="harmful_target",
        claim_eligible=True,
        expected_year="2019",
    )
    harmful_context_second = _extract_rows_from_cohort(
        second_pair_artifact,
        cohort_name="harmful_context",
        row_role="context",
        claim_eligible=False,
        expected_year="2019",
    )
    control_2025_target = _extract_rows_from_cohort(
        second_pair_artifact,
        cohort_name="control_target",
        row_role="control_target",
        claim_eligible=True,
        expected_year="2025",
    )
    control_2025_displacement = _extract_rows_from_cohort(
        second_pair_artifact,
        cohort_name="control_displacement_context",
        row_role="context",
        claim_eligible=False,
        expected_year="2025",
    )
    control_2025_blocked = _extract_rows_from_cohort(
        second_pair_artifact,
        cohort_name="control_blocked_context",
        row_role="context",
        claim_eligible=False,
        expected_year="2025",
    )
    control_2025_aged_weak = _extract_rows_from_cohort(
        second_pair_artifact,
        cohort_name="control_aged_weak_context",
        row_role="context",
        claim_eligible=False,
        expected_year="2025",
    )
    control_2020_target, control_2020_context = _load_transport_rows(transport_artifact)

    _assert_exact_timestamps(
        harmful_target,
        cohort_name="harmful_target",
        expected_timestamps=HARMFUL_TARGET_TIMESTAMPS,
    )
    _assert_exact_timestamps(
        harmful_context,
        cohort_name="harmful_context",
        expected_timestamps=HARMFUL_CONTEXT_TIMESTAMPS,
    )
    _assert_exact_timestamps(
        control_2022_target,
        cohort_name="control_2022_target",
        expected_timestamps=CONTROL_2022_TARGET_TIMESTAMPS,
    )
    _assert_exact_timestamps(
        control_2022_context,
        cohort_name="control_2022_context",
        expected_timestamps=CONTROL_2022_CONTEXT_TIMESTAMPS,
    )
    _assert_exact_timestamps(
        control_2025_target,
        cohort_name="control_2025_target",
        expected_timestamps=CONTROL_2025_TARGET_TIMESTAMPS,
    )
    _assert_exact_timestamps(
        control_2025_displacement,
        cohort_name="control_2025_displacement_context",
        expected_timestamps=CONTROL_2025_DISPLACEMENT_CONTEXT_TIMESTAMPS,
    )
    _assert_exact_timestamps(
        control_2025_blocked,
        cohort_name="control_2025_blocked_context",
        expected_timestamps=CONTROL_2025_BLOCKED_CONTEXT_TIMESTAMPS,
    )
    _assert_exact_timestamps(
        control_2025_aged_weak,
        cohort_name="control_2025_aged_weak_context",
        expected_timestamps=CONTROL_2025_AGED_WEAK_CONTEXT_TIMESTAMPS,
    )

    _assert_row_values(
        harmful_target,
        cohort_name="harmful_target",
        expected_values={
            "zone": "low",
            "candidate": "LONG",
            "absent_action": "LONG",
            "enabled_action": "NONE",
            "selected_policy": "RI_no_trade_policy",
            "switch_reason": "insufficient_evidence",
            "action_pair": "LONG->NONE",
            "bars_since_regime_change": 164,
        },
    )
    _assert_row_values(
        harmful_context,
        cohort_name="harmful_context",
        expected_values={
            "zone": "low",
            "candidate": "LONG",
            "absent_action": "LONG",
            "enabled_action": "NONE",
            "selected_policy": "RI_no_trade_policy",
            "switch_reason": "AGED_WEAK_CONTINUATION_GUARD",
            "action_pair": "LONG->NONE",
            "bars_since_regime_change": 164,
        },
    )
    _assert_row_values(
        control_2022_target,
        cohort_name="control_2022_target",
        expected_values={
            "zone": "low",
            "candidate": "LONG",
            "absent_action": "LONG",
            "enabled_action": "NONE",
            "selected_policy": "RI_no_trade_policy",
            "switch_reason": "insufficient_evidence",
            "bars_since_regime_change": 184,
        },
    )
    _assert_row_values(
        control_2025_target,
        cohort_name="control_2025_target",
        expected_values={
            "zone": "low",
            "candidate": "LONG",
            "absent_action": "LONG",
            "enabled_action": "NONE",
            "selected_policy": "RI_no_trade_policy",
            "switch_reason": "insufficient_evidence",
            "bars_since_regime_change": 65,
        },
    )

    _assert_same_rows(harmful_target, harmful_target_second, cohort_name="harmful_target")
    _assert_same_rows(harmful_context, harmful_context_second, cohort_name="harmful_context")

    control_2025_context = sorted(
        [*control_2025_displacement, *control_2025_blocked, *control_2025_aged_weak],
        key=lambda row: row["timestamp"],
    )

    surfaces = {
        "harmful_2019": {
            "surface_id": "harmful_2019",
            "surface_role": "harmful",
            "primary_source": "first_pair_artifact",
            "secondary_source": "second_pair_artifact",
            "target_rows": harmful_target,
            "context_rows": harmful_context,
        },
        "control_2022": {
            "surface_id": "control_2022",
            "surface_role": "control",
            "primary_source": "first_pair_artifact",
            "secondary_source": None,
            "target_rows": control_2022_target,
            "context_rows": control_2022_context,
        },
        "control_2025": {
            "surface_id": "control_2025",
            "surface_role": "control",
            "primary_source": "second_pair_artifact",
            "secondary_source": None,
            "target_rows": control_2025_target,
            "context_rows": control_2025_context,
        },
        "control_2020": {
            "surface_id": "control_2020",
            "surface_role": "control",
            "primary_source": "transport_artifact",
            "secondary_source": None,
            "target_rows": control_2020_target,
            "context_rows": control_2020_context,
        },
    }
    for surface in surfaces.values():
        surface["summary"] = _build_surface_summary(surface["target_rows"], surface["context_rows"])

    transport_harmful_summary = transport_artifact.get("surfaces", {}).get("harmful_2019")
    if not isinstance(transport_harmful_summary, dict):
        raise ContextCleanSelectivityError("Transport artifact is missing harmful_2019 summary")
    _assert_summary_matches(
        actual_summary=transport_harmful_summary,
        expected_summary=surfaces["harmful_2019"]["summary"],
        surface_id="harmful_2019",
    )

    return {
        "surfaces": surfaces,
        "source_artifacts": {
            "first_pair_artifact": {
                "path": str(FIRST_PAIR_ARTIFACT),
                "audit_version": first_pair_artifact.get("audit_version"),
                "status": first_pair_artifact.get("status"),
                "base_sha": first_pair_artifact.get("base_sha"),
            },
            "second_pair_artifact": {
                "path": str(SECOND_PAIR_ARTIFACT),
                "audit_version": second_pair_artifact.get("audit_version"),
                "status": second_pair_artifact.get("status"),
                "base_sha": second_pair_artifact.get("base_sha"),
            },
            "transport_artifact": {
                "path": str(TRANSPORT_ARTIFACT),
                "audit_version": transport_artifact.get("audit_version"),
                "status": transport_artifact.get("status"),
                "base_sha": transport_artifact.get("base_sha"),
            },
        },
        "transport_control_2020_source_backed_field_proof": transport_artifact.get(
            "control_2020_source_backed_field_proof"
        ),
    }


def _evaluate_field(
    field_definition: FieldDefinition,
    *,
    surfaces: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    all_target_rows = [row for surface in surfaces.values() for row in surface["target_rows"]]
    all_context_rows = [row for surface in surfaces.values() for row in surface["context_rows"]]
    admission = _field_admission([*all_target_rows, *all_context_rows], field_definition.field_name)
    if admission["status"] != "evaluable":
        return {
            "field_name": field_definition.field_name,
            "descriptive_only": field_definition.descriptive_only,
            "excluded_from_pass_fail": field_definition.descriptive_only,
            "admission": admission,
            "claim_status": "not_evaluable",
            "passes_context_clean_test": False,
            "target_bank_ceiling": None,
            "context_bank_min": None,
            "global_separation_margin": None,
            "surface_extrema": {},
            "leaky_context_timestamps": admission["missing_timestamps"],
        }

    target_values = [float(row[field_definition.field_name]) for row in all_target_rows]
    target_ceiling = max(target_values)
    context_values = [float(row[field_definition.field_name]) for row in all_context_rows]
    context_min = min(context_values)
    leaky_context_timestamps = sorted(
        row["timestamp"]
        for row in all_context_rows
        if float(row[field_definition.field_name]) <= target_ceiling
    )
    target_ceiling_source_timestamps = sorted(
        row["timestamp"]
        for row in all_target_rows
        if float(row[field_definition.field_name]) == target_ceiling
    )
    context_min_source_timestamps = sorted(
        row["timestamp"]
        for row in all_context_rows
        if float(row[field_definition.field_name]) == context_min
    )
    surface_extrema: dict[str, Any] = {}
    for surface_id, surface in surfaces.items():
        surface_target_values = [
            float(row[field_definition.field_name]) for row in surface["target_rows"]
        ]
        surface_context_values = [
            float(row[field_definition.field_name]) for row in surface["context_rows"]
        ]
        surface_target_max = max(surface_target_values)
        surface_context_min = min(surface_context_values)
        surface_extrema[surface_id] = {
            "target_max": _round_or_none(surface_target_max),
            "target_max_source_timestamps": sorted(
                row["timestamp"]
                for row in surface["target_rows"]
                if float(row[field_definition.field_name]) == surface_target_max
            ),
            "context_min": _round_or_none(surface_context_min),
            "context_min_source_timestamps": sorted(
                row["timestamp"]
                for row in surface["context_rows"]
                if float(row[field_definition.field_name]) == surface_context_min
            ),
            "separation_margin": _round_or_none(surface_context_min - surface_target_max),
        }
    passes_context_clean_test = not leaky_context_timestamps
    return {
        "field_name": field_definition.field_name,
        "descriptive_only": field_definition.descriptive_only,
        "excluded_from_pass_fail": field_definition.descriptive_only,
        "admission": admission,
        "claim_status": "evaluated",
        "passes_context_clean_test": passes_context_clean_test,
        "target_bank_ceiling": _round_or_none(target_ceiling),
        "target_bank_ceiling_source_timestamps": target_ceiling_source_timestamps,
        "context_bank_min": _round_or_none(context_min),
        "context_bank_min_source_timestamps": context_min_source_timestamps,
        "global_separation_margin": _round_or_none(context_min - target_ceiling),
        "surface_extrema": surface_extrema,
        "leaky_context_timestamps": leaky_context_timestamps,
    }


def run_context_clean_selectivity_falsifier(base_sha: str) -> dict[str, Any]:
    bank_payload = _load_four_surface_bank()
    surfaces = bank_payload["surfaces"]
    all_rows = [
        row
        for surface in surfaces.values()
        for row in [*surface["target_rows"], *surface["context_rows"]]
    ]
    field_evaluations = [
        _evaluate_field(field_definition, surfaces=surfaces)
        for field_definition in FIELD_DEFINITIONS
    ]
    non_null_fields = [
        evaluation["field_name"]
        for evaluation in field_evaluations
        if not evaluation["descriptive_only"] and evaluation["passes_context_clean_test"]
    ]
    claim_fields_without_signal = [
        evaluation["field_name"]
        for evaluation in field_evaluations
        if not evaluation["descriptive_only"] and not evaluation["passes_context_clean_test"]
    ]
    if any(
        evaluation["claim_status"] != "evaluated"
        for evaluation in field_evaluations
        if not evaluation["descriptive_only"]
    ):
        raise ContextCleanSelectivityError(
            "At least one admitted primary field lost direct evaluability on the fixed four-surface bank"
        )
    status = (
        "bounded_context_clean_selectivity_present"
        if non_null_fields
        else "bounded_context_clean_selectivity_null"
    )
    return {
        "audit_version": (
            "ri-policy-router-insufficient-evidence-d1-context-clean-selectivity-falsifier-"
            "2026-05-05"
        ),
        "base_sha": base_sha,
        "status": status,
        "observational_only": True,
        "non_authoritative": True,
        "context_rows_excluded_from_selection": True,
        "skill_usage": ["decision_gate_debug", "python_engineering"],
        "subject": {
            "symbol": SUBJECT_SYMBOL,
            "timeframe": SUBJECT_TIMEFRAME,
            "packet_reference": str(PACKET_REFERENCE),
            "first_pair_reference": str(FIRST_PAIR_REFERENCE),
            "second_pair_reference": str(SECOND_PAIR_REFERENCE),
            "boundary_gap_reference": str(BOUNDARY_GAP_REFERENCE),
            "transport_reference": str(TRANSPORT_REFERENCE),
            "synthesis_reference": str(SYNTHESIS_REFERENCE),
            "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
        },
        "fail_closed_contract": {
            "statement": (
                "The helper reads only the three fixed D1 evaluation artifacts, locks the exact "
                "2019 / 2022 / 2025 / 2020 target-context bank, aborts on any row-lock or shared-2019 "
                "drift, evaluates only the pre-registered target-bank ceiling reread, excludes all "
                "context rows from claim eligibility, and keeps every outcome exact-surface only, "
                "descriptive only, and non-authoritative."
            )
        },
        "search_boundary": {
            "statement": (
                "No threshold search, conjunction search, source widening, raw rereads, subject widening, "
                "or July/March/late-2024 reopening is allowed. This slice tests only whether the fixed "
                "four-surface target bank sits cleanly below the fixed context bank on the admitted D1 family."
            )
        },
        "inputs": bank_payload["source_artifacts"],
        "artifact_row_lock": {
            "harmful_target_timestamps": list(HARMFUL_TARGET_TIMESTAMPS),
            "harmful_context_timestamps": list(HARMFUL_CONTEXT_TIMESTAMPS),
            "control_2022_target_timestamps": list(CONTROL_2022_TARGET_TIMESTAMPS),
            "control_2022_context_timestamps": list(CONTROL_2022_CONTEXT_TIMESTAMPS),
            "control_2025_target_timestamps": list(CONTROL_2025_TARGET_TIMESTAMPS),
            "control_2025_context_timestamps": [
                *CONTROL_2025_DISPLACEMENT_CONTEXT_TIMESTAMPS,
                *CONTROL_2025_BLOCKED_CONTEXT_TIMESTAMPS,
                *CONTROL_2025_AGED_WEAK_CONTEXT_TIMESTAMPS,
            ],
            "control_2020_target_timestamps": list(CONTROL_2020_TARGET_TIMESTAMPS),
            "control_2020_context_timestamps": list(CONTROL_2020_CONTEXT_TIMESTAMPS),
            "shared_2019_surface_match": True,
            "context_rows_excluded_from_selection": True,
            "observational_only_authority": True,
            "target_bank_row_count": sum(
                len(surface["target_rows"]) for surface in surfaces.values()
            ),
            "context_bank_row_count": sum(
                len(surface["context_rows"]) for surface in surfaces.values()
            ),
            "row_role_registry": _build_row_role_registry(surfaces),
        },
        "transport_control_2020_source_backed_field_proof": bank_payload[
            "transport_control_2020_source_backed_field_proof"
        ],
        "surfaces": {
            surface_id: {
                "surface_role": surface["surface_role"],
                "primary_source": surface["primary_source"],
                "secondary_source": surface.get("secondary_source"),
                **surface["summary"],
            }
            for surface_id, surface in surfaces.items()
        },
        "field_admission": {
            field_name: _field_admission(all_rows, field_name)
            for field_name in [*PRIMARY_FIELD_NAMES, *DESCRIPTIVE_FIELD_NAMES]
        },
        "context_clean_summary": {
            "non_null_field_names": non_null_fields,
            "claim_fields_without_signal": claim_fields_without_signal,
            "bounded_signal_present": bool(non_null_fields),
        },
        "field_context_clean_evaluations": field_evaluations,
    }


def main() -> int:
    args = _parse_args()
    output_root = ROOT_DIR / Path(args.output_root_relative)
    output_json = output_root / args.summary_filename
    result = run_context_clean_selectivity_falsifier(base_sha=args.base_sha)

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "summary_artifact": str(output_json),
                "status": result["status"],
                "non_null_field_names": result["context_clean_summary"]["non_null_field_names"],
                "claim_fields_without_signal": result["context_clean_summary"][
                    "claim_fields_without_signal"
                ],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
