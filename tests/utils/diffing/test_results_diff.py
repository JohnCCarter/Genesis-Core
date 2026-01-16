from __future__ import annotations

import pytest

from core.utils.diffing.results_diff import (
    check_backtest_comparability,
    diff_backtest_results,
    diff_metrics,
    format_comparability_issues,
    summarize_metric_deltas,
    summarize_metrics_diff,
)


def _base_results(*, score_version: str | None = None) -> dict:
    payload: dict = {"runtime_version": 123}
    if score_version is not None:
        payload["score"] = {"score": 0.0, "score_version": score_version, "metrics": {}}
    payload["backtest_info"] = {}
    return payload


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


def test_check_backtest_comparability_score_version_mismatch_is_fail_fast():
    old = _base_results(score_version="v1")
    new = _base_results(score_version="v2")
    with pytest.raises(ValueError, match=r"score_version"):
        check_backtest_comparability(old, new)


def test_check_backtest_comparability_score_version_missing_warns():
    old = _base_results(score_version="v2")
    new = _base_results(score_version=None)
    warnings = check_backtest_comparability(old, new, warn_only=True)
    assert any("missing:score_version" in w for w in warnings)


def test_check_backtest_comparability_execution_mode_mismatch_is_fail_fast():
    old = _base_results(score_version="v2")
    new = _base_results(score_version="v2")
    old["backtest_info"]["execution_mode"] = {"fast_window": True, "env_precompute_features": True}
    new["backtest_info"]["execution_mode"] = {"fast_window": False, "env_precompute_features": True}
    with pytest.raises(ValueError, match=r"execution_mode\.fast_window"):
        check_backtest_comparability(old, new)


def test_check_backtest_comparability_htf_drift_is_warn_only():
    old = _base_results(score_version="v2")
    new = _base_results(score_version="v2")
    old["backtest_info"]["htf"] = {"htf_candles_loaded": True}
    new["backtest_info"]["htf"] = {"htf_candles_loaded": False}
    warnings = check_backtest_comparability(old, new)
    assert any("htf.htf_candles_loaded" in w for w in warnings)


def test_format_comparability_issues_truncates():
    issues = [f"x{i}" for i in range(10)]
    s = format_comparability_issues(issues, max_items=3)
    assert s.startswith("x0; x1; x2")
    assert s.endswith("; ...")
