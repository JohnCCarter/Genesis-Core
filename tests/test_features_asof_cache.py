from __future__ import annotations


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
