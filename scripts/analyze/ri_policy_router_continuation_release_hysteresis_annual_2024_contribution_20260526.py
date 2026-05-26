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

START = "2024-01-01"
END = "2024-12-31"
OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = (
    "ri_policy_router_continuation_release_hysteresis_annual_2024_contribution_2026-05-26.json"
)
STATUS_OK = "continuation_release_hysteresis_annual_2024_contribution_generated"
STATUS_FAIL_CLOSED = "continuation_release_hysteresis_annual_2024_contribution_fail_closed"
DIFF_TOLERANCE = 1e-12


class Annual2024ContributionError(RuntimeError):
    pass


def _round_or_none(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 6)


def _summary_float(summary: dict[str, Any], field_name: str) -> float:
    raw_value = summary.get(field_name)
    if raw_value is None:
        raise Annual2024ContributionError(f"Missing summary field {field_name!r}")
    return float(raw_value)


def _packet_summary(
    *,
    baseline_summary: dict[str, Any],
    release_zero_summary: dict[str, Any],
    baseline_position_summary: dict[str, Any],
    release_zero_position_summary: dict[str, Any],
    all_row_diff_count: int,
    action_diff_count: int,
    behavioral_row_diff_count: int,
    continuation_release_diff_count: int,
) -> dict[str, Any]:
    total_return_diff = _summary_float(release_zero_summary, "total_return") - _summary_float(
        baseline_summary, "total_return"
    )
    final_capital_diff = _summary_float(release_zero_summary, "final_capital") - _summary_float(
        baseline_summary, "final_capital"
    )
    profit_factor_diff = _summary_float(release_zero_summary, "profit_factor") - _summary_float(
        baseline_summary, "profit_factor"
    )
    max_drawdown_diff = _summary_float(release_zero_summary, "max_drawdown") - _summary_float(
        baseline_summary, "max_drawdown"
    )
    num_trades_diff = _summary_float(release_zero_summary, "num_trades") - _summary_float(
        baseline_summary, "num_trades"
    )
    net_position_pnl_diff = _summary_float(
        release_zero_position_summary, "net_pnl"
    ) - _summary_float(baseline_position_summary, "net_pnl")

    if total_return_diff > DIFF_TOLERANCE and final_capital_diff > DIFF_TOLERANCE:
        status = "annual_2024_release_zero_outperforms_baseline"
        inference = (
            "On the fixed 2024 full-year surface, removing continuation-release hysteresis improves the top line "
            "relative to the baseline carrier. That means the seam is at least directionally harmful on this broader "
            "stack-preserving year surface, even if the earlier exact local slices repeatedly stayed flat."
        )
    elif total_return_diff < -DIFF_TOLERANCE and final_capital_diff < -DIFF_TOLERANCE:
        status = "annual_2024_baseline_outperforms_release_zero"
        inference = (
            "On the fixed 2024 full-year surface, keeping continuation-release hysteresis improves the top line "
            "relative to the release-zero variant. That means the seam contributes positively on this broader "
            "stack-preserving year surface."
        )
    else:
        status = "annual_2024_topline_mixed_or_flat_between_baseline_and_release_zero"
        inference = (
            "On the fixed 2024 full-year surface, the release-zero-minus-baseline top line is mixed or flat. The seam "
            "still changes many rows, but a broader annual verdict cannot be reduced to a simple one-direction win from "
            "total return and final capital alone."
        )

    return {
        "status": status,
        "total_return_diff": _round_or_none(total_return_diff),
        "final_capital_diff": _round_or_none(final_capital_diff),
        "profit_factor_diff": _round_or_none(profit_factor_diff),
        "max_drawdown_pct_diff": _round_or_none(max_drawdown_diff),
        "num_trades_diff": _round_or_none(num_trades_diff),
        "net_position_pnl_diff": _round_or_none(net_position_pnl_diff),
        "all_row_diff_count": all_row_diff_count,
        "action_diff_count": action_diff_count,
        "behavioral_row_diff_count": behavioral_row_diff_count,
        "continuation_release_diff_count": continuation_release_diff_count,
        "inference": inference,
        "next_hypothesis": (
            "If this broader 2024 seam surface still matters after the local chain is exhausted, the next honest "
            "comparison is either one positive-year control against the same seam or a bounded row-family isolation of "
            "where the annual delta actually accumulates."
        ),
    }


def _build_fail_closed_result(reason: str) -> dict[str, Any]:
    return {
        "audit_version": "ri-policy-router-continuation-release-hysteresis-annual-2024-contribution-2026-05-26",
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
            "comparison": {
                "baseline": "enabled carrier as-is (implicit shared hysteresis)",
                "release_zero": "same enabled carrier with continuation_release_hysteresis=0",
                "variant_setting": {
                    "field": "multi_timeframe.research_policy_router.continuation_release_hysteresis",
                    "baseline_value": "implicit shared hysteresis",
                    "release_zero_value": 0,
                },
            },
            "subject": {
                "symbol": carrier_base.SYMBOL,
                "timeframe": carrier_base.TIMEFRAME,
                "start": START,
                "end": END,
                "warmup": carrier_base.WARMUP,
                "data_source_policy": carrier_base.DATA_SOURCE_POLICY,
            },
        },
    }


def run_annual_2024_contribution() -> dict[str, Any]:
    carrier_base.START = START
    carrier_base.END = END

    base_cfg, carrier_cfg, authority = carrier_base._load_base_and_carrier_cfg()
    baseline = carrier_base._run_case(
        "baseline", base_cfg=base_cfg, carrier_cfg=carrier_cfg, authority=authority
    )
    release_zero = carrier_base._run_case(
        "release_zero", base_cfg=base_cfg, carrier_cfg=carrier_cfg, authority=authority
    )

    baseline_rows = baseline.pop("rows")
    release_zero_rows = release_zero.pop("rows")
    baseline_release_rows = baseline.pop("continuation_release_rows")
    release_zero_release_rows = release_zero.pop("continuation_release_rows")

    diffs: list[dict[str, Any]] = []
    action_diff_count = 0
    reason_only_diff_count = 0
    continuation_release_diff_count = 0
    behavioral_row_diff_count = 0
    parameter_only_diff_count = 0

    for ts in sorted(set(baseline_rows) | set(release_zero_rows)):
        baseline_row = baseline_rows.get(ts)
        release_zero_row = release_zero_rows.get(ts)
        if baseline_row == release_zero_row:
            continue
        action_changed = (baseline_row or {}).get("action") != (release_zero_row or {}).get(
            "action"
        )
        if action_changed:
            action_diff_count += 1
        else:
            reason_only_diff_count += 1

        baseline_debug = (baseline_row or {}).get("router_debug") or {}
        release_zero_debug = (release_zero_row or {}).get("router_debug") or {}
        continuation_release_involved = (
            baseline_debug.get("switch_control_mode") == "continuation_release"
            or release_zero_debug.get("switch_control_mode") == "continuation_release"
        )
        if continuation_release_involved:
            continuation_release_diff_count += 1

        behavior_changed = carrier_base._behavior_row(baseline_row) != carrier_base._behavior_row(
            release_zero_row
        )
        if behavior_changed:
            behavioral_row_diff_count += 1
        else:
            parameter_only_diff_count += 1

        if len(diffs) < carrier_base.REPRESENTATIVE_LIMIT:
            diffs.append(
                {
                    "timestamp": ts,
                    "action_changed": action_changed,
                    "behavior_changed": behavior_changed,
                    "continuation_release_involved": continuation_release_involved,
                    "baseline": baseline_row,
                    "release_zero": release_zero_row,
                }
            )

    baseline_summary = dict(baseline.get("summary") or {})
    release_zero_summary = dict(release_zero.get("summary") or {})
    baseline_position_summary = dict(baseline.get("position_summary") or {})
    release_zero_position_summary = dict(release_zero.get("position_summary") or {})
    packet_summary = _packet_summary(
        baseline_summary=baseline_summary,
        release_zero_summary=release_zero_summary,
        baseline_position_summary=baseline_position_summary,
        release_zero_position_summary=release_zero_position_summary,
        all_row_diff_count=len(sorted(set(baseline_rows) | set(release_zero_rows)))
        - len(
            [
                ts
                for ts in sorted(set(baseline_rows) | set(release_zero_rows))
                if baseline_rows.get(ts) == release_zero_rows.get(ts)
            ]
        ),
        action_diff_count=action_diff_count,
        behavioral_row_diff_count=behavioral_row_diff_count,
        continuation_release_diff_count=continuation_release_diff_count,
    )

    return {
        "audit_version": "ri-policy-router-continuation-release-hysteresis-annual-2024-contribution-2026-05-26",
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
                "fixed full-year 2024 same-stack comparison on the landed continuation_release_hysteresis carrier, "
                "holding the active router stack constant while toggling only continuation_release_hysteresis"
            ),
            "question": (
                "On the fixed 2024 annual surface, does continuation_release_hysteresis contribute positively, "
                "negatively, or only through compensated row changes when compared as baseline vs release_zero under "
                "the same active stack?"
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
            "subject": {
                "symbol": carrier_base.SYMBOL,
                "timeframe": carrier_base.TIMEFRAME,
                "start": START,
                "end": END,
                "warmup": carrier_base.WARMUP,
                "data_source_policy": carrier_base.DATA_SOURCE_POLICY,
            },
        },
        "baseline": baseline,
        "release_zero": release_zero,
        "comparison": {
            "all_row_diff_count": packet_summary["all_row_diff_count"],
            "action_diff_count": action_diff_count,
            "reason_only_diff_count": reason_only_diff_count,
            "behavioral_row_diff_count": behavioral_row_diff_count,
            "parameter_only_diff_count": parameter_only_diff_count,
            "continuation_release_row_count_baseline": len(baseline_release_rows),
            "continuation_release_row_count_release_zero": len(release_zero_release_rows),
            "continuation_release_diff_count": continuation_release_diff_count,
            "representative_diffs": diffs,
            "representative_continuation_release_rows": carrier_base._representative_release_rows(
                baseline_release_rows,
                release_zero_release_rows,
            ),
        },
        "packet_summary": packet_summary,
    }


def main() -> int:
    output_root = ROOT_DIR / OUTPUT_ROOT_RELATIVE
    output_json = output_root / OUTPUT_FILENAME
    try:
        result = run_annual_2024_contribution()
    except Exception as exc:  # fail-closed research wrapper
        result = _build_fail_closed_result(str(exc))

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    packet_summary = result.get("packet_summary") or {}
    summary = {
        "summary_artifact": str(output_json),
        "status": packet_summary.get("status", result.get("status")),
        "total_return_diff": packet_summary.get("total_return_diff"),
        "final_capital_diff": packet_summary.get("final_capital_diff"),
        "profit_factor_diff": packet_summary.get("profit_factor_diff"),
        "max_drawdown_pct_diff": packet_summary.get("max_drawdown_pct_diff"),
        "all_row_diff_count": packet_summary.get("all_row_diff_count"),
        "action_diff_count": packet_summary.get("action_diff_count"),
        "continuation_release_diff_count": packet_summary.get("continuation_release_diff_count"),
        "failure_reason": result.get("failure_reason"),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
