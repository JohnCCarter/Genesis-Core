"""Position lifecycle management for the nested fib agent.

Pure, deterministic: takes an open ``TradeState`` plus one bar of candle data
(high, low) and produces exit events. No I/O, no time, no randomness.

Exit rules (all configurable via ``ExitConfig``):
  - Initial stop = ``signal.stop`` (set by ``compute_signal``)
  - At target 1.272 (TP1): close ``tp1_fraction`` of position, move stop to break-even
  - At target 1.618 (TP2): close ``tp2_fraction`` of position, start trailing the rest
  - Trailing on the residual: stop = best_extreme_since_tp2 ± trail_atr_mult × initial_risk

The bar-precision walk-forward intentionally checks the stop BEFORE the targets
within a single bar — i.e. when both could have triggered, we conservatively assume
the stop fired first. This is the standard "worst-case" backtest convention.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ExitConfig:
    tp1_fraction: float = 1 / 3
    tp2_fraction: float = 1 / 3
    move_stop_to_breakeven_after_tp1: bool = True
    trail_after_tp2: bool = True
    trail_initial_risk_mult: float = 1.5  # trail-distance = mult × initial_risk


@dataclass(slots=True)
class ExitEvent:
    bar_index: int
    reason: str  # "tp1" | "tp2" | "stop" | "breakeven" | "trail" | "force_close"
    price: float
    fraction: float
    pnl_unit: float  # PnL per 1 unit of original size (signed)


@dataclass(slots=True)
class TradeState:
    side: str  # "LONG" | "SHORT"
    entry: float
    initial_stop: float
    target_tp1: float
    target_tp2: float
    open_bar: int
    config: ExitConfig = field(default_factory=ExitConfig)
    stop: float = 0.0
    qty_remaining: float = 1.0
    tp1_hit: bool = False
    tp2_hit: bool = False
    closed: bool = False
    realized_pnl_unit: float = 0.0  # cumulative PnL per unit of original size
    best_since_tp2: float | None = None
    exits: list[ExitEvent] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.stop == 0.0:
            self.stop = self.initial_stop

    @property
    def initial_risk(self) -> float:
        return abs(self.entry - self.initial_stop)


def open_trade(
    *,
    side: str,
    entry: float,
    stop: float,
    target_tp1: float,
    target_tp2: float,
    open_bar: int,
    config: ExitConfig | None = None,
) -> TradeState:
    return TradeState(
        side=side,
        entry=entry,
        initial_stop=stop,
        stop=stop,
        target_tp1=target_tp1,
        target_tp2=target_tp2,
        open_bar=open_bar,
        config=config or ExitConfig(),
    )


def _pnl_long(entry: float, exit_price: float, fraction: float) -> float:
    return fraction * (exit_price - entry)


def _pnl_short(entry: float, exit_price: float, fraction: float) -> float:
    return fraction * (entry - exit_price)


def update(state: TradeState, *, bar_index: int, high: float, low: float) -> list[ExitEvent]:
    """Apply one bar of price action; mutate state. Returns events fired this bar."""
    if state.closed:
        return []

    cfg = state.config
    events: list[ExitEvent] = []
    long = state.side == "LONG"

    # 1) Stop check first (conservative)
    stop_hit = (long and low <= state.stop) or (not long and high >= state.stop)
    if stop_hit:
        fraction = state.qty_remaining
        pnl = (
            _pnl_long(state.entry, state.stop, fraction)
            if long
            else _pnl_short(state.entry, state.stop, fraction)
        )
        # Reason: distinguish initial stop vs break-even vs trailing exit
        if state.tp2_hit:
            reason = "trail"
        elif state.tp1_hit:
            reason = "breakeven" if abs(state.stop - state.entry) < 1e-9 else "stop"
        else:
            reason = "stop"
        ev = ExitEvent(
            bar_index=bar_index, reason=reason, price=state.stop, fraction=fraction, pnl_unit=pnl
        )
        events.append(ev)
        state.exits.append(ev)
        state.realized_pnl_unit += pnl
        state.qty_remaining = 0.0
        state.closed = True
        return events

    # 2) TP1 check
    if not state.tp1_hit:
        tp1_hit = (long and high >= state.target_tp1) or (not long and low <= state.target_tp1)
        if tp1_hit:
            fraction = min(cfg.tp1_fraction, state.qty_remaining)
            pnl = (
                _pnl_long(state.entry, state.target_tp1, fraction)
                if long
                else _pnl_short(state.entry, state.target_tp1, fraction)
            )
            ev = ExitEvent(
                bar_index=bar_index,
                reason="tp1",
                price=state.target_tp1,
                fraction=fraction,
                pnl_unit=pnl,
            )
            events.append(ev)
            state.exits.append(ev)
            state.realized_pnl_unit += pnl
            state.qty_remaining -= fraction
            state.tp1_hit = True
            if cfg.move_stop_to_breakeven_after_tp1:
                state.stop = state.entry

    # 3) TP2 check
    if state.tp1_hit and not state.tp2_hit:
        tp2_hit = (long and high >= state.target_tp2) or (not long and low <= state.target_tp2)
        if tp2_hit:
            fraction = min(cfg.tp2_fraction, state.qty_remaining)
            pnl = (
                _pnl_long(state.entry, state.target_tp2, fraction)
                if long
                else _pnl_short(state.entry, state.target_tp2, fraction)
            )
            ev = ExitEvent(
                bar_index=bar_index,
                reason="tp2",
                price=state.target_tp2,
                fraction=fraction,
                pnl_unit=pnl,
            )
            events.append(ev)
            state.exits.append(ev)
            state.realized_pnl_unit += pnl
            state.qty_remaining -= fraction
            state.tp2_hit = True
            state.best_since_tp2 = high if long else low

    # 4) Trailing on residual (after TP2)
    if state.tp2_hit and state.qty_remaining > 0 and cfg.trail_after_tp2:
        if long:
            state.best_since_tp2 = max(state.best_since_tp2 or high, high)
            new_stop = state.best_since_tp2 - cfg.trail_initial_risk_mult * state.initial_risk
            if new_stop > state.stop:
                state.stop = new_stop
        else:
            state.best_since_tp2 = min(state.best_since_tp2 or low, low)
            new_stop = state.best_since_tp2 + cfg.trail_initial_risk_mult * state.initial_risk
            if new_stop < state.stop:
                state.stop = new_stop

    if state.qty_remaining <= 1e-9:
        state.closed = True

    return events


def force_close(state: TradeState, *, bar_index: int, price: float) -> ExitEvent | None:
    """Mark-to-market the residual at end of dataset."""
    if state.closed or state.qty_remaining <= 1e-9:
        return None
    fraction = state.qty_remaining
    pnl = (
        _pnl_long(state.entry, price, fraction)
        if state.side == "LONG"
        else _pnl_short(state.entry, price, fraction)
    )
    ev = ExitEvent(
        bar_index=bar_index, reason="force_close", price=price, fraction=fraction, pnl_unit=pnl
    )
    state.exits.append(ev)
    state.realized_pnl_unit += pnl
    state.qty_remaining = 0.0
    state.closed = True
    return ev


def state_to_dict(state: TradeState) -> dict[str, Any]:
    return {
        "side": state.side,
        "entry": state.entry,
        "initial_stop": state.initial_stop,
        "stop": state.stop,
        "target_tp1": state.target_tp1,
        "target_tp2": state.target_tp2,
        "tp1_hit": state.tp1_hit,
        "tp2_hit": state.tp2_hit,
        "closed": state.closed,
        "qty_remaining": state.qty_remaining,
        "realized_pnl_unit": state.realized_pnl_unit,
        "exits": [
            {
                "bar": e.bar_index,
                "reason": e.reason,
                "price": e.price,
                "fraction": e.fraction,
                "pnl_unit": e.pnl_unit,
            }
            for e in state.exits
        ],
    }
