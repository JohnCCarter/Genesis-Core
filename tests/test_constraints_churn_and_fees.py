from __future__ import annotations

from core.optimizer.constraints import enforce_constraints
from core.optimizer.scoring import score_backtest


def test_constraints_max_trades_triggers() -> None:
    score_obj = {
        "metrics": {
            "num_trades": 101,
            "profit_factor": 2.0,
            "max_drawdown": 0.05,
        },
        "hard_failures": [],
    }
    config = {"constraints": {"max_trades": 100}}

    res = enforce_constraints(score_obj, config)
    assert not res.ok
    assert any(r.startswith("max_trades:") for r in res.reasons)


def test_constraints_max_total_commission_pct_triggers() -> None:
    score_obj = {
        "metrics": {
            "num_trades": 10,
            "profit_factor": 2.0,
            "max_drawdown": 0.05,
            "total_commission_pct": 0.051,
        },
        "hard_failures": [],
    }
    config = {"constraints": {"max_total_commission_pct": 0.05}}

    res = enforce_constraints(score_obj, config)
    assert not res.ok
    assert any(r.startswith("max_total_commission_pct:") for r in res.reasons)


def test_scoring_exposes_commission_metrics() -> None:
    # Two trades: one winner, one loser, both with commission.
    result = {
        "summary": {"initial_capital": 10000.0},
        "trades": [
            {"pnl": 100.0, "commission": 10.0},
            {"pnl": -50.0, "commission": 10.0},
        ],
        # Equity curve implies net of commissions is reflected in end equity.
        "equity_curve": [
            {"total_equity": 10000.0},
            {"total_equity": 10030.0},
        ],
    }

    score = score_backtest(result)
    metrics = score["metrics"]

    assert "total_commission" in metrics
    assert "total_commission_pct" in metrics
    assert metrics["total_commission"] == 20.0
    assert metrics["total_commission_pct"] == 20.0 / 10000.0
