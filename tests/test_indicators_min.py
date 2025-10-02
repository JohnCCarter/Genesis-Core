from __future__ import annotations

from core.indicators.ema import calculate_ema
from core.indicators.atr import calculate_atr


def test_calculate_ema_basic():
    vals = [1, 2, 3, 4]
    ema = calculate_ema(vals, period=2)
    assert len(ema) == len(vals)
    assert ema[0] == 1.0
    assert ema[-1] > ema[-2]


def test_calculate_atr_shapes():
    highs = [10, 11, 12, 13]
    lows = [9, 9.5, 10, 11]
    closes = [9.5, 10.5, 11.5, 12.5]
    atr = calculate_atr(highs, lows, closes, period=3)
    assert len(atr) == len(highs) == len(lows) == len(closes)
    assert atr[0] >= 0
