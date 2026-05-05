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
    _serialize_local_row,
    build_local_envelope,
    load_subject_rows,
    select_exact_rows,
)

OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = "ri_policy_router_2024_regression_pocket_isolation_2026-04-30.json"
SUBJECT_SYMBOL = "tBTCUSD"
SUBJECT_TIMEFRAME = "3h"
SUBJECT_YEAR = "2024"
TARGET_TIMESTAMPS = (
    "2024-11-28T15:00:00+00:00",
    "2024-11-29T00:00:00+00:00",
    "2024-11-29T09:00:00+00:00",
    "2024-11-29T18:00:00+00:00",
    "2024-11-30T03:00:00+00:00",
    "2024-11-30T12:00:00+00:00",
    "2024-11-30T21:00:00+00:00",
    "2024-12-01T15:00:00+00:00",
    "2024-12-02T00:00:00+00:00",
)
EXPECTED_TARGET_REASON_COUNTS = {
    "AGED_WEAK_CONTINUATION_GUARD": 4,
    "insufficient_evidence": 5,
}
COMPARISON_STABLE_DISPLACEMENT_TIMESTAMPS = ("2024-12-01T00:00:00+00:00",)
STABLE_CONTEXT_TIMESTAMPS = ("2024-12-01T06:00:00+00:00",)
MOTIVATING_ANCHORS = (
    "docs/analysis/regime_intelligence/policy_router/ri_policy_router_enabled_vs_absent_curated_annual_evidence_2026-04-28.md",
    "docs/analysis/regime_intelligence/policy_router/ri_policy_router_negative_year_pocket_isolation_2026-04-28.md",
    "docs/analysis/regime_intelligence/policy_router/ri_policy_router_positive_vs_negative_pocket_comparison_2026-04-28.md",
    "docs/analysis/regime_intelligence/policy_router/ri_policy_router_shared_pocket_outcome_quality_2026-04-28.md",
    "docs/analysis/regime_intelligence/policy_router/ri_policy_router_blocked_reason_split_2026-04-29.md",
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Materialize one fixed 2024 late low-zone regression pocket with a mixed blocked "
            "target cluster, one nearby stable-continuation displacement row, and one nearby "
            "stable blocked context row."
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


def select_exact_target_rows(
    rows: list[Any],
    *,
    exact_timestamps: tuple[Any, ...],
    expected_reason_counts: dict[str, int],
) -> list[Any]:
    expected_set = set(exact_timestamps)
    matched = [row for row in rows if row.timestamp in expected_set]
    matched_set = {row.timestamp for row in matched}
    if matched_set != expected_set:
        missing = sorted(timestamp.isoformat() for timestamp in expected_set - matched_set)
        extra = sorted(timestamp.isoformat() for timestamp in matched_set - expected_set)
        raise LocalWindowEvidenceError(
            f"Exact 2024 regression target rows did not materialize cleanly; missing={missing}, extra={extra}"
        )

    invalid_rows = [
        row
        for row in matched
        if (row.absent_action, row.enabled_action) != ("LONG", "NONE")
        or row.switch_reason not in expected_reason_counts
    ]
    if invalid_rows:
        invalid_payload = [
            {
                "timestamp": row.timestamp.isoformat(),
                "switch_reason": row.switch_reason,
                "action_pair": row.action_pair,
            }
            for row in invalid_rows
        ]
        raise LocalWindowEvidenceError(
            f"Exact 2024 regression target rows failed reason/action validation: {invalid_payload}"
        )

    reason_counts = Counter(row.switch_reason for row in matched)
    if dict(reason_counts) != expected_reason_counts:
        raise LocalWindowEvidenceError(
            "Exact 2024 regression target rows failed reason-signature validation: "
            f"expected={expected_reason_counts}, actual={dict(reason_counts)}"
        )

    ordered = sorted(matched, key=lambda row: row.timestamp)
    if [row.timestamp for row in ordered] != list(exact_timestamps):
        raise LocalWindowEvidenceError("Exact 2024 regression target row ordering drifted")
    return ordered


def label_pocket_cohort(
    row: Any,
    *,
    target_timestamps: set[Any],
    comparison_timestamps: set[Any],
    stable_context_timestamps: set[Any],
) -> str:
    if row.timestamp in target_timestamps:
        return "regression_target"
    if row.timestamp in comparison_timestamps:
        return "stable_continuation_displacement_comparison"
    if row.timestamp in stable_context_timestamps:
        return "stable_continuation_blocked_context"
    return "context_only"


def run_regression_pocket_analysis(base_sha: str) -> dict[str, Any]:
    candles, timestamp_to_index = _load_candles(CURATED_CANDLES_PATH)
    diff_path = ACTION_DIFF_ROOT / f"{SUBJECT_YEAR}_enabled_vs_absent_action_diffs.json"
    rows = load_subject_rows(diff_path)

    exact_target_timestamps = _normalized_constant_timestamps(TARGET_TIMESTAMPS)
    exact_comparison_timestamps = _normalized_constant_timestamps(
        COMPARISON_STABLE_DISPLACEMENT_TIMESTAMPS
    )
    exact_stable_context_timestamps = _normalized_constant_timestamps(STABLE_CONTEXT_TIMESTAMPS)

    target_rows = select_exact_target_rows(
        rows,
        exact_timestamps=exact_target_timestamps,
        expected_reason_counts=EXPECTED_TARGET_REASON_COUNTS,
    )
    comparison_rows = select_exact_rows(
        rows,
        exact_timestamps=exact_comparison_timestamps,
        expected_reason="stable_continuation_state",
        expected_action_pair=("NONE", "LONG"),
    )
    stable_context_rows = select_exact_rows(
        rows,
        exact_timestamps=exact_stable_context_timestamps,
        expected_reason="stable_continuation_state",
        expected_action_pair=("LONG", "NONE"),
    )

    target_bounds = SubjectBounds(start=target_rows[0].timestamp, end=target_rows[-1].timestamp)
    local_envelope = build_local_envelope(target_bounds, padding=LOCAL_PADDING)

    if (
        comparison_rows[0].timestamp < local_envelope.start
        or comparison_rows[0].timestamp > local_envelope.end
    ):
        raise LocalWindowEvidenceError(
            "Stable-continuation displacement comparison row drifted outside the fixed 2024 envelope"
        )
    if (
        stable_context_rows[0].timestamp < local_envelope.start
        or stable_context_rows[0].timestamp > local_envelope.end
    ):
        raise LocalWindowEvidenceError(
            "Stable blocked context row drifted outside the fixed 2024 envelope"
        )

    local_rows = [
        row for row in rows if local_envelope.start <= row.timestamp <= local_envelope.end
    ]

    target_timestamp_set = set(exact_target_timestamps)
    comparison_timestamp_set = set(exact_comparison_timestamps)
    stable_context_timestamp_set = set(exact_stable_context_timestamps)
    local_timeline = [
        _serialize_local_row(
            row,
            cohort_label=label_pocket_cohort(
                row,
                target_timestamps=target_timestamp_set,
                comparison_timestamps=comparison_timestamp_set,
                stable_context_timestamps=stable_context_timestamp_set,
            ),
            candles=candles,
            timestamp_to_index=timestamp_to_index,
        )
        for row in local_rows
    ]

    target_serialized = [
        row for row in local_timeline if row["cohort_label"] == "regression_target"
    ]
    comparison_serialized = [
        row
        for row in local_timeline
        if row["cohort_label"] == "stable_continuation_displacement_comparison"
    ]
    stable_context_serialized = [
        row
        for row in local_timeline
        if row["cohort_label"] == "stable_continuation_blocked_context"
    ]
    context_serialized = [row for row in local_timeline if row["cohort_label"] == "context_only"]

    if [row["timestamp"] for row in target_serialized] != [
        timestamp.isoformat() for timestamp in exact_target_timestamps
    ]:
        raise LocalWindowEvidenceError(
            "Serialized regression target timestamps drifted from the fixed packet"
        )
    if [row["timestamp"] for row in comparison_serialized] != [
        timestamp.isoformat() for timestamp in exact_comparison_timestamps
    ]:
        raise LocalWindowEvidenceError(
            "Serialized stable-continuation displacement timestamps drifted from the fixed packet"
        )
    if [row["timestamp"] for row in stable_context_serialized] != [
        timestamp.isoformat() for timestamp in exact_stable_context_timestamps
    ]:
        raise LocalWindowEvidenceError(
            "Serialized stable blocked context timestamps drifted from the fixed packet"
        )

    target_summary = _cohort_summary(target_serialized)
    comparison_summary = _cohort_summary(comparison_serialized)
    stable_context_summary = _cohort_summary(stable_context_serialized)
    context_reason_counts = Counter(row["switch_reason"] for row in context_serialized)
    context_action_pair_counts = Counter(row["action_pair"] for row in context_serialized)

    return {
        "audit_version": "ri-policy-router-2024-regression-pocket-isolation-2026-04-30",
        "base_sha": base_sha,
        "status": "2024-regression-pocket-generated",
        "observational_only": True,
        "non_authoritative": True,
        "subject": {
            "symbol": SUBJECT_SYMBOL,
            "timeframe": SUBJECT_TIMEFRAME,
            "regression_year": SUBJECT_YEAR,
        },
        "skill_usage": ["decision_gate_debug", "python_engineering"],
        "cohort_definition": {
            "statement": (
                "Fixed 2024 low-zone, candidate-LONG, bars-8+ regression pocket on the curated annual enabled-vs-absent action-diff surface: one exact mixed AGED_WEAK_CONTINUATION_GUARD / insufficient_evidence blocked target cluster compared against one nearby true stable-continuation displacement row while keeping one nearby stable blocked row separate as context."
            )
        },
        "proxy_boundary": {
            "statement": (
                "This slice uses timestamp-close observational proxies only. Reported differences are descriptive, not authoritative, and do not equal realized trade PnL, fill-aware MFE/MAE, one-to-one row pairing, or runtime-authoritative row truth."
            )
        },
        "parse_only_constraint": {
            "statement": (
                "The helper reads one existing 2024 action-diff JSON and curated candles only. It does not import from src/**, rerun backtests, regenerate upstream diff artifacts, or modify runtime/default authority surfaces."
            )
        },
        "fail_closed_contract": {
            "statement": (
                "If the fixed timestamp set, reason split, action transitions, stable-context separation, or envelope membership differ from the packet, the helper aborts rather than widening scope."
            )
        },
        "inputs": {
            "action_diff_root": str(ACTION_DIFF_ROOT_RELATIVE),
            "subject_diff": str(
                ACTION_DIFF_ROOT_RELATIVE / f"{SUBJECT_YEAR}_enabled_vs_absent_action_diffs.json"
            ),
            "curated_candles": str(CURATED_CANDLES_RELATIVE),
            "motivating_anchors": list(MOTIVATING_ANCHORS),
        },
        "local_window": {
            "target_cluster_rule": "fixed mixed blocked cluster with exact 4/5 reason split and action pair LONG->NONE",
            "target_cluster_timestamps": [
                timestamp.isoformat() for timestamp in exact_target_timestamps
            ],
            "target_reason_counts": EXPECTED_TARGET_REASON_COUNTS,
            "comparison_rule": "fixed nearby stable_continuation_state displacement row with action pair NONE->LONG",
            "comparison_timestamps": [
                timestamp.isoformat() for timestamp in exact_comparison_timestamps
            ],
            "stable_context_rule": "fixed nearby stable_continuation_state blocked row with action pair LONG->NONE remains separate context",
            "stable_context_timestamps": [
                timestamp.isoformat() for timestamp in exact_stable_context_timestamps
            ],
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
            "stable_context_timestamp_count": len(exact_stable_context_timestamps),
            "target_timestamps": [timestamp.isoformat() for timestamp in exact_target_timestamps],
            "comparison_timestamps": [
                timestamp.isoformat() for timestamp in exact_comparison_timestamps
            ],
            "stable_context_timestamps": [
                timestamp.isoformat() for timestamp in exact_stable_context_timestamps
            ],
            "target_reason_counts": EXPECTED_TARGET_REASON_COUNTS,
        },
        "cohorts": {
            "regression_target": target_summary,
            "stable_continuation_displacement_comparison": comparison_summary,
            "stable_continuation_blocked_context": stable_context_summary,
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
            "target_vs_displacement": {
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
            "target_vs_stable_context": {
                "fwd_16_close_return_pct": _descriptive_gap(
                    target_summary,
                    stable_context_summary,
                    "fwd_16_close_return_pct",
                ),
                "mfe_16_pct": _descriptive_gap(
                    target_summary,
                    stable_context_summary,
                    "mfe_16_pct",
                ),
                "mae_16_pct": _descriptive_gap(
                    target_summary,
                    stable_context_summary,
                    "mae_16_pct",
                ),
            },
        },
        "local_timeline": local_timeline,
    }


def main() -> int:
    args = _parse_args()
    output_root = ROOT_DIR / Path(args.output_root_relative)
    output_json = output_root / args.summary_filename
    result = run_regression_pocket_analysis(base_sha=args.base_sha)

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "summary_artifact": str(output_json),
                "target_row_count": result["cohorts"]["regression_target"]["row_count"],
                "comparison_row_count": result["cohorts"][
                    "stable_continuation_displacement_comparison"
                ]["row_count"],
                "stable_context_row_count": result["cohorts"][
                    "stable_continuation_blocked_context"
                ]["row_count"],
                "context_row_count": result["cohorts"]["context_only"]["row_count"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
