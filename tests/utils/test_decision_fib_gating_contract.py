from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from core.strategy.decision_fib_gating import apply_fib_gating


def _noop_log(*_args, **_kwargs) -> None:
    return None


def test_apply_fib_gating_pass_path_emits_summary_and_fallback_override_debug() -> None:
    reasons: list[str] = []
    state_out: dict[str, object] = {}

    action, meta = apply_fib_gating(
        policy_symbol="tBTCUSD",
        policy_timeframe="1h",
        candidate="LONG",
        confidence=None,
        cfg={
            "ltf_fib": {
                "entry": {
                    "enabled": True,
                    "long_max_level": 1.0,
                    "tolerance_atr": 1.0,
                }
            }
        },
        state_in={
            "last_close": 100.0,
            "current_atr": 0.5,
            "ltf_fib": {"available": True, "levels": {1.0: 120.0}},
        },
        state_out=state_out,
        reasons=reasons,
        versions={"decision": "v1"},
        regime_str="balanced",
        use_htf_block=False,
        allow_ltf_override_cfg=False,
        ltf_override_threshold=0.85,
        adaptive_cfg={},
        override_state={},
        logger=MagicMock(),
        log_decision_event=_noop_log,
        log_fib_flow=_noop_log,
    )

    assert action is None
    assert meta is None
    assert reasons == []

    override_debug = state_out["ltf_override_debug"]
    assert override_debug["candidate"] == "LONG"
    assert override_debug["confidence"] is None
    assert override_debug["history_key"] is None
    assert override_debug["history_len"] == 0
    assert int(override_debug["history_window"]) >= 1
    assert override_debug["baseline_threshold"] == pytest.approx(0.85)
    assert override_debug["effective_threshold"] == pytest.approx(0.85)
    assert override_debug["details"] is None

    assert state_out["htf_fib_entry_debug"]["reason"] == "DISABLED_BY_CONFIG"
    assert state_out["ltf_fib_entry_debug"]["reason"] == "PASS"
    fib_summary = state_out["fib_gate_summary"]
    assert fib_summary["candidate"] == "LONG"
    assert fib_summary["htf"]["reason"] == "DISABLED_BY_CONFIG"
    assert fib_summary["ltf"]["reason"] == "PASS"


def test_apply_fib_gating_htf_short_circuits_before_ltf_summary() -> None:
    reasons: list[str] = []
    state_out: dict[str, object] = {}

    action, meta = apply_fib_gating(
        policy_symbol="tBTCUSD",
        policy_timeframe="1h",
        candidate="LONG",
        confidence={"buy": 0.6, "sell": 0.1},
        cfg={
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
        },
        state_in={
            "last_close": 98.0,
            "current_atr": 1.0,
            "htf_fib": {"available": True, "levels": {0.5: 100.0}},
            "ltf_fib": {"available": True, "levels": {1.0: 120.0}},
        },
        state_out=state_out,
        reasons=reasons,
        versions={"decision": "v1"},
        regime_str="balanced",
        use_htf_block=True,
        allow_ltf_override_cfg=False,
        ltf_override_threshold=0.85,
        adaptive_cfg={},
        override_state={},
        logger=MagicMock(),
        log_decision_event=_noop_log,
        log_fib_flow=_noop_log,
    )

    assert action == "NONE"
    assert meta is not None
    assert reasons == ["HTF_FIB_LONG_BLOCK"]
    assert state_out["htf_fib_entry_debug"]["reason"] == "LONG_BELOW_LEVEL"
    assert "ltf_fib_entry_debug" not in state_out
    assert "fib_gate_summary" not in state_out
    assert meta["reasons"] == reasons
    assert meta["state_out"] == state_out


def test_apply_fib_gating_ltf_short_circuits_after_htf_pass() -> None:
    reasons: list[str] = []
    state_out: dict[str, object] = {}

    action, meta = apply_fib_gating(
        policy_symbol="tBTCUSD",
        policy_timeframe="1h",
        candidate="LONG",
        confidence=None,
        cfg={
            "ltf_fib": {
                "entry": {
                    "enabled": True,
                    "long_max_level": 1.0,
                    "tolerance_atr": 1.0,
                }
            }
        },
        state_in={
            "last_close": 121.0,
            "current_atr": 0.5,
            "ltf_fib": {"available": True, "levels": {1.0: 120.0}},
        },
        state_out=state_out,
        reasons=reasons,
        versions={"decision": "v1"},
        regime_str="balanced",
        use_htf_block=False,
        allow_ltf_override_cfg=False,
        ltf_override_threshold=0.85,
        adaptive_cfg={},
        override_state={},
        logger=MagicMock(),
        log_decision_event=_noop_log,
        log_fib_flow=_noop_log,
    )

    assert action == "NONE"
    assert meta is not None
    assert reasons == ["LTF_FIB_LONG_BLOCK"]
    assert state_out["htf_fib_entry_debug"]["reason"] == "DISABLED_BY_CONFIG"
    assert state_out["ltf_fib_entry_debug"]["reason"] == "LONG_ABOVE_LEVEL"
    assert "fib_gate_summary" not in state_out
    assert meta["reasons"] == reasons
    assert meta["state_out"] == state_out


def test_apply_fib_gating_exports_adaptive_override_debug_details() -> None:
    reasons: list[str] = []
    state_out: dict[str, object] = {}
    override_state = {"buy_history": [0.1, 0.2]}

    action, meta = apply_fib_gating(
        policy_symbol="tBTCUSD",
        policy_timeframe="1h",
        candidate="LONG",
        confidence={"buy": 0.9, "sell": 0.1},
        cfg={
            "ltf_fib": {
                "entry": {
                    "enabled": True,
                    "long_max_level": 1.0,
                    "tolerance_atr": 1.0,
                }
            }
        },
        state_in={
            "last_close": 100.0,
            "current_atr": 0.5,
            "ltf_fib": {"available": True, "levels": {1.0: 120.0}},
        },
        state_out=state_out,
        reasons=reasons,
        versions={"decision": "v1"},
        regime_str="balanced",
        use_htf_block=False,
        allow_ltf_override_cfg=True,
        ltf_override_threshold=0.85,
        adaptive_cfg={
            "enabled": True,
            "window": 3,
            "min_history": 3,
            "percentile": 0.5,
        },
        override_state=override_state,
        logger=MagicMock(),
        log_decision_event=_noop_log,
        log_fib_flow=_noop_log,
    )

    assert action is None
    assert meta is None
    assert reasons == []
    override_debug = state_out["ltf_override_debug"]
    assert override_debug["candidate"] == "LONG"
    assert override_debug["confidence"] == pytest.approx(0.9)
    assert override_debug["history_key"] == "buy_history"
    assert override_debug["history_len"] == 3
    assert override_debug["history_window"] == 3
    assert override_debug["baseline_threshold"] == pytest.approx(0.85)
    assert override_debug["effective_threshold"] == pytest.approx(0.2)
    details = override_debug["details"]
    assert details is not None
    assert details["history_len"] == 3
    assert details["effective_threshold"] == pytest.approx(0.2)
    assert override_state["buy_history"][-1] == pytest.approx(0.9)
    assert len(override_state["buy_history"]) == 3
    assert state_out["fib_gate_summary"]["ltf"]["reason"] == "PASS"
