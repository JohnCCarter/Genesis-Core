from __future__ import annotations

import pandas as pd

from core.backtest.engine import BacktestEngine


class _DummyChampionCfg:
    def __init__(self) -> None:
        self.config: dict = {}
        self.source = "dummy"
        self.version = "0"
        self.checksum = "dummy"
        self.loaded_at = "now"


def test_new_htf_exit_engine_adapter_normalizes_level_keys(monkeypatch):
    """Regression: new HTF exit engine must receive expected fib keys.

    The strategy-level HTF exit engine reads the fib levels using keys:
    - htf_fib_0382
    - htf_fib_05
    - htf_fib_0618

    Our fib context can store levels keyed by floats (0.382/0.5/0.618). The backtest
    adapter must normalize these so GENESIS_HTF_EXITS=1 doesn't silently degrade
    into "Invalid HTF Data" -> HOLD.
    """

    monkeypatch.setenv("GENESIS_HTF_EXITS", "1")

    ts = pd.date_range("2025-01-01", periods=5, freq="h")
    df = pd.DataFrame(
        {
            "timestamp": ts,
            "open": [100, 101, 102, 103, 104],
            "high": [101, 102, 103, 104, 105],
            "low": [99, 100, 101, 102, 103],
            "close": [100, 101, 102, 103, 104],
            "volume": [1.0, 1.0, 1.0, 1.0, 1.0],
        }
    )

    engine = BacktestEngine(symbol="tBTCUSD", timeframe="1h", warmup_bars=0, fast_window=False)
    engine.champion_loader.load_cached = lambda *_args, **_kwargs: _DummyChampionCfg()
    engine.candles_df = df
    engine._prepare_numpy_arrays()

    # Ensure we have a position so _check_htf_exit_conditions runs.
    engine.position_tracker.execute_action(
        action="LONG",
        size=0.01,
        price=float(df["close"].iloc[0]),
        timestamp=pd.Timestamp(df["timestamp"].iloc[0]),
        symbol="tBTCUSD",
    )

    # Force the new-engine adapter path and verify htf_data normalization.
    engine._use_new_exit_engine = True

    expected = {"htf_fib_0382": 111.0, "htf_fib_05": 222.0, "htf_fib_0618": 333.0}

    def _check_exits_stub(*, htf_data, **_kwargs):
        for key, val in expected.items():
            assert float(htf_data.get(key)) == val
        return []

    engine.htf_exit_engine.check_exits = _check_exits_stub

    bar_index = 3
    meta: dict = {
        "features": {
            "htf_fibonacci": {
                "available": True,
                "levels": {
                    0.382: expected["htf_fib_0382"],
                    0.5: expected["htf_fib_05"],
                    0.618: expected["htf_fib_0618"],
                },
            }
        },
        "decision": {"state_out": {}},
    }
    configs = {"exit": {"enabled": True}, "_global_index": bar_index}

    engine._check_htf_exit_conditions(
        current_price=float(df["close"].iloc[bar_index]),
        timestamp=pd.Timestamp(df["timestamp"].iloc[bar_index]),
        bar_data={
            "timestamp": pd.Timestamp(df["timestamp"].iloc[bar_index]),
            "open": float(df["open"].iloc[bar_index]),
            "high": float(df["high"].iloc[bar_index]),
            "low": float(df["low"].iloc[bar_index]),
            "close": float(df["close"].iloc[bar_index]),
            "volume": float(df["volume"].iloc[bar_index]),
        },
        result={"features": {}},
        meta=meta,
        configs=configs,
        bar_index=bar_index,
    )
