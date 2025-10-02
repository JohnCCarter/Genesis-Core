from __future__ import annotations

from typing import Dict, Iterable


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

