from __future__ import annotations

from core.strategy.ri_policy_router import (
    POLICY_CONTINUATION,
    POLICY_DEFENSIVE,
    POLICY_NO_TRADE,
    resolve_research_policy_router,
)


def _router_cfg(**overrides: object) -> dict[str, object]:
    leaf: dict[str, object] = {
        "enabled": True,
        "switch_threshold": 2,
        "hysteresis": 1,
        "min_dwell": 3,
        "defensive_size_multiplier": 0.5,
    }
    leaf.update(overrides)
    return {"multi_timeframe": {"research_policy_router": leaf}}


def test_policy_router_returns_none_when_disabled() -> None:
    outcome = resolve_research_policy_router(
        candidate="LONG",
        conf_val_gate=0.55,
        p_buy=0.55,
        p_sell=0.45,
        max_ev=0.10,
        r_default=1.0,
        regime="bull",
        state_in={"bars_since_regime_change": 10},
        cfg={"multi_timeframe": {"research_policy_router": {"enabled": False}}},
        zone="base",
    )

    assert outcome is None


def test_policy_router_selects_defensive_policy_in_fresh_transition_pocket() -> None:
    outcome = resolve_research_policy_router(
        candidate="LONG",
        conf_val_gate=0.53,
        p_buy=0.52,
        p_sell=0.48,
        max_ev=0.04,
        r_default=1.0,
        regime="bull",
        state_in={"bars_since_regime_change": 2},
        cfg=_router_cfg(),
        zone="high",
    )

    assert outcome is not None
    assert outcome.selected_policy == POLICY_DEFENSIVE
    assert outcome.no_trade is False
    assert outcome.size_multiplier == 0.5
    assert outcome.state["selected_policy"] == POLICY_DEFENSIVE
    assert outcome.debug["switch_reason"] == "transition_pressure_detected"


def test_policy_router_blocks_return_until_min_dwell_is_satisfied() -> None:
    outcome = resolve_research_policy_router(
        candidate="LONG",
        conf_val_gate=0.80,
        p_buy=0.80,
        p_sell=0.20,
        max_ev=0.60,
        r_default=1.0,
        regime="bull",
        state_in={
            "bars_since_regime_change": 10,
            "research_policy_router_state": {
                "selected_policy": POLICY_DEFENSIVE,
                "mandate_level": 2,
                "confidence": 2,
                "dwell_duration": 1,
            },
        },
        cfg=_router_cfg(),
        zone="base",
    )

    assert outcome is not None
    assert outcome.selected_policy == POLICY_DEFENSIVE
    assert outcome.switch_blocked is True
    assert outcome.switch_reason == "switch_blocked_by_min_dwell"
    assert outcome.dwell_duration == 2


def test_policy_router_returns_to_continuation_after_dwell_and_hysteresis_allow() -> None:
    outcome = resolve_research_policy_router(
        candidate="LONG",
        conf_val_gate=0.80,
        p_buy=0.80,
        p_sell=0.20,
        max_ev=0.60,
        r_default=1.0,
        regime="bull",
        state_in={
            "bars_since_regime_change": 10,
            "research_policy_router_state": {
                "selected_policy": POLICY_DEFENSIVE,
                "mandate_level": 2,
                "confidence": 2,
                "dwell_duration": 3,
            },
        },
        cfg=_router_cfg(),
        zone="base",
    )

    assert outcome is not None
    assert outcome.selected_policy == POLICY_CONTINUATION
    assert outcome.switch_blocked is False
    assert outcome.switch_proposed is True
    assert outcome.dwell_duration == 1
    assert outcome.size_multiplier == 1.0


def test_policy_router_forces_no_trade_when_evidence_floor_fails() -> None:
    outcome = resolve_research_policy_router(
        candidate="LONG",
        conf_val_gate=0.50,
        p_buy=0.51,
        p_sell=0.49,
        max_ev=0.02,
        r_default=1.0,
        regime="bull",
        state_in={"bars_since_regime_change": 2},
        cfg=_router_cfg(),
        zone="base",
    )

    assert outcome is not None
    assert outcome.selected_policy == POLICY_NO_TRADE
    assert outcome.no_trade is True
    assert outcome.size_multiplier == 0.0
    assert outcome.debug["switch_reason"] == "insufficient_evidence"
