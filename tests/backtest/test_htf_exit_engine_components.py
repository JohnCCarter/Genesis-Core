from __future__ import annotations

from datetime import datetime

from core.backtest.htf_exit_engine import HTFFibonacciExitEngine
from core.backtest.position_tracker import Position


def _make_position(side: str) -> Position:
    return Position(
        symbol="tBTCUSD",
        side=side,
        initial_size=1.0,
        current_size=1.0,
        entry_price=100.0,
        entry_time=datetime(2025, 1, 1, 0, 0, 0),
    )


def test_trailing_stop_long_promotes_against_05_after_0618_break() -> None:
    engine = HTFFibonacciExitEngine(config={})
    position = _make_position("LONG")

    action = engine._check_trailing_stop(
        position,
        current_price=126.0,
        ema50=118.0,
        atr=5.0,
        htf_levels={0.5: 120.0, 0.618: 115.0},
    )

    assert action is not None
    assert action.action == "TRAIL_UPDATE"
    assert action.reason == "TRAIL_STOP"
    assert action.stop_price == 120.0


def test_trailing_stop_short_promotes_against_05_below_0382() -> None:
    engine = HTFFibonacciExitEngine(config={})
    position = _make_position("SHORT")

    action = engine._check_trailing_stop(
        position,
        current_price=92.0,
        ema50=90.0,
        atr=5.0,
        htf_levels={0.5: 95.0, 0.382: 94.0},
    )

    assert action is not None
    assert action.action == "TRAIL_UPDATE"
    assert action.reason == "TRAIL_STOP"
    assert action.stop_price == 95.0


def test_structure_break_long_requires_negative_momentum() -> None:
    engine = HTFFibonacciExitEngine(config={})
    position = _make_position("LONG")

    action = engine._check_structure_break(
        position,
        current_price=94.0,
        htf_levels={0.618: 95.0},
        ema_slope50_z=-0.6,
    )

    assert action is not None
    assert action.action == "FULL_EXIT"
    assert action.reason == "STRUCTURE_BREAK_DOWN"


def test_structure_break_short_requires_positive_momentum() -> None:
    engine = HTFFibonacciExitEngine(config={})
    position = _make_position("SHORT")

    action = engine._check_structure_break(
        position,
        current_price=106.0,
        htf_levels={0.382: 105.0},
        ema_slope50_z=0.6,
    )

    assert action is not None
    assert action.action == "FULL_EXIT"
    assert action.reason == "STRUCTURE_BREAK_UP"


def test_fallback_exits_returns_trailing_update_with_reason() -> None:
    engine = HTFFibonacciExitEngine(config={})
    position = _make_position("LONG")

    actions = engine._fallback_exits(
        position,
        current_bar={"close": 100.0},
        indicators={"atr": 10.0, "ema50": 100.0},
    )

    assert len(actions) == 1
    assert actions[0].action == "TRAIL_UPDATE"
    assert actions[0].reason == "FALLBACK_TRAIL"
    assert actions[0].stop_price == 87.0
