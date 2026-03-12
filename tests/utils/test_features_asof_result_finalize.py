from __future__ import annotations

import pytest

from core.strategy.features_asof_parts.result_finalize_utils import finalize_feature_result


def test_finalize_feature_result_preserves_identity_and_caches_same_tuple() -> None:
    features = {"alpha": 1.0}
    fib_feature_status = {"available": True, "reason": "OK"}
    htf_fibonacci_context = {"available": True, "source": "htf"}
    ltf_fibonacci_context = {"available": True, "source": "ltf"}
    htf_selector_meta = {"selected": "6h"}
    atr_vals = [0.7, 0.8]
    atr_percentiles = {"atr_14": {"p50": 0.8}}
    observed: dict[str, object] = {}

    def _fake_build_meta(*args):
        observed["meta_args"] = args
        return {"meta": "ok"}

    def _fake_cache_store(cache_key, result):
        observed["cache_call"] = (cache_key, result)

    result = finalize_feature_result(
        features=features,
        fib_feature_status=fib_feature_status,
        htf_fibonacci_context=htf_fibonacci_context,
        ltf_fibonacci_context=ltf_fibonacci_context,
        htf_selector_meta=htf_selector_meta,
        asof_bar=42,
        total_bars=120,
        atr14_current=0.9,
        atr_vals=atr_vals,
        atr_period=14,
        atr_percentiles=atr_percentiles,
        cache_key="cache-key",
        build_meta_fn=_fake_build_meta,
        cache_store_fn=_fake_cache_store,
    )

    meta = result[1]
    assert observed["meta_args"] == (
        features,
        fib_feature_status,
        htf_fibonacci_context,
        ltf_fibonacci_context,
        htf_selector_meta,
        42,
        120,
        0.9,
        atr_vals,
        14,
        atr_percentiles,
    )
    assert result[0] is features
    assert result[1] is meta
    assert observed["cache_call"] == ("cache-key", result)
    assert observed["cache_call"][1] is result


def test_finalize_feature_result_skips_cache_store_when_meta_builder_raises() -> None:
    cache_calls = []

    def _boom(*_args):
        raise RuntimeError("meta failed")

    def _fake_cache_store(cache_key, result):
        cache_calls.append((cache_key, result))

    with pytest.raises(RuntimeError, match="meta failed"):
        finalize_feature_result(
            features={"alpha": 1.0},
            fib_feature_status={"available": False, "reason": "X"},
            htf_fibonacci_context={},
            ltf_fibonacci_context={},
            htf_selector_meta=None,
            asof_bar=1,
            total_bars=2,
            atr14_current=None,
            atr_vals=None,
            atr_period=14,
            atr_percentiles={},
            cache_key="cache-key",
            build_meta_fn=_boom,
            cache_store_fn=_fake_cache_store,
        )

    assert cache_calls == []
