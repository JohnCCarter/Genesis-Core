from __future__ import annotations

from fastapi import APIRouter, Body

from core.strategy.evaluate import evaluate_pipeline

router = APIRouter()


@router.post("/strategy/evaluate")
def strategy_evaluate(payload: dict = Body({})) -> dict:
    invalid_candles_error = {
        "ok": False,
        "error": {
            "code": "INVALID_CANDLES",
            "message": "candles must include non-empty equal-length open/high/low/close/volume arrays",
        },
    }

    required_keys = ("open", "high", "low", "close", "volume")
    candles = payload.get("candles")
    if not isinstance(candles, dict):
        return invalid_candles_error

    series_list: list[list] = []
    for key in required_keys:
        if key not in candles:
            return invalid_candles_error
        value = candles.get(key)
        if not isinstance(value, list) or len(value) == 0:
            return invalid_candles_error
        series_list.append(value)

    lengths = {len(v) for v in series_list}
    if len(lengths) != 1:
        return invalid_candles_error

    policy = payload.get("policy") or {"symbol": "tBTCUSD", "timeframe": "1m"}
    configs = payload.get("configs") or {}
    state = payload.get("state") or {}
    result, meta = evaluate_pipeline(candles, policy=policy, configs=configs, state=state)
    return {"result": result, "meta": meta}
