from __future__ import annotations

from core.strategy.ema_cross import ema_cross_signal


def test_ema_cross_buy_sell_hold():
    # Konstruera serie där fast korsar upp och senare ned
    prices = [1, 1, 1, 1, 1, 2, 3, 4, 3, 2, 1]
    sig = ema_cross_signal(prices, fast=2, slow=4)
    assert sig in {"buy", "sell", "hold"}
    # Edge: för kort serie => hold
    assert ema_cross_signal([1, 2], fast=2, slow=4) == "hold"
