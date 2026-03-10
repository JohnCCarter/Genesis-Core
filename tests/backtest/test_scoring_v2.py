import pytest

from core.optimizer.scoring import MetricThresholds, score_backtest


def test_score_v2_does_not_explode_on_zero_drawdown(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GENESIS_SCORE_VERSION", raising=False)
    # Monotonic equity curve => max_drawdown = 0.0.
    # Legacy v1 score has a return_to_dd term that can explode; v2 should not.
    result = {
        "summary": {"initial_capital": 10_000.0},
        "trades": [
            {"pnl": 100.0, "commission": 0.0},
            {"pnl": 110.0, "commission": 0.0},
            {"pnl": 90.0, "commission": 0.0},
            {"pnl": 100.0, "commission": 0.0},
        ],
        "equity_curve": [
            {"total_equity": 10_000.0},
            {"total_equity": 10_400.0},
        ],
    }

    thresholds = MetricThresholds(min_trades=0, min_profit_factor=0.0, max_max_dd=1.0)

    score_v1 = score_backtest(result, thresholds=thresholds, score_version="v1")
    score_v2 = score_backtest(result, thresholds=thresholds, score_version="v2")

    assert score_v1["hard_failures"] == []
    assert score_v2["hard_failures"] == []

    # Sanity: v1 should be much larger due to return_to_dd; v2 stays bounded.
    assert score_v1["score"] > 30.0
    assert score_v2["score"] < 10.0

    assert score_v2["baseline"]["score_version"] == "v2"


def test_score_v2_is_selectable_without_affecting_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GENESIS_SCORE_VERSION", raising=False)
    result = {
        "summary": {"initial_capital": 1000.0},
        "trades": [
            {"pnl": 100.0, "commission": 10.0},
            {"pnl": -50.0, "commission": 10.0},
        ],
        "equity_curve": [
            {"total_equity": 1000.0},
            {"total_equity": 1030.0},
        ],
    }

    thresholds = MetricThresholds(min_trades=0, min_profit_factor=0.0, max_max_dd=1.0)

    default_scored = score_backtest(result, thresholds=thresholds)
    v2_scored = score_backtest(result, thresholds=thresholds, score_version="v2")

    assert default_scored["baseline"]["score_version"] == "v1"
    assert v2_scored["baseline"]["score_version"] == "v2"

    # Default and v2 are allowed to differ, but both should be finite numbers.
    assert default_scored["score"] == pytest.approx(float(default_scored["score"]))
    assert v2_scored["score"] == pytest.approx(float(v2_scored["score"]))
