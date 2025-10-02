from __future__ import annotations

from typing import Iterable, List


def calculate_adx(
    highs: Iterable[float],
    lows: Iterable[float],
    closes: Iterable[float],
    period: int = 14,
) -> List[float]:
    """Beräkna ADX (Average Directional Index) med Wilder-smoothing.

    Returnerar ADX med samma längd som input (pad i början med 0 tills nog data).
    """
    hs = [float(x) for x in highs]
    ls = [float(x) for x in lows]
    cs = [float(x) for x in closes]
    if not (len(hs) == len(ls) == len(cs)):
        raise ValueError("highs/lows/closes must have same length")
    n = int(period)
    if n <= 0:
        raise ValueError("period must be > 0")
    length = len(hs)
    if length == 0:
        return []

    # True Range + directional movement
    trs: List[float] = []
    plus_dm: List[float] = []
    minus_dm: List[float] = []
    for i in range(length):
        if i == 0:
            trs.append(hs[0] - ls[0])
            plus_dm.append(0.0)
            minus_dm.append(0.0)
            continue
        up_move = hs[i] - hs[i - 1]
        down_move = ls[i - 1] - ls[i]
        trs.append(max(hs[i] - ls[i], abs(hs[i] - cs[i - 1]), abs(ls[i] - cs[i - 1])))
        plus_dm.append(up_move if up_move > down_move and up_move > 0 else 0.0)
        minus_dm.append(down_move if down_move > up_move and down_move > 0 else 0.0)

    # Wilder smoothing
    def wilder_smooth(vals: List[float], n: int) -> List[float]:
        if not vals:
            return []
        out = [sum(vals[:n])]
        for i in range(n, len(vals)):
            out.append(out[-1] - out[-1] / n + vals[i])
        return out

    atr_w = wilder_smooth(trs, n)
    plus_dm_w = wilder_smooth(plus_dm, n)
    minus_dm_w = wilder_smooth(minus_dm, n)

    # +DI, -DI
    plus_di: List[float] = [0.0] * length
    minus_di: List[float] = [0.0] * length
    for i in range(n - 1, length):
        atr = atr_w[i - (n - 1)]
        if atr > 0:
            plus_di[i] = 100.0 * (plus_dm_w[i - (n - 1)] / atr)
            minus_di[i] = 100.0 * (minus_dm_w[i - (n - 1)] / atr)

    # DX
    dx: List[float] = [0.0] * length
    for i in range(n - 1, length):
        p, m = plus_di[i], minus_di[i]
        denom = p + m
        if denom > 0:
            dx[i] = 100.0 * abs(p - m) / denom
        else:
            dx[i] = 0.0

    # ADX: Wilder smoothing av DX
    adx: List[float] = [0.0] * length
    # initial ADX (genomsnitt av första n DX efter n-1 index)
    if length >= 2 * n - 1:
        first_avg = sum(dx[n - 1 : 2 * n - 1]) / n
        adx[2 * n - 2] = first_avg
        for i in range(2 * n - 1, length):
            adx[i] = (adx[i - 1] * (n - 1) + dx[i]) / n
    return adx
