from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

_ELIGIBLE_TIMEFRAMES = {"1h", "30m", "6h", "15m"}


@dataclass(frozen=True)
class FibonacciContextBundle:
    htf_fibonacci_context: dict[str, Any]
    htf_selector_meta: dict[str, Any] | None
    ltf_fibonacci_context: dict[str, Any]


def build_fibonacci_context_bundle(
    candles: dict[str, Any],
    highs: list[float] | np.ndarray,
    lows: list[float] | np.ndarray,
    closes: list[float] | np.ndarray,
    timeframe: str | None,
    symbol: str | None,
    config: dict[str, Any] | None,
    atr_vals: list[float] | np.ndarray | None,
    build_htf_context_fn,
    build_ltf_context_fn,
) -> FibonacciContextBundle:
    htf_fibonacci_context: dict[str, Any] = {}
    htf_selector_meta: dict[str, Any] | None = None
    ltf_fibonacci_context: dict[str, Any] = {}

    if timeframe in _ELIGIBLE_TIMEFRAMES:
        htf_fibonacci_context, htf_selector_meta = build_htf_context_fn(
            candles,
            highs,
            lows,
            closes,
            timeframe,
            symbol,
            config,
        )
        ltf_fibonacci_context = build_ltf_context_fn(
            candles,
            highs,
            lows,
            closes,
            timeframe,
            atr_vals,
            symbol,
        )

    return FibonacciContextBundle(
        htf_fibonacci_context=htf_fibonacci_context,
        htf_selector_meta=htf_selector_meta,
        ltf_fibonacci_context=ltf_fibonacci_context,
    )
