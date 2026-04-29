from __future__ import annotations

import numpy as np
import pytest

import core.strategy.features_asof as features_asof


@pytest.fixture(autouse=True)
def _clear_features_asof_caches() -> None:
    features_asof._feature_cache.clear()
    try:
        features_asof._indicator_cache.clear()
    except Exception:
        pass
    yield
    features_asof._feature_cache.clear()
    try:
        features_asof._indicator_cache.clear()
    except Exception:
        pass


def _synthetic_candles(*, n: int = 80, seed: int = 17) -> dict[str, list[float]]:
    rng = np.random.default_rng(seed)
    closes = (30_000.0 + np.cumsum(rng.normal(0, 20, size=n))).tolist()
    opens = [closes[0]] + closes[:-1]
    highs = (np.maximum(opens, closes) + 12.0).tolist()
    lows = (np.minimum(opens, closes) - 12.0).tolist()
    volume = (np.ones(n) * 100.0).tolist()
    return {
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volume,
    }


def test_feature_cache_key_separates_precompute_and_runtime_modes(monkeypatch) -> None:
    candles = _synthetic_candles()
    monkeypatch.setenv("GENESIS_PRECOMPUTE_FEATURES", "1")

    runtime_key = features_asof._compute_feature_cache_key(candles, 55, config={})
    precompute_key = features_asof._compute_feature_cache_key(
        candles,
        55,
        config={"precomputed_features": {"atr_14": [1.0] * len(candles["close"])}},
    )

    assert runtime_key != precompute_key
    assert runtime_key.startswith("runtime:")
    assert precompute_key.startswith("precompute:")


def test_feature_cache_lookup_returns_defensive_copy() -> None:
    cache_key = "runtime:55:test"
    original = ({"fib05_prox_atr": 0.1}, {"fibonacci_features": {"available": True}})

    features_asof._feature_cache_store(cache_key, original)

    first = features_asof._feature_cache_lookup(cache_key)
    second = features_asof._feature_cache_lookup(cache_key)

    assert first is not None
    assert second is not None
    assert first is not second
    assert first[0] is not second[0]
    assert first[1] is not second[1]

    first[0]["fib05_prox_atr"] = 999.0
    first[1]["fibonacci_features"]["available"] = False

    third = features_asof._feature_cache_lookup(cache_key)
    assert third is not None
    assert third[0]["fib05_prox_atr"] == 0.1
    assert third[1]["fibonacci_features"]["available"] is True


def test_build_fibonacci_feature_updates_marks_insufficient_local_history() -> None:
    candles = _synthetic_candles()
    highs = candles["high"]
    lows = candles["low"]
    closes = candles["close"]
    atr_values = [150.0] * len(closes)

    fib_features, fib_status = features_asof._build_fibonacci_feature_updates(
        highs=highs,
        lows=lows,
        closes=closes,
        atr_values=atr_values,
        pre={
            "fib_high_idx": [10_000],
            "fib_low_idx": [10_001],
            "fib_high_px": [31_000.0],
            "fib_low_px": [29_000.0],
        },
        pre_idx=len(closes) - 1,
        timeframe="3h",
        asof_bar=len(closes) - 1,
        atr_period=14,
        rsi_current=0.25,
    )

    assert fib_status == {"available": False, "reason": "insufficient_local_history"}
    assert fib_features["fib05_prox_atr"] == 0.0
    assert fib_features["fib0618_prox_atr"] == 0.0
    assert fib_features["fib_prox_score"] == 0.0
    assert fib_features["fib_prox_x_adx"] == 0.0
    assert fib_features["swing_retrace_depth"] == 0.0


def test_build_fibonacci_feature_updates_uses_local_window_normalization_inputs() -> None:
    candles = _synthetic_candles(n=260)
    kwargs = {
        "highs": candles["high"],
        "lows": candles["low"],
        "closes": candles["close"],
        "pre": {},
        "pre_idx": len(candles["close"]) - 1,
        "timeframe": "3h",
        "asof_bar": len(candles["close"]) - 1,
        "atr_period": 14,
    }

    fib_features_a, fib_status_a = features_asof._build_fibonacci_feature_updates(
        atr_values=[1.0] * len(candles["close"]),
        rsi_current=0.99,
        **kwargs,
    )
    fib_features_b, fib_status_b = features_asof._build_fibonacci_feature_updates(
        atr_values=[10_000.0] * len(candles["close"]),
        rsi_current=-0.99,
        **kwargs,
    )

    assert fib_status_a == fib_status_b
    assert fib_features_a == fib_features_b
