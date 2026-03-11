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
    rsi_current: float,
    fallback_features: dict[str, float],
    clip_fn,
    fib_config_cls,
    make_indicator_fingerprint_fn,
    indicator_cache_lookup_fn,
    indicator_cache_store_fn,
    detect_swing_points_fn,
    calculate_fibonacci_levels_fn,
    calculate_fibonacci_features_fn,
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
        current_price = closes[-1] if len(closes) > 0 else 0.0
        current_atr = atr_values[-1] if atr_values else 1.0

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
            hi_cut = bisect_right(pre_sw_hi_idx, pre_idx)
            lo_cut = bisect_right(pre_sw_lo_idx, pre_idx)

            swing_high_indices = [int(i) for i in pre_sw_hi_idx[:hi_cut]]
            swing_low_indices = [int(i) for i in pre_sw_lo_idx[:lo_cut]]
            swing_high_prices = [float(p) for p in pre_sw_hi_px[:hi_cut]]
            swing_low_prices = [float(p) for p in pre_sw_lo_px[:lo_cut]]
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
                        atr_values=atr_values,
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

        pre_ema_slope = pre.get("ema_slope")
        if isinstance(pre_ema_slope, list | tuple) and len(pre_ema_slope) > pre_idx:
            ema_slope_raw = float(pre_ema_slope[pre_idx])
        else:
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
            pre_ema_key = f"ema_{ema_period}"
            pre_ema_full = pre.get(pre_ema_key)
            if isinstance(pre_ema_full, list | tuple) and len(pre_ema_full) >= asof_bar + 1:
                ema_values = list(pre_ema_full[: asof_bar + 1])
            else:
                ema_key = make_indicator_fingerprint_fn(
                    "ema",
                    params={"period": ema_period},
                    series=closes,
                )
                cached_ema = indicator_cache_lookup_fn(ema_key)
                if cached_ema is not None and len(cached_ema) >= asof_bar + 1:
                    ema_values = cached_ema[: asof_bar + 1]
                else:
                    ema_full = calculate_ema_fn(closes, period=ema_period)
                    indicator_cache_store_fn(ema_key, ema_full)
                    ema_values = ema_full
            if len(ema_values) >= ema_lookback + 1:
                ema_slope_raw = (ema_values[-1] - ema_values[-1 - ema_lookback]) / ema_values[
                    -1 - ema_lookback
                ]
            else:
                ema_slope_raw = 0.0
        ema_slope = clip_fn(ema_slope_raw, -0.10, 0.10)

        pre_adx_full = pre.get("adx_14")
        if isinstance(pre_adx_full, list | tuple) and len(pre_adx_full) > pre_idx:
            adx_values = list(pre_adx_full[: pre_idx + 1])
            adx_latest = float(pre_adx_full[pre_idx])
        else:
            adx_key = make_indicator_fingerprint_fn(
                "adx",
                params={"period": 14},
                series=list(zip(highs, lows, closes, strict=False)),
            )
            cached_adx = indicator_cache_lookup_fn(adx_key)
            if cached_adx is not None and len(cached_adx) >= asof_bar + 1:
                adx_values = cached_adx[: asof_bar + 1]
            else:
                adx_full = calculate_adx_fn(highs, lows, closes, period=14)
                indicator_cache_store_fn(adx_key, adx_full)
                adx_values = adx_full
            adx_latest = adx_values[-1] if adx_values else 25.0
        adx_normalized = adx_latest / 100.0

        fib05_x_ema_slope = fib_feature_updates.get("fib05_prox_atr", 0.0) * ema_slope
        fib_prox_x_adx = fib_feature_updates.get("fib_prox_score", 0.0) * adx_normalized
        fib05_x_rsi_inv = fib_feature_updates.get("fib05_prox_atr", 0.0) * (-rsi_current)

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
