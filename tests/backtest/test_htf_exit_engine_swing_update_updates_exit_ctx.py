from __future__ import annotations

from datetime import UTC, datetime

from core.backtest.htf_exit_engine import HTFFibonacciExitEngine
from core.backtest.position_tracker import Position
from core.indicators.exit_fibonacci import calculate_exit_fibonacci_levels


def test_dynamic_swing_update_updates_exit_ctx_levels_and_bounds() -> None:
    engine = HTFFibonacciExitEngine(
        {
            "swing_update_strategy": "dynamic",
            "swing_update_params": {"log_updates": False},
            # Disable other logic to keep the test focused.
            "enable_partials": False,
            "enable_trailing": False,
            "enable_structure_breaks": False,
        }
    )

    entry_time = datetime(2025, 1, 1, tzinfo=UTC)
    position = Position(
        symbol="tBTCUSD",
        side="LONG",
        initial_size=1.0,
        current_size=1.0,
        entry_price=100.0,
        entry_time=entry_time,
    )

    # Initial (entry) swing + frozen context
    initial_high = 110.0
    initial_low = 90.0
    initial_levels = calculate_exit_fibonacci_levels(
        side=position.side,
        swing_high=initial_high,
        swing_low=initial_low,
        levels=[0.786, 0.618, 0.5, 0.382],
    )
    position.exit_swing_high = initial_high
    position.exit_swing_low = initial_low
    position.exit_fib_levels = dict(initial_levels)
    position.arm_exit_context(
        {
            "swing_id": "entry",
            "levels": initial_levels,
            "swing_low": initial_low,
            "swing_high": initial_high,
        }
    )

    old_ctx = dict(position.exit_ctx or {})
    assert old_ctx.get("swing_bounds") == (initial_low, initial_high)

    # New HTF swing arrives (dynamic strategy => should update).
    new_high = 130.0
    new_low = 80.0
    htf_ctx = {
        "available": True,
        "swing_high": new_high,
        "swing_low": new_low,
        "swing_age_bars": 1,
        "last_update": datetime(2025, 1, 2, tzinfo=UTC),
    }

    current_bar = {
        "timestamp": datetime(2025, 1, 2, tzinfo=UTC),
        "open": 100.0,
        "high": 101.0,
        "low": 99.0,
        "close": 100.0,
    }

    engine._check_swing_updates(position, htf_ctx, current_bar, {"atr": 5.0})

    assert position.exit_ctx is not None
    assert position.exit_ctx.get("swing_bounds") == (new_low, new_high)
    assert position.exit_ctx.get("fib") == position.exit_fib_levels
    assert position.exit_ctx.get("fib") != old_ctx.get("fib")
