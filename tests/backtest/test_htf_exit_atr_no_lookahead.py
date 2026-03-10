from __future__ import annotations

import pandas as pd

from core.backtest.engine import BacktestEngine
from core.indicators.atr import calculate_atr


class _DummyChampionCfg:
    def __init__(self) -> None:
        self.config: dict = {}
        self.source = "dummy"
        self.version = "0"
        self.checksum = "dummy"
        self.loaded_at = "now"


def _make_engine(df: pd.DataFrame) -> BacktestEngine:
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

    # Avoid any heavy/complex exit logic; we only want ATR computed.
    engine.htf_exit_engine.check_exits = lambda *_args, **_kwargs: []
    return engine


def test_htf_exit_atr_uses_only_past_bars_and_is_prefix_invariant():
    """Regression: HTF-exit ATR must not use future bars.

    We verify two things:
    1) ATR computed for a given bar_index matches calculate_atr on the same prefix.
    2) Mutating data AFTER bar_index must not change ATR at that bar.
    """

    ts = pd.date_range("2025-01-01", periods=20, freq="h")
    base = pd.DataFrame(
        {
            "timestamp": ts,
            "open": [100 + i for i in range(len(ts))],
            "high": [101 + i for i in range(len(ts))],
            "low": [99 + i for i in range(len(ts))],
            "close": [100 + i for i in range(len(ts))],
            "volume": [1.0 for _ in range(len(ts))],
        }
    )

    engine = _make_engine(base)

    bar_index = 10
    meta: dict = {}
    configs = {"exit": {"enabled": True}, "_global_index": bar_index}

    engine._check_htf_exit_conditions(
        current_price=float(base["close"].iloc[bar_index]),
        timestamp=pd.Timestamp(base["timestamp"].iloc[bar_index]),
        bar_data={
            "timestamp": pd.Timestamp(base["timestamp"].iloc[bar_index]),
            "open": float(base["open"].iloc[bar_index]),
            "high": float(base["high"].iloc[bar_index]),
            "low": float(base["low"].iloc[bar_index]),
            "close": float(base["close"].iloc[bar_index]),
            "volume": float(base["volume"].iloc[bar_index]),
        },
        result={"features": {}},
        meta=meta,
        configs=configs,
        bar_index=bar_index,
    )

    atr_recorded = float(meta.get("signal", {}).get("current_atr", 0.0))

    # Expected ATR is computed on prefix up to bar_index.
    recent_highs = base["high"].iloc[: bar_index + 1].to_numpy(copy=False)
    recent_lows = base["low"].iloc[: bar_index + 1].to_numpy(copy=False)
    recent_closes = base["close"].iloc[: bar_index + 1].to_numpy(copy=False)

    window_size = min(14, len(recent_closes))
    i0 = len(recent_closes) - window_size
    expected_series = calculate_atr(
        recent_highs[i0:],
        recent_lows[i0:],
        recent_closes[i0:],
        period=14,
    )
    expected_atr = float(expected_series[-1]) if expected_series else 100.0

    assert atr_recorded == expected_atr

    # Prefix invariance: mutate *future* bars and confirm ATR at bar_index is unchanged.
    mutated = base.copy()
    mutated.loc[bar_index + 1 :, "high"] = mutated.loc[bar_index + 1 :, "high"] + 10_000
    mutated.loc[bar_index + 1 :, "low"] = mutated.loc[bar_index + 1 :, "low"] - 10_000

    engine2 = _make_engine(mutated)
    meta2: dict = {}
    engine2._check_htf_exit_conditions(
        current_price=float(mutated["close"].iloc[bar_index]),
        timestamp=pd.Timestamp(mutated["timestamp"].iloc[bar_index]),
        bar_data={
            "timestamp": pd.Timestamp(mutated["timestamp"].iloc[bar_index]),
            "open": float(mutated["open"].iloc[bar_index]),
            "high": float(mutated["high"].iloc[bar_index]),
            "low": float(mutated["low"].iloc[bar_index]),
            "close": float(mutated["close"].iloc[bar_index]),
            "volume": float(mutated["volume"].iloc[bar_index]),
        },
        result={"features": {}},
        meta=meta2,
        configs=configs,
        bar_index=bar_index,
    )

    atr_recorded_2 = float(meta2.get("signal", {}).get("current_atr", 0.0))
    assert atr_recorded_2 == expected_atr
