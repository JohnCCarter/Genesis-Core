from __future__ import annotations

from collections.abc import Iterable
from typing import Any


def _sigmoid(z: float) -> float:
    import math

    return 1.0 / (1.0 + math.exp(-z))


def predict_proba(
    features: dict[str, float],
    *,
    schema: Iterable[str] = ("ema", "rsi"),
    buy_w: Iterable[float] | None = None,
    buy_b: float = 0.0,
    sell_w: Iterable[float] | None = None,
    sell_b: float = 0.0,
    calib_buy: tuple[float, float] = (1.0, 0.0),
    calib_sell: tuple[float, float] = (1.0, 0.0),
) -> dict[str, float]:
    """Beräkna {buy,sell,hold} sannolikheter.

    - Två oberoende logistiska modeller (buy/sell); hold = 1 - (buy_raw + sell_raw)
    - Normalisera till simplex om summering != 1
    - Rena beräkningar, inga sidoeffekter
    """
    keys = list(schema)
    x = [float(features.get(k, 0.0)) for k in keys]

    def _dot(w: Iterable[float] | None, b: float) -> float:
        if w is None:
            return b
        w_list = list(w)
        return (
            sum(
                (w_list[i] if i < len(w_list) else 0.0) * (x[i] if i < len(x) else 0.0)
                for i in range(max(len(w_list), len(x)))
            )
            + b
        )

    a_buy, b_buy = calib_buy
    a_sell, b_sell = calib_sell

    p_buy_raw = _sigmoid(a_buy * _dot(buy_w, buy_b) + b_buy)
    p_sell_raw = _sigmoid(a_sell * _dot(sell_w, sell_b) + b_sell)
    p_hold = max(0.0, 1.0 - (p_buy_raw + p_sell_raw))
    total = p_buy_raw + p_sell_raw + p_hold
    if total <= 0:
        return {"buy": 0.0, "sell": 0.0, "hold": 1.0}
    return {
        "buy": p_buy_raw / total,
        "sell": p_sell_raw / total,
        "hold": p_hold / total,
    }


def predict_proba_for(
    symbol: str,
    timeframe: str,
    features: dict[str, float],
    *,
    model_meta: dict[str, Any] | None = None,
    regime: str | None = None,
) -> tuple[dict[str, float], dict[str, Any]]:
    """Wrapper som hämtar vikter/kalibrering från ModelRegistry och applicerar kalibrering.

    Args:
        symbol: Trading symbol
        timeframe: Timeframe
        features: Feature dict
        model_meta: Optional model metadata (for testing)
        regime: Current market regime for regime-aware calibration

    Returnerar (probas, meta) där meta innehåller versions (prob_model/calibration) och schema.
    Inga sidoeffekter/loggning här.
    """
    from core.strategy.model_registry import ModelRegistry

    if model_meta is None:
        meta = ModelRegistry().get_meta(symbol, timeframe) or {}
    else:
        meta = model_meta

    schema = tuple(meta.get("schema", ()))
    buy = meta.get("buy", {})
    sell = meta.get("sell", {})

    # Check for regime-specific calibration
    regime_calib = meta.get("calibration_by_regime", {})

    if regime and regime_calib:
        # Use regime-specific calibration if available
        regime_buy_calib = regime_calib.get("buy", {}).get(regime, {})
        regime_sell_calib = regime_calib.get("sell", {}).get(regime, {})

        if regime_buy_calib:
            calib_buy = (
                regime_buy_calib.get("a", 1.0),
                regime_buy_calib.get("b", 0.0),
            )
        else:
            # Fallback to default calibration
            calib_buy = (
                buy.get("calib", {}).get("a", 1.0),
                buy.get("calib", {}).get("b", 0.0),
            )

        if regime_sell_calib:
            calib_sell = (
                regime_sell_calib.get("a", 1.0),
                regime_sell_calib.get("b", 0.0),
            )
        else:
            # Fallback to default calibration
            calib_sell = (
                sell.get("calib", {}).get("a", 1.0),
                sell.get("calib", {}).get("b", 0.0),
            )
    else:
        # Use default calibration
        calib_buy = (
            buy.get("calib", {}).get("a", 1.0),
            buy.get("calib", {}).get("b", 0.0),
        )
        calib_sell = (
            sell.get("calib", {}).get("a", 1.0),
            sell.get("calib", {}).get("b", 0.0),
        )

    probas = predict_proba(
        features,
        schema=schema,
        buy_w=buy.get("w"),
        buy_b=buy.get("b", 0.0),
        sell_w=sell.get("w"),
        sell_b=sell.get("b", 0.0),
        calib_buy=calib_buy,
        calib_sell=calib_sell,
    )
    meta_out: dict[str, Any] = {
        "versions": {
            "prob_model_version": meta.get("version", "v1"),
            "calibration_version": meta.get("calibration_version", "v1"),
            "regime_aware_calibration": bool(regime and regime_calib),
        },
        "schema": list(schema),
        "calibration_used": {
            "regime": regime if regime else "none",
            "buy_calib": {"a": calib_buy[0], "b": calib_buy[1]},
            "sell_calib": {"a": calib_sell[0], "b": calib_sell[1]},
        },
    }
    return probas, meta_out


class ProbModel:
    def __init__(self, symbol: str, timeframe: str):
        self.symbol = symbol
        self.timeframe = timeframe

    def predict_proba(self, features: dict[str, float]) -> dict[str, float]:
        probas, _meta = predict_proba_for(self.symbol, self.timeframe, features)
        return probas

    def predict_meta(self, features: dict[str, float]) -> tuple[dict[str, float], dict[str, Any]]:
        return predict_proba_for(self.symbol, self.timeframe, features)
