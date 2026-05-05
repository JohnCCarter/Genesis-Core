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
    "ri_policy_router_insufficient_evidence_d1_boundary_gap_to_local_context_floor_"
    "2026-05-04.json"
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
PACKET_REFERENCE = Path(
    "docs/decisions/regime_intelligence/policy_router/"
    "ri_policy_router_insufficient_evidence_d1_boundary_gap_to_local_context_floor_"
    "precode_packet_2026-05-04.md"
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
RESIDUAL_METHOD_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_insufficient_evidence_displacement_normalized_residual_read_"
    "2026-04-30.md"
)
RESIDUAL_METHOD_PACKET_REFERENCE = Path(
    "docs/decisions/regime_intelligence/policy_router/"
    "ri_policy_router_insufficient_evidence_displacement_normalized_residual_read_"
    "packet_2026-04-30.md"
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
CONTROL_2025_DISPLACEMENT_TIMESTAMPS = (
    "2025-03-13T15:00:00+00:00",
    "2025-03-14T00:00:00+00:00",
)
CONTROL_2025_BLOCKED_CONTEXT_TIMESTAMPS = (
    "2025-03-13T21:00:00+00:00",
    "2025-03-14T06:00:00+00:00",
)
CONTROL_2025_AGED_WEAK_CONTEXT_TIMESTAMPS = ("2025-03-16T12:00:00+00:00",)
ROW_COMPARE_FIELDS = (
    "timestamp",
    "cohort_name",
    "year",
    "switch_reason",
    "absent_action",
    "enabled_action",
    "action_pair",
    "selected_policy",
    "raw_target_policy",
    "previous_policy",
    "zone",
    "candidate",
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
SURFACE_SUMMARY_FIELDS = (
    "action_edge",
    "confidence_gate",
    "clarity_raw",
    "clarity_score",
    "fwd_16_close_return_pct",
)


class BoundaryGapArtifactError(RuntimeError):
    """Raised when the fixed artifact-only boundary-gap contract drifts."""


@dataclass(frozen=True)
class FieldDefinition:
    field_name: str
    descriptive_only: bool
    missing_policy: str


FIELD_DEFINITIONS = (
    FieldDefinition(
        field_name="action_edge",
        descriptive_only=False,
        missing_policy="error",
    ),
    FieldDefinition(
        field_name="confidence_gate",
        descriptive_only=False,
        missing_policy="error",
    ),
    FieldDefinition(
        field_name="clarity_raw",
        descriptive_only=False,
        missing_policy="not_evaluable",
    ),
    FieldDefinition(
        field_name="clarity_score",
        descriptive_only=True,
        missing_policy="not_evaluable",
    ),
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Read only the two committed D1 evaluation artifacts and reread the "
            "fixed non-age family as a boundary gap to each surface's all-context floor."
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
        raise BoundaryGapArtifactError(
            f"Expected numeric optional value for {field_name}, got {value!r}"
        )
    numeric_value = float(value)
    if numeric_value != numeric_value or numeric_value in {
        float("inf"),
        float("-inf"),
    }:  # noqa: PLR0124
        raise BoundaryGapArtifactError(
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
    gt_zero_share = sum(value > 0 for value in values) / len(values)
    return {
        "count": len(values),
        "min": _round_or_none(min(values)),
        "max": _round_or_none(max(values)),
        "mean": _round_or_none(fmean(values)),
        "median": _round_or_none(median(values)),
        "gt_zero_share": _round_or_none(gt_zero_share),
    }


def _load_json_file(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise BoundaryGapArtifactError(f"Required artifact not found: {path}") from exc
    if not isinstance(payload, dict):
        raise BoundaryGapArtifactError(f"Expected top-level JSON object in {path}")
    return payload


def _assert_top_level_true(artifact: dict[str, Any], *, field_name: str, label: str) -> None:
    if artifact.get(field_name) is not True:
        raise BoundaryGapArtifactError(
            f"Artifact {label} must keep {field_name}=true for this slice"
        )


def _normalize_row(
    row: dict[str, Any],
    *,
    cohort_name: str,
    row_role: str,
    claim_eligible: bool,
    expected_year: str,
) -> dict[str, Any]:
    timestamp = row.get("timestamp")
    if not isinstance(timestamp, str):
        raise BoundaryGapArtifactError(
            f"Locked row in cohort {cohort_name} is missing a string timestamp"
        )

    existing_row_role = row.get("row_role")
    if existing_row_role is not None and existing_row_role != row_role:
        raise BoundaryGapArtifactError(
            f"Expected row_role={row_role!r} for {timestamp}, got {existing_row_role!r}"
        )
    existing_claim_eligible = row.get("claim_eligible")
    if existing_claim_eligible is not None and existing_claim_eligible is not claim_eligible:
        raise BoundaryGapArtifactError(
            f"Expected claim_eligible={claim_eligible!r} for {timestamp}, "
            f"got {existing_claim_eligible!r}"
        )
    year = row.get("year")
    if year != expected_year:
        raise BoundaryGapArtifactError(
            f"Expected year={expected_year!r} for {timestamp}, got {year!r}"
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
        "action_edge": _coerce_optional_numeric(
            row.get("action_edge"),
            field_name="action_edge",
        ),
        "confidence_gate": _coerce_optional_numeric(
            row.get("confidence_gate"),
            field_name="confidence_gate",
        ),
        "clarity_score": _coerce_optional_numeric(
            row.get("clarity_score"),
            field_name="clarity_score",
        ),
        "clarity_raw": _coerce_optional_numeric(
            row.get("clarity_raw"),
            field_name="clarity_raw",
        ),
        "dwell_duration": _coerce_optional_numeric(
            row.get("dwell_duration"),
            field_name="dwell_duration",
        ),
        "fwd_4_close_return_pct": _coerce_optional_numeric(
            row.get("fwd_4_close_return_pct"),
            field_name="fwd_4_close_return_pct",
        ),
        "fwd_8_close_return_pct": _coerce_optional_numeric(
            row.get("fwd_8_close_return_pct"),
            field_name="fwd_8_close_return_pct",
        ),
        "fwd_16_close_return_pct": _coerce_optional_numeric(
            row.get("fwd_16_close_return_pct"),
            field_name="fwd_16_close_return_pct",
        ),
        "mfe_16_pct": _coerce_optional_numeric(
            row.get("mfe_16_pct"),
            field_name="mfe_16_pct",
        ),
        "mae_16_pct": _coerce_optional_numeric(
            row.get("mae_16_pct"),
            field_name="mae_16_pct",
        ),
    }


def _extract_cohort_rows(
    artifact: dict[str, Any],
    *,
    cohort_name: str,
    row_role: str,
    claim_eligible: bool,
    expected_year: str,
) -> list[dict[str, Any]]:
    cohorts = artifact.get("cohorts")
    if not isinstance(cohorts, dict):
        raise BoundaryGapArtifactError("Artifact is missing a cohort registry")
    cohort_summary = cohorts.get(cohort_name)
    if not isinstance(cohort_summary, dict):
        raise BoundaryGapArtifactError(f"Artifact is missing cohort {cohort_name!r}")
    rows = cohort_summary.get("rows")
    if not isinstance(rows, list):
        raise BoundaryGapArtifactError(f"Cohort {cohort_name!r} is missing row payloads")
    normalized_rows = []
    for item in rows:
        if not isinstance(item, dict):
            raise BoundaryGapArtifactError(
                f"Expected object rows in cohort {cohort_name!r}, got {item!r}"
            )
        normalized_rows.append(
            _normalize_row(
                item,
                cohort_name=cohort_name,
                row_role=row_role,
                claim_eligible=claim_eligible,
                expected_year=expected_year,
            )
        )
    return sorted(normalized_rows, key=lambda row: row["timestamp"])


def _assert_exact_timestamps(
    rows: list[dict[str, Any]],
    *,
    cohort_name: str,
    expected_timestamps: tuple[str, ...],
) -> None:
    actual_timestamps = tuple(row["timestamp"] for row in rows)
    if actual_timestamps != expected_timestamps:
        raise BoundaryGapArtifactError(
            f"Timestamp drift for {cohort_name}: expected {expected_timestamps!r}, "
            f"got {actual_timestamps!r}"
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
                raise BoundaryGapArtifactError(
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
            raise BoundaryGapArtifactError(
                f"Locked row contract mismatch for {cohort_name} on {row['timestamp']}: "
                f"expected {field_name} in {sorted(allowed_values)!r}, "
                f"got {row.get(field_name)!r}"
            )


def _assert_same_shared_surface(
    primary_rows: list[dict[str, Any]],
    secondary_rows: list[dict[str, Any]],
    *,
    cohort_name: str,
) -> None:
    if len(primary_rows) != len(secondary_rows):
        raise BoundaryGapArtifactError(f"Shared 2019 surface row-count drift for {cohort_name}")
    secondary_by_timestamp = {row["timestamp"]: row for row in secondary_rows}
    for primary_row in primary_rows:
        timestamp = primary_row["timestamp"]
        secondary_row = secondary_by_timestamp.get(timestamp)
        if secondary_row is None:
            raise BoundaryGapArtifactError(
                f"Shared 2019 surface drift for {cohort_name}: missing {timestamp} "
                "in second artifact"
            )
        for field_name in ROW_COMPARE_FIELDS:
            if primary_row.get(field_name) != secondary_row.get(field_name):
                raise BoundaryGapArtifactError(
                    f"Shared 2019 surface mismatch for {cohort_name} at {timestamp}: "
                    f"field {field_name!r} differs between source artifacts"
                )


def _build_surface_summary(
    target_rows: list[dict[str, Any]],
    context_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    target_metric_summary = {
        field_name: _summarize_numeric_values(
            [
                float(row[field_name])
                for row in target_rows
                if isinstance(row.get(field_name), int | float)
            ]
        )
        for field_name in SURFACE_SUMMARY_FIELDS
    }
    context_metric_summary = {
        field_name: _summarize_numeric_values(
            [
                float(row[field_name])
                for row in context_rows
                if isinstance(row.get(field_name), int | float)
            ]
        )
        for field_name in SURFACE_SUMMARY_FIELDS
    }
    return {
        "target_row_count": len(target_rows),
        "context_row_count": len(context_rows),
        "target_timestamps": [row["timestamp"] for row in target_rows],
        "context_timestamps": [row["timestamp"] for row in context_rows],
        "target_metric_summary": target_metric_summary,
        "context_metric_summary": context_metric_summary,
    }


def _row_gap_payload(
    rows: list[dict[str, Any]],
    *,
    field_name: str,
    context_floor: float,
) -> list[dict[str, Any]]:
    gap_rows = []
    for row in rows:
        value = row.get(field_name)
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise BoundaryGapArtifactError(
                f"Cannot compute gap for {field_name} on {row['timestamp']} without a "
                "direct numeric row value"
            )
        gap_rows.append(
            {
                "timestamp": row["timestamp"],
                "field_value": _round_or_none(float(value)),
                "boundary_gap": _round_or_none(context_floor - float(value)),
            }
        )
    return gap_rows


def _range_comparison(
    harmful_summary: dict[str, Any],
    control_summary: dict[str, Any],
) -> dict[str, Any]:
    harmful_min = harmful_summary["min"]
    harmful_max = harmful_summary["max"]
    control_min = control_summary["min"]
    control_max = control_summary["max"]
    if None in {harmful_min, harmful_max, control_min, control_max}:
        return {
            "harmful_range": None,
            "control_range": None,
            "non_overlap": None,
            "harmful_strictly_smaller": None,
            "required_order_holds": None,
            "separation_margin": None,
        }

    harmful_range = [harmful_min, harmful_max]
    control_range = [control_min, control_max]
    non_overlap = float(harmful_max) < float(control_min) or float(control_max) < float(harmful_min)
    harmful_strictly_smaller = float(harmful_max) < float(control_min)
    separation_margin = None
    if harmful_strictly_smaller:
        separation_margin = _round_or_none(float(control_min) - float(harmful_max))
    return {
        "harmful_range": harmful_range,
        "control_range": control_range,
        "non_overlap": non_overlap,
        "harmful_strictly_smaller": harmful_strictly_smaller,
        "required_order_holds": harmful_strictly_smaller and non_overlap,
        "separation_margin": separation_margin,
    }


def _evaluate_field(
    field_definition: FieldDefinition,
    *,
    surfaces: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    surface_context_floors: dict[str, dict[str, Any]] = {}
    target_boundary_gaps: dict[str, list[dict[str, Any]]] = {}
    gap_range_summary: dict[str, dict[str, Any]] = {}

    for surface_id, surface in surfaces.items():
        context_rows = surface["context_rows"]
        target_rows = surface["target_rows"]
        missing_context = [
            row["timestamp"]
            for row in context_rows
            if isinstance(row.get(field_definition.field_name), bool)
            or not isinstance(row.get(field_definition.field_name), int | float)
        ]
        missing_target = [
            row["timestamp"]
            for row in target_rows
            if isinstance(row.get(field_definition.field_name), bool)
            or not isinstance(row.get(field_definition.field_name), int | float)
        ]
        if missing_context or missing_target:
            if field_definition.missing_policy == "not_evaluable":
                return {
                    "field_name": field_definition.field_name,
                    "descriptive_only": field_definition.descriptive_only,
                    "field_evaluability": {
                        "status": "not_evaluable",
                        "reason": "not_present_on_every_required_row",
                        "missing_context_timestamps": missing_context,
                        "missing_target_timestamps": missing_target,
                    },
                    "surface_context_floors": None,
                    "target_boundary_gaps": None,
                    "gap_range_summary": None,
                    "pairwise_comparisons": None,
                    "bounded_signal_present": False,
                    "excluded_from_pass_fail": field_definition.descriptive_only,
                }
            raise BoundaryGapArtifactError(
                f"Required claim field {field_definition.field_name!r} is missing on "
                f"surface {surface_id}: contexts={missing_context}, targets={missing_target}"
            )

        context_values = [float(row[field_definition.field_name]) for row in context_rows]
        context_floor = min(context_values)
        floor_source_timestamps = [
            row["timestamp"]
            for row in context_rows
            if float(row[field_definition.field_name]) == context_floor
        ]
        gap_rows = _row_gap_payload(
            target_rows,
            field_name=field_definition.field_name,
            context_floor=context_floor,
        )
        gap_values = [float(row["boundary_gap"]) for row in gap_rows]
        surface_context_floors[surface_id] = {
            "value": _round_or_none(context_floor),
            "context_row_count": len(context_rows),
            "source_timestamps": floor_source_timestamps,
        }
        target_boundary_gaps[surface_id] = gap_rows
        gap_range_summary[surface_id] = _summarize_numeric_values(gap_values)

    harmful_summary = gap_range_summary["harmful_2019"]
    control_2022_summary = gap_range_summary["control_2022"]
    control_2025_summary = gap_range_summary["control_2025"]
    pairwise_comparisons = {
        "harmful_vs_control_2022": _range_comparison(harmful_summary, control_2022_summary),
        "harmful_vs_control_2025": _range_comparison(harmful_summary, control_2025_summary),
    }
    bounded_signal_present = (
        not field_definition.descriptive_only
        and pairwise_comparisons["harmful_vs_control_2022"]["required_order_holds"] is True
        and pairwise_comparisons["harmful_vs_control_2025"]["required_order_holds"] is True
    )
    return {
        "field_name": field_definition.field_name,
        "descriptive_only": field_definition.descriptive_only,
        "field_evaluability": {
            "status": "evaluable",
            "reason": None,
            "missing_context_timestamps": [],
            "missing_target_timestamps": [],
        },
        "surface_context_floors": surface_context_floors,
        "target_boundary_gaps": target_boundary_gaps,
        "gap_range_summary": gap_range_summary,
        "pairwise_comparisons": pairwise_comparisons,
        "bounded_signal_present": bounded_signal_present,
        "excluded_from_pass_fail": field_definition.descriptive_only,
    }


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


def _truth_polarity(surfaces: dict[str, dict[str, Any]]) -> dict[str, Any]:
    harmful_mean = surfaces["harmful_2019"]["summary"]["target_metric_summary"][
        "fwd_16_close_return_pct"
    ]["mean"]
    control_2022_mean = surfaces["control_2022"]["summary"]["target_metric_summary"][
        "fwd_16_close_return_pct"
    ]["mean"]
    control_2025_mean = surfaces["control_2025"]["summary"]["target_metric_summary"][
        "fwd_16_close_return_pct"
    ]["mean"]

    harmful_proxy_holds = harmful_mean is not None and float(harmful_mean) > 0.0
    control_2022_proxy_holds = control_2022_mean is not None and float(control_2022_mean) < 0.0
    control_2025_proxy_holds = control_2025_mean is not None and float(control_2025_mean) < 0.0

    if not harmful_proxy_holds:
        raise BoundaryGapArtifactError(
            "2019-06 harmful target no longer reads as harmful-looking on the offline proxy"
        )
    if not control_2022_proxy_holds:
        raise BoundaryGapArtifactError(
            "2022-06 control target no longer reads as correct-suppression-looking on the "
            "offline proxy"
        )
    if not control_2025_proxy_holds:
        raise BoundaryGapArtifactError(
            "2025-03 control target no longer reads as correct-suppression-looking on the "
            "offline proxy"
        )

    return {
        "harmful_2019_target_fwd_16_mean": harmful_mean,
        "control_2022_target_fwd_16_mean": control_2022_mean,
        "control_2025_target_fwd_16_mean": control_2025_mean,
        "harmful_target_harmful_proxy_holds": harmful_proxy_holds,
        "control_2022_target_correct_suppression_proxy_holds": control_2022_proxy_holds,
        "control_2025_target_correct_suppression_proxy_holds": control_2025_proxy_holds,
    }


def _load_boundary_gap_surfaces() -> dict[str, Any]:
    first_artifact_path = ROOT_DIR / FIRST_PAIR_ARTIFACT
    second_artifact_path = ROOT_DIR / SECOND_PAIR_ARTIFACT
    first_artifact = _load_json_file(first_artifact_path)
    second_artifact = _load_json_file(second_artifact_path)

    _assert_top_level_true(
        first_artifact,
        field_name="context_rows_excluded_from_selection",
        label="first_pair",
    )
    _assert_top_level_true(
        second_artifact,
        field_name="context_rows_excluded_from_selection",
        label="second_pair",
    )

    first_subject = first_artifact.get("subject")
    second_subject = second_artifact.get("subject")
    if not isinstance(first_subject, dict) or not isinstance(second_subject, dict):
        raise BoundaryGapArtifactError("Source artifacts are missing subject metadata")
    if (
        first_subject.get("symbol") != SUBJECT_SYMBOL
        or second_subject.get("symbol") != SUBJECT_SYMBOL
    ):
        raise BoundaryGapArtifactError("Source artifact symbol drift detected")
    if (
        first_subject.get("timeframe") != SUBJECT_TIMEFRAME
        or second_subject.get("timeframe") != SUBJECT_TIMEFRAME
    ):
        raise BoundaryGapArtifactError("Source artifact timeframe drift detected")

    first_harmful_target = _extract_cohort_rows(
        first_artifact,
        cohort_name="harmful_target",
        row_role="harmful_target",
        claim_eligible=True,
        expected_year="2019",
    )
    first_harmful_context = _extract_cohort_rows(
        first_artifact,
        cohort_name="harmful_context",
        row_role="context",
        claim_eligible=False,
        expected_year="2019",
    )
    second_harmful_target = _extract_cohort_rows(
        second_artifact,
        cohort_name="harmful_target",
        row_role="harmful_target",
        claim_eligible=True,
        expected_year="2019",
    )
    second_harmful_context = _extract_cohort_rows(
        second_artifact,
        cohort_name="harmful_context",
        row_role="context",
        claim_eligible=False,
        expected_year="2019",
    )
    control_2022_target = _extract_cohort_rows(
        first_artifact,
        cohort_name="control_target",
        row_role="control_target",
        claim_eligible=True,
        expected_year="2022",
    )
    control_2022_context = _extract_cohort_rows(
        first_artifact,
        cohort_name="control_context",
        row_role="context",
        claim_eligible=False,
        expected_year="2022",
    )
    control_2025_target = _extract_cohort_rows(
        second_artifact,
        cohort_name="control_target",
        row_role="control_target",
        claim_eligible=True,
        expected_year="2025",
    )
    control_2025_displacement = _extract_cohort_rows(
        second_artifact,
        cohort_name="control_displacement_context",
        row_role="context",
        claim_eligible=False,
        expected_year="2025",
    )
    control_2025_blocked = _extract_cohort_rows(
        second_artifact,
        cohort_name="control_blocked_context",
        row_role="context",
        claim_eligible=False,
        expected_year="2025",
    )
    control_2025_aged_weak = _extract_cohort_rows(
        second_artifact,
        cohort_name="control_aged_weak_context",
        row_role="context",
        claim_eligible=False,
        expected_year="2025",
    )

    _assert_exact_timestamps(
        first_harmful_target,
        cohort_name="harmful_target",
        expected_timestamps=HARMFUL_TARGET_TIMESTAMPS,
    )
    _assert_exact_timestamps(
        first_harmful_context,
        cohort_name="harmful_context",
        expected_timestamps=HARMFUL_CONTEXT_TIMESTAMPS,
    )
    _assert_exact_timestamps(
        second_harmful_target,
        cohort_name="harmful_target(second_artifact)",
        expected_timestamps=HARMFUL_TARGET_TIMESTAMPS,
    )
    _assert_exact_timestamps(
        second_harmful_context,
        cohort_name="harmful_context(second_artifact)",
        expected_timestamps=HARMFUL_CONTEXT_TIMESTAMPS,
    )
    _assert_exact_timestamps(
        control_2022_target,
        cohort_name="control_target_2022",
        expected_timestamps=CONTROL_2022_TARGET_TIMESTAMPS,
    )
    _assert_exact_timestamps(
        control_2022_context,
        cohort_name="control_context_2022",
        expected_timestamps=CONTROL_2022_CONTEXT_TIMESTAMPS,
    )
    _assert_exact_timestamps(
        control_2025_target,
        cohort_name="control_target_2025",
        expected_timestamps=CONTROL_2025_TARGET_TIMESTAMPS,
    )
    _assert_exact_timestamps(
        control_2025_displacement,
        cohort_name="control_displacement_context_2025",
        expected_timestamps=CONTROL_2025_DISPLACEMENT_TIMESTAMPS,
    )
    _assert_exact_timestamps(
        control_2025_blocked,
        cohort_name="control_blocked_context_2025",
        expected_timestamps=CONTROL_2025_BLOCKED_CONTEXT_TIMESTAMPS,
    )
    _assert_exact_timestamps(
        control_2025_aged_weak,
        cohort_name="control_aged_weak_context_2025",
        expected_timestamps=CONTROL_2025_AGED_WEAK_CONTEXT_TIMESTAMPS,
    )

    _assert_same_shared_surface(
        first_harmful_target,
        second_harmful_target,
        cohort_name="harmful_target",
    )
    _assert_same_shared_surface(
        first_harmful_context,
        second_harmful_context,
        cohort_name="harmful_context",
    )

    _assert_row_values(
        first_harmful_target,
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
        first_harmful_context,
        cohort_name="harmful_context",
        expected_values={
            "zone": "low",
            "candidate": "LONG",
            "absent_action": "LONG",
            "enabled_action": "NONE",
            "selected_policy": "RI_no_trade_policy",
            "switch_reason": "AGED_WEAK_CONTINUATION_GUARD",
            "action_pair": "LONG->NONE",
        },
    )
    _assert_row_values(
        control_2022_target,
        cohort_name="control_target_2022",
        expected_values={
            "zone": "low",
            "candidate": "LONG",
            "absent_action": "LONG",
            "enabled_action": "NONE",
            "selected_policy": "RI_no_trade_policy",
            "switch_reason": "insufficient_evidence",
            "action_pair": "LONG->NONE",
            "bars_since_regime_change": 184,
        },
    )
    _assert_row_values(
        control_2022_context,
        cohort_name="control_context_2022",
        expected_values={
            "zone": "low",
            "candidate": "LONG",
            "selected_policy": "RI_continuation_policy",
            "switch_reason": "stable_continuation_state",
        },
    )
    _assert_row_allowed_values(
        control_2022_context,
        cohort_name="control_context_2022",
        field_name="action_pair",
        allowed_values={"NONE->LONG", "LONG->NONE"},
    )
    _assert_row_allowed_values(
        control_2022_context,
        cohort_name="control_context_2022",
        field_name="bars_since_regime_change",
        allowed_values={182, 183},
    )
    _assert_row_values(
        control_2025_target,
        cohort_name="control_target_2025",
        expected_values={
            "zone": "low",
            "candidate": "LONG",
            "absent_action": "LONG",
            "enabled_action": "NONE",
            "selected_policy": "RI_no_trade_policy",
            "switch_reason": "insufficient_evidence",
            "action_pair": "LONG->NONE",
            "bars_since_regime_change": 65,
        },
    )
    _assert_row_values(
        control_2025_displacement,
        cohort_name="control_displacement_context_2025",
        expected_values={
            "zone": "low",
            "candidate": "LONG",
            "absent_action": "NONE",
            "enabled_action": "LONG",
            "selected_policy": "RI_continuation_policy",
            "switch_reason": "stable_continuation_state",
            "action_pair": "NONE->LONG",
        },
    )
    _assert_row_allowed_values(
        control_2025_displacement,
        cohort_name="control_displacement_context_2025",
        field_name="bars_since_regime_change",
        allowed_values={63, 64},
    )
    _assert_row_values(
        control_2025_blocked,
        cohort_name="control_blocked_context_2025",
        expected_values={
            "zone": "low",
            "candidate": "LONG",
            "absent_action": "LONG",
            "enabled_action": "NONE",
            "selected_policy": "RI_continuation_policy",
            "switch_reason": "stable_continuation_state",
            "action_pair": "LONG->NONE",
        },
    )
    _assert_row_allowed_values(
        control_2025_blocked,
        cohort_name="control_blocked_context_2025",
        field_name="bars_since_regime_change",
        allowed_values={63, 64},
    )
    _assert_row_values(
        control_2025_aged_weak,
        cohort_name="control_aged_weak_context_2025",
        expected_values={
            "zone": "low",
            "candidate": "LONG",
            "absent_action": "LONG",
            "enabled_action": "NONE",
            "selected_policy": "RI_no_trade_policy",
            "switch_reason": "AGED_WEAK_CONTINUATION_GUARD",
            "action_pair": "LONG->NONE",
            "bars_since_regime_change": 65,
        },
    )

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
            "target_rows": first_harmful_target,
            "context_rows": first_harmful_context,
            "summary": _build_surface_summary(first_harmful_target, first_harmful_context),
        },
        "control_2022": {
            "surface_id": "control_2022",
            "surface_role": "control",
            "primary_source": "first_pair_artifact",
            "target_rows": control_2022_target,
            "context_rows": control_2022_context,
            "summary": _build_surface_summary(control_2022_target, control_2022_context),
        },
        "control_2025": {
            "surface_id": "control_2025",
            "surface_role": "control",
            "primary_source": "second_pair_artifact",
            "target_rows": control_2025_target,
            "context_rows": control_2025_context,
            "summary": _build_surface_summary(control_2025_target, control_2025_context),
        },
    }
    return {
        "surfaces": surfaces,
        "source_artifacts": {
            "first_pair_artifact": {
                "path": str(FIRST_PAIR_ARTIFACT),
                "audit_version": first_artifact.get("audit_version"),
                "status": first_artifact.get("status"),
                "base_sha": first_artifact.get("base_sha"),
            },
            "second_pair_artifact": {
                "path": str(SECOND_PAIR_ARTIFACT),
                "audit_version": second_artifact.get("audit_version"),
                "status": second_artifact.get("status"),
                "base_sha": second_artifact.get("base_sha"),
            },
        },
    }


def run_boundary_gap_analysis(base_sha: str) -> dict[str, Any]:
    surface_payload = _load_boundary_gap_surfaces()
    surfaces = surface_payload["surfaces"]
    truth_polarity = _truth_polarity(surfaces)

    field_evaluations = [
        _evaluate_field(field_definition, surfaces=surfaces)
        for field_definition in FIELD_DEFINITIONS
    ]
    non_null_fields = [
        evaluation["field_name"]
        for evaluation in field_evaluations
        if evaluation["bounded_signal_present"]
    ]
    descriptive_only_fields = [
        evaluation["field_name"]
        for evaluation in field_evaluations
        if evaluation["descriptive_only"]
    ]
    not_evaluable_fields = [
        evaluation["field_name"]
        for evaluation in field_evaluations
        if evaluation["field_evaluability"]["status"] != "evaluable"
    ]
    claim_fields_without_signal = [
        evaluation["field_name"]
        for evaluation in field_evaluations
        if not evaluation["descriptive_only"]
        and evaluation["field_evaluability"]["status"] == "evaluable"
        and not evaluation["bounded_signal_present"]
    ]

    status = (
        "bounded_boundary_gap_signal_present" if non_null_fields else "bounded_boundary_gap_null"
    )

    return {
        "audit_version": (
            "ri-policy-router-insufficient-evidence-d1-boundary-gap-to-local-context-floor-"
            "2026-05-04"
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
            "residual_method_reference": str(RESIDUAL_METHOD_REFERENCE),
            "residual_method_packet_reference": str(RESIDUAL_METHOD_PACKET_REFERENCE),
            "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
        },
        "fail_closed_contract": {
            "statement": (
                "The helper reads only the two committed D1 evaluation artifacts, asserts the "
                "fixed 2019/2022/2025 row locks and the repeated 2019 surface match, computes "
                "only the pre-registered all-context-floor boundary gaps on admitted fields, "
                "excludes all context rows from PASS/FAIL adjudication, and keeps every outcome "
                "exact-surface only, descriptive only, and non-authoritative."
            )
        },
        "search_boundary": {
            "statement": (
                "No threshold search, conjunction search, baseline switching, raw-source reread, "
                "year widening, or subgroup retry is allowed. This slice rereads only the fixed "
                "D1 family as boundary gaps to the local context floor."
            )
        },
        "inputs": surface_payload["source_artifacts"],
        "artifact_row_lock": {
            "harmful_target_timestamps": [
                row["timestamp"] for row in surfaces["harmful_2019"]["target_rows"]
            ],
            "harmful_context_timestamps": [
                row["timestamp"] for row in surfaces["harmful_2019"]["context_rows"]
            ],
            "control_2022_target_timestamps": [
                row["timestamp"] for row in surfaces["control_2022"]["target_rows"]
            ],
            "control_2022_context_timestamps": [
                row["timestamp"] for row in surfaces["control_2022"]["context_rows"]
            ],
            "control_2025_target_timestamps": [
                row["timestamp"] for row in surfaces["control_2025"]["target_rows"]
            ],
            "control_2025_context_timestamps": [
                row["timestamp"] for row in surfaces["control_2025"]["context_rows"]
            ],
            "shared_2019_surface_match": True,
            "context_rows_excluded_from_selection": True,
            "observational_only_authority": True,
            "row_role_registry": _build_row_role_registry(surfaces),
        },
        "truth_polarity": truth_polarity,
        "surfaces": {
            surface_id: {
                "surface_role": surface["surface_role"],
                "primary_source": surface["primary_source"],
                "secondary_source": surface.get("secondary_source"),
                **surface["summary"],
            }
            for surface_id, surface in surfaces.items()
        },
        "boundary_gap_summary": {
            "non_null_field_names": non_null_fields,
            "claim_fields_without_signal": claim_fields_without_signal,
            "descriptive_only_field_names": descriptive_only_fields,
            "not_evaluable_field_names": not_evaluable_fields,
            "bounded_signal_present": bool(non_null_fields),
        },
        "field_boundary_gap_evaluations": field_evaluations,
    }


def main() -> int:
    args = _parse_args()
    output_root = ROOT_DIR / Path(args.output_root_relative)
    output_json = output_root / args.summary_filename
    result = run_boundary_gap_analysis(base_sha=args.base_sha)

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "summary_artifact": str(output_json),
                "status": result["status"],
                "non_null_field_names": result["boundary_gap_summary"]["non_null_field_names"],
                "claim_fields_without_signal": result["boundary_gap_summary"][
                    "claim_fields_without_signal"
                ],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
