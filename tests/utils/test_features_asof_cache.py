from __future__ import annotations

import logging
import math
from collections import OrderedDict


def test_fast_hash_key_changes_with_dataset_state(monkeypatch) -> None:
    from core.strategy.features_asof import _compute_candles_hash

    monkeypatch.setenv("GENESIS_FAST_HASH", "1")

    candles_a = {
        "open": [100.0, 101.0, 102.0, 103.0, 104.0],
        "high": [101.0, 102.0, 103.0, 104.0, 106.0],
        "low": [99.0, 100.0, 101.0, 102.0, 103.0],
        "close": [100.0, 101.0, 102.0, 103.0, 105.0],
        "volume": [10.0, 11.0, 12.0, 13.0, 14.0],
    }
    candles_b = {
        "open": [100.0, 101.0, 102.0, 103.0, 104.0],
        "high": [101.0, 102.0, 103.0, 104.0, 106.0],
        "low": [99.0, 100.0, 101.0, 102.0, 103.0],
        # Same asof_bar and same last_close as candles_a, but different earlier history.
        "close": [90.0, 91.0, 92.0, 103.0, 105.0],
        "volume": [10.0, 11.0, 12.0, 13.0, 14.0],
    }

    key_a = _compute_candles_hash(candles_a, 4)
    key_b = _compute_candles_hash(candles_b, 4)

    assert key_a != key_b


def test_fast_hash_close_only_input_keeps_legacy_shape(monkeypatch) -> None:
    from core.strategy.features_asof import _compute_candles_hash

    monkeypatch.setenv("GENESIS_FAST_HASH", "1")
    candles = {"close": [100.0, 101.23456]}

    key = _compute_candles_hash(candles, 1)

    assert key == "1:101.2346"


def test_as_config_dict_logs_and_falls_back_on_model_dump_error(caplog) -> None:
    from core.strategy.features_asof import _as_config_dict

    class _BrokenConfig:
        def model_dump(self):  # pragma: no cover - called by test
            raise RuntimeError("boom")

    with caplog.at_level(logging.WARNING):
        out = _as_config_dict(_BrokenConfig())

    assert out == {}
    assert "model_dump fallback to empty dict" in caplog.text


def test_clip_feature_value_preserves_nan_and_bounds_semantics() -> None:
    from core.strategy.features_asof_parts.numeric_utils import clip_feature_value

    assert clip_feature_value(float("nan"), -1.0, 1.0) == 0.0
    assert clip_feature_value(-2.5, -1.0, 1.0) == -1.0
    assert clip_feature_value(2.5, -1.0, 1.0) == 1.0
    assert clip_feature_value(0.25, -1.0, 1.0) == 0.25


def test_clip_wrapper_matches_internal_numeric_helper() -> None:
    from core.strategy.features_asof import _clip
    from core.strategy.features_asof_parts.numeric_utils import clip_feature_value

    cases = [
        (float("nan"), -1.0, 1.0),
        (-2.5, -1.0, 1.0),
        (2.5, -1.0, 1.0),
        (0.25, -1.0, 1.0),
    ]

    for value, low, high in cases:
        wrapper_value = _clip(value, low, high)
        helper_value = clip_feature_value(value, low, high)

        if math.isnan(value):
            assert wrapper_value == 0.0
            assert helper_value == 0.0
        else:
            assert wrapper_value == helper_value


def test_indicator_cache_wrappers_delegate_when_enabled() -> None:
    from core.strategy.features_asof import _indicator_cache_lookup, _indicator_cache_store

    class _FakeCache:
        def __init__(self) -> None:
            self.items = {}

        def lookup(self, key):
            return self.items.get(key)

        def store(self, key, value) -> None:
            self.items[key] = value

    import core.strategy.features_asof as features_asof

    original_cache = features_asof._indicator_cache
    original_enabled = features_asof._INDICATOR_CACHE_ENABLED
    fake_cache = _FakeCache()
    try:
        features_asof._indicator_cache = fake_cache
        features_asof._INDICATOR_CACHE_ENABLED = True

        assert _indicator_cache_lookup("missing") is None
        _indicator_cache_store("answer", 42)
        assert _indicator_cache_lookup("answer") == 42
    finally:
        features_asof._indicator_cache = original_cache
        features_asof._INDICATOR_CACHE_ENABLED = original_enabled


def test_indicator_cache_wrappers_are_noop_when_disabled() -> None:
    from core.strategy.features_asof import _indicator_cache_lookup, _indicator_cache_store

    class _FakeCache:
        def __init__(self) -> None:
            self.store_calls = 0

        def lookup(self, key):
            raise AssertionError("lookup should not be called when cache is disabled")

        def store(self, key, value) -> None:
            self.store_calls += 1

    import core.strategy.features_asof as features_asof

    original_cache = features_asof._indicator_cache
    original_enabled = features_asof._INDICATOR_CACHE_ENABLED
    fake_cache = _FakeCache()
    try:
        features_asof._indicator_cache = fake_cache
        features_asof._INDICATOR_CACHE_ENABLED = False

        assert _indicator_cache_lookup("anything") is None
        _indicator_cache_store("answer", 42)
        assert fake_cache.store_calls == 0
    finally:
        features_asof._indicator_cache = original_cache
        features_asof._INDICATOR_CACHE_ENABLED = original_enabled


def test_feature_result_cache_lookup_moves_hit_to_mru_end() -> None:
    from core.strategy.features_asof_parts.result_cache_utils import feature_result_cache_lookup

    first = ({"f": 1.0}, {"m": 1})
    second = ({"f": 2.0}, {"m": 2})
    cache = OrderedDict(
        [
            ("oldest", first),
            ("newest", second),
        ]
    )

    result = feature_result_cache_lookup(cache, "oldest")

    assert result is first
    assert list(cache.keys()) == ["newest", "oldest"]


def test_feature_result_cache_store_enforces_size_and_overwrite_semantics() -> None:
    from core.strategy.features_asof_parts.result_cache_utils import feature_result_cache_store

    first = ({"f": 1.0}, {"m": 1})
    second = ({"f": 2.0}, {"m": 2})
    third = ({"f": 3.0}, {"m": 3})
    updated_second = ({"f": 22.0}, {"m": 22})
    cache = OrderedDict(
        [
            ("k1", first),
            ("k2", second),
        ]
    )

    feature_result_cache_store(cache, "k2", updated_second, 2)
    assert len(cache) == 2
    assert cache["k2"] is updated_second
    assert list(cache.keys()) == ["k1", "k2"]

    feature_result_cache_store(cache, "k3", third, 2)
    assert len(cache) == 2
    assert list(cache.keys()) == ["k2", "k3"]
    assert "k1" not in cache
    assert cache["k3"] is third
