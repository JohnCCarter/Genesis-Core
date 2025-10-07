"""
Performance metrics for backtest results.

Calculates trading performance metrics like Sharpe ratio, max drawdown, etc.
"""

import numpy as np
import pandas as pd


def calculate_metrics(results: dict) -> dict:
    """
    Calculate performance metrics from backtest results.

    Args:
        results: Backtest results dict from BacktestEngine.run()

    Returns:
        Dict with calculated metrics
    """
    summary = results.get("summary", {})
    equity_curve = results.get("equity_curve", [])
    trades = results.get("trades", [])

    # Basic metrics from summary
    metrics = {
        "total_return_pct": summary.get("total_return", 0.0),
        "total_return_usd": summary.get("total_return_usd", 0.0),
        "num_trades": summary.get("num_trades", 0),
        "win_rate": summary.get("win_rate", 0.0),
        "profit_factor": summary.get("profit_factor", 0.0),
    }

    # Calculate advanced metrics if data available
    if equity_curve:
        equity_df = pd.DataFrame(equity_curve)
        equity_series = equity_df["total_equity"]

        # Sharpe ratio (annualized)
        returns = equity_series.pct_change().dropna()
        if len(returns) > 0:
            sharpe = _calculate_sharpe(returns)
            metrics["sharpe_ratio"] = sharpe
        else:
            metrics["sharpe_ratio"] = 0.0

        # Max drawdown
        max_dd, max_dd_pct = _calculate_max_drawdown(equity_series)
        metrics["max_drawdown_usd"] = max_dd
        metrics["max_drawdown_pct"] = max_dd_pct

        # Sortino ratio (downside deviation)
        if len(returns) > 0:
            sortino = _calculate_sortino(returns)
            metrics["sortino_ratio"] = sortino
        else:
            metrics["sortino_ratio"] = 0.0

        # Calmar ratio (return / max drawdown)
        if max_dd_pct != 0:
            calmar = summary.get("total_return", 0.0) / abs(max_dd_pct)
            metrics["calmar_ratio"] = calmar
        else:
            metrics["calmar_ratio"] = 0.0

    # Trade statistics
    if trades:
        trades_df = pd.DataFrame(trades)

        # Average trade duration
        trades_df["duration"] = pd.to_datetime(trades_df["exit_time"]) - pd.to_datetime(
            trades_df["entry_time"]
        )
        avg_duration = trades_df["duration"].mean()
        metrics["avg_trade_duration_hours"] = (
            avg_duration.total_seconds() / 3600 if avg_duration else 0
        )

        # Consecutive wins/losses
        win_streak, loss_streak = _calculate_streaks(trades_df["pnl"].tolist())
        metrics["max_consecutive_wins"] = win_streak
        metrics["max_consecutive_losses"] = loss_streak

        # Expectancy (average profit per trade)
        metrics["expectancy"] = trades_df["pnl"].mean() if len(trades_df) > 0 else 0

    return metrics


def _calculate_sharpe(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    """
    Calculate annualized Sharpe ratio.

    Args:
        returns: Series of returns
        risk_free_rate: Risk-free rate (annual)

    Returns:
        Sharpe ratio
    """
    if len(returns) == 0 or returns.std() == 0:
        return 0.0

    excess_returns = returns - risk_free_rate / 252  # Daily risk-free rate
    sharpe = excess_returns.mean() / returns.std()

    # Annualize (assuming daily data, adjust if needed)
    sharpe_annual = sharpe * np.sqrt(252)

    return float(sharpe_annual)


def _calculate_sortino(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    """
    Calculate annualized Sortino ratio (uses downside deviation).

    Args:
        returns: Series of returns
        risk_free_rate: Risk-free rate (annual)

    Returns:
        Sortino ratio
    """
    if len(returns) == 0:
        return 0.0

    excess_returns = returns - risk_free_rate / 252
    downside_returns = returns[returns < 0]

    if len(downside_returns) == 0 or downside_returns.std() == 0:
        return 0.0

    sortino = excess_returns.mean() / downside_returns.std()
    sortino_annual = sortino * np.sqrt(252)

    return float(sortino_annual)


def _calculate_max_drawdown(equity: pd.Series) -> tuple[float, float]:
    """
    Calculate maximum drawdown (absolute and percentage).

    Args:
        equity: Series of equity values

    Returns:
        Tuple of (max_drawdown_usd, max_drawdown_pct)
    """
    if len(equity) == 0:
        return 0.0, 0.0

    # Calculate running maximum
    running_max = equity.expanding().max()

    # Calculate drawdown
    drawdown = equity - running_max
    drawdown_pct = (drawdown / running_max) * 100

    max_dd = float(drawdown.min())
    max_dd_pct = float(drawdown_pct.min())

    return max_dd, max_dd_pct


def _calculate_streaks(pnl_list: list[float]) -> tuple[int, int]:
    """
    Calculate maximum consecutive wins and losses.

    Args:
        pnl_list: List of PnL values

    Returns:
        Tuple of (max_win_streak, max_loss_streak)
    """
    if not pnl_list:
        return 0, 0

    max_win_streak = 0
    max_loss_streak = 0
    current_win_streak = 0
    current_loss_streak = 0

    for pnl in pnl_list:
        if pnl > 0:
            current_win_streak += 1
            current_loss_streak = 0
            max_win_streak = max(max_win_streak, current_win_streak)
        elif pnl < 0:
            current_loss_streak += 1
            current_win_streak = 0
            max_loss_streak = max(max_loss_streak, current_loss_streak)
        else:
            # Break-even trade
            current_win_streak = 0
            current_loss_streak = 0

    return max_win_streak, max_loss_streak


def print_metrics_report(metrics: dict, backtest_info: dict | None = None):
    """
    Print formatted metrics report.

    Args:
        metrics: Metrics dict from calculate_metrics()
        backtest_info: Optional backtest info for header
    """
    print(f"\n{'='*70}")
    print("BACKTEST PERFORMANCE METRICS")
    print(f"{'='*70}")

    if backtest_info:
        print(f"Symbol:       {backtest_info.get('symbol')}")
        print(f"Timeframe:    {backtest_info.get('timeframe')}")
        print(
            f"Period:       {backtest_info.get('start_date')} to "
            f"{backtest_info.get('end_date')}"
        )
        print(f"Bars:         {backtest_info.get('bars_processed'):,}")
        print(f"{'='*70}")

    print("\n[RETURNS]")
    print(f"  Total Return:     {metrics.get('total_return_pct', 0):.2f}%")
    print(f"  Total Return USD: ${metrics.get('total_return_usd', 0):,.2f}")

    print("\n[RISK METRICS]")
    print(f"  Sharpe Ratio:     {metrics.get('sharpe_ratio', 0):.2f}")
    print(f"  Sortino Ratio:    {metrics.get('sortino_ratio', 0):.2f}")
    print(f"  Calmar Ratio:     {metrics.get('calmar_ratio', 0):.2f}")
    print(
        f"  Max Drawdown:     {metrics.get('max_drawdown_pct', 0):.2f}% "
        f"(${metrics.get('max_drawdown_usd', 0):,.2f})"
    )

    print("\n[TRADE STATISTICS]")
    print(f"  Total Trades:     {metrics.get('num_trades', 0)}")
    print(f"  Win Rate:         {metrics.get('win_rate', 0):.2f}%")
    print(f"  Profit Factor:    {metrics.get('profit_factor', 0):.2f}")
    print(f"  Expectancy:       ${metrics.get('expectancy', 0):.2f}")
    print(f"  Avg Duration:     {metrics.get('avg_trade_duration_hours', 0):.1f}h")
    print(f"  Max Win Streak:   {metrics.get('max_consecutive_wins', 0)}")
    print(f"  Max Loss Streak:  {metrics.get('max_consecutive_losses', 0)}")

    print(f"{'='*70}\n")
