from __future__ import annotations

import math
from types import SimpleNamespace

import numpy as np
import pytest

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


@pytest.fixture(autouse=True)
def _clear_features_asof_result_cache() -> None:
    features_asof._feature_cache.clear()
    yield
    features_asof._feature_cache.clear()


def test_fibonacci_feature_error_exposes_meta_and_fallbacks(monkeypatch) -> None:
    candles = _synthetic_candles()
    expected_features = {
        "rsi_inv_lag1",
        "volatility_shift_ma3",
        "bb_position_inv_ma3",
        "rsi_vol_interaction",
        "vol_regime",
        "atr_14",
        "fib_dist_min_atr",
        "fib_dist_signed_atr",
        "fib_prox_score",
        "fib0618_prox_atr",
        "fib05_prox_atr",
        "swing_retrace_depth",
        "fib05_x_ema_slope",
        "fib_prox_x_adx",
        "fib05_x_rsi_inv",
    }

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
    assert set(feats.keys()) == expected_features
    assert meta.get("feature_count") == 15


def test_ltf_context_error_exposes_meta_without_changing_feature_shape(monkeypatch) -> None:
    candles = _synthetic_candles()

    def _raise_ltf(*_args, **_kwargs):
        raise RuntimeError("forced ltf failure")

    monkeypatch.setattr(features_asof, "get_ltf_fibonacci_context", _raise_ltf)

    feats, meta = features_asof.extract_features_backtest(
        candles,
        asof_bar=len(candles["close"]) - 1,
        timeframe="1h",
        symbol="tBTCUSD",
        config={"thresholds": {"signal_adaptation": {"atr_period": 14}}},
    )

    expected_features = {
        "rsi_inv_lag1",
        "volatility_shift_ma3",
        "bb_position_inv_ma3",
        "rsi_vol_interaction",
        "vol_regime",
        "atr_14",
        "fib_dist_min_atr",
        "fib_dist_signed_atr",
        "fib_prox_score",
        "fib0618_prox_atr",
        "fib05_prox_atr",
        "swing_retrace_depth",
        "fib05_x_ema_slope",
        "fib_prox_x_adx",
        "fib05_x_rsi_inv",
    }

    ltf_status = meta.get("ltf_fibonacci") or {}
    assert ltf_status.get("available") is False
    assert ltf_status.get("reason") == "LTF_CONTEXT_ERROR"
    assert set(feats.keys()) == expected_features
    assert meta.get("feature_count") == 15


def test_htf_context_error_retains_selector_meta_without_changing_feature_shape(
    monkeypatch,
) -> None:
    candles = _synthetic_candles()

    def _raise_htf(*_args, **_kwargs):
        raise RuntimeError("forced htf failure")

    expected_features = {
        "rsi_inv_lag1",
        "volatility_shift_ma3",
        "bb_position_inv_ma3",
        "rsi_vol_interaction",
        "vol_regime",
        "atr_14",
        "fib_dist_min_atr",
        "fib_dist_signed_atr",
        "fib_prox_score",
        "fib0618_prox_atr",
        "fib05_prox_atr",
        "swing_retrace_depth",
        "fib05_x_ema_slope",
        "fib_prox_x_adx",
        "fib05_x_rsi_inv",
    }

    configs = [
        {
            "thresholds": {"signal_adaptation": {"atr_period": 14}},
            "multi_timeframe": {
                "htf_selector": {
                    "mode": "fixed",
                    "per_timeframe": {"1h": {"timeframe": "6h"}},
                }
            },
        },
        SimpleNamespace(
            multi_timeframe={
                "htf_selector": {
                    "mode": "fixed",
                    "per_timeframe": {"1h": {"timeframe": "6h"}},
                }
            }
        ),
    ]

    monkeypatch.setattr(features_asof, "get_htf_fibonacci_context", _raise_htf)

    for config in configs:
        feats, meta = features_asof.extract_features_backtest(
            candles,
            asof_bar=len(candles["close"]) - 1,
            timeframe="1h",
            symbol="tBTCUSD",
            config=config,
        )

        htf_status = meta.get("htf_fibonacci") or {}
        selector_meta = meta.get("htf_selector") or {}
        assert htf_status.get("available") is False
        assert htf_status.get("reason") == "HTF_CONTEXT_ERROR"
        assert "selector" not in htf_status
        assert selector_meta.get("selected") == "6h"
        assert set(feats.keys()) == expected_features
        assert meta.get("feature_count") == 15
