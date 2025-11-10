"""
Position tracker for backtest.

Tracks open positions, calculates PnL, and manages trade lifecycle.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Position:
    """Represents an open position with partial exit support."""

    symbol: str
    side: str  # "LONG" or "SHORT"
    initial_size: float  # Original position size
    current_size: float  # Remaining size after partials
    entry_price: float
    entry_time: datetime
    entry_reasons: list[str] = field(default_factory=list)
    unrealized_pnl: float = 0.0
    partial_exits: list = field(default_factory=list)  # [(size, price, reason, time)]

    # Exit-specific fields (för symmetrisk Fibonacci exit logic)
    exit_swing_high: float = 0.0  # Swing high för denna position's exits
    exit_swing_low: float = 0.0  # Swing low för denna position's exits
    exit_fib_levels: dict = field(default_factory=dict)  # {0.382: price, 0.5: price, ...}
    exit_swing_timestamp: datetime | None = None  # När swing fastställdes
    exit_swing_updated: int = 0  # Antal gånger swing uppdaterats

    # Frozen exit context (en referens per trade)
    exit_ctx: dict | None = (
        None  # {"swing_id": str, "fib": {"0.382":..., "0.5":..., "0.618":...}, "swing_bounds": (low, high)}
    )
    entry_fib_debug: dict[str, Any] = field(default_factory=dict)
    exit_fib_log: list[dict[str, Any]] = field(default_factory=list)

    @property
    def size(self) -> float:
        """Backward compatibility: return current size."""
        return self.current_size

    def get_realized_pnl(self) -> float:
        """Calculate PnL from partial exits."""
        realized = 0.0
        for exit_size, exit_price, _reason, _exit_time in self.partial_exits:
            if self.side == "LONG":
                realized += exit_size * (exit_price - self.entry_price)
            else:  # SHORT
                realized += exit_size * (self.entry_price - exit_price)
        return realized

    def get_total_exits_size(self) -> float:
        """Get total size of partial exits."""
        return sum(exit_size for exit_size, _, _, _ in self.partial_exits)

    def get_remaining_pct(self) -> float:
        """Get percentage of position remaining."""
        return self.current_size / self.initial_size if self.initial_size > 0 else 0.0

    def update_pnl(self, current_price: float) -> float:
        """Update and return unrealized PnL (for remaining position only)."""
        if self.side == "LONG":
            self.unrealized_pnl = (current_price - self.entry_price) * self.current_size
        elif self.side == "SHORT":
            self.unrealized_pnl = (self.entry_price - current_price) * self.current_size
        else:
            self.unrealized_pnl = 0.0
        return self.unrealized_pnl

    def arm_exit_context(self, htf_ctx: dict) -> None:
        """
        Freeze HTF swing and Fibonacci levels for this position.

        Args:
            htf_ctx: HTF Fibonacci context with swing_id, levels, swing_bounds
        """
        self.exit_ctx = {
            "swing_id": htf_ctx.get("swing_id", "unknown"),
            "fib": dict(htf_ctx.get("levels", {})),  # freeze copy
            "swing_bounds": (htf_ctx.get("swing_low", 0.0), htf_ctx.get("swing_high", 0.0)),
            "armed_at": self.entry_time,
        }


@dataclass
class Trade:
    """Represents a completed trade (full or partial)."""

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
    exit_reason: str = "MANUAL"  # Why was this trade closed
    is_partial: bool = False  # True if partial exit, False if full
    remaining_size: float = 0.0  # Size remaining after this exit (for partials)
    position_id: str = ""  # Link partial exits to same position
    entry_reasons: list[str] = field(default_factory=list)
    entry_fib_debug: dict[str, Any] | None = None
    exit_fib_debug: list[dict[str, Any]] = field(default_factory=list)


class PositionTracker:
    """Tracks positions och tradelogik under backtest."""

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
        self._pending_reasons: list[str] = []

        # Statistics
        self.total_commission = 0.0
        self.max_capital = initial_capital
        self.min_capital = initial_capital

    def set_pending_reasons(self, reasons: list[str]) -> None:
        """Spara senaste beslutsorsaker innan eventuell entry."""
        self._pending_reasons = list(reasons)

    def pending_reasons(self) -> list[str]:
        """Hämta sparade beslutsorsaker för nästkommande entry."""
        return list(self._pending_reasons)

    def clear_pending_reasons(self) -> None:
        """Nollställ sparade orsaker efter att entry har skett."""
        self._pending_reasons.clear()

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
        self,
        side: str,
        size: float,
        price: float,
        timestamp: datetime,
        symbol: str,
        meta: dict | None = None,
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

        # Create position with partial exit support
        state_reasons = self.pending_reasons()
        self.clear_pending_reasons()
        self.position = Position(
            symbol=symbol,
            side=side,
            initial_size=size,
            current_size=size,
            entry_price=effective_price,
            entry_time=timestamp,
            entry_reasons=state_reasons,
        )

    def close_position_with_reason(
        self, price: float, timestamp: datetime, reason: str = "MANUAL"
    ) -> Trade | None:
        """
        Close the current position with a specific reason.

        Args:
            price: Exit price
            timestamp: Exit timestamp
            reason: Reason for exit (e.g., "SL", "TP", "TIME", "CONF_DROP", "REGIME_CHANGE")

        Returns:
            Completed Trade object or None if no position
        """
        if self.position is None:
            return None

        # Apply slippage
        effective_price = price * (
            1 - self.slippage_rate if self.position.side == "LONG" else 1 + self.slippage_rate
        )

        # Calculate PnL (for remaining position only)
        if self.position.side == "LONG":
            pnl = (effective_price - self.position.entry_price) * self.position.current_size
        else:  # SHORT
            pnl = (self.position.entry_price - effective_price) * self.position.current_size

        # Add realized PnL from partial exits
        realized_pnl = self.position.get_realized_pnl()
        total_pnl = pnl + realized_pnl

        # Calculate commission (for remaining position only)
        notional = self.position.current_size * effective_price
        commission = notional * self.commission_rate
        self.total_commission += commission

        # Update capital (only from remaining position - partials already accounted for)
        self.capital += pnl - commission

        # Calculate PnL percentage (total PnL vs original position size)
        original_notional = self.position.initial_size * self.position.entry_price
        total_pnl_pct = (total_pnl / original_notional) * 100 if original_notional > 0 else 0.0

        # Generate position ID for linking
        position_id = f"{self.position.symbol}_{self.position.entry_time.isoformat()}"

        # Record trade (final close of remaining position)
        trade = Trade(
            symbol=self.position.symbol,
            side=f"CLOSE_{self.position.side}",  # "CLOSE_LONG" or "CLOSE_SHORT"
            size=self.position.current_size,  # Remaining size being closed
            entry_price=self.position.entry_price,
            entry_time=self.position.entry_time,
            exit_price=effective_price,
            exit_time=timestamp,
            pnl=total_pnl,  # Total PnL including partials
            pnl_pct=total_pnl_pct,  # Based on original position
            commission=commission,
            exit_reason=reason,
            is_partial=False,  # Final close
            remaining_size=0.0,  # Nothing left
            position_id=position_id,
            entry_reasons=list(self.position.entry_reasons or []),
        )
        final_debug = {
            "timestamp": timestamp.isoformat(),
            "reason": reason,
            "pnl_pct": total_pnl_pct,
            "remaining_size": 0.0,
        }
        self.position.exit_fib_log.append(final_debug)
        if self.position.entry_fib_debug:
            trade.entry_fib_debug = dict(self.position.entry_fib_debug)
        if self.position.exit_fib_log:
            trade.exit_fib_debug = list(self.position.exit_fib_log)
        self.trades.append(trade)

        # Clear position
        self.position = None

        return trade

    def partial_close(
        self, close_size: float, price: float, timestamp: datetime, reason: str = "PARTIAL"
    ) -> Trade | None:
        """
        Close part of the current position.

        Args:
            close_size: Size to close (must be <= current_size)
            price: Exit price
            timestamp: Exit timestamp
            reason: Reason for partial exit (e.g., "TP1_0382", "TP2_05")

        Returns:
            Trade object for the partial exit, or None if no position
        """
        if self.position is None:
            return None

        # Validate close size
        if close_size <= 0:
            return None

        # Limit to available size
        actual_close_size = min(close_size, self.position.current_size)

        # Apply slippage
        effective_price = price * (
            1 - self.slippage_rate if self.position.side == "LONG" else 1 + self.slippage_rate
        )

        # Calculate PnL for this partial exit
        if self.position.side == "LONG":
            pnl = (effective_price - self.position.entry_price) * actual_close_size
        else:  # SHORT
            pnl = (self.position.entry_price - effective_price) * actual_close_size

        # Calculate commission
        notional = actual_close_size * effective_price
        commission = notional * self.commission_rate
        self.total_commission += commission

        # Update capital
        self.capital += pnl - commission

        # Calculate PnL percentage (based on original position size)
        entry_notional = actual_close_size * self.position.entry_price
        pnl_pct = (pnl / entry_notional) * 100 if entry_notional > 0 else 0.0

        # Update position
        self.position.current_size -= actual_close_size
        remaining_size = self.position.current_size

        # Record partial exit in position
        self.position.partial_exits.append((actual_close_size, effective_price, reason, timestamp))

        self.position.exit_fib_log.append(
            {
                "timestamp": timestamp.isoformat(),
                "reason": reason,
                "action": "PARTIAL",
                "close_size": actual_close_size,
                "remaining_size": remaining_size,
            }
        )

        # Generate position ID for linking partial exits
        position_id = f"{self.position.symbol}_{self.position.entry_time.isoformat()}"

        # Create trade record
        trade = Trade(
            symbol=self.position.symbol,
            side=f"CLOSE_{self.position.side}",  # "CLOSE_LONG" or "CLOSE_SHORT"
            size=actual_close_size,
            entry_price=self.position.entry_price,
            entry_time=self.position.entry_time,
            exit_price=effective_price,
            exit_time=timestamp,
            pnl=pnl,
            pnl_pct=pnl_pct,
            commission=commission,
            exit_reason=reason,
            is_partial=True,
            remaining_size=remaining_size,
            position_id=position_id,
            entry_reasons=list(self.position.entry_reasons or []),
        )
        if self.position.entry_fib_debug:
            trade.entry_fib_debug = dict(self.position.entry_fib_debug)
        if self.position.exit_fib_log:
            trade.exit_fib_debug = list(self.position.exit_fib_log)

        self.trades.append(trade)

        # If position fully closed, remove it
        if self.position.current_size <= 1e-8:  # Essentially zero
            self.position = None
            # Mark the last trade as full close
            trade.is_partial = False

        # Update statistics
        self.max_capital = max(self.max_capital, self.capital)
        self.min_capital = min(self.min_capital, self.capital)

        return trade

    def _close_position(self, price: float, timestamp: datetime):
        """Close the current position (internal use)."""
        self.close_position_with_reason(price, timestamp, reason="OPPOSITE_SIGNAL")

    def get_unrealized_pnl_pct(self, current_price: float) -> float:
        """Get total PnL percentage for open position (realized + unrealized)."""
        if self.position is None:
            return 0.0

        # Unrealized PnL from remaining position
        if self.position.side == "LONG":
            unrealized_pnl = (
                current_price - self.position.entry_price
            ) * self.position.current_size
        else:  # SHORT
            unrealized_pnl = (
                self.position.entry_price - current_price
            ) * self.position.current_size

        # Realized PnL from partial exits
        realized_pnl = self.position.get_realized_pnl()

        # Total PnL vs original position size
        total_pnl = unrealized_pnl + realized_pnl
        original_notional = self.position.initial_size * self.position.entry_price
        return (total_pnl / original_notional) * 100 if original_notional > 0 else 0.0

    def get_bars_held(self, current_timestamp: datetime) -> int:
        """Get number of bars position has been held (approximate, assumes 1 bar per update)."""
        if self.position is None:
            return 0
        # Note: This is approximate - actual bars held tracked by BacktestEngine
        return 0  # BacktestEngine will track this

    def _close_position_legacy(self, price: float, timestamp: datetime):
        """LEGACY: Close the current position (kept for compatibility)."""
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
        # Local import to avoid global dependency if numpy isn't needed elsewhere
        import numpy as _np

        total_return = (self.capital - self.initial_capital) / self.initial_capital * 100
        num_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t.pnl > 0]
        losing_trades = [t for t in self.trades if t.pnl < 0]

        win_rate = len(winning_trades) / num_trades * 100 if num_trades > 0 else 0
        avg_win = sum(t.pnl for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t.pnl for t in losing_trades) / len(losing_trades) if losing_trades else 0

        # Compute profit factor using gross profit/loss (industry standard)
        gross_profit = sum(t.pnl for t in winning_trades) if winning_trades else 0.0
        gross_loss = abs(sum(t.pnl for t in losing_trades)) if losing_trades else 0.0
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float("inf")

        # Compute max drawdown (%) from equity curve when available
        if self.equity_curve:
            equity_values = [p.get("total_equity", self.capital) for p in self.equity_curve]
            if len(equity_values) > 1:
                running_max = _np.maximum.accumulate(equity_values)
                drawdowns = (running_max - _np.asarray(equity_values)) / running_max * 100.0
                max_drawdown = float(_np.max(drawdowns)) if drawdowns.size > 0 else 0.0
            else:
                max_drawdown = 0.0
        else:
            max_drawdown = 0.0

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
            "profit_factor": profit_factor,
            "max_capital": self.max_capital,
            "min_capital": self.min_capital,
            "max_drawdown": max_drawdown,
        }

    def log_entry_fib_debug(self, debug: dict[str, Any] | None) -> None:
        if self.position is None:
            return
        self.position.entry_fib_debug = dict(debug or {})

    def append_exit_fib_debug(self, debug: dict[str, Any] | None) -> None:
        if self.position is None or debug is None:
            return
        payload = dict(debug)
        last = self.position.exit_fib_log[-1] if self.position.exit_fib_log else None
        if last is not None:
            last_actions = last.get("actions") if isinstance(last, dict) else None
            new_actions = payload.get("actions") if isinstance(payload, dict) else None
            if new_actions and new_actions == last_actions:
                return
        if last == payload:
            return
        self.position.exit_fib_log.append(payload)
