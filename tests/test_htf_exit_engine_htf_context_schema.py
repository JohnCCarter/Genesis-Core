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
