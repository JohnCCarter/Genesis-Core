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


def test_backtest_engine_is_deterministic_across_two_runs(monkeypatch):
    """Regression: same inputs must produce identical results.

    We stub evaluate_pipeline to be fully deterministic and ensure BacktestEngine.run()
    resets state correctly between runs.

    This test is intentionally small/fast and does not rely on external data.
    """

    # Deterministic, side-effect free pipeline stub.
    def _fake_evaluate_pipeline(*, candles, policy, configs, state):  # noqa: ARG001
        # Always return NONE so no trades occur; determinism should still hold.
        result = {"action": "NONE", "confidence": {"overall": 0.5}, "regime": {"name": "BALANCED"}}
        meta = {"decision": {"size": 0.0, "reasons": [], "state_out": {}}, "features": {}}
        return result, meta

    monkeypatch.setattr("core.backtest.engine.evaluate_pipeline", _fake_evaluate_pipeline)

    # Avoid reading any champion config from disk.
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

    # Run twice with same config.
    r1 = engine.run(configs={"exit": {"enabled": False}})
    r2 = engine.run(configs={"exit": {"enabled": False}})

    # Compare the most important deterministic outputs.
    assert r1.get("error") is None
    assert r2.get("error") is None

    assert (r1.get("summary") or {}) == (r2.get("summary") or {})
    assert (r1.get("metrics") or {}) == (r2.get("metrics") or {})
    assert (r1.get("trades") or []) == (r2.get("trades") or [])


def test_backtest_engine_is_deterministic_with_one_trade(monkeypatch):
    """Stronger regression: determinism should hold even when a trade is created.

    We force exactly one LONG entry on the first bar, then rely on end-of-run close.
    Exit logic is disabled to keep the scenario minimal and deterministic.
    """

    def _fake_evaluate_pipeline(*, candles, policy, configs, state):  # noqa: ARG001
        # Use state to ensure exactly one entry.
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
            "decision": {"size": 0.01, "reasons": ["TEST_ENTRY"], "state_out": {"entered": True}},
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

    cfg = {"exit": {"enabled": False}}
    r1 = engine.run(configs=cfg)
    r2 = engine.run(configs=cfg)

    t1 = r1.get("trades") or []
    t2 = r2.get("trades") or []
    assert len(t1) == 1
    assert t1 == t2
    assert (r1.get("summary") or {}) == (r2.get("summary") or {})


def test_backtest_engine_is_deterministic_with_explicit_exit_reason(monkeypatch):
    """Regression: determinism must hold when exit logic closes a position.

    We monkeypatch the HTF-exit checker to return a deterministic exit reason on a
    specific timestamp, so we exercise the exit/close_position_with_reason path.
    """

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
            "decision": {"size": 0.01, "reasons": ["TEST_ENTRY"], "state_out": {"entered": True}},
            "features": {},
        }
        return result, meta

    monkeypatch.setattr("core.backtest.engine.evaluate_pipeline", _fake_evaluate_pipeline)

    # Deterministic exit on the second bar.
    import pandas as _pd

    exit_ts = _pd.Timestamp("2025-01-01 01:00:00")

    def _fake_check_htf_exit_conditions(
        self, *, current_price, timestamp, bar_data, result, meta, configs, bar_index=None
    ):  # noqa: ARG001
        if timestamp == exit_ts:
            return "TEST_EXIT"
        return None

    monkeypatch.setattr(
        "core.backtest.engine.BacktestEngine._check_htf_exit_conditions",
        _fake_check_htf_exit_conditions,
    )

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

    cfg = {"exit": {"enabled": True}}
    r1 = engine.run(configs=cfg)
    r2 = engine.run(configs=cfg)

    t1 = r1.get("trades") or []
    t2 = r2.get("trades") or []
    assert len(t1) == 1
    assert t1 == t2
    assert t1[0].get("exit_reason") == "TEST_EXIT"
    assert (r1.get("summary") or {}) == (r2.get("summary") or {})
