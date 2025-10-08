from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from core.indicators.adx import calculate_adx
from core.indicators.atr import calculate_atr
from core.indicators.bollinger import bollinger_bands
from core.indicators.ema import calculate_ema
from core.indicators.rsi import calculate_rsi
from core.indicators.volume import obv, volume_change, volume_trend


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

    # === BASIC FEATURES (original) ===
    ema_vals = calculate_ema(data_slice_close, period=12)
    rsi_vals = calculate_rsi(data_slice_close, period=14)
    ema_latest = ema_vals[-1] if ema_vals else 0.0
    close_latest = closes[last_idx]
    ema_delta_pct = 0.0 if close_latest == 0 else (ema_latest - close_latest) / close_latest
    rsi_latest = (rsi_vals[-1] - 50.0) / 50.0 if rsi_vals else 0.0  # Scale around 0

    # === VOLATILITY FEATURES ===
    # ATR - Average True Range
    atr_vals = calculate_atr(data_slice_high, data_slice_low, data_slice_close, period=14)
    atr_latest = atr_vals[-1] if atr_vals else 0.0
    atr_pct = (atr_latest / close_latest) if close_latest > 0 else 0.0

    # Bollinger Bands
    bb = bollinger_bands(data_slice_close, period=20, std_dev=2.0)
    bb_width = bb["width"][-1] if bb["width"] else 0.0
    bb_position = bb["position"][-1] if bb["position"] else 0.5

    # === TREND STRENGTH FEATURES ===
    # ADX - Average Directional Index
    adx_vals = calculate_adx(data_slice_high, data_slice_low, data_slice_close, period=14)
    adx_latest = adx_vals[-1] if adx_vals else 0.0
    adx_normalized = adx_latest / 100.0  # Scale 0-100 to 0-1

    # EMA slope (trend direction)
    if len(ema_vals) >= 5:
        ema_start = ema_vals[-5]
        ema_end = ema_vals[-1]
        ema_slope = (ema_end - ema_start) / ema_start if ema_start > 0 else 0.0
    else:
        ema_slope = 0.0

    # Price vs EMA (position)
    price_vs_ema = (close_latest - ema_latest) / ema_latest if ema_latest > 0 else 0.0

    # === VOLUME FEATURES ===
    # Volume change vs average
    vol_change_list = volume_change(data_slice_volume, period=20)
    vol_change_latest = vol_change_list[-1] if vol_change_list else 0.0

    # Volume trend (fast/slow ratio)
    vol_trend_list = volume_trend(data_slice_volume, fast_period=10, slow_period=50)
    vol_trend_latest = vol_trend_list[-1] if vol_trend_list else 1.0

    # OBV (On-Balance Volume)
    obv_vals = obv(data_slice_close, data_slice_volume)
    obv_latest = obv_vals[-1] if obv_vals else 0.0
    # Normalize OBV by cumulative volume
    total_volume = sum(data_slice_volume) if data_slice_volume else 1.0
    obv_normalized = obv_latest / total_volume if total_volume > 0 else 0.0

    # === BUILD FEATURE DICT ===
    # Apply clipping from config
    p_cfg = (cfg.get("features") or {}).get("percentiles") or {}
    ed_lo, ed_hi = p_cfg.get("ema_delta_pct", (-0.05, 0.05))
    rsi_lo, rsi_hi = p_cfg.get("rsi", (-1.0, 1.0))
    atr_lo, atr_hi = p_cfg.get("atr_pct", (0.0, 0.10))
    bb_w_lo, bb_w_hi = p_cfg.get("bb_width", (0.0, 0.20))
    vol_c_lo, vol_c_hi = p_cfg.get("vol_change", (-1.0, 2.0))

    feats: dict[str, float] = {
        # Original features
        "ema_delta_pct": _clip(ema_delta_pct, float(ed_lo), float(ed_hi)),
        "rsi": _clip(rsi_latest, float(rsi_lo), float(rsi_hi)),
        # Volatility features
        "atr_pct": _clip(atr_pct, float(atr_lo), float(atr_hi)),
        "bb_width": _clip(bb_width, float(bb_w_lo), float(bb_w_hi)),
        "bb_position": _clip(bb_position, 0.0, 1.0),
        # Trend features
        "adx": _clip(adx_normalized, 0.0, 1.0),
        "ema_slope": _clip(ema_slope, -0.05, 0.05),
        "price_vs_ema": _clip(price_vs_ema, -0.10, 0.10),
        # Volume features
        "vol_change": _clip(vol_change_latest, float(vol_c_lo), float(vol_c_hi)),
        "vol_trend": _clip(vol_trend_latest, 0.5, 2.0),
        "obv_normalized": _clip(obv_normalized, -1.0, 1.0),
    }

    meta: dict[str, Any] = {
        "versions": {
            **((cfg.get("features") or {}).get("versions") or {}),
            "features_v2": True,  # Mark as enhanced feature set
        },
        "reasons": [],
        "feature_count": len(feats),
    }
    return feats, meta
