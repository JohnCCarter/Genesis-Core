from __future__ import annotations

import pytest

from core.strategy.decision_gates import apply_post_fib_gates, select_candidate


def _noop_log(*_args, **_kwargs) -> None:
    return None


@pytest.mark.parametrize(
    ("regime", "state_in", "expected_candidate", "expected_reason"),
    [
        ("balanced", {"last_action": "SHORT"}, "SHORT", None),
        ("trend", {}, "LONG", None),
        ("bull", {}, "LONG", None),
        ("bear", {}, "SHORT", None),
        ("balanced", {}, None, "P_TIE_BREAK"),
    ],
    ids=[
        "tie_reuses_last_action",
        "tie_trend_defaults_long",
        "tie_bull_defaults_long",
        "tie_bear_defaults_short",
        "tie_balanced_blocks_with_reason",
    ],
)
def test_select_candidate_tie_handling_contract(
    regime: str,
    state_in: dict[str, object],
    expected_candidate: str | None,
    expected_reason: str | None,
) -> None:
    reasons: list[str] = []
    state_out: dict[str, object] = {}

    action, meta, candidate_data = select_candidate(
        policy={},
        probas={"buy": 0.7, "sell": 0.7},
        regime=regime,
        risk_ctx={},
        cfg={
            "ev": {"R_default": 2.0},
            "thresholds": {"entry_conf_overall": 0.6, "regime_proba": {regime: 0.6}},
        },
        state_in=state_in,
        state_out=state_out,
        reasons=reasons,
        versions={"decision": "v1"},
        log_decision_event=_noop_log,
    )

    if expected_reason is None:
        assert action is None
        assert meta is None
        assert candidate_data["candidate"] == expected_candidate
        assert candidate_data["p_buy"] == pytest.approx(0.7)
        assert candidate_data["p_sell"] == pytest.approx(0.7)
        assert candidate_data["max_ev"] == pytest.approx(0.7)
        assert reasons == ["ZONE:base@0.600"]
    else:
        assert action == "NONE"
        assert meta is not None
        assert candidate_data == {}
        assert reasons == ["ZONE:base@0.600", expected_reason]
        assert meta["reasons"] == reasons
        assert meta["state_out"] == state_out


@pytest.mark.parametrize(
    ("probas", "risk_ctx", "expected_reason"),
    [
        (None, {}, "FAIL_SAFE_NULL"),
        ({"buy": 0.8, "sell": 0.2}, {"event_block": True}, "R_EVENT_BLOCK"),
        ({"buy": 0.8, "sell": 0.2}, {"risk_cap_breached": True}, "RISK_CAP"),
    ],
    ids=["null_probas_fail_safe", "event_block_precedes_thresholds", "risk_cap_blocks"],
)
def test_select_candidate_fail_safe_and_blockers(
    probas: dict[str, float] | None,
    risk_ctx: dict[str, object],
    expected_reason: str,
) -> None:
    reasons: list[str] = []
    state_out: dict[str, object] = {}

    action, meta, candidate_data = select_candidate(
        policy={},
        probas=probas,
        regime="balanced",
        risk_ctx=risk_ctx,
        cfg={"ev": {"R_default": 1.0}, "thresholds": {"entry_conf_overall": 0.6}},
        state_in={},
        state_out=state_out,
        reasons=reasons,
        versions={"decision": "v1"},
        log_decision_event=_noop_log,
    )

    assert action == "NONE"
    assert meta is not None
    assert candidate_data == {}
    assert reasons == [expected_reason]
    assert meta["reasons"] == reasons
    assert meta["state_out"] == state_out


def test_apply_post_fib_gates_hysteresis_blocks_and_increments_state() -> None:
    reasons: list[str] = []
    state_out: dict[str, object] = {}

    action, meta, confidence_data = apply_post_fib_gates(
        candidate="LONG",
        confidence={"buy": 0.8, "sell": 0.1},
        cfg={"gates": {"hysteresis_steps": 2, "cooldown_bars": 0}},
        state_in={"last_action": "SHORT", "decision_steps": 0},
        state_out=state_out,
        reasons=reasons,
        versions={"decision": "v1"},
        default_thr=0.6,
        p_buy=0.8,
        p_sell=0.1,
        log_decision_event=_noop_log,
    )

    assert action == "NONE"
    assert meta is not None
    assert confidence_data == {}
    assert reasons == ["HYST_WAIT"]
    assert state_out["decision_steps"] == 1
    assert meta["reasons"] == reasons
    assert meta["state_out"] == state_out


def test_apply_post_fib_gates_cooldown_blocks_and_decrements_state() -> None:
    reasons: list[str] = []
    state_out: dict[str, object] = {}

    action, meta, confidence_data = apply_post_fib_gates(
        candidate="LONG",
        confidence={"buy": 0.8, "sell": 0.1},
        cfg={"gates": {"hysteresis_steps": 2, "cooldown_bars": 0}},
        state_in={"last_action": "LONG", "decision_steps": 4, "cooldown_remaining": 3},
        state_out=state_out,
        reasons=reasons,
        versions={"decision": "v1"},
        default_thr=0.6,
        p_buy=0.8,
        p_sell=0.1,
        log_decision_event=_noop_log,
    )

    assert action == "NONE"
    assert meta is not None
    assert confidence_data == {}
    assert reasons == ["COOLDOWN_ACTIVE"]
    assert state_out["decision_steps"] == 0
    assert state_out["cooldown_remaining"] == 2
    assert meta["reasons"] == reasons
    assert meta["state_out"] == state_out


def test_apply_post_fib_gates_success_exports_selected_confidence() -> None:
    reasons: list[str] = []
    state_out: dict[str, object] = {}

    action, meta, confidence_data = apply_post_fib_gates(
        candidate="SHORT",
        confidence={"buy": 0.1, "sell": 0.75},
        cfg={"gates": {"hysteresis_steps": 2, "cooldown_bars": 0}},
        state_in={"last_action": "SHORT", "decision_steps": 5, "cooldown_remaining": 0},
        state_out=state_out,
        reasons=reasons,
        versions={"decision": "v1"},
        default_thr=0.6,
        p_buy=0.1,
        p_sell=0.75,
        log_decision_event=_noop_log,
    )

    assert action is None
    assert meta is None
    assert reasons == []
    assert state_out["decision_steps"] == 0
    assert confidence_data["c_buy"] == pytest.approx(0.1)
    assert confidence_data["c_sell"] == pytest.approx(0.75)
    assert confidence_data["conf_val_gate"] == pytest.approx(0.75)


def test_select_candidate_research_bull_high_persistence_override_is_default_off() -> None:
    reasons: list[str] = []
    state_out: dict[str, object] = {}

    action, meta, candidate_data = select_candidate(
        policy={},
        probas={"buy": 0.52, "sell": 0.48},
        regime="bull",
        risk_ctx={},
        cfg={
            "ev": {"R_default": 1.0},
            "thresholds": {
                "entry_conf_overall": 0.6,
                "signal_adaptation": {
                    "atr_period": 28,
                    "zones": {"high": {"entry_conf_overall": 0.36, "regime_proba": 0.56}},
                },
            },
            "multi_timeframe": {
                "research_bull_high_persistence_override": {
                    "enabled": False,
                    "min_persistence": 2,
                    "max_probability_gap": 0.06,
                }
            },
        },
        state_in={
            "current_atr": 4.0,
            "atr_percentiles": {"28": {"p40": 1.0, "p80": 3.0}},
        },
        state_out=state_out,
        reasons=reasons,
        versions={"decision": "v1"},
        log_decision_event=_noop_log,
    )

    assert action == "NONE"
    assert meta is not None
    assert candidate_data == {}
    assert reasons == ["ZONE:high@0.360"]
    assert "research_bull_high_persistence_state" not in state_out
    assert "research_bull_high_persistence_debug" not in state_out


def test_select_candidate_research_bull_high_persistence_override_requires_streak() -> None:
    cfg = {
        "ev": {"R_default": 1.0},
        "thresholds": {
            "entry_conf_overall": 0.6,
            "signal_adaptation": {
                "atr_period": 28,
                "zones": {"high": {"entry_conf_overall": 0.36, "regime_proba": 0.56}},
            },
        },
        "multi_timeframe": {
            "research_bull_high_persistence_override": {
                "enabled": True,
                "min_persistence": 2,
                "max_probability_gap": 0.06,
            }
        },
    }
    base_state = {
        "current_atr": 4.0,
        "atr_percentiles": {"28": {"p40": 1.0, "p80": 3.0}},
    }

    reasons_1: list[str] = []
    state_out_1: dict[str, object] = {}
    action_1, meta_1, candidate_data_1 = select_candidate(
        policy={},
        probas={"buy": 0.52, "sell": 0.48},
        regime="bull",
        risk_ctx={},
        cfg=cfg,
        state_in=base_state,
        state_out=state_out_1,
        reasons=reasons_1,
        versions={"decision": "v1"},
        log_decision_event=_noop_log,
    )

    assert action_1 == "NONE"
    assert meta_1 is not None
    assert candidate_data_1 == {}
    assert reasons_1 == ["ZONE:high@0.360"]
    assert state_out_1["research_bull_high_persistence_state"] == {"near_miss_streak": 1}
    assert "research_bull_high_persistence_debug" not in state_out_1

    reasons_2: list[str] = []
    state_out_2: dict[str, object] = {}
    action_2, meta_2, candidate_data_2 = select_candidate(
        policy={},
        probas={"buy": 0.521, "sell": 0.479},
        regime="bull",
        risk_ctx={},
        cfg=cfg,
        state_in={**base_state, **state_out_1},
        state_out=state_out_2,
        reasons=reasons_2,
        versions={"decision": "v1"},
        log_decision_event=_noop_log,
    )

    assert action_2 is None
    assert meta_2 is None
    assert candidate_data_2["candidate"] == "LONG"
    assert reasons_2 == ["ZONE:high@0.360", "RESEARCH_BULL_HIGH_PERSISTENCE_OVERRIDE"]
    assert state_out_2["research_bull_high_persistence_state"] == {"near_miss_streak": 2}
    debug = state_out_2["research_bull_high_persistence_debug"]
    assert debug["applied"] is True
    assert debug["reason"] == "RESEARCH_BULL_HIGH_PERSISTENCE_OVERRIDE"
    assert debug["near_miss_streak"] == 2
    assert debug["min_persistence"] == 2
    assert debug["max_probability_gap"] == pytest.approx(0.06)
    assert debug["threshold"] == pytest.approx(0.56)
    assert debug["threshold_gap"] == pytest.approx(0.039)
    assert debug["buy"] == pytest.approx(0.521)
    assert debug["sell"] == pytest.approx(0.479)
    assert debug["regime"] == "bull"
    assert debug["zone"] == "high"


def test_select_candidate_research_override_uses_resolved_zone_threshold_not_base_threshold() -> (
    None
):
    cfg = {
        "ev": {"R_default": 1.0},
        "thresholds": {
            "entry_conf_overall": 0.6,
            "regime_proba": {"bull": 0.9},
            "signal_adaptation": {
                "atr_period": 28,
                "zones": {"high": {"entry_conf_overall": 0.36, "regime_proba": 0.56}},
            },
        },
        "multi_timeframe": {
            "research_bull_high_persistence_override": {
                "enabled": True,
                "min_persistence": 2,
                "max_probability_gap": 0.06,
            }
        },
    }
    base_state = {
        "current_atr": 4.0,
        "atr_percentiles": {"28": {"p40": 1.0, "p80": 3.0}},
    }

    reasons_1: list[str] = []
    state_out_1: dict[str, object] = {}
    action_1, meta_1, candidate_data_1 = select_candidate(
        policy={},
        probas={"buy": 0.52, "sell": 0.48},
        regime="bull",
        risk_ctx={},
        cfg=cfg,
        state_in=base_state,
        state_out=state_out_1,
        reasons=reasons_1,
        versions={"decision": "v1"},
        log_decision_event=_noop_log,
    )

    assert action_1 == "NONE"
    assert meta_1 is not None
    assert candidate_data_1 == {}

    reasons_2: list[str] = []
    state_out_2: dict[str, object] = {}
    action_2, meta_2, candidate_data_2 = select_candidate(
        policy={},
        probas={"buy": 0.521, "sell": 0.479},
        regime="bull",
        risk_ctx={},
        cfg=cfg,
        state_in={**base_state, **state_out_1},
        state_out=state_out_2,
        reasons=reasons_2,
        versions={"decision": "v1"},
        log_decision_event=_noop_log,
    )

    assert action_2 is None
    assert meta_2 is None
    assert candidate_data_2["candidate"] == "LONG"
    debug = state_out_2["research_bull_high_persistence_debug"]
    assert debug["threshold"] == pytest.approx(0.56)
    assert debug["threshold_gap"] == pytest.approx(0.039)


def test_select_candidate_research_defensive_transition_override_disabled_matches_absent() -> None:
    base_cfg = {
        "ev": {"R_default": 1.0},
        "thresholds": {
            "entry_conf_overall": 0.6,
            "signal_adaptation": {
                "atr_period": 28,
                "zones": {"high": {"entry_conf_overall": 0.36, "regime_proba": 0.56}},
            },
        },
    }
    state_in = {
        "bars_since_regime_change": 2,
        "current_atr": 4.0,
        "atr_percentiles": {"28": {"p40": 1.0, "p80": 3.0}},
    }

    reasons_base: list[str] = []
    state_out_base: dict[str, object] = {}
    action_base, meta_base, candidate_data_base = select_candidate(
        policy={},
        probas={"buy": 0.52, "sell": 0.48},
        regime="bull",
        risk_ctx={},
        cfg=base_cfg,
        state_in=state_in,
        state_out=state_out_base,
        reasons=reasons_base,
        versions={"decision": "v1"},
        log_decision_event=_noop_log,
    )

    reasons_disabled: list[str] = []
    state_out_disabled: dict[str, object] = {}
    action_disabled, meta_disabled, candidate_data_disabled = select_candidate(
        policy={},
        probas={"buy": 0.52, "sell": 0.48},
        regime="bull",
        risk_ctx={},
        cfg={
            **base_cfg,
            "multi_timeframe": {
                "research_defensive_transition_override": {
                    "enabled": False,
                    "guard_bars": 5,
                    "max_probability_gap": 0.08,
                }
            },
        },
        state_in=state_in,
        state_out=state_out_disabled,
        reasons=reasons_disabled,
        versions={"decision": "v1"},
        log_decision_event=_noop_log,
    )

    assert action_base == action_disabled == "NONE"
    assert meta_base == meta_disabled
    assert candidate_data_base == candidate_data_disabled == {}
    assert reasons_base == reasons_disabled == ["ZONE:high@0.360"]
    assert state_out_base == state_out_disabled == {}


def test_select_candidate_research_defensive_transition_override_enables_fresh_high_zone_near_miss() -> (
    None
):
    reasons: list[str] = []
    state_out: dict[str, object] = {}

    action, meta, candidate_data = select_candidate(
        policy={},
        probas={"buy": 0.52, "sell": 0.48},
        regime="bull",
        risk_ctx={},
        cfg={
            "ev": {"R_default": 1.0},
            "thresholds": {
                "entry_conf_overall": 0.6,
                "signal_adaptation": {
                    "atr_period": 28,
                    "zones": {"high": {"entry_conf_overall": 0.36, "regime_proba": 0.56}},
                },
            },
            "multi_timeframe": {
                "research_defensive_transition_override": {
                    "enabled": True,
                    "guard_bars": 3,
                    "max_probability_gap": 0.05,
                }
            },
        },
        state_in={
            "bars_since_regime_change": 2,
            "current_atr": 4.0,
            "atr_percentiles": {"28": {"p40": 1.0, "p80": 3.0}},
        },
        state_out=state_out,
        reasons=reasons,
        versions={"decision": "v1"},
        log_decision_event=_noop_log,
    )

    assert action is None
    assert meta is None
    assert candidate_data["candidate"] == "LONG"
    assert reasons == [
        "ZONE:high@0.360",
        "RESEARCH_DEFENSIVE_TRANSITION_OVERRIDE",
    ]
    debug = state_out["research_defensive_transition_debug"]
    assert debug["applied"] is True
    assert debug["reason"] == "RESEARCH_DEFENSIVE_TRANSITION_OVERRIDE"
    assert debug["candidate"] == "LONG"
    assert debug["bars_since_regime_change"] == 2
    assert debug["guard_bars"] == 3
    assert debug["max_probability_gap"] == pytest.approx(0.05)
    assert debug["threshold"] == pytest.approx(0.56)
    assert debug["threshold_gap"] == pytest.approx(0.04)
    assert debug["buy"] == pytest.approx(0.52)
    assert debug["sell"] == pytest.approx(0.48)
    assert debug["regime"] == "bull"
    assert debug["zone"] == "high"
