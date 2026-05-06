from __future__ import annotations

import argparse
import calendar
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
ANNUAL_DIFF_RELATIVE_BY_YEAR = {
    "2017": Path(
        "results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/"
        "2017_enabled_vs_absent_action_diffs.json"
    ),
    "2023": Path(
        "results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/"
        "2023_enabled_vs_absent_action_diffs.json"
    ),
}
OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = "ri_policy_router_2023_vs_2017_mixed_year_shape_comparison_2026-05-06.json"
PACKET_REFERENCE = Path(
    "docs/decisions/regime_intelligence/policy_router/"
    "ri_policy_router_2023_vs_2017_mixed_year_shape_comparison_precode_packet_2026-05-06.md"
)
CURATED_ANNUAL_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_enabled_vs_absent_curated_annual_evidence_2026-04-28.md"
)
MIXED_2023_REFERENCE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_2023_mixed_year_pocket_isolation_2026-05-06.md"
)
WORKING_CONTRACT_REFERENCE = Path("GENESIS_WORKING_CONTRACT.md")
FIXED_YEARS = ("2017", "2023")
SUPPRESSION_SWITCH_REASONS = {
    "insufficient_evidence",
    "AGED_WEAK_CONTINUATION_GUARD",
}
CONTINUATION_SWITCH_REASON = "stable_continuation_state"
STATUS_DIFFERS = "mixed_year_shape_differs_between_2017_and_2023"
STATUS_OVERLAPS = "mixed_year_shape_overlaps_between_2017_and_2023"
STATUS_FAIL_CLOSED = "fail_closed_missing_mixed_year_surface"


class MixedYearShapeComparisonError(RuntimeError):
    pass


class MissingMixedYearSurfaceError(MixedYearShapeComparisonError):
    pass


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Materialize the bounded 2023-vs-2017 mixed-year comparison by ranking the fixed "
            "shared-shape families on the exact annual action-diff surfaces."
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
        raise MixedYearShapeComparisonError(
            f"Expected non-empty string for {field_name}, got {value!r}"
        )
    return value


def _coerce_optional_str(value: Any, *, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise MixedYearShapeComparisonError(
            f"Expected string-or-null for {field_name}, got {value!r}"
        )
    return value


def _coerce_dict(value: Any, *, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise MixedYearShapeComparisonError(f"Expected object for {field_name}, got {value!r}")
    return value


def _round_or_none(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 6)


def _parse_timestamp(raw: Any) -> datetime:
    timestamp = _coerce_str(raw, field_name="timestamp")
    normalized = timestamp.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise MixedYearShapeComparisonError(f"Invalid timestamp {timestamp!r}") from exc
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def _load_annual_summary() -> dict[str, Any]:
    path = ROOT_DIR / ANNUAL_SUMMARY_RELATIVE
    try:
        payload = _load_json(path)
    except FileNotFoundError as exc:
        raise MissingMixedYearSurfaceError(f"Missing annual summary surface at {path}") from exc

    summary = _coerce_dict(payload, field_name="annual_summary")
    years = _coerce_dict(summary.get("years"), field_name="annual_summary.years")
    metadata: dict[str, Any] = {"path": str(ANNUAL_SUMMARY_RELATIVE), "years": {}}
    for year in FIXED_YEARS:
        if year not in years:
            raise MissingMixedYearSurfaceError(f"Year {year} is missing from annual summary")
        year_payload = _coerce_dict(years[year], field_name=f"annual_summary.years.{year}")
        window = _coerce_dict(year_payload.get("window"), field_name=f"{year}.window")
        if bool(window.get("partial_year")):
            raise MissingMixedYearSurfaceError(f"Year {year} is partial and not admissible")
        comparison = _coerce_dict(
            year_payload.get("comparison"), field_name=f"annual_summary.years.{year}.comparison"
        )
        metadata["years"][year] = {
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
    return metadata


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


def _normalize_family_row(
    row: dict[str, Any], *, family_name: str, expected_year: str
) -> dict[str, Any]:
    enabled = _coerce_dict(row.get("enabled"), field_name="row.enabled")
    absent = _coerce_dict(row.get("absent"), field_name="row.absent")
    router_debug = _coerce_dict(enabled.get("router_debug"), field_name="enabled.router_debug")
    timestamp_dt = _parse_timestamp(row.get("timestamp"))
    timestamp = timestamp_dt.isoformat()
    if timestamp[:4] != expected_year:
        raise MixedYearShapeComparisonError(
            f"Row timestamp {timestamp!r} does not belong to expected year {expected_year}"
        )

    return {
        "timestamp": timestamp,
        "month_number": timestamp_dt.month,
        "month_name": calendar.month_name[timestamp_dt.month],
        "family_name": family_name,
        "absent_action": _coerce_str(absent.get("action"), field_name="absent.action"),
        "enabled_action": _coerce_str(enabled.get("action"), field_name="enabled.action"),
        "switch_reason": _coerce_str(
            router_debug.get("switch_reason"), field_name="enabled.router_debug.switch_reason"
        ),
        "selected_policy": _coerce_str(
            router_debug.get("selected_policy"), field_name="enabled.router_debug.selected_policy"
        ),
        "previous_policy": _coerce_optional_str(
            router_debug.get("previous_policy"), field_name="enabled.router_debug.previous_policy"
        ),
        "zone": _coerce_str(router_debug.get("zone"), field_name="enabled.router_debug.zone"),
        "candidate": _coerce_str(
            router_debug.get("candidate"), field_name="enabled.router_debug.candidate"
        ),
        "bars_since_regime_change": router_debug.get("bars_since_regime_change"),
    }


def _load_year_family_rows(year: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    relative = ANNUAL_DIFF_RELATIVE_BY_YEAR[year]
    path = ROOT_DIR / relative
    try:
        payload = _load_json(path)
    except FileNotFoundError as exc:
        raise MissingMixedYearSurfaceError(f"Missing {year} annual diff surface at {path}") from exc

    if not isinstance(payload, list):
        raise MixedYearShapeComparisonError(f"Expected {year} annual diff payload to be a list")

    family_rows: list[dict[str, Any]] = []
    for item in payload:
        row = _coerce_dict(item, field_name="annual_diff_row")
        family_name = _family_from_row(row)
        if family_name is None:
            continue
        family_rows.append(_normalize_family_row(row, family_name=family_name, expected_year=year))

    return sorted(family_rows, key=lambda row: (row["month_number"], row["timestamp"])), {
        "path": str(relative),
        "row_count": len(payload),
    }


def _month_counter(rows: list[dict[str, Any]], *, family_name: str | None = None) -> Counter[int]:
    counter: Counter[int] = Counter()
    for row in rows:
        if family_name is not None and row["family_name"] != family_name:
            continue
        counter[int(row["month_number"])] += 1
    return counter


def _rank_counter(counter: Counter[int]) -> list[dict[str, Any]]:
    total = sum(counter.values())
    ordered = sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    return [
        {
            "month_number": month_number,
            "month_name": calendar.month_name[month_number],
            "count": count,
            "share_of_counted_rows": _round_or_none(count / total) if total else None,
        }
        for month_number, count in ordered
    ]


def _month_rank(rankings: list[dict[str, Any]], month_number: int) -> int | None:
    for index, row in enumerate(rankings, start=1):
        if row["month_number"] == month_number:
            return index
    return None


def _tied_top_months(rankings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not rankings:
        return []
    top_count = rankings[0]["count"]
    return [row for row in rankings if row["count"] == top_count]


def _primary_top_month(rankings: list[dict[str, Any]]) -> dict[str, Any] | None:
    return rankings[0] if rankings else None


def _year_summary(
    year: str,
    *,
    family_rows: list[dict[str, Any]],
    combined_rankings: list[dict[str, Any]],
    suppression_rankings: list[dict[str, Any]],
    continuation_rankings: list[dict[str, Any]],
    combined_counter: Counter[int],
    suppression_counter: Counter[int],
) -> dict[str, Any]:
    december_count = combined_counter.get(12, 0)
    suppression_total = sum(suppression_counter.values())
    june_suppression_count = suppression_counter.get(6, 0)
    return {
        "counted_row_count": len(family_rows),
        "primary_top_combined_month": _primary_top_month(combined_rankings),
        "primary_top_suppression_month": _primary_top_month(suppression_rankings),
        "primary_top_continuation_month": _primary_top_month(continuation_rankings),
        "tied_top_combined_months": _tied_top_months(combined_rankings),
        "tied_top_suppression_months": _tied_top_months(suppression_rankings),
        "tied_top_continuation_months": _tied_top_months(continuation_rankings),
        "december_combined_rank": _month_rank(combined_rankings, 12),
        "december_is_primary_top_month": bool(
            combined_rankings and combined_rankings[0]["month_number"] == 12
        ),
        "december_is_tied_top_month": any(
            row["month_number"] == 12 for row in _tied_top_months(combined_rankings)
        ),
        "december_combined_count": december_count,
        "december_share_of_total": (
            _round_or_none(december_count / len(family_rows)) if family_rows else None
        ),
        "june_suppression_rank": _month_rank(suppression_rankings, 6),
        "june_is_primary_top_suppression_month": bool(
            suppression_rankings and suppression_rankings[0]["month_number"] == 6
        ),
        "june_is_tied_top_suppression_month": any(
            row["month_number"] == 6 for row in _tied_top_months(suppression_rankings)
        ),
        "june_suppression_count": june_suppression_count,
        "june_share_of_suppression": (
            _round_or_none(june_suppression_count / suppression_total)
            if suppression_total
            else None
        ),
        "year": year,
    }


def _top_month_set(summary: dict[str, Any], key: str) -> list[int]:
    return [int(row["month_number"]) for row in summary[key]]


def _cross_year_comparison(year_summaries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    top_combined_sets = {
        year: _top_month_set(summary, "tied_top_combined_months")
        for year, summary in year_summaries.items()
    }
    top_suppression_sets = {
        year: _top_month_set(summary, "tied_top_suppression_months")
        for year, summary in year_summaries.items()
    }
    top_continuation_sets = {
        year: _top_month_set(summary, "tied_top_continuation_months")
        for year, summary in year_summaries.items()
    }
    return {
        "primary_top_combined_months": {
            year: summary["primary_top_combined_month"] for year, summary in year_summaries.items()
        },
        "primary_top_suppression_months": {
            year: summary["primary_top_suppression_month"]
            for year, summary in year_summaries.items()
        },
        "primary_top_continuation_months": {
            year: summary["primary_top_continuation_month"]
            for year, summary in year_summaries.items()
        },
        "tied_top_combined_month_numbers": top_combined_sets,
        "tied_top_suppression_month_numbers": top_suppression_sets,
        "tied_top_continuation_month_numbers": top_continuation_sets,
        "same_top_combined_month_set": top_combined_sets["2017"] == top_combined_sets["2023"],
        "same_top_suppression_month_set": (
            top_suppression_sets["2017"] == top_suppression_sets["2023"]
        ),
        "same_top_continuation_month_set": (
            top_continuation_sets["2017"] == top_continuation_sets["2023"]
        ),
        "year_specific_checks": {
            "2017": {
                "december_is_primary_top_combined": year_summaries["2017"][
                    "december_is_primary_top_month"
                ],
                "june_is_primary_top_suppression": year_summaries["2017"][
                    "june_is_primary_top_suppression_month"
                ],
            },
            "2023": {
                "december_is_primary_top_combined": year_summaries["2023"][
                    "december_is_primary_top_month"
                ],
                "december_is_primary_top_continuation": bool(
                    year_summaries["2023"]["primary_top_continuation_month"]
                    and year_summaries["2023"]["primary_top_continuation_month"]["month_number"]
                    == 12
                ),
                "june_is_primary_top_suppression": year_summaries["2023"][
                    "june_is_primary_top_suppression_month"
                ],
            },
        },
    }


def _status_from_comparison(comparison: dict[str, Any]) -> str:
    if (
        comparison["same_top_combined_month_set"]
        and comparison["same_top_suppression_month_set"]
        and comparison["same_top_continuation_month_set"]
    ):
        return STATUS_OVERLAPS
    return STATUS_DIFFERS


def _build_fail_closed_result(base_sha: str, reason: str) -> dict[str, Any]:
    return {
        "audit_version": "ri-policy-router-2023-vs-2017-mixed-year-shape-comparison-2026-05-06",
        "base_sha": base_sha,
        "status": STATUS_FAIL_CLOSED,
        "observational_only": True,
        "non_authoritative": True,
        "skill_usage": ["decision_gate_debug", "python_engineering"],
        "subject": {
            "years": list(FIXED_YEARS),
            "packet_reference": str(PACKET_REFERENCE),
            "curated_annual_reference": str(CURATED_ANNUAL_REFERENCE),
            "mixed_2023_reference": str(MIXED_2023_REFERENCE),
            "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
        },
        "failure_reason": reason,
    }


def run_2023_vs_2017_mixed_year_shape_comparison(base_sha: str) -> dict[str, Any]:
    try:
        summary_metadata = _load_annual_summary()
        family_rows_by_year: dict[str, list[dict[str, Any]]] = {}
        diff_metadata: dict[str, Any] = {}
        year_summaries: dict[str, dict[str, Any]] = {}
        month_rankings: dict[str, dict[str, Any]] = {}
        for year in FIXED_YEARS:
            family_rows, year_diff_metadata = _load_year_family_rows(year)
            family_rows_by_year[year] = family_rows
            diff_metadata[year] = year_diff_metadata
            combined_counter = _month_counter(family_rows)
            suppression_counter = _month_counter(family_rows, family_name="suppression")
            continuation_counter = _month_counter(
                family_rows, family_name="continuation_displacement"
            )
            combined_rankings = _rank_counter(combined_counter)
            suppression_rankings = _rank_counter(suppression_counter)
            continuation_rankings = _rank_counter(continuation_counter)
            year_summaries[year] = _year_summary(
                year,
                family_rows=family_rows,
                combined_rankings=combined_rankings,
                suppression_rankings=suppression_rankings,
                continuation_rankings=continuation_rankings,
                combined_counter=combined_counter,
                suppression_counter=suppression_counter,
            )
            month_rankings[year] = {
                "combined": combined_rankings,
                "suppression": suppression_rankings,
                "continuation_displacement": continuation_rankings,
            }
    except (MissingMixedYearSurfaceError, MixedYearShapeComparisonError) as exc:
        return _build_fail_closed_result(base_sha=base_sha, reason=str(exc))

    comparison = _cross_year_comparison(year_summaries)
    status = _status_from_comparison(comparison)

    return {
        "audit_version": "ri-policy-router-2023-vs-2017-mixed-year-shape-comparison-2026-05-06",
        "base_sha": base_sha,
        "status": status,
        "observational_only": True,
        "non_authoritative": True,
        "skill_usage": ["decision_gate_debug", "python_engineering"],
        "subject": {
            "years": list(FIXED_YEARS),
            "packet_reference": str(PACKET_REFERENCE),
            "curated_annual_reference": str(CURATED_ANNUAL_REFERENCE),
            "mixed_2023_reference": str(MIXED_2023_REFERENCE),
            "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
        },
        "fail_closed_contract": {
            "statement": (
                "The helper reads only the fixed curated annual summary plus the exact 2017 and "
                "2023 annual action-diff files, counts only the pre-registered low-zone shared-"
                "shape families, emits full combined/suppression/continuation month rankings for "
                "both years, and fails closed on a missing or malformed mixed-year surface."
            )
        },
        "inputs": {
            "annual_summary": summary_metadata,
            "annual_diffs": diff_metadata,
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
        "year_summaries": year_summaries,
        "month_rankings": month_rankings,
        "cross_year_comparison": comparison,
    }


def main() -> int:
    args = _parse_args()
    output_root = ROOT_DIR / Path(args.output_root_relative)
    output_json = output_root / args.summary_filename
    result = run_2023_vs_2017_mixed_year_shape_comparison(base_sha=args.base_sha)

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "summary_artifact": str(output_json),
                "status": result["status"],
                "primary_top_combined_months": result.get("cross_year_comparison", {}).get(
                    "primary_top_combined_months"
                ),
                "primary_top_suppression_months": result.get("cross_year_comparison", {}).get(
                    "primary_top_suppression_months"
                ),
                "primary_top_continuation_months": result.get("cross_year_comparison", {}).get(
                    "primary_top_continuation_months"
                ),
                "failure_reason": result.get("failure_reason"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
