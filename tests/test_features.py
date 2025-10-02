from __future__ import annotations

from core.strategy.features import extract_features


def test_extract_features_stub_shapes():
    candles = {
        "open": [1, 2, 3],
        "high": [2, 3, 4],
        "low": [0.5, 1.5, 2.5],
        "close": [1.5, 2.5, 3.5],
        "volume": [10, 11, 12],
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
    assert set(feats.keys()) == {"ema_delta_pct", "rsi"}


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
