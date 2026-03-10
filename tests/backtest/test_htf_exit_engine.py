import pandas as pd
import pytest

from core.strategy.htf_exit_engine import HTFFibonacciExitEngine


@pytest.fixture
def exit_engine():
    return HTFFibonacciExitEngine()


def test_tp1_execution_long(exit_engine):
    """Test standard valid TP1 execution for Long position."""
    # Context: Long from 100.
    # Sorted Levels: 110 (TP1), 120 (TP2).

    htf_data = pd.Series({"htf_fib_0382": 130.0, "htf_fib_05": 120.0, "htf_fib_0618": 110.0})

    # 1. Price < TP1
    signal = exit_engine.check_exits(
        current_price=105.0,
        position_size=1.0,
        entry_price=100.0,
        side=1,
        current_atr=1.0,
        htf_data=htf_data,
    )
    assert signal.action == "HOLD"

    # 2. Price hits TP1 (110)
    signal = exit_engine.check_exits(
        current_price=110.1,  # Slightly above
        position_size=1.0,
        entry_price=100.0,
        side=1,
        current_atr=1.0,
        htf_data=htf_data,
    )
    assert signal.action == "PARTIAL_EXIT"
    assert signal.quantity_pct == exit_engine.partial_1_pct
    assert exit_engine.position_state["tp1_hit"] is True

    # 3. Price stays above TP1 (should propose Trailing Stop to Breakeven)
    # The engine now returns UPDATE_STOP if TP1 is hit but not TP2.
    signal = exit_engine.check_exits(
        current_price=115.0,
        position_size=0.67,  # Remaining
        entry_price=100.0,
        side=1,
        current_atr=1.0,
        htf_data=htf_data,
    )
    assert signal.action == "UPDATE_STOP"
    assert signal.new_stop_price == 100.0

    # 4. Price hits TP2 (120)
    signal = exit_engine.check_exits(
        current_price=120.5,
        position_size=0.67,
        entry_price=100.0,
        side=1,
        current_atr=1.0,
        htf_data=htf_data,
    )
    assert signal.action == "PARTIAL_EXIT"
    assert signal.quantity_pct == exit_engine.partial_2_pct
    assert exit_engine.position_state["tp2_hit"] is True


def test_tp1_execution_short(exit_engine):
    """Test standard valid TP1 execution for Short position."""
    # Context: Short from 100.
    # Levels: 90 (TP1), 80 (TP2), 70.

    htf_data = pd.Series({"htf_fib_0382": 70.0, "htf_fib_05": 80.0, "htf_fib_0618": 90.0})

    # 1. Price > TP1
    signal = exit_engine.check_exits(
        current_price=95.0,
        position_size=1.0,
        entry_price=100.0,
        side=-1,
        current_atr=1.0,
        htf_data=htf_data,
    )
    assert signal.action == "HOLD"

    # 2. Price hits TP1 (90)
    signal = exit_engine.check_exits(
        current_price=89.5,  # Slightly below
        position_size=1.0,
        entry_price=100.0,
        side=-1,
        current_atr=1.0,
        htf_data=htf_data,
    )
    assert signal.action == "PARTIAL_EXIT"
    assert "TP1" in signal.reason
    assert exit_engine.position_state["tp1_hit"] is True


def test_no_levels_in_direction(exit_engine):
    """Test behavior when all levels are against validity."""
    # Context: Long from 100. All levels < 100.

    htf_data = pd.Series({"htf_fib_0382": 70.0, "htf_fib_05": 80.0, "htf_fib_0618": 90.0})

    signal = exit_engine.check_exits(
        current_price=105.0,
        position_size=1.0,
        entry_price=100.0,
        side=1,
        current_atr=1.0,
        htf_data=htf_data,
    )
    assert signal.action == "HOLD"


def test_trailing_stop_logic(exit_engine):
    """Test that SL is updated when TPs are hit."""
    # Context: Long from 100.
    # Sorted Levels: 110 (TP1), 120 (TP2).

    htf_data = pd.Series(
        {
            "htf_fib_0382": 130.0,
            "htf_fib_0618": 110.0,
            "htf_fib_05": 120.0,
        }
    )

    # 1. Hit TP1 -> Expect Trailing to Breakeven (100)
    exit_engine.position_state["tp1_hit"] = True

    signal = exit_engine.check_exits(
        current_price=112.0,
        position_size=1.0,
        entry_price=100.0,
        side=1,
        current_atr=1.0,
        htf_data=htf_data,
    )
    assert signal.action == "UPDATE_STOP"
    assert signal.new_stop_price == 100.0

    # 2. Hit TP2 -> Expect Trailing to TP1 (110)
    exit_engine.position_state["tp2_hit"] = True

    signal = exit_engine.check_exits(
        current_price=125.0,
        position_size=0.5,
        entry_price=100.0,
        side=1,
        current_atr=1.0,
        htf_data=htf_data,
    )
    assert signal.action == "UPDATE_STOP"
    assert signal.new_stop_price == 110.0
