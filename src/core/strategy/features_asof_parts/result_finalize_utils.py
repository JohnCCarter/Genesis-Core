from __future__ import annotations

from typing import Any

import numpy as np

CacheResult = tuple[dict[str, float], dict[str, Any]]


def finalize_feature_result(
    features: dict[str, float],
    fib_feature_status: dict[str, Any],
    htf_fibonacci_context: dict[str, Any],
    ltf_fibonacci_context: dict[str, Any],
    htf_selector_meta: dict[str, Any] | None,
    asof_bar: int,
    total_bars: int,
    atr14_current: float | None,
    atr_vals: list[float] | np.ndarray | None,
    atr_period: int,
    atr_percentiles: dict[str, dict[str, float]],
    cache_key: str,
    build_meta_fn,
    cache_store_fn,
) -> CacheResult:
    meta = build_meta_fn(
        features,
        fib_feature_status,
        htf_fibonacci_context,
        ltf_fibonacci_context,
        htf_selector_meta,
        asof_bar,
        total_bars,
        atr14_current,
        atr_vals,
        atr_period,
        atr_percentiles,
    )
    result = (features, meta)
    cache_store_fn(cache_key, result)
    return result
