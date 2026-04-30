from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


LOCAL_ROOT_DIR = Path(__file__).resolve().parents[2]
if str(LOCAL_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(LOCAL_ROOT_DIR))

from scripts.analyze.ri_policy_router_insufficient_evidence_local_window_20260429 import (
    ACTION_DIFF_ROOT,
    ACTION_DIFF_ROOT_RELATIVE,
    CURATED_CANDLES_PATH,
    CURATED_CANDLES_RELATIVE,
    LOCAL_PADDING,
    ROOT_DIR,
    LocalWindowEvidenceError,
    SubjectBounds,
    _cohort_summary,
    _descriptive_gap,
    _load_candles,
    _normalized_constant_timestamps,
    _row_cohort_label,
    _serialize_local_row,
    _validate_exact_insufficient_evidence_cluster,
    build_local_envelope,
    load_subject_rows,
    select_exact_rows,
)

OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = "ri_policy_router_positive_year_insufficient_evidence_control_2026-04-29.json"
SUBJECT_SYMBOL = "tBTCUSD"
SUBJECT_TIMEFRAME = "3h"
CONTROL_YEAR = "2025"
TARGET_IE_TIMESTAMPS = (
    "2025-03-14T15:00:00+00:00",
    "2025-03-15T00:00:00+00:00",
    "2025-03-15T09:00:00+00:00",
    "2025-03-15T18:00:00+00:00",
    "2025-03-16T03:00:00+00:00",
)
COMPARISON_STABLE_DISPLACEMENT_TIMESTAMPS = (
    "2025-03-13T15:00:00+00:00",
    "2025-03-14T00:00:00+00:00",
)
EXCLUDED_STABLE_CONTEXT_TIMESTAMPS = (
    "2025-03-13T21:00:00+00:00",
    "2025-03-14T06:00:00+00:00",
)
NEGATIVE_REFERENCE_NOTE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_insufficient_evidence_local_window_2026-04-29.md"
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Materialize one fixed positive-year insufficient-evidence local control window "
            "using the same framing as the completed March 2021 negative-year slice."
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


def run_positive_control_analysis(base_sha: str) -> dict[str, Any]:
    candles, timestamp_to_index = _load_candles(CURATED_CANDLES_PATH)
    diff_path = ACTION_DIFF_ROOT / f"{CONTROL_YEAR}_enabled_vs_absent_action_diffs.json"
    rows = load_subject_rows(diff_path)

    exact_target_timestamps = _normalized_constant_timestamps(TARGET_IE_TIMESTAMPS)
    exact_comparison_timestamps = _normalized_constant_timestamps(
        COMPARISON_STABLE_DISPLACEMENT_TIMESTAMPS
    )
    exact_excluded_context_timestamps = _normalized_constant_timestamps(
        EXCLUDED_STABLE_CONTEXT_TIMESTAMPS
    )

    _validate_exact_insufficient_evidence_cluster(rows, exact_timestamps=exact_target_timestamps)
    target_rows = select_exact_rows(
        rows,
        exact_timestamps=exact_target_timestamps,
        expected_reason="insufficient_evidence",
        expected_action_pair=("LONG", "NONE"),
    )
    select_exact_rows(
        rows,
        exact_timestamps=exact_comparison_timestamps,
        expected_reason="stable_continuation_state",
        expected_action_pair=("NONE", "LONG"),
    )
    select_exact_rows(
        rows,
        exact_timestamps=exact_excluded_context_timestamps,
        expected_reason="stable_continuation_state",
        expected_action_pair=("LONG", "NONE"),
    )

    target_bounds = SubjectBounds(start=target_rows[0].timestamp, end=target_rows[-1].timestamp)
    local_envelope = build_local_envelope(target_bounds, padding=LOCAL_PADDING)
    local_rows = [
        row for row in rows if local_envelope.start <= row.timestamp <= local_envelope.end
    ]

    target_timestamp_set = set(exact_target_timestamps)
    comparison_timestamp_set = set(exact_comparison_timestamps)
    local_timeline = [
        _serialize_local_row(
            row,
            cohort_label=_row_cohort_label(
                row,
                target_timestamps=target_timestamp_set,
                comparison_timestamps=comparison_timestamp_set,
            ),
            candles=candles,
            timestamp_to_index=timestamp_to_index,
        )
        for row in local_rows
    ]

    target_serialized = [
        row for row in local_timeline if row["cohort_label"] == "insufficient_evidence_target"
    ]
    comparison_serialized = [
        row
        for row in local_timeline
        if row["cohort_label"] == "stable_continuation_displacement_comparison"
    ]
    context_serialized = [row for row in local_timeline if row["cohort_label"] == "context_only"]

    target_summary = _cohort_summary(target_serialized)
    comparison_summary = _cohort_summary(comparison_serialized)
    context_reason_counts = Counter(row["switch_reason"] for row in context_serialized)
    context_action_pair_counts = Counter(row["action_pair"] for row in context_serialized)
    excluded_context_timestamp_strings = [
        timestamp.isoformat() for timestamp in exact_excluded_context_timestamps
    ]
    context_timestamp_strings = [row["timestamp"] for row in context_serialized]
    missing_exclusions = sorted(
        timestamp
        for timestamp in excluded_context_timestamp_strings
        if timestamp not in context_timestamp_strings
    )
    if missing_exclusions:
        raise LocalWindowEvidenceError(
            "Expected context-only stable LONG->NONE timestamps were not preserved: "
            f"{missing_exclusions}"
        )

    return {
        "audit_version": "ri-policy-router-positive-year-insufficient-evidence-control-2026-04-29",
        "base_sha": base_sha,
        "status": "positive-year-insufficient-evidence-control-generated",
        "observational_only": True,
        "non_authoritative": True,
        "subject": {
            "symbol": SUBJECT_SYMBOL,
            "timeframe": SUBJECT_TIMEFRAME,
            "positive_year": CONTROL_YEAR,
            "comparison_reference": str(NEGATIVE_REFERENCE_NOTE),
        },
        "skill_usage": ["decision_gate_debug", "python_engineering"],
        "cohort_definition": {
            "statement": (
                "Fixed positive-year local control on the curated annual enabled-vs-absent action-diff surface: one exact 2025 low-zone, candidate-LONG, bars-8+ insufficient-evidence blocked cluster compared against nearby stable-continuation displacement rows only."
            )
        },
        "proxy_boundary": {
            "statement": (
                "This slice uses timestamp-close observational proxies only. Reported differences are descriptive, not authoritative, and do not equal realized trade PnL, fill-aware MFE/MAE, one-to-one row pairing, or runtime-authoritative row truth."
            )
        },
        "parse_only_constraint": {
            "statement": (
                "This wrapper reads existing 2025 action-diff JSON and curated candles only, via the completed March 2021 local-window helper surface. It does not import from src/**, rerun backtests, regenerate upstream diff artifacts, or modify runtime/default authority surfaces."
            )
        },
        "inputs": {
            "action_diff_root": str(ACTION_DIFF_ROOT_RELATIVE),
            "subject_diff": str(
                ACTION_DIFF_ROOT_RELATIVE / f"{CONTROL_YEAR}_enabled_vs_absent_action_diffs.json"
            ),
            "curated_candles": str(CURATED_CANDLES_RELATIVE),
        },
        "local_window": {
            "target_cluster_rule": "exact insufficient-evidence rows verified as one <=24h adjacency group",
            "target_cluster_timestamps": [
                timestamp.isoformat() for timestamp in exact_target_timestamps
            ],
            "comparison_rule": "fixed nearby stable_continuation_state displacement rows with action pair NONE->LONG",
            "comparison_timestamps": [
                timestamp.isoformat() for timestamp in exact_comparison_timestamps
            ],
            "context_only_exclusions": {
                "rule": "stable_continuation_state rows with action pair LONG->NONE remain context-only and are excluded from comparison",
                "timestamps": excluded_context_timestamp_strings,
            },
            "target_cluster_bounds": {
                "start": target_bounds.start.isoformat(),
                "end": target_bounds.end.isoformat(),
            },
            "local_envelope_bounds": {
                "start": local_envelope.start.isoformat(),
                "end": local_envelope.end.isoformat(),
            },
        },
        "artifact_row_lock": {
            "target_timestamp_count": len(exact_target_timestamps),
            "comparison_timestamp_count": len(exact_comparison_timestamps),
            "context_only_exclusion_count": len(exact_excluded_context_timestamps),
            "target_timestamps": [timestamp.isoformat() for timestamp in exact_target_timestamps],
            "comparison_timestamps": [
                timestamp.isoformat() for timestamp in exact_comparison_timestamps
            ],
            "context_only_exclusion_timestamps": excluded_context_timestamp_strings,
        },
        "cohorts": {
            "insufficient_evidence_target": target_summary,
            "stable_continuation_displacement_comparison": comparison_summary,
            "context_only": {
                "row_count": len(context_serialized),
                "switch_reason_counts": [
                    {"switch_reason": reason, "count": count}
                    for reason, count in context_reason_counts.most_common()
                ],
                "action_pair_counts": [
                    {"action_pair": action_pair, "count": count}
                    for action_pair, count in context_action_pair_counts.most_common()
                ],
                "rows": context_serialized,
            },
        },
        "descriptive_comparison": {
            "fwd_16_close_return_pct": _descriptive_gap(
                target_summary,
                comparison_summary,
                "fwd_16_close_return_pct",
            ),
            "mfe_16_pct": _descriptive_gap(
                target_summary,
                comparison_summary,
                "mfe_16_pct",
            ),
            "mae_16_pct": _descriptive_gap(
                target_summary,
                comparison_summary,
                "mae_16_pct",
            ),
        },
        "local_timeline": local_timeline,
    }


def main() -> int:
    args = _parse_args()
    output_root = ROOT_DIR / Path(args.output_root_relative)
    output_json = output_root / args.summary_filename
    result = run_positive_control_analysis(base_sha=args.base_sha)

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "summary_artifact": str(output_json),
                "target_row_count": result["cohorts"]["insufficient_evidence_target"]["row_count"],
                "comparison_row_count": result["cohorts"][
                    "stable_continuation_displacement_comparison"
                ]["row_count"],
                "context_row_count": result["cohorts"]["context_only"]["row_count"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
