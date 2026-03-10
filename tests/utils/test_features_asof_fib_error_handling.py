from __future__ import annotations

import math

import numpy as np

import core.strategy.features_asof as features_asof


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


def test_fibonacci_feature_error_exposes_meta_and_fallbacks(monkeypatch) -> None:
    candles = _synthetic_candles()

    def _raise_detect(*_args, **_kwargs):
        raise RuntimeError("forced swing failure")

    monkeypatch.setattr(features_asof, "detect_swing_points", _raise_detect)

    feats, meta = features_asof.extract_features_backtest(
        candles,
        asof_bar=len(candles["close"]) - 1,
        timeframe="1h",
        symbol="tBTCUSD",
        config={"thresholds": {"signal_adaptation": {"atr_period": 14}}},
    )

    expected_fallbacks = {
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

    for key, expected in expected_fallbacks.items():
        assert key in feats
        value = float(feats[key])
        assert math.isfinite(value)
        assert value == expected

    fib_status = meta.get("fibonacci_features") or {}
    assert fib_status.get("available") is False
    assert fib_status.get("reason") == "FIB_FEATURES_CONTEXT_ERROR"
    assert "FIB_FEATURES_CONTEXT_ERROR" in (meta.get("reasons") or [])
