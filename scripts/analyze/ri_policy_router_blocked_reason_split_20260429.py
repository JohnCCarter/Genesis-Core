from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Callable
from pathlib import Path
from statistics import fmean, median
from typing import Any

import pandas as pd

CURATED_SUMMARY_RELATIVE = Path(
    "results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/"
    "enabled_vs_absent_all_years_summary.json"
)
CURATED_CANDLES_RELATIVE = Path("data/curated/v1/candles/tBTCUSD_3h.parquet")
OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = "ri_policy_router_blocked_reason_split_2026-04-29.json"
FORWARD_HORIZONS = (4, 8, 16)
EXCURSION_HORIZON = 16
SUBJECT_SYMBOL = "tBTCUSD"
SUBJECT_TIMEFRAME = "3h"


def _find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "pyproject.toml").exists() and (candidate / "src").exists():
            return candidate
    raise RuntimeError("Could not locate repository root from helper path")


ROOT_DIR = _find_repo_root(Path(__file__).resolve())
CURATED_SUMMARY_PATH = ROOT_DIR / CURATED_SUMMARY_RELATIVE
CURATED_CANDLES_PATH = ROOT_DIR / CURATED_CANDLES_RELATIVE


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Split blocked baseline-long rows by switch reason across positive and negative curated years."
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
        help="Repo-relative output directory for the emitted summary artifact.",
    )
    parser.add_argument(
        "--summary-filename",
        default=OUTPUT_FILENAME,
        help="Filename to use for the emitted JSON summary.",
    )
    return parser.parse_args()


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _negative_full_years(summary_payload: dict[str, Any]) -> list[str]:
    years: list[str] = []
    for year, payload in (summary_payload.get("years") or {}).items():
        window = payload.get("window") or {}
        comparison = payload.get("comparison") or {}
        if window.get("partial_year"):
            continue
        enabled_return = comparison.get("enabled_total_return_pct")
        absent_return = comparison.get("absent_total_return_pct")
        enabled_pf = comparison.get("enabled_profit_factor")
        absent_pf = comparison.get("absent_profit_factor")
        enabled_dd = comparison.get("enabled_max_drawdown_pct")
        absent_dd = comparison.get("absent_max_drawdown_pct")
        enabled_net = comparison.get("enabled_position_net_pnl")
        absent_net = comparison.get("absent_position_net_pnl")
        if any(
            value is None
            for value in (
                enabled_return,
                absent_return,
                enabled_pf,
                absent_pf,
                enabled_dd,
                absent_dd,
                enabled_net,
                absent_net,
            )
        ):
            continue
        if (
            enabled_return < absent_return
            and enabled_pf < absent_pf
            and enabled_dd > absent_dd
            and enabled_net < absent_net
        ):
            years.append(str(year))
    return sorted(years)


def _positive_full_years(summary_payload: dict[str, Any]) -> list[str]:
    years: list[str] = []
    for year, payload in (summary_payload.get("years") or {}).items():
        window = payload.get("window") or {}
        comparison = payload.get("comparison") or {}
        if window.get("partial_year"):
            continue
        enabled_return = comparison.get("enabled_total_return_pct")
        absent_return = comparison.get("absent_total_return_pct")
        enabled_pf = comparison.get("enabled_profit_factor")
        absent_pf = comparison.get("absent_profit_factor")
        enabled_dd = comparison.get("enabled_max_drawdown_pct")
        absent_dd = comparison.get("absent_max_drawdown_pct")
        enabled_net = comparison.get("enabled_position_net_pnl")
        absent_net = comparison.get("absent_position_net_pnl")
        if any(
            value is None
            for value in (
                enabled_return,
                absent_return,
                enabled_pf,
                absent_pf,
                enabled_dd,
                absent_dd,
                enabled_net,
                absent_net,
            )
        ):
            continue
        if (
            enabled_return > absent_return
            and enabled_pf > absent_pf
            and enabled_dd < absent_dd
            and enabled_net > absent_net
        ):
            years.append(str(year))
    return sorted(years)


def _normalize_timestamp(value: Any) -> pd.Timestamp:
    timestamp = pd.Timestamp(value)
    if timestamp.tzinfo is None:
        return timestamp.tz_localize("UTC")
    return timestamp.tz_convert("UTC")


def _load_candles(path: Path) -> tuple[pd.DataFrame, dict[pd.Timestamp, int]]:
    candles = pd.read_parquet(path)
    required_columns = {"timestamp", "open", "close", "high", "low", "volume"}
    missing = sorted(required_columns - set(candles.columns))
    if missing:
        raise SystemExit(f"Missing candle columns in {path}: {missing}")

    frame = candles.loc[:, ["timestamp", "open", "close", "high", "low", "volume"]].copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
    frame = frame.sort_values("timestamp").reset_index(drop=True)
    if frame["timestamp"].duplicated().any():
        raise SystemExit(f"Duplicate timestamps detected in {path}")

    timestamp_to_index = {
        _normalize_timestamp(timestamp): int(index)
        for index, timestamp in enumerate(frame["timestamp"].tolist())
    }
    return frame, timestamp_to_index


def _pct_change(entry_price: float, exit_price: float) -> float:
    return ((exit_price - entry_price) / entry_price) * 100.0


def _row_observational_metrics(
    *,
    timestamp: str,
    candles: pd.DataFrame,
    timestamp_to_index: dict[pd.Timestamp, int],
) -> dict[str, float | int | None]:
    normalized_timestamp = _normalize_timestamp(timestamp)
    index = timestamp_to_index.get(normalized_timestamp)
    if index is None:
        raise SystemExit(f"Timestamp {timestamp} was not found in curated candles")

    entry_close = float(candles.at[index, "close"])
    metrics: dict[str, float | int | None] = {
        "entry_close": entry_close,
        "matched_candle_index": index,
    }

    for horizon in FORWARD_HORIZONS:
        future_index = index + horizon
        metric_key = f"fwd_{horizon}_close_return_pct"
        if future_index >= len(candles):
            metrics[metric_key] = None
            continue
        future_close = float(candles.at[future_index, "close"])
        metrics[metric_key] = _pct_change(entry_close, future_close)

    excursion_start = index + 1
    excursion_end = min(index + EXCURSION_HORIZON, len(candles) - 1)
    if excursion_start > excursion_end:
        metrics["mfe_16_pct"] = None
        metrics["mae_16_pct"] = None
        metrics["future_bars_available"] = 0
        return metrics

    future_high = float(candles.loc[excursion_start:excursion_end, "high"].max())
    future_low = float(candles.loc[excursion_start:excursion_end, "low"].min())
    metrics["mfe_16_pct"] = _pct_change(entry_close, future_high)
    metrics["mae_16_pct"] = _pct_change(entry_close, future_low)
    metrics["future_bars_available"] = excursion_end - excursion_start + 1
    return metrics


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


def _common_router_debug(row: dict[str, Any]) -> dict[str, Any] | None:
    enabled = row.get("enabled") or {}
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
    return router_debug


def _is_blocked_baseline_long(row: dict[str, Any]) -> bool:
    router_debug = _common_router_debug(row)
    if router_debug is None:
        return False

    enabled = row.get("enabled") or {}
    absent = row.get("absent") or {}
    if (absent.get("action") or "NONE") != "LONG":
        return False
    if (enabled.get("action") or "NONE") != "NONE":
        return False
    return True


Matcher = Callable[[dict[str, Any]], bool]


def _collect_rows(
    *,
    years: list[str],
    matcher: Matcher,
    candles: pd.DataFrame,
    timestamp_to_index: dict[pd.Timestamp, int],
) -> list[dict[str, Any]]:
    collected: list[dict[str, Any]] = []
    for year in years:
        diff_path = CURATED_SUMMARY_PATH.parent / f"{year}_enabled_vs_absent_action_diffs.json"
        diff_rows = _load_json(diff_path)
        if not isinstance(diff_rows, list):
            raise SystemExit(f"Expected diff row list in {diff_path}")

        for row in diff_rows:
            if not isinstance(row, dict) or not matcher(row):
                continue
            enabled = row.get("enabled") or {}
            router_debug = enabled.get("router_debug") or {}
            timestamp = row.get("timestamp")
            if not isinstance(timestamp, str):
                raise SystemExit(f"Row without string timestamp in {diff_path}")
            metrics = _row_observational_metrics(
                timestamp=timestamp,
                candles=candles,
                timestamp_to_index=timestamp_to_index,
            )
            collected.append(
                {
                    "year": year,
                    "timestamp": timestamp,
                    "switch_reason": router_debug.get("switch_reason") or "unknown",
                    "raw_target_policy": router_debug.get("raw_target_policy") or "unknown",
                    "previous_policy": router_debug.get("previous_policy") or "unknown",
                    "bars_since_regime_change": router_debug.get("bars_since_regime_change"),
                    "action_edge": router_debug.get("action_edge"),
                    "confidence_gate": router_debug.get("confidence_gate"),
                    "clarity_score": router_debug.get("clarity_score"),
                    **metrics,
                }
            )
    return collected


def _sample_rows(rows: list[dict[str, Any]], *, limit: int = 5) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    for row in sorted(rows, key=lambda item: (item["year"], item["timestamp"]))[:limit]:
        samples.append(
            {
                "year": row["year"],
                "timestamp": row["timestamp"],
                "switch_reason": row["switch_reason"],
                "raw_target_policy": row["raw_target_policy"],
                "previous_policy": row["previous_policy"],
                "bars_since_regime_change": row["bars_since_regime_change"],
                "action_edge": row["action_edge"],
                "confidence_gate": row["confidence_gate"],
                "clarity_score": row["clarity_score"],
                "fwd_4_close_return_pct": row.get("fwd_4_close_return_pct"),
                "fwd_8_close_return_pct": row.get("fwd_8_close_return_pct"),
                "fwd_16_close_return_pct": row.get("fwd_16_close_return_pct"),
                "mfe_16_pct": row.get("mfe_16_pct"),
                "mae_16_pct": row.get("mae_16_pct"),
            }
        )
    return samples


def _summarize_reason_rows(
    reason: str, rows: list[dict[str, Any]], group_total: int
) -> dict[str, Any]:
    year_counter = Counter(row["year"] for row in rows)
    raw_target_counter = Counter(row["raw_target_policy"] for row in rows)
    previous_policy_counter = Counter(row["previous_policy"] for row in rows)
    metrics = {
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
    bars_values = [
        int(row["bars_since_regime_change"])
        for row in rows
        if isinstance(row.get("bars_since_regime_change"), int)
    ]
    return {
        "switch_reason": reason,
        "row_count": len(rows),
        "share_of_group": _round_or_none(len(rows) / group_total if group_total else None),
        "year_counts": [
            {"year": year, "count": count} for year, count in sorted(year_counter.items())
        ],
        "raw_target_policy_counts": [
            {"raw_target_policy": key, "count": count}
            for key, count in raw_target_counter.most_common()
        ],
        "previous_policy_counts": [
            {"previous_policy": key, "count": count}
            for key, count in previous_policy_counter.most_common()
        ],
        "bars_since_regime_change": {
            "min": min(bars_values) if bars_values else None,
            "median": (
                _round_or_none(median([float(value) for value in bars_values]))
                if bars_values
                else None
            ),
            "mean": (
                _round_or_none(fmean([float(value) for value in bars_values]))
                if bars_values
                else None
            ),
            "max": max(bars_values) if bars_values else None,
        },
        "metric_summary": metrics,
        "sample_rows": _sample_rows(rows),
    }


def _summarize_group(rows: list[dict[str, Any]]) -> dict[str, Any]:
    reason_counter = Counter(row["switch_reason"] for row in rows)
    grouped_rows: dict[str, list[dict[str, Any]]] = {}
    for reason in sorted(reason_counter):
        grouped_rows[reason] = [row for row in rows if row["switch_reason"] == reason]

    reason_summaries = [
        _summarize_reason_rows(reason, grouped_rows[reason], len(rows))
        for reason, _count in reason_counter.most_common()
    ]

    return {
        "blocked_row_count": len(rows),
        "switch_reason_counts": [
            {"switch_reason": reason, "count": count}
            for reason, count in reason_counter.most_common()
        ],
        "reasons": reason_summaries,
    }


def _build_shared_reason_comparison(
    negative_rows: list[dict[str, Any]], positive_rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    negative_by_reason = Counter(row["switch_reason"] for row in negative_rows)
    positive_by_reason = Counter(row["switch_reason"] for row in positive_rows)
    shared_reasons = sorted(set(negative_by_reason) & set(positive_by_reason))

    comparisons: list[dict[str, Any]] = []
    for reason in shared_reasons:
        neg_reason_rows = [row for row in negative_rows if row["switch_reason"] == reason]
        pos_reason_rows = [row for row in positive_rows if row["switch_reason"] == reason]
        neg_fwd16 = [
            float(row["fwd_16_close_return_pct"])
            for row in neg_reason_rows
            if isinstance(row.get("fwd_16_close_return_pct"), int | float)
        ]
        pos_fwd16 = [
            float(row["fwd_16_close_return_pct"])
            for row in pos_reason_rows
            if isinstance(row.get("fwd_16_close_return_pct"), int | float)
        ]
        comparisons.append(
            {
                "switch_reason": reason,
                "negative_row_count": len(neg_reason_rows),
                "positive_row_count": len(pos_reason_rows),
                "negative_fwd_16_mean": _round_or_none(fmean(neg_fwd16)) if neg_fwd16 else None,
                "positive_fwd_16_mean": _round_or_none(fmean(pos_fwd16)) if pos_fwd16 else None,
                "negative_fwd_16_median": _round_or_none(median(neg_fwd16)) if neg_fwd16 else None,
                "positive_fwd_16_median": _round_or_none(median(pos_fwd16)) if pos_fwd16 else None,
                "fwd_16_mean_gap_negative_minus_positive": _round_or_none(
                    (fmean(neg_fwd16) - fmean(pos_fwd16)) if neg_fwd16 and pos_fwd16 else None
                ),
                "fwd_16_median_gap_negative_minus_positive": _round_or_none(
                    (median(neg_fwd16) - median(pos_fwd16)) if neg_fwd16 and pos_fwd16 else None
                ),
            }
        )
    comparisons.sort(
        key=lambda item: (
            -(item["negative_row_count"] + item["positive_row_count"]),
            item["switch_reason"],
        )
    )
    return comparisons


def main() -> int:
    args = _parse_args()
    summary_payload = _load_json(CURATED_SUMMARY_PATH)
    candles, timestamp_to_index = _load_candles(CURATED_CANDLES_PATH)

    negative_years = _negative_full_years(summary_payload)
    positive_years = _positive_full_years(summary_payload)
    output_root = ROOT_DIR / Path(args.output_root_relative)
    output_json = output_root / args.summary_filename

    negative_rows = _collect_rows(
        years=negative_years,
        matcher=_is_blocked_baseline_long,
        candles=candles,
        timestamp_to_index=timestamp_to_index,
    )
    positive_rows = _collect_rows(
        years=positive_years,
        matcher=_is_blocked_baseline_long,
        candles=candles,
        timestamp_to_index=timestamp_to_index,
    )

    result = {
        "audit_version": "ri-policy-router-blocked-reason-split-2026-04-29",
        "base_sha": args.base_sha,
        "status": "blocked-reason-split-generated",
        "observational_only": True,
        "non_authoritative": True,
        "subject": {"symbol": SUBJECT_SYMBOL, "timeframe": SUBJECT_TIMEFRAME},
        "skill_usage": ["decision_gate_debug", "python_engineering"],
        "cohort_definition": {
            "statement": (
                "Blocked baseline-long rows where absent action is LONG, enabled action is NONE, zone is low, candidate is LONG, and bars_since_regime_change >= 8 on the curated annual enabled-vs-absent action-diff surface."
            )
        },
        "proxy_boundary": {
            "statement": (
                "This slice uses timestamp-close observational proxies only. Reported differences are descriptive, not authoritative, and do not equal realized trade PnL, fill-aware MFE/MAE, one-to-one row pairing, or runtime-authoritative row truth."
            )
        },
        "parse_only_constraint": {
            "statement": (
                "The helper reads existing JSON and parquet inputs only. It does not import from src/**, rerun backtests, regenerate upstream diff artifacts, or modify runtime/default authority surfaces."
            )
        },
        "inputs": {
            "curated_summary": str(CURATED_SUMMARY_RELATIVE),
            "curated_candles": str(CURATED_CANDLES_RELATIVE),
            "action_diff_root": str(CURATED_SUMMARY_RELATIVE.parent),
        },
        "year_groups": {
            "negative_full_years": negative_years,
            "positive_full_years": positive_years,
        },
        "groups": {
            "negative_full_years": _summarize_group(negative_rows),
            "positive_full_years": _summarize_group(positive_rows),
        },
        "shared_reason_comparison": _build_shared_reason_comparison(negative_rows, positive_rows),
    }

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "summary_artifact": str(output_json),
                "negative_rows": len(negative_rows),
                "positive_rows": len(positive_rows),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
