from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from core.indicators.atr import calculate_atr
from core.indicators.bollinger import bollinger_bands
from core.indicators.derived_features import calculate_volatility_shift
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
