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
OUTPUT_FILENAME = "ri_policy_router_insufficient_evidence_discriminator_bundle_displacement_crosscheck_2026-04-30.json"
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
TARGET_CONTRAST_REFERENCE_NOTE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_insufficient_evidence_selective_feature_gate_contrast_2026-04-30.md"
)
NEGATIVE_TARGET_TIMESTAMPS = (
    "2021-03-26T12:00:00+00:00",
    "2021-03-27T06:00:00+00:00",
    "2021-03-27T15:00:00+00:00",
    "2021-03-28T00:00:00+00:00",
)
NEGATIVE_DISPLACEMENT_TIMESTAMPS = (
    "2021-03-26T15:00:00+00:00",
    "2021-03-29T00:00:00+00:00",
)
POSITIVE_TARGET_TIMESTAMPS = (
    "2025-03-14T15:00:00+00:00",
    "2025-03-15T00:00:00+00:00",
    "2025-03-15T09:00:00+00:00",
    "2025-03-15T18:00:00+00:00",
    "2025-03-16T03:00:00+00:00",
)
POSITIVE_DISPLACEMENT_TIMESTAMPS = (
    "2025-03-13T15:00:00+00:00",
    "2025-03-14T00:00:00+00:00",
)
REQUIRED_ROUTER_DEBUG_FIELDS = (
    "switch_reason",
    "zone",
    "selected_policy",
    "raw_target_policy",
    "regime",
    "confidence_level",
    "mandate_level",
    "switch_proposed",
    "switch_blocked",
    "bars_since_regime_change",
    "dwell_duration",
    "action_edge",
    "confidence_gate",
    "clarity_raw",
    "clarity_score",
)
ALLOWED_OBSERVATIONAL_PROXY_FIELDS = (
    "fwd_4_close_return_pct",
    "fwd_8_close_return_pct",
    "fwd_16_close_return_pct",
    "mfe_16_pct",
    "mae_16_pct",
)
SIGNATURE_FIELDS = (
    "switch_reason",
    "absent_action",
    "enabled_action",
    "zone",
    "selected_policy",
    "raw_target_policy",
    "regime",
    "confidence_level",
    "mandate_level",
    "switch_proposed",
    "switch_blocked",
)
NUMERIC_SUMMARY_FIELDS = (
    "bars_since_regime_change",
    "dwell_duration",
    "action_edge",
    "confidence_gate",
    "clarity_raw",
    "clarity_score",
    "confidence_level",
    "mandate_level",
    *ALLOWED_OBSERVATIONAL_PROXY_FIELDS,
)


@dataclass(frozen=True)
class CohortDefinition:
    name: str
    year: str
    exact_timestamps: tuple[str, ...]
    expected_switch_reason: str
    expected_action_pair: tuple[str, str]


COHORT_DEFINITIONS = (
    CohortDefinition(
        name="negative_year_target_2021",
        year=NEGATIVE_YEAR,
        exact_timestamps=NEGATIVE_TARGET_TIMESTAMPS,
        expected_switch_reason="insufficient_evidence",
        expected_action_pair=("LONG", "NONE"),
    ),
    CohortDefinition(
        name="negative_year_displacement_2021",
        year=NEGATIVE_YEAR,
        exact_timestamps=NEGATIVE_DISPLACEMENT_TIMESTAMPS,
        expected_switch_reason="stable_continuation_state",
        expected_action_pair=("NONE", "LONG"),
    ),
    CohortDefinition(
        name="positive_year_target_2025",
        year=POSITIVE_YEAR,
        exact_timestamps=POSITIVE_TARGET_TIMESTAMPS,
        expected_switch_reason="insufficient_evidence",
        expected_action_pair=("LONG", "NONE"),
    ),
    CohortDefinition(
        name="positive_year_displacement_2025",
        year=POSITIVE_YEAR,
        exact_timestamps=POSITIVE_DISPLACEMENT_TIMESTAMPS,
        expected_switch_reason="stable_continuation_state",
        expected_action_pair=("NONE", "LONG"),
    ),
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Crosscheck the candidate insufficient-evidence discriminator bundle against the "
            "already-fixed nearby displacement rows inside the March 2021 and March 2025 windows."
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


def _coerce_int(value: Any, *, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise LocalWindowEvidenceError(f"Expected integer value for {field_name}, got {value!r}")
    return value


def _coerce_bool(value: Any, *, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise LocalWindowEvidenceError(f"Expected bool value for {field_name}, got {value!r}")
    return value


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


def select_exact_rows_by_definition(
    payload: Any,
    *,
    exact_timestamps: tuple[str, ...],
    expected_year: str,
    expected_switch_reason: str,
    expected_action_pair: tuple[str, str],
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
                f"Duplicate exact timestamp recovered for {expected_year}: {normalized_timestamp}"
            )
        absent = item.get("absent")
        enabled = item.get("enabled")
        if not isinstance(absent, dict) or not isinstance(enabled, dict):
            raise LocalWindowEvidenceError(
                "Action-diff row is missing absent/enabled action payloads"
            )
        router_debug = _require_router_debug(item)
        absent_action = str(absent.get("action") or "NONE")
        enabled_action = str(enabled.get("action") or "NONE")
        if (absent_action, enabled_action) != expected_action_pair:
            raise LocalWindowEvidenceError(
                "Fixed cohort row failed action-pair validation: "
                f"{normalized_timestamp} -> {absent_action}->{enabled_action}"
            )
        if str(router_debug["switch_reason"]) != expected_switch_reason:
            raise LocalWindowEvidenceError(
                "Fixed cohort row failed switch-reason validation: "
                f"{normalized_timestamp} -> {router_debug['switch_reason']!r}"
            )
        matched.append(item)
        seen.add(normalized_timestamp)

    if seen != expected_set:
        missing = sorted(expected_set - seen)
        extra = sorted(seen - expected_set)
        raise LocalWindowEvidenceError(
            f"Exact cohort rows did not materialize cleanly for {expected_year}; "
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
    return [{"value": json.loads(value), "count": count} for value, count in ordered]


def _shared_signature(rows: list[dict[str, Any]]) -> dict[str, Any]:
    signature: dict[str, Any] = {}
    for field_name in SIGNATURE_FIELDS:
        values = {json.dumps(row[field_name], sort_keys=True) for row in rows}
        if len(values) == 1:
            signature[field_name] = json.loads(next(iter(values)))
    return signature


def _serialize_cohort_row(
    row: dict[str, Any],
    *,
    cohort_name: str,
    year: str,
    candles: Any,
    timestamp_to_index: dict[Any, int],
) -> dict[str, Any]:
    timestamp = _normalize_timestamp(str(row["timestamp"]))
    absent = row.get("absent")
    enabled = row.get("enabled")
    if not isinstance(absent, dict) or not isinstance(enabled, dict):
        raise LocalWindowEvidenceError("Action-diff row is missing absent/enabled dictionaries")
    router_debug = _require_router_debug(row)
    absent_action = str(absent.get("action") or "NONE")
    enabled_action = str(enabled.get("action") or "NONE")

    serialized = {
        "cohort_name": cohort_name,
        "year": year,
        "timestamp": timestamp.isoformat(),
        "absent_action": absent_action,
        "enabled_action": enabled_action,
        "action_pair": f"{absent_action}->{enabled_action}",
        "switch_reason": str(router_debug["switch_reason"]),
        "zone": str(router_debug["zone"]),
        "selected_policy": str(router_debug["selected_policy"]),
        "raw_target_policy": str(router_debug["raw_target_policy"]),
        "regime": str(router_debug["regime"]),
        "confidence_level": round(
            _coerce_float(router_debug["confidence_level"], field_name="confidence_level"),
            6,
        ),
        "mandate_level": round(
            _coerce_float(router_debug["mandate_level"], field_name="mandate_level"),
            6,
        ),
        "switch_proposed": _coerce_bool(
            router_debug["switch_proposed"], field_name="switch_proposed"
        ),
        "switch_blocked": _coerce_bool(router_debug["switch_blocked"], field_name="switch_blocked"),
        "bars_since_regime_change": _coerce_int(
            router_debug["bars_since_regime_change"], field_name="bars_since_regime_change"
        ),
        "dwell_duration": round(
            _coerce_float(router_debug["dwell_duration"], field_name="dwell_duration"),
            6,
        ),
        "action_edge": round(
            _coerce_float(router_debug["action_edge"], field_name="action_edge"),
            6,
        ),
        "confidence_gate": round(
            _coerce_float(router_debug["confidence_gate"], field_name="confidence_gate"),
            6,
        ),
        "clarity_raw": round(
            _coerce_float(router_debug["clarity_raw"], field_name="clarity_raw"),
            6,
        ),
        "clarity_score": round(
            _coerce_float(router_debug["clarity_score"], field_name="clarity_score"),
            6,
        ),
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
        "action_pair_counts": _value_counts(rows, "action_pair"),
        "switch_reason_counts": _value_counts(rows, "switch_reason"),
        "selected_policy_counts": _value_counts(rows, "selected_policy"),
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


def classify_gap_direction(left_mean_gap: float | None, right_mean_gap: float | None) -> str:
    if left_mean_gap is None or right_mean_gap is None:
        return "missing"
    if left_mean_gap == 0 and right_mean_gap == 0:
        return "both_zero"
    if left_mean_gap > 0 and right_mean_gap > 0:
        return "same_positive"
    if left_mean_gap < 0 and right_mean_gap < 0:
        return "same_negative"
    return "opposite_or_mixed"


def _target_minus_displacement_gap(
    target_summary: dict[str, Any],
    displacement_summary: dict[str, Any],
    field_name: str,
) -> dict[str, float | None]:
    target_metric = target_summary["metric_summary"][field_name]
    displacement_metric = displacement_summary["metric_summary"][field_name]
    target_mean = target_metric["mean"]
    displacement_mean = displacement_metric["mean"]
    target_median = target_metric["median"]
    displacement_median = displacement_metric["median"]
    return {
        "mean_gap_target_minus_displacement": (
            None
            if target_mean is None or displacement_mean is None
            else round(float(target_mean) - float(displacement_mean), 6)
        ),
        "median_gap_target_minus_displacement": (
            None
            if target_median is None or displacement_median is None
            else round(float(target_median) - float(displacement_median), 6)
        ),
    }


def _rank_gap_metrics(metric_gaps: dict[str, dict[str, float | None]]) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []
    for metric, gap in metric_gaps.items():
        mean_gap = gap["mean_gap_target_minus_displacement"]
        if mean_gap is None:
            continue
        ranked.append(
            {
                "metric": metric,
                **gap,
                "absolute_mean_gap": round(abs(float(mean_gap)), 6),
            }
        )
    return sorted(ranked, key=lambda item: (-float(item["absolute_mean_gap"]), item["metric"]))


def _build_year_contrast(
    target_summary: dict[str, Any],
    displacement_summary: dict[str, Any],
    *,
    year: str,
) -> dict[str, Any]:
    metric_gaps = {
        field_name: _target_minus_displacement_gap(
            target_summary,
            displacement_summary,
            field_name,
        )
        for field_name in NUMERIC_SUMMARY_FIELDS
    }
    return {
        "year": year,
        "target_row_count": target_summary["row_count"],
        "displacement_row_count": displacement_summary["row_count"],
        "metric_gaps_target_minus_displacement": metric_gaps,
        "largest_mean_gaps": _rank_gap_metrics(metric_gaps),
    }


def _cross_year_recurrence(
    negative_year_contrast: dict[str, Any],
    positive_year_contrast: dict[str, Any],
) -> dict[str, Any]:
    recurrence: dict[str, Any] = {}
    for field_name in NUMERIC_SUMMARY_FIELDS:
        negative_gap = negative_year_contrast["metric_gaps_target_minus_displacement"][field_name][
            "mean_gap_target_minus_displacement"
        ]
        positive_gap = positive_year_contrast["metric_gaps_target_minus_displacement"][field_name][
            "mean_gap_target_minus_displacement"
        ]
        recurrence[field_name] = {
            "mean_gap_2021_target_minus_displacement": negative_gap,
            "mean_gap_2025_target_minus_displacement": positive_gap,
            "gap_direction_class": classify_gap_direction(negative_gap, positive_gap),
            "gap_of_gaps_2021_minus_2025": (
                None
                if negative_gap is None or positive_gap is None
                else round(float(negative_gap) - float(positive_gap), 6)
            ),
        }
    return recurrence


def run_displacement_crosscheck(base_sha: str) -> dict[str, Any]:
    candles, timestamp_to_index = _load_candles(CURATED_CANDLES_PATH)
    payloads = {
        NEGATIVE_YEAR: _load_json(
            ACTION_DIFF_ROOT / f"{NEGATIVE_YEAR}_enabled_vs_absent_action_diffs.json"
        ),
        POSITIVE_YEAR: _load_json(
            ACTION_DIFF_ROOT / f"{POSITIVE_YEAR}_enabled_vs_absent_action_diffs.json"
        ),
    }

    serialized_by_cohort: dict[str, list[dict[str, Any]]] = {}
    summaries_by_cohort: dict[str, dict[str, Any]] = {}
    artifact_row_lock: dict[str, Any] = {}
    for definition in COHORT_DEFINITIONS:
        exact_timestamps = _normalized_constant_timestamps(definition.exact_timestamps)
        rows = select_exact_rows_by_definition(
            payloads[definition.year],
            exact_timestamps=exact_timestamps,
            expected_year=definition.year,
            expected_switch_reason=definition.expected_switch_reason,
            expected_action_pair=definition.expected_action_pair,
        )
        serialized = [
            _serialize_cohort_row(
                row,
                cohort_name=definition.name,
                year=definition.year,
                candles=candles,
                timestamp_to_index=timestamp_to_index,
            )
            for row in rows
        ]
        serialized_by_cohort[definition.name] = serialized
        summaries_by_cohort[definition.name] = _cohort_summary(serialized)
        artifact_row_lock[definition.name] = {
            "year": definition.year,
            "expected_switch_reason": definition.expected_switch_reason,
            "expected_action_pair": list(definition.expected_action_pair),
            "timestamps": list(exact_timestamps),
            "row_count": len(exact_timestamps),
        }

    negative_year_contrast = _build_year_contrast(
        summaries_by_cohort["negative_year_target_2021"],
        summaries_by_cohort["negative_year_displacement_2021"],
        year=NEGATIVE_YEAR,
    )
    positive_year_contrast = _build_year_contrast(
        summaries_by_cohort["positive_year_target_2025"],
        summaries_by_cohort["positive_year_displacement_2025"],
        year=POSITIVE_YEAR,
    )

    return {
        "audit_version": "ri-policy-router-insufficient-evidence-discriminator-bundle-displacement-crosscheck-2026-04-30",
        "base_sha": base_sha,
        "status": "insufficient-evidence-discriminator-bundle-displacement-crosscheck-generated",
        "observational_only": True,
        "non_authoritative": True,
        "subject": {
            "symbol": SUBJECT_SYMBOL,
            "timeframe": SUBJECT_TIMEFRAME,
            "negative_year": NEGATIVE_YEAR,
            "positive_year": POSITIVE_YEAR,
            "negative_reference": str(NEGATIVE_REFERENCE_NOTE),
            "positive_reference": str(POSITIVE_REFERENCE_NOTE),
            "target_contrast_reference": str(TARGET_CONTRAST_REFERENCE_NOTE),
        },
        "skill_usage": ["decision_gate_debug", "python_engineering"],
        "comparison_contract": {
            "statement": (
                "This slice is a fixed-surface observational crosscheck. It compares only the "
                "already-frozen 2021 target rows, 2021 nearby displacement rows, 2025 target "
                "rows, and 2025 nearby displacement rows from the existing enabled-vs-absent "
                "action-diff JSONs."
            ),
            "allowed_top_level_fields": ["timestamp", "absent_action", "enabled_action"],
            "allowed_router_debug_fields": list(REQUIRED_ROUTER_DEBUG_FIELDS),
            "allowed_observational_proxy_fields": list(ALLOWED_OBSERVATIONAL_PROXY_FIELDS),
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
        "artifact_row_lock": artifact_row_lock,
        "cohorts": {
            cohort_name: {
                **summaries_by_cohort[cohort_name],
                "rows": serialized_by_cohort[cohort_name],
            }
            for cohort_name in (
                "negative_year_target_2021",
                "negative_year_displacement_2021",
                "positive_year_target_2025",
                "positive_year_displacement_2025",
            )
        },
        "within_year_contrasts": {
            "negative_year_2021": negative_year_contrast,
            "positive_year_2025": positive_year_contrast,
        },
        "cross_year_recurrence": {
            "metric_recurrence": _cross_year_recurrence(
                negative_year_contrast,
                positive_year_contrast,
            )
        },
    }


def main() -> int:
    args = _parse_args()
    output_root = ROOT_DIR / Path(args.output_root_relative)
    output_json = output_root / args.summary_filename
    result = run_displacement_crosscheck(base_sha=args.base_sha)

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "summary_artifact": str(output_json),
                "negative_target_row_count": result["cohorts"]["negative_year_target_2021"][
                    "row_count"
                ],
                "negative_displacement_row_count": result["cohorts"][
                    "negative_year_displacement_2021"
                ]["row_count"],
                "positive_target_row_count": result["cohorts"]["positive_year_target_2025"][
                    "row_count"
                ],
                "positive_displacement_row_count": result["cohorts"][
                    "positive_year_displacement_2025"
                ]["row_count"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
