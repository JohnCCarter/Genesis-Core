from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
ACTION_DIFF_RELATIVE_BY_SUBJECT = {
    "2017-03": Path(
        "results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/"
        "2017_enabled_vs_absent_action_diffs.json"
    ),
    "2023-12": Path(
        "results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/"
        "2023_enabled_vs_absent_action_diffs.json"
    ),
}
TARGET_SUBJECTS = {
    "2017-03": {"year": 2017, "month_number": 3, "month_name": "March"},
    "2023-12": {"year": 2023, "month_number": 12, "month_name": "December"},
}
OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = (
    "ri_policy_router_2023_12_vs_2017_03_continuation_local_window_concentration_2026-05-06.json"
)
PACKET_REFERENCE = Path(
    "docs/decisions/regime_intelligence/policy_router/"
    "ri_policy_router_2023_12_vs_2017_03_continuation_local_window_concentration_precode_packet_2026-05-06.md"
)
ANNUAL_COMPARISON_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_2023_vs_2017_mixed_year_shape_comparison_2026-05-06.md"
)
LOCAL_WINDOW_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_substituted_continuation_local_tail_windows_2026-04-28.md"
)
WORKING_CONTRACT_REFERENCE = Path("GENESIS_WORKING_CONTRACT.md")
MAX_ADJACENCY_GAP = timedelta(hours=24)
STATUS_DIFFERS = "continuation_local_window_shape_differs_between_2023_12_and_2017_03"
STATUS_OVERLAPS = "continuation_local_window_shape_overlaps_between_2023_12_and_2017_03"
STATUS_FAIL_CLOSED = "fail_closed_missing_fixed_continuation_surface"


class ContinuationLocalWindowConcentrationError(RuntimeError):
    pass


class MissingFixedContinuationSurfaceError(ContinuationLocalWindowConcentrationError):
    pass


@dataclass(frozen=True)
class NormalizedContinuationRow:
    timestamp: datetime
    selected_policy: str
    previous_policy: str | None


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Materialize the bounded 2023-12 versus 2017-03 continuation local-window "
            "concentration comparison using a fixed <=24h adjacency rule."
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


def _coerce_dict(value: Any, *, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContinuationLocalWindowConcentrationError(
            f"Expected object for {field_name}, got {value!r}"
        )
    return value


def _coerce_str(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ContinuationLocalWindowConcentrationError(
            f"Expected non-empty string for {field_name}, got {value!r}"
        )
    return value


def _coerce_optional_str(value: Any, *, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise ContinuationLocalWindowConcentrationError(
            f"Expected string-or-null for {field_name}, got {value!r}"
        )
    return value


def _round_or_none(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 6)


def _parse_timestamp(raw: Any) -> datetime:
    timestamp = _coerce_str(raw, field_name="timestamp")
    normalized = timestamp.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ContinuationLocalWindowConcentrationError(f"Invalid timestamp {timestamp!r}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _normalize_row(row: dict[str, Any], *, subject_id: str) -> NormalizedContinuationRow | None:
    expected = TARGET_SUBJECTS[subject_id]
    timestamp = _parse_timestamp(row.get("timestamp"))
    if timestamp.year != expected["year"] or timestamp.month != expected["month_number"]:
        return None

    enabled = _coerce_dict(row.get("enabled"), field_name="row.enabled")
    absent = _coerce_dict(row.get("absent"), field_name="row.absent")
    enabled_action = _coerce_str(enabled.get("action"), field_name="enabled.action")
    absent_action = _coerce_str(absent.get("action"), field_name="absent.action")
    if (absent_action, enabled_action) != ("NONE", "LONG"):
        return None

    router_debug = _coerce_dict(enabled.get("router_debug"), field_name="enabled.router_debug")
    zone = _coerce_str(router_debug.get("zone"), field_name="enabled.router_debug.zone")
    switch_reason = _coerce_str(
        router_debug.get("switch_reason"),
        field_name="enabled.router_debug.switch_reason",
    )
    if zone != "low" or switch_reason != "stable_continuation_state":
        return None

    selected_policy = _coerce_optional_str(
        router_debug.get("selected_policy"),
        field_name="enabled.router_debug.selected_policy",
    )
    previous_policy = _coerce_optional_str(
        router_debug.get("previous_policy"),
        field_name="enabled.router_debug.previous_policy",
    )
    return NormalizedContinuationRow(
        timestamp=timestamp,
        selected_policy=selected_policy or "unknown",
        previous_policy=previous_policy,
    )


def _load_subject_rows(subject_id: str) -> tuple[list[NormalizedContinuationRow], dict[str, Any]]:
    relative_path = ACTION_DIFF_RELATIVE_BY_SUBJECT[subject_id]
    path = ROOT_DIR / relative_path
    try:
        payload = _load_json(path)
    except FileNotFoundError as exc:
        raise MissingFixedContinuationSurfaceError(
            f"Missing fixed continuation surface at {path}"
        ) from exc
    if not isinstance(payload, list):
        raise ContinuationLocalWindowConcentrationError(
            f"Expected list payload in {path}, got {type(payload).__name__}"
        )

    rows: list[NormalizedContinuationRow] = []
    for item in payload:
        row = _coerce_dict(item, field_name="annual_diff_row")
        normalized = _normalize_row(row, subject_id=subject_id)
        if normalized is not None:
            rows.append(normalized)
    rows = sorted(rows, key=lambda row: row.timestamp)
    if not rows:
        raise MissingFixedContinuationSurfaceError(
            f"No fixed continuation rows materialized for subject {subject_id}"
        )

    return rows, {"path": str(relative_path), "row_count": len(payload)}


def _group_adjacent_rows(
    rows: list[NormalizedContinuationRow],
) -> list[list[NormalizedContinuationRow]]:
    if not rows:
        return []
    groups: list[list[NormalizedContinuationRow]] = [[rows[0]]]
    for row in rows[1:]:
        if row.timestamp - groups[-1][-1].timestamp <= MAX_ADJACENCY_GAP:
            groups[-1].append(row)
        else:
            groups.append([row])
    return groups


def _serialize_window(window: list[NormalizedContinuationRow]) -> dict[str, Any]:
    start = window[0].timestamp
    end = window[-1].timestamp
    span_hours = (end - start).total_seconds() / 3600.0
    return {
        "row_count": len(window),
        "start": start.isoformat(),
        "end": end.isoformat(),
        "span_hours": _round_or_none(span_hours),
        "timestamps": [row.timestamp.isoformat() for row in window],
    }


def _subject_summary(subject_id: str, rows: list[NormalizedContinuationRow]) -> dict[str, Any]:
    windows = _group_adjacent_rows(rows)
    chronological_windows = [_serialize_window(window) for window in windows]
    windows_by_size = sorted(
        chronological_windows,
        key=lambda window: (-int(window["row_count"]), str(window["start"])),
    )
    window_sizes_desc = [int(window["row_count"]) for window in windows_by_size]
    total_rows = len(rows)
    top_two_window_rows = sum(window_sizes_desc[:2])
    rows_in_multi_row_windows = sum(
        int(window["row_count"]) for window in chronological_windows if int(window["row_count"]) > 1
    )
    subject = TARGET_SUBJECTS[subject_id]
    return {
        "subject_id": subject_id,
        "year": subject["year"],
        "month_number": subject["month_number"],
        "month_name": subject["month_name"],
        "continuation_row_count": total_rows,
        "window_count": len(chronological_windows),
        "window_size_sequence_desc": window_sizes_desc,
        "largest_window": windows_by_size[0],
        "second_largest_window": windows_by_size[1] if len(windows_by_size) > 1 else None,
        "largest_window_share": _round_or_none(int(windows_by_size[0]["row_count"]) / total_rows),
        "top_two_window_rows": top_two_window_rows,
        "top_two_window_share": _round_or_none(top_two_window_rows / total_rows),
        "multi_row_window_count": sum(
            int(window["row_count"]) > 1 for window in chronological_windows
        ),
        "singleton_window_count": sum(
            int(window["row_count"]) == 1 for window in chronological_windows
        ),
        "rows_in_multi_row_windows": rows_in_multi_row_windows,
        "rows_in_multi_row_windows_share": _round_or_none(rows_in_multi_row_windows / total_rows),
        "rows_with_null_previous_policy": sum(row.previous_policy is None for row in rows),
        "chronological_windows": chronological_windows,
    }


def _cross_subject_comparison(subject_summaries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    march = subject_summaries["2017-03"]
    december = subject_summaries["2023-12"]
    return {
        "same_window_size_sequence_desc": (
            march["window_size_sequence_desc"] == december["window_size_sequence_desc"]
        ),
        "same_window_count": march["window_count"] == december["window_count"],
        "largest_window_row_delta_2023_12_minus_2017_03": int(
            december["largest_window"]["row_count"]
        )
        - int(march["largest_window"]["row_count"]),
        "largest_window_share_delta_2023_12_minus_2017_03": _round_or_none(
            float(december["largest_window_share"]) - float(march["largest_window_share"])
        ),
        "top_two_window_rows_delta_2023_12_minus_2017_03": int(december["top_two_window_rows"])
        - int(march["top_two_window_rows"]),
        "top_two_window_share_delta_2023_12_minus_2017_03": _round_or_none(
            float(december["top_two_window_share"]) - float(march["top_two_window_share"])
        ),
        "largest_windows": {
            "2017-03": march["largest_window"],
            "2023-12": december["largest_window"],
        },
    }


def _status_from_comparison(comparison: dict[str, Any]) -> str:
    if comparison["same_window_size_sequence_desc"] and comparison["same_window_count"]:
        return STATUS_OVERLAPS
    return STATUS_DIFFERS


def _build_fail_closed_result(base_sha: str, reason: str) -> dict[str, Any]:
    return {
        "audit_version": (
            "ri-policy-router-2023-12-vs-2017-03-continuation-local-window-concentration-"
            "2026-05-06"
        ),
        "base_sha": base_sha,
        "status": STATUS_FAIL_CLOSED,
        "observational_only": True,
        "non_authoritative": True,
        "skill_usage": ["python_engineering"],
        "subject": {
            "subject_ids": list(TARGET_SUBJECTS.keys()),
            "packet_reference": str(PACKET_REFERENCE),
            "annual_comparison_reference": str(ANNUAL_COMPARISON_REFERENCE),
            "local_window_reference": str(LOCAL_WINDOW_REFERENCE),
            "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
        },
        "failure_reason": reason,
    }


def run_continuation_local_window_concentration(base_sha: str) -> dict[str, Any]:
    try:
        subject_rows: dict[str, list[NormalizedContinuationRow]] = {}
        inputs: dict[str, Any] = {}
        summaries: dict[str, dict[str, Any]] = {}
        for subject_id in TARGET_SUBJECTS:
            rows, metadata = _load_subject_rows(subject_id)
            subject_rows[subject_id] = rows
            inputs[subject_id] = metadata
            summaries[subject_id] = _subject_summary(subject_id, rows)
    except (MissingFixedContinuationSurfaceError, ContinuationLocalWindowConcentrationError) as exc:
        return _build_fail_closed_result(base_sha=base_sha, reason=str(exc))

    comparison = _cross_subject_comparison(summaries)
    status = _status_from_comparison(comparison)
    return {
        "audit_version": (
            "ri-policy-router-2023-12-vs-2017-03-continuation-local-window-concentration-"
            "2026-05-06"
        ),
        "base_sha": base_sha,
        "status": status,
        "observational_only": True,
        "non_authoritative": True,
        "skill_usage": ["python_engineering"],
        "subject": {
            "subject_ids": list(TARGET_SUBJECTS.keys()),
            "family_definition": {
                "absent_action": "NONE",
                "enabled_action": "LONG",
                "zone": "low",
                "switch_reason": "stable_continuation_state",
            },
            "local_packaging_rule": {
                "max_adjacency_hours": 24,
                "statement": (
                    "Adjacent continuation timestamps separated by <=24h are packaged into the "
                    "same descriptive local window."
                ),
            },
            "packet_reference": str(PACKET_REFERENCE),
            "annual_comparison_reference": str(ANNUAL_COMPARISON_REFERENCE),
            "local_window_reference": str(LOCAL_WINDOW_REFERENCE),
            "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
        },
        "inputs": inputs,
        "subject_summaries": summaries,
        "cross_subject_comparison": comparison,
    }


def main() -> int:
    args = _parse_args()
    output_root = ROOT_DIR / Path(args.output_root_relative)
    output_json = output_root / args.summary_filename
    result = run_continuation_local_window_concentration(base_sha=args.base_sha)

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "summary_artifact": str(output_json),
                "status": result["status"],
                "window_size_sequences": {
                    subject_id: summary["window_size_sequence_desc"]
                    for subject_id, summary in result.get("subject_summaries", {}).items()
                },
                "largest_window_shares": {
                    subject_id: summary["largest_window_share"]
                    for subject_id, summary in result.get("subject_summaries", {}).items()
                },
                "top_two_window_shares": {
                    subject_id: summary["top_two_window_share"]
                    for subject_id, summary in result.get("subject_summaries", {}).items()
                },
                "failure_reason": result.get("failure_reason"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
