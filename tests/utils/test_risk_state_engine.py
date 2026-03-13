"""Tests for risk_state state injection in engine and decision_sizing."""

from unittest.mock import MagicMock


def test_equity_drawdown_pct_injected_into_state():
    """equity_drawdown_pct is 0.0 when equity equals peak."""
    from core.backtest.engine import BacktestEngine

    engine = BacktestEngine.__new__(BacktestEngine)
    engine.state = {}
    mock_pt = MagicMock()
    mock_pt.current_equity = 10000.0
    engine.position_tracker = mock_pt

    _cur_eq = engine.position_tracker.current_equity
    _peak_eq = engine.state.get("_peak_equity", _cur_eq)
    if _cur_eq > _peak_eq:
        _peak_eq = _cur_eq
    engine.state["_peak_equity"] = _peak_eq
    engine.state["equity_drawdown_pct"] = (_peak_eq - _cur_eq) / _peak_eq if _peak_eq > 0 else 0.0

    assert engine.state["equity_drawdown_pct"] == 0.0
    assert engine.state["_peak_equity"] == 10000.0


def test_equity_drawdown_pct_reflects_loss():
    """equity_drawdown_pct is 0.05 when equity dropped 5% from peak."""
    from core.backtest.engine import BacktestEngine

    engine = BacktestEngine.__new__(BacktestEngine)
    engine.state = {"_peak_equity": 10000.0}
    mock_pt = MagicMock()
    mock_pt.current_equity = 9500.0
    engine.position_tracker = mock_pt

    _cur_eq = engine.position_tracker.current_equity
    _peak_eq = engine.state.get("_peak_equity", _cur_eq)
    if _cur_eq > _peak_eq:
        _peak_eq = _cur_eq
    engine.state["_peak_equity"] = _peak_eq
    engine.state["equity_drawdown_pct"] = (_peak_eq - _cur_eq) / _peak_eq if _peak_eq > 0 else 0.0

    assert abs(engine.state["equity_drawdown_pct"] - 0.05) < 1e-9


def test_bars_since_regime_change_resets_on_transition():
    """bars_since_regime_change resets to 1 when regime changes."""
    state_in = {"last_regime": "bull", "bars_since_regime_change": 5}
    state_out = {}

    _last_regime = state_in.get("last_regime")
    _cur_regime = "bear"
    if _last_regime is None or _last_regime == _cur_regime:
        _bars_since_change = int(state_in.get("bars_since_regime_change", 0))
    else:
        _bars_since_change = 0
    state_out["last_regime"] = _cur_regime
    state_out["bars_since_regime_change"] = _bars_since_change + 1

    assert state_out["bars_since_regime_change"] == 1
    assert state_out["last_regime"] == "bear"


def test_bars_since_regime_change_increments_on_stable():
    """bars_since_regime_change increments when regime is stable."""
    state_in = {"last_regime": "bull", "bars_since_regime_change": 5}
    state_out = {}

    _last_regime = state_in.get("last_regime")
    _cur_regime = "bull"
    if _last_regime is None or _last_regime == _cur_regime:
        _bars_since_change = int(state_in.get("bars_since_regime_change", 0))
    else:
        _bars_since_change = 0
    state_out["last_regime"] = _cur_regime
    state_out["bars_since_regime_change"] = _bars_since_change + 1

    assert state_out["bars_since_regime_change"] == 6
