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

    # Should contain TOP 7 features (coefficient importance - optimal balance)
    expected_features = {
        "rsi",
        "bb_position",
        "trend_confluence",
        "vol_trend",
        "bb_width",
        "momentum_displacement_z",
        "adx",
    }
    assert set(feats.keys()) == expected_features
    assert meta.get("feature_count") == 7
    assert meta.get("versions", {}).get("features_v2") is True


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
