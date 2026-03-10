from __future__ import annotations


def test_htf_exit_engine_auto_enabled_by_config_when_env_unset(monkeypatch):
    """P1 regression: if config provides a non-empty htf_exit_config and env is unset,
    BacktestEngine should select the NEW HTF exit engine.

    This prevents runner vs manual backtest mismatches where htf_exit_config was present
    but GENESIS_HTF_EXITS wasn't set.
    """

    # Avoid unrelated mode-mismatch warnings leaking from the developer environment.
    monkeypatch.setenv("GENESIS_PRECOMPUTE_FEATURES", "0")

    monkeypatch.delenv("GENESIS_HTF_EXITS", raising=False)

    from core.backtest.engine import BacktestEngine

    engine = BacktestEngine(symbol="tBTCUSD", timeframe="1h")
    engine._init_htf_exit_engine({"enable_partials": True})

    assert getattr(engine, "_use_new_exit_engine", False) is True


def test_htf_exit_engine_env_can_force_legacy_even_with_config(monkeypatch):
    """If GENESIS_HTF_EXITS is explicitly set to 0, it must be authoritative."""

    # Avoid unrelated mode-mismatch warnings leaking from the developer environment.
    monkeypatch.setenv("GENESIS_PRECOMPUTE_FEATURES", "0")

    monkeypatch.setenv("GENESIS_HTF_EXITS", "0")

    from core.backtest.engine import BacktestEngine

    engine = BacktestEngine(symbol="tBTCUSD", timeframe="1h")
    engine._init_htf_exit_engine({"enable_partials": True})

    assert getattr(engine, "_use_new_exit_engine", False) is False
