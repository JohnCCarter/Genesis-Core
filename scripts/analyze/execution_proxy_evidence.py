"""Read-only execution-proxy analysis over locked trace artifacts.

This module derives deterministic proxy price-path evidence from attested trace-row
price fields without modifying runtime strategy code or locked Phase 10 outputs.
The produced evidence remains observational only and must not be interpreted as
realized fill, slippage, or latency authority.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_FIXED_HORIZONS = (1, 4, 8)
OUTPUT_FILES = (
    "execution_proxy_evidence.json",
    "execution_proxy_summary.md",
)


class ExecutionProxyEvidenceError(RuntimeError):
    """Raised when execution-proxy evidence cannot be attested safely."""


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
    exit_row: dict[str, Any]
    entry_bar_index: int
    exit_bar_index: int
    direction: int


@dataclass(frozen=True)
class ProxyTradeMetrics:
    trade_key: dict[str, Any]
    entry_bar_index: int
    exit_bar_index: int
    window_row_count: int
    observed_price_row_count: int
    observed_price_coverage_ratio: float
    full_window_price_attested: bool
    missing_proxy_price_bar_count: int
    missing_proxy_price_bar_indexes: list[int]
    first_missing_proxy_price_bar_index: int | None
    last_observed_proxy_price_bar_index: int
    exit_bar_proxy_price_present: bool
    proxy_window_missingness_class: str
    entry_proxy_price: float
    exit_proxy_price: float | None
    exact_exit_proxy_price_status: str
    proxy_mae_price_delta: float
    proxy_mfe_price_delta: float
    fixed_horizon_deltas: list[dict[str, Any]]


def normalize_timestamp(timestamp: str) -> str:
    """Normalize artifact timestamps by removing a single +00:00 suffix."""

    if not isinstance(timestamp, str) or not timestamp:
        raise ExecutionProxyEvidenceError("timestamp must be a non-empty string")
    return timestamp[:-6] if timestamp.endswith("+00:00") else timestamp


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _require_dict(value: Any, *, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ExecutionProxyEvidenceError(f"{context} must be an object")
    return value


def _require_list(value: Any, *, context: str) -> list[Any]:
    if not isinstance(value, list):
        raise ExecutionProxyEvidenceError(f"{context} must be an array")
    return value


def _nested_get(mapping: dict[str, Any], path: str) -> Any:
    current: Any = mapping
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            raise ExecutionProxyEvidenceError(f"Missing required field: {path}")
        current = current[part]
    return current


def _require_text(mapping: dict[str, Any], path: str) -> str:
    value = _nested_get(mapping, path)
    if not isinstance(value, str) or not value:
        raise ExecutionProxyEvidenceError(f"Field must be a non-empty string: {path}")
    return value


def _require_number(mapping: dict[str, Any], path: str) -> float:
    value = _nested_get(mapping, path)
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ExecutionProxyEvidenceError(f"Field must be numeric: {path}")
    out = float(value)
    if out != out or out in {float("inf"), float("-inf")}:
        raise ExecutionProxyEvidenceError(f"Field must be finite: {path}")
    return out


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ExecutionProxyEvidenceError(f"Missing input file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ExecutionProxyEvidenceError(f"Invalid JSON in {path}: {exc}") from exc
    return _require_dict(payload, context=f"payload:{path}")


def _load_trade_signatures(payload: dict[str, Any]) -> list[TradeSignature]:
    rows = _require_list(payload.get("trade_signatures"), context="trade_signatures")
    trades: list[TradeSignature] = []
    for idx, raw in enumerate(rows):
        item = _require_dict(raw, context=f"trade_signatures[{idx}]")
        trades.append(
            TradeSignature(
                entry_timestamp=_require_text(item, "entry_timestamp"),
                exit_timestamp=_require_text(item, "exit_timestamp"),
                side=_require_text(item, "side"),
                size=_require_number(item, "size"),
                pnl=_require_number(item, "pnl"),
            )
        )
    return trades


def _side_direction(side: str) -> int:
    upper = side.upper()
    if "LONG" in upper:
        return 1
    if "SHORT" in upper:
        return -1
    raise ExecutionProxyEvidenceError(f"Unsupported trade side for proxy path semantics: {side}")


def _eligible_rows_by_timestamp(
    trace_rows: list[dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], int]:
    bucket: dict[str, list[dict[str, Any]]] = {}
    for row in trace_rows:
        if row.get("sizing_phase") is None:
            continue
        normalized = normalize_timestamp(_require_text(row, "timestamp"))
        bucket.setdefault(normalized, []).append(row)

    duplicate_count = sum(max(0, len(rows) - 1) for rows in bucket.values())
    if duplicate_count:
        raise ExecutionProxyEvidenceError("duplicate normalized baseline trace timestamps detected")
    return {key: rows[0] for key, rows in bucket.items()}, duplicate_count


def _rows_by_timestamp(trace_rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    bucket: dict[str, list[dict[str, Any]]] = {}
    for row in trace_rows:
        normalized = normalize_timestamp(_require_text(row, "timestamp"))
        bucket.setdefault(normalized, []).append(row)
    return bucket


def _rows_by_bar_index(trace_rows: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    rows: dict[int, dict[str, Any]] = {}
    for idx, row in enumerate(trace_rows):
        bar_index_value = _nested_get(row, "bar_index")
        if isinstance(bar_index_value, bool) or not isinstance(bar_index_value, int):
            raise ExecutionProxyEvidenceError(f"trace_rows[{idx}].bar_index must be an int")
        if bar_index_value in rows:
            raise ExecutionProxyEvidenceError("duplicate trace bar_index detected")
        rows[int(bar_index_value)] = row
    return rows


def _observed_proxy_price(row: dict[str, Any]) -> float | None:
    fib_phase = row.get("fib_phase")
    if fib_phase is None:
        return None
    fib_phase_dict = _require_dict(fib_phase, context="fib_phase")
    ltf_debug = fib_phase_dict.get("ltf_debug")
    if ltf_debug is None:
        return None
    ltf_debug_dict = _require_dict(ltf_debug, context="fib_phase.ltf_debug")
    if "price" not in ltf_debug_dict:
        return None
    value = ltf_debug_dict["price"]
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ExecutionProxyEvidenceError("fib_phase.ltf_debug.price must be numeric when present")
    out = float(value)
    if out != out or out in {float("inf"), float("-inf")}:
        raise ExecutionProxyEvidenceError("fib_phase.ltf_debug.price must be finite when present")
    return out


def _trade_sort_key(trade: TradeSignature) -> tuple[Any, ...]:
    return (
        trade.entry_timestamp,
        trade.exit_timestamp,
        trade.side,
        trade.size,
        trade.pnl,
    )


def join_baseline_trades(
    payload: dict[str, Any]
) -> tuple[list[JoinedTrade], dict[str, Any], list[dict[str, Any]]]:
    payload_name = payload.get("name")
    if payload_name is not None and payload_name != "baseline_current":
        raise ExecutionProxyEvidenceError("baseline payload name must be baseline_current")

    trades = _load_trade_signatures(payload)
    trace_rows = [
        _require_dict(row, context=f"trace_rows[{idx}]")
        for idx, row in enumerate(_require_list(payload.get("trace_rows"), context="trace_rows"))
    ]

    eligible_rows, duplicate_trace_count = _eligible_rows_by_timestamp(trace_rows)
    all_rows = _rows_by_timestamp(trace_rows)
    _rows_by_bar_index(trace_rows)
    entry_counts = Counter(normalize_timestamp(trade.entry_timestamp) for trade in trades)

    joined: list[JoinedTrade] = []
    unmatched = 0
    duplicate_exit_count = 0

    for trade in trades:
        if trade.pnl == 0:
            raise ExecutionProxyEvidenceError("FLAT trades are forbidden by the packet")
        normalized_entry = normalize_timestamp(trade.entry_timestamp)
        entry_row = eligible_rows.get(normalized_entry)
        if entry_row is None:
            unmatched += 1
            continue

        normalized_exit = normalize_timestamp(trade.exit_timestamp)
        exit_candidates = all_rows.get(normalized_exit, [])
        if len(exit_candidates) != 1:
            duplicate_exit_count += max(1, len(exit_candidates))
            raise ExecutionProxyEvidenceError("exit row must resolve exactly once for every trade")
        exit_row = exit_candidates[0]

        entry_bar_index = int(_nested_get(entry_row, "bar_index"))
        exit_bar_index = int(_nested_get(exit_row, "bar_index"))
        if exit_bar_index < entry_bar_index:
            raise ExecutionProxyEvidenceError("exit bar_index must be >= entry bar_index")

        joined.append(
            JoinedTrade(
                trade=trade,
                entry_row=entry_row,
                exit_row=exit_row,
                entry_bar_index=entry_bar_index,
                exit_bar_index=exit_bar_index,
                direction=_side_direction(trade.side),
            )
        )

    if unmatched or duplicate_trace_count:
        raise ExecutionProxyEvidenceError("baseline trades did not join exactly once to entry rows")

    joined.sort(key=lambda item: _trade_sort_key(item.trade))
    join_integrity = {
        "baseline_trade_count_raw": len(trades),
        "matched_trade_count": len(joined),
        "binary_trade_count": len(joined),
        "unmatched_trade_count": unmatched,
        "duplicate_trade_entry_timestamp_count": sum(
            max(0, count - 1) for count in entry_counts.values()
        ),
        "duplicate_normalized_trace_timestamp_count": duplicate_trace_count,
        "duplicate_exit_timestamp_resolution_count": duplicate_exit_count,
        "join_status": "EXACT_ONE_MATCH_PER_TRADE",
        "exit_row_resolution_status": "EXACT_ONE_EXIT_ROW_PER_TRADE",
    }
    return joined, join_integrity, trace_rows


def _price_delta(direction: int, entry_price: float, observed_price: float) -> float:
    return float(direction * (observed_price - entry_price))


def _window_rows(
    rows_by_bar_index: dict[int, dict[str, Any]], start_bar_index: int, end_bar_index: int
) -> list[tuple[int, dict[str, Any]]]:
    indexes = [
        bar_index
        for bar_index in sorted(rows_by_bar_index)
        if start_bar_index <= bar_index <= end_bar_index
    ]
    if not indexes:
        raise ExecutionProxyEvidenceError(
            "inclusive entry-exit window must contain at least one row"
        )
    expected_count = end_bar_index - start_bar_index + 1
    if len(indexes) != expected_count:
        raise ExecutionProxyEvidenceError(
            "missing trace bar_index inside inclusive entry-exit window"
        )
    return [(bar_index, rows_by_bar_index[bar_index]) for bar_index in indexes]


def _fixed_horizon_metrics(
    rows_by_bar_index: dict[int, dict[str, Any]],
    entry_bar_index: int,
    entry_price: float,
    direction: int,
    horizons: tuple[int, ...],
) -> list[dict[str, Any]]:
    metrics: list[dict[str, Any]] = []
    for horizon in horizons:
        target_bar_index = entry_bar_index + horizon
        row = rows_by_bar_index.get(target_bar_index)
        if row is None:
            metrics.append(
                {
                    "horizon_bars": horizon,
                    "status": "OMITTED_MISSING_BAR_INDEX",
                    "target_bar_index": target_bar_index,
                    "proxy_price_delta": None,
                }
            )
            continue
        observed_price = _observed_proxy_price(row)
        if observed_price is None:
            metrics.append(
                {
                    "horizon_bars": horizon,
                    "status": "OMITTED_MISSING_PROXY_PRICE",
                    "target_bar_index": target_bar_index,
                    "proxy_price_delta": None,
                }
            )
            continue
        metrics.append(
            {
                "horizon_bars": horizon,
                "status": "PASS",
                "target_bar_index": target_bar_index,
                "proxy_price_delta": round(
                    _price_delta(direction, entry_price, observed_price), 12
                ),
            }
        )
    return metrics


def _classify_proxy_window_missingness(
    *,
    missing_proxy_price_bar_indexes: list[int],
    exit_bar_index: int,
) -> str:
    if not missing_proxy_price_bar_indexes:
        return "FULL_WINDOW_PROXY_PRICE_OBSERVED"

    exit_missing = exit_bar_index in missing_proxy_price_bar_indexes
    interior_missing = any(
        bar_index != exit_bar_index for bar_index in missing_proxy_price_bar_indexes
    )

    if exit_missing and interior_missing:
        return "EXIT_AND_INTERIOR_PROXY_PRICE_MISSING"
    if exit_missing:
        return "EXIT_BAR_PROXY_PRICE_MISSING"
    return "INTERIOR_PROXY_PRICE_MISSING"


def _build_trade_proxy_metrics(
    joined_trade: JoinedTrade,
    rows_by_bar_index: dict[int, dict[str, Any]],
    horizons: tuple[int, ...],
) -> ProxyTradeMetrics:
    entry_price = _observed_proxy_price(joined_trade.entry_row)
    if entry_price is None:
        raise ExecutionProxyEvidenceError("joined entry row must expose fib_phase.ltf_debug.price")

    window_rows = _window_rows(
        rows_by_bar_index,
        joined_trade.entry_bar_index,
        joined_trade.exit_bar_index,
    )
    observed_rows: list[tuple[int, float]] = []
    for bar_index, row in window_rows:
        observed_price = _observed_proxy_price(row)
        if observed_price is not None:
            observed_rows.append((bar_index, observed_price))

    if not observed_rows or observed_rows[0][0] != joined_trade.entry_bar_index:
        raise ExecutionProxyEvidenceError(
            "inclusive proxy window must begin with an attested entry-row price"
        )

    missing_proxy_price_bar_indexes = [
        bar_index for bar_index, row in window_rows if _observed_proxy_price(row) is None
    ]
    coverage_ratio = round(len(observed_rows) / len(window_rows), 12)
    deltas = [
        _price_delta(joined_trade.direction, entry_price, price) for _, price in observed_rows
    ]
    exit_proxy_price = _observed_proxy_price(joined_trade.exit_row)
    exit_status = "PASS" if exit_proxy_price is not None else "OMITTED_MISSING_PROXY_PRICE"
    proxy_window_missingness_class = _classify_proxy_window_missingness(
        missing_proxy_price_bar_indexes=missing_proxy_price_bar_indexes,
        exit_bar_index=joined_trade.exit_bar_index,
    )
    fixed_horizon_deltas = _fixed_horizon_metrics(
        rows_by_bar_index,
        joined_trade.entry_bar_index,
        entry_price,
        joined_trade.direction,
        horizons,
    )

    return ProxyTradeMetrics(
        trade_key={
            "entry_timestamp": joined_trade.trade.entry_timestamp,
            "exit_timestamp": joined_trade.trade.exit_timestamp,
            "side": joined_trade.trade.side,
            "size": joined_trade.trade.size,
            "pnl": joined_trade.trade.pnl,
        },
        entry_bar_index=joined_trade.entry_bar_index,
        exit_bar_index=joined_trade.exit_bar_index,
        window_row_count=len(window_rows),
        observed_price_row_count=len(observed_rows),
        observed_price_coverage_ratio=coverage_ratio,
        full_window_price_attested=len(observed_rows) == len(window_rows),
        missing_proxy_price_bar_count=len(missing_proxy_price_bar_indexes),
        missing_proxy_price_bar_indexes=missing_proxy_price_bar_indexes,
        first_missing_proxy_price_bar_index=(
            None if not missing_proxy_price_bar_indexes else missing_proxy_price_bar_indexes[0]
        ),
        last_observed_proxy_price_bar_index=observed_rows[-1][0],
        exit_bar_proxy_price_present=exit_proxy_price is not None,
        proxy_window_missingness_class=proxy_window_missingness_class,
        entry_proxy_price=round(entry_price, 12),
        exit_proxy_price=(None if exit_proxy_price is None else round(exit_proxy_price, 12)),
        exact_exit_proxy_price_status=exit_status,
        proxy_mae_price_delta=round(min(deltas), 12),
        proxy_mfe_price_delta=round(max(deltas), 12),
        fixed_horizon_deltas=fixed_horizon_deltas,
    )


def _mean(values: list[float]) -> float:
    if not values:
        raise ExecutionProxyEvidenceError("values must not be empty")
    return float(statistics.fmean(values))


def _median(values: list[float]) -> float:
    if not values:
        raise ExecutionProxyEvidenceError("values must not be empty")
    return float(statistics.median(values))


def _serialize_output(name: str, value: Any) -> str:
    if name.endswith(".json"):
        return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if not isinstance(value, str):
        raise ExecutionProxyEvidenceError(f"Markdown output must be text: {name}")
    return value.rstrip() + "\n"


def _build_non_self_hashes(outputs: dict[str, Any]) -> dict[str, str]:
    return {
        name: _sha256_text(_serialize_output(name, value))
        for name, value in sorted(outputs.items())
    }


def _build_manifest_hash(output_hashes: dict[str, str]) -> str:
    return _sha256_text(_canonical_json(output_hashes))


def build_execution_proxy_outputs(
    baseline_payload: dict[str, Any],
    *,
    horizons: tuple[int, ...] = DEFAULT_FIXED_HORIZONS,
) -> dict[str, Any]:
    if not horizons or any(horizon <= 0 for horizon in horizons):
        raise ExecutionProxyEvidenceError("horizons must be positive integers")

    joined_trades, join_integrity, trace_rows = join_baseline_trades(baseline_payload)
    rows_by_bar_index = _rows_by_bar_index(trace_rows)
    proxy_metrics = [
        _build_trade_proxy_metrics(joined_trade, rows_by_bar_index, horizons)
        for joined_trade in joined_trades
    ]

    resolved_exit_prices = [
        metric.exit_proxy_price for metric in proxy_metrics if metric.exit_proxy_price is not None
    ]
    favorable_exit_deltas = [
        (
            round(metric.exit_proxy_price - metric.entry_proxy_price, 12)
            if metric.trade_key["side"].upper().find("SHORT") == -1
            else round(metric.entry_proxy_price - metric.exit_proxy_price, 12)
        )
        for metric in proxy_metrics
        if metric.exit_proxy_price is not None
    ]
    mae_values = [metric.proxy_mae_price_delta for metric in proxy_metrics]
    mfe_values = [metric.proxy_mfe_price_delta for metric in proxy_metrics]
    coverage_values = [metric.observed_price_coverage_ratio for metric in proxy_metrics]
    missingness_class_counts = Counter(
        metric.proxy_window_missingness_class for metric in proxy_metrics
    )

    fixed_horizon_summaries: list[dict[str, Any]] = []
    for horizon in horizons:
        matching = []
        omitted = 0
        for metric in proxy_metrics:
            row = next(
                item for item in metric.fixed_horizon_deltas if item["horizon_bars"] == horizon
            )
            if row["status"] == "PASS":
                matching.append(float(row["proxy_price_delta"]))
            else:
                omitted += 1
        fixed_horizon_summaries.append(
            {
                "horizon_bars": horizon,
                "resolved_trade_count": len(matching),
                "omitted_trade_count": omitted,
                "status": "PASS" if matching else "OMITTED_NO_RESOLVED_PROXY_PRICE",
                "mean_proxy_price_delta": (None if not matching else round(_mean(matching), 12)),
                "median_proxy_price_delta": (
                    None if not matching else round(_median(matching), 12)
                ),
            }
        )

    evidence_payload = {
        "analysis_population": join_integrity,
        "proxy_surface": {
            "price_source": "trace_rows.fib_phase.ltf_debug.price",
            "window_semantics": "inclusive_entry_exit_bar_index_window",
            "price_observation_semantics": "attested_rows_only",
            "full_window_attested_trade_count": sum(
                1 for metric in proxy_metrics if metric.full_window_price_attested
            ),
            "sparse_window_trade_count": sum(
                1 for metric in proxy_metrics if not metric.full_window_price_attested
            ),
            "fixed_horizon_bars": list(horizons),
        },
        "entry_exit_proxy_summary": {
            "trade_count": len(proxy_metrics),
            "exact_exit_proxy_price_count": len(resolved_exit_prices),
            "omitted_exit_proxy_price_count": len(proxy_metrics) - len(resolved_exit_prices),
            "mean_entry_proxy_price": round(
                _mean([metric.entry_proxy_price for metric in proxy_metrics]), 12
            ),
            "mean_exit_proxy_price": (
                None if not resolved_exit_prices else round(_mean(resolved_exit_prices), 12)
            ),
            "mean_favorable_exit_price_delta": (
                None if not favorable_exit_deltas else round(_mean(favorable_exit_deltas), 12)
            ),
            "median_favorable_exit_price_delta": (
                None if not favorable_exit_deltas else round(_median(favorable_exit_deltas), 12)
            ),
        },
        "proxy_path_summary": {
            "trade_count": len(proxy_metrics),
            "mean_window_row_count": round(
                _mean([float(metric.window_row_count) for metric in proxy_metrics]), 12
            ),
            "mean_observed_price_row_count": round(
                _mean([float(metric.observed_price_row_count) for metric in proxy_metrics]), 12
            ),
            "mean_observed_price_coverage_ratio": round(_mean(coverage_values), 12),
            "median_observed_price_coverage_ratio": round(_median(coverage_values), 12),
            "mean_proxy_mae_price_delta": round(_mean(mae_values), 12),
            "median_proxy_mae_price_delta": round(_median(mae_values), 12),
            "mean_proxy_mfe_price_delta": round(_mean(mfe_values), 12),
            "median_proxy_mfe_price_delta": round(_median(mfe_values), 12),
        },
        "proxy_window_missingness_summary": {
            "trade_count": len(proxy_metrics),
            "full_window_proxy_price_observed_count": missingness_class_counts[
                "FULL_WINDOW_PROXY_PRICE_OBSERVED"
            ],
            "exit_bar_proxy_price_present_count": sum(
                1 for metric in proxy_metrics if metric.exit_bar_proxy_price_present
            ),
            "exit_bar_proxy_price_missing_count": sum(
                1 for metric in proxy_metrics if not metric.exit_bar_proxy_price_present
            ),
            "missingness_class_counts": {
                name: missingness_class_counts[name] for name in sorted(missingness_class_counts)
            },
        },
        "fixed_horizon_summaries": fixed_horizon_summaries,
        "trade_proxy_metrics": [
            {
                "trade_key": metric.trade_key,
                "entry_bar_index": metric.entry_bar_index,
                "exit_bar_index": metric.exit_bar_index,
                "window_row_count": metric.window_row_count,
                "observed_price_row_count": metric.observed_price_row_count,
                "observed_price_coverage_ratio": metric.observed_price_coverage_ratio,
                "full_window_price_attested": metric.full_window_price_attested,
                "missing_proxy_price_bar_count": metric.missing_proxy_price_bar_count,
                "missing_proxy_price_bar_indexes": metric.missing_proxy_price_bar_indexes,
                "first_missing_proxy_price_bar_index": metric.first_missing_proxy_price_bar_index,
                "last_observed_proxy_price_bar_index": metric.last_observed_proxy_price_bar_index,
                "exit_bar_proxy_price_present": metric.exit_bar_proxy_price_present,
                "proxy_window_missingness_class": metric.proxy_window_missingness_class,
                "entry_proxy_price": metric.entry_proxy_price,
                "exit_proxy_price": metric.exit_proxy_price,
                "exact_exit_proxy_price_status": metric.exact_exit_proxy_price_status,
                "proxy_mae_price_delta": metric.proxy_mae_price_delta,
                "proxy_mfe_price_delta": metric.proxy_mfe_price_delta,
                "fixed_horizon_deltas": metric.fixed_horizon_deltas,
            }
            for metric in proxy_metrics
        ],
        "limitations": [
            "Proxy evidence uses only attested trace_rows.fib_phase.ltf_debug.price observations.",
            "Proxy evidence does not attest realized execution price, slippage, latency, or queue position.",
            "Sparse windows indicate missing attested price observations inside the inclusive entry-exit bar window.",
            "Proxy missingness diagnostics describe coverage only and do not attest realized execution, slippage, latency, or venue behavior.",
            "Proxy evidence does not support causal support or rejection of execution_inefficiency.",
        ],
        "proxy_conclusion": (
            "This lane produces proxy price-path evidence only from authorized trace-row fields and "
            "does not attest realized execution quality."
        ),
    }

    summary_lines = [
        "# Execution proxy summary",
        "",
        "This lane is observational only and emits proxy price-path evidence from attested trace rows.",
        "",
        f"- trade_count: `{join_integrity['matched_trade_count']}`",
        f"- price source: `{evidence_payload['proxy_surface']['price_source']}`",
        f"- window semantics: `{evidence_payload['proxy_surface']['window_semantics']}`",
        f"- full-window attested trades: `{evidence_payload['proxy_surface']['full_window_attested_trade_count']}`",
        f"- sparse-window trades: `{evidence_payload['proxy_surface']['sparse_window_trade_count']}`",
        "- these diagnostics describe proxy price-path coverage and missingness only. They do not attest realized execution, slippage, latency, or venue behavior.",
        f"- exit-bar proxy price present trades: `{evidence_payload['proxy_window_missingness_summary']['exit_bar_proxy_price_present_count']}`",
        f"- exit-bar proxy price missing trades: `{evidence_payload['proxy_window_missingness_summary']['exit_bar_proxy_price_missing_count']}`",
        f"- mean proxy MAE price delta: `{evidence_payload['proxy_path_summary']['mean_proxy_mae_price_delta']}`",
        f"- mean proxy MFE price delta: `{evidence_payload['proxy_path_summary']['mean_proxy_mfe_price_delta']}`",
        "- fixed-horizon summaries are proxy-only and omit unresolved bar-price observations explicitly.",
        "- limitation: this output does not attest realized execution price, slippage, latency, or queue position.",
        f"- conclusion: {evidence_payload['proxy_conclusion']}",
    ]

    return {
        "execution_proxy_evidence.json": evidence_payload,
        "execution_proxy_summary.md": "\n".join(summary_lines),
    }


def run_execution_proxy_evidence(
    baseline_payload: dict[str, Any],
    *,
    horizons: tuple[int, ...] = DEFAULT_FIXED_HORIZONS,
) -> dict[str, Any]:
    run1 = build_execution_proxy_outputs(baseline_payload, horizons=horizons)
    run2 = build_execution_proxy_outputs(baseline_payload, horizons=horizons)
    run1_hashes = _build_non_self_hashes(run1)
    run2_hashes = _build_non_self_hashes(run2)
    run1_hash = _build_manifest_hash(run1_hashes)
    run2_hash = _build_manifest_hash(run2_hashes)

    outputs = dict(run1)
    outputs["audit_execution_proxy_determinism.json"] = {
        "non_self_outputs": sorted(run1_hashes),
        "run1_hashes": run1_hashes,
        "run2_hashes": run2_hashes,
        "run1_hash": run1_hash,
        "run2_hash": run2_hash,
        "match": bool(run1_hashes == run2_hashes and run1_hash == run2_hash),
    }
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
        description="Read-only execution-proxy evidence analysis over locked traces"
    )
    parser.add_argument("baseline", type=Path, help="Path to trace_baseline_current.json")
    parser.add_argument("--out-dir", type=Path, default=None, help="Optional output directory")
    parser.add_argument(
        "--horizons",
        type=int,
        nargs="*",
        default=list(DEFAULT_FIXED_HORIZONS),
        help="Positive bar horizons for fixed-horizon proxy summaries",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable summary")
    args = parser.parse_args(argv)

    try:
        outputs = run_execution_proxy_evidence(
            _load_json(args.baseline),
            horizons=tuple(int(value) for value in args.horizons),
        )
    except ExecutionProxyEvidenceError as exc:
        print(json.dumps({"status": "FAIL", "failure": str(exc)}, sort_keys=True))
        return 1

    written: dict[str, str] = {}
    if args.out_dir is not None:
        written = write_outputs(outputs, args.out_dir)

    audit = outputs["audit_execution_proxy_determinism.json"]
    payload = {
        "status": "PASS" if audit["match"] else "FAIL",
        "horizons": [int(value) for value in args.horizons],
        "match": audit["match"],
        "output_dir": str(args.out_dir) if args.out_dir is not None else None,
        "written_files": written,
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"[EXECUTION-PROXY] {payload['status']}")
        print(f"[EXECUTION-PROXY] determinism_match={payload['match']}")
        print(f"[EXECUTION-PROXY] horizons={payload['horizons']}")
        if args.out_dir is not None:
            print(f"[EXECUTION-PROXY] output_dir={args.out_dir}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
