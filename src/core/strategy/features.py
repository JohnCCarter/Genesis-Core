from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import pandas as pd

from core.indicators.adx import calculate_adx
from core.indicators.atr import calculate_atr
from core.indicators.bollinger import bollinger_bands
from core.indicators.derived_features import calculate_volatility_shift
from core.indicators.ema import calculate_ema
from core.indicators.fibonacci import (
    FibonacciConfig,
    calculate_fibonacci_features,
    calculate_fibonacci_levels,
    detect_swing_points,
)
from core.indicators.rsi import calculate_rsi


def extract_features(
    candles: dict[str, Iterable[float]] | list[tuple[float, float, float, float, float, float]],
    *,
    config: dict[str, Any] | None = None,
    now_index: int | None = None,
    timeframe: str | None = None,
) -> tuple[dict[str, float], dict[str, Any]]:
    """Extrahera features från stängda candles (pure, ingen IO).

    Inparametrar
    - candles: antingen dict-of-lists {"open","high","low","close","volume"} (lika längd)
      eller lista av tuples (ts, open, high, low, close, volume) i stigande tid.
    - config: valfri strategi‑config som kan innehålla versioner/percentiler/klippgränser.
    - now_index: index för senaste stängda bar som ska användas (default: sista).

    Returnerar
    - features: dict[str,float] (ex: {"ema": x, "rsi": y})
    - meta: {"versions": {...}, "reasons": [...]} – ingen loggning här.

    Not: Denna funktion ska inte läsa framtida barer; använd endast stängda data.
    """
    cfg = dict(config or {})
    # Normalisera candles till dict-of-lists
    if isinstance(candles, dict):
        opens = list(map(float, candles.get("open", [])))
        highs = list(map(float, candles.get("high", [])))
        lows = list(map(float, candles.get("low", [])))
        closes = list(map(float, candles.get("close", [])))
        volumes = list(map(float, candles.get("volume", [])))
    else:
        # lista av (ts, o, h, l, c, v)
        opens = [float(t[1]) for t in candles]
        highs = [float(t[2]) for t in candles]
        lows = [float(t[3]) for t in candles]
        closes = [float(t[4]) for t in candles]
        volumes = [float(t[5]) for t in candles]

    length = min(len(opens), len(highs), len(lows), len(closes), len(volumes))
    if length == 0:
        return {}, {"versions": {}, "reasons": ["FAIL_SAFE_NULL"]}

    idx = length - 1 if now_index is None else int(now_index)
    if idx <= 0 or idx >= length:
        idx = length - 1

    # Använd endast stängda barer: ta features från idx-1 (senaste stängda)
    last_idx = idx - 1
    if last_idx < 0:
        return {}, {"versions": {}, "reasons": ["FAIL_SAFE_NULL"]}

    # Helper function for clipping
    def _clip(x: float, lo: float, hi: float) -> float:
        if x != x:  # NaN
            return 0.0
        if x == float("inf"):
            return hi
        if x == float("-inf"):
            return lo
        return max(lo, min(hi, x))

    # Slice data up to last_idx
    data_slice_close = closes[: last_idx + 1]
    data_slice_high = highs[: last_idx + 1]
    data_slice_low = lows[: last_idx + 1]

    # === CALCULATE ALL INDICATORS ===

    # ATR (needed for volatility shift)
    atr_vals = calculate_atr(data_slice_high, data_slice_low, data_slice_close, period=14)
    atr_long = calculate_atr(data_slice_high, data_slice_low, data_slice_close, period=50)

    # === CALCULATE CORE INDICATORS FOR v15 FEATURES ===

    # 1. RSI (momentum)
    rsi_vals = calculate_rsi(data_slice_close, period=14)
    rsi_latest = (rsi_vals[-1] - 50.0) / 50.0 if rsi_vals else 0.0  # Scale around 0

    # 2. Bollinger Position (volatility)
    bb = bollinger_bands(data_slice_close, period=20, std_dev=2.0)

    # 3. Volatility Shift (regime change)
    vol_shift = calculate_volatility_shift(atr_vals, atr_long)
    vol_shift_latest = vol_shift[-1] if vol_shift else 1.0

    # === CALCULATE SMOOTHED & LAGGED FEATURES (matching vectorized.py) ===

    # Get 3-bar window for smoothing
    bb_last_3 = bb["position"][-3:] if len(bb["position"]) >= 3 else [0.5] * 3
    vol_shift_last_3 = vol_shift[-3:] if len(vol_shift) >= 3 else [1.0] * 3

    # Smoothed (MA3)
    bb_inv_ma3 = sum([1.0 - pos for pos in bb_last_3]) / len(bb_last_3)
    vol_shift_ma3 = sum(vol_shift_last_3) / len(vol_shift_last_3)

    # Lagged (1-bar)
    rsi_inv_lag1 = (rsi_vals[-2] - 50.0) / 50.0 if len(rsi_vals) >= 2 else 0.0

    # Interaction (RSI × Vol)
    rsi_inv_current = -rsi_latest
    vol_shift_current = _clip(vol_shift_latest, 0.5, 2.0)
    rsi_vol_interaction = rsi_inv_current * vol_shift_current

    # Regime binary (HighVol = 1, LowVol = 0)
    vol_regime = 1.0 if vol_shift_current > 1.0 else 0.0

    # === CALCULATE FIBONACCI FEATURES ===
    # Adjusted parameters for 1D timeframe (less strict than 1h)
    fib_config = FibonacciConfig(atr_depth=3.0, max_swings=8, min_swings=1)
    current_price = data_slice_close[-1] if data_slice_close else 0.0
    current_atr = atr_vals[-1] if atr_vals else 1.0

    # Detect real swing points using ATR-based pivot detection
    swing_high_indices, swing_low_indices, swing_high_prices, swing_low_prices = (
        detect_swing_points(
            pd.Series(data_slice_high),
            pd.Series(data_slice_low),
            pd.Series(data_slice_close),
            fib_config,
        )
    )

    # Calculate Fibonacci retracement levels from detected swings
    fib_levels = calculate_fibonacci_levels(swing_high_prices, swing_low_prices, fib_config.levels)

    # Get current swing context for retrace depth calculation
    current_swing_high = swing_high_prices[-1] if swing_high_prices else current_price * 1.05
    current_swing_low = swing_low_prices[-1] if swing_low_prices else current_price * 0.95

    # Calculate Fibonacci features with real swing data
    fib_features = calculate_fibonacci_features(
        current_price, fib_levels, current_atr, fib_config, current_swing_high, current_swing_low
    )

    # === CALCULATE CONTEXT FEATURES FOR FIBONACCI COMBINATIONS ===

    # EMA Slope (timeframe-optimized parameters)
    # Optimized via parameter sweep: 30m uses EMA=50/lookback=20 (+166% improvement)
    # Other timeframes use standard EMA=20/lookback=5
    EMA_SLOPE_PARAMS = {
        "30m": {"ema_period": 50, "lookback": 20},  # Proven winner: +166% IC improvement
        "1h": {"ema_period": 20, "lookback": 5},  # Keep standard (overfit risk detected)
    }
    params = EMA_SLOPE_PARAMS.get(timeframe, {"ema_period": 20, "lookback": 5})

    ema_values = calculate_ema(data_slice_close, period=params["ema_period"])
    if len(ema_values) >= params["lookback"] + 1:
        ema_slope_raw = (ema_values[-1] - ema_values[-1 - params["lookback"]]) / ema_values[
            -1 - params["lookback"]
        ]
    else:
        ema_slope_raw = 0.0
    ema_slope = _clip(ema_slope_raw, -0.10, 0.10)

    # ADX (Average Directional Index) for trend strength
    adx_values = calculate_adx(data_slice_high, data_slice_low, data_slice_close, period=14)
    adx_latest = adx_values[-1] if adx_values else 25.0
    adx_normalized = adx_latest / 100.0  # Normalize to 0-1 range

    # === CALCULATE FIBONACCI COMBINATION FEATURES ===
    # These combinations have been validated via IC analysis on multiple timeframes

    # 1. fib05_x_ema_slope (CHAMPION - best on 1W, 1h, 30m)
    #    Use Case: Timing reversals when price reaches Fib 0.5 AND trend changes direction
    #    IC: -0.78 (1W), -0.04 (1h), -0.04 (30m)
    fib05_x_ema_slope = fib_features.get("fib05_prox_atr", 0.0) * ema_slope

    # 2. fib_prox_x_adx (TREND CONTINUATION - best on 6h)
    #    Use Case: Trend continuation setups when price near Fib AND strong trend
    #    IC: -0.20 (6h), +6.2% improvement vs baseline
    fib_prox_x_adx = fib_features.get("fib_prox_score", 0.0) * adx_normalized

    # 3. fib05_x_rsi_inv (MEAN REVERSION - best on 1W, 1D, 3h)
    #    Use Case: Oversold/overbought bounces at Fib 0.5 level
    #    IC: +0.70 (1W), +0.35 (1D), +0.10 (3h)
    fib05_x_rsi_inv = fib_features.get("fib05_prox_atr", 0.0) * (-rsi_latest)

    feats: dict[str, float] = {
        # === TOP 5 NON-REDUNDANT FEATURES (HighVol regime tested, IC-validated) ===
        "rsi_inv_lag1": _clip(rsi_inv_lag1, -1.0, 1.0),  # IC +0.0583, Spread +0.157%
        "volatility_shift_ma3": _clip(vol_shift_ma3, 0.5, 2.0),  # IC +0.0520, Spread +0.248%
        "bb_position_inv_ma3": _clip(bb_inv_ma3, 0.0, 1.0),  # IC +0.0555, Spread +0.145%
        "rsi_vol_interaction": _clip(rsi_vol_interaction, -2.0, 2.0),  # IC +0.0513, Spread +0.123%
        "vol_regime": vol_regime,  # IC +0.0462, binary indicator
        # === FIBONACCI FEATURES (v16) ===
        "fib_dist_min_atr": _clip(fib_features.get("fib_dist_min_atr", 0.0), 0.0, 10.0),
        "fib_dist_signed_atr": _clip(fib_features.get("fib_dist_signed_atr", 0.0), -10.0, 10.0),
        "fib_prox_score": _clip(fib_features.get("fib_prox_score", 0.0), 0.0, 1.0),
        "fib0618_prox_atr": _clip(fib_features.get("fib0618_prox_atr", 0.0), 0.0, 1.0),
        "fib05_prox_atr": _clip(fib_features.get("fib05_prox_atr", 0.0), 0.0, 1.0),
        "swing_retrace_depth": _clip(fib_features.get("swing_retrace_depth", 0.0), 0.0, 1.0),
        # === FIBONACCI COMBINATION FEATURES (v17) ===
        # Validated via IC analysis on multiple timeframes, zero new code (combinations only)
        "fib05_x_ema_slope": _clip(
            fib05_x_ema_slope, -0.10, 0.10
        ),  # Champion: +166% (30m), +1009% (1h)
        "fib_prox_x_adx": _clip(fib_prox_x_adx, 0.0, 1.0),  # Trend: +6.2% (6h)
        "fib05_x_rsi_inv": _clip(fib05_x_rsi_inv, -1.0, 1.0),  # Mean reversion: +23% (1W)
    }

    meta: dict[str, Any] = {
        "versions": {
            **((cfg.get("features") or {}).get("versions") or {}),
            "features_v17_fibonacci_combinations": True,  # v17: Added Fibonacci × Context combinations
        },
        "reasons": [],
        "feature_count": len(feats),  # 14 features: 5 original + 6 Fibonacci + 3 combinations
        "ema_slope_params": (
            params if timeframe else {"ema_period": 20, "lookback": 5}
        ),  # Track which params were used
    }
    return feats, meta
