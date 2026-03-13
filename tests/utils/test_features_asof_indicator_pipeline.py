from __future__ import annotations

from types import SimpleNamespace

import numpy as np

from core.strategy.features_asof_parts.indicator_pipeline_utils import build_indicator_pipeline


def test_build_indicator_pipeline_preserves_order_and_returns_fresh_feature_copy() -> None:
    calls: list[str] = []
    atr_vals = np.asarray([1.1, 1.2, 1.3], dtype=float)
    base_features = {"rsi_inv_lag1": 0.2, "atr_14": 1.3}

    indicator_state = SimpleNamespace(
        rsi_current_raw=60.0,
        rsi_lag1_raw=55.0,
        bb_last_3=[0.2, 0.3, 0.4],
        atr_vals=atr_vals,
        atr_window_56=[0.9, 1.0],
        atr14_current=1.3,
        vol_shift_last_3=[1.1, 1.2, 1.3],
        vol_shift_current=1.4,
        rsi_used_fast_path=True,
    )
    base_bundle = SimpleNamespace(
        features=base_features,
        rsi_current=0.2,
        atr_percentiles={"14": {"p40": 1.0, "p80": 1.5}},
    )

    def _fake_indicator_builder(*args):
        calls.append("indicator")
        assert args == (
            [1.0, 2.0],
            [0.5, 1.5],
            [0.8, 1.8],
            1,
            {"ema_20": [1.0, 1.1]},
            1,
            14,
        )
        return indicator_state

    def _fake_base_builder(*args):
        calls.append("base")
        assert args == (
            60.0,
            55.0,
            [0.2, 0.3, 0.4],
            [1.1, 1.2, 1.3],
            1.4,
            [0.9, 1.0],
            atr_vals,
            1.3,
        )
        return base_bundle

    bundle = build_indicator_pipeline(
        highs=[1.0, 2.0],
        lows=[0.5, 1.5],
        closes=[0.8, 1.8],
        asof_bar=1,
        pre={"ema_20": [1.0, 1.1]},
        pre_idx=1,
        atr_period=14,
        build_indicator_state_fn=_fake_indicator_builder,
        build_base_feature_bundle_fn=_fake_base_builder,
    )

    assert calls == ["indicator", "base"]
    assert bundle.features == base_features
    assert bundle.features is not base_features
    assert bundle.rsi_current == 0.2
    assert bundle.atr_percentiles == {"14": {"p40": 1.0, "p80": 1.5}}
    assert bundle.atr_vals is atr_vals
    assert bundle.atr14_current == 1.3
    assert bundle.rsi_used_fast_path is True


def test_build_indicator_pipeline_preserves_slow_signal_and_none_atr_values() -> None:
    indicator_state = SimpleNamespace(
        rsi_current_raw=40.0,
        rsi_lag1_raw=42.0,
        bb_last_3=[],
        atr_vals=None,
        atr_window_56=[],
        atr14_current=None,
        vol_shift_last_3=[],
        vol_shift_current=1.0,
        rsi_used_fast_path=False,
    )
    base_bundle = SimpleNamespace(
        features={"rsi_inv_lag1": -0.16, "atr_14": 0.0},
        rsi_current=-0.2,
        atr_percentiles={"14": {"p40": 0.0, "p80": 0.0}},
    )

    bundle = build_indicator_pipeline(
        highs=[1.0],
        lows=[0.5],
        closes=[0.8],
        asof_bar=0,
        pre={},
        pre_idx=0,
        atr_period=21,
        build_indicator_state_fn=lambda *_args: indicator_state,
        build_base_feature_bundle_fn=lambda *_args: base_bundle,
    )

    assert bundle.features == {"rsi_inv_lag1": -0.16, "atr_14": 0.0}
    assert bundle.atr_vals is None
    assert bundle.atr14_current is None
    assert bundle.rsi_used_fast_path is False
