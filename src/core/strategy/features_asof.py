"""
Feature extraction with explicit AS-OF semantik.

DESIGN PRINCIPLE:
  All feature computation defined as: "features AS OF asof_bar (inclusive)"

  asof_bar = last closed bar that can be used
  Features computed using bars [0:asof_bar] inclusive

This eliminates all ambiguity between live and backtest modes.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
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
from core.indicators.htf_fibonacci import get_htf_fibonacci_context, get_ltf_fibonacci_context
from core.indicators.rsi import calculate_rsi
from core.observability.metrics import metrics
from core.utils.data_loader import load_features
from core.utils.logging_redaction import get_logger

_log = get_logger(__name__)


_FEATURE_VERSION_MARKERS = {
    "features_v15_highvol_optimized": True,
    "features_v16_fibonacci": True,
    "features_v17_fibonacci_combinations": True,
    "htf_fibonacci_symmetric_chamoun": True,
}

_VECTOR_FEATURE_CACHE: dict[tuple[str, str, str], pd.DataFrame] = {}

_EMA_SLOPE_PARAMS = {
    "30m": {"ema_period": 50, "lookback": 20},
    "1h": {"ema_period": 20, "lookback": 5},
    "3h": {"ema_period": 20, "lookback": 5},
    "6h": {"ema_period": 20, "lookback": 5},
}


def _clip(value: float, lo: float, hi: float) -> float:
    if value != value:  # NaN
        return 0.0
    return max(lo, min(hi, value))


def _compute_fibonacci_contexts(
    candles: dict[str, Any],
    timeframe: str | None,
    symbol: str | None,
    highs: list[float],
    lows: list[float],
    closes: list[float],
) -> tuple[dict[str, Any], dict[str, Any]]:
    htf_fibonacci_context: dict[str, Any] = {}
    ltf_fibonacci_context: dict[str, Any] = {}

    if timeframe in ["1h", "30m", "6h", "15m"]:
        try:
            htf_fibonacci_context = get_htf_fibonacci_context(
                candles, timeframe=timeframe, symbol=symbol or "tBTCUSD"
            )
        except Exception as e:
            htf_fibonacci_context = {
                "available": False,
                "reason": "HTF_CONTEXT_ERROR",
                "error": str(e),
            }

        try:
            ltf_fibonacci_context = get_ltf_fibonacci_context(
                {
                    "high": highs,
                    "low": lows,
                    "close": closes,
                    "timestamp": candles.get("timestamp") if isinstance(candles, dict) else None,
                },
                timeframe=timeframe,
            )
        except Exception as e:  # pragma: no cover - defensive
            ltf_fibonacci_context = {
                "available": False,
                "reason": "LTF_CONTEXT_ERROR",
                "error": str(e),
            }

    return htf_fibonacci_context, ltf_fibonacci_context


def _extract_asof(
    candles: dict[str, list[float]],
    asof_bar: int,
    *,
    timeframe: str | None = None,
    symbol: str | None = None,
) -> tuple[dict[str, float], dict[str, Any]]:
    """
    Core feature extraction AS OF specified bar (inclusive).

    This is the SINGLE SOURCE OF TRUTH for feature calculation.

    Args:
        candles: Dict with OHLCV lists (all same length)
        asof_bar: Last bar index to use (inclusive, 0-indexed)

    Returns:
        (features, meta)

    Invariants:
        - Uses bars [0:asof_bar] inclusive
        - asof_bar >= min_lookback (validated)
        - asof_bar < len(candles) (validated)
        - No lookahead: never uses bars > asof_bar
    """
    # Validate inputs
    lengths = [len(candles[k]) for k in ["open", "high", "low", "close", "volume"]]
    if not all(length == lengths[0] for length in lengths):
        raise ValueError("All OHLCV lists must have same length")

    total_bars = lengths[0]

    # Validate asof_bar
    if asof_bar < 0:
        raise ValueError(f"asof_bar must be >= 0, got {asof_bar}")
    if asof_bar >= total_bars:
        raise ValueError(f"asof_bar={asof_bar} >= total_bars={total_bars}")

    min_lookback = 50  # Need at least 50 bars for EMA/indicators
    if asof_bar < min_lookback:
        return {}, {
            "versions": {},
            "reasons": [f"INSUFFICIENT_DATA: asof_bar={asof_bar} < min_lookback={min_lookback}"],
            "asof_bar": asof_bar,
            "uses_bars": [0, asof_bar],
        }

    # Extract data AS OF asof_bar (inclusive)
    highs = [float(x) for x in candles["high"][: asof_bar + 1]]
    lows = [float(x) for x in candles["low"][: asof_bar + 1]]
    closes = [float(x) for x in candles["close"][: asof_bar + 1]]

    # Invariant check
    assert (
        len(closes) == asof_bar + 1
    ), f"Expected {asof_bar + 1} bars, got {len(closes)}"  # nosec B101

    # === CALCULATE INDICATORS ===

    # RSI (returns [0, 100])
    rsi_vals = calculate_rsi(closes, period=14)

    # Bollinger Bands
    bb = bollinger_bands(closes, period=20, std_dev=2.0)

    # ATR
    atr_vals = calculate_atr(highs, lows, closes, period=14)
    atr_long = calculate_atr(highs, lows, closes, period=50)

    # Volatility shift
    vol_shift = calculate_volatility_shift(atr_vals, atr_long)

    # === FEATURE 1: rsi_inv_lag1 ===
    # Use RSI from 1 bar ago (asof_bar - 1)
    if len(rsi_vals) >= 2:
        rsi_lag1 = rsi_vals[-2]  # Previous bar's RSI
        rsi_inv_lag1 = (rsi_lag1 - 50.0) / 50.0
    else:
        rsi_inv_lag1 = 0.0

    # === FEATURE 2: volatility_shift_ma3 ===
    # 3-bar MA of volatility shift
    if len(vol_shift) >= 3:
        vol_shift_last_3 = vol_shift[-3:]
        vol_shift_ma3 = sum(vol_shift_last_3) / 3.0
    else:
        vol_shift_ma3 = vol_shift[-1] if vol_shift else 1.0

    # === FEATURE 3: bb_position_inv_ma3 ===
    # 3-bar MA of inverted BB position
    if len(bb["position"]) >= 3:
        bb_last_3 = bb["position"][-3:]
        bb_inv_last_3 = [1.0 - pos for pos in bb_last_3]
        bb_position_inv_ma3 = sum(bb_inv_last_3) / 3.0
    else:
        bb_position_inv_ma3 = 1.0 - bb["position"][-1] if bb["position"] else 0.5

    # === FEATURE 4: rsi_vol_interaction ===
    # Current bar RSI × current bar vol_shift
    rsi_current = (rsi_vals[-1] - 50.0) / 50.0 if rsi_vals else 0.0
    vol_shift_current = vol_shift[-1] if vol_shift else 1.0
    rsi_vol_interaction = rsi_current * _clip(vol_shift_current, 0.5, 2.0)

    # === FEATURE 5: vol_regime ===
    # Binary: HighVol=1, LowVol=0
    vol_regime = 1.0 if vol_shift_current > 1.0 else 0.0

    # === BUILD FEATURES DICT ===
    atr_series = pd.Series(atr_vals) if atr_vals else pd.Series(dtype=float)
    atr_percentiles: dict[str, dict[str, float]] = {}
    if not atr_series.empty:
        for period in (14, 28, 56):
            if len(atr_series) >= period:
                window = atr_series.iloc[-period:]
                atr_percentiles[str(period)] = {
                    "p40": float(np.percentile(window, 40)),
                    "p80": float(np.percentile(window, 80)),
                }

    features = {
        "rsi_inv_lag1": _clip(rsi_inv_lag1, -1.0, 1.0),
        "volatility_shift_ma3": _clip(vol_shift_ma3, 0.5, 2.0),
        "bb_position_inv_ma3": _clip(bb_position_inv_ma3, 0.0, 1.0),
        "rsi_vol_interaction": _clip(rsi_vol_interaction, -2.0, 2.0),
        "vol_regime": vol_regime,
        "atr_14": float(atr_vals[-1]) if atr_vals else 0.0,
    }

    # === FIBONACCI FEATURES (levels + distances/proximity) ===
    # Beräkna endast om vi har tillräckligt med data (kräver ATR, swing-detektion)
    try:
        fib_config = FibonacciConfig(atr_depth=3.0, max_swings=8, min_swings=1)
        current_price = closes[-1] if closes else 0.0
        current_atr = atr_vals[-1] if atr_vals else 1.0

        swing_high_indices, swing_low_indices, swing_high_prices, swing_low_prices = (
            detect_swing_points(pd.Series(highs), pd.Series(lows), pd.Series(closes), fib_config)
        )
        fib_levels = calculate_fibonacci_levels(
            swing_high_prices, swing_low_prices, fib_config.levels
        )

        current_swing_high = swing_high_prices[-1] if swing_high_prices else current_price * 1.05
        current_swing_low = swing_low_prices[-1] if swing_low_prices else current_price * 0.95

        fib_feats = calculate_fibonacci_features(
            current_price,
            fib_levels,
            current_atr,
            fib_config,
            current_swing_high,
            current_swing_low,
        )

        # Lägg till fib-features (klampade)
        features.update(
            {
                "fib_dist_min_atr": _clip(fib_feats.get("fib_dist_min_atr", 0.0), 0.0, 10.0),
                "fib_dist_signed_atr": _clip(
                    fib_feats.get("fib_dist_signed_atr", 0.0), -10.0, 10.0
                ),
                "fib_prox_score": _clip(fib_feats.get("fib_prox_score", 0.0), 0.0, 1.0),
                "fib0618_prox_atr": _clip(fib_feats.get("fib0618_prox_atr", 0.0), 0.0, 1.0),
                "fib05_prox_atr": _clip(fib_feats.get("fib05_prox_atr", 0.0), 0.0, 1.0),
                "swing_retrace_depth": _clip(fib_feats.get("swing_retrace_depth", 0.0), 0.0, 1.0),
            }
        )

        # === FIBONACCI-KOMBINATIONER (kontext × signal) ===
        # EMA-slope parametrar per timeframe
        par = _EMA_SLOPE_PARAMS.get(str(timeframe or "").lower(), {"ema_period": 20, "lookback": 5})
        ema_period = par["ema_period"]
        ema_lookback = par["lookback"]
        ema_values = calculate_ema(closes, period=ema_period)
        if len(ema_values) >= ema_lookback + 1:
            ema_slope_raw = (ema_values[-1] - ema_values[-1 - ema_lookback]) / ema_values[
                -1 - ema_lookback
            ]
        else:
            ema_slope_raw = 0.0
        ema_slope = _clip(ema_slope_raw, -0.10, 0.10)

        adx_values = calculate_adx(highs, lows, closes, period=14)
        adx_latest = adx_values[-1] if adx_values else 25.0
        adx_normalized = adx_latest / 100.0

        fib05_x_ema_slope = features.get("fib05_prox_atr", 0.0) * ema_slope
        fib_prox_x_adx = features.get("fib_prox_score", 0.0) * adx_normalized
        # rsi_inv = -rsi_current
        fib05_x_rsi_inv = features.get("fib05_prox_atr", 0.0) * (-rsi_current)

        features.update(
            {
                "fib05_x_ema_slope": _clip(fib05_x_ema_slope, -0.10, 0.10),
                "fib_prox_x_adx": _clip(fib_prox_x_adx, 0.0, 1.0),
                "fib05_x_rsi_inv": _clip(fib05_x_rsi_inv, -1.0, 1.0),
            }
        )
    except Exception as exc:
        # Om något går fel i fib-beräkning, behåll bas-features och fortsätt
        metrics.increment("feature_fib_errors")
        if _log:
            _log.warning("fib feature combination failed: %s", exc)

    htf_fibonacci_context, ltf_fibonacci_context = _compute_fibonacci_contexts(
        candles, timeframe, symbol, highs, lows, closes
    )

    meta = {
        "versions": dict(_FEATURE_VERSION_MARKERS),
        "reasons": [],
        "feature_count": len(features),
        "asof_bar": asof_bar,
        "uses_bars": [0, asof_bar],
        "total_bars_available": total_bars,
        "htf_fibonacci": htf_fibonacci_context,  # NEW: HTF context for exit logic
        "ltf_fibonacci": ltf_fibonacci_context,
        "current_atr": float(atr_vals[-1]) if atr_vals else None,
        "atr_percentiles": atr_percentiles,
    }

    return features, meta


def extract_features_live(
    candles: dict[str, list[float]],
    *,
    timeframe: str | None = None,
    symbol: str | None = None,
) -> tuple[dict[str, float], dict[str, Any]]:
    """
    Extract features for LIVE TRADING.

    Assumes last bar is FORMING (not closed yet).
    Uses second-to-last bar as asof_bar.

    Args:
        candles: OHLCV dict, last bar is forming

    Returns:
        Features AS OF last closed bar

    Example:
        candles has 100 bars [0-99], bar 99 is forming
        → asof_bar = 98
        → Features computed from bars [0-98]
    """
    total_bars = len(candles["close"])

    if total_bars < 2:
        raise ValueError("Need at least 2 bars for live mode")

    # Last closed bar (forming bar is total_bars - 1)
    asof_bar = total_bars - 2

    # Invariant: asof_bar points to last CLOSED bar
    assert asof_bar == total_bars - 2, "Live mode invariant failed"  # nosec B101

    return _extract_asof(candles, asof_bar, timeframe=timeframe, symbol=symbol)


def extract_features_backtest(
    candles: dict[str, list[float]],
    asof_bar: int,
    *,
    timeframe: str | None = None,
    symbol: str | None = None,
) -> tuple[dict[str, float], dict[str, Any]]:
    """
    Extract features for BACKTESTING.

    All bars are CLOSED. Uses specified asof_bar (inclusive).

    Args:
        candles: OHLCV dict, all bars are closed
        asof_bar: Last bar to use (inclusive, 0-indexed)

    Returns:
        Features AS OF asof_bar

    Example:
        candles has 100 bars [0-99], all closed
        asof_bar = 99
        → Features computed from bars [0-99]
    """
    total_bars = len(candles["close"])

    # Validate asof_bar
    if asof_bar < 0:
        raise ValueError(f"asof_bar must be >= 0, got {asof_bar}")
    if asof_bar >= total_bars:
        raise ValueError(f"asof_bar={asof_bar} >= total_bars={total_bars}")

    return _extract_asof(candles, asof_bar, timeframe=timeframe, symbol=symbol)


# Backward compatibility wrapper
def _load_vectorized_dataframe(
    symbol: str,
    timeframe: str,
    vectorized_cfg: dict[str, Any],
) -> pd.DataFrame:
    version = str(vectorized_cfg.get("version", "v17") or "v17")
    custom_path = vectorized_cfg.get("path")

    cache_key = (symbol, timeframe, version if not custom_path else f"custom::{custom_path}")
    cached = _VECTOR_FEATURE_CACHE.get(cache_key)
    if cached is not None:
        return cached

    if custom_path:
        path = Path(custom_path)
        if not path.exists():
            raise FileNotFoundError(f"Vectorized cache not found at {path}")
        if path.suffix.lower() == ".feather":
            df = pd.read_feather(path)
        elif path.suffix.lower() in {".parquet", ".pq"}:
            df = pd.read_parquet(path)
        else:
            raise ValueError(f"Unsupported vectorized cache format: {path.suffix}")
    else:
        df = load_features(symbol, timeframe, version=version)

    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.set_index("timestamp", drop=False)

    _VECTOR_FEATURE_CACHE[cache_key] = df
    return df


def _extract_vectorized(
    candles: dict[str, list[float]],
    asof_bar: int,
    *,
    timeframe: str | None,
    symbol: str | None,
    vectorized_cfg: dict[str, Any],
) -> tuple[dict[str, float], dict[str, Any]]:
    timestamps = candles.get("timestamp")
    if not timestamps or asof_bar >= len(timestamps):
        raise ValueError("timestamp data required for vectorized cache lookup")

    target_ts = pd.Timestamp(timestamps[asof_bar])
    df = _load_vectorized_dataframe(symbol or "tBTCUSD", timeframe or "1h", vectorized_cfg)

    try:
        row = df.loc[target_ts]
    except KeyError as exc:
        raise KeyError(f"Timestamp {target_ts} not found in vectorized cache") from exc

    if isinstance(row, pd.DataFrame):
        row = row.iloc[0]

    feature_cols = [col for col in df.columns if not col.startswith("meta_") and col != "timestamp"]
    features = {col: float(row[col]) for col in feature_cols}

    atr_percentiles: dict[str, dict[str, float]] = {}
    for period in ("14", "28", "56"):
        p40_key = f"meta_atr{period}_p40"
        p80_key = f"meta_atr{period}_p80"
        if p40_key in row.index and p80_key in row.index:
            atr_percentiles[period] = {
                "p40": float(row[p40_key]),
                "p80": float(row[p80_key]),
            }

    highs = [float(x) for x in candles["high"][: asof_bar + 1]]
    lows = [float(x) for x in candles["low"][: asof_bar + 1]]
    closes = [float(x) for x in candles["close"][: asof_bar + 1]]

    atr_vals = calculate_atr(highs, lows, closes, period=14)

    try:
        fib_config = FibonacciConfig(atr_depth=3.0, max_swings=8, min_swings=1)
        current_price = closes[-1] if closes else 0.0
        current_atr = atr_vals[-1] if atr_vals else 1.0

        swing_high_indices, swing_low_indices, swing_high_prices, swing_low_prices = (
            detect_swing_points(pd.Series(highs), pd.Series(lows), pd.Series(closes), fib_config)
        )
        fib_levels = calculate_fibonacci_levels(
            swing_high_prices, swing_low_prices, fib_config.levels
        )

        current_swing_high = swing_high_prices[-1] if swing_high_prices else current_price * 1.05
        current_swing_low = swing_low_prices[-1] if swing_low_prices else current_price * 0.95

        fib_feats = calculate_fibonacci_features(
            current_price,
            fib_levels,
            current_atr,
            fib_config,
            current_swing_high,
            current_swing_low,
        )

        features.update(
            {
                "fib_dist_min_atr": _clip(fib_feats.get("fib_dist_min_atr", 0.0), 0.0, 10.0),
                "fib_dist_signed_atr": _clip(
                    fib_feats.get("fib_dist_signed_atr", 0.0), -10.0, 10.0
                ),
                "fib_prox_score": _clip(fib_feats.get("fib_prox_score", 0.0), 0.0, 1.0),
                "fib0618_prox_atr": _clip(fib_feats.get("fib0618_prox_atr", 0.0), 0.0, 1.0),
                "fib05_prox_atr": _clip(fib_feats.get("fib05_prox_atr", 0.0), 0.0, 1.0),
                "swing_retrace_depth": _clip(fib_feats.get("swing_retrace_depth", 0.0), 0.0, 1.0),
            }
        )

        par = _EMA_SLOPE_PARAMS.get(str(timeframe or "").lower(), {"ema_period": 20, "lookback": 5})
        ema_period = par["ema_period"]
        ema_lookback = par["lookback"]
        ema_values = calculate_ema(closes, period=ema_period)
        if len(ema_values) >= ema_lookback + 1:
            ema_slope_raw = (ema_values[-1] - ema_values[-1 - ema_lookback]) / ema_values[
                -1 - ema_lookback
            ]
        else:
            ema_slope_raw = 0.0
        ema_slope = _clip(ema_slope_raw, -0.10, 0.10)

        adx_values = calculate_adx(highs, lows, closes, period=14)
        adx_latest = adx_values[-1] if adx_values else 25.0
        adx_normalized = adx_latest / 100.0

        rsi_vals = calculate_rsi(closes, period=14)
        rsi_current = (rsi_vals[-1] - 50.0) / 50.0 if rsi_vals else 0.0

        fib05_x_ema_slope = features.get("fib05_prox_atr", 0.0) * ema_slope
        fib_prox_x_adx = features.get("fib_prox_score", 0.0) * adx_normalized
        fib05_x_rsi_inv = features.get("fib05_prox_atr", 0.0) * (-rsi_current)

        features.update(
            {
                "fib05_x_ema_slope": _clip(fib05_x_ema_slope, -0.10, 0.10),
                "fib_prox_x_adx": _clip(fib_prox_x_adx, 0.0, 1.0),
                "fib05_x_rsi_inv": _clip(fib05_x_rsi_inv, -1.0, 1.0),
            }
        )
    except Exception as exc:
        metrics.increment("feature_fib_errors")
        if _log:
            _log.warning("vectorized fib feature combination failed: %s", exc)

    htf_fibonacci_context, ltf_fibonacci_context = _compute_fibonacci_contexts(
        candles, timeframe, symbol, highs, lows, closes
    )

    total_bars = len(candles["close"])

    meta = {
        "versions": dict(_FEATURE_VERSION_MARKERS),
        "reasons": [],
        "feature_count": len(features),
        "asof_bar": asof_bar,
        "uses_bars": [0, asof_bar],
        "total_bars_available": total_bars,
        "htf_fibonacci": htf_fibonacci_context,
        "ltf_fibonacci": ltf_fibonacci_context,
        "current_atr": float(atr_vals[-1]) if atr_vals else float(row.get("meta_current_atr", 0.0)),
        "atr_percentiles": atr_percentiles,
    }

    return features, meta


def extract_features(
    candles: dict[str, list[float]] | list[tuple],
    *,
    config: dict[str, Any] | None = None,
    now_index: int | None = None,
    timeframe: str | None = None,
    symbol: str | None = None,
) -> tuple[dict[str, float], dict[str, Any]]:
    """
    DEPRECATED: Use extract_features_live() or extract_features_backtest() instead!

    This wrapper maintains backward compatibility but maps to new AS-OF semantik:
    - If now_index is None: LIVE mode (uses len-2)
    - If now_index is set: BACKTEST mode (uses now_index-1 for compatibility)

    WARNING: This has confusing semantik! Prefer explicit functions.
    """
    # Normalize to dict
    if isinstance(candles, dict):
        candles_dict = candles
    else:
        # Convert list of tuples
        candles_dict = {
            "open": [t[1] for t in candles],
            "high": [t[2] for t in candles],
            "low": [t[3] for t in candles],
            "close": [t[4] for t in candles],
            "volume": [t[5] for t in candles],
        }

    total_bars = len(candles_dict["close"])

    vectorized_cfg = (config or {}).get("vectorized", {})
    use_vectorized = bool(vectorized_cfg.get("use_cache"))

    if now_index is None:
        if total_bars < 2:
            raise ValueError("Need at least 2 bars for live mode")
        asof_bar = total_bars - 2
    else:
        asof_bar = now_index - 1
        if asof_bar < 0:
            asof_bar = 0
        if asof_bar >= total_bars:
            asof_bar = total_bars - 1

    if use_vectorized:
        try:
            features, meta = _extract_vectorized(
                candles_dict,
                asof_bar,
                timeframe=timeframe,
                symbol=symbol,
                vectorized_cfg=vectorized_cfg,
            )
            metrics.event(
                "features_vectorized_cache_hit", {"timeframe": timeframe, "symbol": symbol}
            )
            return features, meta
        except Exception as exc:
            metrics.increment("features_vectorized_cache_fallback")
            if _log:
                _log.warning("vectorized cache fallback: %s", exc)

    return _extract_asof(candles_dict, asof_bar, timeframe=timeframe, symbol=symbol)
