"""Tests for compute_risk_state_multiplier in regime_intelligence."""

import pytest


def _cfg(
    enabled=True,
    soft_threshold=0.03,
    hard_threshold=0.06,
    soft_mult=0.70,
    hard_mult=0.40,
    transition_enabled=True,
    guard_bars=4,
    transition_mult=0.60,
):
    return {
        "enabled": enabled,
        "drawdown_guard": {
            "soft_threshold": soft_threshold,
            "hard_threshold": hard_threshold,
            "soft_mult": soft_mult,
            "hard_mult": hard_mult,
        },
        "transition_guard": {
            "enabled": transition_enabled,
            "guard_bars": guard_bars,
            "mult": transition_mult,
        },
    }


def test_disabled_returns_one():
    from core.intelligence.regime.risk_state import compute_risk_state_multiplier

    result = compute_risk_state_multiplier(
        cfg=_cfg(enabled=False),
        equity_drawdown_pct=0.10,
        bars_since_regime_change=1,
    )
    assert result["multiplier"] == 1.0
    assert result["enabled"] is False


def test_no_drawdown_no_transition_returns_one():
    from core.intelligence.regime.risk_state import compute_risk_state_multiplier

    result = compute_risk_state_multiplier(
        cfg=_cfg(),
        equity_drawdown_pct=0.0,
        bars_since_regime_change=10,
    )
    assert result["multiplier"] == 1.0


def test_soft_drawdown_reduces_size():
    from core.intelligence.regime.risk_state import compute_risk_state_multiplier

    # At soft_threshold (0.03), mult should be soft_mult (0.70)
    result = compute_risk_state_multiplier(
        cfg=_cfg(),
        equity_drawdown_pct=0.03,
        bars_since_regime_change=10,
    )
    assert result["multiplier"] == pytest.approx(0.70, abs=0.01)


def test_hard_drawdown_reduces_size_to_hard_mult():
    from core.intelligence.regime.risk_state import compute_risk_state_multiplier

    result = compute_risk_state_multiplier(
        cfg=_cfg(),
        equity_drawdown_pct=0.06,
        bars_since_regime_change=10,
    )
    assert result["multiplier"] == pytest.approx(0.40, abs=0.01)


def test_drawdown_beyond_hard_clamped():
    from core.intelligence.regime.risk_state import compute_risk_state_multiplier

    result = compute_risk_state_multiplier(
        cfg=_cfg(),
        equity_drawdown_pct=0.20,
        bars_since_regime_change=10,
    )
    assert result["multiplier"] == pytest.approx(0.40, abs=0.01)


def test_transition_within_guard_window_reduces_size():
    from core.intelligence.regime.risk_state import compute_risk_state_multiplier

    result = compute_risk_state_multiplier(
        cfg=_cfg(),
        equity_drawdown_pct=0.0,
        bars_since_regime_change=2,  # within guard_bars=4
    )
    assert result["multiplier"] == pytest.approx(0.60, abs=0.01)


def test_transition_outside_guard_window_no_effect():
    from core.intelligence.regime.risk_state import compute_risk_state_multiplier

    result = compute_risk_state_multiplier(
        cfg=_cfg(),
        equity_drawdown_pct=0.0,
        bars_since_regime_change=5,  # outside guard_bars=4
    )
    assert result["multiplier"] == 1.0


def test_drawdown_and_transition_are_multiplicative():
    from core.intelligence.regime.risk_state import compute_risk_state_multiplier

    # soft drawdown (0.70) * transition (0.60) = 0.42
    result = compute_risk_state_multiplier(
        cfg=_cfg(),
        equity_drawdown_pct=0.03,
        bars_since_regime_change=2,
    )
    assert result["multiplier"] == pytest.approx(0.70 * 0.60, abs=0.01)


def test_result_contains_debug_keys():
    from core.intelligence.regime.risk_state import compute_risk_state_multiplier

    result = compute_risk_state_multiplier(
        cfg=_cfg(),
        equity_drawdown_pct=0.04,
        bars_since_regime_change=2,
    )
    assert "multiplier" in result
    assert "drawdown_mult" in result
    assert "transition_mult" in result
    assert "equity_drawdown_pct" in result
    assert "bars_since_regime_change" in result
