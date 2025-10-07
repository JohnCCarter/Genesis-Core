"""Tests for backtest position tracker."""

from datetime import datetime

from core.backtest.position_tracker import Position, PositionTracker


def test_position_update_pnl_long():
    """Test PnL calculation for LONG position."""
    pos = Position(
        symbol="tBTCUSD",
        side="LONG",
        size=0.1,
        entry_price=100.0,
        entry_time=datetime.now(),
    )

    # Price goes up - profit
    pnl = pos.update_pnl(110.0)
    assert pnl == 1.0  # (110 - 100) * 0.1
    assert pos.unrealized_pnl == 1.0

    # Price goes down - loss
    pnl = pos.update_pnl(90.0)
    assert pnl == -1.0  # (90 - 100) * 0.1
    assert pos.unrealized_pnl == -1.0


def test_position_update_pnl_short():
    """Test PnL calculation for SHORT position."""
    pos = Position(
        symbol="tBTCUSD",
        side="SHORT",
        size=0.1,
        entry_price=100.0,
        entry_time=datetime.now(),
    )

    # Price goes down - profit
    pnl = pos.update_pnl(90.0)
    assert pnl == 1.0  # (100 - 90) * 0.1
    assert pos.unrealized_pnl == 1.0

    # Price goes up - loss
    pnl = pos.update_pnl(110.0)
    assert pnl == -1.0  # (100 - 110) * 0.1
    assert pos.unrealized_pnl == -1.0


def test_position_tracker_initialization():
    """Test PositionTracker initialization."""
    tracker = PositionTracker(initial_capital=10000.0, commission_rate=0.001, slippage_rate=0.0005)

    assert tracker.initial_capital == 10000.0
    assert tracker.capital == 10000.0
    assert tracker.commission_rate == 0.001
    assert tracker.slippage_rate == 0.0005
    assert tracker.position is None
    assert len(tracker.trades) == 0
    assert len(tracker.equity_curve) == 0


def test_execute_action_none():
    """Test that NONE action does nothing."""
    tracker = PositionTracker()
    result = tracker.execute_action(action="NONE", size=0.1, price=100.0, timestamp=datetime.now())

    assert result["action"] == "NONE"
    assert not result["executed"]
    assert result["reason"] == "no_action"
    assert tracker.position is None


def test_open_long_position():
    """Test opening a LONG position."""
    tracker = PositionTracker(initial_capital=10000.0, commission_rate=0.001)
    timestamp = datetime.now()

    result = tracker.execute_action(
        action="LONG", size=0.1, price=100.0, timestamp=timestamp, symbol="tBTCUSD"
    )

    assert result["executed"]
    assert result["reason"] == "opened"
    assert tracker.position is not None
    assert tracker.position.side == "LONG"
    assert tracker.position.size == 0.1
    # Commission should be deducted
    assert tracker.capital < 10000.0


def test_open_short_position():
    """Test opening a SHORT position."""
    tracker = PositionTracker(initial_capital=10000.0, commission_rate=0.001)
    timestamp = datetime.now()

    result = tracker.execute_action(
        action="SHORT", size=0.1, price=100.0, timestamp=timestamp, symbol="tBTCUSD"
    )

    assert result["executed"]
    assert result["reason"] == "opened"
    assert tracker.position is not None
    assert tracker.position.side == "SHORT"
    assert tracker.position.size == 0.1


def test_close_position_on_opposite_action():
    """Test that opposite action closes current position."""
    tracker = PositionTracker(initial_capital=10000.0)
    timestamp = datetime.now()

    # Open LONG
    tracker.execute_action(
        action="LONG", size=0.1, price=100.0, timestamp=timestamp, symbol="tBTCUSD"
    )
    assert tracker.position.side == "LONG"

    # Execute SHORT - should close LONG and open SHORT
    result = tracker.execute_action(
        action="SHORT", size=0.1, price=110.0, timestamp=timestamp, symbol="tBTCUSD"
    )

    assert result["executed"]
    assert tracker.position.side == "SHORT"
    assert len(tracker.trades) == 1  # LONG was closed


def test_profitable_long_trade():
    """Test a profitable LONG trade."""
    tracker = PositionTracker(initial_capital=10000.0, commission_rate=0.0)
    timestamp = datetime.now()

    # Open LONG at 100
    tracker.execute_action(
        action="LONG", size=0.1, price=100.0, timestamp=timestamp, symbol="tBTCUSD"
    )

    # Close at 110 (10% profit)
    tracker.execute_action(
        action="SHORT", size=0.1, price=110.0, timestamp=timestamp, symbol="tBTCUSD"
    )

    assert len(tracker.trades) == 1
    trade = tracker.trades[0]
    # Allow small slippage variance
    assert abs(trade.pnl - 1.0) < 0.02  # (110 - 100) * 0.1 with slippage
    assert trade.pnl_pct > 0
    assert tracker.capital > 10000.0


def test_losing_short_trade():
    """Test a losing SHORT trade."""
    tracker = PositionTracker(initial_capital=10000.0, commission_rate=0.0)
    timestamp = datetime.now()

    # Open SHORT at 100
    tracker.execute_action(
        action="SHORT", size=0.1, price=100.0, timestamp=timestamp, symbol="tBTCUSD"
    )

    # Close at 110 (10% loss)
    tracker.execute_action(
        action="LONG", size=0.1, price=110.0, timestamp=timestamp, symbol="tBTCUSD"
    )

    assert len(tracker.trades) == 1
    trade = tracker.trades[0]
    # Allow small slippage variance
    assert abs(trade.pnl - (-1.0)) < 0.02  # (100 - 110) * 0.1 with slippage
    assert trade.pnl_pct < 0
    assert tracker.capital < 10000.0


def test_commission_deduction():
    """Test that commission is properly deducted."""
    tracker = PositionTracker(initial_capital=10000.0, commission_rate=0.001, slippage_rate=0.0)
    timestamp = datetime.now()

    initial_capital = tracker.capital

    # Open position
    tracker.execute_action(
        action="LONG", size=0.1, price=100.0, timestamp=timestamp, symbol="tBTCUSD"
    )

    # Commission: 0.1 * 100 * 0.001 = 0.01
    expected_commission = 0.01
    assert abs(tracker.total_commission - expected_commission) < 0.0001
    assert tracker.capital == initial_capital - expected_commission


def test_equity_curve_tracking():
    """Test equity curve is properly tracked."""
    tracker = PositionTracker(initial_capital=10000.0, commission_rate=0.0)
    timestamp = datetime.now()

    # Open LONG
    tracker.execute_action(
        action="LONG", size=0.1, price=100.0, timestamp=timestamp, symbol="tBTCUSD"
    )

    # Update equity at different prices
    tracker.update_equity(105.0, timestamp)
    tracker.update_equity(110.0, timestamp)

    assert len(tracker.equity_curve) == 2
    # First update: unrealized PnL = (105-100)*0.1 = 0.5 (with slippage)
    assert abs(tracker.equity_curve[0]["unrealized_pnl"] - 0.5) < 0.01
    # Second update: unrealized PnL = (110-100)*0.1 = 1.0 (with slippage)
    assert abs(tracker.equity_curve[1]["unrealized_pnl"] - 1.0) < 0.01


def test_get_summary():
    """Test summary statistics generation."""
    tracker = PositionTracker(initial_capital=10000.0, commission_rate=0.0)
    timestamp = datetime.now()

    # Make 2 trades: 1 win, 1 loss
    # Trade 1: LONG 100 -> 110 (win)
    tracker.execute_action(
        action="LONG", size=0.1, price=100.0, timestamp=timestamp, symbol="tBTCUSD"
    )
    tracker.execute_action(
        action="SHORT", size=0.1, price=110.0, timestamp=timestamp, symbol="tBTCUSD"
    )

    # Trade 2: SHORT 110 -> 115 (loss)
    tracker.execute_action(
        action="LONG", size=0.1, price=115.0, timestamp=timestamp, symbol="tBTCUSD"
    )

    summary = tracker.get_summary()

    assert summary["num_trades"] == 2
    assert summary["winning_trades"] == 1
    assert summary["losing_trades"] == 1
    assert summary["win_rate"] == 50.0
    assert summary["total_return"] > 0  # Net positive


def test_close_all_positions():
    """Test force closing all positions."""
    tracker = PositionTracker(initial_capital=10000.0)
    timestamp = datetime.now()

    # Open position
    tracker.execute_action(
        action="LONG", size=0.1, price=100.0, timestamp=timestamp, symbol="tBTCUSD"
    )

    assert tracker.position is not None

    # Close all
    tracker.close_all_positions(price=105.0, timestamp=timestamp)

    assert tracker.position is None
    assert len(tracker.trades) == 1
