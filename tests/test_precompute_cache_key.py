from __future__ import annotations

import re

import pandas as pd

from core.backtest.engine import BacktestEngine


def test_precompute_cache_key_changes_with_date_window(monkeypatch) -> None:
    # Ensure engine init doesn't warn/error due to mixed-mode env.
    monkeypatch.setenv("GENESIS_PRECOMPUTE_FEATURES", "0")

    engine = BacktestEngine(symbol="tBTCUSD", timeframe="1h", warmup_bars=0, fast_window=False)

    df_a = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=10, freq="h"),
            "open": [1.0] * 10,
            "high": [1.0] * 10,
            "low": [1.0] * 10,
            "close": [1.0] * 10,
            "volume": [1.0] * 10,
        }
    )
    df_b = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-02-01", periods=10, freq="h"),
            "open": [1.0] * 10,
            "high": [1.0] * 10,
            "low": [1.0] * 10,
            "close": [1.0] * 10,
            "volume": [1.0] * 10,
        }
    )

    key_a = engine._precompute_cache_key(df_a)
    key_b = engine._precompute_cache_key(df_b)

    assert key_a != key_b
    assert key_a.startswith("tBTCUSD_1h_v1_")
    assert key_b.startswith("tBTCUSD_1h_v1_")


def test_precompute_cache_key_legacy_shape_when_config_hash_unset_or_empty(monkeypatch) -> None:
    monkeypatch.setenv("GENESIS_PRECOMPUTE_FEATURES", "0")

    engine = BacktestEngine(symbol="tBTCUSD", timeframe="1h", warmup_bars=0, fast_window=False)
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-03-01", periods=10, freq="h"),
            "open": [1.0] * 10,
            "high": [1.0] * 10,
            "low": [1.0] * 10,
            "close": [1.0] * 10,
            "volume": [1.0] * 10,
        }
    )

    monkeypatch.delenv("GENESIS_PRECOMPUTE_CONFIG_HASH", raising=False)
    key_unset = engine._precompute_cache_key(df)

    assert "_cfg" not in key_unset
    assert re.fullmatch(r"tBTCUSD_1h_v1_[0-9a-f]{12}_\d+_-?\d+_-?\d+", key_unset)

    monkeypatch.setenv("GENESIS_PRECOMPUTE_CONFIG_HASH", "")
    key_empty = engine._precompute_cache_key(df)

    assert key_empty == key_unset


def test_precompute_cache_key_changes_with_non_empty_config_hash(monkeypatch) -> None:
    monkeypatch.setenv("GENESIS_PRECOMPUTE_FEATURES", "0")

    engine = BacktestEngine(symbol="tBTCUSD", timeframe="1h", warmup_bars=0, fast_window=False)
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-03-01", periods=10, freq="h"),
            "open": [1.0] * 10,
            "high": [1.0] * 10,
            "low": [1.0] * 10,
            "close": [1.0] * 10,
            "volume": [1.0] * 10,
        }
    )

    monkeypatch.setenv("GENESIS_PRECOMPUTE_CONFIG_HASH", "cfg-A:atr=14")
    key_a = engine._precompute_cache_key(df)

    monkeypatch.setenv("GENESIS_PRECOMPUTE_CONFIG_HASH", "cfg-B:atr=21")
    key_b = engine._precompute_cache_key(df)

    assert key_a != key_b
    assert re.search(r"_cfg[0-9a-f]{12}_", key_a)
    assert re.search(r"_cfg[0-9a-f]{12}_", key_b)
    assert "cfg-A:atr=14" not in key_a
    assert "cfg-B:atr=21" not in key_b
