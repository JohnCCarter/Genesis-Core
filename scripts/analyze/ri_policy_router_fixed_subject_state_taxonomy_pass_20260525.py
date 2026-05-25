from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from statistics import fmean
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

SOURCE_ARTIFACT_RELATIVE = Path(
    "results/evaluation/ri_policy_router_2023_12_vs_2024_fixed_window_phase_contrast_2026-05-25.json"
)
OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = "ri_policy_router_fixed_subject_state_taxonomy_pass_2026-05-25.json"
STATUS_OK = "fixed_subject_state_taxonomy_generated"
STATUS_FAIL_CLOSED = "fixed_subject_state_taxonomy_fail_closed"
MAX_ADJACENCY_GAP = timedelta(hours=24)
WORKING_CONTRACT_REFERENCE = Path("GENESIS_WORKING_CONTRACT.md")
DEFENSIVE_SWITCH_REASONS = {"transition_pressure_detected", "defensive_transition_state"}
AGED_SWITCH_REASONS = {"AGED_WEAK_CONTINUATION_GUARD"}
CONTINUATION_POLICY = "RI_continuation_policy"
DEFENSIVE_POLICY = "RI_defensive_transition_policy"
BLOCKED_PHASE_LABELS = {
    "blocked_insufficient_evidence",
    "blocked_stable_context",
}
STATE_LABEL_ORDER = (
    "clean_continuation",
    "aging_continuation",
    "blocked_mixed",
    "transition_chop",
    "unclassified",
)


class StateTaxonomyError(RuntimeError):
    """Raised when the source artifact is missing or structurally invalid."""


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run a read-only deterministic state-taxonomy pass over the fixed 2023-12 vs 2024 "
            "policy-router contrast artifact without changing runtime behavior."
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
        help="Repo-relative source fixed-window artifact to classify.",
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


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(str(value))


def _counter_payload(counter: Counter[str]) -> list[dict[str, Any]]:
    ordered_keys = sorted(counter)
    return [{"label": key, "count": counter[key]} for key in ordered_keys]


def _metric_summary(rows: list[dict[str, Any]], key: str) -> dict[str, Any] | None:
    values = [float(row[key]) for row in rows if isinstance(row.get(key), int | float)]
    if not values:
        return None
    return {
        "count": len(values),
        "mean": round(fmean(values), 6),
        "min": round(min(values), 6),
        "max": round(max(values), 6),
        "gt_zero_share": round(sum(value > 0.0 for value in values) / len(values), 6),
    }


def _load_source_artifact(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise StateTaxonomyError(f"Source artifact not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise StateTaxonomyError("Source artifact is not a JSON object")
    timelines = payload.get("timelines")
    if not isinstance(timelines, dict):
        raise StateTaxonomyError("Source artifact missing timelines payload")
    continuation_rows = timelines.get("continuation_2023")
    harmful_rows = timelines.get("harmful_2024")
    if not isinstance(continuation_rows, list) or not isinstance(harmful_rows, list):
        raise StateTaxonomyError("Source artifact timelines are malformed")
    return payload


def _classify_segment(rows: list[dict[str, Any]]) -> tuple[str, str]:
    switch_reasons = {str(row.get("switch_reason")) for row in rows}
    selected_policies = {str(row.get("selected_policy")) for row in rows}
    phase_labels = {str(row.get("phase_label")) for row in rows}
    phase_families = {str(row.get("phase_family")) for row in rows}

    if switch_reasons & DEFENSIVE_SWITCH_REASONS or DEFENSIVE_POLICY in selected_policies:
        return (
            "transition_chop",
            "segment contains explicit defensive-transition routing signals",
        )
    if (
        switch_reasons & AGED_SWITCH_REASONS
        or "blocked_aged_weak_continuation_guard" in phase_labels
    ):
        return (
            "aging_continuation",
            "segment is blocked by aged-weak continuation guard semantics",
        )
    if (
        phase_labels == {"continuation_release"}
        and phase_families == {"continuation_like"}
        and selected_policies == {CONTINUATION_POLICY}
    ):
        return (
            "clean_continuation",
            "segment is a pure continuation-release cluster with no blocked or defensive rows",
        )
    if phase_labels & BLOCKED_PHASE_LABELS or phase_families == {"blocked_like"}:
        return (
            "blocked_mixed",
            "segment is a blocked-like cluster without explicit defensive routing",
        )
    return ("unclassified", "segment does not cleanly satisfy the current state taxonomy rules")


def _segment_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not rows:
        return []

    ordered_rows = sorted(rows, key=lambda row: _parse_timestamp(str(row["timestamp"])))
    grouped: list[list[dict[str, Any]]] = [[ordered_rows[0]]]
    for row in ordered_rows[1:]:
        current_timestamp = _parse_timestamp(str(row["timestamp"]))
        previous_row = grouped[-1][-1]
        previous_timestamp = _parse_timestamp(str(previous_row["timestamp"]))
        same_phase_label = str(row.get("phase_label")) == str(previous_row.get("phase_label"))
        within_gap = current_timestamp - previous_timestamp <= MAX_ADJACENCY_GAP
        if same_phase_label and within_gap:
            grouped[-1].append(row)
        else:
            grouped.append([row])

    segments: list[dict[str, Any]] = []
    for rows_in_segment in grouped:
        state_label, rule_reason = _classify_segment(rows_in_segment)
        switch_reason_counts = Counter(str(row.get("switch_reason")) for row in rows_in_segment)
        selected_policy_counts = Counter(str(row.get("selected_policy")) for row in rows_in_segment)
        segment = {
            "state_label": state_label,
            "classification_reason": rule_reason,
            "row_count": len(rows_in_segment),
            "start": rows_in_segment[0]["timestamp"],
            "end": rows_in_segment[-1]["timestamp"],
            "phase_label": rows_in_segment[0].get("phase_label"),
            "phase_family": rows_in_segment[0].get("phase_family"),
            "switch_reason_counts": _counter_payload(switch_reason_counts),
            "selected_policy_counts": _counter_payload(selected_policy_counts),
            "rows": rows_in_segment,
        }
        for row in rows_in_segment:
            row["state_taxonomy_label"] = state_label
            row["state_taxonomy_reason"] = rule_reason
        segments.append(segment)
    return segments


def _classify_subject(
    rows: list[dict[str, Any]], segments: list[dict[str, Any]]
) -> tuple[str, str]:
    row_label_counts = Counter(str(row.get("state_taxonomy_label", "unclassified")) for row in rows)
    segment_labels = [str(segment["state_label"]) for segment in segments]

    if segments and all(label == "clean_continuation" for label in segment_labels):
        return (
            "clean_continuation",
            "all segments are clean continuation-release clusters with no blocked or defensive substructure",
        )
    if segments and all(label == "aging_continuation" for label in segment_labels):
        return (
            "aging_continuation",
            "all segments are dominated by aged-weak continuation guard structure",
        )
    if row_label_counts["transition_chop"] > 0 and row_label_counts["transition_chop"] >= (
        len(rows) / 2.0
    ):
        return (
            "transition_chop",
            "defensive-transition rows dominate the fixed subject",
        )
    if (
        row_label_counts["blocked_mixed"] + row_label_counts["aging_continuation"]
        > row_label_counts["clean_continuation"]
    ):
        return (
            "blocked_mixed",
            "blocked-like and aged-weak blocked rows dominate over clean continuation rows",
        )
    if row_label_counts["clean_continuation"] > 0 and (
        row_label_counts["blocked_mixed"]
        + row_label_counts["aging_continuation"]
        + row_label_counts["transition_chop"]
        == 0
    ):
        return (
            "clean_continuation",
            "only clean continuation rows materialize in this fixed subject",
        )
    if row_label_counts["aging_continuation"] > 0 and (
        row_label_counts["blocked_mixed"]
        + row_label_counts["clean_continuation"]
        + row_label_counts["transition_chop"]
        == 0
    ):
        return (
            "aging_continuation",
            "only aged-weak continuation guard rows materialize in this fixed subject",
        )
    return (
        "unclassified",
        "the fixed subject does not map cleanly to one dominant current taxonomy label",
    )


def _subject_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    copied_rows = [dict(row) for row in rows]
    segments = _segment_rows(copied_rows)
    dominant_state_label, classification_reason = _classify_subject(copied_rows, segments)
    row_state_label_counts = Counter(
        str(row.get("state_taxonomy_label", "unclassified")) for row in copied_rows
    )
    segment_state_label_counts = Counter(str(segment["state_label"]) for segment in segments)

    return {
        "row_count": len(copied_rows),
        "dominant_state_label": dominant_state_label,
        "classification_reason": classification_reason,
        "decision_time_state": {
            "switch_reason_counts": _counter_payload(
                Counter(str(row.get("switch_reason")) for row in copied_rows)
            ),
            "selected_policy_counts": _counter_payload(
                Counter(str(row.get("selected_policy")) for row in copied_rows)
            ),
            "zone_counts": _counter_payload(Counter(str(row.get("zone")) for row in copied_rows)),
            "phase_label_counts": _counter_payload(
                Counter(str(row.get("phase_label")) for row in copied_rows)
            ),
            "bars_since_regime_change": _metric_summary(copied_rows, "bars_since_regime_change"),
            "action_edge": _metric_summary(copied_rows, "action_edge"),
            "confidence_gate": _metric_summary(copied_rows, "confidence_gate"),
            "clarity_score": _metric_summary(copied_rows, "clarity_score"),
        },
        "taxonomy_counts": {
            "row_state_label_counts": _counter_payload(row_state_label_counts),
            "segment_state_label_counts": _counter_payload(segment_state_label_counts),
        },
        "segments": [
            {
                "state_label": segment["state_label"],
                "classification_reason": segment["classification_reason"],
                "row_count": segment["row_count"],
                "start": segment["start"],
                "end": segment["end"],
                "phase_label": segment["phase_label"],
                "phase_family": segment["phase_family"],
                "switch_reason_counts": segment["switch_reason_counts"],
                "selected_policy_counts": segment["selected_policy_counts"],
            }
            for segment in segments
        ],
        "observational_outcome_context": {
            "fwd_16_close_return_pct": _metric_summary(copied_rows, "fwd_16_close_return_pct"),
            "fwd_8_close_return_pct": _metric_summary(copied_rows, "fwd_8_close_return_pct"),
            "fwd_4_close_return_pct": _metric_summary(copied_rows, "fwd_4_close_return_pct"),
            "mfe_16_pct": _metric_summary(copied_rows, "mfe_16_pct"),
            "mae_16_pct": _metric_summary(copied_rows, "mae_16_pct"),
        },
        "rows": copied_rows,
    }


def _build_fixed_subjects(payload: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    timelines = payload["timelines"]
    continuation_rows = list(timelines["continuation_2023"])
    harmful_rows = list(timelines["harmful_2024"])

    return {
        "continuation_2023_wave_one": [
            row for row in continuation_rows if row.get("cohort_label") == "continuation_wave_one"
        ],
        "continuation_2023_wave_two": [
            row for row in continuation_rows if row.get("cohort_label") == "continuation_wave_two"
        ],
        "continuation_2023_combined": continuation_rows,
        "harmful_2024_regression_target": [
            row for row in harmful_rows if row.get("cohort_label") == "regression_target"
        ],
        "harmful_2024_displacement": [
            row
            for row in harmful_rows
            if row.get("cohort_label") == "stable_continuation_displacement"
        ],
        "harmful_2024_stable_context": [
            row
            for row in harmful_rows
            if row.get("cohort_label") == "stable_continuation_blocked_context"
        ],
        "harmful_2024_combined": harmful_rows,
    }


def _coverage_payload(subject_summaries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    dominant_labels = sorted(
        {
            summary["dominant_state_label"]
            for summary in subject_summaries.values()
            if summary["dominant_state_label"] != "unclassified"
        }
    )
    segment_labels = sorted(
        {
            segment["state_label"]
            for summary in subject_summaries.values()
            for segment in summary["segments"]
            if segment["state_label"] != "unclassified"
        }
    )
    absent_labels = [
        label
        for label in STATE_LABEL_ORDER
        if label not in {"unclassified"} and label not in set(segment_labels)
    ]
    dominant_subjects = {
        label: sorted(
            [
                subject_name
                for subject_name, summary in subject_summaries.items()
                if summary["dominant_state_label"] == label
            ]
        )
        for label in dominant_labels
    }
    segment_subjects = {
        label: sorted(
            {
                subject_name
                for subject_name, summary in subject_summaries.items()
                if any(segment["state_label"] == label for segment in summary["segments"])
            }
        )
        for label in segment_labels
    }
    return {
        "dominant_subject_labels_materialized": dominant_labels,
        "segment_level_labels_materialized": segment_labels,
        "unmaterialized_on_fixed_subjects": absent_labels,
        "dominant_subjects_by_label": dominant_subjects,
        "subjects_with_any_segment_by_label": segment_subjects,
    }


def _fail_closed_result(
    base_sha: str, reason: str, source_artifact_relative: str
) -> dict[str, Any]:
    return {
        "audit_version": "ri-policy-router-fixed-subject-state-taxonomy-pass-2026-05-25",
        "base_sha": base_sha,
        "status": STATUS_FAIL_CLOSED,
        "observational_only": True,
        "non_authoritative": True,
        "failure_reason": reason,
        "classification_boundary": {
            "decision_time_only_for_taxonomy": True,
            "outcome_metrics_observational_only": True,
        },
        "inputs": {
            "source_artifact": source_artifact_relative,
            "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
        },
    }


def run_state_taxonomy_pass(base_sha: str, source_artifact_relative: Path) -> dict[str, Any]:
    try:
        payload = _load_source_artifact(ROOT_DIR / source_artifact_relative)
        fixed_subjects = _build_fixed_subjects(payload)
        subject_summaries = {
            subject_name: _subject_summary(rows) for subject_name, rows in fixed_subjects.items()
        }
    except StateTaxonomyError as exc:
        return _fail_closed_result(
            base_sha=base_sha,
            reason=str(exc),
            source_artifact_relative=str(source_artifact_relative),
        )

    return {
        "audit_version": "ri-policy-router-fixed-subject-state-taxonomy-pass-2026-05-25",
        "base_sha": base_sha,
        "status": STATUS_OK,
        "observational_only": True,
        "non_authoritative": True,
        "classification_boundary": {
            "decision_time_only_for_taxonomy": True,
            "outcome_metrics_observational_only": True,
            "state_labels": [
                "clean_continuation",
                "aging_continuation",
                "blocked_mixed",
                "transition_chop",
            ],
            "rule_order": [
                "transition_chop if explicit defensive-transition routing materializes",
                "aging_continuation if aged-weak continuation guard materializes",
                "clean_continuation if continuation-release materializes without blocked or defensive rows",
                "blocked_mixed if blocked-like structure materializes without explicit defensive routing",
            ],
        },
        "inputs": {
            "source_artifact": str(source_artifact_relative),
            "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
        },
        "subjects": subject_summaries,
        "coverage": _coverage_payload(subject_summaries),
    }


def main() -> int:
    args = _parse_args()
    source_artifact_relative = Path(args.source_artifact_relative)
    output_root = ROOT_DIR / Path(args.output_root_relative)
    output_json = output_root / args.summary_filename
    result = run_state_taxonomy_pass(
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
                "dominant_subject_labels_materialized": result.get("coverage", {}).get(
                    "dominant_subject_labels_materialized"
                ),
                "segment_level_labels_materialized": result.get("coverage", {}).get(
                    "segment_level_labels_materialized"
                ),
                "unmaterialized_on_fixed_subjects": result.get("coverage", {}).get(
                    "unmaterialized_on_fixed_subjects"
                ),
                "failure_reason": result.get("failure_reason"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
