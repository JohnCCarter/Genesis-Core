from __future__ import annotations

from typing import Any

import numpy as np


def build_htf_fibonacci_context(
    candles: dict[str, Any],
    highs: list[float] | np.ndarray,
    lows: list[float] | np.ndarray,
    closes: list[float] | np.ndarray,
    timeframe: str | None,
    symbol: str | None,
    config: Any,
    as_config_dict_fn,
    select_htf_timeframe_fn,
    get_htf_fibonacci_context_fn,
    log_fib_flow_fn,
    logger,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    htf_selector_meta: dict[str, Any] | None = None
    try:
        config_dict = as_config_dict_fn(config)
        candles_for_htf = {
            "high": highs.tolist() if isinstance(highs, np.ndarray) else highs,
            "low": lows.tolist() if isinstance(lows, np.ndarray) else lows,
            "close": closes.tolist() if isinstance(closes, np.ndarray) else closes,
            "timestamp": candles.get("timestamp") if isinstance(candles, dict) else None,
        }
        mtf_cfg_value = None
        if hasattr(config, "multi_timeframe"):
            mtf_cfg_value = config.multi_timeframe
        else:
            mtf_cfg_value = config_dict.get("multi_timeframe")
        multi_timeframe_cfg = as_config_dict_fn(mtf_cfg_value)
        selector_cfg = multi_timeframe_cfg.get("htf_selector")
        if not selector_cfg and multi_timeframe_cfg.get("htf_timeframe"):
            selector_cfg = {
                "mode": "fixed",
                "per_timeframe": multi_timeframe_cfg.get("htf_timeframe", {}),
            }
        htf_timeframe, htf_selector_meta = select_htf_timeframe_fn(timeframe or "", selector_cfg)
        htf_context_kwargs: dict[str, Any] = {}
        data_source_policy = config_dict.get("data_source_policy")
        if data_source_policy is not None:
            htf_context_kwargs["data_source_policy"] = data_source_policy
        htf_fibonacci_context = get_htf_fibonacci_context_fn(
            candles_for_htf,
            timeframe=timeframe,
            symbol=symbol or "tBTCUSD",
            htf_timeframe=htf_timeframe,
            **htf_context_kwargs,
        )
        if htf_selector_meta:
            htf_fibonacci_context["selector"] = htf_selector_meta
        log_fib_flow_fn(
            "[FIB-FLOW] HTF fibonacci context created: symbol=%s timeframe=%s htf_tf=%s available=%s",
            symbol or "tBTCUSD",
            timeframe,
            htf_timeframe,
            htf_fibonacci_context.get("available", False),
            logger=logger,
        )
        return htf_fibonacci_context, htf_selector_meta
    except Exception as exc:  # pragma: no cover - defensive orchestration wrapper
        htf_fibonacci_context = {
            "available": False,
            "reason": "HTF_CONTEXT_ERROR",
        }
        log_fib_flow_fn(
            "[FIB-FLOW] HTF fibonacci context failed: symbol=%s timeframe=%s error=%s",
            symbol or "tBTCUSD",
            timeframe,
            str(exc),
            logger=logger,
        )
        return htf_fibonacci_context, htf_selector_meta


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
