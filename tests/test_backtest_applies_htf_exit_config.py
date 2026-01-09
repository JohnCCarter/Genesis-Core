import pandas as pd

from core.backtest.engine import BacktestEngine


class _DummyChampionCfg:
    def __init__(self) -> None:
        self.config: dict = {}
        self.source = "dummy"
        self.version = "0"
        self.checksum = "dummy"
        self.loaded_at = "now"


def test_backtest_engine_applies_htf_exit_config(monkeypatch):
    # Stub pipeline evaluation to avoid pulling in full strategy/model stack.
    def _fake_evaluate_pipeline(*, candles, policy, configs, state):
        # Minimal structure expected by BacktestEngine.run()
        result = {"action": "NONE", "confidence": 0.5, "regime": "BALANCED", "features": {}}
        meta = {"decision": {"size": 0.0, "reasons": [], "state_out": {}}, "features": {}}
        return result, meta

    monkeypatch.setattr("core.backtest.engine.evaluate_pipeline", _fake_evaluate_pipeline)

    # Build a tiny candle frame.
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2025-01-01", periods=5, freq="h"),
            "open": [100, 101, 102, 103, 104],
            "high": [101, 102, 103, 104, 105],
            "low": [99, 100, 101, 102, 103],
            "close": [100, 101, 102, 103, 104],
            "volume": [1, 1, 1, 1, 1],
        }
    )

    engine = BacktestEngine(symbol="tBTCUSD", timeframe="1h", warmup_bars=0, fast_window=False)
    engine.candles_df = df

    # Avoid reading champion files during test.
    engine.champion_loader.load_cached = lambda *_args, **_kwargs: _DummyChampionCfg()

    engine.run(configs={"htf_exit_config": {"enable_partials": False}})

    assert engine.htf_exit_config["enable_partials"] is False
    assert engine.htf_exit_engine.enable_partials is False
