"""
Backtest Metrics Calculations for Genesis-Core

Comprehensive metrics for evaluating trading strategy performance.
"""

from typing import Any

import numpy as np
import pandas as pd


def calculate_backtest_metrics(
    trades: list[dict[str, Any]], initial_capital: float = 10000.0, risk_free_rate: float = 0.02
) -> dict[str, float]:
    """
    Calculate comprehensive backtest metrics.

    Args:
        trades: List of trade dictionaries
        initial_capital: Starting capital
        risk_free_rate: Risk-free rate for Sharpe calculation

    Returns:
        Dictionary of calculated metrics
    """
    if not trades:
        return _empty_metrics()

    # Extract trade data
    pnls = [trade.get("pnl", 0) for trade in trades]
    returns_pct = [(pnl / initial_capital) * 100 for pnl in pnls]

    # Basic metrics
    total_trades = len(trades)
    winning_trades = [pnl for pnl in pnls if pnl > 0]
    losing_trades = [pnl for pnl in pnls if pnl < 0]

    total_pnl = sum(pnls)
    total_return_pct = (total_pnl / initial_capital) * 100

    win_rate = len(winning_trades) / total_trades * 100 if total_trades > 0 else 0.0

    # Profit metrics
    gross_profit = sum(winning_trades) if winning_trades else 0
    gross_loss = abs(sum(losing_trades)) if losing_trades else 1
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")

    avg_win = np.mean(winning_trades) if winning_trades else 0.0
    avg_loss = np.mean(losing_trades) if losing_trades else 0.0
    expectancy = np.mean(pnls) if pnls else 0.0

    # Risk metrics
    if len(returns_pct) > 1:
        returns_std = np.std(returns_pct, ddof=1)
        sharpe_ratio = (
            (np.mean(returns_pct) - risk_free_rate / 12) / returns_std if returns_std > 0 else 0.0
        )
    else:
        sharpe_ratio = 0.0
        returns_std = 0.0

    # Drawdown (simplified - based on cumulative returns)
    cumulative_returns = np.cumsum(returns_pct)
    running_max = np.maximum.accumulate(cumulative_returns) if len(cumulative_returns) > 0 else [0]
    drawdowns = running_max - cumulative_returns
    max_drawdown = np.max(drawdowns) if len(drawdowns) > 0 else 0.0

    # Trade duration (if available)
    durations = []
    for trade in trades:
        if "entry_time" in trade and "exit_time" in trade:
            entry_time = pd.to_datetime(trade["entry_time"])
            exit_time = pd.to_datetime(trade["exit_time"])
            duration_hours = (exit_time - entry_time).total_seconds() / 3600
            durations.append(duration_hours)

    avg_duration_hours = np.mean(durations) if durations else 0.0

    return {
        "total_return": total_return_pct,
        "total_pnl": total_pnl,
        "total_trades": total_trades,
        "winning_trades": len(winning_trades),
        "losing_trades": len(losing_trades),
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "gross_profit": gross_profit,
        "gross_loss": gross_loss,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "expectancy": expectancy,
        "sharpe_ratio": sharpe_ratio,
        "max_drawdown": max_drawdown,
        "returns_std": returns_std,
        "avg_duration_hours": avg_duration_hours,
        "trade_returns": returns_pct,
    }


def _empty_metrics() -> dict[str, float]:
    """Return empty metrics for cases with no trades."""
    return {
        "total_return": 0.0,
        "total_pnl": 0.0,
        "total_trades": 0,
        "winning_trades": 0,
        "losing_trades": 0,
        "win_rate": 0.0,
        "profit_factor": 0.0,
        "gross_profit": 0.0,
        "gross_loss": 0.0,
        "avg_win": 0.0,
        "avg_loss": 0.0,
        "expectancy": 0.0,
        "sharpe_ratio": 0.0,
        "max_drawdown": 0.0,
        "returns_std": 0.0,
        "avg_duration_hours": 0.0,
        "trade_returns": [],
    }


def compare_strategies(
    strategy_results: dict[str, dict[str, float]], baseline_name: str = "BASELINE"
) -> dict[str, dict[str, float]]:
    """
    Compare multiple strategy results against a baseline.

    Args:
        strategy_results: Dict of strategy_name -> metrics
        baseline_name: Name of baseline strategy

    Returns:
        Dict of comparisons with improvement metrics
    """
    if baseline_name not in strategy_results:
        raise ValueError(f"Baseline strategy '{baseline_name}' not found in results")

    baseline = strategy_results[baseline_name]
    comparisons = {}

    for strategy_name, metrics in strategy_results.items():
        if strategy_name == baseline_name:
            continue

        comparison = {}

        # Calculate improvements
        comparison["return_improvement"] = metrics["total_return"] - baseline["total_return"]
        comparison["return_improvement_pct"] = (
            (metrics["total_return"] / baseline["total_return"] - 1) * 100
            if baseline["total_return"] != 0
            else 0.0
        )

        comparison["sharpe_improvement"] = metrics["sharpe_ratio"] - baseline["sharpe_ratio"]
        comparison["drawdown_improvement"] = (
            baseline["max_drawdown"] - metrics["max_drawdown"]
        )  # Lower is better

        comparison["win_rate_improvement"] = metrics["win_rate"] - baseline["win_rate"]
        comparison["trade_count_change"] = metrics["total_trades"] - baseline["total_trades"]

        # Relative metrics
        comparison["profit_factor_ratio"] = (
            metrics["profit_factor"] / baseline["profit_factor"]
            if baseline["profit_factor"] > 0
            else float("inf")
        )

        comparisons[strategy_name] = comparison

    return comparisons


# Backward compatibility alias
def calculate_metrics(
    results: dict | list[dict[str, Any]], initial_capital: float = 10000.0
) -> dict[str, float]:
    """Backward compatibility wrapper for calculate_backtest_metrics."""
    # Handle both old API (full results dict) and new API (trades list)
    if isinstance(results, dict):
        # Old API: results dict with "trades" key
        trades = results.get("trades", [])
        summary = results.get("summary", {})
        initial_capital = summary.get("initial_capital", initial_capital)
    else:
        # New API: trades list directly
        trades = results

    return calculate_backtest_metrics(trades, initial_capital)


def print_metrics_report(metrics: dict[str, float], backtest_info: dict = None):
    """Print metrics report (backward compatibility)."""
    print("\n=== Backtest Metrics ===")
    if backtest_info:
        print(f"Symbol: {backtest_info.get('symbol', 'N/A')}")
        print(f"Timeframe: {backtest_info.get('timeframe', 'N/A')}")
        print(
            f"Period: {backtest_info.get('start_date', 'N/A')} to {backtest_info.get('end_date', 'N/A')}"
        )
        print()
    print(f"Total Return: {metrics.get('total_return', 0):.2f}%")
    print(f"Total Trades: {metrics.get('total_trades', 0)}")
    print(f"Win Rate: {metrics.get('win_rate', 0):.1f}%")
    print(f"Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.3f}")
    print(f"Max Drawdown: {metrics.get('max_drawdown', 0):.2f}%")
    print(f"Profit Factor: {metrics.get('profit_factor', 0):.2f}")


def calculate_statistical_significance(
    returns_a: list[float], returns_b: list[float], alpha: float = 0.05
) -> dict[str, Any]:
    """
    Calculate statistical significance between two return series.

    Args:
        returns_a: Returns from strategy A
        returns_b: Returns from strategy B
        alpha: Significance level

    Returns:
        Statistical test results
    """
    from scipy import stats

    if len(returns_a) == 0 or len(returns_b) == 0:
        return {
            "test_type": "insufficient_data",
            "statistic": 0.0,
            "p_value": 1.0,
            "significant": False,
            "effect_size": 0.0,
        }

    # Choose appropriate test
    if len(returns_a) == len(returns_b):
        # Paired t-test (assumes same trades)
        if len(returns_a) > 1:
            statistic, p_value = stats.ttest_rel(returns_a, returns_b)
            test_type = "paired_ttest"
        else:
            statistic, p_value = 0.0, 1.0
            test_type = "single_observation"
    else:
        # Independent t-test
        if len(returns_a) > 1 and len(returns_b) > 1:
            statistic, p_value = stats.ttest_ind(returns_a, returns_b)
            test_type = "independent_ttest"
        else:
            statistic, p_value = 0.0, 1.0
            test_type = "insufficient_data"

    # Effect size (Cohen's d)
    if len(returns_a) > 0 and len(returns_b) > 0:
        pooled_std = np.sqrt(
            (
                (len(returns_a) - 1) * np.var(returns_a, ddof=1)
                + (len(returns_b) - 1) * np.var(returns_b, ddof=1)
            )
            / (len(returns_a) + len(returns_b) - 2)
        )
        effect_size = (
            (np.mean(returns_a) - np.mean(returns_b)) / pooled_std if pooled_std > 0 else 0.0
        )
    else:
        effect_size = 0.0

    return {
        "test_type": test_type,
        "statistic": statistic,
        "p_value": p_value,
        "significant": p_value < alpha,
        "effect_size": effect_size,
        "alpha": alpha,
    }
