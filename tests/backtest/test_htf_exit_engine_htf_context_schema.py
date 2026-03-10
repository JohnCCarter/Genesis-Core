from __future__ import annotations

from datetime import datetime

import pandas as pd

from core.backtest.htf_exit_engine import HTFFibonacciExitEngine
from core.backtest.position_tracker import Position


def _make_position() -> Position:
    return Position(
        symbol="tBTCUSD",
        side="LONG",
        initial_size=1.0,
        current_size=1.0,
        entry_price=100.0,
        entry_time=datetime(2025, 1, 1, 0, 0, 0),
    )


def test_initialize_position_exit_levels_reads_producer_schema():
    engine = HTFFibonacciExitEngine(config={"swing_update_strategy": "fixed"})
    pos = _make_position()

    htf_ctx = {
        "available": True,
        "levels": {0.382: 104.72, 0.5: 100.0, 0.618: 95.28, 0.786: 88.56},
        "swing_high": 120.0,
        "swing_low": 80.0,
        "swing_age_bars": 5,
        "data_age_hours": 1.0,
        "htf_timeframe": "1D",
        "last_update": pd.Timestamp("2025-01-01T00:00:00Z"),
    }

    # Make validation pass: swing_size=40 -> 4 ATR, distance to bounds <=2 ATR.
    indicators = {"ema50": 100.0, "atr": 10.0}

    engine._initialize_position_exit_levels(pos, htf_ctx, indicators)

    assert pos.exit_swing_high == 120.0
    assert pos.exit_swing_low == 80.0
    assert pos.exit_fib_levels
    assert set(pos.exit_fib_levels.keys()) == {0.786, 0.618, 0.5, 0.382}
    assert pos.exit_swing_timestamp == htf_ctx["last_update"]


def test_check_swing_updates_reads_producer_schema_and_keeps_0786_level():
    engine = HTFFibonacciExitEngine(
        config={
            "swing_update_strategy": "hybrid",
            "swing_update_params": {
                "min_improvement_pct": 0.0,
                "max_age_bars": 30,
                "allow_worse_swing": False,
                "log_updates": False,
            },
        }
    )
    pos = _make_position()

    # Seed position with a valid initial swing.
    engine._initialize_position_exit_levels(
        pos,
        {
            "available": True,
            "levels": {0.382: 104.72, 0.5: 100.0, 0.618: 95.28, 0.786: 88.56},
            "swing_high": 120.0,
            "swing_low": 80.0,
            "swing_age_bars": 1,
            "data_age_hours": 1.0,
            "htf_timeframe": "1D",
            "last_update": pd.Timestamp("2025-01-01T00:00:00Z"),
        },
        {"ema50": 100.0, "atr": 10.0},
    )

    assert pos.exit_fib_levels

    # New HTF context with an improved swing high.
    new_ctx = {
        "available": True,
        "levels": {0.382: 109.44, 0.5: 105.0, 0.618: 100.56, 0.786: 92.68},
        "swing_high": 130.0,
        "swing_low": 80.0,
        "swing_age_bars": 2,
        "data_age_hours": 1.0,
        "htf_timeframe": "1D",
        "last_update": pd.Timestamp("2025-01-02T00:00:00Z"),
    }

    engine._check_swing_updates(
        pos,
        new_ctx,
        current_bar={"timestamp": pd.Timestamp("2025-01-02T01:00:00Z"), "close": 110.0},
        indicators={"ema50": 110.0, "atr": 10.0},
    )

    assert pos.exit_swing_high == 130.0
    assert pos.exit_swing_low == 80.0
    assert set(pos.exit_fib_levels.keys()) == {0.786, 0.618, 0.5, 0.382}
    assert pos.exit_swing_timestamp == new_ctx["last_update"]


def test_check_partial_exits_tp1_uses_padding_semantics():
    engine = HTFFibonacciExitEngine(config={})
    pos = _make_position()

    position_id = f"{pos.symbol}_{pos.entry_time.isoformat()}"
    engine.triggered_exits[position_id] = set()

    current_bar = {
        "open": 104.6,
        "high": 104.7,
        "low": 104.6,
        "close": 104.65,
    }
    atr = 10.0
    htf_levels = {0.382: 105.0}

    actions = engine._check_partial_exits(pos, current_bar, atr, htf_levels, position_id)

    assert len(actions) == 1
    assert actions[0].action == "PARTIAL"
    assert actions[0].reason == "TP1_0382"
    assert actions[0].size == pos.current_size * engine.partial_1_pct


def test_check_partial_exits_tp1_outside_padding_does_not_trigger():
    engine = HTFFibonacciExitEngine(config={})
    pos = _make_position()

    position_id = f"{pos.symbol}_{pos.entry_time.isoformat()}"
    engine.triggered_exits[position_id] = set()

    # Target=105.0 and ATR=10.0 => pad=max(0.05*10, 0.0005*105)=0.5
    # With high=104.49 and low=104.4, target is just outside upper boundary (104.99).
    current_bar = {
        "open": 104.4,
        "high": 104.49,
        "low": 104.4,
        "close": 104.45,
    }
    atr = 10.0
    htf_levels = {0.382: 105.0}

    actions = engine._check_partial_exits(pos, current_bar, atr, htf_levels, position_id)

    assert actions == []
