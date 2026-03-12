from __future__ import annotations

import pytest

from core.strategy.features_asof_parts.base_feature_utils import build_base_feature_bundle


def test_build_base_feature_bundle_keeps_feature_formulas_and_handoff() -> None:
    captured = {}

    def _capture_atr_percentiles(source):
        captured["source"] = source
        return {"14": {"p40": 1.4, "p80": 1.8}}

    bundle = build_base_feature_bundle(
        rsi_current_raw=80.0,
        rsi_lag1_raw=65.0,
        bb_last_3=[0.2, 0.4, 0.6],
        vol_shift_last_3=[0.8, 1.0, 1.2],
        vol_shift_current=1.4,
        atr_window_56=[0.9, 1.1, 1.3],
        atr_vals=[9.9],
        atr14_current=2.5,
        clip_fn=lambda value, lo, hi: max(lo, min(hi, value)),
        build_atr_percentiles_fn=_capture_atr_percentiles,
    )

    assert bundle.features == {
        "rsi_inv_lag1": 0.3,
        "volatility_shift_ma3": 1.0,
        "bb_position_inv_ma3": 0.6,
        "rsi_vol_interaction": 0.84,
        "vol_regime": 1.0,
        "atr_14": 2.5,
    }
    assert bundle.rsi_current == 0.6
    assert bundle.atr_percentiles == {"14": {"p40": 1.4, "p80": 1.8}}
    assert captured["source"] == [0.9, 1.1, 1.3]


def test_build_base_feature_bundle_keeps_defaults_and_atr_fallback() -> None:
    captured = {}

    def _capture_atr_percentiles(source):
        captured["source"] = source
        return {"56": {"p40": 0.4, "p80": 0.8}}

    bundle = build_base_feature_bundle(
        rsi_current_raw=20.0,
        rsi_lag1_raw=-25.0,
        bb_last_3=[],
        vol_shift_last_3=[],
        vol_shift_current=0.2,
        atr_window_56=[],
        atr_vals=[0.4, 0.6],
        atr14_current=None,
        clip_fn=lambda value, lo, hi: max(lo, min(hi, value)),
        build_atr_percentiles_fn=_capture_atr_percentiles,
    )

    assert bundle.features == {
        "rsi_inv_lag1": -1.0,
        "volatility_shift_ma3": 1.0,
        "bb_position_inv_ma3": 0.5,
        "rsi_vol_interaction": -0.3,
        "vol_regime": 0.0,
        "atr_14": 0.0,
    }
    assert bundle.rsi_current == -0.6
    assert bundle.atr_percentiles == {"56": {"p40": 0.4, "p80": 0.8}}
    assert captured["source"] == [0.4, 0.6]


def test_build_base_feature_bundle_clips_interaction_after_vol_shift_clip() -> None:
    bundle = build_base_feature_bundle(
        rsi_current_raw=200.0,
        rsi_lag1_raw=50.0,
        bb_last_3=[0.5],
        vol_shift_last_3=[5.0],
        vol_shift_current=8.0,
        atr_window_56=[],
        atr_vals=None,
        atr14_current=1.0,
        clip_fn=lambda value, lo, hi: max(lo, min(hi, value)),
        build_atr_percentiles_fn=lambda _source: {"14": {"p40": 1.0, "p80": 1.0}},
    )

    assert bundle.rsi_current == pytest.approx(3.0)
    assert bundle.features["rsi_vol_interaction"] == pytest.approx(2.0)
    assert bundle.features["volatility_shift_ma3"] == pytest.approx(2.0)
