from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from core.indicators.bollinger import bollinger_bands
from core.indicators.derived_features import (
    calculate_trend_confluence,
)
from core.indicators.ema import calculate_ema
from core.indicators.rsi import calculate_rsi


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
    highs[: last_idx + 1]
    lows[: last_idx + 1]
    volumes[: last_idx + 1]

    # === FEATURES FOR V10 (TOP 3) ===
    closes[last_idx]

    # 1. RSI (momentum)
    rsi_vals = calculate_rsi(data_slice_close, period=14)
    rsi_latest = (rsi_vals[-1] - 50.0) / 50.0 if rsi_vals else 0.0  # Scale around 0

    # 2. Bollinger Position (mean reversion)
    bb = bollinger_bands(data_slice_close, period=20, std_dev=2.0)
    bb_position = bb["position"][-1] if bb["position"] else 0.5

    # 3. Trend Confluence (multi-TF alignment - DERIVED from FVG concept)
    ema20_vals = calculate_ema(data_slice_close, period=20)
    ema100_vals = calculate_ema(data_slice_close, period=100)
    trend_conf = calculate_trend_confluence(ema20_vals, ema100_vals, window=20)
    trend_conf_latest = trend_conf[-1] if trend_conf else 0.0

    # NOTE: FVG features removed after testing showed consistent AUC degradation
    # FVG concepts preserved as pure statistical features above (derived_features)

    # === BUILD FEATURE DICT ===
    # Apply clipping from config
    p_cfg = (cfg.get("features") or {}).get("percentiles") or {}
    ed_lo, ed_hi = p_cfg.get("ema_delta_pct", (-0.05, 0.05))
    rsi_lo, rsi_hi = p_cfg.get("rsi", (-1.0, 1.0))
    atr_lo, atr_hi = p_cfg.get("atr_pct", (0.0, 0.10))
    bb_w_lo, bb_w_hi = p_cfg.get("bb_width", (0.0, 0.20))
    vol_c_lo, vol_c_hi = p_cfg.get("vol_change", (-1.0, 2.0))

    feats: dict[str, float] = {
        # CLEAN: TOP 3 POSITIVE PERMUTATION IMPORTANCE (v10 - lookahead-free baseline)
        # Remove NEGATIVE features: vol_trend (-2.21%), momentum_displacement_z (-1.15%)
        "bb_position": _clip(bb_position, 0.0, 1.0),  # +2.02% (BEST!)
        "trend_confluence": _clip(trend_conf_latest, -1.0, 1.0),  # +0.99% (DERIVED!)
        "rsi": _clip(rsi_latest, float(rsi_lo), float(rsi_hi)),  # +0.33% (MOMENTUM)
    }

    meta: dict[str, Any] = {
        "versions": {
            **((cfg.get("features") or {}).get("versions") or {}),
            "features_v10": True,  # v10: Lookahead-free + TOP 3 positive features
        },
        "reasons": [],
        "feature_count": 3,  # bb_position, trend_confluence, rsi
    }
    return feats, meta
