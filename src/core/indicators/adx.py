from __future__ import annotations

from collections.abc import Iterable

import numpy as np


def calculate_adx(
    highs: Iterable[float],
    lows: Iterable[float],
    closes: Iterable[float],
    period: int = 14,
) -> list[float]:
    """Beräkna ADX (Average Directional Index) med vektoriserad NumPy.

    Returnerar ADX med samma längd som input.
    """
    hs = np.asarray(highs, dtype=float)
    ls = np.asarray(lows, dtype=float)
    cs = np.asarray(closes, dtype=float)

    if not (len(hs) == len(ls) == len(cs)):
        raise ValueError("highs/lows/closes must have same length")
    n = int(period)
    if n <= 0:
        raise ValueError("period must be > 0")
    length = len(hs)
    if length == 0:
        return []

    # 1. Calculate True Range (TR) and Directional Movement (DM)
    prev_closes = np.roll(cs, 1)
    prev_closes[0] = cs[0]

    tr1 = hs - ls
    tr2 = np.abs(hs - prev_closes)
    tr3 = np.abs(ls - prev_closes)
    trs = np.maximum(tr1, np.maximum(tr2, tr3))

    prev_highs = np.roll(hs, 1)
    prev_highs[0] = hs[0]
    prev_lows = np.roll(ls, 1)
    prev_lows[0] = ls[0]

    up_move = hs - prev_highs
    down_move = prev_lows - ls

    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)

    # Fix first element
    plus_dm[0] = 0.0
    minus_dm[0] = 0.0

    # 2. Wilder Smoothing
    def smooth(vals, period):
        out = np.zeros_like(vals)
        if len(vals) < period:
            return out

        # First value is sum of first period
        out[period - 1] = np.sum(vals[:period])

        alpha = 1.0 / period
        out_view = out[period:]
        vals_view = vals[period:]

        curr = out[period - 1]
        for i in range(len(out_view)):
            curr = curr - (curr * alpha) + vals_view[i]
            out_view[i] = curr
        return out

    tr_smooth = smooth(trs, n)
    plus_dm_smooth = smooth(plus_dm, n)
    minus_dm_smooth = smooth(minus_dm, n)

    # 3. Calculate DI+ and DI-
    with np.errstate(divide="ignore", invalid="ignore"):
        plus_di = 100.0 * (plus_dm_smooth / tr_smooth)
        minus_di = 100.0 * (minus_dm_smooth / tr_smooth)

        # 4. Calculate DX
        dx = 100.0 * np.abs(plus_di - minus_di) / (plus_di + minus_di)

    plus_di = np.nan_to_num(plus_di)
    minus_di = np.nan_to_num(minus_di)
    dx = np.nan_to_num(dx)

    # 5. Calculate ADX (Smoothed DX)
    # First ADX is average of first N DX values starting from where DX is valid (n-1)
    adx = np.zeros_like(dx)

    # DX is valid from index n-1.
    # We need N values of DX to calculate first ADX.
    # So first ADX is at index (n-1) + (n-1) = 2n - 2.

    start_idx = 2 * n - 2
    if length > start_idx:
        # Average of DX[n-1 : 2n-1]
        adx[start_idx] = np.mean(dx[n - 1 : 2 * n - 1])

        curr = adx[start_idx]
        alpha = 1.0 / n

        dx_view = dx[start_idx + 1 :]
        adx_view = adx[start_idx + 1 :]

        for i in range(len(dx_view)):
            curr = (curr * (n - 1) + dx_view[i]) * alpha
            adx_view[i] = curr

    return adx.tolist()
