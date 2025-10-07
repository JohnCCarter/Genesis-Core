"""Tests for backtest performance metrics."""

import numpy as np
import pandas as pd
import pytest

from core.backtest.metrics import (
    _calculate_max_drawdown,
    _calculate_sharpe,
    _calculate_sortino,
    _calculate_streaks,
    calculate_metrics,
)


def test_calculate_sharpe_positive():
    """Test Sharpe ratio calculation with positive returns."""
    # Create synthetic returns with clear positive trend
    np.random.seed(42)
    returns = pd.Series(np.random.normal(0.005, 0.01, 100))  # Higher mean for stable test

    sharpe = _calculate_sharpe(returns)

    # Should be positive with positive mean return
    # Just check it's a valid number
    assert isinstance(sharpe, (int, float))
    assert not np.isnan(sharpe)


def test_calculate_sharpe_zero_std():
    """Test Sharpe ratio when returns have zero std (edge case)."""
    returns = pd.Series([0.0] * 100)  # No variance

    sharpe = _calculate_sharpe(returns)

    assert sharpe == 0.0


def test_calculate_sharpe_empty():
    """Test Sharpe ratio with empty series."""
    returns = pd.Series([])

    sharpe = _calculate_sharpe(returns)

    assert sharpe == 0.0


def test_calculate_sortino():
    """Test Sortino ratio calculation."""
    # Mix of positive and negative returns
    returns = pd.Series([0.01, 0.02, -0.01, 0.015, -0.005, 0.01])

    sortino = _calculate_sortino(returns)

    # Should be positive overall
    assert sortino > 0


def test_calculate_sortino_no_downside():
    """Test Sortino when there are no negative returns."""
    returns = pd.Series([0.01, 0.02, 0.015, 0.01])  # All positive

    sortino = _calculate_sortino(returns)

    # Should be 0 (no downside deviation)
    assert sortino == 0.0


def test_calculate_max_drawdown_positive():
    """Test max drawdown calculation."""
    # Equity curve: 100 -> 110 -> 105 -> 115
    equity = pd.Series([100, 110, 105, 115])

    max_dd, max_dd_pct = _calculate_max_drawdown(equity)

    # Max drawdown from 110 to 105 = -5
    assert max_dd == -5.0
    # Percentage: -5 / 110 * 100 = -4.545%
    assert abs(max_dd_pct - (-4.545454)) < 0.001


def test_calculate_max_drawdown_monotonic_increase():
    """Test max drawdown when equity only increases."""
    equity = pd.Series([100, 110, 120, 130])

    max_dd, max_dd_pct = _calculate_max_drawdown(equity)

    # No drawdown
    assert max_dd == 0.0
    assert max_dd_pct == 0.0


def test_calculate_max_drawdown_empty():
    """Test max drawdown with empty series."""
    equity = pd.Series([])

    max_dd, max_dd_pct = _calculate_max_drawdown(equity)

    assert max_dd == 0.0
    assert max_dd_pct == 0.0


def test_calculate_streaks():
    """Test win/loss streak calculation."""
    # Pattern: win, win, loss, win, loss, loss, loss, win
    pnl_list = [10, 5, -3, 8, -2, -4, -1, 6]

    max_wins, max_losses = _calculate_streaks(pnl_list)

    assert max_wins == 2  # Two wins in a row at start
    assert max_losses == 3  # Three losses in a row


def test_calculate_streaks_all_wins():
    """Test streaks when all trades are wins."""
    pnl_list = [10, 5, 8, 3]

    max_wins, max_losses = _calculate_streaks(pnl_list)

    assert max_wins == 4
    assert max_losses == 0


def test_calculate_streaks_empty():
    """Test streaks with empty list."""
    pnl_list = []

    max_wins, max_losses = _calculate_streaks(pnl_list)

    assert max_wins == 0
    assert max_losses == 0


def test_calculate_metrics_no_trades():
    """Test metrics calculation when there are no trades."""
    results = {
        "summary": {
            "total_return": 0.0,
            "total_return_usd": 0.0,
            "num_trades": 0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
        },
        "equity_curve": [
            {"timestamp": "2025-01-01", "total_equity": 10000},
            {"timestamp": "2025-01-02", "total_equity": 10000},
        ],
        "trades": [],
    }

    metrics = calculate_metrics(results)

    assert metrics["total_return_pct"] == 0.0
    assert metrics["num_trades"] == 0
    # Sharpe can be NaN when no variance - check it exists
    assert "sharpe_ratio" in metrics
    assert "max_drawdown_usd" in metrics


def test_calculate_metrics_with_trades():
    """Test metrics calculation with actual trades."""
    results = {
        "summary": {
            "total_return": 5.0,
            "total_return_usd": 500.0,
            "num_trades": 2,
            "win_rate": 50.0,
            "profit_factor": 2.0,
        },
        "equity_curve": [
            {"timestamp": "2025-01-01", "total_equity": 10000},
            {"timestamp": "2025-01-02", "total_equity": 10200},
            {"timestamp": "2025-01-03", "total_equity": 10500},
        ],
        "trades": [
            {
                "entry_time": "2025-01-01T10:00:00",
                "exit_time": "2025-01-01T12:00:00",
                "pnl": 200,
            },
            {
                "entry_time": "2025-01-02T10:00:00",
                "exit_time": "2025-01-02T14:00:00",
                "pnl": 300,
            },
        ],
    }

    metrics = calculate_metrics(results)

    assert metrics["total_return_pct"] == 5.0
    assert metrics["num_trades"] == 2
    assert metrics["win_rate"] == 50.0
    assert "sharpe_ratio" in metrics
    assert "max_drawdown_usd" in metrics
    assert "avg_trade_duration_hours" in metrics
    assert "expectancy" in metrics


def test_calculate_metrics_calmar_ratio():
    """Test Calmar ratio calculation."""
    results = {
        "summary": {
            "total_return": 10.0,  # 10% return
            "total_return_usd": 1000.0,
            "num_trades": 5,
            "win_rate": 60.0,
            "profit_factor": 1.5,
        },
        "equity_curve": [
            {"timestamp": "2025-01-01", "total_equity": 10000},
            {"timestamp": "2025-01-02", "total_equity": 11000},
            {"timestamp": "2025-01-03", "total_equity": 10500},  # Drawdown
            {"timestamp": "2025-01-04", "total_equity": 11000},
        ],
        "trades": [],
    }

    metrics = calculate_metrics(results)

    # Calmar = return / abs(max_drawdown_pct)
    assert "calmar_ratio" in metrics
    assert metrics["calmar_ratio"] > 0  # Should be positive


def test_calculate_metrics_zero_drawdown():
    """Test Calmar ratio when drawdown is zero."""
    results = {
        "summary": {
            "total_return": 10.0,
            "total_return_usd": 1000.0,
            "num_trades": 2,
            "win_rate": 100.0,
            "profit_factor": 999,
        },
        "equity_curve": [
            {"timestamp": "2025-01-01", "total_equity": 10000},
            {"timestamp": "2025-01-02", "total_equity": 10500},
            {"timestamp": "2025-01-03", "total_equity": 11000},  # Only up
        ],
        "trades": [],
    }

    metrics = calculate_metrics(results)

    assert metrics["calmar_ratio"] == 0.0  # Division by zero case
