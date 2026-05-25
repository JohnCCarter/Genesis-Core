from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
SOURCE_ARTIFACT_RELATIVE = Path(
    "results/evaluation/scpe_ri_v1_selected_defensive_transition_window_audit_2026-04-20.json"
)
OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = "ri_policy_router_transition_chop_exact_carrier_pass_2026-05-25.json"
STATUS_OK = "transition_chop_exact_carrier_pass_generated"
STATUS_FAIL_CLOSED = "transition_chop_exact_carrier_pass_fail_closed"
EXPECTED_SOURCE_STATUS = "selected-defensive-transition-window-audit-generated"
WORKING_CONTRACT_REFERENCE = Path("GENESIS_WORKING_CONTRACT.md")
EXPECTED_LABEL = "transition_chop"
TRANSITION_BUCKETS = {"acute", "recent"}
TRANSITION_RAW_REASONS = {"transition_pressure_detected", "defensive_transition_state"}
SELECTED_DEFENSIVE_POLICY = "RI_defensive_transition_policy"
SELECTED_DEFENSIVE_ZONE = "low"
MAX_FRESH_BARS = 5.0


class TransitionChopCarrierError(RuntimeError):
    """Raised when the exact-carrier source artifact is missing or malformed."""


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run a read-only exact-carrier pass over the selected-defensive transition-window "
            "audit artifact to test whether transition_chop materializes on the tiny defensive "
            "pocket."
        )
    )
    parser.add_argument(
        "--base-sha",
        required=True,
        help="Exact repository HEAD SHA for provenance in the emitted artifact.",
    )
    parser.add_argument(
        "--source-artifact-relative",
        default=str(SOURCE_ARTIFACT_RELATIVE),
        help="Repo-relative selected-defensive source artifact used for the exact-carrier pass.",
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


def _load_source_artifact(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise TransitionChopCarrierError(f"Source artifact not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TransitionChopCarrierError("Source artifact is not a JSON object")
    if payload.get("status") != EXPECTED_SOURCE_STATUS:
        raise TransitionChopCarrierError(
            f"Unexpected source artifact status: {payload.get('status')!r}"
        )
    return payload


def _extract_exact_carrier_rows(payload: dict[str, Any]) -> dict[str, Any]:
    selected_defensive = payload.get("selected_defensive_examples_sorted")
    threshold_rows = payload.get("threshold_nearest_by_recency")
    min_dwell_rows = payload.get("min_dwell_nearest_by_recency")
    comparator_summaries = payload.get("comparator_summaries")
    if not isinstance(selected_defensive, list) or len(selected_defensive) != 2:
        raise TransitionChopCarrierError(
            "Selected-defensive exact carrier is missing or does not contain exactly two rows"
        )
    if not isinstance(threshold_rows, list) or not threshold_rows:
        raise TransitionChopCarrierError("Threshold comparator rows missing from source artifact")
    if not isinstance(min_dwell_rows, list) or not min_dwell_rows:
        raise TransitionChopCarrierError("Min-dwell comparator rows missing from source artifact")
    if not isinstance(comparator_summaries, dict):
        raise TransitionChopCarrierError("Comparator summaries missing from source artifact")
    return {
        "selected_defensive": selected_defensive,
        "threshold_nearest": threshold_rows[0],
        "min_dwell_nearest": min_dwell_rows[0],
        "comparator_summaries": comparator_summaries,
    }


def _serialize_row(row: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "timestamp",
        "row_index",
        "bars_since_regime_change",
        "transition_bucket",
        "zone",
        "raw_switch_reason",
        "selected_policy",
        "switch_reason",
        "final_routed_action",
        "veto_reason",
        "ri_clarity_score",
        "conf_overall",
        "action_edge",
    )
    return {key: row.get(key) for key in keys}


def _classify_transition_chop(row: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "selected_policy_is_defensive": row.get("selected_policy") == SELECTED_DEFENSIVE_POLICY,
        "fresh_transition_window": float(row.get("bars_since_regime_change", 0.0))
        <= MAX_FRESH_BARS,
        "fresh_transition_bucket": str(row.get("transition_bucket")) in TRANSITION_BUCKETS,
        "low_zone": str(row.get("zone")) == SELECTED_DEFENSIVE_ZONE,
        "transition_reason": str(row.get("raw_switch_reason")) in TRANSITION_RAW_REASONS,
    }
    materializes = all(checks.values())
    return {
        "state_label": EXPECTED_LABEL if materializes else "outside_exact_transition_chop_carrier",
        "materializes_transition_chop": materializes,
        "checks": checks,
        "failed_checks": [name for name, passed in checks.items() if not passed],
    }


def _carrier_gap_summary(comparator_summaries: dict[str, Any]) -> dict[str, Any]:
    selected_summary = comparator_summaries.get("selected_defensive")
    threshold_summary = comparator_summaries.get("threshold_retained")
    min_dwell_summary = comparator_summaries.get("min_dwell_retained")
    if not isinstance(selected_summary, dict):
        raise TransitionChopCarrierError("Selected-defensive summary missing from source artifact")
    if not isinstance(threshold_summary, dict):
        raise TransitionChopCarrierError("Threshold summary missing from source artifact")
    if not isinstance(min_dwell_summary, dict):
        raise TransitionChopCarrierError("Min-dwell summary missing from source artifact")

    selected_ceiling = float(selected_summary["max_bars_since_regime_change"])
    threshold_floor = float(threshold_summary["min_bars_since_regime_change"])
    min_dwell_floor = float(min_dwell_summary["min_bars_since_regime_change"])
    return {
        "selected_defensive_window": {
            "min_bars_since_regime_change": float(selected_summary["min_bars_since_regime_change"]),
            "max_bars_since_regime_change": selected_ceiling,
            "transition_bucket_counts": selected_summary["transition_bucket_counts"],
            "zone_counts": selected_summary["zone_counts"],
        },
        "threshold_gap_from_selected_defensive_ceiling": round(
            threshold_floor - selected_ceiling,
            6,
        ),
        "min_dwell_gap_from_selected_defensive_ceiling": round(
            min_dwell_floor - selected_ceiling,
            6,
        ),
        "nearest_threshold_floor": threshold_floor,
        "nearest_min_dwell_floor": min_dwell_floor,
    }


def _build_fail_closed_result(
    base_sha: str, reason: str, source_artifact_relative: str
) -> dict[str, Any]:
    return {
        "audit_version": "ri-policy-router-transition-chop-exact-carrier-pass-2026-05-25",
        "base_sha": base_sha,
        "status": STATUS_FAIL_CLOSED,
        "observational_only": True,
        "non_authoritative": True,
        "failure_reason": reason,
        "inputs": {
            "source_artifact": source_artifact_relative,
            "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
        },
    }


def run_transition_chop_exact_carrier_pass(
    *,
    base_sha: str,
    source_artifact_relative: Path,
) -> dict[str, Any]:
    try:
        payload = _load_source_artifact(ROOT_DIR / source_artifact_relative)
        extracted = _extract_exact_carrier_rows(payload)
        selected_rows = extracted["selected_defensive"]
        threshold_nearest = extracted["threshold_nearest"]
        min_dwell_nearest = extracted["min_dwell_nearest"]
        comparator_summaries = extracted["comparator_summaries"]

        selected_classifications = []
        for row in selected_rows:
            selected_classifications.append(
                {
                    "row": _serialize_row(row),
                    "classification": _classify_transition_chop(row),
                }
            )

        threshold_comparator = {
            "row": _serialize_row(threshold_nearest),
            "classification": _classify_transition_chop(threshold_nearest),
        }
        min_dwell_comparator = {
            "row": _serialize_row(min_dwell_nearest),
            "classification": _classify_transition_chop(min_dwell_nearest),
        }
        carrier_gaps = _carrier_gap_summary(comparator_summaries)
    except TransitionChopCarrierError as exc:
        return _build_fail_closed_result(
            base_sha=base_sha,
            reason=str(exc),
            source_artifact_relative=str(source_artifact_relative),
        )

    return {
        "audit_version": "ri-policy-router-transition-chop-exact-carrier-pass-2026-05-25",
        "base_sha": base_sha,
        "status": STATUS_OK,
        "observational_only": True,
        "non_authoritative": True,
        "classification_boundary": {
            "state_label_under_test": EXPECTED_LABEL,
            "fresh_transition_window_max_bars": MAX_FRESH_BARS,
            "transition_buckets_required": sorted(TRANSITION_BUCKETS),
            "raw_switch_reasons_required": sorted(TRANSITION_RAW_REASONS),
            "selected_policy_required": SELECTED_DEFENSIVE_POLICY,
            "zone_required": SELECTED_DEFENSIVE_ZONE,
        },
        "inputs": {
            "source_artifact": str(source_artifact_relative),
            "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
        },
        "selected_defensive_exact_carrier": {
            "row_count": len(selected_classifications),
            "dominant_state_label": EXPECTED_LABEL,
            "rows": selected_classifications,
        },
        "nearest_comparators": {
            "min_dwell_retained": min_dwell_comparator,
            "threshold_retained": threshold_comparator,
        },
        "carrier_gap_summary": carrier_gaps,
        "bounded_verdict": {
            "transition_chop_materializes_on_selected_defensive_rows": all(
                item["classification"]["materializes_transition_chop"]
                for item in selected_classifications
            ),
            "transition_chop_materializes_on_nearest_min_dwell": min_dwell_comparator[
                "classification"
            ]["materializes_transition_chop"],
            "transition_chop_materializes_on_nearest_threshold": threshold_comparator[
                "classification"
            ]["materializes_transition_chop"],
        },
    }


def main() -> int:
    args = _parse_args()
    source_artifact_relative = Path(args.source_artifact_relative)
    output_root = ROOT_DIR / Path(args.output_root_relative)
    output_json = output_root / args.summary_filename
    result = run_transition_chop_exact_carrier_pass(
        base_sha=args.base_sha,
        source_artifact_relative=source_artifact_relative,
    )

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "summary_artifact": str(output_json),
                "status": result["status"],
                "bounded_verdict": result.get("bounded_verdict"),
                "failure_reason": result.get("failure_reason"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
