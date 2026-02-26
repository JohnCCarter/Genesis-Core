from __future__ import annotations

import pandas as pd

import core.backtest.engine as engine_mod
from core.backtest.engine import BacktestEngine


def _make_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "timestamp": [pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02")],
            "open": [1.0, 2.0],
            "high": [1.5, 2.5],
            "low": [0.5, 1.5],
            "close": [1.2, 2.2],
            "volume": [10.0, 11.0],
        }
    )


def test_precompute_cache_key_changes_when_schema_version_changes(monkeypatch) -> None:
    df = _make_df()
    engine = BacktestEngine(symbol="tBTCUSD", timeframe="1h")

    v0 = int(engine_mod.PRECOMPUTE_SCHEMA_VERSION)
    key1 = engine._precompute_cache_key(df)
    assert f"_v{v0}_" in key1

    monkeypatch.setattr(engine_mod, "PRECOMPUTE_SCHEMA_VERSION", v0 + 1)

    key2 = engine._precompute_cache_key(df)

    assert key1 != key2
    assert f"_v{v0 + 1}_" in key2
