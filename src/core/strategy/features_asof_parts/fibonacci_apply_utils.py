from __future__ import annotations

from typing import Any

import numpy as np


def apply_fibonacci_feature_updates(
    features: dict[str, float],
    highs: list[float] | np.ndarray,
    lows: list[float] | np.ndarray,
    closes: list[float] | np.ndarray,
    atr_vals: list[float] | np.ndarray | None,
    pre: dict[str, Any],
    pre_idx: int,
    timeframe: str | None,
    asof_bar: int,
    rsi_current: float,
    build_fibonacci_updates_fn,
) -> tuple[dict[str, float], dict[str, Any]]:
    fib_feature_status: dict[str, Any] = {
        "available": True,
        "reason": "OK",
    }
    fib_feature_updates, fib_feature_status = build_fibonacci_updates_fn(
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
    return features, fib_feature_status
