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


def test_backtest_entry_reasons_attached_to_trade(monkeypatch):
    """Regression: entry reasons must come from the entry bar.

    BacktestEngine should pass meta['decision']['reasons'] into PositionTracker before
    executing an entry, so the resulting trade contains the correct entry_reasons.
    """

    reasons = ["R1", "R2"]

    def _fake_evaluate_pipeline(*, candles, policy, configs, state):  # noqa: ARG001
        already_entered = bool((state or {}).get("entered"))
        if already_entered:
            result = {"action": "NONE", "confidence": 0.5, "regime": "BALANCED"}
            meta = {
                "decision": {"size": 0.0, "reasons": [], "state_out": {"entered": True}},
                "features": {},
            }
            return result, meta

        result = {"action": "LONG", "confidence": {"overall": 0.6}, "regime": {"name": "BALANCED"}}
        meta = {
            "decision": {"size": 0.01, "reasons": reasons, "state_out": {"entered": True}},
            "features": {},
        }
        return result, meta

    monkeypatch.setattr("core.backtest.engine.evaluate_pipeline", _fake_evaluate_pipeline)

    engine = BacktestEngine(symbol="tBTCUSD", timeframe="1h", warmup_bars=0, fast_window=False)
    engine.champion_loader.load_cached = lambda *_args, **_kwargs: _DummyChampionCfg()

    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2025-01-01", periods=10, freq="h"),
            "open": [100 + i for i in range(10)],
            "high": [101 + i for i in range(10)],
            "low": [99 + i for i in range(10)],
            "close": [100 + i for i in range(10)],
            "volume": [1 for _ in range(10)],
        }
    )
    engine.candles_df = df

    # Keep exit enabled/disabled irrelevant; we rely on end-of-run close.
    res = engine.run(configs={"exit": {"enabled": False}})
    trades = res.get("trades") or []
    assert len(trades) == 1
    assert trades[0].get("entry_reasons") == reasons
