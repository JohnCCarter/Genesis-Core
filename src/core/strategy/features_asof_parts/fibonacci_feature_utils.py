from __future__ import annotations

from bisect import bisect_right
from typing import Any

import numpy as np


def build_fibonacci_feature_updates(
    highs: list[float] | np.ndarray,
    lows: list[float] | np.ndarray,
    closes: list[float] | np.ndarray,
    atr_values: list[float] | np.ndarray | None,
    pre: dict[str, Any],
    pre_idx: int,
    timeframe: str | None,
    asof_bar: int,
    atr_period: int,
    rsi_current: float,
    fallback_features: dict[str, float],
    clip_fn,
    fib_config_cls,
    make_indicator_fingerprint_fn,
    indicator_cache_lookup_fn,
    indicator_cache_store_fn,
    calculate_atr_fn,
    detect_swing_points_fn,
    calculate_fibonacci_levels_fn,
    calculate_fibonacci_features_fn,
    calculate_rsi_fn,
    calculate_ema_fn,
    calculate_adx_fn,
    metrics_obj,
    logger,
) -> tuple[dict[str, float], dict[str, Any]]:
    fib_feature_status: dict[str, Any] = {
        "available": True,
        "reason": "OK",
    }
    try:
        fib_config = fib_config_cls(atr_depth=3.0, max_swings=8, min_swings=1)
        confirmed_idx = pre_idx - max(1, int(fib_config.atr_depth))
        current_price = closes[-1] if len(closes) > 0 else 0.0
        window_len = len(closes)

        def _local_indicator_series(name: str, params: dict[str, Any], series, build_fn):
            cache_key = make_indicator_fingerprint_fn(
                name,
                params={**params, "window_bounded": True, "window_len": window_len},
                series=series,
            )
            cached = indicator_cache_lookup_fn(cache_key)
            if cached is not None and len(cached) >= window_len:
                return list(cached[:window_len])
            values = build_fn()
            indicator_cache_store_fn(cache_key, values)
            return list(values)

        local_atr_values = _local_indicator_series(
            f"fib_atr_{int(atr_period)}",
            {"period": int(atr_period)},
            [highs, lows, closes],
            lambda: calculate_atr_fn(highs, lows, closes, period=atr_period),
        )
        current_atr = float(local_atr_values[-1]) if local_atr_values else 1.0

        pre_sw_hi_idx = pre.get("fib_high_idx")
        pre_sw_lo_idx = pre.get("fib_low_idx")
        pre_sw_hi_px = pre.get("fib_high_px")
        pre_sw_lo_px = pre.get("fib_low_px")
        if (
            isinstance(pre_sw_hi_idx, list | tuple)
            and isinstance(pre_sw_lo_idx, list | tuple)
            and isinstance(pre_sw_hi_px, list | tuple)
            and isinstance(pre_sw_lo_px, list | tuple)
        ):
            hi_cut = bisect_right(pre_sw_hi_idx, confirmed_idx)
            lo_cut = bisect_right(pre_sw_lo_idx, confirmed_idx)

            eligible_high_indices = [int(i) for i in pre_sw_hi_idx[:hi_cut]]
            eligible_low_indices = [int(i) for i in pre_sw_lo_idx[:lo_cut]]
            eligible_high_prices = [float(p) for p in pre_sw_hi_px[:hi_cut]]
            eligible_low_prices = [float(p) for p in pre_sw_lo_px[:lo_cut]]

            if eligible_high_indices:
                last_high_idx = eligible_high_indices[-1]
                high_pairs = [
                    (idx, price)
                    for idx, price in zip(eligible_high_indices, eligible_high_prices, strict=False)
                    if (last_high_idx - idx) <= fib_config.max_lookback
                ]
            else:
                high_pairs = []

            if eligible_low_indices:
                last_low_idx = eligible_low_indices[-1]
                low_pairs = [
                    (idx, price)
                    for idx, price in zip(eligible_low_indices, eligible_low_prices, strict=False)
                    if (last_low_idx - idx) <= fib_config.max_lookback
                ]
            else:
                low_pairs = []

            swing_high_indices = [idx for idx, _ in high_pairs[-fib_config.max_swings :]]
            swing_low_indices = [idx for idx, _ in low_pairs[-fib_config.max_swings :]]
            swing_high_prices = [price for _, price in high_pairs[-fib_config.max_swings :]]
            swing_low_prices = [price for _, price in low_pairs[-fib_config.max_swings :]]
        else:
            swing_key = make_indicator_fingerprint_fn(
                "fib_swings",
                params={
                    "atr_depth": fib_config.atr_depth,
                    "max_swings": fib_config.max_swings,
                    "min_swings": fib_config.min_swings,
                },
                series=[highs, lows, closes],
            )
            cached_swings = indicator_cache_lookup_fn(swing_key)
            if cached_swings:
                swing_high_indices = cached_swings.get("swing_high_indices", [])
                swing_low_indices = cached_swings.get("swing_low_indices", [])
                swing_high_prices = cached_swings.get("swing_high_prices", [])
                swing_low_prices = cached_swings.get("swing_low_prices", [])
            else:
                swing_high_indices, swing_low_indices, swing_high_prices, swing_low_prices = (
                    detect_swing_points_fn(
                        highs,
                        lows,
                        closes,
                        fib_config,
                        atr_values=local_atr_values,
                    )
                )
                indicator_cache_store_fn(
                    swing_key,
                    {
                        "swing_high_indices": swing_high_indices,
                        "swing_low_indices": swing_low_indices,
                        "swing_high_prices": swing_high_prices,
                        "swing_low_prices": swing_low_prices,
                    },
                )
        fib_levels = calculate_fibonacci_levels_fn(
            swing_high_prices,
            swing_low_prices,
            fib_config.levels,
        )
        if not swing_high_prices or not swing_low_prices or not fib_levels:
            fib_feature_status = {
                "available": False,
                "reason": "insufficient_local_history",
            }

        current_swing_high = swing_high_prices[-1] if swing_high_prices else current_price * 1.05
        current_swing_low = swing_low_prices[-1] if swing_low_prices else current_price * 0.95

        fib_feats = calculate_fibonacci_features_fn(
            current_price,
            fib_levels,
            current_atr,
            fib_config,
            current_swing_high,
            current_swing_low,
        )

        fib_feature_updates = {
            "fib_dist_min_atr": clip_fn(fib_feats.get("fib_dist_min_atr", 0.0), 0.0, 10.0),
            "fib_dist_signed_atr": clip_fn(
                fib_feats.get("fib_dist_signed_atr", 0.0),
                -10.0,
                10.0,
            ),
            "fib_prox_score": clip_fn(fib_feats.get("fib_prox_score", 0.0), 0.0, 1.0),
            "fib0618_prox_atr": clip_fn(fib_feats.get("fib0618_prox_atr", 0.0), 0.0, 1.0),
            "fib05_prox_atr": clip_fn(fib_feats.get("fib05_prox_atr", 0.0), 0.0, 1.0),
            "swing_retrace_depth": clip_fn(
                fib_feats.get("swing_retrace_depth", 0.0),
                0.0,
                1.0,
            ),
        }

        ema_slope_params = {
            "30m": {"ema_period": 50, "lookback": 20},
            "1h": {"ema_period": 20, "lookback": 5},
            "3h": {"ema_period": 20, "lookback": 5},
        }
        params = ema_slope_params.get(
            str(timeframe or "").lower(),
            {"ema_period": 20, "lookback": 5},
        )
        ema_period = params["ema_period"]
        ema_lookback = params["lookback"]
        ema_values = _local_indicator_series(
            f"fib_ema_{int(ema_period)}",
            {"period": int(ema_period)},
            closes,
            lambda: calculate_ema_fn(closes, period=ema_period),
        )
        if len(ema_values) >= ema_lookback + 1:
            ema_slope_raw = (ema_values[-1] - ema_values[-1 - ema_lookback]) / ema_values[
                -1 - ema_lookback
            ]
        else:
            ema_slope_raw = 0.0
        ema_slope = clip_fn(ema_slope_raw, -0.10, 0.10)

        local_rsi_values = _local_indicator_series(
            "fib_rsi_14",
            {"period": 14},
            closes,
            lambda: calculate_rsi_fn(closes, period=14),
        )
        fib_rsi_current = float(local_rsi_values[-1]) if local_rsi_values else float(rsi_current)

        adx_values = _local_indicator_series(
            "fib_adx_14",
            {"period": 14},
            [highs, lows, closes],
            lambda: calculate_adx_fn(highs, lows, closes, period=14),
        )
        adx_latest = float(adx_values[-1]) if adx_values else 25.0
        adx_normalized = adx_latest / 100.0

        fib05_x_ema_slope = fib_feature_updates.get("fib05_prox_atr", 0.0) * ema_slope
        fib_prox_x_adx = fib_feature_updates.get("fib_prox_score", 0.0) * adx_normalized
        fib05_x_rsi_inv = fib_feature_updates.get("fib05_prox_atr", 0.0) * (-fib_rsi_current)

        fib_feature_updates.update(
            {
                "fib05_x_ema_slope": clip_fn(fib05_x_ema_slope, -0.10, 0.10),
                "fib_prox_x_adx": clip_fn(fib_prox_x_adx, 0.0, 1.0),
                "fib05_x_rsi_inv": clip_fn(fib05_x_rsi_inv, -1.0, 1.0),
            }
        )
        return fib_feature_updates, fib_feature_status
    except Exception as exc:
        try:
            metrics_obj.inc("feature_fib_errors")
        except Exception:  # nosec B110
            pass
        if logger:
            logger.warning("fib feature combination failed: %s", exc)
        return dict(fallback_features), {
            "available": False,
            "reason": "FIB_FEATURES_CONTEXT_ERROR",
        }
