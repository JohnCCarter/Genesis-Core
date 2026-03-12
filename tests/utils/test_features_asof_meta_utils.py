from __future__ import annotations

from core.strategy.features_asof_parts.meta_utils import build_feature_meta


def test_build_feature_meta_preserves_passthrough_and_atr_fields() -> None:
    features = {"atr_14": 2.5, "x": 1.0}
    fib_status = {"available": True, "reason": "OK"}
    htf_context = {"available": True, "reason": "OK"}
    ltf_context = {"available": False, "reason": "LTF_CONTEXT_ERROR"}
    selector_meta = {"selected": "6h"}
    atr_vals = [1.0, 1.5, 3.5]
    atr_percentiles = {"14": {"p40": 1.2, "p80": 2.8}}

    meta = build_feature_meta(
        features=features,
        fib_feature_status=fib_status,
        htf_fibonacci_context=htf_context,
        ltf_fibonacci_context=ltf_context,
        htf_selector_meta=selector_meta,
        asof_bar=77,
        total_bars=120,
        atr14_current=2.5,
        atr_vals=atr_vals,
        atr_period=28,
        atr_percentiles=atr_percentiles,
    )

    assert meta["versions"] == {
        "features_v15_highvol_optimized": True,
        "features_v16_fibonacci": True,
        "features_v17_fibonacci_combinations": True,
        "htf_fibonacci_symmetric_chamoun": True,
    }
    assert meta["reasons"] == []
    assert meta["feature_count"] == len(features)
    assert meta["asof_bar"] == 77
    assert meta["uses_bars"] == [0, 77]
    assert meta["total_bars_available"] == 120
    assert meta["fibonacci_features"] is fib_status
    assert meta["htf_fibonacci"] is htf_context
    assert meta["ltf_fibonacci"] is ltf_context
    assert meta["current_atr"] == 2.5
    assert meta["current_atr_used"] == 3.5
    assert meta["atr_period_used"] == 28
    assert meta["atr_percentiles"] is atr_percentiles
    assert meta["htf_selector"] is selector_meta


def test_build_feature_meta_uses_fib_reason_fallback_when_unavailable() -> None:
    meta = build_feature_meta(
        features={"atr_14": 0.0},
        fib_feature_status={"available": False, "reason": None},
        htf_fibonacci_context={},
        ltf_fibonacci_context={},
        htf_selector_meta=None,
        asof_bar=60,
        total_bars=100,
        atr14_current=None,
        atr_vals=None,
        atr_period=14,
        atr_percentiles={"14": {"p40": 1.0, "p80": 1.0}},
    )

    assert meta["reasons"] == ["FIB_FEATURES_CONTEXT_ERROR"]
    assert meta["current_atr"] is None
    assert meta["current_atr_used"] is None
    assert meta["htf_selector"] is None


def test_build_feature_meta_preserves_explicit_fib_reason_and_empty_atr_values() -> None:
    meta = build_feature_meta(
        features={"atr_14": 1.1, "foo": 2.2},
        fib_feature_status={"available": False, "reason": "FIB_TOO_EARLY"},
        htf_fibonacci_context={"available": False},
        ltf_fibonacci_context={"available": False},
        htf_selector_meta={"selected": "1d"},
        asof_bar=10,
        total_bars=25,
        atr14_current=1.1,
        atr_vals=[],
        atr_period=14,
        atr_percentiles={"14": {"p40": 0.9, "p80": 1.3}},
    )

    assert meta["reasons"] == ["FIB_TOO_EARLY"]
    assert meta["feature_count"] == 2
    assert meta["current_atr"] == 1.1
    assert meta["current_atr_used"] is None
    assert meta["htf_selector"] == {"selected": "1d"}
