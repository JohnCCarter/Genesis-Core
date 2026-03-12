from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class IndicatorState:
    rsi_current_raw: float
    rsi_lag1_raw: float
    bb_last_3: list[float]
    atr_vals: list[float] | np.ndarray | None
    atr_window_56: list[float]
    atr14_current: float | None
    vol_shift_last_3: list[float]
    vol_shift_current: float
    rsi_used_fast_path: bool


def build_indicator_state(
    highs: list[float] | np.ndarray,
    lows: list[float] | np.ndarray,
    closes: list[float] | np.ndarray,
    asof_bar: int,
    pre: dict[str, Any],
    pre_idx: int,
    atr_period: int,
    make_indicator_fingerprint_fn,
    indicator_cache_lookup_fn,
    indicator_cache_store_fn,
    calculate_rsi_fn,
    bollinger_bands_fn,
    calculate_atr_fn,
    calculate_volatility_shift_fn,
) -> IndicatorState:
    pre_rsi = pre.get("rsi_14")
    rsi_vals = None
    rsi_current_raw = 50.0
    rsi_lag1_raw = 50.0
    rsi_used_fast_path = False

    if isinstance(pre_rsi, list | tuple) and len(pre_rsi) > pre_idx:
        rsi_used_fast_path = True
        rsi_current_raw = float(pre_rsi[pre_idx])
        rsi_lag1_raw = float(pre_rsi[pre_idx - 1]) if pre_idx > 0 else rsi_current_raw
    else:
        key = make_indicator_fingerprint_fn(
            "rsi",
            params={"period": 14},
            series=closes,
        )
        cached_rsi = indicator_cache_lookup_fn(key)
        if cached_rsi is not None and len(cached_rsi) >= asof_bar + 1:
            rsi_vals = cached_rsi[: asof_bar + 1]
        else:
            rsi_full = calculate_rsi_fn(closes, period=14)
            indicator_cache_store_fn(key, rsi_full)
            rsi_vals = rsi_full

        if rsi_vals:
            rsi_current_raw = rsi_vals[-1]
            rsi_lag1_raw = rsi_vals[-2] if len(rsi_vals) > 1 else rsi_current_raw

    pre_bb_pos = pre.get("bb_position_20_2")
    bb_vals = None
    bb_last_3: list[float] = []

    if isinstance(pre_bb_pos, list | tuple) and len(pre_bb_pos) > pre_idx:
        start_idx = max(0, pre_idx - 2)
        bb_last_3 = list(pre_bb_pos[start_idx : pre_idx + 1])
    else:
        close_series = closes.tolist() if isinstance(closes, np.ndarray) else closes
        bb_key = make_indicator_fingerprint_fn(
            "bollinger",
            params={"period": 20, "std_dev": 2.0},
            series=close_series,
        )
        cached_bb = indicator_cache_lookup_fn(bb_key)
        if cached_bb is not None and len(cached_bb.get("position", [])) >= asof_bar + 1:
            bb_vals = list(cached_bb["position"][: asof_bar + 1])
        else:
            bb_full = bollinger_bands_fn(close_series, period=20, std_dev=2.0)
            indicator_cache_store_fn(bb_key, bb_full)
            bb_vals = bb_full["position"]

        if bb_vals:
            bb_last_3 = bb_vals[-3:]

    pre_atr_key = f"atr_{atr_period}"
    pre_atr_full = pre.get(pre_atr_key)
    if pre_atr_full is None and atr_period == 14:
        pre_atr_full = pre.get("atr_14")

    atr_vals: list[float] | np.ndarray | None = None
    atr_window_56: list[float] = []

    if isinstance(pre_atr_full, list | tuple) and len(pre_atr_full) > pre_idx:
        start_idx = max(0, pre_idx - 55)
        atr_window_56 = list(pre_atr_full[start_idx : pre_idx + 1])
        atr_vals = list(pre_atr_full[: pre_idx + 1])
    else:
        key_atr = make_indicator_fingerprint_fn(
            f"atr_{atr_period}",
            params={"period": atr_period},
            series=closes,
        )
        cached_atr = indicator_cache_lookup_fn(key_atr)
        if cached_atr is not None and len(cached_atr) >= asof_bar + 1:
            atr_vals = cached_atr[: asof_bar + 1]
        else:
            atr_full = calculate_atr_fn(highs, lows, closes, period=atr_period)
            indicator_cache_store_fn(key_atr, atr_full)
            atr_vals = atr_full

        if atr_vals:
            atr_window_56 = list(atr_vals[-56:])

    atr14_vals = None
    atr14_current = None
    if atr_period == 14:
        atr14_vals = atr_vals
        atr14_current = float(atr_vals[-1]) if atr_vals else None
    else:
        pre_atr14_full = pre.get("atr_14")
        if isinstance(pre_atr14_full, list | tuple) and len(pre_atr14_full) > pre_idx:
            atr14_current = float(pre_atr14_full[pre_idx])
            atr14_vals = list(pre_atr14_full[: pre_idx + 1])
        else:
            key_atr14 = make_indicator_fingerprint_fn(
                "atr_14",
                params={"period": 14},
                series=closes,
            )
            cached_atr14 = indicator_cache_lookup_fn(key_atr14)
            if cached_atr14 is not None and len(cached_atr14) >= asof_bar + 1:
                atr14_vals = cached_atr14[: asof_bar + 1]
            else:
                atr14_full = calculate_atr_fn(highs, lows, closes, period=14)
                indicator_cache_store_fn(key_atr14, atr14_full)
                atr14_vals = atr14_full
            atr14_current = float(atr14_vals[-1]) if atr14_vals else None

    pre_atr50_full = pre.get("atr_50")
    atr_long = None
    if not pre.get("volatility_shift"):
        if isinstance(pre_atr50_full, list | tuple) and len(pre_atr50_full) > pre_idx:
            atr_long = list(pre_atr50_full[: pre_idx + 1])
        else:
            key_atr50 = make_indicator_fingerprint_fn(
                "atr_50",
                params={"period": 50},
                series=closes,
            )
            cached_atr50 = indicator_cache_lookup_fn(key_atr50)
            if cached_atr50 is not None and len(cached_atr50) >= asof_bar + 1:
                atr_long = cached_atr50[: asof_bar + 1]
            else:
                atr_long_full = calculate_atr_fn(highs, lows, closes, period=50)
                indicator_cache_store_fn(key_atr50, atr_long_full)
                atr_long = atr_long_full

    pre_vol_shift = pre.get("volatility_shift")
    vol_shift_vals = None
    vol_shift_last_3: list[float] = []
    vol_shift_current = 1.0

    if isinstance(pre_vol_shift, list | tuple) and len(pre_vol_shift) > pre_idx:
        start_idx = max(0, pre_idx - 2)
        vol_shift_last_3 = list(pre_vol_shift[start_idx : pre_idx + 1])
        vol_shift_current = float(pre_vol_shift[pre_idx])
    else:
        if atr_vals is None and isinstance(pre_atr_full, list | tuple):
            atr_vals = list(pre_atr_full[: pre_idx + 1])

        if atr_vals and atr_long:
            vol_key = make_indicator_fingerprint_fn(
                "volatility_shift",
                params={},
                series=[atr_vals, atr_long],
            )
            cached_vol_shift = indicator_cache_lookup_fn(vol_key)
            if cached_vol_shift is not None and len(cached_vol_shift) >= len(atr_vals):
                vol_shift_vals = cached_vol_shift[: len(atr_vals)]
            else:
                vol_shift_vals = calculate_volatility_shift_fn(atr_vals, atr_long)
                indicator_cache_store_fn(vol_key, vol_shift_vals)

            if vol_shift_vals:
                vol_shift_last_3 = list(vol_shift_vals[-3:])
                vol_shift_current = float(vol_shift_vals[-1])

    return IndicatorState(
        rsi_current_raw=rsi_current_raw,
        rsi_lag1_raw=rsi_lag1_raw,
        bb_last_3=bb_last_3,
        atr_vals=atr_vals,
        atr_window_56=atr_window_56,
        atr14_current=atr14_current,
        vol_shift_last_3=vol_shift_last_3,
        vol_shift_current=vol_shift_current,
        rsi_used_fast_path=rsi_used_fast_path,
    )
