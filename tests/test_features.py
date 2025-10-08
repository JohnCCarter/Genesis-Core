from __future__ import annotations

from core.strategy.features import extract_features


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

    # Should contain all 11 enhanced features
    expected_features = {
        "ema_delta_pct",
        "rsi",
        "atr_pct",
        "bb_width",
        "bb_position",
        "adx",
        "ema_slope",
        "price_vs_ema",
        "vol_change",
        "vol_trend",
        "obv_normalized",
    }
    assert set(feats.keys()) == expected_features
    assert meta.get("feature_count") == 11
    assert meta.get("versions", {}).get("features_v2") is True


def test_extract_features_time_alignment_uses_closed_bar():
    candles = {
        "open": [1, 2, 3, 4],
        "high": [2, 3, 4, 5],
        "low": [0.5, 1.5, 2.5, 3.5],
        "close": [1.5, 2.5, 3.5, 4.5],
        "volume": [10, 11, 12, 13],
    }
    cfg = {
        "features": {
            "percentiles": {"ema_delta_pct": [-10.0, 10.0], "rsi": [-10.0, 10.0]},
            "versions": {"feature_set": "v1"},
        }
    }
    feats_last, _ = extract_features(candles, config=cfg, now_index=3)
    feats_prev, _ = extract_features(candles, config=cfg, now_index=2)
    # now_index=3 ska använda stängd bar index 2; now_index=2 -> stängd bar 1
    assert feats_last != feats_prev
