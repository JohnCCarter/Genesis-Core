from __future__ import annotations


def test_compute_candles_hash_fast_hash_env_is_case_insensitive(monkeypatch) -> None:
    from core.strategy.features_asof import _compute_candles_hash

    candles = {"close": [100.0, 101.23456]}

    monkeypatch.setenv("GENESIS_FAST_HASH", "TRUE")
    key = _compute_candles_hash(candles, 1)

    # Fast-hash path has the stable "asof:last_close" format.
    assert key == "1:101.2346"
