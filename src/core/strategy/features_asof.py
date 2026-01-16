"""
Feature extraction with explicit AS-OF semantik.

DESIGN PRINCIPLE:
  All feature computation defined as: "features AS OF asof_bar (inclusive)"

  asof_bar = last closed bar that can be used
  Features computed using bars [0:asof_bar] inclusive

This eliminates all ambiguity between live and backtest modes.
"""

from __future__ import annotations

import hashlib
import os
from bisect import bisect_right
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
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        try:
            return value.model_dump()  # type: ignore[return-value]
        except Exception:
            return {}
    return {}


_feature_cache: OrderedDict[str, tuple[dict[str, float], dict[str, Any]]] = OrderedDict()
# Allow overriding via env; default larger LRU cache for speed
try:
    _MAX_CACHE_SIZE = int(os.environ.get("GENESIS_FEATURE_CACHE_SIZE", "500"))
except Exception:
    _MAX_CACHE_SIZE = 500
_indicator_cache = IndicatorCache(max_size=2048)
_INDICATOR_CACHE_ENABLED = not env_flag_enabled(os.getenv("GENESIS_DISABLE_INDICATOR_CACHE"), default=False)
_PRECOMPUTE_DEBUG_ONCE = False
_PRECOMPUTE_WARN_ONCE = False


def _indicator_cache_lookup(key):
    if not _INDICATOR_CACHE_ENABLED:
        return None
    return _indicator_cache.lookup(key)


def _indicator_cache_store(key, value):
    if _INDICATOR_CACHE_ENABLED:
        _indicator_cache.store(key, value)


def _remap_precomputed_features(
    pre: dict[str, Any], window_start_idx: int, lookup_idx: int
) -> tuple[dict[str, Any], int]:
    """Remappa precompute till lokalt fönster när backtestet startar mitt i historiken.

    Returnerar (remappad_pre, remappat_lookup_idx). Vid fel återgår vi till tom pre
    och behåller original-index så att slow path tar över.
    """
    if not pre or window_start_idx <= 0:
        return pre, lookup_idx

    try:
        local_lookup_idx = lookup_idx - window_start_idx
        if local_lookup_idx < 0:
            return {}, lookup_idx

        remapped: dict[str, Any] = {}
        # Standardserier: klipp bort prefixet före window_start_idx
        for key, val in pre.items():
            if isinstance(val, list | tuple):
                if len(val) <= window_start_idx:
                    continue
                remapped[key] = list(val[window_start_idx:])
            else:
                remapped[key] = val

        # Remappa fib-svängar (behåll endast de som finns inom fönstret och offset:a index)
        def _remap_swings(idx_key: str, px_key: str) -> None:
            idxs = pre.get(idx_key)
            pxs = pre.get(px_key)
            if not (isinstance(idxs, list | tuple) and isinstance(pxs, list | tuple)):
                return
            new_idx: list[int] = []
            new_px: list[float] = []
            for i, p in zip(idxs, pxs, strict=False):
                try:
                    if i < window_start_idx:
                        continue
                    new_idx.append(int(i - window_start_idx))
                    new_px.append(float(p))
                except (TypeError, ValueError):
                    continue
            if new_idx and len(new_idx) == len(new_px):
                remapped[idx_key] = new_idx
                remapped[px_key] = new_px

        _remap_swings("fib_high_idx", "fib_high_px")
        _remap_swings("fib_low_idx", "fib_low_px")

        return remapped, local_lookup_idx
    except Exception:
        return {}, lookup_idx


def _log_precompute_status(
    use_precompute: bool, pre: dict[str, Any], lookup_idx: int, window_start_idx: int
) -> None:
    """Loggar en engångsrad som visar om precompute-data är laddad."""
    global _PRECOMPUTE_DEBUG_ONCE
    if _PRECOMPUTE_DEBUG_ONCE or not _log:
        return
    _PRECOMPUTE_DEBUG_ONCE = True
    try:
        keys_sample = sorted(pre.keys())[:10]
    except Exception:
        keys_sample = []
    _log.debug(
        "precompute_status use_precompute=%s lookup_idx=%s window_start_idx=%s pre_keys=%s",
        use_precompute,
        lookup_idx,
        window_start_idx,
        keys_sample,
    )


def _compute_candles_hash(candles: dict[str, list[float] | np.ndarray], asof_bar: int) -> str:
    """Compute a cache key for candles up to asof_bar.

    Fast path (opt-in): GENESIS_FAST_HASH=1 -> simple f-string on asof_bar:last_close
    Default: compact digest summarized over last up to 100 bars, hashed by SHA256.
    """
    # Optional ultra-fast key for tight loops
    if str(os.environ.get("GENESIS_FAST_HASH", "")).strip().lower() in {"1", "true"}:
        try:
            last_close = float(candles["close"][asof_bar])
        except Exception:
            last_close = 0.0
        return f"{asof_bar}:{last_close:.4f}"

    # Default compact SHA256 key
    # Optimization: Use Python's built-in hash() for speed instead of SHA256
    # We include asof_bar, last close, and a few sample points to ensure uniqueness
    # without summing the entire array.
    try:
        close = candles.get("close")
        high = candles.get("high")
        low = candles.get("low")

        def _safe_value(series: list[float] | np.ndarray | None, idx: int) -> float:
            if series is None or idx < 0:
                return 0.0
            try:
                if len(series) <= idx:
                    return 0.0
                return float(series[idx])
            except Exception:
                return 0.0

        # Sample points: current, -1, -10, -50
        c_now = _safe_value(close, asof_bar)
        c_prev = _safe_value(close, asof_bar - 1)
        h_now = _safe_value(high, asof_bar)
        l_now = _safe_value(low, asof_bar)

        # Create a tuple representing the state
        state = (asof_bar, c_now, c_prev, h_now, l_now)
        return str(hash(state))
    except Exception:
        # Fallback to robust string construction if something fails
        data_str = f"{asof_bar}"
        for key in ["open", "high", "low", "close", "volume"]:
            if key in candles:
                start_idx = max(0, asof_bar - 99)
                data = candles[key][start_idx : asof_bar + 1]
                length = len(data)
                data_sum = float(np.sum(data)) if length else 0.0
                last_val = float(data[-1]) if length else 0.0
                data_str += f"|{key}:{length}:{data_sum:.2f}:{last_val:.2f}"
        return hashlib.sha256(data_str.encode()).hexdigest()


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
        value = _feature_cache[cache_key]
        try:
            _feature_cache.move_to_end(cache_key)  # LRU
        except Exception:  # nosec B110
            pass  # Cache error non-critical
        return value

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

    # Determine lookup index for precomputed features
    # If _global_index is provided in config (from backtest engine), use it.
    # Otherwise fallback to asof_bar (assuming full history or relative index).
    lookup_idx = (config or {}).get("_global_index", asof_bar)
    window_len = len(closes)
    window_start_idx = max(0, lookup_idx - (window_len - 1)) if window_len > 0 else 0

    # RSI (returns [0, 100]) - use precomputed if available
    pre = dict((config or {}).get("precomputed_features") or {})
    pre, lookup_idx_local = _remap_precomputed_features(pre, window_start_idx, lookup_idx)
    pre_idx = lookup_idx_local

    # Enforce precompute if requested via env var
    use_precompute = os.environ.get("GENESIS_PRECOMPUTE_FEATURES") == "1"
    if use_precompute and not pre:
        # Graceful fallback: tillåt slow path men logga en engångsvarning
        global _PRECOMPUTE_WARN_ONCE
        if not _PRECOMPUTE_WARN_ONCE and _log:
            _log.warning(
                "GENESIS_PRECOMPUTE_FEATURES=1 men precomputed_features saknas; "
                "faller tillbaka till slow path."
            )
            _PRECOMPUTE_WARN_ONCE = True
        use_precompute = False
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

    # Determine ATR period used by signal_adaptation (default 14)
    thresholds = (config or {}).get("thresholds") or {}
    sig_adapt = thresholds.get("signal_adaptation") or {}
    atr_period = int(sig_adapt.get("atr_period", 14))

    pre_atr_key = f"atr_{atr_period}"
    pre_atr_full = pre.get(pre_atr_key)

    # Fallback to atr_14 if specific period not found but period is 14 (legacy compat)
    if pre_atr_full is None and atr_period == 14:
        pre_atr_full = pre.get("atr_14")

    atr_vals = None
    atr_window_56 = []
    current_atr = 1.0

    if isinstance(pre_atr_full, list | tuple) and len(pre_atr_full) > pre_idx:
        # FAST PATH: Slice only what we need for percentiles (last 56 bars)
        start_idx = max(0, pre_idx - 55)
        atr_window_56 = list(pre_atr_full[start_idx : pre_idx + 1])
        current_atr = float(pre_atr_full[pre_idx])
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
            current_atr = atr_vals[-1]

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
    atr_percentiles: dict[str, dict[str, float]] = {}

    # Use atr_window_56 if available (fast path), otherwise atr_vals (slow path)
    atr_source = atr_window_56 if atr_window_56 else atr_vals

    if atr_source:
        atr_arr = np.asarray(atr_source, dtype=float)
        n_atr = atr_arr.size
        for period in (14, 28, 56):
            if n_atr >= period:
                window = atr_arr[-period:]
                # Performance: compute both percentiles in one call (2x faster)
                p40, p80 = np.percentile(window, [40, 80])
                atr_percentiles[str(period)] = {
                    "p40": float(p40),
                    "p80": float(p80),
                }
            else:
                # Fallback for insufficient data
                atr_percentiles[str(period)] = {"p40": 1.0, "p80": 1.0}
    else:
        # No ATR data
        for period in (14, 28, 56):
            atr_percentiles[str(period)] = {"p40": 1.0, "p80": 1.0}

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
            # Filter swings AS-OF current bar using bisect (O(log N))
            # pre_sw_hi_idx is sorted, so we can find the cut-off point quickly
            hi_cut = bisect_right(pre_sw_hi_idx, pre_idx)
            lo_cut = bisect_right(pre_sw_lo_idx, pre_idx)

            swing_high_indices = [int(i) for i in pre_sw_hi_idx[:hi_cut]]
            swing_low_indices = [int(i) for i in pre_sw_lo_idx[:lo_cut]]
            swing_high_prices = [float(p) for p in pre_sw_hi_px[:hi_cut]]
            swing_low_prices = [float(p) for p in pre_sw_lo_px[:lo_cut]]
        else:
            swing_key = make_indicator_fingerprint(
                "fib_swings",
                params={
                    "atr_depth": fib_config.atr_depth,
                    "max_swings": fib_config.max_swings,
                    "min_swings": fib_config.min_swings,
                },
                series=[highs, lows, closes],
            )
            cached_swings = _indicator_cache_lookup(swing_key)
            if cached_swings:
                swing_high_indices = cached_swings.get("swing_high_indices", [])
                swing_low_indices = cached_swings.get("swing_low_indices", [])
                swing_high_prices = cached_swings.get("swing_high_prices", [])
                swing_low_prices = cached_swings.get("swing_low_prices", [])
            else:
                swing_high_indices, swing_low_indices, swing_high_prices, swing_low_prices = (
                    detect_swing_points(
                        highs,
                        lows,
                        closes,
                        fib_config,
                        atr_values=atr_vals,
                    )
                )
                _indicator_cache_store(
                    swing_key,
                    {
                        "swing_high_indices": swing_high_indices,
                        "swing_low_indices": swing_low_indices,
                        "swing_high_prices": swing_high_prices,
                        "swing_low_prices": swing_low_prices,
                    },
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

        # === FIBONACCI-KOMBINATIONER (kontext x signal) ===
        # EMA-slope parametrar per timeframe
        pre_ema_slope = pre.get("ema_slope")
        if isinstance(pre_ema_slope, list | tuple) and len(pre_ema_slope) > pre_idx:
            ema_slope_raw = float(pre_ema_slope[pre_idx])
        else:
            EMA_SLOPE_PARAMS = {
                "30m": {"ema_period": 50, "lookback": 20},
                "1h": {"ema_period": 20, "lookback": 5},
                "3h": {"ema_period": 20, "lookback": 5},
            }
            par = EMA_SLOPE_PARAMS.get(
                str(timeframe or "").lower(), {"ema_period": 20, "lookback": 5}
            )
            ema_period = par["ema_period"]
            ema_lookback = par["lookback"]
            # EMA (use precomputed if exact period available)
            pre_ema_key = f"ema_{ema_period}"
            pre_ema_full = pre.get(pre_ema_key)
            if isinstance(pre_ema_full, list | tuple) and len(pre_ema_full) >= asof_bar + 1:
                ema_values = list(pre_ema_full[: asof_bar + 1])
            else:
                ema_key = make_indicator_fingerprint(
                    "ema",
                    params={"period": ema_period},
                    series=closes,
                )
                cached_ema = _indicator_cache_lookup(ema_key)
                if cached_ema is not None and len(cached_ema) >= asof_bar + 1:
                    ema_values = cached_ema[: asof_bar + 1]
                else:
                    ema_full = calculate_ema(closes, period=ema_period)
                    _indicator_cache_store(ema_key, ema_full)
                    ema_values = ema_full
            if len(ema_values) >= ema_lookback + 1:
                ema_slope_raw = (ema_values[-1] - ema_values[-1 - ema_lookback]) / ema_values[
                    -1 - ema_lookback
                ]
            else:
                ema_slope_raw = 0.0
        ema_slope = _clip(ema_slope_raw, -0.10, 0.10)

        pre_adx_full = pre.get("adx_14")
        if isinstance(pre_adx_full, list | tuple) and len(pre_adx_full) > pre_idx:
            adx_values = list(pre_adx_full[: pre_idx + 1])
            adx_latest = float(pre_adx_full[pre_idx])
        else:
            adx_key = make_indicator_fingerprint(
                "adx",
                params={"period": 14},
                series=list(zip(highs, lows, closes, strict=False)),
            )
            cached_adx = _indicator_cache_lookup(adx_key)
            if cached_adx is not None and len(cached_adx) >= asof_bar + 1:
                adx_values = cached_adx[: asof_bar + 1]
            else:
                adx_full = calculate_adx(highs, lows, closes, period=14)
                _indicator_cache_store(adx_key, adx_full)
                adx_values = adx_full
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
        except Exception:  # nosec B110
            pass  # Metrics error non-critical
        if _log:
            _log.warning("fib feature combination failed: %s", exc)

    # === ADD HTF FIBONACCI CONTEXT FOR SYMMETRIC CHAMOUN MODEL ===
    # Only for LTF timeframes that can benefit from HTF structure
    htf_fibonacci_context = {}
    htf_selector_meta: dict[str, Any] | None = None
    if timeframe in ["1h", "30m", "6h", "15m"]:
        try:
            _candles_for_htf = {
                "high": highs.tolist() if isinstance(highs, np.ndarray) else highs,
                "low": lows.tolist() if isinstance(lows, np.ndarray) else lows,
                "close": closes.tolist() if isinstance(closes, np.ndarray) else closes,
                "timestamp": candles.get("timestamp") if isinstance(candles, dict) else None,
            }
            mtf_cfg_value = None
            if hasattr(config, "multi_timeframe"):
                mtf_cfg_value = config.multi_timeframe
            elif isinstance(config, dict):
                mtf_cfg_value = (config or {}).get("multi_timeframe")
            multi_timeframe_cfg = _as_config_dict(mtf_cfg_value)
            selector_cfg = multi_timeframe_cfg.get("htf_selector")
            if not selector_cfg and multi_timeframe_cfg.get("htf_timeframe"):
                selector_cfg = {
                    "mode": "fixed",
                    "per_timeframe": multi_timeframe_cfg.get("htf_timeframe", {}),
                }
            htf_timeframe, htf_selector_meta = select_htf_timeframe(timeframe or "", selector_cfg)
            htf_fibonacci_context = get_htf_fibonacci_context(
                _candles_for_htf,
                timeframe=timeframe,
                symbol=symbol or "tBTCUSD",
                htf_timeframe=htf_timeframe,
            )
            if htf_selector_meta:
                htf_fibonacci_context["selector"] = htf_selector_meta
            log_fib_flow(
                "[FIB-FLOW] HTF fibonacci context created: symbol=%s timeframe=%s htf_tf=%s available=%s",
                symbol or "tBTCUSD",
                timeframe,
                htf_timeframe,
                htf_fibonacci_context.get("available", False),
                logger=_log,
            )
        except Exception as e:
            # Don't fail feature extraction if HTF context unavailable
            htf_fibonacci_context = {
                "available": False,
                "reason": "HTF_CONTEXT_ERROR",
            }
            log_fib_flow(
                "[FIB-FLOW] HTF fibonacci context failed: symbol=%s timeframe=%s error=%s",
                symbol or "tBTCUSD",
                timeframe,
                str(e),
                logger=_log,
            )

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
                atr_values=atr_vals,
            )
            log_fib_flow(
                "[FIB-FLOW] LTF fibonacci context created: symbol=%s timeframe=%s available=%s",
                symbol or "tBTCUSD",
                timeframe,
                ltf_fibonacci_context.get("available", False),
                logger=_log,
            )
        except Exception as e:  # pragma: no cover - defensive
            ltf_fibonacci_context = {
                "available": False,
                "reason": "LTF_CONTEXT_ERROR",
            }
            log_fib_flow(
                "[FIB-FLOW] LTF fibonacci context failed: symbol=%s timeframe=%s error=%s",
                symbol or "tBTCUSD",
                timeframe,
                str(e),
                logger=_log,
            )

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
        # Backcompat: current_atr aligns with features['atr_14'] (true ATR(14))
        "current_atr": float(atr14_current) if atr14_current is not None else None,
        # Transparency: show the ATR used for signal_adaptation (may be != 14)
        "current_atr_used": float(atr_vals[-1]) if atr_vals else None,
        "atr_period_used": atr_period,
        "atr_percentiles": atr_percentiles,
        "htf_selector": htf_selector_meta,
    }

    result = (features, meta)

    # Cache the result with LRU eviction (OrderedDict maintains insertion order)
    if len(_feature_cache) >= _MAX_CACHE_SIZE:
        # Evict least recently used entry (first item in OrderedDict)
        _feature_cache.popitem(last=False)
    _feature_cache[cache_key] = result
    # Move to end to mark as recently used (LRU behavior)
    _feature_cache.move_to_end(cache_key)
    # Cache the result (with size limit to prevent memory issues)
    _feature_cache[cache_key] = result
    # Enforce LRU size
    try:
        while len(_feature_cache) > _MAX_CACHE_SIZE:
            _feature_cache.popitem(last=False)
    except Exception:
        # Fallback: simple FIFO eviction if OrderedDict semantics unavailable
        if len(_feature_cache) > _MAX_CACHE_SIZE:
            _feature_cache.pop(next(iter(_feature_cache)))

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
