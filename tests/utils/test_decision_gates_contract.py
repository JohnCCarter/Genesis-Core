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
