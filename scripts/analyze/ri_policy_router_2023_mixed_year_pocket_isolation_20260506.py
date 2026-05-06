from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
ANNUAL_SUMMARY_RELATIVE = Path(
    "results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/"
    "enabled_vs_absent_all_years_summary.json"
)
ANNUAL_2023_DIFF_RELATIVE = Path(
    "results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/"
    "2023_enabled_vs_absent_action_diffs.json"
)
OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = "ri_policy_router_2023_mixed_year_pocket_isolation_2026-05-06.json"
PACKET_REFERENCE = Path(
    "docs/decisions/regime_intelligence/policy_router/"
    "ri_policy_router_2023_mixed_year_pocket_isolation_precode_packet_2026-05-06.md"
)
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
BOUNDED_CONTRIBUTION_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_enabled_vs_absent_bounded_contribution_evidence_2026-04-28.md"
)
DECEMBER_RESIDUAL_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_weak_pre_aged_single_veto_release_residual_blocked_longs_diagnosis_2026-04-27.md"
)
WORKING_CONTRACT_REFERENCE = Path("GENESIS_WORKING_CONTRACT.md")
FIXED_YEAR = "2023"
DECEMBER_MONTH = "2023-12"
SUPPRESSION_SWITCH_REASONS = {
    "insufficient_evidence",
    "AGED_WEAK_CONTINUATION_GUARD",
}
CONTINUATION_SWITCH_REASON = "stable_continuation_state"
DECEMBER_ANCHOR_TIMESTAMPS = (
    "2023-12-20T03:00:00+00:00",
    "2023-12-21T18:00:00+00:00",
    "2023-12-22T09:00:00+00:00",
    "2023-12-28T09:00:00+00:00",
    "2023-12-30T21:00:00+00:00",
)


class MixedYearPocketIsolationError(RuntimeError):
    pass


class Missing2023AnnualSurfaceError(MixedYearPocketIsolationError):
    pass


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Materialize the bounded 2023 mixed-year pocket isolation summary by ranking the "
            "fixed shared-shape family across annual 2023 action-diff months."
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


def _coerce_str(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise MixedYearPocketIsolationError(
            f"Expected non-empty string for {field_name}, got {value!r}"
        )
    return value


def _coerce_dict(value: Any, *, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise MixedYearPocketIsolationError(f"Expected object for {field_name}, got {value!r}")
    return value


def _round_or_none(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 6)


def _normalize_timestamp(raw: Any) -> str:
    timestamp = _coerce_str(raw, field_name="timestamp")
    normalized = timestamp.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise MixedYearPocketIsolationError(f"Invalid timestamp {timestamp!r}") from exc
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC).isoformat()


def _load_annual_summary() -> tuple[dict[str, Any], dict[str, Any]]:
    path = ROOT_DIR / ANNUAL_SUMMARY_RELATIVE
    try:
        payload = _load_json(path)
    except FileNotFoundError as exc:
        raise Missing2023AnnualSurfaceError(f"Missing annual summary surface at {path}") from exc
    summary = _coerce_dict(payload, field_name="annual_summary")
    years = _coerce_dict(summary.get("years"), field_name="annual_summary.years")
    if FIXED_YEAR not in years:
        raise Missing2023AnnualSurfaceError(f"Year {FIXED_YEAR} is missing from annual summary")
    year_payload = _coerce_dict(years[FIXED_YEAR], field_name=f"annual_summary.years.{FIXED_YEAR}")
    window = _coerce_dict(year_payload.get("window"), field_name=f"{FIXED_YEAR}.window")
    if bool(window.get("partial_year")):
        raise Missing2023AnnualSurfaceError(f"Year {FIXED_YEAR} is partial and not admissible")
    comparison = _coerce_dict(
        year_payload.get("comparison"), field_name=f"annual_summary.years.{FIXED_YEAR}.comparison"
    )
    return summary, {
        "path": str(ANNUAL_SUMMARY_RELATIVE),
        "window": {
            "start": window.get("start"),
            "end": window.get("end"),
            "partial_year": bool(window.get("partial_year")),
        },
        "comparison": {
            "enabled_total_return_pct": comparison.get("enabled_total_return_pct"),
            "absent_total_return_pct": comparison.get("absent_total_return_pct"),
            "enabled_profit_factor": comparison.get("enabled_profit_factor"),
            "absent_profit_factor": comparison.get("absent_profit_factor"),
            "enabled_max_drawdown_pct": comparison.get("enabled_max_drawdown_pct"),
            "absent_max_drawdown_pct": comparison.get("absent_max_drawdown_pct"),
            "enabled_position_net_pnl": comparison.get("enabled_position_net_pnl"),
            "absent_position_net_pnl": comparison.get("absent_position_net_pnl"),
            "action_diff_count": comparison.get("action_diff_count"),
            "reason_only_diff_count": comparison.get("reason_only_diff_count"),
        },
    }


def _family_from_row(row: dict[str, Any]) -> str | None:
    enabled = _coerce_dict(row.get("enabled"), field_name="row.enabled")
    absent = _coerce_dict(row.get("absent"), field_name="row.absent")
    enabled_action = _coerce_str(enabled.get("action"), field_name="enabled.action")
    absent_action = _coerce_str(absent.get("action"), field_name="absent.action")

    action_pair = (absent_action, enabled_action)
    if action_pair not in {("LONG", "NONE"), ("NONE", "LONG")}:
        return None

    router_debug = _coerce_dict(enabled.get("router_debug"), field_name="enabled.router_debug")
    zone = _coerce_str(router_debug.get("zone"), field_name="enabled.router_debug.zone")
    switch_reason = _coerce_str(
        router_debug.get("switch_reason"), field_name="enabled.router_debug.switch_reason"
    )

    if zone != "low":
        return None
    if action_pair == ("LONG", "NONE") and switch_reason in SUPPRESSION_SWITCH_REASONS:
        return "suppression"
    if action_pair == ("NONE", "LONG") and switch_reason == CONTINUATION_SWITCH_REASON:
        return "continuation_displacement"
    return None


def _normalize_family_row(row: dict[str, Any], *, family_name: str) -> dict[str, Any]:
    enabled = _coerce_dict(row.get("enabled"), field_name="row.enabled")
    absent = _coerce_dict(row.get("absent"), field_name="row.absent")
    router_debug = _coerce_dict(enabled.get("router_debug"), field_name="enabled.router_debug")
    timestamp = _normalize_timestamp(row.get("timestamp"))
    return {
        "timestamp": timestamp,
        "month": timestamp[:7],
        "family_name": family_name,
        "absent_action": _coerce_str(absent.get("action"), field_name="absent.action"),
        "enabled_action": _coerce_str(enabled.get("action"), field_name="enabled.action"),
        "switch_reason": _coerce_str(
            router_debug.get("switch_reason"), field_name="enabled.router_debug.switch_reason"
        ),
        "selected_policy": _coerce_str(
            router_debug.get("selected_policy"), field_name="enabled.router_debug.selected_policy"
        ),
        "previous_policy": _coerce_str(
            router_debug.get("previous_policy"), field_name="enabled.router_debug.previous_policy"
        ),
        "zone": _coerce_str(router_debug.get("zone"), field_name="enabled.router_debug.zone"),
        "candidate": _coerce_str(
            router_debug.get("candidate"), field_name="enabled.router_debug.candidate"
        ),
        "bars_since_regime_change": router_debug.get("bars_since_regime_change"),
    }


def _normalize_anchor_row(row: dict[str, Any], *, family_name: str | None) -> dict[str, Any]:
    enabled = _coerce_dict(row.get("enabled"), field_name="row.enabled")
    absent = _coerce_dict(row.get("absent"), field_name="row.absent")
    router_debug = enabled.get("router_debug")
    if router_debug is None:
        return {
            "timestamp": _normalize_timestamp(row.get("timestamp")),
            "family_name": family_name,
            "absent_action": _coerce_str(absent.get("action"), field_name="absent.action"),
            "enabled_action": _coerce_str(enabled.get("action"), field_name="enabled.action"),
            "switch_reason": None,
            "selected_policy": None,
            "previous_policy": None,
            "zone": None,
            "candidate": None,
            "bars_since_regime_change": None,
            "matches_shared_shape": family_name is not None,
        }
    router_debug_dict = _coerce_dict(router_debug, field_name="enabled.router_debug")
    return {
        "timestamp": _normalize_timestamp(row.get("timestamp")),
        "family_name": family_name,
        "absent_action": _coerce_str(absent.get("action"), field_name="absent.action"),
        "enabled_action": _coerce_str(enabled.get("action"), field_name="enabled.action"),
        "switch_reason": router_debug_dict.get("switch_reason"),
        "selected_policy": router_debug_dict.get("selected_policy"),
        "previous_policy": router_debug_dict.get("previous_policy"),
        "zone": router_debug_dict.get("zone"),
        "candidate": router_debug_dict.get("candidate"),
        "bars_since_regime_change": router_debug_dict.get("bars_since_regime_change"),
        "matches_shared_shape": family_name is not None,
    }


def _load_2023_family_rows() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    path = ROOT_DIR / ANNUAL_2023_DIFF_RELATIVE
    try:
        payload = _load_json(path)
    except FileNotFoundError as exc:
        raise Missing2023AnnualSurfaceError(f"Missing 2023 annual diff surface at {path}") from exc
    if not isinstance(payload, list):
        raise MixedYearPocketIsolationError("Expected 2023 annual diff payload to be a list")

    family_rows: list[dict[str, Any]] = []
    anchor_rows: dict[str, dict[str, Any]] = {}
    for item in payload:
        row = _coerce_dict(item, field_name="annual_diff_row")
        timestamp = _normalize_timestamp(row.get("timestamp"))
        family_name = _family_from_row(row)
        if family_name is not None:
            family_rows.append(_normalize_family_row(row, family_name=family_name))
        if timestamp in DECEMBER_ANCHOR_TIMESTAMPS:
            anchor_rows[timestamp] = _normalize_anchor_row(row, family_name=family_name)

    return sorted(family_rows, key=lambda row: row["timestamp"]), {
        "path": str(ANNUAL_2023_DIFF_RELATIVE),
        "row_count": len(payload),
        "anchor_rows_seen": anchor_rows,
    }


def _month_counter(rows: list[dict[str, Any]], *, family_name: str | None = None) -> Counter[str]:
    counter: Counter[str] = Counter()
    for row in rows:
        if family_name is not None and row["family_name"] != family_name:
            continue
        counter[row["month"]] += 1
    return counter


def _rank_counter(counter: Counter[str]) -> list[dict[str, Any]]:
    total = sum(counter.values())
    ordered = sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    return [
        {
            "month": month,
            "count": count,
            "share_of_counted_rows": _round_or_none(count / total) if total else None,
        }
        for month, count in ordered
    ]


def _month_rank(rankings: list[dict[str, Any]], month: str) -> int | None:
    for index, row in enumerate(rankings, start=1):
        if row["month"] == month:
            return index
    return None


def _shared_shape_summary(
    combined_rankings: list[dict[str, Any]],
    suppression_rankings: list[dict[str, Any]],
    continuation_rankings: list[dict[str, Any]],
    family_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    december_rows = [row for row in family_rows if row["month"] == DECEMBER_MONTH]
    return {
        "counted_row_count": len(family_rows),
        "top_combined_month": (combined_rankings[0] if combined_rankings else None),
        "top_suppression_month": (suppression_rankings[0] if suppression_rankings else None),
        "top_continuation_month": (continuation_rankings[0] if continuation_rankings else None),
        "december_combined_rank": _month_rank(combined_rankings, DECEMBER_MONTH),
        "december_is_top_month": bool(
            combined_rankings and combined_rankings[0]["month"] == DECEMBER_MONTH
        ),
        "december_combined_count": len(december_rows),
        "december_share_of_total": (
            _round_or_none(len(december_rows) / len(family_rows)) if family_rows else None
        ),
    }


def _december_anchor_summary(
    anchor_rows_seen: dict[str, dict[str, Any]], family_rows: list[dict[str, Any]]
) -> dict[str, Any]:
    matching_rows = [row for row in family_rows if row["timestamp"] in DECEMBER_ANCHOR_TIMESTAMPS]
    matching_timestamps = {row["timestamp"] for row in matching_rows}
    seen_timestamps = set(anchor_rows_seen)
    return {
        "configured_anchor_timestamps": list(DECEMBER_ANCHOR_TIMESTAMPS),
        "seen_on_annual_surface": [
            anchor_rows_seen[timestamp] for timestamp in sorted(seen_timestamps)
        ],
        "matching_shared_shape": sorted(matching_rows, key=lambda item: item["timestamp"]),
        "missing_from_annual_surface": sorted(set(DECEMBER_ANCHOR_TIMESTAMPS) - seen_timestamps),
        "seen_but_not_matching_shared_shape": sorted(seen_timestamps - matching_timestamps),
    }


def _build_fail_closed_result(base_sha: str, reason: str) -> dict[str, Any]:
    return {
        "audit_version": "ri-policy-router-2023-mixed-year-pocket-isolation-2026-05-06",
        "base_sha": base_sha,
        "status": "fail_closed_missing_2023_annual_surface",
        "observational_only": True,
        "non_authoritative": True,
        "skill_usage": ["decision_gate_debug", "python_engineering"],
        "subject": {
            "year": FIXED_YEAR,
            "packet_reference": str(PACKET_REFERENCE),
            "curated_annual_reference": str(CURATED_ANNUAL_REFERENCE),
            "negative_year_reference": str(NEGATIVE_YEAR_REFERENCE),
            "positive_negative_reference": str(POSITIVE_NEGATIVE_REFERENCE),
            "bounded_contribution_reference": str(BOUNDED_CONTRIBUTION_REFERENCE),
            "december_residual_reference": str(DECEMBER_RESIDUAL_REFERENCE),
            "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
        },
        "failure_reason": reason,
    }


def run_2023_mixed_year_pocket_isolation(base_sha: str) -> dict[str, Any]:
    try:
        _, summary_metadata = _load_annual_summary()
        family_rows, diff_metadata = _load_2023_family_rows()
    except (Missing2023AnnualSurfaceError, MixedYearPocketIsolationError) as exc:
        return _build_fail_closed_result(base_sha=base_sha, reason=str(exc))

    combined_rankings = _rank_counter(_month_counter(family_rows))
    suppression_rankings = _rank_counter(_month_counter(family_rows, family_name="suppression"))
    continuation_rankings = _rank_counter(
        _month_counter(family_rows, family_name="continuation_displacement")
    )
    summary = _shared_shape_summary(
        combined_rankings=combined_rankings,
        suppression_rankings=suppression_rankings,
        continuation_rankings=continuation_rankings,
        family_rows=family_rows,
    )
    december_rows = [row for row in family_rows if row["month"] == DECEMBER_MONTH]
    status = (
        "december_is_top_shared_shape_month"
        if summary["december_is_top_month"]
        else "december_is_not_top_shared_shape_month"
    )

    return {
        "audit_version": "ri-policy-router-2023-mixed-year-pocket-isolation-2026-05-06",
        "base_sha": base_sha,
        "status": status,
        "observational_only": True,
        "non_authoritative": True,
        "skill_usage": ["decision_gate_debug", "python_engineering"],
        "subject": {
            "year": FIXED_YEAR,
            "packet_reference": str(PACKET_REFERENCE),
            "curated_annual_reference": str(CURATED_ANNUAL_REFERENCE),
            "negative_year_reference": str(NEGATIVE_YEAR_REFERENCE),
            "positive_negative_reference": str(POSITIVE_NEGATIVE_REFERENCE),
            "bounded_contribution_reference": str(BOUNDED_CONTRIBUTION_REFERENCE),
            "december_residual_reference": str(DECEMBER_RESIDUAL_REFERENCE),
            "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
        },
        "fail_closed_contract": {
            "statement": (
                "The helper reads only the fixed curated annual summary and exact 2023 annual "
                "action-diff file, counts only the pre-registered low-zone shared-shape families, "
                "reports the full month ranking rather than December only, and fails closed on a "
                "missing or malformed 2023 annual surface."
            )
        },
        "inputs": {
            "annual_summary": summary_metadata,
            "annual_2023_diff": {
                "path": diff_metadata["path"],
                "row_count": diff_metadata["row_count"],
            },
        },
        "family_definitions": {
            "suppression": {
                "absent_action": "LONG",
                "enabled_action": "NONE",
                "zone": "low",
                "switch_reasons": sorted(SUPPRESSION_SWITCH_REASONS),
            },
            "continuation_displacement": {
                "absent_action": "NONE",
                "enabled_action": "LONG",
                "zone": "low",
                "switch_reason": CONTINUATION_SWITCH_REASON,
            },
        },
        "shared_shape_summary": summary,
        "month_rankings": {
            "combined": combined_rankings,
            "suppression": suppression_rankings,
            "continuation_displacement": continuation_rankings,
        },
        "december_anchor_rows": _december_anchor_summary(
            anchor_rows_seen=diff_metadata["anchor_rows_seen"],
            family_rows=family_rows,
        ),
        "december_month_summary": {
            "month": DECEMBER_MONTH,
            "combined_count": len(december_rows),
            "suppression_count": sum(row["family_name"] == "suppression" for row in december_rows),
            "continuation_count": sum(
                row["family_name"] == "continuation_displacement" for row in december_rows
            ),
            "rows": december_rows,
        },
    }


def main() -> int:
    args = _parse_args()
    output_root = ROOT_DIR / Path(args.output_root_relative)
    output_json = output_root / args.summary_filename
    result = run_2023_mixed_year_pocket_isolation(base_sha=args.base_sha)

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "summary_artifact": str(output_json),
                "status": result["status"],
                "top_combined_month": result.get("shared_shape_summary", {}).get(
                    "top_combined_month"
                ),
                "december_combined_rank": result.get("shared_shape_summary", {}).get(
                    "december_combined_rank"
                ),
                "failure_reason": result.get("failure_reason"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
