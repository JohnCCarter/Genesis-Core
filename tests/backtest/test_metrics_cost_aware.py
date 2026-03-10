import pytest

from core.backtest.metrics import calculate_metrics
from core.optimizer.scoring import MetricThresholds, score_backtest


def test_calculate_metrics_uses_net_pnl_minus_commission() -> None:
    result = {
        "summary": {"initial_capital": 1000.0},
        "trades": [
            {"pnl": 100.0, "commission": 10.0},  # net +90
            {"pnl": -50.0, "commission": 10.0},  # net -60
        ],
        "equity_curve": [
            {"total_equity": 1000.0},
            {"total_equity": 1030.0},  # net +30
        ],
    }

    mt = calculate_metrics(result)

    assert mt["total_return"] == pytest.approx(3.0)
    assert mt["total_pnl"] == pytest.approx(30.0)
    assert mt["profit_factor"] == pytest.approx(90.0 / 60.0)
    assert mt["win_rate"] == pytest.approx(50.0)


def test_calculate_metrics_drawdown_from_equity_curve() -> None:
    result = {
        "summary": {"initial_capital": 1000.0},
        "trades": [],
        "equity_curve": [
            {"total_equity": 1000.0},
            {"total_equity": 1100.0},
            {"total_equity": 900.0},
            {"total_equity": 950.0},
        ],
    }

    mt = calculate_metrics(result)

    # Peak-to-trough drawdown: (1100-900)/1100 = 18.1818%
    assert mt["max_drawdown"] == pytest.approx((1100.0 - 900.0) / 1100.0 * 100.0)


def test_score_backtest_sees_net_total_return() -> None:
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

    thresholds = MetricThresholds(min_trades=0, min_profit_factor=1.0, max_max_dd=1.0)
    scored = score_backtest(result, thresholds=thresholds)

    assert scored["hard_failures"] == []
    assert scored["metrics"]["total_return"] == pytest.approx(0.03)
    assert scored["metrics"]["profit_factor"] == pytest.approx(90.0 / 60.0)
