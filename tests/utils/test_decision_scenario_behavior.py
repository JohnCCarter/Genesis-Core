from __future__ import annotations

from copy import deepcopy

import pytest

from core.strategy.decision import decide

_BASE_CFG = {
    "ev": {"R_default": 1.0},
    "thresholds": {
        "entry_conf_overall": 0.6,
        "regime_proba": {"bull": 0.6},
    },
    "gates": {"cooldown_bars": 0, "hysteresis_steps": 1},
    "risk": {
        "risk_map": [[0.6, 1.0]],
        "min_combined_multiplier": 0.1,
    },
    "multi_timeframe": {
        "use_htf_block": False,
        "allow_ltf_override": False,
        "regime_intelligence": {
            "enabled": True,
            "version": "v2",
            "clarity_score": {"enabled": False},
            "risk_state": {
                "enabled": True,
                "drawdown_guard": {
                    "soft_threshold": 0.03,
                    "hard_threshold": 0.06,
                    "soft_mult": 0.7,
                    "hard_mult": 0.4,
                },
                "transition_guard": {
                    "enabled": True,
                    "guard_bars": 3,
                    "mult": 0.6,
                },
            },
        },
    },
    "htf_fib": {"entry": {"enabled": False}},
    "ltf_fib": {"entry": {"enabled": False}},
}

_BASE_DECISION_KWARGS = {
    "policy": {},
    "probas": {"buy": 0.8, "sell": 0.2},
    "confidence": {"buy": 0.8, "sell": 0.2},
    "regime": "bull",
    "risk_ctx": {},
}


def test_decide_risk_state_stress_reduces_size_without_changing_action_path() -> None:
    cfg = deepcopy(_BASE_CFG)
    baseline_state = {
        "equity_drawdown_pct": 0.0,
        "bars_since_regime_change": 10,
        "last_regime": "bull",
    }
    stressed_state = {
        "equity_drawdown_pct": 0.03,
        "bars_since_regime_change": 2,
        "last_regime": "bull",
    }

    action_base, meta_base = decide(cfg=cfg, state=baseline_state, **_BASE_DECISION_KWARGS)
    action_stress, meta_stress = decide(cfg=cfg, state=stressed_state, **_BASE_DECISION_KWARGS)

    assert action_base == action_stress == "LONG"
    assert meta_base["reasons"][-1] == "ENTRY_LONG"
    assert meta_stress["reasons"][-1] == "ENTRY_LONG"

    assert float(meta_base["size"]) == pytest.approx(1.0)
    assert float(meta_stress["size"]) == pytest.approx(0.42)
    assert float(meta_stress["size"]) < float(meta_base["size"])

    state_out_base = meta_base["state_out"]
    state_out_stress = meta_stress["state_out"]

    assert state_out_base["ri_risk_state_enabled"] is True
    assert state_out_base["ri_clarity_enabled"] is False
    assert state_out_base["ri_risk_state_multiplier"] == pytest.approx(1.0)
    assert state_out_base["ri_risk_state_transition_mult"] == pytest.approx(1.0)
    assert state_out_base["bars_since_regime_change"] == 11

    assert state_out_stress["ri_risk_state_enabled"] is True
    assert state_out_stress["ri_clarity_enabled"] is False
    assert state_out_stress["ri_risk_state_drawdown_mult"] == pytest.approx(0.7)
    assert state_out_stress["ri_risk_state_transition_mult"] == pytest.approx(0.6)
    assert state_out_stress["ri_risk_state_multiplier"] == pytest.approx(0.42)
    assert state_out_stress["last_regime"] == "bull"
    assert state_out_stress["bars_since_regime_change"] == 3


def test_decide_risk_state_transition_guard_tracks_propagated_state_window() -> None:
    cfg = deepcopy(_BASE_CFG)
    state = {
        "equity_drawdown_pct": 0.0,
        "bars_since_regime_change": 9,
        "last_regime": "bear",
    }

    actions: list[str] = []
    reasons: list[list[str]] = []
    sizes: list[float] = []
    transition_mults: list[float] = []
    propagated_bars: list[int] = []

    for _ in range(5):
        action, meta = decide(cfg=cfg, state=state, **_BASE_DECISION_KWARGS)
        state = meta["state_out"]

        actions.append(action)
        reasons.append(list(meta["reasons"]))
        sizes.append(float(meta["size"]))
        transition_mults.append(float(state["ri_risk_state_transition_mult"]))
        propagated_bars.append(int(state["bars_since_regime_change"]))

    assert actions == ["LONG"] * 5
    assert all(entry[-1] == "ENTRY_LONG" for entry in reasons)

    assert sizes == pytest.approx([1.0, 0.6, 0.6, 0.6, 1.0])
    assert transition_mults == pytest.approx([1.0, 0.6, 0.6, 0.6, 1.0])
    assert propagated_bars == [1, 2, 3, 4, 5]


def test_decide_adaptive_htf_override_progression_flips_block_into_entry() -> None:
    cfg = {
        "ev": {"R_default": 1.0},
        "thresholds": {
            "entry_conf_overall": 0.6,
            "regime_proba": {"balanced": 0.55},
        },
        "gates": {"cooldown_bars": 0, "hysteresis_steps": 1},
        "risk": {"risk_map": [[0.55, 1.0]]},
        "multi_timeframe": {
            "allow_ltf_override": True,
            "ltf_override_threshold": 0.95,
            "ltf_override_adaptive": {
                "enabled": True,
                "window": 2,
                "min_history": 2,
                "percentile": 0.0,
                "fallback_threshold": 0.95,
            },
        },
        "htf_fib": {
            "entry": {
                "enabled": True,
                "long_min_level": 0.5,
                "tolerance_atr": 1.0,
            }
        },
        "ltf_fib": {
            "entry": {
                "enabled": True,
                "long_max_level": 1.0,
                "tolerance_atr": 1.0,
            }
        },
    }
    state_base = {
        "last_close": 98.0,
        "current_atr": 1.0,
        "htf_fib": {"available": True, "levels": {0.5: 100.0}},
        "ltf_fib": {"available": True, "levels": {1.0: 120.0}},
    }
    decision_kwargs = {
        "policy": {"symbol": "tBTCUSD", "timeframe": "1h"},
        "probas": {"buy": 0.9, "sell": 0.1},
        "regime": "balanced",
        "risk_ctx": {},
        "cfg": cfg,
    }

    action_1, meta_1 = decide(
        confidence={"buy": 0.4, "sell": 0.1},
        state=deepcopy(state_base),
        **decision_kwargs,
    )
    state_1 = meta_1["state_out"]
    reasons_1 = meta_1["reasons"]
    override_debug_1 = state_1["ltf_override_debug"]

    assert action_1 == "NONE"
    assert "HTF_FIB_LONG_BLOCK" in reasons_1
    assert "HTF_OVERRIDE_LTF_CONF" not in reasons_1
    assert "ENTRY_LONG" not in reasons_1
    assert override_debug_1["history_len"] == 1
    assert override_debug_1["history_window"] == 2
    assert override_debug_1["effective_threshold"] == pytest.approx(0.95)
    assert len(state_1["ltf_override_state"]["buy_history"]) == 1

    action_2, meta_2 = decide(
        confidence={"buy": 0.7, "sell": 0.1},
        state={**deepcopy(state_base), "ltf_override_state": state_1["ltf_override_state"]},
        **decision_kwargs,
    )
    state_2 = meta_2["state_out"]
    reasons_2 = meta_2["reasons"]
    override_debug_2 = state_2["ltf_override_debug"]
    htf_debug_2 = state_2["htf_fib_entry_debug"]

    assert action_2 == "LONG"
    assert "HTF_OVERRIDE_LTF_CONF" in reasons_2
    assert "ENTRY_LONG" in reasons_2
    assert reasons_2.index("HTF_OVERRIDE_LTF_CONF") < reasons_2.index("ENTRY_LONG")
    assert override_debug_2["history_len"] == 2
    assert override_debug_2["history_window"] == 2
    assert override_debug_2["effective_threshold"] == pytest.approx(0.4)
    assert htf_debug_2["reason"] == "LONG_BELOW_LEVEL_OVERRIDE"
    assert htf_debug_2["override"]["source"] == "multi_timeframe_threshold"
    assert htf_debug_2["override"]["threshold"] == pytest.approx(0.4)
    assert len(state_2["ltf_override_state"]["buy_history"]) == 2
    assert state_2["ltf_override_state"]["buy_history"][-1] == pytest.approx(0.7)

    action_3, meta_3 = decide(
        confidence={"buy": 0.6, "sell": 0.1},
        state={**deepcopy(state_base), "ltf_override_state": state_2["ltf_override_state"]},
        **decision_kwargs,
    )
    state_3 = meta_3["state_out"]
    reasons_3 = meta_3["reasons"]
    override_debug_3 = state_3["ltf_override_debug"]

    assert action_3 == "LONG"
    assert "HTF_OVERRIDE_LTF_CONF" in reasons_3
    assert "ENTRY_LONG" in reasons_3
    assert reasons_3.index("HTF_OVERRIDE_LTF_CONF") < reasons_3.index("ENTRY_LONG")
    assert override_debug_3["history_len"] == 2
    assert override_debug_3["history_window"] == 2
    assert override_debug_3["effective_threshold"] == pytest.approx(0.6)
    assert len(state_3["ltf_override_state"]["buy_history"]) == 2
    assert state_3["ltf_override_state"]["buy_history"][-1] == pytest.approx(0.6)


def test_decide_ltf_entry_range_override_remains_static_across_history() -> None:
    cfg = {
        "ev": {"R_default": 1.0},
        "thresholds": {
            "entry_conf_overall": 0.6,
            "regime_proba": {"balanced": 0.55},
        },
        "gates": {"cooldown_bars": 0, "hysteresis_steps": 1},
        "risk": {"risk_map": [[0.55, 1.0]]},
        "multi_timeframe": {
            "allow_ltf_override": False,
            "ltf_override_threshold": 0.85,
            "ltf_override_adaptive": {
                "enabled": False,
                "window": 2,
                "min_history": 2,
                "percentile": 0.0,
                "fallback_threshold": 0.95,
            },
        },
        "htf_fib": {
            "entry": {
                "enabled": True,
                "long_min_level": 0.5,
                "tolerance_atr": 1.0,
            }
        },
        "ltf_fib": {
            "entry": {
                "enabled": True,
                "long_max_level": 1.0,
                "tolerance_atr": 1.0,
                "override_confidence": {
                    "enabled": True,
                    "min": 0.65,
                    "max": 0.75,
                },
            }
        },
    }
    state_base = {
        "last_close": 98.0,
        "current_atr": 1.0,
        "htf_fib": {"available": True, "levels": {0.5: 100.0}},
        "ltf_fib": {"available": True, "levels": {1.0: 120.0}},
    }
    decision_kwargs = {
        "policy": {"symbol": "tBTCUSD", "timeframe": "1h"},
        "probas": {"buy": 0.9, "sell": 0.1},
        "regime": "balanced",
        "risk_ctx": {},
        "cfg": cfg,
    }

    action_1, meta_1 = decide(
        confidence={"buy": 0.7, "sell": 0.1},
        state=deepcopy(state_base),
        **decision_kwargs,
    )
    state_1 = meta_1["state_out"]
    reasons_1 = meta_1["reasons"]
    override_debug_1 = state_1["ltf_override_debug"]
    htf_debug_1 = state_1["htf_fib_entry_debug"]

    assert action_1 == "LONG"
    assert "HTF_OVERRIDE_LTF_CONF" in reasons_1
    assert "ENTRY_LONG" in reasons_1
    assert reasons_1.index("HTF_OVERRIDE_LTF_CONF") < reasons_1.index("ENTRY_LONG")
    assert override_debug_1["effective_threshold"] == pytest.approx(0.85)
    assert htf_debug_1["override"]["source"] == "ltf_entry_range"

    action_2, meta_2 = decide(
        confidence={"buy": 0.6, "sell": 0.1},
        state={**deepcopy(state_base), "ltf_override_state": state_1["ltf_override_state"]},
        **decision_kwargs,
    )
    state_2 = meta_2["state_out"]
    reasons_2 = meta_2["reasons"]
    override_debug_2 = state_2["ltf_override_debug"]
    htf_debug_2 = state_2["htf_fib_entry_debug"]

    assert action_2 == "NONE"
    assert "HTF_FIB_LONG_BLOCK" in reasons_2
    assert "HTF_OVERRIDE_LTF_CONF" not in reasons_2
    assert override_debug_2["effective_threshold"] == pytest.approx(0.85)
    assert htf_debug_2["reason"] == "LONG_BELOW_LEVEL"
    assert "override" not in htf_debug_2

    action_3, meta_3 = decide(
        confidence={"buy": 0.7, "sell": 0.1},
        state={**deepcopy(state_base), "ltf_override_state": state_2["ltf_override_state"]},
        **decision_kwargs,
    )
    state_3 = meta_3["state_out"]
    reasons_3 = meta_3["reasons"]
    override_debug_3 = state_3["ltf_override_debug"]
    htf_debug_3 = state_3["htf_fib_entry_debug"]

    assert action_3 == "LONG"
    assert "HTF_OVERRIDE_LTF_CONF" in reasons_3
    assert "ENTRY_LONG" in reasons_3
    assert reasons_3.index("HTF_OVERRIDE_LTF_CONF") < reasons_3.index("ENTRY_LONG")
    assert override_debug_3["effective_threshold"] == pytest.approx(0.85)
    assert htf_debug_3["override"]["source"] == "ltf_entry_range"
    assert len(state_3["ltf_override_state"]["buy_history"]) == 2
    assert state_3["ltf_override_state"]["buy_history"][-1] == pytest.approx(0.7)


def test_decide_stacked_sizing_penalties_reduce_size_without_changing_entry_path() -> None:
    cfg = {
        "ev": {"R_default": 1.0},
        "thresholds": {
            "entry_conf_overall": 0.6,
            "regime_proba": {"bull": 0.6},
        },
        "gates": {"cooldown_bars": 0, "hysteresis_steps": 1},
        "risk": {
            "risk_map": [[0.6, 1.0]],
            "regime_size_multipliers": {"bull": 0.8},
            "htf_regime_size_multipliers": {"bear": 0.5},
            "min_combined_multiplier": 0.1,
        },
        "multi_timeframe": {
            "use_htf_block": False,
            "allow_ltf_override": False,
            "regime_intelligence": {
                "enabled": True,
                "version": "v2",
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
                        "soft_mult": 0.7,
                        "hard_mult": 0.4,
                    },
                    "transition_guard": {
                        "enabled": True,
                        "guard_bars": 3,
                        "mult": 0.6,
                    },
                },
            },
        },
        "htf_fib": {"entry": {"enabled": False}},
        "ltf_fib": {"entry": {"enabled": False}},
    }

    decision_kwargs = {
        "policy": {},
        "probas": {"buy": 0.8, "sell": 0.2},
        "confidence": {"buy": 0.8, "sell": 0.2},
        "regime": "bull",
        "risk_ctx": {},
        "cfg": cfg,
    }

    action_base, meta_base = decide(
        htf_regime="bull",
        state={
            "equity_drawdown_pct": 0.0,
            "bars_since_regime_change": 10,
            "last_regime": "bull",
        },
        **decision_kwargs,
    )
    action_constrained, meta_constrained = decide(
        htf_regime="bear",
        state={
            "equity_drawdown_pct": 0.03,
            "bars_since_regime_change": 2,
            "last_regime": "bull",
        },
        **decision_kwargs,
    )

    assert action_base == action_constrained == "LONG"
    assert meta_base["reasons"][-1] == "ENTRY_LONG"
    assert meta_constrained["reasons"][-1] == "ENTRY_LONG"
    assert float(meta_constrained["size"]) < float(meta_base["size"])

    state_out_base = meta_base["state_out"]
    state_out_constrained = meta_constrained["state_out"]

    assert state_out_base["size_regime_mult"] == pytest.approx(0.8)
    assert state_out_base["size_htf_regime_mult"] == pytest.approx(1.0)
    assert state_out_base["ri_risk_state_multiplier"] == pytest.approx(1.0)
    assert state_out_base["ri_clarity_multiplier"] == pytest.approx(0.5)

    assert state_out_constrained["size_regime_mult"] == pytest.approx(0.8)
    assert state_out_constrained["size_htf_regime_mult"] == pytest.approx(0.5)
    assert state_out_constrained["ri_risk_state_multiplier"] == pytest.approx(0.42)
    assert state_out_constrained["ri_clarity_multiplier"] == pytest.approx(0.5)
    assert (
        state_out_constrained["size_before_ri_clarity"] < state_out_base["size_before_ri_clarity"]
    )
