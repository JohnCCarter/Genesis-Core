from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from statistics import fmean, median
from typing import Any

import pandas as pd

ACTION_DIFF_ROOT_RELATIVE = Path(
    "results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only"
)
CURATED_CANDLES_RELATIVE = Path("data/curated/v1/candles/tBTCUSD_3h.parquet")
OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = "ri_policy_router_insufficient_evidence_local_window_2026-04-29.json"
FORWARD_HORIZONS = (4, 8, 16)
EXCURSION_HORIZON = 16
SUBJECT_SYMBOL = "tBTCUSD"
SUBJECT_TIMEFRAME = "3h"
SUBJECT_YEAR = "2021"
LOCAL_PADDING = pd.Timedelta(hours=24)
MAX_ADJACENCY_GAP = pd.Timedelta(hours=24)
TARGET_IE_TIMESTAMPS = (
    "2021-03-26T12:00:00+00:00",
    "2021-03-27T06:00:00+00:00",
    "2021-03-27T15:00:00+00:00",
    "2021-03-28T00:00:00+00:00",
)
COMPARISON_STABLE_DISPLACEMENT_TIMESTAMPS = (
    "2021-03-26T15:00:00+00:00",
    "2021-03-29T00:00:00+00:00",
)


class LocalWindowEvidenceError(RuntimeError):
    """Raised when the fixed local-window evidence cannot be materialized safely."""


@dataclass(frozen=True)
class NormalizedActionDiffRow:
    timestamp: pd.Timestamp
    switch_reason: str
    absent_action: str
    enabled_action: str
    selected_policy: str
    raw_target_policy: str
    previous_policy: str
    zone: str
    candidate: str
    bars_since_regime_change: int
    action_edge: float | None
    confidence_gate: float | None
    clarity_score: float | None

    @property
    def action_pair(self) -> str:
        return f"{self.absent_action}->{self.enabled_action}"


@dataclass(frozen=True)
class SubjectBounds:
    start: pd.Timestamp
    end: pd.Timestamp


def _find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "pyproject.toml").exists() and (candidate / "src").exists():
            return candidate
    raise LocalWindowEvidenceError("Could not locate repository root from helper path")


ROOT_DIR = _find_repo_root(Path(__file__).resolve())
ACTION_DIFF_ROOT = ROOT_DIR / ACTION_DIFF_ROOT_RELATIVE
CURATED_CANDLES_PATH = ROOT_DIR / CURATED_CANDLES_RELATIVE


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Materialize one fixed negative-year insufficient-evidence local window and compare "
            "it against nearby stable-continuation displacement rows."
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


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_timestamp(value: Any) -> pd.Timestamp:
    timestamp = pd.Timestamp(value)
    if timestamp.tzinfo is None:
        return timestamp.tz_localize("UTC")
    return timestamp.tz_convert("UTC")


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise LocalWindowEvidenceError(f"Expected numeric optional value, got {value!r}")
    out = float(value)
    if out != out or out in {float("inf"), float("-inf")}:
        raise LocalWindowEvidenceError(f"Expected finite optional value, got {value!r}")
    return out


def _load_candles(path: Path) -> tuple[pd.DataFrame, dict[pd.Timestamp, int]]:
    candles = pd.read_parquet(path)
    required_columns = {"timestamp", "open", "close", "high", "low", "volume"}
    missing = sorted(required_columns - set(candles.columns))
    if missing:
        raise LocalWindowEvidenceError(f"Missing candle columns in {path}: {missing}")

    frame = candles.loc[:, ["timestamp", "open", "close", "high", "low", "volume"]].copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
    frame = frame.sort_values("timestamp").reset_index(drop=True)
    if frame["timestamp"].duplicated().any():
        raise LocalWindowEvidenceError(f"Duplicate timestamps detected in {path}")

    timestamp_to_index = {
        _normalize_timestamp(timestamp): int(index)
        for index, timestamp in enumerate(frame["timestamp"].tolist())
    }
    return frame, timestamp_to_index


def _pct_change(entry_price: float, exit_price: float) -> float:
    return ((exit_price - entry_price) / entry_price) * 100.0


def _row_observational_metrics(
    *,
    timestamp: pd.Timestamp,
    candles: pd.DataFrame,
    timestamp_to_index: dict[pd.Timestamp, int],
) -> dict[str, float | int | None]:
    index = timestamp_to_index.get(_normalize_timestamp(timestamp))
    if index is None:
        raise LocalWindowEvidenceError(
            f"Timestamp {timestamp.isoformat()} was not found in candles"
        )

    entry_close = float(candles.at[index, "close"])
    metrics: dict[str, float | int | None] = {
        "entry_close": round(entry_close, 6),
        "matched_candle_index": index,
    }

    for horizon in FORWARD_HORIZONS:
        future_index = index + horizon
        metric_key = f"fwd_{horizon}_close_return_pct"
        if future_index >= len(candles):
            metrics[metric_key] = None
            continue
        future_close = float(candles.at[future_index, "close"])
        metrics[metric_key] = round(_pct_change(entry_close, future_close), 6)

    excursion_start = index + 1
    excursion_end = min(index + EXCURSION_HORIZON, len(candles) - 1)
    if excursion_start > excursion_end:
        metrics["mfe_16_pct"] = None
        metrics["mae_16_pct"] = None
        metrics["future_bars_available"] = 0
        return metrics

    future_high = float(candles.loc[excursion_start:excursion_end, "high"].max())
    future_low = float(candles.loc[excursion_start:excursion_end, "low"].min())
    metrics["mfe_16_pct"] = round(_pct_change(entry_close, future_high), 6)
    metrics["mae_16_pct"] = round(_pct_change(entry_close, future_low), 6)
    metrics["future_bars_available"] = excursion_end - excursion_start + 1
    return metrics


def _normalize_action_diff_row(row: dict[str, Any]) -> NormalizedActionDiffRow | None:
    enabled = row.get("enabled") or {}
    absent = row.get("absent") or {}
    router_debug = enabled.get("router_debug")
    if not isinstance(router_debug, dict):
        return None
    if router_debug.get("zone") != "low":
        return None
    if router_debug.get("candidate") != "LONG":
        return None
    bars_since_regime_change = router_debug.get("bars_since_regime_change")
    if not isinstance(bars_since_regime_change, int) or bars_since_regime_change < 8:
        return None

    timestamp_value = row.get("timestamp")
    if not isinstance(timestamp_value, str):
        raise LocalWindowEvidenceError("Action-diff row is missing a string timestamp")

    return NormalizedActionDiffRow(
        timestamp=_normalize_timestamp(timestamp_value),
        switch_reason=str(router_debug.get("switch_reason") or "unknown"),
        absent_action=str(absent.get("action") or "NONE"),
        enabled_action=str(enabled.get("action") or "NONE"),
        selected_policy=str(router_debug.get("selected_policy") or "unknown"),
        raw_target_policy=str(router_debug.get("raw_target_policy") or "unknown"),
        previous_policy=str(router_debug.get("previous_policy") or "unknown"),
        zone=str(router_debug.get("zone") or "unknown"),
        candidate=str(router_debug.get("candidate") or "unknown"),
        bars_since_regime_change=bars_since_regime_change,
        action_edge=_optional_float(router_debug.get("action_edge")),
        confidence_gate=_optional_float(router_debug.get("confidence_gate")),
        clarity_score=_optional_float(router_debug.get("clarity_score")),
    )


def load_subject_rows(diff_path: Path) -> list[NormalizedActionDiffRow]:
    payload = _load_json(diff_path)
    if not isinstance(payload, list):
        raise LocalWindowEvidenceError(f"Expected row list in {diff_path}")

    rows: list[NormalizedActionDiffRow] = []
    for item in payload:
        if not isinstance(item, dict):
            raise LocalWindowEvidenceError(f"Expected object rows in {diff_path}")
        normalized = _normalize_action_diff_row(item)
        if normalized is not None:
            rows.append(normalized)
    return sorted(rows, key=lambda row: row.timestamp)


def group_adjacent_timestamps(
    timestamps: list[pd.Timestamp], *, max_gap: pd.Timedelta
) -> list[list[pd.Timestamp]]:
    if not timestamps:
        return []

    ordered = sorted(_normalize_timestamp(timestamp) for timestamp in timestamps)
    groups: list[list[pd.Timestamp]] = [[ordered[0]]]
    for current in ordered[1:]:
        if current - groups[-1][-1] <= max_gap:
            groups[-1].append(current)
        else:
            groups.append([current])
    return groups


def _normalized_constant_timestamps(values: tuple[str, ...]) -> tuple[pd.Timestamp, ...]:
    return tuple(_normalize_timestamp(value) for value in values)


def select_exact_rows(
    rows: list[NormalizedActionDiffRow],
    *,
    exact_timestamps: tuple[pd.Timestamp, ...],
    expected_reason: str,
    expected_action_pair: tuple[str, str],
) -> list[NormalizedActionDiffRow]:
    expected_set = set(exact_timestamps)
    matched = [row for row in rows if row.timestamp in expected_set]
    matched_set = {row.timestamp for row in matched}
    if matched_set != expected_set:
        missing = sorted(timestamp.isoformat() for timestamp in expected_set - matched_set)
        extra = sorted(timestamp.isoformat() for timestamp in matched_set - expected_set)
        raise LocalWindowEvidenceError(
            f"Exact subject rows did not materialize cleanly; missing={missing}, extra={extra}"
        )

    invalid_rows = [
        row
        for row in matched
        if row.switch_reason != expected_reason
        or (row.absent_action, row.enabled_action) != expected_action_pair
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
            f"Exact subject rows failed reason/action validation: {invalid_payload}"
        )

    return sorted(matched, key=lambda row: row.timestamp)


def _validate_exact_insufficient_evidence_cluster(
    rows: list[NormalizedActionDiffRow], *, exact_timestamps: tuple[pd.Timestamp, ...]
) -> None:
    clustered_timestamps = [
        row.timestamp
        for row in rows
        if row.switch_reason == "insufficient_evidence"
        and row.absent_action == "LONG"
        and row.enabled_action == "NONE"
    ]
    grouped = group_adjacent_timestamps(clustered_timestamps, max_gap=MAX_ADJACENCY_GAP)
    exact_set = set(exact_timestamps)
    matches = [group for group in grouped if set(group) == exact_set]
    if len(matches) != 1:
        rendered_groups = [[timestamp.isoformat() for timestamp in group] for group in grouped]
        raise LocalWindowEvidenceError(
            "Exact insufficient-evidence cluster was not recovered as one <=24h adjacency group: "
            f"{rendered_groups}"
        )


def build_local_envelope(bounds: SubjectBounds, *, padding: pd.Timedelta) -> SubjectBounds:
    return SubjectBounds(start=bounds.start - padding, end=bounds.end + padding)


def _row_cohort_label(
    row: NormalizedActionDiffRow,
    *,
    target_timestamps: set[pd.Timestamp],
    comparison_timestamps: set[pd.Timestamp],
) -> str:
    if row.timestamp in target_timestamps:
        return "insufficient_evidence_target"
    if row.timestamp in comparison_timestamps:
        return "stable_continuation_displacement_comparison"
    return "context_only"


def _round_or_none(value: float | None) -> float | None:
    if value is None:
        return None
    return round(value, 6)


def _summarize_numeric_values(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"count": 0, "mean": None, "median": None, "gt_zero_share": None}
    positive_share = sum(value > 0 for value in values) / len(values)
    return {
        "count": len(values),
        "mean": _round_or_none(fmean(values)),
        "median": _round_or_none(median(values)),
        "gt_zero_share": _round_or_none(positive_share),
    }


def _serialize_local_row(
    row: NormalizedActionDiffRow,
    *,
    cohort_label: str,
    candles: pd.DataFrame,
    timestamp_to_index: dict[pd.Timestamp, int],
) -> dict[str, Any]:
    return {
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
        **_row_observational_metrics(
            timestamp=row.timestamp,
            candles=candles,
            timestamp_to_index=timestamp_to_index,
        ),
    }


def _cohort_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    action_pair_counts = Counter(row["action_pair"] for row in rows)
    switch_reason_counts = Counter(row["switch_reason"] for row in rows)
    selected_policy_counts = Counter(row["selected_policy"] for row in rows)
    bars_values = [int(row["bars_since_regime_change"]) for row in rows]
    metric_summary = {
        metric: _summarize_numeric_values(
            [float(row[metric]) for row in rows if isinstance(row.get(metric), int | float)]
        )
        for metric in (
            "fwd_4_close_return_pct",
            "fwd_8_close_return_pct",
            "fwd_16_close_return_pct",
            "mfe_16_pct",
            "mae_16_pct",
            "action_edge",
            "confidence_gate",
            "clarity_score",
        )
    }
    return {
        "row_count": len(rows),
        "timestamps": [row["timestamp"] for row in rows],
        "action_pair_counts": [
            {"action_pair": action_pair, "count": count}
            for action_pair, count in action_pair_counts.most_common()
        ],
        "switch_reason_counts": [
            {"switch_reason": switch_reason, "count": count}
            for switch_reason, count in switch_reason_counts.most_common()
        ],
        "selected_policy_counts": [
            {"selected_policy": selected_policy, "count": count}
            for selected_policy, count in selected_policy_counts.most_common()
        ],
        "bars_since_regime_change": {
            "min": min(bars_values),
            "max": max(bars_values),
            "mean": _round_or_none(fmean(float(value) for value in bars_values)),
            "median": _round_or_none(median(float(value) for value in bars_values)),
        },
        "metric_summary": metric_summary,
        "rows": rows,
    }


def _descriptive_gap(
    left_summary: dict[str, Any],
    right_summary: dict[str, Any],
    metric_name: str,
) -> dict[str, float | None]:
    left_metric = left_summary["metric_summary"][metric_name]
    right_metric = right_summary["metric_summary"][metric_name]
    left_mean = left_metric["mean"]
    right_mean = right_metric["mean"]
    left_median = left_metric["median"]
    right_median = right_metric["median"]
    return {
        "mean_gap_left_minus_right": _round_or_none(
            None
            if left_mean is None or right_mean is None
            else float(left_mean) - float(right_mean)
        ),
        "median_gap_left_minus_right": _round_or_none(
            None
            if left_median is None or right_median is None
            else float(left_median) - float(right_median)
        ),
    }


def run_local_window_analysis(base_sha: str) -> dict[str, Any]:
    candles, timestamp_to_index = _load_candles(CURATED_CANDLES_PATH)
    diff_path = ACTION_DIFF_ROOT / f"{SUBJECT_YEAR}_enabled_vs_absent_action_diffs.json"
    rows = load_subject_rows(diff_path)

    exact_target_timestamps = _normalized_constant_timestamps(TARGET_IE_TIMESTAMPS)
    exact_comparison_timestamps = _normalized_constant_timestamps(
        COMPARISON_STABLE_DISPLACEMENT_TIMESTAMPS
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

    return {
        "audit_version": "ri-policy-router-insufficient-evidence-local-window-2026-04-29",
        "base_sha": base_sha,
        "status": "insufficient-evidence-local-window-generated",
        "observational_only": True,
        "non_authoritative": True,
        "subject": {
            "symbol": SUBJECT_SYMBOL,
            "timeframe": SUBJECT_TIMEFRAME,
            "negative_year": SUBJECT_YEAR,
        },
        "skill_usage": ["decision_gate_debug", "python_engineering"],
        "cohort_definition": {
            "statement": (
                "Fixed negative-year local window on the curated annual enabled-vs-absent action-diff surface: one exact 2021 low-zone, candidate-LONG, bars-8+ insufficient-evidence blocked cluster compared against nearby stable-continuation displacement rows only."
            )
        },
        "proxy_boundary": {
            "statement": (
                "This slice uses timestamp-close observational proxies only. Reported differences are descriptive, not authoritative, and do not equal realized trade PnL, fill-aware MFE/MAE, one-to-one row pairing, or runtime-authoritative row truth."
            )
        },
        "parse_only_constraint": {
            "statement": (
                "The helper reads existing 2021 action-diff JSON and curated candles only. It does not import from src/**, rerun backtests, regenerate upstream diff artifacts, or modify runtime/default authority surfaces."
            )
        },
        "inputs": {
            "action_diff_root": str(ACTION_DIFF_ROOT_RELATIVE),
            "subject_diff": str(
                ACTION_DIFF_ROOT_RELATIVE / f"{SUBJECT_YEAR}_enabled_vs_absent_action_diffs.json"
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
            "target_cluster_bounds": {
                "start": target_bounds.start.isoformat(),
                "end": target_bounds.end.isoformat(),
            },
            "local_envelope_bounds": {
                "start": local_envelope.start.isoformat(),
                "end": local_envelope.end.isoformat(),
            },
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
    result = run_local_window_analysis(base_sha=args.base_sha)

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
