# ruff: noqa: E402

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def _find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "pyproject.toml").exists() and (candidate / "src").exists():
            return candidate
    raise RuntimeError("Could not locate repository root from probe path")


ROOT_DIR = _find_repo_root(Path(__file__).resolve())
SRC_DIR = ROOT_DIR / "src"
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from scripts.analyze import (
    ri_policy_router_continuation_release_hysteresis_carrier_validation_20260504 as carrier_base,
)

EXACT_START = "2025-10-01"
EXACT_END = "2025-10-31"
ANNUAL_START = "2025-01-01"
ANNUAL_END = "2025-12-31"
MONTH_PREFIX = "2025-10-"
OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = "ri_policy_router_continuation_release_hysteresis_window_sensitivity_2025_10_vs_annual_2025_2026-05-26.json"
STATUS_OK = "continuation_release_hysteresis_window_sensitivity_2025_10_vs_annual_2025_generated"
STATUS_FAIL_CLOSED = (
    "continuation_release_hysteresis_window_sensitivity_2025_10_vs_annual_2025_fail_closed"
)
DIFF_TOLERANCE = 1e-12


class WindowSensitivityError(RuntimeError):
    pass


def _round_or_none(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 6)


def _summary_float(summary: dict[str, Any], field_name: str) -> float:
    raw_value = summary.get(field_name)
    if raw_value is None:
        raise WindowSensitivityError(f"Missing summary field {field_name!r}")
    return float(raw_value)


def _strip_rows(case: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in case.items()
        if key not in {"rows", "continuation_release_rows"}
    }


def _is_continuation_release(row: dict[str, Any] | None) -> bool:
    debug = (row or {}).get("router_debug") or {}
    return debug.get("switch_control_mode") == "continuation_release"


def _select_month_rows(rows: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {timestamp: row for timestamp, row in rows.items() if timestamp.startswith(MONTH_PREFIX)}


def _run_surface(
    *,
    start: str,
    end: str,
    base_cfg: dict[str, Any],
    carrier_cfg: dict[str, Any],
    authority: Any,
) -> dict[str, dict[str, Any]]:
    carrier_base.START = start
    carrier_base.END = end
    baseline = carrier_base._run_case(
        "baseline", base_cfg=base_cfg, carrier_cfg=carrier_cfg, authority=authority
    )
    release_zero = carrier_base._run_case(
        "release_zero", base_cfg=base_cfg, carrier_cfg=carrier_cfg, authority=authority
    )
    return {"baseline": baseline, "release_zero": release_zero}


def _compare_mode(
    *,
    mode: str,
    exact_case: dict[str, Any],
    annual_case: dict[str, Any],
) -> dict[str, Any]:
    exact_rows = dict(exact_case.get("rows") or {})
    annual_rows = _select_month_rows(dict(annual_case.get("rows") or {}))
    exact_release_rows = dict(exact_case.get("continuation_release_rows") or {})
    annual_release_rows = _select_month_rows(
        dict(annual_case.get("continuation_release_rows") or {})
    )

    timestamps = sorted(set(exact_rows) | set(annual_rows))
    shared_timestamps = sorted(set(exact_rows) & set(annual_rows))

    all_row_diff_count = 0
    action_diff_count = 0
    behavioral_row_diff_count = 0
    continuation_release_presence_diff_count = 0
    shared_row_diff_count = 0
    shared_action_diff_count = 0
    shared_behavioral_row_diff_count = 0
    shared_continuation_release_presence_diff_count = 0
    exact_only_timestamp_count = 0
    annual_only_timestamp_count = 0
    first_row_diff: dict[str, Any] | None = None
    first_behavior_diff: dict[str, Any] | None = None
    first_continuation_release_presence_diff: dict[str, Any] | None = None
    first_shared_row_diff: dict[str, Any] | None = None
    first_shared_behavior_diff: dict[str, Any] | None = None
    first_shared_continuation_release_presence_diff: dict[str, Any] | None = None
    representative_diffs: list[dict[str, Any]] = []

    for timestamp in timestamps:
        exact_row = exact_rows.get(timestamp)
        annual_row = annual_rows.get(timestamp)
        row_differs = exact_row != annual_row
        action_diff = (exact_row or {}).get("action") != (annual_row or {}).get("action")
        behavior_diff = carrier_base._behavior_row(exact_row) != carrier_base._behavior_row(
            annual_row
        )
        exact_continuation_release = _is_continuation_release(exact_row)
        annual_continuation_release = _is_continuation_release(annual_row)
        continuation_release_presence_diff = (
            exact_continuation_release != annual_continuation_release
        )

        if exact_row is None:
            annual_only_timestamp_count += 1
        if annual_row is None:
            exact_only_timestamp_count += 1
        shared_timestamp = exact_row is not None and annual_row is not None
        if row_differs:
            all_row_diff_count += 1
            if first_row_diff is None:
                first_row_diff = {
                    "timestamp": timestamp,
                    "exact": exact_row,
                    "annual_embedded": annual_row,
                }
            if shared_timestamp:
                shared_row_diff_count += 1
                if first_shared_row_diff is None:
                    first_shared_row_diff = {
                        "timestamp": timestamp,
                        "exact": exact_row,
                        "annual_embedded": annual_row,
                    }
        if action_diff:
            action_diff_count += 1
            if shared_timestamp:
                shared_action_diff_count += 1
        if behavior_diff:
            behavioral_row_diff_count += 1
            if first_behavior_diff is None:
                first_behavior_diff = {
                    "timestamp": timestamp,
                    "exact": exact_row,
                    "annual_embedded": annual_row,
                }
            if shared_timestamp:
                shared_behavioral_row_diff_count += 1
                if first_shared_behavior_diff is None:
                    first_shared_behavior_diff = {
                        "timestamp": timestamp,
                        "exact": exact_row,
                        "annual_embedded": annual_row,
                    }
        if continuation_release_presence_diff:
            continuation_release_presence_diff_count += 1
            if first_continuation_release_presence_diff is None:
                first_continuation_release_presence_diff = {
                    "timestamp": timestamp,
                    "exact": exact_row,
                    "annual_embedded": annual_row,
                }
            if shared_timestamp:
                shared_continuation_release_presence_diff_count += 1
                if first_shared_continuation_release_presence_diff is None:
                    first_shared_continuation_release_presence_diff = {
                        "timestamp": timestamp,
                        "exact": exact_row,
                        "annual_embedded": annual_row,
                    }

        if (row_differs or behavior_diff or continuation_release_presence_diff) and len(
            representative_diffs
        ) < carrier_base.REPRESENTATIVE_LIMIT:
            representative_diffs.append(
                {
                    "timestamp": timestamp,
                    "row_differs": row_differs,
                    "action_diff": action_diff,
                    "behavior_diff": behavior_diff,
                    "exact_continuation_release": exact_continuation_release,
                    "annual_embedded_continuation_release": annual_continuation_release,
                    "exact": exact_row,
                    "annual_embedded": annual_row,
                }
            )

    return {
        "mode": mode,
        "exact_row_count": len(exact_rows),
        "annual_embedded_row_count": len(annual_rows),
        "shared_timestamp_count": len(shared_timestamps),
        "exact_only_timestamp_count": exact_only_timestamp_count,
        "annual_only_timestamp_count": annual_only_timestamp_count,
        "all_row_diff_count": all_row_diff_count,
        "action_diff_count": action_diff_count,
        "behavioral_row_diff_count": behavioral_row_diff_count,
        "continuation_release_presence_diff_count": continuation_release_presence_diff_count,
        "shared_row_diff_count": shared_row_diff_count,
        "shared_action_diff_count": shared_action_diff_count,
        "shared_behavioral_row_diff_count": shared_behavioral_row_diff_count,
        "shared_continuation_release_presence_diff_count": shared_continuation_release_presence_diff_count,
        "exact_continuation_release_row_count": len(exact_release_rows),
        "annual_embedded_continuation_release_row_count": len(annual_release_rows),
        "exact_continuation_release_timestamps": sorted(exact_release_rows),
        "annual_embedded_continuation_release_timestamps": sorted(annual_release_rows),
        "first_row_diff": first_row_diff,
        "first_behavior_diff": first_behavior_diff,
        "first_continuation_release_presence_diff": first_continuation_release_presence_diff,
        "first_shared_row_diff": first_shared_row_diff,
        "first_shared_behavior_diff": first_shared_behavior_diff,
        "first_shared_continuation_release_presence_diff": first_shared_continuation_release_presence_diff,
        "representative_diffs": representative_diffs,
    }


def _packet_summary(
    *,
    exact_baseline_summary: dict[str, Any],
    exact_release_zero_summary: dict[str, Any],
    annual_baseline_summary: dict[str, Any],
    annual_release_zero_summary: dict[str, Any],
    baseline_mode_comparison: dict[str, Any],
    release_zero_mode_comparison: dict[str, Any],
) -> dict[str, Any]:
    exact_total_return_diff = _summary_float(
        exact_release_zero_summary, "total_return"
    ) - _summary_float(exact_baseline_summary, "total_return")
    exact_final_capital_diff = _summary_float(
        exact_release_zero_summary, "final_capital"
    ) - _summary_float(exact_baseline_summary, "final_capital")
    annual_total_return_diff = _summary_float(
        annual_release_zero_summary, "total_return"
    ) - _summary_float(annual_baseline_summary, "total_return")
    annual_final_capital_diff = _summary_float(
        annual_release_zero_summary, "final_capital"
    ) - _summary_float(annual_baseline_summary, "final_capital")

    window_sensitivity_detected = any(
        [
            baseline_mode_comparison["all_row_diff_count"] > 0,
            release_zero_mode_comparison["all_row_diff_count"] > 0,
            baseline_mode_comparison["continuation_release_presence_diff_count"] > 0,
            release_zero_mode_comparison["continuation_release_presence_diff_count"] > 0,
        ]
    )

    if window_sensitivity_detected:
        status = "exact_october_vs_embedded_october_window_sensitivity_detected"
        inference = (
            "The exact October 2025 subject is not equivalent to October as reached through the full-year 2025 path. "
            "That means the local October seam behavior is anchor- or carry-in-sensitive rather than a simple property "
            "of calendar rows viewed in isolation."
        )
    else:
        status = "exact_october_matches_embedded_october_on_observed_surface"
        inference = (
            "The exact October 2025 subject reproduces the same observed row surface as October embedded inside the "
            "annual 2025 path. That would argue against anchoring sensitivity on this observed surface."
        )

    if (
        abs(exact_total_return_diff) > DIFF_TOLERANCE
        and abs(annual_total_return_diff) <= DIFF_TOLERANCE
    ):
        top_line_read = (
            "The exact October subject still shows a local top-line delta while the full-year 2025 same-stack surface "
            "stays flat, which reinforces that exact-month evidence and annual evidence are answering different questions."
        )
    else:
        top_line_read = (
            "The exact-month and annual top-line surfaces do not separate into a simple local-vs-annual contrast on "
            "this run."
        )

    return {
        "status": status,
        "exact_total_return_diff": _round_or_none(exact_total_return_diff),
        "exact_final_capital_diff": _round_or_none(exact_final_capital_diff),
        "annual_total_return_diff": _round_or_none(annual_total_return_diff),
        "annual_final_capital_diff": _round_or_none(annual_final_capital_diff),
        "baseline_first_union_row_diff_timestamp": (
            baseline_mode_comparison.get("first_row_diff") or {}
        ).get("timestamp"),
        "release_zero_first_union_row_diff_timestamp": (
            release_zero_mode_comparison.get("first_row_diff") or {}
        ).get("timestamp"),
        "baseline_first_shared_row_diff_timestamp": (
            baseline_mode_comparison.get("first_shared_row_diff") or {}
        ).get("timestamp"),
        "release_zero_first_shared_row_diff_timestamp": (
            release_zero_mode_comparison.get("first_shared_row_diff") or {}
        ).get("timestamp"),
        "baseline_shared_row_diff_count": baseline_mode_comparison["shared_row_diff_count"],
        "release_zero_shared_row_diff_count": release_zero_mode_comparison["shared_row_diff_count"],
        "baseline_exact_continuation_release_row_count": baseline_mode_comparison[
            "exact_continuation_release_row_count"
        ],
        "baseline_annual_embedded_continuation_release_row_count": baseline_mode_comparison[
            "annual_embedded_continuation_release_row_count"
        ],
        "release_zero_exact_continuation_release_row_count": release_zero_mode_comparison[
            "exact_continuation_release_row_count"
        ],
        "release_zero_annual_embedded_continuation_release_row_count": release_zero_mode_comparison[
            "annual_embedded_continuation_release_row_count"
        ],
        "inference": inference,
        "top_line_read": top_line_read,
        "next_hypothesis": (
            "If exact October and embedded October separate immediately or before continuation-release rows appear, the "
            "next honest slice is to isolate the first state-carry timestamp that makes the exact month enter a different "
            "router path than the annual run."
        ),
    }


def _build_fail_closed_result(reason: str) -> dict[str, Any]:
    return {
        "audit_version": (
            "ri-policy-router-continuation-release-hysteresis-window-sensitivity-2025-10-vs-annual-2025-2026-05-26"
        ),
        "base_sha": carrier_base._json_safe(
            __import__("subprocess")
            .check_output(["git", "rev-parse", "HEAD"], cwd=ROOT_DIR, text=True)
            .strip()
        ),
        "status": STATUS_FAIL_CLOSED,
        "observational_only": True,
        "non_authoritative": True,
        "failure_reason": reason,
        "inputs": {
            "carrier_path": str(carrier_base.CARRIER_PATH.relative_to(ROOT_DIR)),
            "exact_subject": {
                "start": EXACT_START,
                "end": EXACT_END,
            },
            "embedded_annual_subject": {
                "start": ANNUAL_START,
                "end": ANNUAL_END,
                "month_prefix": MONTH_PREFIX,
            },
        },
    }


def run_window_sensitivity_probe() -> dict[str, Any]:
    base_cfg, carrier_cfg, authority = carrier_base._load_base_and_carrier_cfg()
    exact_surface = _run_surface(
        start=EXACT_START,
        end=EXACT_END,
        base_cfg=base_cfg,
        carrier_cfg=carrier_cfg,
        authority=authority,
    )
    annual_surface = _run_surface(
        start=ANNUAL_START,
        end=ANNUAL_END,
        base_cfg=base_cfg,
        carrier_cfg=carrier_cfg,
        authority=authority,
    )

    baseline_mode_comparison = _compare_mode(
        mode="baseline",
        exact_case=exact_surface["baseline"],
        annual_case=annual_surface["baseline"],
    )
    release_zero_mode_comparison = _compare_mode(
        mode="release_zero",
        exact_case=exact_surface["release_zero"],
        annual_case=annual_surface["release_zero"],
    )

    packet_summary = _packet_summary(
        exact_baseline_summary=dict(exact_surface["baseline"].get("summary") or {}),
        exact_release_zero_summary=dict(exact_surface["release_zero"].get("summary") or {}),
        annual_baseline_summary=dict(annual_surface["baseline"].get("summary") or {}),
        annual_release_zero_summary=dict(annual_surface["release_zero"].get("summary") or {}),
        baseline_mode_comparison=baseline_mode_comparison,
        release_zero_mode_comparison=release_zero_mode_comparison,
    )

    return {
        "audit_version": (
            "ri-policy-router-continuation-release-hysteresis-window-sensitivity-2025-10-vs-annual-2025-2026-05-26"
        ),
        "base_sha": carrier_base._json_safe(
            __import__("subprocess")
            .check_output(["git", "rev-parse", "HEAD"], cwd=ROOT_DIR, text=True)
            .strip()
        ),
        "status": STATUS_OK,
        "observational_only": True,
        "non_authoritative": True,
        "classification_boundary": {
            "reference_surface": (
                "exact 2025-10 subject versus the October rows embedded inside the full-year 2025 same-stack path, "
                "comparing both baseline and release_zero under the same landed continuation_release_hysteresis carrier"
            ),
            "question": (
                "Does the continuation-release behavior seen on the exact 2025-10 subject persist when October is "
                "reached through the full-year 2025 path, or is the observed October seam footprint anchor-sensitive?"
            ),
            "outcome_metrics_observational_only": True,
        },
        "inputs": {
            "carrier_path": str(carrier_base.CARRIER_PATH.relative_to(ROOT_DIR)),
            "comparison": {
                "baseline": "enabled carrier as-is (implicit shared hysteresis)",
                "release_zero": "same enabled carrier with continuation_release_hysteresis=0",
                "variant_setting": {
                    "field": "multi_timeframe.research_policy_router.continuation_release_hysteresis",
                    "baseline_value": "implicit shared hysteresis",
                    "release_zero_value": 0,
                },
            },
            "exact_subject": {
                "symbol": carrier_base.SYMBOL,
                "timeframe": carrier_base.TIMEFRAME,
                "start": EXACT_START,
                "end": EXACT_END,
                "warmup": carrier_base.WARMUP,
                "data_source_policy": carrier_base.DATA_SOURCE_POLICY,
            },
            "embedded_annual_subject": {
                "symbol": carrier_base.SYMBOL,
                "timeframe": carrier_base.TIMEFRAME,
                "start": ANNUAL_START,
                "end": ANNUAL_END,
                "month_prefix": MONTH_PREFIX,
                "warmup": carrier_base.WARMUP,
                "data_source_policy": carrier_base.DATA_SOURCE_POLICY,
            },
        },
        "exact_surface": {
            "baseline": _strip_rows(exact_surface["baseline"]),
            "release_zero": _strip_rows(exact_surface["release_zero"]),
        },
        "annual_surface": {
            "baseline": _strip_rows(annual_surface["baseline"]),
            "release_zero": _strip_rows(annual_surface["release_zero"]),
        },
        "comparison": {
            "baseline_exact_vs_annual_embedded_october": baseline_mode_comparison,
            "release_zero_exact_vs_annual_embedded_october": release_zero_mode_comparison,
        },
        "packet_summary": packet_summary,
    }


def main() -> int:
    output_root = ROOT_DIR / OUTPUT_ROOT_RELATIVE
    output_json = output_root / OUTPUT_FILENAME
    try:
        result = run_window_sensitivity_probe()
    except Exception as exc:  # fail-closed research wrapper
        result = _build_fail_closed_result(str(exc))

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    packet_summary = result.get("packet_summary") or {}
    summary = {
        "summary_artifact": str(output_json),
        "status": packet_summary.get("status", result.get("status")),
        "exact_total_return_diff": packet_summary.get("exact_total_return_diff"),
        "annual_total_return_diff": packet_summary.get("annual_total_return_diff"),
        "baseline_first_union_row_diff_timestamp": packet_summary.get(
            "baseline_first_union_row_diff_timestamp"
        ),
        "release_zero_first_union_row_diff_timestamp": packet_summary.get(
            "release_zero_first_union_row_diff_timestamp"
        ),
        "baseline_first_shared_row_diff_timestamp": packet_summary.get(
            "baseline_first_shared_row_diff_timestamp"
        ),
        "release_zero_first_shared_row_diff_timestamp": packet_summary.get(
            "release_zero_first_shared_row_diff_timestamp"
        ),
        "baseline_exact_continuation_release_row_count": packet_summary.get(
            "baseline_exact_continuation_release_row_count"
        ),
        "baseline_annual_embedded_continuation_release_row_count": packet_summary.get(
            "baseline_annual_embedded_continuation_release_row_count"
        ),
        "release_zero_exact_continuation_release_row_count": packet_summary.get(
            "release_zero_exact_continuation_release_row_count"
        ),
        "release_zero_annual_embedded_continuation_release_row_count": packet_summary.get(
            "release_zero_annual_embedded_continuation_release_row_count"
        ),
        "failure_reason": result.get("failure_reason"),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
