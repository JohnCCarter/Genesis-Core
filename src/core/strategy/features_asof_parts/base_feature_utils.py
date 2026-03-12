from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class BaseFeatureBundle:
    features: dict[str, float]
    rsi_current: float
    atr_percentiles: dict[str, dict[str, float]]


def build_base_feature_bundle(
    rsi_current_raw: float,
    rsi_lag1_raw: float,
    bb_last_3: list[float],
    vol_shift_last_3: list[float],
    vol_shift_current: float,
    atr_window_56: list[float],
    atr_vals: list[float] | np.ndarray | None,
    atr14_current: float | None,
    clip_fn,
    build_atr_percentiles_fn,
) -> BaseFeatureBundle:
    rsi_inv_lag1 = (rsi_lag1_raw - 50.0) / 50.0

    if len(vol_shift_last_3) > 0:
        vol_shift_ma3 = sum(vol_shift_last_3) / len(vol_shift_last_3)
    else:
        vol_shift_ma3 = 1.0

    if len(bb_last_3) > 0:
        bb_inv_last_3 = [1.0 - pos for pos in bb_last_3]
        bb_position_inv_ma3 = sum(bb_inv_last_3) / len(bb_inv_last_3)
    else:
        bb_position_inv_ma3 = 0.5

    rsi_current = (rsi_current_raw - 50.0) / 50.0
    rsi_vol_interaction = rsi_current * clip_fn(vol_shift_current, 0.5, 2.0)
    vol_regime = 1.0 if vol_shift_current > 1.0 else 0.0

    atr_source = atr_window_56 if atr_window_56 else atr_vals
    atr_percentiles = build_atr_percentiles_fn(atr_source)

    features = {
        "rsi_inv_lag1": clip_fn(rsi_inv_lag1, -1.0, 1.0),
        "volatility_shift_ma3": clip_fn(vol_shift_ma3, 0.5, 2.0),
        "bb_position_inv_ma3": clip_fn(bb_position_inv_ma3, 0.0, 1.0),
        "rsi_vol_interaction": clip_fn(rsi_vol_interaction, -2.0, 2.0),
        "vol_regime": vol_regime,
        "atr_14": float(atr14_current) if atr14_current is not None else 0.0,
    }

    return BaseFeatureBundle(
        features=features,
        rsi_current=rsi_current,
        atr_percentiles=atr_percentiles,
    )
