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
from core.strategy.features_asof_parts.base_feature_utils import (
    build_base_feature_bundle as _build_base_feature_bundle_impl,
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
from core.strategy.features_asof_parts.indicator_state_utils import (
    build_indicator_state as _build_indicator_state_impl,
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
    indicator_state = _build_indicator_state_impl(
        highs,
        lows,
        closes,
        asof_bar,
        pre,
        pre_idx,
        atr_period,
        make_indicator_fingerprint,
        _indicator_cache_lookup,
        _indicator_cache_store,
        calculate_rsi,
        bollinger_bands,
        calculate_atr,
        calculate_volatility_shift,
    )
    if indicator_state.rsi_used_fast_path:
        FAST_HITS += 1
    else:
        SLOW_HITS += 1

    rsi_current_raw = indicator_state.rsi_current_raw
    rsi_lag1_raw = indicator_state.rsi_lag1_raw
    bb_last_3 = indicator_state.bb_last_3
    atr_vals = indicator_state.atr_vals
    atr_window_56 = indicator_state.atr_window_56
    atr14_current = indicator_state.atr14_current
    vol_shift_last_3 = indicator_state.vol_shift_last_3
    vol_shift_current = indicator_state.vol_shift_current
    base_feature_bundle = _build_base_feature_bundle_impl(
        rsi_current_raw,
        rsi_lag1_raw,
        bb_last_3,
        vol_shift_last_3,
        vol_shift_current,
        atr_window_56,
        atr_vals,
        atr14_current,
        _clip,
        _build_atr_percentiles,
    )
    features = dict(base_feature_bundle.features)
    rsi_current = base_feature_bundle.rsi_current
    atr_percentiles = base_feature_bundle.atr_percentiles

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
