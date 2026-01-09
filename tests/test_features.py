from __future__ import annotations

import numpy as np

from core.strategy.features_asof import _compute_candles_hash, extract_features


def test_extract_features_stub_shapes():
    # Need at least 60 bars for volume_trend (slow_period=50)
    candles = {
        "open": [100.0 + i for i in range(60)],
        "high": [102.0 + i for i in range(60)],
        "low": [99.0 + i for i in range(60)],
        "close": [101.0 + i for i in range(60)],
        "volume": [1000.0 + i * 10 for i in range(60)],
    }
    cfg = {
        "features": {
            "percentiles": {"ema_delta_pct": [-0.5, 0.5], "rsi": [-1.0, 1.0]},
            "versions": {"feature_set": "v1"},
        }
    }
    feats, meta = extract_features(candles, config=cfg)
    assert isinstance(feats, dict) and isinstance(meta, dict)
    assert "versions" in meta and "reasons" in meta

    # SSOT (features_asof) ska innehålla v17 features + atr_14 (5 original + atr_14 + 6 Fibonacci + 3 kombinationer = 15)
    expected_original_features = {
        "rsi_inv_lag1",
        "volatility_shift_ma3",
        "bb_position_inv_ma3",
        "rsi_vol_interaction",
        "vol_regime",
    }
    expected_core_features = {"atr_14"}
    expected_fibonacci_features = {
        "fib_dist_min_atr",
        "fib_dist_signed_atr",
        "fib_prox_score",
        "fib0618_prox_atr",
        "fib05_prox_atr",
        "swing_retrace_depth",
    }
    expected_combination_features = {
        "fib05_x_ema_slope",
        "fib_prox_x_adx",
        "fib05_x_rsi_inv",
    }
    expected_features = (
        expected_original_features
        | expected_core_features
        | expected_fibonacci_features
        | expected_combination_features
    )

    assert set(feats.keys()) == expected_features
    assert len(feats) == 15  # 5 original + atr_14 + 6 Fibonacci + 3 combinations

    assert meta.get("feature_count") == 15
    assert meta.get("versions", {}).get("features_v17_fibonacci_combinations") is True


def test_extract_features_time_alignment_uses_closed_bar():
    # Need more bars for derived features (240 window)
    candles = {
        "open": [100.0 + i for i in range(300)],
        "high": [102.0 + i for i in range(300)],
        "low": [99.0 + i for i in range(300)],
        "close": [101.0 + i * 0.5 for i in range(300)],
        "volume": [1000.0 + i * 10 for i in range(300)],
    }
    cfg = {
        "features": {
            "percentiles": {"ema_delta_pct": [-10.0, 10.0], "rsi": [-10.0, 10.0]},
            "versions": {"feature_set": "v1"},
        }
    }
    feats_last, _ = extract_features(candles, config=cfg, now_index=299)
    feats_prev, _ = extract_features(candles, config=cfg, now_index=298)
    # now_index=299 ska använda stängd bar index 298; now_index=298 -> stängd bar 297
    # With 300 bars of trending data, features should differ
    assert feats_last != feats_prev


def test_compute_candles_hash_accepts_numpy_arrays():
    # Arrange: numpy-slices ska fungera utan sanningsvärdeskrasch
    arr = np.linspace(100.0, 109.0, num=10, dtype=float)
    candles_np = {
        "open": arr + 1.0,
        "high": arr + 2.0,
        "low": arr - 1.0,
        "close": arr,
        "volume": arr * 10.0,
    }
    candles_list = {k: v.tolist() for k, v in candles_np.items()}
    asof = len(arr) - 1

    # Act: hashen ska vara densamma och ingen exception ska uppstå
    hash_np = _compute_candles_hash(candles_np, asof)
    hash_list = _compute_candles_hash(candles_list, asof)

    # Assert
    assert hash_np == hash_list
