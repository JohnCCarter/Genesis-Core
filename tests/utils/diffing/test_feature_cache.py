from __future__ import annotations

from core.utils.diffing.feature_cache import IndicatorCache, make_indicator_fingerprint


def test_indicator_cache_roundtrip():
    cache = IndicatorCache(max_size=2)
    key = make_indicator_fingerprint("rsi", params={"period": 14}, series=[1.0, 2.0, 3.0])
    cache.store(key, [10, 20, 30])
    assert cache.lookup(key) == [10, 20, 30]


def test_indicator_cache_eviction():
    cache = IndicatorCache(max_size=1)
    key1 = make_indicator_fingerprint("rsi", params={"period": 14}, series=[1, 2, 3])
    key2 = make_indicator_fingerprint("atr", params={"period": 14}, series=[1, 2, 3])
    cache.store(key1, [1])
    cache.store(key2, [2])
    assert cache.lookup(key1) is None
    assert cache.lookup(key2) == [2]


def test_indicator_cache_updates_lru():
    cache = IndicatorCache(max_size=2)
    k1 = make_indicator_fingerprint("rsi", params={"period": 14}, series=[1, 2, 3])
    k2 = make_indicator_fingerprint("atr", params={"period": 14}, series=[1, 2, 3])
    k3 = make_indicator_fingerprint("ema", params={"period": 20}, series=[1, 2, 3])
    cache.store(k1, [1])
    cache.store(k2, [2])
    assert cache.lookup(k1) == [1]
    cache.store(k3, [3])
    assert cache.lookup(k2) is None
    assert cache.lookup(k1) == [1]


def test_indicator_fingerprint_handles_nested_series():
    cache = IndicatorCache(max_size=2)
    nested_series = [(1.0, 2.0, 3.0), (4.0, 5.0, 6.0)]
    key_nested = make_indicator_fingerprint("adx", params={"period": 14}, series=nested_series)
    cache.store(key_nested, [0.5, 0.6])
    assert cache.lookup(key_nested) == [0.5, 0.6]
