from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class MetricDelta:
    old: float | int | None
    new: float | int | None
    delta: float | int | None
    regression: bool = False


def _compute_delta(old_value: Any, new_value: Any) -> MetricDelta:
    if old_value is None and new_value is None:
        return MetricDelta(old=None, new=None, delta=None, regression=False)
    try:
        old_num = float(old_value) if old_value is not None else 0.0
        new_num = float(new_value) if new_value is not None else 0.0
        return MetricDelta(
            old=old_value,
            new=new_value,
            delta=new_num - old_num,
            regression=False,
        )
    except (TypeError, ValueError):
        regression = old_value != new_value
        return MetricDelta(old=old_value, new=new_value, delta=None, regression=regression)


def diff_metrics(
    old_metrics: dict[str, Any],
    new_metrics: dict[str, Any],
    *,
    regression_thresholds: dict[str, float | int] | None = None,
) -> dict[str, MetricDelta]:
    regression_thresholds = regression_thresholds or {}
    diff: dict[str, MetricDelta] = {}
    keys = set(old_metrics.keys()) | set(new_metrics.keys())
    for key in sorted(keys):
        delta = _compute_delta(old_metrics.get(key), new_metrics.get(key))
        if delta.delta is not None:
            threshold = regression_thresholds.get(key)
            if threshold is not None and delta.delta <= threshold:
                delta.regression = True
        diff[key] = delta
    return diff


def diff_backtest_results(
    old_results: dict[str, Any], new_results: dict[str, Any]
) -> dict[str, Any]:
    old_metrics = (
        (old_results.get("summary") or {}).get("metrics") or old_results.get("metrics") or {}
    )
    new_metrics = (
        (new_results.get("summary") or {}).get("metrics") or new_results.get("metrics") or {}
    )
    metric_diff = diff_metrics(old_metrics, new_metrics)
    trades_old = len(old_results.get("trades") or [])
    trades_new = len(new_results.get("trades") or [])
    trade_delta = MetricDelta(old=trades_old, new=trades_new, delta=trades_new - trades_old)
    metrics_serialized = {
        key: {
            "old": delta.old,
            "new": delta.new,
            "delta": delta.delta,
            "regression": delta.regression,
        }
        for key, delta in metric_diff.items()
    }
    trade_serialized = {
        "old": trade_delta.old,
        "new": trade_delta.new,
        "delta": trade_delta.delta,
        "regression": trade_delta.regression,
    }
    return {
        "metrics": metrics_serialized,
        "trades": trade_serialized,
    }


def diff_backtest_files(old_path: Path | str, new_path: Path | str) -> dict[str, Any]:
    with (
        Path(old_path).open("r", encoding="utf-8") as f_old,
        Path(new_path).open("r", encoding="utf-8") as f_new,
    ):
        old_data = json.load(f_old)
        new_data = json.load(f_new)
    return diff_backtest_results(old_data, new_data)


def summarize_metric_deltas(diff: dict[str, MetricDelta]) -> str:
    lines = []
    for key, delta in diff.items():
        if delta.delta is not None:
            lines.append(f"{key}: {delta.delta:+.4f} (old={delta.old}, new={delta.new})")
        elif delta.regression:
            lines.append(f"{key}: changed from {delta.old} to {delta.new}")
    return "\n".join(lines)


def summarize_metrics_diff(serialized_diff: dict[str, Any]) -> str:
    lines = []
    for key, payload in serialized_diff.items():
        delta = payload.get("delta")
        if delta is not None:
            lines.append(
                f"{key}: {delta:+.4f} (old={payload.get('old')}, new={payload.get('new')})"
            )
        elif payload.get("regression"):
            lines.append(f"{key}: changed from {payload.get('old')} to {payload.get('new')}")
    return "\n".join(lines)
