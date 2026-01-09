import numpy as np

from core.utils.diffing import feature_cache


def test_flatten_series_respects_limit_with_numpy_arrays():
    data = np.arange(0, 100, dtype=float)
    flattened = feature_cache._flatten_series(data, limit=5)
    assert flattened == [95.0, 96.0, 97.0, 98.0, 99.0]


def test_make_indicator_fingerprint_consistent_for_dict_input():
    candles = {
        "open": [float(i) for i in range(50)],
        "high": [float(i + 0.5) for i in range(50)],
        "low": [float(i - 0.5) for i in range(50)],
    }
    fp1 = feature_cache.make_indicator_fingerprint(
        "test", params={"x": 1}, series=candles, series_limit=10
    )
    fp2 = feature_cache.make_indicator_fingerprint(
        "test", params={"x": 1}, series=candles, series_limit=10
    )
    assert fp1 == fp2


def test_indicator_fingerprint_changes_on_tail_difference():
    base = [float(i) for i in range(60)]
    altered = base.copy()
    altered[-1] = 999.0
    fp_base = feature_cache.make_indicator_fingerprint("series", series=base, series_limit=10)
    fp_altered = feature_cache.make_indicator_fingerprint("series", series=altered, series_limit=10)
    assert fp_base != fp_altered


def test_numeric_hash_matches_iterable_hash():
    numbers = [0.123456789, 1.987654321, -2.5, 42.0]
    fast = feature_cache._hash_numeric_sequence(np.asarray(numbers, dtype=float), precision=6)
    slow = feature_cache._hash_iterable(numbers, precision=6)
    assert fast == slow


def test_indicator_fingerprint_respects_limit_fast_path():
    data = [float(i) for i in range(300)]
    fingerprint = feature_cache.make_indicator_fingerprint(
        "fast", series=data, series_limit=32, precision=5
    )
    expected = feature_cache._hash_iterable(data[-32:], precision=5)
    assert fingerprint.data_hash == expected
