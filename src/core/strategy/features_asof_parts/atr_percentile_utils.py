from __future__ import annotations

import numpy as np


def build_atr_percentiles(
    atr_source: list[float] | np.ndarray | None,
) -> dict[str, dict[str, float]]:
    atr_percentiles = {str(period): {"p40": 1.0, "p80": 1.0} for period in (14, 28, 56)}

    if atr_source is None:
        return atr_percentiles

    atr_arr = np.asarray(atr_source, dtype=float)
    n_atr = atr_arr.size
    if n_atr == 0:
        return atr_percentiles

    for period in (14, 28, 56):
        if n_atr >= period:
            window = atr_arr[-period:]
            p40, p80 = np.percentile(window, [40, 80])
            atr_percentiles[str(period)] = {
                "p40": float(p40),
                "p80": float(p80),
            }

    return atr_percentiles
