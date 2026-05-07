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
    "ri_policy_router_insufficient_evidence_d1_2023_06_external_surface_falsifier_"
    "2026-05-07.json"
)
CONTEXT_CLEAN_ARTIFACT_RELATIVE = Path(
    "results/evaluation/"
    "ri_policy_router_insufficient_evidence_d1_context_clean_selectivity_falsifier_"
    "2026-05-05.json"
)
ANNUAL_2023_DIFF_RELATIVE = Path(
    "results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/"
    "2023_enabled_vs_absent_action_diffs.json"
)
PACKET_REFERENCE = Path(
    "docs/decisions/regime_intelligence/policy_router/"
    "ri_policy_router_insufficient_evidence_d1_2023_06_external_surface_falsifier_"
    "precode_packet_2026-05-07.md"
)
CONTEXT_CLEAN_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_insufficient_evidence_d1_context_clean_selectivity_falsifier_"
    "2026-05-05.md"
)
BANK_STATE_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_insufficient_evidence_d1_bank_state_synthesis_2026-05-06.md"
)
POCKET_ISOLATION_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_2023_mixed_year_pocket_isolation_2026-05-06.md"
)
WORKING_CONTRACT_REFERENCE = Path("GENESIS_WORKING_CONTRACT.md")

SUBJECT_SYMBOL = "tBTCUSD"
SUBJECT_TIMEFRAME = "3h"
SUBJECT_MONTH = "2023-06"
SUBJECT_YEAR = "2023"

TARGET_SWITCH_REASON = "insufficient_evidence"
TARGET_ABSENT_ACTION = "LONG"
TARGET_ENABLED_ACTION = "NONE"
TARGET_ZONE = "low"

ANTITARGET_SWITCH_REASONS = {
    "AGED_WEAK_CONTINUATION_GUARD",
    "stable_continuation_state",
}

STATUS_SURVIVOR = "external_surface_survivor"
STATUS_FALSIFIED = "external_surface_falsified"
STATUS_SOURCE_UNAVAILABLE = "source_data_unavailable"


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
            "Materialize one exact 2023-06 external-surface falsifier by transporting the "
            "fixed D1 bank ceilings from the completed context-clean bank reread onto the "
            "exact 2023-06 low-zone insufficient_evidence surface."
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


def _normalize_annual_diff_row(row: dict[str, Any], *, cohort_name: str) -> dict[str, Any]:
    """Normalize one raw annual diff row to the flat format used by the transport check."""
    if not isinstance(row, dict):
        raise LocalWindowEvidenceError(f"Expected dict row in annual diff, got {type(row)!r}")
    enabled = row.get("enabled")
    absent = row.get("absent")
    if not isinstance(enabled, dict):
        raise LocalWindowEvidenceError("Annual diff row is missing enabled side")
    if not isinstance(absent, dict):
        raise LocalWindowEvidenceError("Annual diff row is missing absent side")
    router_debug = enabled.get("router_debug")
    if not isinstance(router_debug, dict):
        raise LocalWindowEvidenceError("Annual diff row.enabled is missing router_debug")

    timestamp = _normalize_timestamp(row.get("timestamp")).isoformat()
    absent_action = _coerce_str(absent.get("action"), field_name="absent.action")
    enabled_action = _coerce_str(enabled.get("action"), field_name="enabled.action")
    switch_reason = _coerce_str(
        router_debug.get("switch_reason"), field_name="enabled.router_debug.switch_reason"
    )
    selected_policy = _coerce_str(
        router_debug.get("selected_policy"), field_name="enabled.router_debug.selected_policy"
    )
    previous_policy = router_debug.get("previous_policy")
    zone = _coerce_str(router_debug.get("zone"), field_name="enabled.router_debug.zone")
    candidate = _coerce_str(
        router_debug.get("candidate"), field_name="enabled.router_debug.candidate"
    )
    bars_since_regime_change = router_debug.get("bars_since_regime_change")

    action_edge = _coerce_optional_float(
        router_debug.get("action_edge"), field_name="router_debug.action_edge"
    )
    confidence_gate = _coerce_optional_float(
        router_debug.get("confidence_gate"), field_name="router_debug.confidence_gate"
    )
    # clarity_raw is intentionally absent from annual diff router_debug rows;
    # fail closed (not_evaluable) rather than backfill or infer.
    clarity_raw = None
    clarity_score = _coerce_optional_float(
        router_debug.get("clarity_score"), field_name="router_debug.clarity_score"
    )

    return {
        "cohort_name": cohort_name,
        "timestamp": timestamp,
        "month": timestamp[:7],
        "absent_action": absent_action,
        "enabled_action": enabled_action,
        "action_pair": f"{absent_action}->{enabled_action}",
        "switch_reason": switch_reason,
        "selected_policy": selected_policy,
        "previous_policy": (
            _coerce_str(previous_policy, field_name="previous_policy")
            if isinstance(previous_policy, str) and previous_policy
            else None
        ),
        "zone": zone,
        "candidate": candidate,
        "bars_since_regime_change": (
            _coerce_int(bars_since_regime_change, field_name="bars_since_regime_change")
            if isinstance(bars_since_regime_change, int)
            and not isinstance(bars_since_regime_change, bool)
            else None
        ),
        "action_edge": action_edge,
        "confidence_gate": confidence_gate,
        "clarity_raw": clarity_raw,
        "clarity_score": clarity_score,
    }


def _is_target_row(row: dict[str, Any]) -> bool:
    return (
        row["month"] == SUBJECT_MONTH
        and row["zone"] == TARGET_ZONE
        and row["absent_action"] == TARGET_ABSENT_ACTION
        and row["enabled_action"] == TARGET_ENABLED_ACTION
        and row["switch_reason"] == TARGET_SWITCH_REASON
    )


def _is_antitarget_row(row: dict[str, Any]) -> bool:
    return (
        row["month"] == SUBJECT_MONTH
        and row["zone"] == TARGET_ZONE
        and row["switch_reason"] in ANTITARGET_SWITCH_REASONS
    )


def load_2023_06_surface() -> (
    tuple[dict[str, list[dict[str, Any]]], dict[str, Any], dict[str, Any] | None]
):
    """Load the 2023-06 external surface from the annual diff artifact.

    Returns (cohorts, row_lock, source_input_info) if successful.
    Raises FileNotFoundError if the source artifact is absent (caller handles this for
    fail-closed status).
    """
    source_path = ROOT_DIR / ANNUAL_2023_DIFF_RELATIVE
    payload = _load_json(source_path)
    if not isinstance(payload, list):
        raise LocalWindowEvidenceError("Expected list payload in 2023 annual diff artifact")

    all_rows_raw = [row for row in payload if isinstance(row, dict)]

    target_rows = []
    antitarget_rows = []
    all_june_rows = []

    for raw_row in all_rows_raw:
        ts_raw = raw_row.get("timestamp")
        if not isinstance(ts_raw, str):
            continue
        ts_normalized = _normalize_timestamp(ts_raw).isoformat()
        if not ts_normalized.startswith(SUBJECT_MONTH):
            continue

        enabled = raw_row.get("enabled")
        if not isinstance(enabled, dict):
            continue
        router_debug = enabled.get("router_debug")
        if not isinstance(router_debug, dict):
            continue
        zone = router_debug.get("zone")
        if zone != TARGET_ZONE:
            continue

        normalized = _normalize_annual_diff_row(raw_row, cohort_name="")
        all_june_rows.append(normalized)
        if _is_target_row(normalized):
            target_rows.append(_normalize_annual_diff_row(raw_row, cohort_name="2023_06_ie_target"))
        elif _is_antitarget_row(normalized):
            antitarget_rows.append(
                _normalize_annual_diff_row(raw_row, cohort_name="2023_06_antitarget")
            )

    target_rows = sorted(target_rows, key=lambda r: r["timestamp"])
    antitarget_rows = sorted(antitarget_rows, key=lambda r: r["timestamp"])
    full_surface_rows = sorted(target_rows + antitarget_rows, key=lambda r: r["timestamp"])

    target_count = len(target_rows)
    antitarget_count = len(antitarget_rows)
    total_count = len(full_surface_rows)

    row_lock = {
        "target_count": target_count,
        "antitarget_count": antitarget_count,
        "total_count": total_count,
        "target_timestamps": [r["timestamp"] for r in target_rows],
        "antitarget_timestamps": [r["timestamp"] for r in antitarget_rows],
        "full_surface_timestamps": [r["timestamp"] for r in full_surface_rows],
        "target_switch_reason": TARGET_SWITCH_REASON,
        "antitarget_switch_reasons": sorted(ANTITARGET_SWITCH_REASONS),
        "subject_month": SUBJECT_MONTH,
        "subject_zone": TARGET_ZONE,
    }

    source_info = {
        "path": str(ANNUAL_2023_DIFF_RELATIVE),
        "total_rows_in_source": len(all_rows_raw),
        "june_low_zone_rows": len(all_june_rows),
        "target_rows": target_count,
        "antitarget_rows": antitarget_count,
    }

    return (
        {
            "2023_06_ie_target": target_rows,
            "2023_06_antitarget": antitarget_rows,
            "2023_06_full_surface": full_surface_rows,
        },
        row_lock,
        source_info,
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
                item.get("target_bank_ceiling"),
                field_name=f"{field_name}.target_bank_ceiling",
            ),
            "target_bank_ceiling_source_timestamps": _coerce_str_list(
                item.get("target_bank_ceiling_source_timestamps"),
                field_name=f"{field_name}.target_bank_ceiling_source_timestamps",
            ),
            "context_bank_min": _coerce_optional_float(
                item.get("context_bank_min"),
                field_name=f"{field_name}.context_bank_min",
            ),
            "global_separation_margin": _coerce_optional_float(
                item.get("global_separation_margin"),
                field_name=f"{field_name}.global_separation_margin",
            ),
            "admission": {
                "status": _coerce_str(
                    admission.get("status"),
                    field_name=f"{field_name}.admission.status",
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
            f"D1 context-clean artifact is missing required field evaluations: "
            f"{missing_required_fields}"
        )

    for field_definition in FIELD_TRANSPORT_DEFINITIONS:
        bank_field = field_map[field_definition.field_name]
        if bank_field["target_bank_ceiling"] is None:
            raise LocalWindowEvidenceError(
                f"Transport field {field_definition.field_name} is missing a target-bank ceiling"
            )
        if bank_field["claim_status"] != "evaluated":
            raise LocalWindowEvidenceError(
                f"Transport field {field_definition.field_name} must remain evaluated "
                f"in the D1 bank artifact"
            )
        if field_definition.descriptive_only:
            if not bank_field["descriptive_only"]:
                raise LocalWindowEvidenceError(
                    f"Transport field {field_definition.field_name} must remain descriptive-only"
                )
        else:
            if bank_field["descriptive_only"]:
                raise LocalWindowEvidenceError(
                    f"Transport field {field_definition.field_name} unexpectedly became "
                    f"descriptive-only"
                )
            if not bank_field["passes_context_clean_test"]:
                raise LocalWindowEvidenceError(
                    f"Transport field {field_definition.field_name} no longer passes the "
                    f"frozen D1 bank test"
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
    target_count: int,
) -> dict[str, Any]:
    target_rows = cohorts["2023_06_ie_target"]
    antitarget_rows = cohorts["2023_06_antitarget"]
    full_surface_rows = cohorts["2023_06_full_surface"]
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
        len(selected_target_rows) == target_count and not selected_antitarget_rows
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


def run_2023_06_external_surface_falsifier(base_sha: str) -> dict[str, Any]:
    bank_fields, bank_input = _load_context_clean_transport_fields()

    transport_ceiling_registry = {
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
    }

    base_result: dict[str, Any] = {
        "audit_version": (
            "ri-policy-router-insufficient-evidence-d1-2023-06-external-surface-falsifier-"
            "2026-05-07"
        ),
        "base_sha": base_sha,
        "observational_only": True,
        "non_authoritative": True,
        "skill_usage": ["python_engineering"],
        "subject": {
            "symbol": SUBJECT_SYMBOL,
            "timeframe": SUBJECT_TIMEFRAME,
            "month": SUBJECT_MONTH,
            "year": SUBJECT_YEAR,
            "packet_reference": str(PACKET_REFERENCE),
            "context_clean_reference": str(CONTEXT_CLEAN_REFERENCE),
            "bank_state_reference": str(BANK_STATE_REFERENCE),
            "pocket_isolation_reference": str(POCKET_ISOLATION_REFERENCE),
            "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
        },
        "fail_closed_contract": {
            "statement": (
                "The helper reads only the frozen D1 context-clean artifact for bank ceilings "
                "and the 2023 annual diff artifact for the external surface. If the annual diff "
                "source is absent it emits source_data_unavailable without backfill or rescue. "
                "clarity_raw is always not_evaluable on this surface because annual diff "
                "router_debug does not carry clarity_raw. clarity_score is descriptive-only "
                "with no PASS/FAIL authority."
            )
        },
        "transport_rubric": {
            "target_cohort": (
                f"month={SUBJECT_MONTH}, zone={TARGET_ZONE}, "
                f"absent_action={TARGET_ABSENT_ACTION}, "
                f"enabled_action={TARGET_ENABLED_ACTION}, "
                f"switch_reason={TARGET_SWITCH_REASON}"
            ),
            "antitarget_switch_reasons": sorted(ANTITARGET_SWITCH_REASONS),
            "pass_condition": (
                "all target rows selected (field_value <= ceiling) "
                "AND zero antitarget rows selected"
            ),
            "statement": (
                "Each admitted claim field is evaluated independently. "
                "Overall status is external_surface_survivor iff at least one admitted "
                "claim field passes the full transport test. "
                "external_surface_falsified iff all admitted fields are transport_falsified "
                "or not_evaluable with at least one transport_falsified."
            ),
        },
        "inputs": {
            "context_clean_artifact": bank_input,
        },
        "transport_ceiling_registry": transport_ceiling_registry,
    }

    try:
        cohorts, row_lock, source_info = load_2023_06_surface()
    except FileNotFoundError:
        base_result["status"] = STATUS_SOURCE_UNAVAILABLE
        base_result["source_unavailable_reason"] = (
            f"Annual diff source not found at {ANNUAL_2023_DIFF_RELATIVE!s}. "
            f"This path is git-ignored (results/backtests/**) and absent in the cloud "
            f"checkout. Run the backtest locally and re-execute this helper with the "
            f"source present to obtain an evaluable result."
        )
        base_result["inputs"]["annual_2023_diff_source"] = {
            "path": str(ANNUAL_2023_DIFF_RELATIVE),
            "available": False,
        }
        return base_result

    target_count = row_lock["target_count"]
    field_evaluations = _sorted_field_transport_evaluations(
        [
            _evaluate_transport_field(
                field_definition,
                bank_field=bank_fields[field_definition.field_name],
                cohorts=cohorts,
                target_count=target_count,
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
    status = STATUS_SURVIVOR if admitted_survivor_field_names else STATUS_FALSIFIED

    base_result["status"] = status
    base_result["inputs"]["annual_2023_diff_source"] = {
        "path": str(ANNUAL_2023_DIFF_RELATIVE),
        "available": True,
        **source_info,
    }
    base_result["artifact_row_lock"] = row_lock
    base_result["transport_summary"] = {
        "admitted_survivor_field_names": admitted_survivor_field_names,
        "admitted_falsified_field_names": admitted_falsified_field_names,
        "not_evaluable_claim_field_names": not_evaluable_claim_field_names,
        "descriptive_shape_match_field_names": descriptive_shape_match_field_names,
        "best_partial_claim_field": best_partial_claim_field,
        "bounded_signal_present": bool(admitted_survivor_field_names),
    }
    base_result["field_transport_evaluations"] = field_evaluations
    return base_result


def main() -> int:
    args = _parse_args()
    output_root = ROOT_DIR / Path(args.output_root_relative)
    output_json = output_root / args.summary_filename
    result = run_2023_06_external_surface_falsifier(base_sha=args.base_sha)

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "summary_artifact": str(output_json),
                "status": result["status"],
                "transport_summary": result.get("transport_summary"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
