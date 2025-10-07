"""
Position tracker for backtest.

Tracks open positions, calculates PnL, and manages trade lifecycle.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Position:
    """Represents an open position."""

    symbol: str
    side: str  # "LONG" or "SHORT"
    size: float
    entry_price: float
    entry_time: datetime
    unrealized_pnl: float = 0.0

    def update_pnl(self, current_price: float) -> float:
        """Update and return unrealized PnL."""
        if self.side == "LONG":
            self.unrealized_pnl = (current_price - self.entry_price) * self.size
        elif self.side == "SHORT":
            self.unrealized_pnl = (self.entry_price - current_price) * self.size
        else:
            self.unrealized_pnl = 0.0
        return self.unrealized_pnl


@dataclass
class Trade:
    """Represents a completed trade."""

    symbol: str
    side: str
    size: float
    entry_price: float
    entry_time: datetime
    exit_price: float
    exit_time: datetime
    pnl: float
    pnl_pct: float
    commission: float = 0.0


class PositionTracker:
    """
    Tracks positions and calculates PnL during backtest.

    Features:
    - Track open positions
    - Calculate unrealized/realized PnL
    - Handle LONG/SHORT entries/exits
    - Commission simulation
    - Trade history
    """

    def __init__(
        self,
        initial_capital: float = 10000.0,
        commission_rate: float = 0.001,  # 0.1% per trade
        slippage_rate: float = 0.0005,  # 0.05% slippage
    ):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate

        self.position: Position | None = None
        self.trades: list[Trade] = []
        self.equity_curve: list[dict] = []

        # Statistics
        self.total_commission = 0.0
        self.max_capital = initial_capital
        self.min_capital = initial_capital

    def has_position(self) -> bool:
        """Check if there's an open position."""
        return self.position is not None

    def execute_action(
        self,
        action: str,
        size: float,
        price: float,
        timestamp: datetime,
        symbol: str = "unknown",
    ) -> dict:
        """
        Execute a trading action.

        Args:
            action: "LONG", "SHORT", or "NONE"
            size: Position size
            price: Current market price
            timestamp: Timestamp of the action
            symbol: Trading symbol

        Returns:
            Dict with execution details
        """
        result = {"action": action, "executed": False, "reason": None}

        if action == "NONE":
            result["reason"] = "no_action"
            return result

        # Close existing position if action is opposite
        if self.position is not None:
            if (self.position.side == "LONG" and action == "SHORT") or (
                self.position.side == "SHORT" and action == "LONG"
            ):
                self._close_position(price, timestamp)
                result["reason"] = "closed_opposite"

        # Open new position if no position or after closing
        if self.position is None:
            self._open_position(action, size, price, timestamp, symbol)
            result["executed"] = True
            result["reason"] = "opened"
        else:
            result["reason"] = "already_in_position"

        return result

    def _open_position(
        self, side: str, size: float, price: float, timestamp: datetime, symbol: str
    ):
        """Open a new position."""
        # Apply slippage
        effective_price = price * (
            1 + self.slippage_rate if side == "LONG" else 1 - self.slippage_rate
        )

        # Calculate commission
        notional = size * effective_price
        commission = notional * self.commission_rate
        self.total_commission += commission
        self.capital -= commission

        # Create position
        self.position = Position(
            symbol=symbol,
            side=side,
            size=size,
            entry_price=effective_price,
            entry_time=timestamp,
        )

    def _close_position(self, price: float, timestamp: datetime):
        """Close the current position."""
        if self.position is None:
            return

        # Apply slippage
        effective_price = price * (
            1 - self.slippage_rate if self.position.side == "LONG" else 1 + self.slippage_rate
        )

        # Calculate PnL
        if self.position.side == "LONG":
            pnl = (effective_price - self.position.entry_price) * self.position.size
        else:  # SHORT
            pnl = (self.position.entry_price - effective_price) * self.position.size

        # Calculate commission
        notional = self.position.size * effective_price
        commission = notional * self.commission_rate
        self.total_commission += commission

        # Update capital
        self.capital += pnl - commission

        # Calculate PnL percentage
        entry_notional = self.position.size * self.position.entry_price
        pnl_pct = (pnl / entry_notional) * 100 if entry_notional > 0 else 0

        # Record trade
        trade = Trade(
            symbol=self.position.symbol,
            side=self.position.side,
            size=self.position.size,
            entry_price=self.position.entry_price,
            entry_time=self.position.entry_time,
            exit_price=effective_price,
            exit_time=timestamp,
            pnl=pnl,
            pnl_pct=pnl_pct,
            commission=commission,
        )
        self.trades.append(trade)

        # Clear position
        self.position = None

        # Update statistics
        self.max_capital = max(self.max_capital, self.capital)
        self.min_capital = min(self.min_capital, self.capital)

    def update_equity(self, price: float, timestamp: datetime):
        """Update equity curve with current market price."""
        unrealized_pnl = 0.0
        if self.position is not None:
            unrealized_pnl = self.position.update_pnl(price)

        total_equity = self.capital + unrealized_pnl

        self.equity_curve.append(
            {
                "timestamp": timestamp,
                "capital": self.capital,
                "unrealized_pnl": unrealized_pnl,
                "total_equity": total_equity,
            }
        )

        # Update statistics
        self.max_capital = max(self.max_capital, total_equity)
        self.min_capital = min(self.min_capital, total_equity)

    def close_all_positions(self, price: float, timestamp: datetime):
        """Force close all open positions (end of backtest)."""
        if self.position is not None:
            self._close_position(price, timestamp)

    def get_summary(self) -> dict:
        """Get backtest summary statistics."""
        total_return = (self.capital - self.initial_capital) / self.initial_capital * 100
        num_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t.pnl > 0]
        losing_trades = [t for t in self.trades if t.pnl < 0]

        win_rate = len(winning_trades) / num_trades * 100 if num_trades > 0 else 0
        avg_win = sum(t.pnl for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t.pnl for t in losing_trades) / len(losing_trades) if losing_trades else 0

        return {
            "initial_capital": self.initial_capital,
            "final_capital": self.capital,
            "total_return": total_return,
            "total_return_usd": self.capital - self.initial_capital,
            "total_commission": self.total_commission,
            "num_trades": num_trades,
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": win_rate,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "profit_factor": (abs(avg_win / avg_loss) if avg_loss != 0 else float("inf")),
            "max_capital": self.max_capital,
            "min_capital": self.min_capital,
        }
