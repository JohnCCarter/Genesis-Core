from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from core.indicators.adx import calculate_adx
from core.indicators.atr import calculate_atr
from core.indicators.bollinger import bollinger_bands
from core.indicators.derived_features import (
    calculate_momentum_displacement_z,
    calculate_price_reversion_potential,
    calculate_price_stretch_z,
    calculate_regime_persistence,
    calculate_trend_confluence,
    calculate_volatility_shift,
    calculate_volume_anomaly_z,
)
from core.indicators.ema import calculate_ema
from core.indicators.macd import calculate_macd
from core.indicators.rsi import calculate_rsi
from core.indicators.volume import calculate_volume_sma


def extract_features(
    candles: dict[str, Iterable[float]] | list[tuple[float, float, float, float, float, float]],
    *,
    config: dict[str, Any] | None = None,
    now_index: int | None = None,
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
    data_slice_volume = volumes[: last_idx + 1]
    current_close = closes[last_idx]

    # === CALCULATE ALL INDICATORS ===

    # EMAs (needed for multiple features)
    ema20_vals = calculate_ema(data_slice_close, period=20)
    ema50_vals = calculate_ema(data_slice_close, period=50)
    ema100_vals = calculate_ema(data_slice_close, period=100)

    # ATR (needed for multiple features)
    atr_vals = calculate_atr(data_slice_high, data_slice_low, data_slice_close, period=14)
    atr_long = calculate_atr(data_slice_high, data_slice_low, data_slice_close, period=50)

    # === ORIGINAL 3 FEATURES ===

    # 1. RSI (momentum)
    rsi_vals = calculate_rsi(data_slice_close, period=14)
    rsi_latest = (rsi_vals[-1] - 50.0) / 50.0 if rsi_vals else 0.0  # Scale around 0

    # 2. Bollinger Position (volatility)
    bb = bollinger_bands(data_slice_close, period=20, std_dev=2.0)
    bb_position = bb["position"][-1] if bb["position"] else 0.5

    # 3. Trend Confluence (DRIFT PROBLEM - men keep för IC test)
    trend_conf = calculate_trend_confluence(ema20_vals, ema100_vals, window=20)
    trend_conf_latest = trend_conf[-1] if trend_conf else 0.0

    # === FVG-DERIVED FEATURES (REACTIVATED!) ===

    # 4. Momentum Displacement (surge detection)
    mom_disp_z = calculate_momentum_displacement_z(data_slice_close, atr_vals, period=3, window=240)
    mom_disp = mom_disp_z[-1] if mom_disp_z else 0.0

    # 5. Price Stretch (mean reversion)
    price_stretch_z = calculate_price_stretch_z(data_slice_close, ema20_vals, atr_vals, window=240)
    price_stretch = price_stretch_z[-1] if price_stretch_z else 0.0

    # 6. Volatility Shift (regime change)
    vol_shift = calculate_volatility_shift(atr_vals, atr_long)
    vol_shift_latest = vol_shift[-1] if vol_shift else 1.0

    # 7. Volume Anomaly (orderflow)
    vol_anomaly_z = calculate_volume_anomaly_z(data_slice_volume, window=240)
    vol_anomaly = vol_anomaly_z[-1] if vol_anomaly_z else 0.0

    # 8. Regime Persistence (trend stability)
    regime_persist = calculate_regime_persistence(ema20_vals, window=24)
    regime_persist_latest = regime_persist[-1] if regime_persist else 0.0

    # 9. Price Reversion Potential (mean reversion strength)
    price_reversion = calculate_price_reversion_potential(price_stretch_z)
    price_reversion_latest = price_reversion[-1] if price_reversion else 0.0

    # === NEW CLASSICAL INDICATORS ===

    # 10. EMA Slope (trend direction - SHOULD HAVE POSITIVE IC!)
    if len(ema20_vals) > 5 and ema20_vals[-6] > 0:
        ema_slope = (ema20_vals[-1] - ema20_vals[-6]) / ema20_vals[-6]
        ema_slope_clipped = max(-0.05, min(0.05, ema_slope))  # Clip extremes
    else:
        ema_slope_clipped = 0.0

    # 11. ADX (trend strength)
    adx_vals = calculate_adx(data_slice_high, data_slice_low, data_slice_close, period=14)
    adx_latest = adx_vals[-1] / 50.0 if adx_vals else 0.0  # Normalize (0-50 range typical)

    # 12. ATR Percentage (volatility context)
    if current_close > 0 and atr_vals:
        atr_pct = atr_vals[-1] / current_close
    else:
        atr_pct = 0.0

    # 13. MACD Histogram (momentum shifts)
    macd_data = calculate_macd(data_slice_close, fast_period=12, slow_period=26, signal_period=9)
    macd_histogram = macd_data["histogram"][-1] if macd_data["histogram"] else 0.0
    # Normalize by current price
    if current_close > 0:
        macd_histogram_norm = macd_histogram / current_close
    else:
        macd_histogram_norm = 0.0

    # 14. Volume Ratio (confirmation)
    volume_sma = calculate_volume_sma(data_slice_volume, period=20)
    if volume_sma and volume_sma[-1] > 0 and data_slice_volume:
        volume_ratio = data_slice_volume[-1] / volume_sma[-1]
        volume_ratio_clipped = max(0.1, min(5.0, volume_ratio))  # Clip outliers
    else:
        volume_ratio_clipped = 1.0

    # 15. Price vs EMA (trend position)
    if ema50_vals and ema50_vals[-1] > 0:
        price_vs_ema = (current_close - ema50_vals[-1]) / ema50_vals[-1]
        price_vs_ema_clipped = max(-0.10, min(0.10, price_vs_ema))
    else:
        price_vs_ema_clipped = 0.0

    # === CALCULATE SMOOTHED & LAGGED FEATURES (matching vectorized.py) ===
    
    # Get 3-bar window for smoothing
    rsi_last_3 = rsi_vals[-3:] if len(rsi_vals) >= 3 else [0.0] * 3
    bb_last_3 = bb["position"][-3:] if len(bb["position"]) >= 3 else [0.5] * 3
    vol_shift_last_3 = vol_shift[-3:] if len(vol_shift) >= 3 else [1.0] * 3
    
    # Smoothed (MA3)
    rsi_inv_ma3 = sum([(r - 50.0) / 50.0 for r in rsi_last_3]) / len(rsi_last_3)
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
    
    feats: dict[str, float] = {
        # === TOP 5 NON-REDUNDANT FEATURES (HighVol regime tested, IC-validated) ===
        "rsi_inv_lag1": _clip(rsi_inv_lag1, -1.0, 1.0),  # IC +0.0583, Spread +0.157%
        "volatility_shift_ma3": _clip(vol_shift_ma3, 0.5, 2.0),  # IC +0.0520, Spread +0.248%
        "bb_position_inv_ma3": _clip(bb_inv_ma3, 0.0, 1.0),  # IC +0.0555, Spread +0.145%
        "rsi_vol_interaction": _clip(rsi_vol_interaction, -2.0, 2.0),  # IC +0.0513, Spread +0.123%
        "vol_regime": vol_regime,  # IC +0.0462, binary indicator
    }

    meta: dict[str, Any] = {
        "versions": {
            **((cfg.get("features") or {}).get("versions") or {}),
            "features_v15_highvol_optimized": True,  # v15: HighVol regime-tested, Partial-IC selected
        },
        "reasons": [],
        "feature_count": len(feats),  # 5 non-redundant features
    }
    return feats, meta
