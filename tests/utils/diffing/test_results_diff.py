from __future__ import annotations

import pytest

from core.utils.diffing.results_diff import (
    diff_backtest_results,
    diff_metrics,
    summarize_metric_deltas,
    summarize_metrics_diff,
)


def test_diff_metrics_basic():
    old = {"total_return": 0.10, "num_trades": 50}
    new = {"total_return": 0.12, "num_trades": 40}
    diff = diff_metrics(old, new)
    assert diff["total_return"].delta == pytest.approx(0.02)
    assert diff["num_trades"].delta == -10


def test_diff_metrics_regression_flag():
    old = {"total_return": 0.10}
    new = {"total_return": 0.05}
    diff = diff_metrics(old, new, regression_thresholds={"total_return": -0.01})
    assert diff["total_return"].regression is True


def test_diff_backtest_results():
    old_results = {
        "summary": {"metrics": {"total_return": 0.10, "num_trades": 10}},
        "trades": [{"pnl": 10}, {"pnl": -5}],
    }
    new_results = {
        "summary": {"metrics": {"total_return": 0.12, "num_trades": 8}},
        "trades": [{"pnl": 5}],
    }
    diff = diff_backtest_results(old_results, new_results)
    assert diff["metrics"]["total_return"]["delta"] == pytest.approx(0.02)
    assert diff["trades"]["delta"] == -1


def test_summarize_metric_deltas():
    diff = diff_metrics({"a": 1.0}, {"a": 2.0})
    summary = summarize_metric_deltas(diff)
    assert "a: +1.0000" in summary


def test_summarize_metrics_diff():
    diff = {
        "total_return": {"old": 0.1, "new": 0.2, "delta": 0.1, "regression": False},
        "num_trades": {"old": 10, "new": 8, "delta": -2, "regression": False},
    }
    summary = summarize_metrics_diff(diff)
    assert "total_return: +0.1000" in summary
    assert "num_trades: -2.0000" in summary
