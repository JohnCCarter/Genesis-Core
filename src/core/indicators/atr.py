from __future__ import annotations

from collections.abc import Iterable

import numpy as np


def calculate_atr(
    highs: Iterable[float], lows: Iterable[float], closes: Iterable[float], period: int
) -> list[float]:
    """Beräkna Average True Range (ATR) med vektoriserad NumPy.

    highs/lows/closes ska vara lika långa.
    """
    hs = np.asarray(highs, dtype=float)
    ls = np.asarray(lows, dtype=float)
    cs = np.asarray(closes, dtype=float)

    if not (len(hs) == len(ls) == len(cs)):
        raise ValueError("highs/lows/closes must have same length")
    n = int(period)
    if n <= 0:
        raise ValueError("period must be > 0")
    if len(hs) == 0:
        return []

    # Calculate True Range (Vectorized)
    # TR = max(H-L, abs(H-Cp), abs(L-Cp))

    # Shift closes to get prev_close (pad with first close to avoid NaN at start,
    # though TR[0] is usually just H-L, but standard def often uses prev close.
    # We'll match the original logic: prev_close = cs[0] for first iteration)
    prev_closes = np.roll(cs, 1)
    prev_closes[0] = cs[0]

    tr1 = hs - ls
    tr2 = np.abs(hs - prev_closes)
    tr3 = np.abs(ls - prev_closes)

    trs = np.maximum(tr1, np.maximum(tr2, tr3))

    # Calculate ATR using Wilder's Smoothing (alpha = 1/n)
    atr = np.zeros_like(trs)

    # First ATR is simple average of first N TRs (or just first TR? Original code used trs[0] as init)
    # Original code: atr = [trs[0]]; for tr in trs[1:]: atr.append(atr[-1] + alpha * (tr - atr[-1]))
    # This means ATR[0] = TR[0].

    atr[0] = trs[0]
    alpha = 1.0 / n

    # Fast loop for recursive smoothing
    # Using a view for speed
    for i in range(1, len(trs)):
        atr[i] = atr[i - 1] + alpha * (trs[i] - atr[i - 1])

    return atr.tolist()
