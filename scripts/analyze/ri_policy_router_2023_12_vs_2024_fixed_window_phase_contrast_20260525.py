from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from statistics import fmean
from typing import Any

import pandas as pd

LOCAL_ROOT_DIR = Path(__file__).resolve().parents[2]
if str(LOCAL_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(LOCAL_ROOT_DIR))

from scripts.analyze.ri_policy_router_insufficient_evidence_local_window_20260429 import (
    ACTION_DIFF_ROOT,
    ACTION_DIFF_ROOT_RELATIVE,
    CURATED_CANDLES_PATH,
    CURATED_CANDLES_RELATIVE,
    LOCAL_PADDING,
    MAX_ADJACENCY_GAP,
    ROOT_DIR,
    LocalWindowEvidenceError,
    SubjectBounds,
    _cohort_summary,
    _descriptive_gap,
    _load_candles,
    _normalized_constant_timestamps,
    _round_or_none,
    _serialize_local_row,
    build_local_envelope,
    group_adjacent_timestamps,
    load_subject_rows,
    select_exact_rows,
)

OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = "ri_policy_router_2023_12_vs_2024_fixed_window_phase_contrast_2026-05-25.json"
SUBJECT_SYMBOL = "tBTCUSD"
SUBJECT_TIMEFRAME = "3h"
SUBJECT_2023_YEAR = "2023"
SUBJECT_2024_YEAR = "2024"
TARGET_2023_WAVE_ONE_TIMESTAMPS = (
    "2023-12-15T21:00:00+00:00",
    "2023-12-16T06:00:00+00:00",
    "2023-12-16T15:00:00+00:00",
    "2023-12-17T00:00:00+00:00",
    "2023-12-17T09:00:00+00:00",
    "2023-12-17T18:00:00+00:00",
)
TARGET_2023_WAVE_TWO_TIMESTAMPS = (
    "2023-12-22T15:00:00+00:00",
    "2023-12-23T00:00:00+00:00",
    "2023-12-23T09:00:00+00:00",
    "2023-12-24T03:00:00+00:00",
    "2023-12-24T12:00:00+00:00",
    "2023-12-25T06:00:00+00:00",
    "2023-12-26T00:00:00+00:00",
)
TARGET_2024_TIMESTAMPS = (
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
EXPECTED_2024_TARGET_REASON_COUNTS = {
    "AGED_WEAK_CONTINUATION_GUARD": 4,
    "insufficient_evidence": 5,
}
TARGET_2024_DISPLACEMENT_TIMESTAMPS = ("2024-12-01T00:00:00+00:00",)
TARGET_2024_STABLE_CONTEXT_TIMESTAMPS = ("2024-12-01T06:00:00+00:00",)
CURATED_ANNUAL_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_enabled_vs_absent_curated_annual_evidence_2026-04-28.md"
)
NEGATIVE_YEAR_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_negative_year_pocket_isolation_2026-04-28.md"
)
POSITIVE_NEGATIVE_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_positive_vs_negative_pocket_comparison_2026-04-28.md"
)
WINDOW_CONCENTRATION_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_2023_12_vs_2017_03_continuation_local_window_concentration_2026-05-06.md"
)
WINDOW_CHRONOLOGY_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_2023_12_vs_2017_03_dominant_window_chronology_2026-05-06.md"
)
REGRESSION_POCKET_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_2024_regression_pocket_isolation_2026-04-30.md"
)
REASON_SPLIT_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_2024_regression_pocket_reason_split_2026-04-30.md"
)
FINDINGS_INDEX_REFERENCE = Path("artifacts/research_ledger/indexes/findings_index.json")
REGRESSION_POCKET_ARTIFACT_REFERENCE = Path(
    "results/evaluation/ri_policy_router_2024_regression_pocket_isolation_2026-04-30.json"
)
WORKING_CONTRACT_REFERENCE = Path("GENESIS_WORKING_CONTRACT.md")
STATUS_OK = "fixed_window_phase_contrast_generated"
STATUS_FAIL_CLOSED = "fixed_window_phase_contrast_fail_closed"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Contrast the fixed 2023-12 continuation-local dual-wave surface against the fixed "
            "late-2024 harmful pocket using descriptive phase structure and proxy metrics only."
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


def _exact_timestamp_strings(values: tuple[pd.Timestamp, ...]) -> list[str]:
    return [value.isoformat() for value in values]


def _load_existing_2024_proxy_reference() -> dict[str, Any] | None:
    path = ROOT_DIR / REGRESSION_POCKET_ARTIFACT_REFERENCE
    if not path.is_file():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise LocalWindowEvidenceError(
            "Existing 2024 regression pocket artifact is malformed or not a JSON object"
        )
    return {
        "path": str(REGRESSION_POCKET_ARTIFACT_REFERENCE),
        "cohorts": payload.get("cohorts"),
        "descriptive_comparison": payload.get("descriptive_comparison"),
    }


def _validate_exact_continuation_windows(
    rows: list[Any],
    *,
    exact_timestamps: tuple[pd.Timestamp, ...],
    expected_window_sizes: list[int],
) -> list[Any]:
    matched = select_exact_rows(
        rows,
        exact_timestamps=exact_timestamps,
        expected_reason="stable_continuation_state",
        expected_action_pair=("NONE", "LONG"),
    )
    invalid_rows = [
        row
        for row in matched
        if row.selected_policy != "RI_continuation_policy"
        or row.raw_target_policy != "RI_continuation_policy"
    ]
    if invalid_rows:
        invalid_payload = [
            {
                "timestamp": row.timestamp.isoformat(),
                "selected_policy": row.selected_policy,
                "raw_target_policy": row.raw_target_policy,
            }
            for row in invalid_rows
        ]
        raise LocalWindowEvidenceError(
            "Exact 2023 continuation rows failed continuation-policy validation: "
            f"{invalid_payload}"
        )

    grouped = group_adjacent_timestamps(
        [row.timestamp for row in matched],
        max_gap=MAX_ADJACENCY_GAP,
    )
    observed_sizes = [len(group) for group in grouped]
    if observed_sizes != expected_window_sizes:
        rendered_groups = [[timestamp.isoformat() for timestamp in group] for group in grouped]
        raise LocalWindowEvidenceError(
            "Exact 2023 continuation window packaging drifted: "
            f"expected_sizes={expected_window_sizes}, actual_sizes={observed_sizes}, "
            f"groups={rendered_groups}"
        )

    return matched


def _select_exact_target_rows(
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
            "Exact 2024 regression target rows did not materialize cleanly; "
            f"missing={missing}, extra={extra}"
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
            "Exact 2024 regression target rows failed reason/action validation: "
            f"{invalid_payload}"
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


def _serialize_phase_row(
    row: Any,
    *,
    cohort_label: str,
    phase_label: str,
    phase_family: str,
    candles: pd.DataFrame | None,
    timestamp_to_index: dict[pd.Timestamp, int] | None,
) -> dict[str, Any]:
    if candles is not None and timestamp_to_index is not None:
        serialized = _serialize_local_row(
            row,
            cohort_label=cohort_label,
            candles=candles,
            timestamp_to_index=timestamp_to_index,
        )
    else:
        serialized = {
            "timestamp": row.timestamp.isoformat(),
            "cohort_label": cohort_label,
            "switch_reason": row.switch_reason,
            "absent_action": row.absent_action,
            "enabled_action": row.enabled_action,
            "action_pair": row.action_pair,
            "selected_policy": row.selected_policy,
            "raw_target_policy": row.raw_target_policy,
            "previous_policy": row.previous_policy,
            "zone": row.zone,
            "candidate": row.candidate,
            "bars_since_regime_change": row.bars_since_regime_change,
            "action_edge": row.action_edge,
            "confidence_gate": row.confidence_gate,
            "clarity_score": row.clarity_score,
            "entry_close": None,
            "matched_candle_index": None,
            "future_bars_available": None,
            "fwd_4_close_return_pct": None,
            "fwd_8_close_return_pct": None,
            "fwd_16_close_return_pct": None,
            "mfe_16_pct": None,
            "mae_16_pct": None,
        }
    serialized["phase_label"] = phase_label
    serialized["phase_family"] = phase_family
    return serialized


def _segment_serialized_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not rows:
        return []

    segments: list[list[dict[str, Any]]] = [[rows[0]]]
    for row in rows[1:]:
        current_timestamp = pd.Timestamp(row["timestamp"])
        previous_timestamp = pd.Timestamp(segments[-1][-1]["timestamp"])
        same_label = row["phase_label"] == segments[-1][-1]["phase_label"]
        within_gap = current_timestamp - previous_timestamp <= MAX_ADJACENCY_GAP
        if same_label and within_gap:
            segments[-1].append(row)
        else:
            segments.append([row])

    out: list[dict[str, Any]] = []
    for segment in segments:
        start = pd.Timestamp(segment[0]["timestamp"])
        end = pd.Timestamp(segment[-1]["timestamp"])
        fwd_16_values = [
            float(row["fwd_16_close_return_pct"])
            for row in segment
            if isinstance(row.get("fwd_16_close_return_pct"), int | float)
        ]
        out.append(
            {
                "phase_label": segment[0]["phase_label"],
                "phase_family": segment[0]["phase_family"],
                "row_count": len(segment),
                "start": start.isoformat(),
                "end": end.isoformat(),
                "span_hours": _round_or_none((end - start).total_seconds() / 3600.0),
                "timestamps": [row["timestamp"] for row in segment],
                "switch_reason_counts": [
                    {"switch_reason": key, "count": value}
                    for key, value in Counter(row["switch_reason"] for row in segment).most_common()
                ],
                "action_pair_counts": [
                    {"action_pair": key, "count": value}
                    for key, value in Counter(row["action_pair"] for row in segment).most_common()
                ],
                "fwd_16_mean": _round_or_none(fmean(fwd_16_values)) if fwd_16_values else None,
            }
        )
    return out


def _summarize_phase_subject(rows: list[dict[str, Any]]) -> dict[str, Any]:
    segments = _segment_serialized_rows(rows)
    blocked_like_rows = [row for row in rows if row["phase_family"] == "blocked_like"]
    continuation_like_rows = [row for row in rows if row["phase_family"] == "continuation_like"]
    return {
        "row_count": len(rows),
        "blocked_like_row_count": len(blocked_like_rows),
        "continuation_like_row_count": len(continuation_like_rows),
        "blocked_like_row_share": _round_or_none(
            len(blocked_like_rows) / len(rows) if rows else None
        ),
        "continuation_like_row_share": _round_or_none(
            len(continuation_like_rows) / len(rows) if rows else None
        ),
        "segment_count": len(segments),
        "leading_phase_label": segments[0]["phase_label"] if segments else None,
        "trailing_phase_label": segments[-1]["phase_label"] if segments else None,
        "phase_label_sequence": [segment["phase_label"] for segment in segments],
        "segments": segments,
    }


def _label_2023_row(
    row: Any,
    *,
    wave_one_timestamps: set[pd.Timestamp],
    wave_two_timestamps: set[pd.Timestamp],
) -> tuple[str, str, str]:
    if row.timestamp in wave_one_timestamps:
        return (
            "continuation_wave_one",
            "continuation_release",
            "continuation_like",
        )
    if row.timestamp in wave_two_timestamps:
        return (
            "continuation_wave_two",
            "continuation_release",
            "continuation_like",
        )
    raise LocalWindowEvidenceError(
        f"Unexpected 2023 continuation timestamp outside fixed waves: {row.timestamp.isoformat()}"
    )


def _label_2024_row(
    row: Any,
    *,
    target_timestamps: set[pd.Timestamp],
    displacement_timestamps: set[pd.Timestamp],
    stable_context_timestamps: set[pd.Timestamp],
) -> tuple[str, str, str]:
    if row.timestamp in displacement_timestamps:
        return (
            "stable_continuation_displacement",
            "continuation_release",
            "continuation_like",
        )
    if row.timestamp in stable_context_timestamps:
        return (
            "stable_continuation_blocked_context",
            "blocked_stable_context",
            "blocked_like",
        )
    if row.timestamp in target_timestamps:
        if row.switch_reason == "AGED_WEAK_CONTINUATION_GUARD":
            return (
                "regression_target",
                "blocked_aged_weak_continuation_guard",
                "blocked_like",
            )
        if row.switch_reason == "insufficient_evidence":
            return (
                "regression_target",
                "blocked_insufficient_evidence",
                "blocked_like",
            )
    raise LocalWindowEvidenceError(
        f"Unexpected 2024 harmful-surface timestamp classification: {row.timestamp.isoformat()}"
    )


def _build_fail_closed_result(base_sha: str, reason: str) -> dict[str, Any]:
    return {
        "audit_version": "ri-policy-router-2023-12-vs-2024-fixed-window-phase-contrast-2026-05-25",
        "base_sha": base_sha,
        "status": STATUS_FAIL_CLOSED,
        "observational_only": True,
        "non_authoritative": True,
        "skill_usage": ["python_engineering"],
        "failure_reason": reason,
        "subject": {
            "symbol": SUBJECT_SYMBOL,
            "timeframe": SUBJECT_TIMEFRAME,
            "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
        },
    }


def run_phase_contrast(base_sha: str) -> dict[str, Any]:
    try:
        try:
            candles, timestamp_to_index = _load_candles(CURATED_CANDLES_PATH)
        except FileNotFoundError:
            candles = None
            timestamp_to_index = None

        existing_2024_proxy_reference = _load_existing_2024_proxy_reference()
        rows_2023 = load_subject_rows(
            ACTION_DIFF_ROOT / f"{SUBJECT_2023_YEAR}_enabled_vs_absent_action_diffs.json"
        )
        rows_2024 = load_subject_rows(
            ACTION_DIFF_ROOT / f"{SUBJECT_2024_YEAR}_enabled_vs_absent_action_diffs.json"
        )

        exact_2023_wave_one = _normalized_constant_timestamps(TARGET_2023_WAVE_ONE_TIMESTAMPS)
        exact_2023_wave_two = _normalized_constant_timestamps(TARGET_2023_WAVE_TWO_TIMESTAMPS)
        exact_2023_combined = exact_2023_wave_one + exact_2023_wave_two
        exact_2024_target = _normalized_constant_timestamps(TARGET_2024_TIMESTAMPS)
        exact_2024_displacement = _normalized_constant_timestamps(
            TARGET_2024_DISPLACEMENT_TIMESTAMPS
        )
        exact_2024_stable_context = _normalized_constant_timestamps(
            TARGET_2024_STABLE_CONTEXT_TIMESTAMPS
        )

        continuation_rows = _validate_exact_continuation_windows(
            rows_2023,
            exact_timestamps=exact_2023_combined,
            expected_window_sizes=[6, 7],
        )
        target_rows = _select_exact_target_rows(
            rows_2024,
            exact_timestamps=exact_2024_target,
            expected_reason_counts=EXPECTED_2024_TARGET_REASON_COUNTS,
        )
        displacement_rows = select_exact_rows(
            rows_2024,
            exact_timestamps=exact_2024_displacement,
            expected_reason="stable_continuation_state",
            expected_action_pair=("NONE", "LONG"),
        )
        stable_context_rows = select_exact_rows(
            rows_2024,
            exact_timestamps=exact_2024_stable_context,
            expected_reason="stable_continuation_state",
            expected_action_pair=("LONG", "NONE"),
        )

        wave_one_set = set(exact_2023_wave_one)
        wave_two_set = set(exact_2023_wave_two)
        target_set = set(exact_2024_target)
        displacement_set = set(exact_2024_displacement)
        stable_context_set = set(exact_2024_stable_context)

        continuation_timeline = []
        for row in continuation_rows:
            cohort_label, phase_label, phase_family = _label_2023_row(
                row,
                wave_one_timestamps=wave_one_set,
                wave_two_timestamps=wave_two_set,
            )
            continuation_timeline.append(
                _serialize_phase_row(
                    row,
                    cohort_label=cohort_label,
                    phase_label=phase_label,
                    phase_family=phase_family,
                    candles=candles,
                    timestamp_to_index=timestamp_to_index,
                )
            )

        harmful_timeline_rows = [
            *target_rows,
            *displacement_rows,
            *stable_context_rows,
        ]
        harmful_timeline_rows = sorted(harmful_timeline_rows, key=lambda row: row.timestamp)
        harmful_timeline = []
        for row in harmful_timeline_rows:
            cohort_label, phase_label, phase_family = _label_2024_row(
                row,
                target_timestamps=target_set,
                displacement_timestamps=displacement_set,
                stable_context_timestamps=stable_context_set,
            )
            harmful_timeline.append(
                _serialize_phase_row(
                    row,
                    cohort_label=cohort_label,
                    phase_label=phase_label,
                    phase_family=phase_family,
                    candles=candles,
                    timestamp_to_index=timestamp_to_index,
                )
            )

        wave_one_serialized = [
            row for row in continuation_timeline if row["cohort_label"] == "continuation_wave_one"
        ]
        wave_two_serialized = [
            row for row in continuation_timeline if row["cohort_label"] == "continuation_wave_two"
        ]
        target_serialized = [
            row for row in harmful_timeline if row["cohort_label"] == "regression_target"
        ]
        displacement_serialized = [
            row
            for row in harmful_timeline
            if row["cohort_label"] == "stable_continuation_displacement"
        ]
        stable_context_serialized = [
            row
            for row in harmful_timeline
            if row["cohort_label"] == "stable_continuation_blocked_context"
        ]

        target_bounds = SubjectBounds(start=target_rows[0].timestamp, end=target_rows[-1].timestamp)
        harmful_envelope = build_local_envelope(target_bounds, padding=LOCAL_PADDING)

        combined_summary = _cohort_summary(continuation_timeline)
        wave_one_summary = _cohort_summary(wave_one_serialized)
        wave_two_summary = _cohort_summary(wave_two_serialized)
        target_summary = _cohort_summary(target_serialized)
        displacement_summary = _cohort_summary(displacement_serialized)
        stable_context_summary = _cohort_summary(stable_context_serialized)

        continuation_phase_summary = _summarize_phase_subject(continuation_timeline)
        harmful_phase_summary = _summarize_phase_subject(harmful_timeline)
    except LocalWindowEvidenceError as exc:
        return _build_fail_closed_result(base_sha=base_sha, reason=str(exc))

    return {
        "audit_version": "ri-policy-router-2023-12-vs-2024-fixed-window-phase-contrast-2026-05-25",
        "base_sha": base_sha,
        "status": STATUS_OK,
        "observational_only": True,
        "non_authoritative": True,
        "skill_usage": ["python_engineering"],
        "subject": {
            "symbol": SUBJECT_SYMBOL,
            "timeframe": SUBJECT_TIMEFRAME,
            "statement": (
                "Fixed-window descriptive contrast only: compare the exact 2023-12 dual-wave "
                "continuation surface against the exact late-2024 harmful pocket without "
                "reopening runtime tuning, threshold discovery, or year-level screening."
            ),
            "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
        },
        "inputs": {
            "action_diff_root": str(ACTION_DIFF_ROOT_RELATIVE),
            "subject_diffs": {
                "2023": str(ACTION_DIFF_ROOT_RELATIVE / "2023_enabled_vs_absent_action_diffs.json"),
                "2024": str(ACTION_DIFF_ROOT_RELATIVE / "2024_enabled_vs_absent_action_diffs.json"),
            },
            "curated_candles": str(CURATED_CANDLES_RELATIVE),
            "motivating_anchors": [
                str(CURATED_ANNUAL_REFERENCE),
                str(NEGATIVE_YEAR_REFERENCE),
                str(POSITIVE_NEGATIVE_REFERENCE),
                str(WINDOW_CONCENTRATION_REFERENCE),
                str(WINDOW_CHRONOLOGY_REFERENCE),
                str(REGRESSION_POCKET_REFERENCE),
                str(REASON_SPLIT_REFERENCE),
                str(FINDINGS_INDEX_REFERENCE),
            ],
            "existing_2024_proxy_artifact": str(REGRESSION_POCKET_ARTIFACT_REFERENCE),
        },
        "proxy_availability": {
            "curated_candles_available": candles is not None,
            "row_level_proxy_metrics_materialized": candles is not None,
            "note": (
                "If curated candles are missing in the current workspace, the helper still emits "
                "the fixed-window structure contrast and reuses the committed 2024 proxy artifact "
                "as a reference only."
            ),
        },
        "existing_2024_proxy_reference": existing_2024_proxy_reference,
        "fixed_subject_lock": {
            "continuation_2023_12": {
                "wave_one_timestamps": _exact_timestamp_strings(exact_2023_wave_one),
                "wave_two_timestamps": _exact_timestamp_strings(exact_2023_wave_two),
                "combined_timestamp_count": len(exact_2023_combined),
                "expected_window_sizes": [6, 7],
                "cohort_rule": (
                    "exact stable_continuation_state NONE->LONG rows, packaged as two <=24h "
                    "continuation-release waves"
                ),
            },
            "harmful_2024": {
                "target_timestamps": _exact_timestamp_strings(exact_2024_target),
                "target_reason_counts": EXPECTED_2024_TARGET_REASON_COUNTS,
                "displacement_timestamps": _exact_timestamp_strings(exact_2024_displacement),
                "stable_context_timestamps": _exact_timestamp_strings(exact_2024_stable_context),
                "harmful_envelope_bounds": {
                    "start": harmful_envelope.start.isoformat(),
                    "end": harmful_envelope.end.isoformat(),
                },
                "cohort_rule": (
                    "exact late-2024 harmful pocket: mixed LONG->NONE blocked target cluster plus "
                    "one nearby NONE->LONG stable-continuation displacement row and one nearby "
                    "LONG->NONE stable blocked context row"
                ),
            },
        },
        "cohorts": {
            "continuation_2023_wave_one": wave_one_summary,
            "continuation_2023_wave_two": wave_two_summary,
            "continuation_2023_combined": combined_summary,
            "harmful_2024_regression_target": target_summary,
            "harmful_2024_displacement": displacement_summary,
            "harmful_2024_stable_context": stable_context_summary,
        },
        "phase_subject_summaries": {
            "continuation_2023": continuation_phase_summary,
            "harmful_2024": harmful_phase_summary,
        },
        "descriptive_comparison": {
            "continuation_2023_combined_vs_2024_target": {
                "fwd_16_close_return_pct": _descriptive_gap(
                    combined_summary,
                    target_summary,
                    "fwd_16_close_return_pct",
                ),
                "mfe_16_pct": _descriptive_gap(
                    combined_summary,
                    target_summary,
                    "mfe_16_pct",
                ),
                "mae_16_pct": _descriptive_gap(
                    combined_summary,
                    target_summary,
                    "mae_16_pct",
                ),
            },
            "continuation_2023_wave_two_vs_2024_target": {
                "fwd_16_close_return_pct": _descriptive_gap(
                    wave_two_summary,
                    target_summary,
                    "fwd_16_close_return_pct",
                ),
                "mfe_16_pct": _descriptive_gap(
                    wave_two_summary,
                    target_summary,
                    "mfe_16_pct",
                ),
                "mae_16_pct": _descriptive_gap(
                    wave_two_summary,
                    target_summary,
                    "mae_16_pct",
                ),
            },
            "continuation_2023_combined_vs_2024_displacement": {
                "fwd_16_close_return_pct": _descriptive_gap(
                    combined_summary,
                    displacement_summary,
                    "fwd_16_close_return_pct",
                ),
                "mfe_16_pct": _descriptive_gap(
                    combined_summary,
                    displacement_summary,
                    "mfe_16_pct",
                ),
                "mae_16_pct": _descriptive_gap(
                    combined_summary,
                    displacement_summary,
                    "mae_16_pct",
                ),
            },
        },
        "timelines": {
            "continuation_2023": continuation_timeline,
            "harmful_2024": harmful_timeline,
        },
    }


def main() -> int:
    args = _parse_args()
    output_root = ROOT_DIR / Path(args.output_root_relative)
    output_json = output_root / args.summary_filename
    result = run_phase_contrast(base_sha=args.base_sha)

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "summary_artifact": str(output_json),
                "status": result["status"],
                "continuation_2023_rows": result.get("cohorts", {})
                .get("continuation_2023_combined", {})
                .get("row_count"),
                "harmful_2024_target_rows": result.get("cohorts", {})
                .get("harmful_2024_regression_target", {})
                .get("row_count"),
                "continuation_2023_segment_count": result.get("phase_subject_summaries", {})
                .get("continuation_2023", {})
                .get("segment_count"),
                "harmful_2024_segment_count": result.get("phase_subject_summaries", {})
                .get("harmful_2024", {})
                .get("segment_count"),
                "failure_reason": result.get("failure_reason"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
