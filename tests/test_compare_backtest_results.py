from __future__ import annotations

import json

from tools.compare_backtest_results import compare_backtest_payloads


def test_compare_backtest_payloads_pass_equal() -> None:
    baseline = {
        "score": 1.0,
        "summary": {
            "total_return": 0.1,
            "profit_factor": 1.2,
            "max_drawdown": 0.05,
            "total_trades": 10,
        },
    }
    candidate = json.loads(json.dumps(baseline))

    result = compare_backtest_payloads(baseline=baseline, candidate=candidate, mode="strict")
    assert result.status == "PASS"


def test_compare_backtest_payloads_fail_regression() -> None:
    baseline = {
        "score": 1.0,
        "summary": {
            "total_return": 0.1,
            "profit_factor": 1.2,
            "max_drawdown": 0.05,
            "total_trades": 10,
        },
    }
    candidate = {
        "score": 0.9,
        "summary": {
            "total_return": 0.0,
            "profit_factor": 1.1,
            "max_drawdown": 0.06,
            "total_trades": 9,
        },
    }

    result = compare_backtest_payloads(baseline=baseline, candidate=candidate, mode="strict")
    assert result.status == "FAIL"
    assert result.failure == "REGRESSION"


def test_compare_backtest_payloads_invalid_shape() -> None:
    result = compare_backtest_payloads(baseline=[], candidate={}, mode="strict")  # type: ignore[arg-type]
    assert result.status == "FAIL"
    assert result.failure == "INPUT_INVALID_SHAPE"
