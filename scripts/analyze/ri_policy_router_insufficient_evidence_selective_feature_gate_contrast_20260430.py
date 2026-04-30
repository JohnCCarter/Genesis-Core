from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from statistics import fmean, median
from typing import Any


LOCAL_ROOT_DIR = Path(__file__).resolve().parents[2]
if str(LOCAL_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(LOCAL_ROOT_DIR))

from scripts.analyze.ri_policy_router_insufficient_evidence_local_window_20260429 import (
    ACTION_DIFF_ROOT,
    ACTION_DIFF_ROOT_RELATIVE,
    CURATED_CANDLES_PATH,
    CURATED_CANDLES_RELATIVE,
    ROOT_DIR,
    LocalWindowEvidenceError,
    _load_candles,
    _load_json,
    _normalize_timestamp,
    _row_observational_metrics,
)

OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = (
    "ri_policy_router_insufficient_evidence_selective_feature_gate_contrast_2026-04-30.json"
)
SUBJECT_SYMBOL = "tBTCUSD"
SUBJECT_TIMEFRAME = "3h"
NEGATIVE_YEAR = "2021"
POSITIVE_YEAR = "2025"
NEGATIVE_REFERENCE_NOTE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_insufficient_evidence_local_window_2026-04-29.md"
)
POSITIVE_REFERENCE_NOTE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_positive_year_insufficient_evidence_control_2026-04-29.md"
)
NEGATIVE_TARGET_TIMESTAMPS = (
    "2021-03-26T12:00:00+00:00",
    "2021-03-27T06:00:00+00:00",
    "2021-03-27T15:00:00+00:00",
    "2021-03-28T00:00:00+00:00",
)
POSITIVE_TARGET_TIMESTAMPS = (
    "2025-03-14T15:00:00+00:00",
    "2025-03-15T00:00:00+00:00",
    "2025-03-15T09:00:00+00:00",
    "2025-03-15T18:00:00+00:00",
    "2025-03-16T03:00:00+00:00",
)
REQUIRED_ROUTER_DEBUG_FIELDS = (
    "switch_reason",
    "selected_policy",
    "raw_target_policy",
    "previous_policy",
    "zone",
    "candidate",
    "bars_since_regime_change",
    "action_edge",
    "confidence_gate",
    "clarity_raw",
    "clarity_score",
    "confidence_level",
    "mandate_level",
    "dwell_duration",
    "regime",
    "switch_proposed",
    "switch_blocked",
    "size_multiplier",
)
SHARED_SIGNATURE_FIELDS = (
    "switch_reason",
    "selected_policy",
    "raw_target_policy",
    "previous_policy",
    "zone",
    "candidate",
    "absent_action",
    "enabled_action",
    "regime",
    "confidence_level",
    "mandate_level",
    "switch_proposed",
    "switch_blocked",
    "size_multiplier",
)
NUMERIC_SUMMARY_FIELDS = (
    "bars_since_regime_change",
    "action_edge",
    "confidence_gate",
    "clarity_raw",
    "clarity_score",
    "confidence_level",
    "mandate_level",
    "dwell_duration",
    "size_multiplier",
    "fwd_4_close_return_pct",
    "fwd_8_close_return_pct",
    "fwd_16_close_return_pct",
    "mfe_16_pct",
    "mae_16_pct",
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compare the fixed March 2021 and March 2025 insufficient-evidence target clusters "
            "on the smallest available feature/gate surface using existing action-diff rows only."
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


def _normalized_constant_timestamps(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(_normalize_timestamp(value).isoformat() for value in values)


def _coerce_float(value: Any, *, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise LocalWindowEvidenceError(f"Expected numeric value for {field_name}, got {value!r}")
    out = float(value)
    if out != out or out in {float("inf"), float("-inf")}:
        raise LocalWindowEvidenceError(f"Expected finite value for {field_name}, got {value!r}")
    return out


def _require_router_debug(row: dict[str, Any]) -> dict[str, Any]:
    enabled = row.get("enabled")
    if not isinstance(enabled, dict):
        raise LocalWindowEvidenceError("Action-diff row is missing enabled payload")
    router_debug = enabled.get("router_debug")
    if not isinstance(router_debug, dict):
        raise LocalWindowEvidenceError("Action-diff row is missing enabled.router_debug payload")
    missing = [field for field in REQUIRED_ROUTER_DEBUG_FIELDS if field not in router_debug]
    if missing:
        raise LocalWindowEvidenceError(
            f"Action-diff row is missing required router_debug fields: {missing}"
        )
    return router_debug


def select_exact_target_rows(
    payload: Any,
    *,
    exact_timestamps: tuple[str, ...],
    expected_year: str,
) -> list[dict[str, Any]]:
    if not isinstance(payload, list):
        raise LocalWindowEvidenceError("Expected row list payload in action-diff JSON")

    expected_set = set(exact_timestamps)
    matched: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in payload:
        if not isinstance(item, dict):
            raise LocalWindowEvidenceError("Expected object rows in action-diff JSON")
        timestamp = item.get("timestamp")
        if not isinstance(timestamp, str):
            raise LocalWindowEvidenceError("Action-diff row is missing a string timestamp")
        normalized_timestamp = _normalize_timestamp(timestamp).isoformat()
        if normalized_timestamp not in expected_set:
            continue
        if normalized_timestamp in seen:
            raise LocalWindowEvidenceError(
                f"Duplicate target timestamp recovered for {expected_year}: {normalized_timestamp}"
            )
        router_debug = _require_router_debug(item)
        absent = item.get("absent")
        enabled = item.get("enabled")
        if not isinstance(absent, dict) or not isinstance(enabled, dict):
            raise LocalWindowEvidenceError(
                "Action-diff row is missing absent/enabled action payloads"
            )
        absent_action = str(absent.get("action") or "NONE")
        enabled_action = str(enabled.get("action") or "NONE")
        if absent_action != "LONG" or enabled_action != "NONE":
            raise LocalWindowEvidenceError(
                "Fixed target row failed action-pair validation: "
                f"{normalized_timestamp} -> {absent_action}->{enabled_action}"
            )
        if str(router_debug.get("switch_reason")) != "insufficient_evidence":
            raise LocalWindowEvidenceError(
                "Fixed target row failed switch-reason validation: "
                f"{normalized_timestamp} -> {router_debug.get('switch_reason')!r}"
            )
        matched.append(item)
        seen.add(normalized_timestamp)

    if seen != expected_set:
        missing = sorted(expected_set - seen)
        extra = sorted(seen - expected_set)
        raise LocalWindowEvidenceError(
            f"Exact target rows did not materialize cleanly for {expected_year}; "
            f"missing={missing}, extra={extra}"
        )

    return sorted(matched, key=lambda row: _normalize_timestamp(str(row["timestamp"])))


def summarize_numeric_metric(values: list[float]) -> dict[str, float | int | None]:
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
        "min": round(min(values), 6),
        "max": round(max(values), 6),
        "mean": round(fmean(values), 6),
        "median": round(median(values), 6),
        "gt_zero_share": round(positive_share, 6),
    }


def _value_counts(rows: list[dict[str, Any]], field_name: str) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    for row in rows:
        value = json.dumps(row[field_name], sort_keys=True)
        counts[value] = counts.get(value, 0) + 1
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [{"value": json.loads(serialized), "count": count} for serialized, count in ordered]


def _shared_signature(rows: list[dict[str, Any]]) -> dict[str, Any]:
    signature: dict[str, Any] = {}
    for field_name in SHARED_SIGNATURE_FIELDS:
        values = {json.dumps(row[field_name], sort_keys=True) for row in rows}
        if len(values) == 1:
            signature[field_name] = json.loads(next(iter(values)))
    return signature


def _serialize_target_row(
    row: dict[str, Any],
    *,
    year: str,
    candles: Any,
    timestamp_to_index: dict[Any, int],
) -> dict[str, Any]:
    timestamp = _normalize_timestamp(str(row["timestamp"]))
    absent = row.get("absent") or {}
    enabled = row.get("enabled") or {}
    if not isinstance(absent, dict) or not isinstance(enabled, dict):
        raise LocalWindowEvidenceError("Action-diff row is missing absent/enabled dictionaries")
    router_debug = _require_router_debug(row)
    reasons = enabled.get("reasons")
    if reasons is None:
        enabled_reasons: list[str] = []
    elif isinstance(reasons, list) and all(isinstance(item, str) for item in reasons):
        enabled_reasons = list(reasons)
    else:
        raise LocalWindowEvidenceError(f"Expected string reasons list, got {reasons!r}")

    serialized = {
        "year": year,
        "timestamp": timestamp.isoformat(),
        "absent_action": str(absent.get("action") or "NONE"),
        "enabled_action": str(enabled.get("action") or "NONE"),
        "enabled_reasons": enabled_reasons,
        "switch_reason": str(router_debug["switch_reason"]),
        "selected_policy": str(router_debug["selected_policy"]),
        "raw_target_policy": str(router_debug["raw_target_policy"]),
        "previous_policy": str(router_debug["previous_policy"]),
        "zone": str(router_debug["zone"]),
        "candidate": str(router_debug["candidate"]),
        "bars_since_regime_change": int(router_debug["bars_since_regime_change"]),
        "action_edge": round(
            _coerce_float(router_debug["action_edge"], field_name="action_edge"), 6
        ),
        "confidence_gate": round(
            _coerce_float(router_debug["confidence_gate"], field_name="confidence_gate"), 6
        ),
        "clarity_raw": round(
            _coerce_float(router_debug["clarity_raw"], field_name="clarity_raw"), 6
        ),
        "clarity_score": round(
            _coerce_float(router_debug["clarity_score"], field_name="clarity_score"), 6
        ),
        "confidence_level": round(
            _coerce_float(router_debug["confidence_level"], field_name="confidence_level"), 6
        ),
        "mandate_level": round(
            _coerce_float(router_debug["mandate_level"], field_name="mandate_level"), 6
        ),
        "dwell_duration": round(
            _coerce_float(router_debug["dwell_duration"], field_name="dwell_duration"), 6
        ),
        "regime": str(router_debug["regime"]),
        "switch_proposed": bool(router_debug["switch_proposed"]),
        "switch_blocked": bool(router_debug["switch_blocked"]),
        "size_multiplier": round(
            _coerce_float(router_debug["size_multiplier"], field_name="size_multiplier"), 6
        ),
        "router_params": router_debug.get("router_params"),
    }
    serialized.update(
        _row_observational_metrics(
            timestamp=timestamp,
            candles=candles,
            timestamp_to_index=timestamp_to_index,
        )
    )
    return serialized


def _cohort_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "row_count": len(rows),
        "timestamps": [row["timestamp"] for row in rows],
        "shared_signature": _shared_signature(rows),
        "enabled_reasons_counts": _value_counts(rows, "enabled_reasons"),
        "metric_summary": {
            field_name: summarize_numeric_metric(
                [
                    float(row[field_name])
                    for row in rows
                    if isinstance(row.get(field_name), int | float)
                ]
            )
            for field_name in NUMERIC_SUMMARY_FIELDS
        },
    }


def _mean_gap(
    left_summary: dict[str, Any],
    right_summary: dict[str, Any],
    field_name: str,
) -> dict[str, float | None]:
    left_metric = left_summary["metric_summary"][field_name]
    right_metric = right_summary["metric_summary"][field_name]
    left_mean = left_metric["mean"]
    right_mean = right_metric["mean"]
    left_median = left_metric["median"]
    right_median = right_metric["median"]
    return {
        "mean_gap_2021_minus_2025": (
            None
            if left_mean is None or right_mean is None
            else round(float(left_mean) - float(right_mean), 6)
        ),
        "median_gap_2021_minus_2025": (
            None
            if left_median is None or right_median is None
            else round(float(left_median) - float(right_median), 6)
        ),
    }


def _rank_mean_gaps(
    negative_summary: dict[str, Any],
    positive_summary: dict[str, Any],
) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []
    for field_name in NUMERIC_SUMMARY_FIELDS:
        gap = _mean_gap(negative_summary, positive_summary, field_name)
        mean_gap = gap["mean_gap_2021_minus_2025"]
        if mean_gap is None:
            continue
        ranked.append(
            {
                "metric": field_name,
                **gap,
                "absolute_mean_gap": round(abs(float(mean_gap)), 6),
            }
        )
    return sorted(ranked, key=lambda item: (-float(item["absolute_mean_gap"]), item["metric"]))


def run_selective_feature_gate_contrast(base_sha: str) -> dict[str, Any]:
    candles, timestamp_to_index = _load_candles(CURATED_CANDLES_PATH)
    negative_payload = _load_json(
        ACTION_DIFF_ROOT / f"{NEGATIVE_YEAR}_enabled_vs_absent_action_diffs.json"
    )
    positive_payload = _load_json(
        ACTION_DIFF_ROOT / f"{POSITIVE_YEAR}_enabled_vs_absent_action_diffs.json"
    )

    negative_timestamps = _normalized_constant_timestamps(NEGATIVE_TARGET_TIMESTAMPS)
    positive_timestamps = _normalized_constant_timestamps(POSITIVE_TARGET_TIMESTAMPS)

    negative_rows = select_exact_target_rows(
        negative_payload,
        exact_timestamps=negative_timestamps,
        expected_year=NEGATIVE_YEAR,
    )
    positive_rows = select_exact_target_rows(
        positive_payload,
        exact_timestamps=positive_timestamps,
        expected_year=POSITIVE_YEAR,
    )

    negative_serialized = [
        _serialize_target_row(
            row,
            year=NEGATIVE_YEAR,
            candles=candles,
            timestamp_to_index=timestamp_to_index,
        )
        for row in negative_rows
    ]
    positive_serialized = [
        _serialize_target_row(
            row,
            year=POSITIVE_YEAR,
            candles=candles,
            timestamp_to_index=timestamp_to_index,
        )
        for row in positive_rows
    ]

    negative_summary = _cohort_summary(negative_serialized)
    positive_summary = _cohort_summary(positive_serialized)

    metric_gaps = {
        field_name: _mean_gap(negative_summary, positive_summary, field_name)
        for field_name in NUMERIC_SUMMARY_FIELDS
    }

    return {
        "audit_version": "ri-policy-router-insufficient-evidence-selective-feature-gate-contrast-2026-04-30",
        "base_sha": base_sha,
        "status": "insufficient-evidence-selective-feature-gate-contrast-generated",
        "observational_only": True,
        "non_authoritative": True,
        "subject": {
            "symbol": SUBJECT_SYMBOL,
            "timeframe": SUBJECT_TIMEFRAME,
            "negative_year": NEGATIVE_YEAR,
            "positive_year": POSITIVE_YEAR,
            "negative_reference": str(NEGATIVE_REFERENCE_NOTE),
            "positive_reference": str(POSITIVE_REFERENCE_NOTE),
        },
        "skill_usage": ["decision_gate_debug", "python_engineering"],
        "comparison_contract": {
            "statement": (
                "This slice is fail-closed to the exact fixed March 2021 and March 2025 "
                "insufficient_evidence target timestamps only. It uses existing action-diff "
                "rows plus the same candle observational proxies already used in the prior "
                "local-window notes."
            ),
            "allowed_router_debug_fields": list(REQUIRED_ROUTER_DEBUG_FIELDS),
            "allowed_observational_proxy_fields": [
                "fwd_4_close_return_pct",
                "fwd_8_close_return_pct",
                "fwd_16_close_return_pct",
                "mfe_16_pct",
                "mae_16_pct",
            ],
        },
        "inputs": {
            "action_diff_root": str(ACTION_DIFF_ROOT_RELATIVE),
            "negative_year_diff": str(
                ACTION_DIFF_ROOT_RELATIVE / f"{NEGATIVE_YEAR}_enabled_vs_absent_action_diffs.json"
            ),
            "positive_year_diff": str(
                ACTION_DIFF_ROOT_RELATIVE / f"{POSITIVE_YEAR}_enabled_vs_absent_action_diffs.json"
            ),
            "curated_candles": str(CURATED_CANDLES_RELATIVE),
        },
        "artifact_row_lock": {
            "negative_target_timestamps": list(negative_timestamps),
            "positive_target_timestamps": list(positive_timestamps),
            "negative_target_count": len(negative_timestamps),
            "positive_target_count": len(positive_timestamps),
        },
        "cohorts": {
            "negative_year_target_2021": {
                **negative_summary,
                "rows": negative_serialized,
            },
            "positive_year_target_2025": {
                **positive_summary,
                "rows": positive_serialized,
            },
        },
        "contrast": {
            "metric_gaps_2021_minus_2025": metric_gaps,
            "largest_mean_gaps": _rank_mean_gaps(negative_summary, positive_summary),
        },
    }


def main() -> int:
    args = _parse_args()
    output_root = ROOT_DIR / Path(args.output_root_relative)
    output_json = output_root / args.summary_filename
    result = run_selective_feature_gate_contrast(base_sha=args.base_sha)

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "summary_artifact": str(output_json),
                "negative_target_row_count": result["cohorts"]["negative_year_target_2021"][
                    "row_count"
                ],
                "positive_target_row_count": result["cohorts"]["positive_year_target_2025"][
                    "row_count"
                ],
                "largest_mean_gap_metric": result["contrast"]["largest_mean_gaps"][0]["metric"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
