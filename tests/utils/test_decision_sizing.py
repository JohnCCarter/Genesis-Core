from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from core.config.authority_mode_resolver import AUTHORITY_MODE_SOURCE_CANONICAL
from core.strategy.decision_sizing import apply_sizing


def test_apply_sizing_composes_active_multipliers_and_exports_ri_state() -> None:
    cfg = {
        "multi_timeframe": {
            "regime_intelligence": {
                "enabled": True,
                "version": "v2",
                "authority_mode": "regime_module",
                "clarity_score": {
                    "enabled": True,
                    "weights": {
                        "confidence": 1.0,
                        "edge": 0.0,
                        "ev": 0.0,
                        "regime_alignment": 0.0,
                    },
                },
                "size_multiplier": {"min": 0.5, "max": 0.5},
                "risk_state": {
                    "enabled": True,
                    "drawdown_guard": {
                        "soft_threshold": 0.03,
                        "hard_threshold": 0.06,
                        "soft_mult": 0.70,
                        "hard_mult": 0.40,
                    },
                    "transition_guard": {
                        "enabled": True,
                        "guard_bars": 4,
                        "mult": 0.60,
                    },
                },
            }
        },
        "risk": {
            "risk_map": [[0.50, 1.0], [0.80, 2.0]],
            "regime_size_multipliers": {"bull": 0.8},
            "htf_regime_size_multipliers": {"bear": 0.5},
            "volatility_sizing": {
                "enabled": True,
                "high_vol_threshold": 80,
                "high_vol_multiplier": 0.4,
                "atr_period": 14,
            },
            "min_combined_multiplier": 0.01,
        },
    }
    state_in = {
        "atr_percentiles": {"14": {"p80": 1.0}},
        "current_atr": 1.5,
        "equity_drawdown_pct": 0.03,
        "bars_since_regime_change": 2,
        "last_regime": "bear",
    }
    state_out: dict[str, object] = {}

    size, conf_val_gate = apply_sizing(
        candidate="LONG",
        confidence={"buy": 0.8, "sell": 0.1, "buy_scaled": 0.6},
        regime="bull",
        htf_regime="bear",
        state_in=state_in,
        state_out=state_out,
        cfg=cfg,
        p_buy=0.9,
        p_sell=0.1,
        r_default=1.0,
        max_ev=1.0,
        logger=MagicMock(),
        sanitize_context=lambda value: value,
    )

    assert conf_val_gate == pytest.approx(0.8)
    assert size == pytest.approx(0.0504)
    assert state_out["size_base"] == pytest.approx(2.0)
    assert state_out["size_scale"] == pytest.approx(0.75)
    assert state_out["size_regime_mult"] == pytest.approx(0.8)
    assert state_out["size_htf_regime_mult"] == pytest.approx(0.5)
    assert state_out["size_vol_mult"] == pytest.approx(0.4)
    assert state_out["size_combined_mult"] == pytest.approx(0.0504)
    assert state_out["size_before_ri_clarity"] == pytest.approx(0.1008)
    assert state_out["size_after_ri_clarity"] == pytest.approx(size)
    assert state_out["ri_flag_enabled"] is True
    assert state_out["ri_version"] == "v2"
    assert state_out["authority_mode"] == "regime_module"
    assert state_out["authority_mode_source"] == AUTHORITY_MODE_SOURCE_CANONICAL
    assert state_out["ri_clarity_enabled"] is True
    assert state_out["ri_clarity_apply"] == "sizing_only"
    assert state_out["ri_clarity_score"] == 80
    assert state_out["ri_clarity_raw"] == pytest.approx(0.8)
    assert state_out["ri_clarity_round_policy"] == "half_even"
    assert state_out["ri_clarity_multiplier"] == pytest.approx(0.5)
    assert state_out["ri_risk_state_enabled"] is True
    assert state_out["ri_risk_state_drawdown_mult"] == pytest.approx(0.7)
    assert state_out["ri_risk_state_transition_mult"] == pytest.approx(0.6)
    assert state_out["ri_risk_state_multiplier"] == pytest.approx(0.42)
    assert state_out["last_regime"] == "bull"
    assert state_out["bars_since_regime_change"] == 1


def test_apply_sizing_uses_min_combined_floor_and_increments_regime_counter() -> None:
    cfg = {
        "risk": {
            "risk_map": [[0.50, 1.0]],
            "regime_size_multipliers": {"balanced": 0.5},
            "htf_regime_size_multipliers": {"bull": 0.5},
            "volatility_sizing": {
                "enabled": True,
                "high_vol_threshold": 80,
                "high_vol_multiplier": 0.5,
                "atr_period": 14,
            },
            "min_combined_multiplier": 0.1,
        }
    }
    state_in = {
        "atr_percentiles": {"14": {"p80": 1.0}},
        "current_atr": 2.0,
        "bars_since_regime_change": 5,
        "last_regime": "balanced",
    }
    state_out: dict[str, object] = {}

    size, conf_val_gate = apply_sizing(
        candidate="LONG",
        confidence={"buy": 0.5, "sell": 0.1, "buy_scaled": 0.1},
        regime="balanced",
        htf_regime="bull",
        state_in=state_in,
        state_out=state_out,
        cfg=cfg,
        p_buy=0.7,
        p_sell=0.2,
        r_default=1.0,
        max_ev=0.5,
        logger=MagicMock(),
        sanitize_context=lambda value: value,
    )

    assert conf_val_gate == pytest.approx(0.5)
    assert state_out["size_base"] == pytest.approx(1.0)
    assert state_out["size_scale"] == pytest.approx(0.2)
    assert state_out["size_regime_mult"] == pytest.approx(0.5)
    assert state_out["size_htf_regime_mult"] == pytest.approx(0.5)
    assert state_out["size_vol_mult"] == pytest.approx(0.5)
    assert state_out["size_combined_mult"] == pytest.approx(0.1)
    assert size == pytest.approx(0.1)
    assert state_out["ri_clarity_enabled"] is False
    assert state_out["ri_clarity_score"] is None
    assert state_out["ri_risk_state_enabled"] is False
    assert state_out["ri_risk_state_multiplier"] == pytest.approx(1.0)
    assert state_out["last_regime"] == "balanced"
    assert state_out["bars_since_regime_change"] == 6
