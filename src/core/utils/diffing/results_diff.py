"""
Results diffing utilities for comparing backtest results.
"""

from __future__ import annotations

from typing import Any


def diff_backtest_results(baseline: dict[str, Any], new_results: dict[str, Any]) -> dict[str, Any]:
    """
    Compare two backtest result dictionaries and return the differences.

    Args:
        baseline: Baseline backtest results
        new_results: New backtest results to compare

    Returns:
        Dictionary with 'metrics' and 'trades' diff information
    """
    diff_payload: dict[str, Any] = {"metrics": {}, "trades": {}}

    # Compare metrics
    baseline_metrics = baseline.get("metrics", {})
    new_metrics = new_results.get("metrics", {})

    # Get all metric keys from both results
    all_metric_keys = set(baseline_metrics.keys()) | set(new_metrics.keys())

    for metric_key in all_metric_keys:
        old_val = baseline_metrics.get(metric_key)
        new_val = new_metrics.get(metric_key)

        # Skip if both are None
        if old_val is None and new_val is None:
            continue

        # Handle numeric metrics
        if isinstance(old_val, (int, float)) and isinstance(new_val, (int, float)):
            delta = new_val - old_val
            diff_payload["metrics"][metric_key] = {"old": old_val, "new": new_val, "delta": delta}
        elif old_val != new_val:
            # Non-numeric or changed values
            diff_payload["metrics"][metric_key] = {"old": old_val, "new": new_val, "delta": None}

    # Compare trade counts
    baseline_trades = baseline.get("trades", [])
    new_trades = new_results.get("trades", [])

    diff_payload["trades"] = {
        "baseline_count": len(baseline_trades) if isinstance(baseline_trades, list) else 0,
        "new_count": len(new_trades) if isinstance(new_trades, list) else 0,
        "delta": (len(new_trades) if isinstance(new_trades, list) else 0)
        - (len(baseline_trades) if isinstance(baseline_trades, list) else 0),
    }

    return diff_payload


__all__ = ["diff_backtest_results"]
