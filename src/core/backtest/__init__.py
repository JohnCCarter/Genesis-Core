"""
Backtest module for Genesis-Core.

Provides tools for backtesting trading strategies on historical data.
"""

from core.backtest.engine import BacktestEngine
from core.backtest.metrics import (
    calculate_backtest_metrics,
    calculate_metrics,  # Backward compatibility
    print_metrics_report,  # Backward compatibility
)
from core.backtest.position_tracker import PositionTracker
from core.backtest.trade_logger import TradeLogger

__all__ = [
    "BacktestEngine",
    "PositionTracker",
    "calculate_backtest_metrics",
    "calculate_metrics",
    "print_metrics_report",
    "TradeLogger",
]
