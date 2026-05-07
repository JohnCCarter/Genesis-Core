from __future__ import annotations

from core.agent.trade_manager import (
    ExitConfig,
    TradeState,
    force_close,
    open_trade,
    update,
)


def _long_trade(stop: float = 95.0, tp1: float = 110.0, tp2: float = 120.0) -> TradeState:
    return open_trade(
        side="LONG", entry=100.0, stop=stop,
        target_tp1=tp1, target_tp2=tp2, open_bar=0,
    )


def _short_trade(stop: float = 105.0, tp1: float = 90.0, tp2: float = 80.0) -> TradeState:
    return open_trade(
        side="SHORT", entry=100.0, stop=stop,
        target_tp1=tp1, target_tp2=tp2, open_bar=0,
    )


def test_long_full_stop_out_no_targets() -> None:
    s = _long_trade()
    events = update(s, bar_index=1, high=98.0, low=94.0)
    assert s.closed
    assert len(events) == 1
    assert events[0].reason == "stop"
    assert events[0].fraction == 1.0
    assert events[0].pnl_unit == -5.0  # 1 * (95 - 100)
    assert s.realized_pnl_unit == -5.0


def test_long_tp1_hit_moves_stop_to_breakeven() -> None:
    s = _long_trade()
    events = update(s, bar_index=1, high=110.5, low=99.0)
    assert not s.closed
    assert s.tp1_hit
    assert abs(s.qty_remaining - (1 - 1 / 3)) < 1e-9
    assert s.stop == 100.0  # break-even
    assert len(events) == 1
    assert events[0].reason == "tp1"
    assert abs(events[0].pnl_unit - (1 / 3) * 10.0) < 1e-9


def test_long_tp1_then_breakeven_stop_blocks_loss() -> None:
    s = _long_trade()
    update(s, bar_index=1, high=110.5, low=99.0)  # tp1 hit, stop → 100
    events = update(s, bar_index=2, high=105.0, low=99.0)  # low touches BE
    assert s.closed
    last = events[-1]
    assert last.reason == "breakeven"
    assert last.fraction == s.config.tp2_fraction + (1 - s.config.tp1_fraction - s.config.tp2_fraction)


def test_long_tp1_tp2_hit_starts_trailing_on_residual() -> None:
    s = _long_trade()
    events = update(s, bar_index=1, high=120.0, low=99.0)  # both targets in one bar
    assert s.tp1_hit and s.tp2_hit
    assert not s.closed
    assert abs(s.qty_remaining - (1 - 2 / 3)) < 1e-9
    assert {e.reason for e in events} == {"tp1", "tp2"}
    # Trailing started: stop moved up from break-even
    assert s.stop > s.entry - 1e-9


def test_long_trailing_stop_advances_with_new_highs() -> None:
    s = _long_trade()
    update(s, bar_index=1, high=120.0, low=99.0)  # tp1+tp2
    stop_after_tp2 = s.stop
    update(s, bar_index=2, high=130.0, low=119.0)  # higher high → trail advances
    assert s.stop > stop_after_tp2


def test_long_trailing_stop_never_retreats() -> None:
    s = _long_trade()
    update(s, bar_index=1, high=120.0, low=99.0)
    stop_after = s.stop
    update(s, bar_index=2, high=121.0, low=119.0)  # only tiny new high
    update(s, bar_index=3, high=120.5, low=118.0)  # lower high should NOT lower stop
    assert s.stop >= stop_after


def test_long_trailing_exit_on_pullback() -> None:
    s = _long_trade()
    update(s, bar_index=1, high=120.0, low=99.0)
    update(s, bar_index=2, high=140.0, low=119.0)  # raise trail
    trail_stop = s.stop
    events = update(s, bar_index=3, high=141.0, low=trail_stop - 0.1)
    assert s.closed
    assert events[-1].reason == "trail"


def test_short_full_stop_out() -> None:
    s = _short_trade()
    events = update(s, bar_index=1, high=106.0, low=99.0)
    assert s.closed
    assert events[0].reason == "stop"
    assert events[0].pnl_unit == -5.0  # short: entry - stop = 100 - 105


def test_short_tp1_then_breakeven() -> None:
    s = _short_trade()
    update(s, bar_index=1, high=101.0, low=89.5)  # tp1 hit
    assert s.tp1_hit
    assert s.stop == 100.0
    events = update(s, bar_index=2, high=100.5, low=99.0)  # high touches BE
    assert s.closed
    assert events[-1].reason == "breakeven"


def test_short_tp1_tp2_then_trailing() -> None:
    s = _short_trade()
    events = update(s, bar_index=1, high=101.0, low=80.0)  # both
    assert s.tp1_hit and s.tp2_hit
    assert s.stop < s.entry  # trailing pulled stop down for SHORT
    update(s, bar_index=2, high=85.0, low=70.0)  # new low
    assert s.stop < s.entry


def test_pnl_aggregation_partial_then_trail_exit() -> None:
    s = _long_trade()
    update(s, bar_index=1, high=110.5, low=99.0)  # tp1 (1/3 at +10)
    update(s, bar_index=2, high=120.0, low=109.0)  # tp2 (1/3 at +20)
    update(s, bar_index=3, high=140.0, low=119.0)  # extend
    events = update(s, bar_index=4, high=141.0, low=s.stop - 0.5)  # trail-out
    assert s.closed
    expected_realized = (1 / 3) * 10.0 + (1 / 3) * 20.0 + (1 / 3) * (s.exits[-1].price - 100.0)
    assert abs(s.realized_pnl_unit - expected_realized) < 1e-6


def test_force_close_marks_residual() -> None:
    s = _long_trade()
    update(s, bar_index=1, high=110.5, low=99.0)
    ev = force_close(s, bar_index=99, price=115.0)
    assert s.closed
    assert ev is not None
    assert ev.reason == "force_close"
    expected_pnl = (1 / 3) * 10.0 + (1 - 1 / 3) * 15.0
    assert abs(s.realized_pnl_unit - expected_pnl) < 1e-6


def test_no_breakeven_when_disabled() -> None:
    cfg = ExitConfig(move_stop_to_breakeven_after_tp1=False)
    s = open_trade(
        side="LONG", entry=100.0, stop=95.0,
        target_tp1=110.0, target_tp2=120.0, open_bar=0, config=cfg,
    )
    update(s, bar_index=1, high=110.5, low=99.0)
    assert s.stop == 95.0  # unchanged


def test_no_trailing_when_disabled() -> None:
    cfg = ExitConfig(trail_after_tp2=False)
    s = open_trade(
        side="LONG", entry=100.0, stop=95.0,
        target_tp1=110.0, target_tp2=120.0, open_bar=0, config=cfg,
    )
    update(s, bar_index=1, high=125.0, low=99.0)
    stop_after_tp2 = s.stop
    update(s, bar_index=2, high=140.0, low=124.0)
    assert s.stop == stop_after_tp2  # no advance
