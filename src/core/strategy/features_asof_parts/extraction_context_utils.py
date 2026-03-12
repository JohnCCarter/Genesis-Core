from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class ExtractionContext:
    total_bars: int
    highs: np.ndarray
    lows: np.ndarray
    closes: np.ndarray
    lookup_idx: int
    window_start_idx: int
    pre: dict[str, Any]
    pre_idx: int
    atr_period: int
    use_precompute: bool
    warn_precompute_missing: bool


def prepare_extraction_context(
    candles: dict[str, list[float]],
    asof_bar: int,
    config: dict[str, Any] | None,
    remap_precomputed_features_fn,
) -> ExtractionContext:
    """Build the internal prep context for `_extract_asof` without owning warning state."""
    highs_arr = np.asarray(candles["high"], dtype=float)
    lows_arr = np.asarray(candles["low"], dtype=float)
    closes_arr = np.asarray(candles["close"], dtype=float)
    highs = highs_arr[: asof_bar + 1]
    lows = lows_arr[: asof_bar + 1]
    closes = closes_arr[: asof_bar + 1]

    assert (
        len(closes) == asof_bar + 1
    ), f"Expected {asof_bar + 1} bars, got {len(closes)}"  # nosec B101

    cfg = config or {}
    lookup_idx = cfg.get("_global_index", asof_bar)
    window_len = len(closes)
    window_start_idx = max(0, lookup_idx - (window_len - 1)) if window_len > 0 else 0

    pre = dict(cfg.get("precomputed_features") or {})
    pre, pre_idx = remap_precomputed_features_fn(pre, window_start_idx, lookup_idx)

    thresholds = cfg.get("thresholds") or {}
    sig_adapt = thresholds.get("signal_adaptation") or {}
    atr_period = int(sig_adapt.get("atr_period", 14))

    use_precompute = os.environ.get("GENESIS_PRECOMPUTE_FEATURES") == "1"
    warn_precompute_missing = use_precompute and not pre
    if warn_precompute_missing:
        use_precompute = False

    return ExtractionContext(
        total_bars=len(candles["close"]),
        highs=highs,
        lows=lows,
        closes=closes,
        lookup_idx=lookup_idx,
        window_start_idx=window_start_idx,
        pre=pre,
        pre_idx=pre_idx,
        atr_period=atr_period,
        use_precompute=use_precompute,
        warn_precompute_missing=warn_precompute_missing,
    )
