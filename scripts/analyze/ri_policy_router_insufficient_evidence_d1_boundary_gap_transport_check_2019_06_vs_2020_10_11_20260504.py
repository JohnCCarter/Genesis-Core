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
    "ri_policy_router_insufficient_evidence_d1_boundary_gap_transport_check_"
    "2019_06_vs_2020_10_11_2026-05-04.json"
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
BOUNDARY_GAP_ARTIFACT = Path(
    "results/evaluation/"
    "ri_policy_router_insufficient_evidence_d1_boundary_gap_to_local_context_floor_"
    "2026-05-04.json"
)
TRUTH_SURFACE_ARTIFACT = Path(
    "results/evaluation/"
    "ri_policy_router_insufficient_evidence_truth_surface_correction_2026-04-30.json"
)
CONTROL_2020_ACTION_DIFF = Path(
    "results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/"
    "2020_enabled_vs_absent_action_diffs.json"
)
PACKET_REFERENCE = Path(
    "docs/decisions/regime_intelligence/policy_router/"
    "ri_policy_router_insufficient_evidence_d1_boundary_gap_transport_check_"
    "2019_06_vs_2020_10_11_precode_packet_2026-05-04.md"
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
TRUTH_SURFACE_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_insufficient_evidence_truth_surface_correction_2026-04-30.md"
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
CONTROL_2020_TARGET_TIMESTAMPS = (
    "2020-10-31T21:00:00+00:00",
    "2020-11-01T06:00:00+00:00",
    "2020-11-01T15:00:00+00:00",
    "2020-11-02T00:00:00+00:00",
)
CONTROL_2020_DISPLACEMENT_TIMESTAMPS = (
    "2020-11-02T03:00:00+00:00",
    "2020-11-02T21:00:00+00:00",
)
CONTROL_2020_BLOCKED_CONTEXT_TIMESTAMPS = (
    "2020-11-02T09:00:00+00:00",
    "2020-11-03T03:00:00+00:00",
)
PRIMARY_FIELD_NAMES = ("action_edge", "confidence_gate", "clarity_raw")
DESCRIPTIVE_FIELD_NAMES = ("clarity_score", "bars_since_regime_change")
SURFACE_SUMMARY_FIELDS = (
    "action_edge",
    "confidence_gate",
    "clarity_raw",
    "clarity_score",
    "bars_since_regime_change",
    "fwd_16_close_return_pct",
)
SHARED_RAW_COMPARE_FIELDS = (
    "zone",
    "candidate",
    "switch_reason",
    "selected_policy",
    "absent_action",
    "enabled_action",
    "action_pair",
    "bars_since_regime_change",
    "action_edge",
    "confidence_gate",
    "clarity_score",
)


class TransportCheckError(RuntimeError):
    """Raised when the fixed transport-check contract drifts."""


@dataclass(frozen=True)
class FieldDefinition:
    field_name: str
    descriptive_only: bool


FIELD_DEFINITIONS = (
    FieldDefinition(field_name="action_edge", descriptive_only=False),
    FieldDefinition(field_name="confidence_gate", descriptive_only=False),
    FieldDefinition(field_name="clarity_raw", descriptive_only=False),
    FieldDefinition(field_name="clarity_score", descriptive_only=True),
    FieldDefinition(field_name="bars_since_regime_change", descriptive_only=True),
)


@dataclass(frozen=True)
class RawActionDiffRow:
    timestamp: str
    zone: str
    candidate: str
    switch_reason: str
    selected_policy: str
    raw_target_policy: str
    previous_policy: str
    absent_action: str
    enabled_action: str
    action_pair: str
    bars_since_regime_change: int
    action_edge: float | None
    confidence_gate: float | None
    clarity_score: float | None
    clarity_raw: float | None


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Materialize one source-backed D1 boundary-gap transport check on the fixed "
            "2019-06 harmful anchor versus the exact 2020-10/11 weak-control cluster."
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
        raise TransportCheckError(
            f"Expected numeric optional value for {field_name}, got {value!r}"
        )
    numeric_value = float(value)
    if numeric_value != numeric_value or numeric_value in {float("inf"), float("-inf")}:
        raise TransportCheckError(f"Expected finite optional value for {field_name}, got {value!r}")
    return _round_or_none(numeric_value)


def _coerce_required_int(value: Any, *, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TransportCheckError(f"Expected integer value for {field_name}, got {value!r}")
    return int(value)


def _coerce_required_str(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise TransportCheckError(f"Expected string value for {field_name}, got {value!r}")
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
        raise TransportCheckError(f"Required JSON input not found: {path}") from exc


def _assert_top_level_true(payload: dict[str, Any], *, field_name: str, label: str) -> None:
    if payload.get(field_name) is not True:
        raise TransportCheckError(f"Artifact {label} must keep {field_name}=true for this slice")


def _assert_exact_timestamps(
    rows: list[dict[str, Any]],
    *,
    cohort_name: str,
    expected_timestamps: tuple[str, ...],
) -> None:
    actual_timestamps = tuple(row["timestamp"] for row in rows)
    if actual_timestamps != expected_timestamps:
        raise TransportCheckError(
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
                raise TransportCheckError(
                    f"Locked row contract mismatch for {cohort_name} on {row['timestamp']}: "
                    f"expected {field_name}={expected_value!r}, got {row.get(field_name)!r}"
                )


def _normalize_harmful_artifact_row(
    row: dict[str, Any],
    *,
    cohort_name: str,
    row_role: str,
    claim_eligible: bool,
    expected_year: str,
) -> dict[str, Any]:
    timestamp = _coerce_required_str(row.get("timestamp"), field_name="timestamp")
    if row.get("year") != expected_year:
        raise TransportCheckError(
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
        "fwd_4_close_return_pct": _coerce_optional_numeric(
            row.get("fwd_4_close_return_pct"), field_name="fwd_4_close_return_pct"
        ),
        "fwd_8_close_return_pct": _coerce_optional_numeric(
            row.get("fwd_8_close_return_pct"), field_name="fwd_8_close_return_pct"
        ),
        "fwd_16_close_return_pct": _coerce_optional_numeric(
            row.get("fwd_16_close_return_pct"), field_name="fwd_16_close_return_pct"
        ),
        "mfe_16_pct": _coerce_optional_numeric(row.get("mfe_16_pct"), field_name="mfe_16_pct"),
        "mae_16_pct": _coerce_optional_numeric(row.get("mae_16_pct"), field_name="mae_16_pct"),
    }


def _extract_harmful_rows(
    artifact: dict[str, Any],
    *,
    cohort_name: str,
    row_role: str,
    claim_eligible: bool,
    expected_year: str,
) -> list[dict[str, Any]]:
    cohorts = artifact.get("cohorts")
    if not isinstance(cohorts, dict):
        raise TransportCheckError("D1 artifact is missing a cohort registry")
    cohort_summary = cohorts.get(cohort_name)
    if not isinstance(cohort_summary, dict):
        raise TransportCheckError(f"D1 artifact is missing cohort {cohort_name!r}")
    rows = cohort_summary.get("rows")
    if not isinstance(rows, list):
        raise TransportCheckError(f"Cohort {cohort_name!r} is missing row payloads")
    normalized_rows = [
        _normalize_harmful_artifact_row(
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


def _assert_same_harmful_surface(
    primary_rows: list[dict[str, Any]],
    secondary_rows: list[dict[str, Any]],
    *,
    cohort_name: str,
) -> None:
    if len(primary_rows) != len(secondary_rows):
        raise TransportCheckError(f"Shared harmful surface row-count drift for {cohort_name}")
    secondary_by_timestamp = {row["timestamp"]: row for row in secondary_rows}
    for primary_row in primary_rows:
        secondary_row = secondary_by_timestamp.get(primary_row["timestamp"])
        if secondary_row is None:
            raise TransportCheckError(
                f"Shared harmful surface missing timestamp {primary_row['timestamp']} "
                f"in second artifact for cohort {cohort_name}"
            )
        for field_name, primary_value in primary_row.items():
            if secondary_row.get(field_name) != primary_value:
                raise TransportCheckError(
                    f"Shared harmful surface mismatch for {cohort_name} at "
                    f"{primary_row['timestamp']}: field {field_name!r} differs"
                )


def _normalize_truth_surface_row(
    row: dict[str, Any],
    *,
    cohort_name: str,
    row_role: str,
    claim_eligible: bool,
) -> dict[str, Any]:
    timestamp = _coerce_required_str(row.get("timestamp"), field_name="timestamp")
    year = _coerce_required_str(row.get("year"), field_name="year")
    return {
        "timestamp": timestamp,
        "cohort_name": cohort_name,
        "row_role": row_role,
        "claim_eligible": claim_eligible,
        "year": year,
        "switch_reason": _coerce_required_str(row.get("switch_reason"), field_name="switch_reason"),
        "absent_action": _coerce_required_str(row.get("absent_action"), field_name="absent_action"),
        "enabled_action": _coerce_required_str(
            row.get("enabled_action"), field_name="enabled_action"
        ),
        "action_pair": _coerce_required_str(row.get("action_pair"), field_name="action_pair"),
        "selected_policy": _coerce_required_str(
            row.get("selected_policy"), field_name="selected_policy"
        ),
        "raw_target_policy": _coerce_required_str(
            row.get("raw_target_policy"), field_name="raw_target_policy"
        ),
        "previous_policy": _coerce_required_str(
            row.get("previous_policy"), field_name="previous_policy"
        ),
        "zone": _coerce_required_str(row.get("zone"), field_name="zone"),
        "candidate": _coerce_required_str(row.get("candidate"), field_name="candidate"),
        "bars_since_regime_change": _coerce_required_int(
            row.get("bars_since_regime_change"), field_name="bars_since_regime_change"
        ),
        "action_edge": _coerce_optional_numeric(row.get("action_edge"), field_name="action_edge"),
        "confidence_gate": _coerce_optional_numeric(
            row.get("confidence_gate"), field_name="confidence_gate"
        ),
        "clarity_score": _coerce_optional_numeric(
            row.get("clarity_score"), field_name="clarity_score"
        ),
        "clarity_raw": None,
        "dwell_duration": None,
        "fwd_4_close_return_pct": _coerce_optional_numeric(
            row.get("fwd_4_close_return_pct"), field_name="fwd_4_close_return_pct"
        ),
        "fwd_8_close_return_pct": _coerce_optional_numeric(
            row.get("fwd_8_close_return_pct"), field_name="fwd_8_close_return_pct"
        ),
        "fwd_16_close_return_pct": _coerce_optional_numeric(
            row.get("fwd_16_close_return_pct"), field_name="fwd_16_close_return_pct"
        ),
        "mfe_16_pct": _coerce_optional_numeric(row.get("mfe_16_pct"), field_name="mfe_16_pct"),
        "mae_16_pct": _coerce_optional_numeric(row.get("mae_16_pct"), field_name="mae_16_pct"),
    }


def _extract_truth_surface_rows(
    artifact: dict[str, Any],
    *,
    cohort_name: str,
    row_role: str,
    claim_eligible: bool,
) -> list[dict[str, Any]]:
    cohorts = artifact.get("cohorts")
    if not isinstance(cohorts, dict):
        raise TransportCheckError("Truth-surface artifact is missing cohort registry")
    cohort_summary = cohorts.get(cohort_name)
    if not isinstance(cohort_summary, dict):
        raise TransportCheckError(f"Truth-surface artifact is missing cohort {cohort_name!r}")
    rows = cohort_summary.get("rows")
    if not isinstance(rows, list):
        raise TransportCheckError(f"Truth-surface cohort {cohort_name!r} is missing rows")
    normalized = [
        _normalize_truth_surface_row(
            row,
            cohort_name=cohort_name,
            row_role=row_role,
            claim_eligible=claim_eligible,
        )
        for row in rows
        if isinstance(row, dict)
    ]
    return sorted(normalized, key=lambda item: item["timestamp"])


def _load_raw_2020_rows(path: Path, *, locked_timestamps: set[str]) -> dict[str, RawActionDiffRow]:
    payload = _load_json_file(path)
    if not isinstance(payload, list):
        raise TransportCheckError(f"Expected list payload in {path}")
    extracted: dict[str, RawActionDiffRow] = {}
    for item in payload:
        if not isinstance(item, dict):
            raise TransportCheckError(f"Expected object rows in {path}")
        timestamp = _coerce_required_str(item.get("timestamp"), field_name="timestamp")
        if timestamp not in locked_timestamps:
            continue
        absent = item.get("absent") or {}
        enabled = item.get("enabled") or {}
        if not isinstance(absent, dict) or not isinstance(enabled, dict):
            raise TransportCheckError(f"Malformed action-diff row at {timestamp}")
        router_debug = enabled.get("router_debug")
        if not isinstance(router_debug, dict):
            raise TransportCheckError(f"Missing router_debug for locked 2020 row {timestamp}")
        absent_action = _coerce_required_str(absent.get("action"), field_name="absent.action")
        enabled_action = _coerce_required_str(enabled.get("action"), field_name="enabled.action")
        extracted[timestamp] = RawActionDiffRow(
            timestamp=timestamp,
            zone=_coerce_required_str(router_debug.get("zone"), field_name="zone"),
            candidate=_coerce_required_str(router_debug.get("candidate"), field_name="candidate"),
            switch_reason=_coerce_required_str(
                router_debug.get("switch_reason"), field_name="switch_reason"
            ),
            selected_policy=_coerce_required_str(
                router_debug.get("selected_policy"), field_name="selected_policy"
            ),
            raw_target_policy=_coerce_required_str(
                router_debug.get("raw_target_policy"), field_name="raw_target_policy"
            ),
            previous_policy=_coerce_required_str(
                router_debug.get("previous_policy"), field_name="previous_policy"
            ),
            absent_action=absent_action,
            enabled_action=enabled_action,
            action_pair=f"{absent_action}->{enabled_action}",
            bars_since_regime_change=_coerce_required_int(
                router_debug.get("bars_since_regime_change"),
                field_name="bars_since_regime_change",
            ),
            action_edge=_coerce_optional_numeric(
                router_debug.get("action_edge"), field_name="action_edge"
            ),
            confidence_gate=_coerce_optional_numeric(
                router_debug.get("confidence_gate"), field_name="confidence_gate"
            ),
            clarity_score=_coerce_optional_numeric(
                router_debug.get("clarity_score"), field_name="clarity_score"
            ),
            clarity_raw=_coerce_optional_numeric(
                router_debug.get("clarity_raw"), field_name="clarity_raw"
            ),
        )
    missing = sorted(locked_timestamps - set(extracted))
    if missing:
        raise TransportCheckError(
            f"Locked 2020 action-diff rows missing from raw source: {missing}"
        )
    return extracted


def _assert_raw_matches_truth_row(truth_row: dict[str, Any], raw_row: RawActionDiffRow) -> None:
    for field_name in SHARED_RAW_COMPARE_FIELDS:
        truth_value = truth_row.get(field_name)
        raw_value = getattr(raw_row, field_name)
        if isinstance(truth_value, float | int) and isinstance(raw_value, float | int):
            if _round_or_none(float(truth_value)) != _round_or_none(float(raw_value)):
                raise TransportCheckError(
                    f"Raw/truth mismatch at {truth_row['timestamp']} for field {field_name!r}: "
                    f"truth={truth_value!r}, raw={raw_value!r}"
                )
            continue
        if truth_value != raw_value:
            raise TransportCheckError(
                f"Raw/truth mismatch at {truth_row['timestamp']} for field {field_name!r}: "
                f"truth={truth_value!r}, raw={raw_value!r}"
            )


def _merge_control_row(truth_row: dict[str, Any], raw_row: RawActionDiffRow) -> dict[str, Any]:
    _assert_raw_matches_truth_row(truth_row, raw_row)
    merged = dict(truth_row)
    merged["clarity_raw"] = raw_row.clarity_raw
    merged["raw_target_policy"] = raw_row.raw_target_policy
    merged["previous_policy"] = raw_row.previous_policy
    return merged


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
            for field_name in SURFACE_SUMMARY_FIELDS
        },
        "context_metric_summary": {
            field_name: _summarize_numeric_values(
                [
                    float(row[field_name])
                    for row in context_rows
                    if isinstance(row.get(field_name), int | float)
                ]
            )
            for field_name in SURFACE_SUMMARY_FIELDS
        },
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
            raise TransportCheckError(
                f"Cannot compute gap for {field_name} on {row['timestamp']} without a numeric value"
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
        context_values = [float(row[field_definition.field_name]) for row in context_rows]
        context_floor = min(context_values)
        floor_source_timestamps = [
            row["timestamp"]
            for row in context_rows
            if float(row[field_definition.field_name]) == context_floor
        ]
        gap_rows = _row_gap_payload(
            target_rows, field_name=field_definition.field_name, context_floor=context_floor
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
    control_summary = gap_range_summary["control_2020"]
    pairwise_comparison = _range_comparison(harmful_summary, control_summary)
    bounded_signal_present = (
        not field_definition.descriptive_only
        and pairwise_comparison["required_order_holds"] is True
    )
    return {
        "field_name": field_definition.field_name,
        "descriptive_only": field_definition.descriptive_only,
        "surface_context_floors": surface_context_floors,
        "target_boundary_gaps": target_boundary_gaps,
        "gap_range_summary": gap_range_summary,
        "pairwise_comparison": pairwise_comparison,
        "bounded_signal_present": bounded_signal_present,
        "excluded_from_pass_fail": field_definition.descriptive_only,
    }


def _truth_polarity(surfaces: dict[str, dict[str, Any]]) -> dict[str, Any]:
    harmful_mean = surfaces["harmful_2019"]["summary"]["target_metric_summary"][
        "fwd_16_close_return_pct"
    ]["mean"]
    control_mean = surfaces["control_2020"]["summary"]["target_metric_summary"][
        "fwd_16_close_return_pct"
    ]["mean"]
    harmful_proxy_holds = harmful_mean is not None and float(harmful_mean) > 0.0
    control_proxy_holds = control_mean is not None and float(control_mean) < 0.0
    if not harmful_proxy_holds:
        raise TransportCheckError(
            "2019-06 harmful target no longer reads as harmful-looking on the offline proxy"
        )
    if not control_proxy_holds:
        raise TransportCheckError(
            "2020-10/11 control target no longer reads as correct-suppression-looking on the offline proxy"
        )
    return {
        "harmful_2019_target_fwd_16_mean": harmful_mean,
        "control_2020_target_fwd_16_mean": control_mean,
        "harmful_target_harmful_proxy_holds": harmful_proxy_holds,
        "control_2020_target_correct_suppression_proxy_holds": control_proxy_holds,
    }


def _load_transport_surfaces() -> dict[str, Any]:
    first_pair_artifact = _load_json_file(ROOT_DIR / FIRST_PAIR_ARTIFACT)
    second_pair_artifact = _load_json_file(ROOT_DIR / SECOND_PAIR_ARTIFACT)
    truth_surface_artifact = _load_json_file(ROOT_DIR / TRUTH_SURFACE_ARTIFACT)
    boundary_gap_artifact = _load_json_file(ROOT_DIR / BOUNDARY_GAP_ARTIFACT)
    raw_2020_path = ROOT_DIR / CONTROL_2020_ACTION_DIFF

    if not isinstance(first_pair_artifact, dict) or not isinstance(second_pair_artifact, dict):
        raise TransportCheckError("D1 source artifacts must be JSON objects")
    if not isinstance(truth_surface_artifact, dict) or not isinstance(boundary_gap_artifact, dict):
        raise TransportCheckError("Supporting artifacts must be JSON objects")

    _assert_top_level_true(
        first_pair_artifact, field_name="context_rows_excluded_from_selection", label="first_pair"
    )
    _assert_top_level_true(
        second_pair_artifact, field_name="context_rows_excluded_from_selection", label="second_pair"
    )
    _assert_top_level_true(
        boundary_gap_artifact,
        field_name="context_rows_excluded_from_selection",
        label="boundary_gap",
    )

    harmful_target = _extract_harmful_rows(
        first_pair_artifact,
        cohort_name="harmful_target",
        row_role="harmful_target",
        claim_eligible=True,
        expected_year="2019",
    )
    harmful_context = _extract_harmful_rows(
        first_pair_artifact,
        cohort_name="harmful_context",
        row_role="context",
        claim_eligible=False,
        expected_year="2019",
    )
    harmful_target_second = _extract_harmful_rows(
        second_pair_artifact,
        cohort_name="harmful_target",
        row_role="harmful_target",
        claim_eligible=True,
        expected_year="2019",
    )
    harmful_context_second = _extract_harmful_rows(
        second_pair_artifact,
        cohort_name="harmful_context",
        row_role="context",
        claim_eligible=False,
        expected_year="2019",
    )
    _assert_exact_timestamps(
        harmful_target, cohort_name="harmful_target", expected_timestamps=HARMFUL_TARGET_TIMESTAMPS
    )
    _assert_exact_timestamps(
        harmful_context,
        cohort_name="harmful_context",
        expected_timestamps=HARMFUL_CONTEXT_TIMESTAMPS,
    )
    _assert_same_harmful_surface(
        harmful_target, harmful_target_second, cohort_name="harmful_target"
    )
    _assert_same_harmful_surface(
        harmful_context, harmful_context_second, cohort_name="harmful_context"
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

    control_target_truth = _extract_truth_surface_rows(
        truth_surface_artifact,
        cohort_name="control_2020_target",
        row_role="control_target",
        claim_eligible=True,
    )
    control_displacement_truth = _extract_truth_surface_rows(
        truth_surface_artifact,
        cohort_name="control_2020_nearby_displacement",
        row_role="context",
        claim_eligible=False,
    )
    control_blocked_truth = _extract_truth_surface_rows(
        truth_surface_artifact,
        cohort_name="control_2020_nearby_blocked_context",
        row_role="context",
        claim_eligible=False,
    )
    _assert_exact_timestamps(
        control_target_truth,
        cohort_name="control_2020_target",
        expected_timestamps=CONTROL_2020_TARGET_TIMESTAMPS,
    )
    _assert_exact_timestamps(
        control_displacement_truth,
        cohort_name="control_2020_nearby_displacement",
        expected_timestamps=CONTROL_2020_DISPLACEMENT_TIMESTAMPS,
    )
    _assert_exact_timestamps(
        control_blocked_truth,
        cohort_name="control_2020_nearby_blocked_context",
        expected_timestamps=CONTROL_2020_BLOCKED_CONTEXT_TIMESTAMPS,
    )
    _assert_row_values(
        control_target_truth,
        cohort_name="control_2020_target",
        expected_values={
            "year": "2020",
            "zone": "low",
            "candidate": "LONG",
            "absent_action": "LONG",
            "enabled_action": "NONE",
            "switch_reason": "insufficient_evidence",
            "selected_policy": "RI_no_trade_policy",
            "bars_since_regime_change": 302,
        },
    )
    _assert_row_values(
        control_displacement_truth,
        cohort_name="control_2020_nearby_displacement",
        expected_values={
            "year": "2020",
            "zone": "low",
            "candidate": "LONG",
            "absent_action": "NONE",
            "enabled_action": "LONG",
            "switch_reason": "stable_continuation_state",
            "selected_policy": "RI_continuation_policy",
        },
    )
    _assert_row_values(
        control_blocked_truth,
        cohort_name="control_2020_nearby_blocked_context",
        expected_values={
            "year": "2020",
            "zone": "low",
            "candidate": "LONG",
            "absent_action": "LONG",
            "enabled_action": "NONE",
            "switch_reason": "stable_continuation_state",
            "selected_policy": "RI_continuation_policy",
        },
    )

    locked_2020_timestamps = {
        *CONTROL_2020_TARGET_TIMESTAMPS,
        *CONTROL_2020_DISPLACEMENT_TIMESTAMPS,
        *CONTROL_2020_BLOCKED_CONTEXT_TIMESTAMPS,
    }
    raw_2020_rows = _load_raw_2020_rows(raw_2020_path, locked_timestamps=locked_2020_timestamps)
    control_target_rows = [
        _merge_control_row(row, raw_2020_rows[row["timestamp"]]) for row in control_target_truth
    ]
    control_displacement_rows = [
        _merge_control_row(row, raw_2020_rows[row["timestamp"]])
        for row in control_displacement_truth
    ]
    control_blocked_rows = [
        _merge_control_row(row, raw_2020_rows[row["timestamp"]]) for row in control_blocked_truth
    ]
    control_context_rows = sorted(
        [*control_displacement_rows, *control_blocked_rows], key=lambda row: row["timestamp"]
    )

    surfaces = {
        "harmful_2019": {
            "surface_id": "harmful_2019",
            "surface_role": "harmful",
            "primary_source": "first_pair_artifact",
            "secondary_source": "second_pair_artifact",
            "target_rows": harmful_target,
            "context_rows": harmful_context,
            "summary": _build_surface_summary(harmful_target, harmful_context),
        },
        "control_2020": {
            "surface_id": "control_2020",
            "surface_role": "control",
            "primary_source": "truth_surface_artifact+raw_action_diff",
            "target_rows": control_target_rows,
            "context_rows": control_context_rows,
            "summary": _build_surface_summary(control_target_rows, control_context_rows),
        },
    }
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
            "truth_surface_artifact": {
                "path": str(TRUTH_SURFACE_ARTIFACT),
                "audit_version": truth_surface_artifact.get("audit_version"),
                "status": truth_surface_artifact.get("status"),
                "base_sha": truth_surface_artifact.get("base_sha"),
            },
            "raw_control_2020_action_diff": {
                "path": str(CONTROL_2020_ACTION_DIFF),
                "locked_timestamp_count": len(locked_2020_timestamps),
                "clarity_raw_present_on_all_locked_rows": all(
                    raw_2020_rows[timestamp].clarity_raw is not None
                    for timestamp in locked_2020_timestamps
                ),
            },
        },
        "control_2020_source_backed_rows": [
            {
                "timestamp": row.timestamp,
                "action_pair": row.action_pair,
                "switch_reason": row.switch_reason,
                "selected_policy": row.selected_policy,
                "bars_since_regime_change": row.bars_since_regime_change,
                "action_edge": row.action_edge,
                "confidence_gate": row.confidence_gate,
                "clarity_score": row.clarity_score,
                "clarity_raw": row.clarity_raw,
            }
            for row in sorted(raw_2020_rows.values(), key=lambda item: item.timestamp)
        ],
    }


def run_transport_check(base_sha: str) -> dict[str, Any]:
    surface_payload = _load_transport_surfaces()
    surfaces = surface_payload["surfaces"]
    truth_polarity = _truth_polarity(surfaces)
    all_rows = [
        *surfaces["harmful_2019"]["target_rows"],
        *surfaces["harmful_2019"]["context_rows"],
        *surfaces["control_2020"]["target_rows"],
        *surfaces["control_2020"]["context_rows"],
    ]

    primary_field_admission = {
        field_name: _field_admission(all_rows, field_name) for field_name in PRIMARY_FIELD_NAMES
    }
    descriptive_field_admission = {
        field_name: _field_admission(all_rows, field_name) for field_name in DESCRIPTIVE_FIELD_NAMES
    }
    missing_primary_fields = [
        field_name
        for field_name, admission in primary_field_admission.items()
        if admission["status"] != "evaluable"
    ]
    field_admission = {
        "primary_fields": primary_field_admission,
        "descriptive_fields": descriptive_field_admission,
        "all_primary_fields_available": not missing_primary_fields,
        "missing_primary_fields": missing_primary_fields,
    }

    field_evaluations: list[dict[str, Any]] = []
    non_null_fields: list[str] = []
    claim_fields_without_signal: list[str] = []
    if not field_admission["all_primary_fields_available"]:
        status = "fail_closed_required_field_unavailable"
    else:
        field_evaluations = [
            _evaluate_field(field_definition, surfaces=surfaces)
            for field_definition in FIELD_DEFINITIONS
        ]
        non_null_fields = [
            evaluation["field_name"]
            for evaluation in field_evaluations
            if evaluation["bounded_signal_present"]
        ]
        claim_fields_without_signal = [
            evaluation["field_name"]
            for evaluation in field_evaluations
            if not evaluation["descriptive_only"] and not evaluation["bounded_signal_present"]
        ]
        status = (
            "bounded_boundary_gap_signal_present"
            if non_null_fields
            else "bounded_boundary_gap_null"
        )

    return {
        "audit_version": (
            "ri-policy-router-insufficient-evidence-d1-boundary-gap-transport-check-"
            "2019-06-vs-2020-10-11-2026-05-04"
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
            "truth_surface_reference": str(TRUTH_SURFACE_REFERENCE),
            "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
        },
        "fail_closed_contract": {
            "statement": (
                "The helper keeps the exact 2019 harmful anchor fixed, locks the exact 2020 "
                "target/context timestamps, requires direct source-backed clarity_raw admission on "
                "every locked 2020 row, excludes context rows from PASS/FAIL adjudication, and keeps "
                "every outcome exact-surface only, descriptive only, and non-authoritative."
            )
        },
        "search_boundary": {
            "statement": (
                "No threshold search, new field discovery, conjunction search, source widening, or July/"
                "March/late-2024 reopening is allowed. This slice only tests the already-admitted D1 "
                "family on one third exact control surface."
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
            "control_2020_target_timestamps": [
                row["timestamp"] for row in surfaces["control_2020"]["target_rows"]
            ],
            "control_2020_context_timestamps": [
                row["timestamp"] for row in surfaces["control_2020"]["context_rows"]
            ],
            "shared_2019_surface_match": True,
            "context_rows_excluded_from_selection": True,
            "observational_only_authority": True,
            "row_role_registry": _build_row_role_registry(surfaces),
        },
        "control_2020_source_backed_field_proof": {
            "raw_action_diff_path": str(CONTROL_2020_ACTION_DIFF),
            "field_names_checked": [*PRIMARY_FIELD_NAMES, *DESCRIPTIVE_FIELD_NAMES],
            "rows": surface_payload["control_2020_source_backed_rows"],
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
        "field_admission": field_admission,
        "boundary_gap_summary": {
            "non_null_field_names": non_null_fields,
            "claim_fields_without_signal": claim_fields_without_signal,
            "bounded_signal_present": bool(non_null_fields),
        },
        "field_boundary_gap_evaluations": field_evaluations,
    }


def main() -> int:
    args = _parse_args()
    output_root = ROOT_DIR / Path(args.output_root_relative)
    output_json = output_root / args.summary_filename
    result = run_transport_check(base_sha=args.base_sha)

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "summary_artifact": str(output_json),
                "status": result["status"],
                "non_null_field_names": result["boundary_gap_summary"]["non_null_field_names"],
                "missing_primary_fields": result["field_admission"]["missing_primary_fields"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
