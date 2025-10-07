"""
Backtest module for Genesis-Core.

Provides tools for backtesting trading strategies on historical data.
"""

from core.backtest.engine import BacktestEngine
from core.backtest.position_tracker import PositionTracker
from core.backtest.metrics import calculate_metrics
from core.backtest.trade_logger import TradeLogger

__all__ = [
    "BacktestEngine",
    "PositionTracker",
    "calculate_metrics",
    "TradeLogger",
]
