from __future__ import annotations

from collections.abc import Iterable


def calculate_atr(
    highs: Iterable[float], lows: Iterable[float], closes: Iterable[float], period: int
) -> list[float]:
    """Beräkna Average True Range (ATR) som ren funktion.

    highs/lows/closes ska vara lika långa. ATR returneras med samma längd;
    första värdet sätts till första true range och därefter EMA-aktig smoothing.
    """
    hs = [float(x) for x in highs]
    ls = [float(x) for x in lows]
    cs = [float(x) for x in closes]
    if not (len(hs) == len(ls) == len(cs)):
        raise ValueError("highs/lows/closes must have same length")
    n = int(period)
    if n <= 0:
        raise ValueError("period must be > 0")
    if len(hs) == 0:
        return []
    trs: list[float] = []
    prev_close = cs[0]
    for h, low, c in zip(hs, ls, cs, strict=False):
        tr = max(h - low, abs(h - prev_close), abs(low - prev_close))
        trs.append(tr)
        prev_close = c
    # Smidig ATR: EMA över TR med alpha 1/period (Wilder's smoothing approximativt)
    alpha = 1.0 / float(n)
    atr: list[float] = [trs[0]]
    for tr in trs[1:]:
        atr.append(atr[-1] + alpha * (tr - atr[-1]))
    return atr
