"""
Feature extraction with explicit AS-OF semantik.

DESIGN PRINCIPLE:
  All feature computation defined as: "features AS OF asof_bar (inclusive)"

  asof_bar = last closed bar that can be used
  Features computed using bars [0:asof_bar] inclusive

This eliminates all ambiguity between live and backtest modes.
"""

from __future__ import annotations

import os
from collections import OrderedDict
from typing import Any

import numpy as np

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
from core.strategy.features_asof_parts.atr_percentile_utils import (
    build_atr_percentiles as _build_atr_percentiles_impl,
)
from core.strategy.features_asof_parts.cache_utils import (
    indicator_cache_lookup as _indicator_cache_lookup_impl,
)
from core.strategy.features_asof_parts.cache_utils import (
    indicator_cache_store as _indicator_cache_store_impl,
)
from core.strategy.features_asof_parts.extraction_context_utils import (
    prepare_extraction_context as _prepare_extraction_context_impl,
)
from core.strategy.features_asof_parts.fibonacci_context_utils import (
    build_htf_fibonacci_context as _build_htf_fibonacci_context_impl,
)
from core.strategy.features_asof_parts.fibonacci_context_utils import (
    build_ltf_fibonacci_context as _build_ltf_fibonacci_context_impl,
)
from core.strategy.features_asof_parts.fibonacci_feature_utils import (
    build_fibonacci_feature_updates as _build_fibonacci_feature_updates_impl,
)
from core.strategy.features_asof_parts.hash_utils import as_config_dict as _as_config_dict_impl
from core.strategy.features_asof_parts.hash_utils import (
    compute_candles_hash as _compute_candles_hash_impl,
)
from core.strategy.features_asof_parts.hash_utils import (
    safe_series_value as _safe_series_value_impl,
)
from core.strategy.features_asof_parts.logging_utils import (
    log_precompute_status as _log_precompute_status_impl,
)
from core.strategy.features_asof_parts.numeric_utils import (
    clip_feature_value as _clip_feature_value_impl,
)
from core.strategy.features_asof_parts.precompute_utils import (
    remap_precomputed_features as _remap_precomputed_features_impl,
)
from core.strategy.features_asof_parts.result_cache_utils import (
    feature_result_cache_lookup as _feature_result_cache_lookup_impl,
)
from core.strategy.features_asof_parts.result_cache_utils import (
    feature_result_cache_store as _feature_result_cache_store_impl,
)
from core.strategy.fib_logging import log_fib_flow
from core.strategy.htf_selector import select_htf_timeframe
from core.utils.diffing.feature_cache import IndicatorCache, make_indicator_fingerprint
from core.utils.env_flags import env_flag_enabled
from core.utils.logging_redaction import get_logger

_log = get_logger(__name__)

# Performance counters
FAST_HITS = 0
SLOW_HITS = 0


def get_feature_hit_counts() -> tuple[int, int]:
    """Return (fast_hits, slow_hits) and reset counters."""
    global FAST_HITS, SLOW_HITS
    counts = (FAST_HITS, SLOW_HITS)
    FAST_HITS = 0
    SLOW_HITS = 0
    return counts


def _as_config_dict(value: Any) -> dict[str, Any]:
    return _as_config_dict_impl(value, logger=_log)


_feature_cache: OrderedDict[str, tuple[dict[str, float], dict[str, Any]]] = OrderedDict()
# Allow overriding via env; default larger LRU cache for speed
try:
    _MAX_CACHE_SIZE = int(os.environ.get("GENESIS_FEATURE_CACHE_SIZE", "500"))
except Exception:
    _MAX_CACHE_SIZE = 500
_indicator_cache = IndicatorCache(max_size=2048)
_INDICATOR_CACHE_ENABLED = not env_flag_enabled(
    os.getenv("GENESIS_DISABLE_INDICATOR_CACHE"), default=False
)
_PRECOMPUTE_DEBUG_ONCE = False
_PRECOMPUTE_WARN_ONCE = False

_FIB_FEATURE_FALLBACKS: dict[str, float] = {
    "fib_dist_min_atr": 10.0,
    "fib_dist_signed_atr": 0.0,
    "fib_prox_score": 0.0,
    "fib0618_prox_atr": 0.0,
    "fib05_prox_atr": 0.0,
    "swing_retrace_depth": 0.0,
    "fib05_x_ema_slope": 0.0,
    "fib_prox_x_adx": 0.0,
    "fib05_x_rsi_inv": 0.0,
}


def _indicator_cache_lookup(key):
    return _indicator_cache_lookup_impl(_indicator_cache, _INDICATOR_CACHE_ENABLED, key)


def _indicator_cache_store(key, value):
    _indicator_cache_store_impl(_indicator_cache, _INDICATOR_CACHE_ENABLED, key, value)


def _remap_precomputed_features(
    pre: dict[str, Any], window_start_idx: int, lookup_idx: int
) -> tuple[dict[str, Any], int]:
    return _remap_precomputed_features_impl(pre, window_start_idx, lookup_idx)


def _log_precompute_status(
    use_precompute: bool, pre: dict[str, Any], lookup_idx: int, window_start_idx: int
) -> None:
    global _PRECOMPUTE_DEBUG_ONCE
    _PRECOMPUTE_DEBUG_ONCE = _log_precompute_status_impl(
        _PRECOMPUTE_DEBUG_ONCE,
        _log,
        use_precompute,
        pre,
        lookup_idx,
        window_start_idx,
    )


def _safe_series_value(series: list[float] | np.ndarray | None, idx: int) -> float:
    return _safe_series_value_impl(series, idx)


def _compute_candles_hash(candles: dict[str, list[float] | np.ndarray], asof_bar: int) -> str:
    return _compute_candles_hash_impl(candles, asof_bar)


def _clip(x: float, lo: float, hi: float) -> float:
    return _clip_feature_value_impl(x, lo, hi)


def _build_atr_percentiles(
    atr_source: list[float] | np.ndarray | None,
) -> dict[str, dict[str, float]]:
    return _build_atr_percentiles_impl(atr_source)


def _build_ltf_fibonacci_context(
    candles: dict[str, Any],
    highs: list[float] | np.ndarray,
    lows: list[float] | np.ndarray,
    closes: list[float] | np.ndarray,
    timeframe: str | None,
    atr_values: list[float] | np.ndarray | None,
    symbol: str | None,
) -> dict[str, Any]:
    return _build_ltf_fibonacci_context_impl(
        candles,
        highs,
        lows,
        closes,
        timeframe,
        atr_values,
        symbol,
        get_ltf_fibonacci_context,
        log_fib_flow,
        _log,
    )


def _build_htf_fibonacci_context(
    candles: dict[str, Any],
    highs: list[float] | np.ndarray,
    lows: list[float] | np.ndarray,
    closes: list[float] | np.ndarray,
    timeframe: str | None,
    symbol: str | None,
    config: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    return _build_htf_fibonacci_context_impl(
        candles,
        highs,
        lows,
        closes,
        timeframe,
        symbol,
        config,
        _as_config_dict,
        select_htf_timeframe,
        get_htf_fibonacci_context,
        log_fib_flow,
        _log,
    )


def _build_fibonacci_feature_updates(
    highs: list[float] | np.ndarray,
    lows: list[float] | np.ndarray,
    closes: list[float] | np.ndarray,
    atr_values: list[float] | np.ndarray | None,
    pre: dict[str, Any],
    pre_idx: int,
    timeframe: str | None,
    asof_bar: int,
    rsi_current: float,
) -> tuple[dict[str, float], dict[str, Any]]:
    return _build_fibonacci_feature_updates_impl(
        highs,
        lows,
        closes,
        atr_values,
        pre,
        pre_idx,
        timeframe,
        asof_bar,
        rsi_current,
        _FIB_FEATURE_FALLBACKS,
        _clip,
        FibonacciConfig,
        make_indicator_fingerprint,
        _indicator_cache_lookup,
        _indicator_cache_store,
        detect_swing_points,
        calculate_fibonacci_levels,
        calculate_fibonacci_features,
        calculate_ema,
        calculate_adx,
        metrics,
        _log,
    )


def _feature_cache_lookup(cache_key: str):
    return _feature_result_cache_lookup_impl(_feature_cache, cache_key)


def _feature_cache_store(cache_key: str, result: tuple[dict[str, float], dict[str, Any]]) -> None:
    _feature_result_cache_store_impl(_feature_cache, cache_key, result, _MAX_CACHE_SIZE)


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
    cached_value = _feature_cache_lookup(cache_key)
    if cached_value is not None:
        metrics.inc("feature_cache_hit")
        return cached_value

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

    prep = _prepare_extraction_context_impl(
        candles,
        asof_bar,
        config,
        _remap_precomputed_features,
    )
    highs = prep.highs
    lows = prep.lows
    closes = prep.closes
    window_start_idx = prep.window_start_idx
    pre = prep.pre
    pre_idx = prep.pre_idx
    use_precompute = prep.use_precompute
    atr_period = prep.atr_period

    if prep.warn_precompute_missing:
        # Graceful fallback: tillåt slow path men logga en engångsvarning
        global _PRECOMPUTE_WARN_ONCE
        if not _PRECOMPUTE_WARN_ONCE and _log:
            _log.warning(
                "GENESIS_PRECOMPUTE_FEATURES=1 men precomputed_features saknas; "
                "faller tillbaka till slow path."
            )
            _PRECOMPUTE_WARN_ONCE = True

    # === CALCULATE INDICATORS ===

    _log_precompute_status(use_precompute, pre, pre_idx, window_start_idx)

    global FAST_HITS, SLOW_HITS

    pre_rsi = pre.get("rsi_14")
    rsi_vals = None
    rsi_current_raw = 50.0
    rsi_lag1_raw = 50.0

    if isinstance(pre_rsi, list | tuple) and len(pre_rsi) > pre_idx:
        # FAST PATH: Direct access (no copy)
        FAST_HITS += 1
        rsi_current_raw = float(pre_rsi[pre_idx])
        rsi_lag1_raw = float(pre_rsi[pre_idx - 1]) if pre_idx > 0 else rsi_current_raw
    else:
        SLOW_HITS += 1
        key = make_indicator_fingerprint(
            "rsi",
            params={"period": 14},
            series=closes,
        )
        cached_rsi = _indicator_cache_lookup(key)
        if cached_rsi is not None and len(cached_rsi) >= asof_bar + 1:
            rsi_vals = cached_rsi[: asof_bar + 1]
        else:
            rsi_full = calculate_rsi(closes, period=14)
            _indicator_cache_store(key, rsi_full)
            rsi_vals = rsi_full

        if rsi_vals:
            rsi_current_raw = rsi_vals[-1]
            rsi_lag1_raw = rsi_vals[-2] if len(rsi_vals) > 1 else rsi_current_raw

    # Bollinger Bands
    pre_bb_pos = pre.get("bb_position_20_2")
    bb_vals = None
    bb_last_3 = []

    if isinstance(pre_bb_pos, list | tuple) and len(pre_bb_pos) > pre_idx:
        # FAST PATH: Slice only what we need (last 3 bars)
        start_idx = max(0, pre_idx - 2)
        bb_last_3 = list(pre_bb_pos[start_idx : pre_idx + 1])
    else:
        _cl = closes.tolist() if isinstance(closes, np.ndarray) else closes
        bb_key = make_indicator_fingerprint(
            "bollinger",
            params={"period": 20, "std_dev": 2.0},
            series=_cl,
        )
        cached_bb = _indicator_cache_lookup(bb_key)
        if cached_bb is not None and len(cached_bb.get("position", [])) >= asof_bar + 1:
            bb_vals = list(cached_bb["position"][: asof_bar + 1])
        else:
            bb_full = bollinger_bands(_cl, period=20, std_dev=2.0)
            _indicator_cache_store(bb_key, bb_full)
            bb_vals = bb_full["position"]

        if bb_vals:
            bb_last_3 = bb_vals[-3:]

    # ATR (use precomputed if available)

    pre_atr_key = f"atr_{atr_period}"
    pre_atr_full = pre.get(pre_atr_key)

    # Fallback to atr_14 if specific period not found but period is 14 (legacy compat)
    if pre_atr_full is None and atr_period == 14:
        pre_atr_full = pre.get("atr_14")

    atr_vals = None
    atr_window_56 = []

    if isinstance(pre_atr_full, list | tuple) and len(pre_atr_full) > pre_idx:
        # FAST PATH: Slice only what we need for percentiles (last 56 bars)
        start_idx = max(0, pre_idx - 55)
        atr_window_56 = list(pre_atr_full[start_idx : pre_idx + 1])
        # Ensure atr_vals is available for LTF context later
        atr_vals = list(pre_atr_full[: pre_idx + 1])
    else:
        key_atr = make_indicator_fingerprint(
            f"atr_{atr_period}", params={"period": atr_period}, series=closes
        )
        cached_atr = _indicator_cache_lookup(key_atr)
        if cached_atr is not None and len(cached_atr) >= asof_bar + 1:
            atr_vals = cached_atr[: asof_bar + 1]
        else:
            atr_full = calculate_atr(highs, lows, closes, period=atr_period)
            _indicator_cache_store(key_atr, atr_full)
            atr_vals = atr_full

        if atr_vals:
            atr_window_56 = atr_vals[-56:]

    # Always compute true ATR(14) for legacy feature key stability.
    # This prevents semantic drift where features["atr_14"] accidentally becomes ATR(atr_period).
    atr14_vals = None
    atr14_current = None
    if atr_period == 14:
        atr14_vals = atr_vals
        atr14_current = float(atr_vals[-1]) if atr_vals else None
    else:
        pre_atr14_full = pre.get("atr_14")
        if isinstance(pre_atr14_full, list | tuple) and len(pre_atr14_full) > pre_idx:
            atr14_current = float(pre_atr14_full[pre_idx])
            atr14_vals = list(pre_atr14_full[: pre_idx + 1])
        else:
            key_atr14 = make_indicator_fingerprint("atr_14", params={"period": 14}, series=closes)
            cached_atr14 = _indicator_cache_lookup(key_atr14)
            if cached_atr14 is not None and len(cached_atr14) >= asof_bar + 1:
                atr14_vals = cached_atr14[: asof_bar + 1]
            else:
                atr14_full = calculate_atr(highs, lows, closes, period=14)
                _indicator_cache_store(key_atr14, atr14_full)
                atr14_vals = atr14_full
            atr14_current = float(atr14_vals[-1]) if atr14_vals else None

    # ATR Long (needed for Vol Shift if not precomputed)
    pre_atr50_full = pre.get("atr_50")
    atr_long = None
    if not pre.get("volatility_shift"):  # Only needed if vol shift not precomputed
        if isinstance(pre_atr50_full, list | tuple) and len(pre_atr50_full) > pre_idx:
            # We might need full history if calculating vol shift manually?
            # calculate_volatility_shift takes lists.
            # If we are here, we are in slow path for vol shift anyway.
            atr_long = list(pre_atr50_full[: pre_idx + 1])
        else:
            key_atr50 = make_indicator_fingerprint("atr_50", params={"period": 50}, series=closes)
            cached_atr50 = _indicator_cache_lookup(key_atr50)
            if cached_atr50 is not None and len(cached_atr50) >= asof_bar + 1:
                atr_long = cached_atr50[: asof_bar + 1]
            else:
                atr_long_full = calculate_atr(highs, lows, closes, period=50)
                _indicator_cache_store(key_atr50, atr_long_full)
                atr_long = atr_long_full

    # Volatility shift
    pre_vol_shift = pre.get("volatility_shift")
    vol_shift_vals = None
    vol_shift_last_3 = []
    vol_shift_current = 1.0

    if isinstance(pre_vol_shift, list | tuple) and len(pre_vol_shift) > pre_idx:
        # FAST PATH
        start_idx = max(0, pre_idx - 2)
        vol_shift_last_3 = list(pre_vol_shift[start_idx : pre_idx + 1])
        vol_shift_current = float(pre_vol_shift[pre_idx])
    else:
        # SLOW PATH
        # We need atr_vals and atr_long here.
        # If we took fast path for ATR, atr_vals is None.
        # So we must reconstruct atr_vals if we are here.
        if atr_vals is None and isinstance(pre_atr_full, list | tuple):
            atr_vals = list(pre_atr_full[: pre_idx + 1])

        if atr_vals and atr_long:
            vol_key = make_indicator_fingerprint(
                "volatility_shift",
                params={},
                series=[atr_vals, atr_long],
            )
            cached_vol_shift = _indicator_cache_lookup(vol_key)
            if cached_vol_shift is not None and len(cached_vol_shift) >= len(atr_vals):
                vol_shift_vals = cached_vol_shift[: len(atr_vals)]
            else:
                vol_shift_vals = calculate_volatility_shift(atr_vals, atr_long)
                _indicator_cache_store(vol_key, vol_shift_vals)

            if vol_shift_vals:
                vol_shift_last_3 = vol_shift_vals[-3:]
                vol_shift_current = vol_shift_vals[-1]

    # === FEATURE 1: rsi_inv_lag1 ===
    # Use RSI from 1 bar ago (asof_bar - 1)
    rsi_inv_lag1 = (rsi_lag1_raw - 50.0) / 50.0

    # === FEATURE 2: volatility_shift_ma3 ===
    # 3-bar MA of volatility shift
    if len(vol_shift_last_3) > 0:
        vol_shift_ma3 = sum(vol_shift_last_3) / len(vol_shift_last_3)
    else:
        vol_shift_ma3 = 1.0

    # === FEATURE 3: bb_position_inv_ma3 ===
    # 3-bar MA of inverted BB position
    if len(bb_last_3) > 0:
        bb_inv_last_3 = [1.0 - pos for pos in bb_last_3]
        bb_position_inv_ma3 = sum(bb_inv_last_3) / len(bb_inv_last_3)
    else:
        bb_position_inv_ma3 = 0.5

    # === FEATURE 4: rsi_vol_interaction ===
    # Current bar RSI x current bar vol_shift
    rsi_current = (rsi_current_raw - 50.0) / 50.0
    rsi_vol_interaction = rsi_current * _clip(vol_shift_current, 0.5, 2.0)

    # === FEATURE 5: vol_regime ===
    # Binary: HighVol=1, LowVol=0
    vol_regime = 1.0 if vol_shift_current > 1.0 else 0.0

    # === BUILD FEATURES DICT ===
    # Use atr_window_56 if available (fast path), otherwise atr_vals (slow path)
    atr_source = atr_window_56 if atr_window_56 else atr_vals
    atr_percentiles = _build_atr_percentiles(atr_source)

    features = {
        "rsi_inv_lag1": _clip(rsi_inv_lag1, -1.0, 1.0),
        "volatility_shift_ma3": _clip(vol_shift_ma3, 0.5, 2.0),
        "bb_position_inv_ma3": _clip(bb_position_inv_ma3, 0.0, 1.0),
        "rsi_vol_interaction": _clip(rsi_vol_interaction, -2.0, 2.0),
        "vol_regime": vol_regime,
        "atr_14": float(atr14_current) if atr14_current is not None else 0.0,
    }

    # === FIBONACCI FEATURES (levels + distances/proximity) ===
    # Beräkna endast om vi har tillräckligt med data (kräver ATR, swing-detektion)
    fib_feature_status: dict[str, Any] = {
        "available": True,
        "reason": "OK",
    }
    fib_feature_updates, fib_feature_status = _build_fibonacci_feature_updates(
        highs,
        lows,
        closes,
        atr_vals,
        pre,
        pre_idx,
        timeframe,
        asof_bar,
        rsi_current,
    )
    features.update(fib_feature_updates)

    # === ADD HTF FIBONACCI CONTEXT FOR SYMMETRIC CHAMOUN MODEL ===
    # Only for LTF timeframes that can benefit from HTF structure
    htf_fibonacci_context = {}
    htf_selector_meta: dict[str, Any] | None = None
    if timeframe in ["1h", "30m", "6h", "15m"]:
        htf_fibonacci_context, htf_selector_meta = _build_htf_fibonacci_context(
            candles,
            highs,
            lows,
            closes,
            timeframe,
            symbol,
            config,
        )

    # === Same timeframe Fibonacci context for entry/exit logic ===
    ltf_fibonacci_context = {}
    if timeframe in ["1h", "30m", "6h", "15m"]:
        ltf_fibonacci_context = _build_ltf_fibonacci_context(
            candles,
            highs,
            lows,
            closes,
            timeframe,
            atr_vals,
            symbol,
        )

    meta_reasons: list[str] = []
    if not bool(fib_feature_status.get("available", True)):
        meta_reasons.append(str(fib_feature_status.get("reason") or "FIB_FEATURES_CONTEXT_ERROR"))

    meta = {
        "versions": {
            "features_v15_highvol_optimized": True,
            "features_v16_fibonacci": True,
            "features_v17_fibonacci_combinations": True,
            "htf_fibonacci_symmetric_chamoun": True,  # NEW: HTF context for symmetric exits
        },
        "reasons": meta_reasons,
        "feature_count": len(features),
        "asof_bar": asof_bar,
        "uses_bars": [0, asof_bar],
        "total_bars_available": total_bars,
        "fibonacci_features": fib_feature_status,
        "htf_fibonacci": htf_fibonacci_context,  # NEW: HTF context for exit logic
        "ltf_fibonacci": ltf_fibonacci_context,
        # Backcompat: current_atr aligns with features['atr_14'] (true ATR(14))
        "current_atr": float(atr14_current) if atr14_current is not None else None,
        # Transparency: show the ATR used for signal_adaptation (may be != 14)
        "current_atr_used": float(atr_vals[-1]) if atr_vals else None,
        "atr_period_used": atr_period,
        "atr_percentiles": atr_percentiles,
        "htf_selector": htf_selector_meta,
    }

    result = (features, meta)

    # Cache the result (OrderedDict + LRU eviction)
    _feature_cache_store(cache_key, result)

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
        -> asof_bar = 98
        -> Features computed from bars [0-98]
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
        -> Features computed from bars [0-99]
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
