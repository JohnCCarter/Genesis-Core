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


def test_decide_research_bull_high_persistence_override_flips_second_near_miss_only() -> None:
    cfg = {
        "ev": {"R_default": 1.0},
        "thresholds": {
            "entry_conf_overall": 0.6,
            "signal_adaptation": {
                "atr_period": 28,
                "zones": {"high": {"entry_conf_overall": 0.36, "regime_proba": 0.56}},
            },
        },
        "gates": {"cooldown_bars": 0, "hysteresis_steps": 1},
        "risk": {"risk_map": [[0.36, 1.0]]},
        "multi_timeframe": {
            "research_bull_high_persistence_override": {
                "enabled": True,
                "min_persistence": 2,
                "max_probability_gap": 0.06,
            }
        },
    }
    state_base = {
        "current_atr": 4.0,
        "atr_percentiles": {"28": {"p40": 1.0, "p80": 3.0}},
    }

    action_1, meta_1 = decide(
        {},
        probas={"buy": 0.52, "sell": 0.48},
        confidence={"buy": 0.52, "sell": 0.48},
        regime="bull",
        state=state_base,
        risk_ctx={},
        cfg=cfg,
    )

    assert action_1 == "NONE"
    assert meta_1["reasons"] == ["ZONE:high@0.360"]
    assert meta_1["state_out"]["research_bull_high_persistence_state"] == {"near_miss_streak": 1}
    assert "research_bull_high_persistence_debug" not in meta_1["state_out"]

    action_2, meta_2 = decide(
        {},
        probas={"buy": 0.521, "sell": 0.479},
        confidence={"buy": 0.521, "sell": 0.479},
        regime="bull",
        state={**state_base, **meta_1["state_out"]},
        risk_ctx={},
        cfg=cfg,
    )

    assert action_2 == "LONG"
    assert meta_2["reasons"] == [
        "ZONE:high@0.360",
        "RESEARCH_BULL_HIGH_PERSISTENCE_OVERRIDE",
        "ENTRY_LONG",
    ]
    assert float(meta_2["size"]) == pytest.approx(1.0)
    assert meta_2["state_out"]["research_bull_high_persistence_state"] == {"near_miss_streak": 2}
    assert meta_2["state_out"]["research_bull_high_persistence_debug"]["applied"] is True
    assert (
        meta_2["state_out"]["research_bull_high_persistence_debug"]["reason"]
        == "RESEARCH_BULL_HIGH_PERSISTENCE_OVERRIDE"
    )


def test_decide_research_bull_high_persistence_override_enabled_but_unmet_preserves_action_path() -> (
    None
):
    cfg = {
        "ev": {"R_default": 1.0},
        "thresholds": {
            "entry_conf_overall": 0.6,
            "signal_adaptation": {
                "atr_period": 28,
                "zones": {"high": {"entry_conf_overall": 0.36, "regime_proba": 0.56}},
            },
        },
        "gates": {"cooldown_bars": 0, "hysteresis_steps": 1},
        "risk": {"risk_map": [[0.36, 1.0]]},
        "multi_timeframe": {
            "research_bull_high_persistence_override": {
                "enabled": True,
                "min_persistence": 2,
                "max_probability_gap": 0.01,
            }
        },
    }
    state = {
        "current_atr": 4.0,
        "atr_percentiles": {"28": {"p40": 1.0, "p80": 3.0}},
    }

    action, meta = decide(
        {},
        probas={"buy": 0.52, "sell": 0.48},
        confidence={"buy": 0.52, "sell": 0.48},
        regime="bull",
        state=state,
        risk_ctx={},
        cfg=cfg,
    )

    assert action == "NONE"
    assert meta["reasons"] == ["ZONE:high@0.360"]
    assert "research_bull_high_persistence_state" not in meta["state_out"]
    assert "research_bull_high_persistence_debug" not in meta["state_out"]


def test_decide_research_bull_high_persistence_min_size_base_zero_preserves_enabled_path() -> None:
    cfg_base = {
        "ev": {"R_default": 1.0},
        "thresholds": {
            "entry_conf_overall": 0.6,
            "signal_adaptation": {
                "atr_period": 28,
                "zones": {"high": {"entry_conf_overall": 0.36, "regime_proba": 0.56}},
            },
        },
        "gates": {"cooldown_bars": 0, "hysteresis_steps": 1},
        "risk": {"risk_map": [[0.6, 1.0]]},
        "multi_timeframe": {
            "research_bull_high_persistence_override": {
                "enabled": True,
                "min_persistence": 2,
                "max_probability_gap": 0.06,
            }
        },
    }
    cfg_zero = deepcopy(cfg_base)
    cfg_zero["multi_timeframe"]["research_bull_high_persistence_override"]["min_size_base"] = 0.0
    state_base = {
        "current_atr": 4.0,
        "atr_percentiles": {"28": {"p40": 1.0, "p80": 3.0}},
    }

    _, meta_base_1 = decide(
        {},
        probas={"buy": 0.52, "sell": 0.48},
        confidence={"buy": 0.52, "sell": 0.48},
        regime="bull",
        state=state_base,
        risk_ctx={},
        cfg=cfg_base,
    )
    _, meta_zero_1 = decide(
        {},
        probas={"buy": 0.52, "sell": 0.48},
        confidence={"buy": 0.52, "sell": 0.48},
        regime="bull",
        state=state_base,
        risk_ctx={},
        cfg=cfg_zero,
    )

    action_base_2, meta_base_2 = decide(
        {},
        probas={"buy": 0.521, "sell": 0.479},
        confidence={"buy": 0.521, "sell": 0.479},
        regime="bull",
        state={**state_base, **meta_base_1["state_out"]},
        risk_ctx={},
        cfg=cfg_base,
    )
    action_zero_2, meta_zero_2 = decide(
        {},
        probas={"buy": 0.521, "sell": 0.479},
        confidence={"buy": 0.521, "sell": 0.479},
        regime="bull",
        state={**state_base, **meta_zero_1["state_out"]},
        risk_ctx={},
        cfg=cfg_zero,
    )

    assert action_base_2 == action_zero_2 == "LONG"
    assert float(meta_base_2["size"]) == pytest.approx(0.0)
    assert float(meta_zero_2["size"]) == pytest.approx(0.0)
    assert meta_base_2["reasons"] == meta_zero_2["reasons"]
    assert meta_base_2["state_out"] == meta_zero_2["state_out"]


def test_decide_research_bull_high_persistence_non_penalized_leaf_false_matches_absent() -> None:
    cfg_base = {
        "ev": {"R_default": 1.0},
        "thresholds": {
            "entry_conf_overall": 0.6,
            "signal_adaptation": {
                "atr_period": 28,
                "zones": {"high": {"entry_conf_overall": 0.36, "regime_proba": 0.56}},
            },
        },
        "gates": {"cooldown_bars": 0, "hysteresis_steps": 1},
        "risk": {"risk_map": [[0.6, 1.0]]},
        "multi_timeframe": {
            "research_bull_high_persistence_override": {
                "enabled": True,
                "min_persistence": 2,
                "max_probability_gap": 0.06,
                "min_size_base": 0.02,
            }
        },
    }
    cfg_false = deepcopy(cfg_base)
    cfg_false["multi_timeframe"]["research_bull_high_persistence_override"][
        "require_non_penalized_volatility_for_min_size_base"
    ] = False
    state_base = {
        "current_atr": 4.0,
        "atr_percentiles": {"28": {"p40": 1.0, "p80": 3.0}},
    }

    _, meta_base_1 = decide(
        {},
        probas={"buy": 0.52, "sell": 0.48},
        confidence={"buy": 0.52, "sell": 0.48},
        regime="bull",
        state=state_base,
        risk_ctx={},
        cfg=cfg_base,
    )
    _, meta_false_1 = decide(
        {},
        probas={"buy": 0.52, "sell": 0.48},
        confidence={"buy": 0.52, "sell": 0.48},
        regime="bull",
        state=state_base,
        risk_ctx={},
        cfg=cfg_false,
    )

    action_base_2, meta_base_2 = decide(
        {},
        probas={"buy": 0.521, "sell": 0.479},
        confidence={"buy": 0.521, "sell": 0.479},
        regime="bull",
        state={**state_base, **meta_base_1["state_out"]},
        risk_ctx={},
        cfg=cfg_base,
    )
    action_false_2, meta_false_2 = decide(
        {},
        probas={"buy": 0.521, "sell": 0.479},
        confidence={"buy": 0.521, "sell": 0.479},
        regime="bull",
        state={**state_base, **meta_false_1["state_out"]},
        risk_ctx={},
        cfg=cfg_false,
    )

    assert action_base_2 == action_false_2 == "LONG"
    assert float(meta_base_2["size"]) == pytest.approx(0.02)
    assert float(meta_false_2["size"]) == pytest.approx(0.02)
    assert meta_base_2["reasons"] == meta_false_2["reasons"]
    assert meta_base_2["state_out"] == meta_false_2["state_out"]


def test_decide_research_bull_high_persistence_min_size_base_only_affects_override_bar() -> None:
    cfg = {
        "ev": {"R_default": 1.0},
        "thresholds": {
            "entry_conf_overall": 0.3,
            "regime_proba": {"bull": 0.3},
        },
        "gates": {"cooldown_bars": 0, "hysteresis_steps": 1},
        "risk": {"risk_map": [[0.6, 1.0]]},
        "multi_timeframe": {
            "research_bull_high_persistence_override": {
                "enabled": True,
                "min_persistence": 2,
                "max_probability_gap": 0.06,
                "min_size_base": 0.02,
            }
        },
    }

    action, meta = decide(
        {},
        probas={"buy": 0.52, "sell": 0.48},
        confidence={"buy": 0.52, "sell": 0.48},
        regime="bull",
        state={},
        risk_ctx={},
        cfg=cfg,
    )

    assert action == "LONG"
    assert meta["reasons"] == ["ZONE:base@0.300", "ENTRY_LONG"]
    assert float(meta["size"]) == pytest.approx(0.0)
    assert "research_bull_high_persistence_size_override" not in meta["state_out"]


def test_decide_research_bull_high_persistence_min_size_base_enables_small_entry() -> None:
    cfg = {
        "ev": {"R_default": 1.0},
        "thresholds": {
            "entry_conf_overall": 0.6,
            "signal_adaptation": {
                "atr_period": 28,
                "zones": {"high": {"entry_conf_overall": 0.36, "regime_proba": 0.56}},
            },
        },
        "gates": {"cooldown_bars": 0, "hysteresis_steps": 1},
        "risk": {"risk_map": [[0.6, 1.0]]},
        "multi_timeframe": {
            "research_bull_high_persistence_override": {
                "enabled": True,
                "min_persistence": 2,
                "max_probability_gap": 0.06,
                "min_size_base": 0.02,
            }
        },
    }
    state_base = {
        "current_atr": 4.0,
        "atr_percentiles": {"28": {"p40": 1.0, "p80": 3.0}},
    }

    action_1, meta_1 = decide(
        {},
        probas={"buy": 0.52, "sell": 0.48},
        confidence={"buy": 0.52, "sell": 0.48},
        regime="bull",
        state=state_base,
        risk_ctx={},
        cfg=cfg,
    )

    assert action_1 == "NONE"

    action_2, meta_2 = decide(
        {},
        probas={"buy": 0.521, "sell": 0.479},
        confidence={"buy": 0.521, "sell": 0.479},
        regime="bull",
        state={**state_base, **meta_1["state_out"]},
        risk_ctx={},
        cfg=cfg,
    )

    assert action_2 == "LONG"
    assert meta_2["reasons"] == [
        "ZONE:high@0.360",
        "RESEARCH_BULL_HIGH_PERSISTENCE_OVERRIDE",
        "ENTRY_LONG",
    ]
    assert float(meta_2["size"]) == pytest.approx(0.02)
    assert meta_2["state_out"]["research_bull_high_persistence_size_override"] == {
        "applied": True,
        "reason": "RESEARCH_BULL_HIGH_PERSISTENCE_OVERRIDE",
        "size_base_before": 0.0,
        "size_base_after": 0.02,
    }


def test_decide_research_bull_high_persistence_non_penalized_leaf_blocks_penalized_bar() -> None:
    cfg = {
        "ev": {"R_default": 1.0},
        "thresholds": {
            "entry_conf_overall": 0.6,
            "signal_adaptation": {
                "atr_period": 28,
                "zones": {"high": {"entry_conf_overall": 0.36, "regime_proba": 0.56}},
            },
        },
        "gates": {"cooldown_bars": 0, "hysteresis_steps": 1},
        "risk": {
            "risk_map": [[0.6, 1.0]],
            "volatility_sizing": {
                "enabled": True,
                "high_vol_threshold": 80,
                "high_vol_multiplier": 0.7,
                "atr_period": 14,
            },
        },
        "multi_timeframe": {
            "research_bull_high_persistence_override": {
                "enabled": True,
                "min_persistence": 2,
                "max_probability_gap": 0.06,
                "min_size_base": 0.02,
                "require_non_penalized_volatility_for_min_size_base": True,
            }
        },
    }
    state_base = {
        "current_atr": 4.0,
        "atr_percentiles": {
            "14": {"p40": 1.0, "p80": 3.0},
            "28": {"p40": 1.0, "p80": 3.0},
        },
    }

    action_1, meta_1 = decide(
        {},
        probas={"buy": 0.52, "sell": 0.48},
        confidence={"buy": 0.52, "sell": 0.48},
        regime="bull",
        state=state_base,
        risk_ctx={},
        cfg=cfg,
    )

    assert action_1 == "NONE"

    action_2, meta_2 = decide(
        {},
        probas={"buy": 0.521, "sell": 0.479},
        confidence={"buy": 0.521, "sell": 0.479},
        regime="bull",
        state={**state_base, **meta_1["state_out"]},
        risk_ctx={},
        cfg=cfg,
    )

    assert action_2 == "LONG"
    assert float(meta_2["size"]) == pytest.approx(0.0)
    assert meta_2["state_out"]["size_vol_mult"] == pytest.approx(0.7)
    assert "research_bull_high_persistence_size_override" not in meta_2["state_out"]


def test_decide_research_bull_high_persistence_non_penalized_leaf_allows_non_penalized_bar() -> (
    None
):
    cfg = {
        "ev": {"R_default": 1.0},
        "thresholds": {
            "entry_conf_overall": 0.6,
            "signal_adaptation": {
                "atr_period": 28,
                "zones": {"high": {"entry_conf_overall": 0.36, "regime_proba": 0.56}},
            },
        },
        "gates": {"cooldown_bars": 0, "hysteresis_steps": 1},
        "risk": {
            "risk_map": [[0.6, 1.0]],
            "volatility_sizing": {
                "enabled": True,
                "high_vol_threshold": 80,
                "high_vol_multiplier": 0.7,
                "atr_period": 14,
            },
        },
        "multi_timeframe": {
            "research_bull_high_persistence_override": {
                "enabled": True,
                "min_persistence": 2,
                "max_probability_gap": 0.06,
                "min_size_base": 0.02,
                "require_non_penalized_volatility_for_min_size_base": True,
            }
        },
    }
    state_base = {
        "current_atr": 4.0,
        "atr_percentiles": {
            "14": {"p40": 1.0, "p80": 5.0},
            "28": {"p40": 1.0, "p80": 3.0},
        },
    }

    action_1, meta_1 = decide(
        {},
        probas={"buy": 0.52, "sell": 0.48},
        confidence={"buy": 0.52, "sell": 0.48},
        regime="bull",
        state=state_base,
        risk_ctx={},
        cfg=cfg,
    )

    assert action_1 == "NONE"

    action_2, meta_2 = decide(
        {},
        probas={"buy": 0.521, "sell": 0.479},
        confidence={"buy": 0.521, "sell": 0.479},
        regime="bull",
        state={**state_base, **meta_1["state_out"]},
        risk_ctx={},
        cfg=cfg,
    )

    assert action_2 == "LONG"
    assert float(meta_2["size"]) == pytest.approx(0.02)
    assert meta_2["state_out"]["size_vol_mult"] == pytest.approx(1.0)
    assert meta_2["state_out"]["research_bull_high_persistence_size_override"] == {
        "applied": True,
        "reason": "RESEARCH_BULL_HIGH_PERSISTENCE_OVERRIDE",
        "size_base_before": 0.0,
        "size_base_after": 0.02,
    }


def test_decide_current_atr_selective_high_vol_multiplier_increases_size_on_eligible_bar() -> None:
    cfg_base = {
        "ev": {"R_default": 1.0},
        "thresholds": {
            "entry_conf_overall": 0.6,
            "regime_proba": {"bull": 0.6},
        },
        "gates": {"cooldown_bars": 0, "hysteresis_steps": 1},
        "risk": {
            "risk_map": [[0.6, 0.01]],
            "volatility_sizing": {
                "enabled": True,
                "high_vol_threshold": 80,
                "high_vol_multiplier": 0.9,
                "atr_period": 14,
            },
            "min_combined_multiplier": 0.01,
        },
    }
    cfg_selective = deepcopy(cfg_base)
    cfg_selective["multi_timeframe"] = {
        "research_current_atr_high_vol_multiplier_override": {
            "enabled": True,
            "current_atr_threshold": 4.0,
            "high_vol_multiplier_override": 1.0,
        }
    }
    state = {
        "current_atr": 4.0,
        "atr_percentiles": {"14": {"p80": 3.0}},
    }

    action_base, meta_base = decide(
        {},
        probas={"buy": 0.6, "sell": 0.4},
        confidence={"buy": 0.6, "sell": 0.4},
        regime="bull",
        state=state,
        risk_ctx={},
        cfg=cfg_base,
    )
    action_selective, meta_selective = decide(
        {},
        probas={"buy": 0.6, "sell": 0.4},
        confidence={"buy": 0.6, "sell": 0.4},
        regime="bull",
        state=state,
        risk_ctx={},
        cfg=cfg_selective,
    )

    assert action_base == action_selective == "LONG"
    assert meta_base["reasons"] == meta_selective["reasons"] == ["ZONE:base@0.600", "ENTRY_LONG"]
    assert float(meta_base["size"]) == pytest.approx(0.009)
    assert float(meta_selective["size"]) == pytest.approx(0.01)
    assert meta_base["state_out"]["size_vol_mult"] == pytest.approx(0.9)
    assert meta_selective["state_out"]["size_vol_mult"] == pytest.approx(1.0)
    assert meta_selective["state_out"]["current_atr_selective_high_vol_multiplier_override"] == {
        "applied": True,
        "current_atr": 4.0,
        "current_atr_threshold": 4.0,
        "high_vol_multiplier_before": 0.9,
        "high_vol_multiplier_after": 1.0,
    }


def test_decide_research_defensive_transition_override_flips_fresh_high_zone_near_miss_only() -> (
    None
):
    cfg = {
        "ev": {"R_default": 1.0},
        "thresholds": {
            "entry_conf_overall": 0.6,
            "signal_adaptation": {
                "atr_period": 28,
                "zones": {"high": {"entry_conf_overall": 0.36, "regime_proba": 0.56}},
            },
        },
        "gates": {"cooldown_bars": 0, "hysteresis_steps": 1},
        "risk": {"risk_map": [[0.36, 1.0]]},
        "multi_timeframe": {
            "research_defensive_transition_override": {
                "enabled": True,
                "guard_bars": 3,
                "max_probability_gap": 0.05,
            }
        },
    }
    state_base = {
        "current_atr": 4.0,
        "atr_percentiles": {"28": {"p40": 1.0, "p80": 3.0}},
    }

    action_fresh, meta_fresh = decide(
        {},
        probas={"buy": 0.52, "sell": 0.48},
        confidence={"buy": 0.52, "sell": 0.48},
        regime="bull",
        state={**state_base, "bars_since_regime_change": 2},
        risk_ctx={},
        cfg=cfg,
    )
    action_stale, meta_stale = decide(
        {},
        probas={"buy": 0.52, "sell": 0.48},
        confidence={"buy": 0.52, "sell": 0.48},
        regime="bull",
        state={**state_base, "bars_since_regime_change": 5},
        risk_ctx={},
        cfg=cfg,
    )

    assert action_fresh == "LONG"
    assert meta_fresh["reasons"] == [
        "ZONE:high@0.360",
        "RESEARCH_DEFENSIVE_TRANSITION_OVERRIDE",
        "ENTRY_LONG",
    ]
    assert float(meta_fresh["size"]) == pytest.approx(1.0)
    assert meta_fresh["state_out"]["research_defensive_transition_debug"] == {
        "applied": True,
        "reason": "RESEARCH_DEFENSIVE_TRANSITION_OVERRIDE",
        "candidate": "LONG",
        "bars_since_regime_change": 2,
        "guard_bars": 3,
        "max_probability_gap": 0.05,
        "threshold": 0.56,
        "threshold_gap": pytest.approx(0.04),
        "buy": 0.52,
        "sell": 0.48,
        "regime": "bull",
        "zone": "high",
    }

    assert action_stale == "NONE"
    assert meta_stale["reasons"] == ["ZONE:high@0.360"]
    assert "research_defensive_transition_debug" not in meta_stale["state_out"]


def test_decide_enabled_policy_router_selects_defensive_and_reduces_size() -> None:
    cfg = deepcopy(_BASE_CFG)
    cfg["thresholds"] = {
        "entry_conf_overall": 0.3,
        "regime_proba": {"bull": 0.5},
    }
    cfg["risk"] = {"risk_map": [[0.3, 1.0]], "min_combined_multiplier": 0.1}
    cfg["multi_timeframe"] = {
        "use_htf_block": False,
        "allow_ltf_override": False,
        "research_policy_router": {
            "enabled": True,
            "switch_threshold": 2,
            "hysteresis": 1,
            "min_dwell": 3,
            "defensive_size_multiplier": 0.5,
        },
    }
    cfg["htf_fib"] = {"entry": {"enabled": False}}
    cfg["ltf_fib"] = {"entry": {"enabled": False}}

    action, meta = decide(
        cfg=cfg,
        state={"bars_since_regime_change": 2, "last_regime": "bull"},
        probas={"buy": 0.52, "sell": 0.48},
        confidence={"buy": 0.52, "sell": 0.48},
        regime="bull",
        risk_ctx={},
        policy={},
    )

    assert action == "LONG"
    assert meta["reasons"][-1] == "ENTRY_LONG"
    assert "RESEARCH_POLICY_ROUTER_DEFENSIVE" in meta["reasons"]
    assert float(meta["size"]) == pytest.approx(0.5)
    assert meta["versions"]["ri_policy_router"] == "ri_policy_router_v1"

    state_out = meta["state_out"]
    assert (
        state_out["research_policy_router_state"]["selected_policy"]
        == "RI_defensive_transition_policy"
    )
    assert (
        state_out["research_policy_router_debug"]["switch_reason"] == "transition_pressure_detected"
    )
    assert state_out["research_policy_router_debug"]["size_multiplier"] == pytest.approx(0.5)


def test_decide_enabled_policy_router_can_force_no_trade_before_sizing() -> None:
    cfg = deepcopy(_BASE_CFG)
    cfg["thresholds"] = {
        "entry_conf_overall": 0.3,
        "regime_proba": {"bull": 0.5},
    }
    cfg["risk"] = {"risk_map": [[0.3, 1.0]], "min_combined_multiplier": 0.1}
    cfg["multi_timeframe"] = {
        "use_htf_block": False,
        "allow_ltf_override": False,
        "research_policy_router": {
            "enabled": True,
            "switch_threshold": 2,
            "hysteresis": 1,
            "min_dwell": 3,
            "defensive_size_multiplier": 0.5,
        },
    }
    cfg["htf_fib"] = {"entry": {"enabled": False}}
    cfg["ltf_fib"] = {"entry": {"enabled": False}}

    action, meta = decide(
        cfg=cfg,
        state={"bars_since_regime_change": 2, "last_regime": "bull"},
        probas={"buy": 0.51, "sell": 0.49},
        confidence={"buy": 0.51, "sell": 0.49},
        regime="bull",
        risk_ctx={},
        policy={},
    )

    assert action == "NONE"
    assert "RESEARCH_POLICY_ROUTER_NO_TRADE" in meta["reasons"]
    assert "ENTRY_LONG" not in meta["reasons"]
    assert "size" not in meta

    state_out = meta["state_out"]
    assert state_out["research_policy_router_state"]["selected_policy"] == "RI_no_trade_policy"
    assert state_out["research_policy_router_debug"]["switch_reason"] == "insufficient_evidence"


def test_decide_enabled_policy_router_blocks_only_aged_weak_continuation() -> None:
    cfg = deepcopy(_BASE_CFG)
    cfg["thresholds"] = {
        "entry_conf_overall": 0.3,
        "regime_proba": {"bull": 0.5},
    }
    cfg["risk"] = {"risk_map": [[0.3, 1.0]], "min_combined_multiplier": 0.1}
    cfg["multi_timeframe"] = {
        "use_htf_block": False,
        "allow_ltf_override": False,
        "research_policy_router": {
            "enabled": True,
            "switch_threshold": 2,
            "hysteresis": 1,
            "min_dwell": 3,
            "defensive_size_multiplier": 0.5,
        },
    }
    cfg["htf_fib"] = {"entry": {"enabled": False}}
    cfg["ltf_fib"] = {"entry": {"enabled": False}}

    common_kwargs = {
        "cfg": cfg,
        "probas": {"buy": 0.535, "sell": 0.465},
        "confidence": {"buy": 0.53, "sell": 0.47},
        "regime": "bear",
        "risk_ctx": {},
        "policy": {},
    }

    action_fresh, meta_fresh = decide(
        state={"bars_since_regime_change": 10, "last_regime": "bear"},
        **common_kwargs,
    )
    action_aged, meta_aged = decide(
        state={"bars_since_regime_change": 16, "last_regime": "bear"},
        **common_kwargs,
    )

    assert action_fresh == "LONG"
    assert "RESEARCH_POLICY_ROUTER_CONTINUATION" in meta_fresh["reasons"]
    assert meta_fresh["reasons"][-1] == "ENTRY_LONG"
    assert meta_fresh["state_out"]["research_policy_router_debug"]["switch_reason"] == (
        "continuation_state_supported"
    )

    assert action_aged == "NONE"
    assert "RESEARCH_POLICY_ROUTER_NO_TRADE" in meta_aged["reasons"]
    assert "ENTRY_LONG" not in meta_aged["reasons"]
    assert "size" not in meta_aged
    assert meta_aged["state_out"]["research_policy_router_state"]["selected_policy"] == (
        "RI_no_trade_policy"
    )
    assert meta_aged["state_out"]["research_policy_router_debug"]["switch_reason"] == (
        "AGED_WEAK_CONTINUATION_GUARD"
    )


def test_decide_enabled_policy_router_blocks_weak_pre_aged_release_from_no_trade() -> None:
    cfg = deepcopy(_BASE_CFG)
    cfg["thresholds"] = {
        "entry_conf_overall": 0.3,
        "regime_proba": {"bull": 0.5},
    }
    cfg["risk"] = {"risk_map": [[0.3, 1.0]], "min_combined_multiplier": 0.1}
    cfg["multi_timeframe"] = {
        "use_htf_block": False,
        "allow_ltf_override": False,
        "research_policy_router": {
            "enabled": True,
            "switch_threshold": 2,
            "hysteresis": 1,
            "min_dwell": 3,
            "defensive_size_multiplier": 0.5,
        },
    }
    cfg["htf_fib"] = {"entry": {"enabled": False}}
    cfg["ltf_fib"] = {"entry": {"enabled": False}}

    common_kwargs = {
        "cfg": cfg,
        "probas": {"buy": 0.54, "sell": 0.46},
        "confidence": {"buy": 0.54, "sell": 0.46},
        "regime": "bear",
        "risk_ctx": {},
        "policy": {},
    }

    no_trade_state = {
        "research_policy_router_state": {
            "selected_policy": "RI_no_trade_policy",
            "mandate_level": 0,
            "confidence": 0,
            "dwell_duration": 3,
        },
        "last_regime": "bear",
    }

    action_blocked, meta_blocked = decide(
        state={**no_trade_state, "bars_since_regime_change": 7},
        **common_kwargs,
    )
    action_release, meta_release = decide(
        state={**no_trade_state, "bars_since_regime_change": 8},
        **common_kwargs,
    )

    assert action_blocked == "NONE"
    assert "RESEARCH_POLICY_ROUTER_NO_TRADE" in meta_blocked["reasons"]
    assert "ENTRY_LONG" not in meta_blocked["reasons"]
    assert "size" not in meta_blocked
    assert meta_blocked["state_out"]["research_policy_router_state"]["selected_policy"] == (
        "RI_no_trade_policy"
    )
    assert meta_blocked["state_out"]["research_policy_router_debug"]["switch_reason"] == (
        "WEAK_PRE_AGED_CONTINUATION_RELEASE_GUARD"
    )

    assert action_release == "LONG"
    assert "RESEARCH_POLICY_ROUTER_CONTINUATION" in meta_release["reasons"]
    assert meta_release["reasons"][-1] == "ENTRY_LONG"
    assert meta_release["state_out"]["research_policy_router_state"]["selected_policy"] == (
        "RI_continuation_policy"
    )
    assert meta_release["state_out"]["research_policy_router_debug"]["switch_reason"] == (
        "stable_continuation_state"
    )
