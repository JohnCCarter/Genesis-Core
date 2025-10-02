from __future__ import annotations

from core.indicators.rsi import calculate_rsi
from core.indicators.adx import calculate_adx


def test_rsi_basic_monotone():
    prices = [1, 2, 3, 4, 5, 6, 7]
    rsi = calculate_rsi(prices, period=3)
    assert len(rsi) == len(prices)
    assert max(rsi) <= 100.0 and min(rsi) >= 0.0


def test_adx_shapes():
    highs = [10, 11, 12, 13, 14, 15]
    lows = [9, 9.5, 10, 11, 12, 13]
    closes = [9.5, 10.5, 11.5, 12.5, 13.5, 14.5]
    adx = calculate_adx(highs, lows, closes, period=3)
    assert len(adx) == len(highs)
    assert all(v >= 0 for v in adx)
