from __future__ import annotations

import math

import numpy as np

import core.strategy.features_asof as features_asof
from core.strategy.features_asof_parts.fibonacci_apply_utils import (
    apply_fibonacci_feature_updates,
)

FIB_KEYS = {
    "fib_dist_min_atr": 10.0,
    "fib_dist_signed_atr": 0.0,
    "fib_prox_score": 0.0,
    "fib0618_prox_atr": 0.0,
    "fib05_prox_atr": 0.0,
    "swing_retrace_depth": 0.0,
    "fib05_x_ema_slope": 0.0,
    "fib_prox_x_adx": 0.0,
    "fib05_x_rsi_inv": 0.0,
}


def _synthetic_candles(*, n: int = 260, seed: int = 7) -> dict[str, list[float]]:
    rng = np.random.default_rng(seed)
    closes = (30_000.0 + np.cumsum(rng.normal(0, 15, size=n))).tolist()
    opens = [closes[0]] + closes[:-1]
    highs = (np.maximum(opens, closes) + 10.0).tolist()
    lows = (np.minimum(opens, closes) - 10.0).tolist()
    volume = (np.ones(n) * 100.0).tolist()
    return {
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volume,
    }


def test_apply_fibonacci_feature_updates_mutates_same_features_dict() -> None:
    features = {"rsi_inv_lag1": 0.3}
    observed: dict[str, object] = {}
    status = {"available": False, "reason": "WRAPPED_STATUS"}

    def _fake_builder(*args):
        observed["args"] = args
        return {"fib_prox_score": 0.75, "fib05_x_rsi_inv": -0.2}, status

    result_features, result_status = apply_fibonacci_feature_updates(
        features=features,
        highs=[1.0, 2.0],
        lows=[0.5, 1.5],
        closes=[0.8, 1.8],
        atr_vals=[0.1, 0.2],
        pre={"ema_20": [1.0, 1.1]},
        pre_idx=1,
        timeframe="1h",
        asof_bar=1,
        rsi_current=0.4,
        build_fibonacci_updates_fn=_fake_builder,
    )

    assert observed["args"] == (
        [1.0, 2.0],
        [0.5, 1.5],
        [0.8, 1.8],
        [0.1, 0.2],
        {"ema_20": [1.0, 1.1]},
        1,
        "1h",
        1,
        0.4,
    )
    assert result_features is features
    assert features["fib_prox_score"] == 0.75
    assert features["fib05_x_rsi_inv"] == -0.2
    assert result_status is status


def test_extract_asof_continues_to_route_through_fibonacci_wrapper(
    monkeypatch,
) -> None:
    candles = _synthetic_candles()
    calls = {"count": 0}

    def _fake_wrapper(
        highs,
        lows,
        closes,
        atr_vals,
        pre,
        pre_idx,
        timeframe,
        asof_bar,
        rsi_current,
    ):
        calls["count"] += 1
        assert timeframe == "1h"
        assert asof_bar == len(closes) - 1
        assert isinstance(pre_idx, int)
        assert math.isfinite(float(rsi_current))
        return dict(FIB_KEYS), {"available": False, "reason": "WRAPPER_PATH"}

    monkeypatch.setattr(features_asof, "_build_fibonacci_feature_updates", _fake_wrapper)

    feats, meta = features_asof.extract_features_backtest(
        candles,
        asof_bar=len(candles["close"]) - 1,
        timeframe="1h",
        symbol="tBTCUSD",
        config={"thresholds": {"signal_adaptation": {"atr_period": 14}}},
    )

    assert calls["count"] == 1
    for key, expected in FIB_KEYS.items():
        assert key in feats
        assert float(feats[key]) == expected
    fib_status = meta.get("fibonacci_features") or {}
    assert fib_status.get("available") is False
    assert fib_status.get("reason") == "WRAPPER_PATH"
    assert "WRAPPER_PATH" in (meta.get("reasons") or [])
