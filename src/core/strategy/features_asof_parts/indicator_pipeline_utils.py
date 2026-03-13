from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class IndicatorPipelineBundle:
    features: dict[str, float]
    rsi_current: float
    atr_percentiles: dict[str, dict[str, float]]
    atr_vals: list[float] | np.ndarray | None
    atr14_current: float | None
    rsi_used_fast_path: bool


def build_indicator_pipeline(
    highs: list[float] | np.ndarray,
    lows: list[float] | np.ndarray,
    closes: list[float] | np.ndarray,
    asof_bar: int,
    pre: dict[str, Any],
    pre_idx: int,
    atr_period: int,
    build_indicator_state_fn,
    build_base_feature_bundle_fn,
) -> IndicatorPipelineBundle:
    indicator_state = build_indicator_state_fn(
        highs,
        lows,
        closes,
        asof_bar,
        pre,
        pre_idx,
        atr_period,
    )

    base_feature_bundle = build_base_feature_bundle_fn(
        indicator_state.rsi_current_raw,
        indicator_state.rsi_lag1_raw,
        indicator_state.bb_last_3,
        indicator_state.vol_shift_last_3,
        indicator_state.vol_shift_current,
        indicator_state.atr_window_56,
        indicator_state.atr_vals,
        indicator_state.atr14_current,
    )

    return IndicatorPipelineBundle(
        features=dict(base_feature_bundle.features),
        rsi_current=base_feature_bundle.rsi_current,
        atr_percentiles=base_feature_bundle.atr_percentiles,
        atr_vals=indicator_state.atr_vals,
        atr14_current=indicator_state.atr14_current,
        rsi_used_fast_path=indicator_state.rsi_used_fast_path,
    )
