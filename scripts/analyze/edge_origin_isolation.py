"""Read-only Phase 10 edge-origin isolation analysis.

This module analyzes locked trace artifacts without touching runtime strategy code.
It builds packet-authorized execution, sizing, path, selection, counterfactual,
and determinism outputs from already-produced trace payloads.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import statistics
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_SEED = 20260402
DEFAULT_SHUFFLE_ITERATIONS = 5000
OUTPUT_FILES = (
    "execution_attribution.json",
    "execution_summary.md",
    "sizing_attribution.json",
    "sizing_summary.md",
    "path_dependency.json",
    "path_summary.md",
    "selection_attribution.json",
    "selection_summary.md",
    "counterfactual_matrix.json",
)


class EdgeOriginIsolationError(RuntimeError):
    """Raised when packet-authorized edge-origin analysis cannot be attested."""


@dataclass(frozen=True)
class TradeSignature:
    entry_timestamp: str
    exit_timestamp: str
    side: str
    size: float
    pnl: float


@dataclass(frozen=True)
class JoinedTrade:
    trade: TradeSignature
    entry_row: dict[str, Any]
    exit_row: dict[str, Any] | None
    normalized_entry_timestamp: str
    normalized_exit_timestamp: str
    outcome: str
    unit_pnl: float


def normalize_timestamp(timestamp: str) -> str:
    """Normalize artifact timestamps per packet contract."""

    if not isinstance(timestamp, str) or not timestamp:
        raise EdgeOriginIsolationError("timestamp must be a non-empty string")
    return timestamp[:-6] if timestamp.endswith("+00:00") else timestamp


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _require_dict(value: Any, *, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise EdgeOriginIsolationError(f"{context} must be an object")
    return value


def _require_list(value: Any, *, context: str) -> list[Any]:
    if not isinstance(value, list):
        raise EdgeOriginIsolationError(f"{context} must be an array")
    return value


def _nested_get(mapping: dict[str, Any], path: str) -> Any:
    current: Any = mapping
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            raise EdgeOriginIsolationError(f"Missing required field: {path}")
        current = current[part]
    return current


def _require_number(mapping: dict[str, Any], path: str) -> float:
    value = _nested_get(mapping, path)
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise EdgeOriginIsolationError(f"Field must be numeric: {path}")
    out = float(value)
    if out != out or out in {float("inf"), float("-inf")}:
        raise EdgeOriginIsolationError(f"Field must be finite: {path}")
    return out


def _require_text(mapping: dict[str, Any], path: str) -> str:
    value = _nested_get(mapping, path)
    if not isinstance(value, str) or not value:
        raise EdgeOriginIsolationError(f"Field must be a non-empty string: {path}")
    return value


def _mean(values: list[float]) -> float:
    if not values:
        raise EdgeOriginIsolationError("values must not be empty")
    return float(statistics.fmean(values))


def _median(values: list[float]) -> float:
    if not values:
        raise EdgeOriginIsolationError("values must not be empty")
    return float(statistics.median(values))


def _profit_factor(pnls: list[float]) -> tuple[float | None, str]:
    gross_profit = sum(p for p in pnls if p > 0)
    gross_loss = abs(sum(p for p in pnls if p < 0))
    if gross_loss == 0:
        return None, "NO_LOSS_DENOMINATOR"
    return float(gross_profit / gross_loss), "FINITE"


def _win_rate(pnls: list[float]) -> float:
    return float(sum(1 for p in pnls if p > 0) / len(pnls))


def _compute_path_metrics(pnls: list[float]) -> dict[str, float | int]:
    cumulative = 0.0
    peak = 0.0
    max_drawdown = 0.0
    underwater = 0
    longest_loss_streak = 0
    longest_win_streak = 0
    current_loss_streak = 0
    current_win_streak = 0

    for pnl in pnls:
        cumulative += pnl
        if cumulative > peak:
            peak = cumulative
        drawdown = peak - cumulative
        if drawdown > max_drawdown:
            max_drawdown = drawdown
        if cumulative < peak:
            underwater += 1

        if pnl < 0:
            current_loss_streak += 1
            current_win_streak = 0
        else:
            current_win_streak += 1
            current_loss_streak = 0
        longest_loss_streak = max(longest_loss_streak, current_loss_streak)
        longest_win_streak = max(longest_win_streak, current_win_streak)

    return {
        "final_cumulative_pnl": round(float(cumulative), 12),
        "max_drawdown": round(float(max_drawdown), 12),
        "longest_loss_streak": int(longest_loss_streak),
        "longest_win_streak": int(longest_win_streak),
        "time_under_water_in_trades": int(underwater),
    }


def _empirical_p_value(actual_value: float, distribution: list[float]) -> tuple[float, float]:
    if not distribution:
        raise EdgeOriginIsolationError("distribution must not be empty")
    median_value = _median(distribution)
    actual_distance = abs(actual_value - median_value)
    extreme_count = sum(1 for value in distribution if abs(value - median_value) >= actual_distance)
    return float((extreme_count + 1) / (len(distribution) + 1)), float(median_value)


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise EdgeOriginIsolationError(f"Missing input file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise EdgeOriginIsolationError(f"Invalid JSON in {path}: {exc}") from exc
    return _require_dict(payload, context=f"payload:{path}")


def _load_trade_signatures(payload: dict[str, Any]) -> list[TradeSignature]:
    rows = _require_list(payload.get("trade_signatures"), context="trade_signatures")
    trades: list[TradeSignature] = []
    for idx, row in enumerate(rows):
        item = _require_dict(row, context=f"trade_signatures[{idx}]")
        size = _require_number(item, "size")
        pnl = _require_number(item, "pnl")
        trades.append(
            TradeSignature(
                entry_timestamp=_require_text(item, "entry_timestamp"),
                exit_timestamp=_require_text(item, "exit_timestamp"),
                side=_require_text(item, "side"),
                size=size,
                pnl=pnl,
            )
        )
    return trades


def _eligible_rows_by_timestamp(
    trace_rows: list[dict[str, Any]]
) -> tuple[dict[str, dict[str, Any]], int]:
    bucket: dict[str, list[dict[str, Any]]] = {}
    for row in trace_rows:
        if row.get("sizing_phase") is None:
            continue
        normalized = normalize_timestamp(_require_text(row, "timestamp"))
        bucket.setdefault(normalized, []).append(row)

    duplicate_count = sum(max(0, len(rows) - 1) for rows in bucket.values())
    if duplicate_count:
        raise EdgeOriginIsolationError("duplicate normalized baseline trace timestamps detected")
    return {key: rows[0] for key, rows in bucket.items()}, duplicate_count


def _all_rows_by_timestamp(trace_rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    bucket: dict[str, list[dict[str, Any]]] = {}
    for row in trace_rows:
        normalized = normalize_timestamp(_require_text(row, "timestamp"))
        bucket.setdefault(normalized, []).append(row)
    return bucket


def _outcome_class(pnl: float) -> str:
    if pnl > 0:
        return "WIN"
    if pnl < 0:
        return "LOSS"
    raise EdgeOriginIsolationError("FLAT trades are forbidden by the packet")


def join_baseline_trades(payload: dict[str, Any]) -> tuple[list[JoinedTrade], dict[str, Any]]:
    payload_name = payload.get("name")
    if payload_name is not None and payload_name != "baseline_current":
        raise EdgeOriginIsolationError("baseline payload name must be baseline_current")

    trades = _load_trade_signatures(payload)
    trace_rows = [
        _require_dict(row, context=f"trace_rows[{idx}]")
        for idx, row in enumerate(_require_list(payload.get("trace_rows"), context="trace_rows"))
    ]

    eligible_rows, duplicate_trace_count = _eligible_rows_by_timestamp(trace_rows)
    all_rows = _all_rows_by_timestamp(trace_rows)
    entry_counts = Counter(normalize_timestamp(trade.entry_timestamp) for trade in trades)

    joined: list[JoinedTrade] = []
    unmatched = 0
    exit_row_attested = True

    for trade in trades:
        normalized_entry = normalize_timestamp(trade.entry_timestamp)
        entry_row = eligible_rows.get(normalized_entry)
        if entry_row is None:
            unmatched += 1
            continue

        normalized_exit = normalize_timestamp(trade.exit_timestamp)
        exit_candidates = all_rows.get(normalized_exit, [])
        exit_row = exit_candidates[0] if len(exit_candidates) == 1 else None
        if exit_row is None:
            exit_row_attested = False

        if trade.size <= 0:
            raise EdgeOriginIsolationError("trade size must be > 0 for sizing attribution")
        outcome = _outcome_class(trade.pnl)
        joined.append(
            JoinedTrade(
                trade=trade,
                entry_row=entry_row,
                exit_row=exit_row,
                normalized_entry_timestamp=normalized_entry,
                normalized_exit_timestamp=normalized_exit,
                outcome=outcome,
                unit_pnl=float(trade.pnl / trade.size),
            )
        )

    join_status = (
        "EXACT_ONE_MATCH_PER_TRADE"
        if len(joined) == len(trades) and unmatched == 0 and duplicate_trace_count == 0
        else "FAIL"
    )
    if join_status != "EXACT_ONE_MATCH_PER_TRADE":
        raise EdgeOriginIsolationError("baseline trades did not join exactly once to entry rows")

    return joined, {
        "baseline_trade_count_raw": len(trades),
        "matched_trade_count": len(joined),
        "unmatched_trade_count": unmatched,
        "duplicate_trade_entry_timestamp_count": sum(
            max(0, count - 1) for count in entry_counts.values()
        ),
        "duplicate_normalized_trace_timestamp_count": duplicate_trace_count,
        "join_status": join_status,
        "exit_row_resolution_status": (
            "ATTESTED" if exit_row_attested else "OMITTED_EXIT_ROW_UNATTESTED"
        ),
    }


def _analysis_population(join_integrity: dict[str, Any]) -> dict[str, Any]:
    return {
        "baseline_trade_count_raw": join_integrity["baseline_trade_count_raw"],
        "matched_trade_count": join_integrity["matched_trade_count"],
        "binary_trade_count": join_integrity["matched_trade_count"],
        "join_status": join_integrity["join_status"],
        "exit_row_resolution_status": join_integrity["exit_row_resolution_status"],
    }


def _build_execution_attribution(
    joined_trades: list[JoinedTrade],
    join_integrity: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    pnls = [trade.trade.pnl for trade in joined_trades]
    profit_factor, profit_factor_status = _profit_factor(pnls)
    baseline_metrics: dict[str, Any] = {
        "trade_count": len(joined_trades),
        "profit_factor": profit_factor,
        "profit_factor_status": profit_factor_status,
        "expectancy": round(_mean(pnls), 12),
        "win_rate": round(_win_rate(pnls), 12),
    }

    authorized_subtests = [
        {"name": "baseline_realized_metrics", "status": "PASS"},
        {"name": "holding_period_bars", "status": "PASS"},
    ]
    omitted_subtests = [
        {"name": "MAE_MFE", "reason": "OMITTED_LIMITED_ARTIFACT_SURFACE"},
        {"name": "price_path_fixed_exit", "reason": "OMITTED_LIMITED_ARTIFACT_SURFACE"},
        {"name": "deterministic_entry_shift", "reason": "OMITTED_LIMITED_ARTIFACT_SURFACE"},
        {"name": "fixed_horizon_exit_k_bars", "reason": "OMITTED_LIMITED_ARTIFACT_SURFACE"},
    ]

    if join_integrity["exit_row_resolution_status"] == "ATTESTED":
        holding_periods = [
            max(
                0,
                int(
                    _nested_get(trade.exit_row or {}, "bar_index")
                    - _nested_get(trade.entry_row, "bar_index")
                ),
            )
            for trade in joined_trades
        ]
        baseline_metrics["holding_period_bars"] = {
            "count": len(holding_periods),
            "mean": round(_mean([float(v) for v in holding_periods]), 12),
            "median": round(_median([float(v) for v in holding_periods]), 12),
            "min": int(min(holding_periods)),
            "max": int(max(holding_periods)),
        }
    else:
        baseline_metrics["holding_period_bars"] = None
        authorized_subtests[1]["status"] = "OMITTED_EXIT_ROW_UNATTESTED"

    execution = {
        "analysis_status": "LIMITED_ARTIFACT_SURFACE",
        "analysis_population": _analysis_population(join_integrity),
        "baseline_metrics": baseline_metrics,
        "authorized_subtests": authorized_subtests,
        "omitted_subtests": omitted_subtests,
        "execution_conclusion": (
            "Execution attribution remains observational-only on the realized baseline ledger; "
            "path-dependent and intratrade controls remain omitted on the limited artifact surface."
        ),
    }

    summary_lines = [
        "# Execution attribution",
        "",
        "Execution attribution is observational only and does not modify strategy logic.",
        f"- realized trade_count: `{baseline_metrics['trade_count']}`",
        f"- profit_factor: `{baseline_metrics['profit_factor']}` ({baseline_metrics['profit_factor_status']})",
        f"- expectancy: `{baseline_metrics['expectancy']}`",
        f"- win_rate: `{baseline_metrics['win_rate']}`",
        f"- analysis_status: `{execution['analysis_status']}`",
        "- executed execution subtests: `baseline_realized_metrics`, `holding_period_bars`",
        "- omitted execution subtests: `MAE_MFE`, `price_path_fixed_exit`, `deterministic_entry_shift`, `fixed_horizon_exit_k_bars`",
        "- conclusion: limited artifact surface supports descriptive execution attribution only.",
    ]
    return execution, "\n".join(summary_lines)


def _extract_sizing_snapshot(entry_row: dict[str, Any]) -> dict[str, Any]:
    required_numeric = (
        "sizing_phase.base_size",
        "sizing_phase.size_scale",
        "sizing_phase.volatility_adjustment",
        "sizing_phase.regime_multiplier",
        "sizing_phase.htf_regime_multiplier",
        "sizing_phase.combined_multiplier",
        "sizing_phase.final_size",
        "decision_phase.p_buy",
        "decision_phase.p_sell",
        "decision_phase.ev_long",
        "decision_phase.ev_short",
        "decision_phase.max_ev",
        "fib_phase.ltf_debug.price",
        "fib_phase.ltf_debug.atr",
        "fib_phase.ltf_debug.tolerance",
    )
    snapshot = {path.split(".")[-1]: _require_number(entry_row, path) for path in required_numeric}
    snapshot["selected_candidate"] = _require_text(entry_row, "decision_phase.selected_candidate")
    snapshot["candidate"] = _require_text(entry_row, "sizing_phase.candidate")
    snapshot["final_action"] = _require_text(entry_row, "final.action")
    snapshot["final_regime"] = _require_text(entry_row, "final.regime")
    snapshot["final_htf_regime"] = _require_text(entry_row, "final.htf_regime")
    snapshot["zone"] = _require_text(entry_row, "final.zone_debug.zone")
    snapshot["zone_atr"] = _require_number(entry_row, "final.zone_debug.atr")
    snapshot["reasons"] = list(_nested_get(entry_row, "final.reasons"))
    return snapshot


def _build_sizing_attribution(
    joined_trades: list[JoinedTrade], join_integrity: dict[str, Any]
) -> tuple[dict[str, Any], str]:
    pnls = [trade.trade.pnl for trade in joined_trades]
    unit_pnls = [trade.unit_pnl for trade in joined_trades]
    baseline_profit_factor, baseline_pf_status = _profit_factor(pnls)
    unit_profit_factor, unit_pf_status = _profit_factor(unit_pnls)
    snapshots = [_extract_sizing_snapshot(trade.entry_row) for trade in joined_trades]

    baseline_metrics = {
        "trade_count": len(joined_trades),
        "profit_factor": baseline_profit_factor,
        "profit_factor_status": baseline_pf_status,
        "expectancy": round(_mean(pnls), 12),
        "win_rate": round(_win_rate(pnls), 12),
    }
    unit_metrics = {
        "trade_count": len(joined_trades),
        "profit_factor": unit_profit_factor,
        "profit_factor_status": unit_pf_status,
        "expectancy": round(_mean(unit_pnls), 12),
        "win_rate": round(_win_rate(unit_pnls), 12),
    }
    deltas = {
        "expectancy_delta_actual_minus_unit": round(
            baseline_metrics["expectancy"] - unit_metrics["expectancy"], 12
        ),
        "profit_factor_delta_actual_minus_unit": (
            None
            if baseline_metrics["profit_factor"] is None or unit_metrics["profit_factor"] is None
            else round(float(baseline_metrics["profit_factor"] - unit_metrics["profit_factor"]), 12)
        ),
        "win_rate_delta_actual_minus_unit": round(
            baseline_metrics["win_rate"] - unit_metrics["win_rate"], 12
        ),
    }
    sizing_surface_summary = {
        "mean_base_size": round(_mean([float(item["base_size"]) for item in snapshots]), 12),
        "mean_size_scale": round(_mean([float(item["size_scale"]) for item in snapshots]), 12),
        "mean_volatility_adjustment": round(
            _mean([float(item["volatility_adjustment"]) for item in snapshots]), 12
        ),
        "mean_regime_multiplier": round(
            _mean([float(item["regime_multiplier"]) for item in snapshots]), 12
        ),
        "mean_htf_regime_multiplier": round(
            _mean([float(item["htf_regime_multiplier"]) for item in snapshots]), 12
        ),
        "mean_combined_multiplier": round(
            _mean([float(item["combined_multiplier"]) for item in snapshots]), 12
        ),
        "mean_final_size": round(_mean([float(item["final_size"]) for item in snapshots]), 12),
    }

    sizing = {
        "analysis_population": _analysis_population(join_integrity),
        "baseline_metrics": baseline_metrics,
        "unit_size_metrics": unit_metrics,
        "deltas": deltas,
        "sizing_surface_summary": sizing_surface_summary,
        "sizing_conclusion": (
            "Sizing attribution is descriptive: unit-size normalization isolates realized size impact "
            "without changing the underlying trade ledger."
        ),
    }
    summary_lines = [
        "# Sizing attribution",
        "",
        f"- baseline expectancy: `{baseline_metrics['expectancy']}`",
        f"- unit-size expectancy: `{unit_metrics['expectancy']}`",
        f"- baseline profit_factor: `{baseline_metrics['profit_factor']}`",
        f"- unit-size profit_factor: `{unit_metrics['profit_factor']}`",
        f"- expectancy delta (actual-unit): `{deltas['expectancy_delta_actual_minus_unit']}`",
        f"- profit_factor delta (actual-unit): `{deltas['profit_factor_delta_actual_minus_unit']}`",
        f"- win_rate delta (actual-unit): `{deltas['win_rate_delta_actual_minus_unit']}`",
        "- conclusion: realized edge can be inspected under unit-size normalization without rerunning trades.",
    ]
    return sizing, "\n".join(summary_lines)


def _build_path_dependency(
    joined_trades: list[JoinedTrade],
    join_integrity: dict[str, Any],
    *,
    seed: int,
    shuffle_iterations: int,
) -> tuple[dict[str, Any], str]:
    if shuffle_iterations <= 0:
        raise EdgeOriginIsolationError("shuffle_iterations must be > 0")

    baseline_pnls = [trade.trade.pnl for trade in joined_trades]
    baseline_path_metrics = _compute_path_metrics(baseline_pnls)
    rng = random.Random(seed)
    shuffled_max_drawdowns: list[float] = []
    shuffled_path_metrics: list[dict[str, float | int]] = []

    for _ in range(shuffle_iterations):
        shuffled = list(baseline_pnls)
        rng.shuffle(shuffled)
        metrics = _compute_path_metrics(shuffled)
        shuffled_path_metrics.append(metrics)
        shuffled_max_drawdowns.append(float(metrics["max_drawdown"]))

    p_value, median_max_drawdown = _empirical_p_value(
        float(baseline_path_metrics["max_drawdown"]), shuffled_max_drawdowns
    )
    summary = {
        "iterations": shuffle_iterations,
        "seed": seed,
        "shuffled_median_max_drawdown": round(median_max_drawdown, 12),
        "shuffled_mean_max_drawdown": round(_mean(shuffled_max_drawdowns), 12),
        "shuffled_min_max_drawdown": round(float(min(shuffled_max_drawdowns)), 12),
        "shuffled_max_max_drawdown": round(float(max(shuffled_max_drawdowns)), 12),
        "max_drawdown_p_value": round(p_value, 12),
    }
    detected = "YES" if p_value <= 0.05 else "NO"
    payload = {
        "analysis_population": _analysis_population(join_integrity),
        "baseline_path_metrics": baseline_path_metrics,
        "shuffle_distribution_summary": summary,
        "path_dependency_detected": detected,
        "path_conclusion": (
            "Path inference is based on max drawdown over deterministic trade-order shuffles; "
            "profit factor remains order-invariant for a fixed trade multiset."
        ),
    }
    summary_lines = [
        "# Path dependency",
        "",
        f"- baseline max_drawdown: `{baseline_path_metrics['max_drawdown']}`",
        f"- shuffled median max_drawdown: `{summary['shuffled_median_max_drawdown']}`",
        f"- shuffled max_drawdown p-value: `{summary['max_drawdown_p_value']}`",
        "- PF is order-invariant for a fixed trade multiset; path inference is based on path metrics instead.",
        f"- path_dependency_detected: `{detected}`",
        "- conclusion: deterministic shuffle analysis inspects path-shape sensitivity without changing trade membership.",
    ]
    return payload, "\n".join(summary_lines)


def _collect_unique_eligible_timestamps(
    payload: dict[str, Any]
) -> tuple[set[str] | None, dict[str, Any]]:
    trace_rows = _require_list(payload.get("trace_rows"), context="trace_rows")
    timestamps: list[str] = []
    for idx, raw_row in enumerate(trace_rows):
        row = _require_dict(raw_row, context=f"trace_rows[{idx}]")
        if row.get("sizing_phase") is None:
            continue
        timestamps.append(normalize_timestamp(_require_text(row, "timestamp")))

    counts = Counter(timestamps)
    duplicates = sum(max(0, count - 1) for count in counts.values())
    if duplicates:
        return None, {
            "eligible_row_count": len(timestamps),
            "duplicate_eligible_timestamp_count": duplicates,
            "reason": "CONTRAST_UNAVAILABLE_DUPLICATE_TIMESTAMP",
        }
    return set(timestamps), {
        "eligible_row_count": len(timestamps),
        "duplicate_eligible_timestamp_count": 0,
    }


def _build_selection_attribution(
    baseline_payload: dict[str, Any],
    adaptation_payload: dict[str, Any],
    join_integrity: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    baseline_name = baseline_payload.get("name")
    if baseline_name is not None and baseline_name != "baseline_current":
        raise EdgeOriginIsolationError("baseline payload name must be baseline_current")
    adaptation_name = adaptation_payload.get("name")
    if adaptation_name is not None and adaptation_name != "adaptation_off":
        raise EdgeOriginIsolationError("adaptation payload name must be adaptation_off")

    baseline_keys, baseline_diag = _collect_unique_eligible_timestamps(baseline_payload)
    adaptation_keys, adaptation_diag = _collect_unique_eligible_timestamps(adaptation_payload)
    if baseline_keys is None or adaptation_keys is None:
        status = "CONTRAST_UNAVAILABLE"
        selection_metrics = {
            "baseline": baseline_diag,
            "adaptation_off": adaptation_diag,
        }
    else:
        status = "CONTRAST_AVAILABLE"
        selection_metrics = {
            "shared_opportunity_count": len(baseline_keys & adaptation_keys),
            "baseline_only_opportunity_count": len(baseline_keys - adaptation_keys),
            "adaptation_off_only_opportunity_count": len(adaptation_keys - baseline_keys),
            "baseline_eligible_row_count": baseline_diag["eligible_row_count"],
            "adaptation_off_eligible_row_count": adaptation_diag["eligible_row_count"],
        }

    selection = {
        "analysis_population": _analysis_population(join_integrity),
        "contrast_source": "timestamp_level_opportunity_availability",
        "selection_surface_status": status,
        "selection_metrics": selection_metrics,
        "selection_conclusion": (
            "Selection attribution is limited to timestamp-level opportunity contrast and does not infer stronger causality."
        ),
    }
    summary_lines = [
        "# Selection attribution",
        "",
        f"- deterministic contrast population available: `{status == 'CONTRAST_AVAILABLE'}`",
        f"- selection_surface_status: `{status}`",
        "- executed selection test: `timestamp_level_opportunity_availability`",
        "- omitted selection tests: stronger causal selection claims",
        "- conclusion: selection attribution remains a contrast-only surface on eligible timestamps.",
    ]
    return selection, "\n".join(summary_lines)


def _build_counterfactual_matrix(
    sizing_payload: dict[str, Any],
    path_payload: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "control_name": "unit_size_normalization",
            "status": "PASS",
            "reason": "EXECUTED_PACKET_AUTHORIZED_CONTROL",
            "metrics": {
                "baseline_metrics": sizing_payload["baseline_metrics"],
                "unit_size_metrics": sizing_payload["unit_size_metrics"],
                "deltas": sizing_payload["deltas"],
            },
        },
        {
            "control_name": "trade_order_shuffle",
            "status": "PASS",
            "reason": "EXECUTED_PACKET_AUTHORIZED_CONTROL",
            "metrics": {
                "baseline_path_metrics": path_payload["baseline_path_metrics"],
                "shuffle_distribution_summary": path_payload["shuffle_distribution_summary"],
                "path_dependency_detected": path_payload["path_dependency_detected"],
            },
        },
    ]


def _serialize_output(name: str, value: Any) -> str:
    if name.endswith(".json"):
        return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if not isinstance(value, str):
        raise EdgeOriginIsolationError(f"Markdown output must be text: {name}")
    return value.rstrip() + "\n"


def _build_non_self_hashes(outputs: dict[str, Any]) -> dict[str, str]:
    return {
        name: _sha256_text(_serialize_output(name, value))
        for name, value in sorted(outputs.items())
    }


def _build_manifest_hash(output_hashes: dict[str, str]) -> str:
    return _sha256_text(_canonical_json(output_hashes))


def build_edge_origin_outputs(
    baseline_payload: dict[str, Any],
    adaptation_payload: dict[str, Any],
    *,
    seed: int = DEFAULT_SEED,
    shuffle_iterations: int = DEFAULT_SHUFFLE_ITERATIONS,
) -> dict[str, Any]:
    joined_trades, join_integrity = join_baseline_trades(baseline_payload)
    execution_payload, execution_summary = _build_execution_attribution(
        joined_trades, join_integrity
    )
    sizing_payload, sizing_summary = _build_sizing_attribution(joined_trades, join_integrity)
    path_payload, path_summary = _build_path_dependency(
        joined_trades,
        join_integrity,
        seed=seed,
        shuffle_iterations=shuffle_iterations,
    )
    selection_payload, selection_summary = _build_selection_attribution(
        baseline_payload,
        adaptation_payload,
        join_integrity,
    )
    counterfactual_matrix = _build_counterfactual_matrix(sizing_payload, path_payload)

    return {
        "execution_attribution.json": execution_payload,
        "execution_summary.md": execution_summary,
        "sizing_attribution.json": sizing_payload,
        "sizing_summary.md": sizing_summary,
        "path_dependency.json": path_payload,
        "path_summary.md": path_summary,
        "selection_attribution.json": selection_payload,
        "selection_summary.md": selection_summary,
        "counterfactual_matrix.json": counterfactual_matrix,
    }


def run_edge_origin_isolation(
    baseline_payload: dict[str, Any],
    adaptation_payload: dict[str, Any],
    *,
    seed: int = DEFAULT_SEED,
    shuffle_iterations: int = DEFAULT_SHUFFLE_ITERATIONS,
) -> dict[str, Any]:
    run1 = build_edge_origin_outputs(
        baseline_payload,
        adaptation_payload,
        seed=seed,
        shuffle_iterations=shuffle_iterations,
    )
    run2 = build_edge_origin_outputs(
        baseline_payload,
        adaptation_payload,
        seed=seed,
        shuffle_iterations=shuffle_iterations,
    )
    run1_hashes = _build_non_self_hashes(run1)
    run2_hashes = _build_non_self_hashes(run2)
    run1_hash = _build_manifest_hash(run1_hashes)
    run2_hash = _build_manifest_hash(run2_hashes)

    audit_payload = {
        "join_integrity": run1["execution_attribution.json"]["analysis_population"]
        | join_baseline_trades(baseline_payload)[1],
        "non_self_outputs": sorted(run1_hashes),
        "run1_hashes": run1_hashes,
        "run2_hashes": run2_hashes,
        "run1_hash": run1_hash,
        "run2_hash": run2_hash,
        "match": bool(run1_hashes == run2_hashes and run1_hash == run2_hash),
    }

    outputs = dict(run1)
    outputs["audit_phase10_determinism.json"] = audit_payload
    return outputs


def write_outputs(outputs: dict[str, Any], out_dir: Path) -> dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, str] = {}
    for name, value in outputs.items():
        path = out_dir / name
        path.write_text(_serialize_output(name, value), encoding="utf-8")
        written[name] = str(path)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read-only Phase 10 edge-origin isolation analysis"
    )
    parser.add_argument("baseline", type=Path, help="Path to trace_baseline_current.json")
    parser.add_argument("adaptation_off", type=Path, help="Path to trace_adaptation_off.json")
    parser.add_argument(
        "--out-dir", type=Path, default=None, help="Optional directory for output files"
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--shuffle-iterations", type=int, default=DEFAULT_SHUFFLE_ITERATIONS)
    parser.add_argument("--json", action="store_true", help="Print machine-readable run summary")
    args = parser.parse_args(argv)

    try:
        outputs = run_edge_origin_isolation(
            _load_json(args.baseline),
            _load_json(args.adaptation_off),
            seed=int(args.seed),
            shuffle_iterations=int(args.shuffle_iterations),
        )
    except EdgeOriginIsolationError as exc:
        payload = {"status": "FAIL", "failure": str(exc)}
        print(json.dumps(payload, sort_keys=True))
        return 1

    written: dict[str, str] = {}
    if args.out_dir is not None:
        written = write_outputs(outputs, args.out_dir)

    audit = outputs["audit_phase10_determinism.json"]
    payload = {
        "status": "PASS" if audit["match"] else "FAIL",
        "seed": int(args.seed),
        "shuffle_iterations": int(args.shuffle_iterations),
        "join_status": audit["join_integrity"]["join_status"],
        "match": audit["match"],
        "output_dir": str(args.out_dir) if args.out_dir is not None else None,
        "written_files": written,
    }

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"[EDGE-ORIGIN] {payload['status']}")
        print(f"[EDGE-ORIGIN] seed={payload['seed']}")
        print(f"[EDGE-ORIGIN] join_status={payload['join_status']}")
        print(f"[EDGE-ORIGIN] determinism_match={payload['match']}")
        if args.out_dir is not None:
            print(f"[EDGE-ORIGIN] output_dir={args.out_dir}")

    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
