from __future__ import annotations

from typing import Any, Dict, Iterable, Tuple


def _sigmoid(z: float) -> float:
    import math

    return 1.0 / (1.0 + math.exp(-z))


def predict_proba(
    features: Dict[str, float],
    *,
    schema: Iterable[str] = ("ema", "rsi"),
    buy_w: Iterable[float] | None = None,
    buy_b: float = 0.0,
    sell_w: Iterable[float] | None = None,
    sell_b: float = 0.0,
    calib_buy: tuple[float, float] = (1.0, 0.0),
    calib_sell: tuple[float, float] = (1.0, 0.0),
) -> Dict[str, float]:
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
    features: Dict[str, float],
    *,
    model_meta: Dict[str, Any] | None = None,
) -> Tuple[Dict[str, float], Dict[str, Any]]:
    """Wrapper som hämtar vikter/kalibrering från ModelRegistry och applicerar kalibrering.

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
    meta_out: Dict[str, Any] = {
        "versions": {
            "prob_model_version": meta.get("version", "v1"),
            "calibration_version": meta.get("calibration_version", "v1"),
        },
        "schema": list(schema),
    }
    return probas, meta_out
