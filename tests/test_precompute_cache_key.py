from __future__ import annotations

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
    assert key_a.startswith("tBTCUSD_1h_10_")
    assert key_b.startswith("tBTCUSD_1h_10_")
