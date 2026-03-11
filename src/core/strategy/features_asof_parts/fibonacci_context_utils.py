from __future__ import annotations

from typing import Any

import numpy as np


def build_ltf_fibonacci_context(
    candles: dict[str, Any],
    highs: list[float] | np.ndarray,
    lows: list[float] | np.ndarray,
    closes: list[float] | np.ndarray,
    timeframe: str | None,
    atr_values: list[float] | np.ndarray | None,
    symbol: str | None,
    get_ltf_fibonacci_context_fn,
    log_fib_flow_fn,
    logger,
) -> dict[str, Any]:
    try:
        ltf_fibonacci_context = get_ltf_fibonacci_context_fn(
            {
                "high": highs.tolist() if isinstance(highs, np.ndarray) else highs,
                "low": lows.tolist() if isinstance(lows, np.ndarray) else lows,
                "close": closes.tolist() if isinstance(closes, np.ndarray) else closes,
                "timestamp": candles.get("timestamp") if isinstance(candles, dict) else None,
            },
            timeframe=timeframe,
            atr_values=atr_values,
        )
        log_fib_flow_fn(
            "[FIB-FLOW] LTF fibonacci context created: symbol=%s timeframe=%s available=%s",
            symbol or "tBTCUSD",
            timeframe,
            ltf_fibonacci_context.get("available", False),
            logger=logger,
        )
        return ltf_fibonacci_context
    except Exception as exc:  # pragma: no cover - defensive orchestration wrapper
        ltf_fibonacci_context = {
            "available": False,
            "reason": "LTF_CONTEXT_ERROR",
        }
        log_fib_flow_fn(
            "[FIB-FLOW] LTF fibonacci context failed: symbol=%s timeframe=%s error=%s",
            symbol or "tBTCUSD",
            timeframe,
            str(exc),
            logger=logger,
        )
        return ltf_fibonacci_context
