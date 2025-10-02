from __future__ import annotations

from typing import Any, Dict, Iterable, List, Tuple

from core.indicators.ema import calculate_ema
from core.indicators.rsi import calculate_rsi


def extract_features(
    candles: (Dict[str, Iterable[float]] | List[Tuple[float, float, float, float, float, float]]),
    *,
    config: Dict[str, Any] | None = None,
    now_index: int | None = None,
) -> Tuple[Dict[str, float], Dict[str, Any]]:
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

    # Beräkna basfeatures
    ema_vals = calculate_ema(closes[: last_idx + 1], period=12)
    rsi_vals = calculate_rsi(closes[: last_idx + 1], period=14)
    ema_latest = ema_vals[-1] if ema_vals else 0.0
    close_latest = closes[last_idx]
    ema_delta_pct = 0.0 if close_latest == 0 else (ema_latest - close_latest) / close_latest
    rsi_latest = (rsi_vals[-1] - 50.0) / 50.0 if rsi_vals else 0.0  # skala kring 0

    # Klippning p10–p90 via config artefakter
    p_cfg = (cfg.get("features") or {}).get("percentiles") or {}
    ed_lo, ed_hi = p_cfg.get("ema_delta_pct", (-0.05, 0.05))
    rsi_lo, rsi_hi = p_cfg.get("rsi", (-1.0, 1.0))

    def _clip(x: float, lo: float, hi: float) -> float:
        if x != x:  # NaN
            return 0.0
        if x == float("inf"):
            return hi
        if x == float("-inf"):
            return lo
        return max(lo, min(hi, x))

    feats: Dict[str, float] = {
        "ema_delta_pct": _clip(ema_delta_pct, float(ed_lo), float(ed_hi)),
        "rsi": _clip(rsi_latest, float(rsi_lo), float(rsi_hi)),
    }

    meta: Dict[str, Any] = {
        "versions": {
            **((cfg.get("features") or {}).get("versions") or {}),
        },
        "reasons": [],
    }
    return feats, meta
