"""
Feature extraction with explicit AS-OF semantik.

DESIGN PRINCIPLE:
  All feature computation defined as: "features AS OF asof_bar (inclusive)"

  asof_bar = last closed bar that can be used
  Features computed using bars [0:asof_bar] inclusive

This eliminates all ambiguity between live and backtest modes.
"""

from __future__ import annotations

from collections import OrderedDict
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
from core.utils.logging_redaction import get_logger

_log = get_logger(__name__)

# Cache for feature extraction to avoid recomputing features for same data
# Using OrderedDict for LRU-style eviction (Python 3.7+ maintains insertion order)

_feature_cache: OrderedDict[str, tuple[dict[str, float], dict[str, Any]]] = OrderedDict()
_MAX_CACHE_SIZE = 500  # Increased from 100 to reduce thrashing during backtests


def _compute_candles_hash(candles: dict[str, list[float] | np.ndarray], asof_bar: int) -> str:
    """Compute a fast hash of candles data up to asof_bar for caching.

    Optimization: Use a simpler hash based on bar index and last values only.
    This is much faster than summing 100 bars and gives good cache discrimination.
    Works with both lists and NumPy arrays.
    """
    # For sequential access patterns (like backtesting), asof_bar alone is often sufficient
    # Add last close value for additional discrimination
    close_data = candles.get("close")
    if close_data is not None and len(close_data) > asof_bar:
        # Handle both numpy arrays and lists
        last_close = float(close_data[asof_bar])
        # Use simple string hash instead of cryptographic hash (10x faster)
        return f"{asof_bar}:{last_close:.4f}"
    return str(asof_bar)


def _extract_asof(
    candles: dict[str, list[float]],
    asof_bar: int,
    *,
    timeframe: str | None = None,
    symbol: str | None = None,
    config: dict[str, Any] | None = None,
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
    # Check cache first (optimization: avoid recomputing features for same data)
    cache_key = _compute_candles_hash(candles, asof_bar)
    if cache_key in _feature_cache:
        metrics.inc("feature_cache_hit")
        return _feature_cache[cache_key]

    metrics.inc("feature_cache_miss")

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
        result = (
            {},
            {
                "versions": {},
                "reasons": [
                    f"INSUFFICIENT_DATA: asof_bar={asof_bar} < min_lookback={min_lookback}"
                ],
                "asof_bar": asof_bar,
                "uses_bars": [0, asof_bar],
            },
        )
        # Don't cache error results
        return result

    # Extract data AS OF asof_bar (inclusive) using NumPy views (no copy)
    highs_arr = np.asarray(candles["high"], dtype=float)
    lows_arr = np.asarray(candles["low"], dtype=float)
    closes_arr = np.asarray(candles["close"], dtype=float)
    highs = highs_arr[: asof_bar + 1]
    lows = lows_arr[: asof_bar + 1]
    closes = closes_arr[: asof_bar + 1]

    # Invariant check
    assert (
        len(closes) == asof_bar + 1
    ), f"Expected {asof_bar + 1} bars, got {len(closes)}"  # nosec B101

    # Helper for clipping
    def _clip(x: float, lo: float, hi: float) -> float:
        if x != x:  # NaN
            return 0.0
        return max(lo, min(hi, x))

    # === CALCULATE INDICATORS ===

    # RSI (returns [0, 100]) - use precomputed if available
    pre = dict((config or {}).get("precomputed_features") or {})
    pre_rsi = pre.get("rsi_14")
    if isinstance(pre_rsi, list | tuple) and len(pre_rsi) >= asof_bar + 1:
        rsi_vals = list(pre_rsi[: asof_bar + 1])
    else:
        rsi_vals = calculate_rsi(closes, period=14)

    # Bollinger Bands
    pre_bb_pos = pre.get("bb_position_20_2")
    if isinstance(pre_bb_pos, list | tuple) and len(pre_bb_pos) >= asof_bar + 1:
        bb = {"position": list(pre_bb_pos[: asof_bar + 1])}
    else:
        _cl = closes.tolist() if isinstance(closes, np.ndarray) else closes
        bb = bollinger_bands(_cl, period=20, std_dev=2.0)

    # ATR (use precomputed if available)
    pre = dict((config or {}).get("precomputed_features") or {})
    pre_atr_full = pre.get("atr_14")
    if isinstance(pre_atr_full, list | tuple) and len(pre_atr_full) >= asof_bar + 1:
        atr_vals = list(pre_atr_full[: asof_bar + 1])
    else:
        atr_vals = calculate_atr(highs, lows, closes, period=14)
    pre_atr50_full = pre.get("atr_50")
    if isinstance(pre_atr50_full, list | tuple) and len(pre_atr50_full) >= asof_bar + 1:
        atr_long = list(pre_atr50_full[: asof_bar + 1])
    else:
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
        # Avoid NumPy truth-value ambiguity on array slices
        current_price = closes[-1] if len(closes) > 0 else 0.0
        current_atr = atr_vals[-1] if atr_vals else 1.0

        # Use precomputed swings if available, otherwise detect
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
            # Filter swings AS-OF current bar
            swing_high_indices = [int(i) for i in pre_sw_hi_idx if int(i) <= asof_bar]
            swing_low_indices = [int(i) for i in pre_sw_lo_idx if int(i) <= asof_bar]
            # Align prices by keeping same positions from original arrays that satisfy index<=asof_bar
            swing_high_prices = [
                float(pre_sw_hi_px[idx])
                for idx, si in enumerate(pre_sw_hi_idx)
                if int(si) <= asof_bar
            ]
            swing_low_prices = [
                float(pre_sw_lo_px[idx])
                for idx, si in enumerate(pre_sw_lo_idx)
                if int(si) <= asof_bar
            ]
        else:
            swing_high_indices, swing_low_indices, swing_high_prices, swing_low_prices = (
                detect_swing_points(
                    pd.Series(highs), pd.Series(lows), pd.Series(closes), fib_config
                )
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
        EMA_SLOPE_PARAMS = {
            "30m": {"ema_period": 50, "lookback": 20},
            "1h": {"ema_period": 20, "lookback": 5},
            "3h": {"ema_period": 20, "lookback": 5},
        }
        par = EMA_SLOPE_PARAMS.get(str(timeframe or "").lower(), {"ema_period": 20, "lookback": 5})
        ema_period = par["ema_period"]
        ema_lookback = par["lookback"]
        # EMA (use precomputed if exact period available)
        pre_ema_key = f"ema_{ema_period}"
        pre_ema_full = pre.get(pre_ema_key)
        if isinstance(pre_ema_full, list | tuple) and len(pre_ema_full) >= asof_bar + 1:
            ema_values = list(pre_ema_full[: asof_bar + 1])
        else:
            ema_values = calculate_ema(closes, period=ema_period)
        if len(ema_values) >= ema_lookback + 1:
            ema_slope_raw = (ema_values[-1] - ema_values[-1 - ema_lookback]) / ema_values[
                -1 - ema_lookback
            ]
        else:
            ema_slope_raw = 0.0
        ema_slope = _clip(ema_slope_raw, -0.10, 0.10)

        pre_adx_full = pre.get("adx_14")
        if isinstance(pre_adx_full, list | tuple) and len(pre_adx_full) >= asof_bar + 1:
            adx_values = list(pre_adx_full[: asof_bar + 1])
        else:
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
        try:
            metrics.inc("feature_fib_errors")
        except Exception:
            pass
        if _log:
            _log.warning("fib feature combination failed: %s", exc)

    # === ADD HTF FIBONACCI CONTEXT FOR SYMMETRIC CHAMOUN MODEL ===
    # Only for LTF timeframes that can benefit from HTF structure
    htf_fibonacci_context = {}
    if timeframe in ["1h", "30m", "6h", "15m"]:
        try:
            _candles_for_htf = {
                "high": highs.tolist() if isinstance(highs, np.ndarray) else highs,
                "low": lows.tolist() if isinstance(lows, np.ndarray) else lows,
                "close": closes.tolist() if isinstance(closes, np.ndarray) else closes,
                "timestamp": candles.get("timestamp") if isinstance(candles, dict) else None,
            }
            htf_fibonacci_context = get_htf_fibonacci_context(
                _candles_for_htf, timeframe=timeframe, symbol=symbol or "tBTCUSD"
            )
        except Exception as e:
            # Don't fail feature extraction if HTF context unavailable
            htf_fibonacci_context = {
                "available": False,
                "reason": "HTF_CONTEXT_ERROR",
                "error": str(e),
            }

    # === Same timeframe Fibonacci context for entry/exit logic ===
    ltf_fibonacci_context = {}
    if timeframe in ["1h", "30m", "6h", "15m"]:
        try:
            ltf_fibonacci_context = get_ltf_fibonacci_context(
                {
                    "high": highs.tolist() if isinstance(highs, np.ndarray) else highs,
                    "low": lows.tolist() if isinstance(lows, np.ndarray) else lows,
                    "close": closes.tolist() if isinstance(closes, np.ndarray) else closes,
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

    meta = {
        "versions": {
            "features_v15_highvol_optimized": True,
            "features_v16_fibonacci": True,
            "features_v17_fibonacci_combinations": True,
            "htf_fibonacci_symmetric_chamoun": True,  # NEW: HTF context for symmetric exits
        },
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

    result = (features, meta)

    # Cache the result with LRU eviction (OrderedDict maintains insertion order)
    if len(_feature_cache) >= _MAX_CACHE_SIZE:
        # Evict least recently used entry (first item in OrderedDict)
        _feature_cache.popitem(last=False)
    _feature_cache[cache_key] = result
    # Move to end to mark as recently used (LRU behavior)
    _feature_cache.move_to_end(cache_key)

    return result


def extract_features_live(
    candles: dict[str, list[float]],
    *,
    timeframe: str | None = None,
    symbol: str | None = None,
    config: dict[str, Any] | None = None,
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

    return _extract_asof(candles, asof_bar, timeframe=timeframe, symbol=symbol, config=config)


def extract_features_backtest(
    candles: dict[str, list[float]],
    asof_bar: int,
    *,
    timeframe: str | None = None,
    symbol: str | None = None,
    config: dict[str, Any] | None = None,
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

    return _extract_asof(candles, asof_bar, timeframe=timeframe, symbol=symbol, config=config)


# Backward compatibility wrapper
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

    if now_index is None:
        # LIVE mode
        return extract_features_live(
            candles_dict, timeframe=timeframe, symbol=symbol, config=config
        )
    else:
        # BACKTEST mode with legacy offset
        # Old behavior: now_index=i used bars [0:i-1]
        # New AS-OF: asof_bar=i-1
        asof_bar = now_index - 1

        if asof_bar < 0:
            asof_bar = 0
        if asof_bar >= total_bars:
            asof_bar = total_bars - 1

        return _extract_asof(
            candles_dict, asof_bar, timeframe=timeframe, symbol=symbol, config=config
        )
