from __future__ import annotations

import pytest

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


def _resolve_bars7_continuation_signature(
    *,
    confidence_gate: float = 0.5060251200,
    action_edge: float = 0.0120502401,
    max_ev: float = 0.2316,
    r_default: float = 1.0,
    regime: str = "balanced",
    bars_since_regime_change: int = 7,
    zone: str = "low",
    previous_state: dict[str, object] | None = None,
    p_buy: float | None = None,
) -> object:
    buy = confidence_gate if p_buy is None else p_buy
    sell = max(0.0, buy - action_edge)
    state_in = {"bars_since_regime_change": bars_since_regime_change}
    if previous_state is not None:
        state_in["research_policy_router_state"] = previous_state
    return resolve_research_policy_router(
        candidate="LONG",
        conf_val_gate=confidence_gate,
        p_buy=buy,
        p_sell=sell,
        max_ev=max_ev,
        r_default=r_default,
        regime=regime,
        state_in=state_in,
        cfg=_router_cfg(),
        zone=zone,
    )


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


def test_policy_router_keeps_fresh_weak_continuation_allowed() -> None:
    outcome = resolve_research_policy_router(
        candidate="LONG",
        conf_val_gate=0.54,
        p_buy=0.54,
        p_sell=0.46,
        max_ev=0.02,
        r_default=1.0,
        regime="bear",
        state_in={"bars_since_regime_change": 10},
        cfg=_router_cfg(),
        zone="base",
    )

    assert outcome is not None
    assert outcome.selected_policy == POLICY_CONTINUATION
    assert outcome.no_trade is False
    assert outcome.debug["switch_reason"] == "continuation_state_supported"


def test_policy_router_blocks_aged_weak_continuation() -> None:
    outcome = resolve_research_policy_router(
        candidate="LONG",
        conf_val_gate=0.54,
        p_buy=0.54,
        p_sell=0.46,
        max_ev=0.02,
        r_default=1.0,
        regime="bear",
        state_in={"bars_since_regime_change": 16},
        cfg=_router_cfg(),
        zone="base",
    )

    assert outcome is not None
    assert outcome.selected_policy == POLICY_NO_TRADE
    assert outcome.no_trade is True
    assert outcome.size_multiplier == 0.0
    assert outcome.debug["switch_reason"] == "AGED_WEAK_CONTINUATION_GUARD"


def test_policy_router_preserves_aged_strong_continuation() -> None:
    outcome = resolve_research_policy_router(
        candidate="LONG",
        conf_val_gate=0.55,
        p_buy=0.60,
        p_sell=0.40,
        max_ev=0.10,
        r_default=1.0,
        regime="bear",
        state_in={"bars_since_regime_change": 16},
        cfg=_router_cfg(),
        zone="base",
    )

    assert outcome is not None
    assert outcome.selected_policy == POLICY_CONTINUATION
    assert outcome.no_trade is False
    assert outcome.debug["switch_reason"] == "stable_continuation_state"


def test_policy_router_blocks_weak_pre_aged_release_from_no_trade() -> None:
    outcome = resolve_research_policy_router(
        candidate="LONG",
        conf_val_gate=0.54,
        p_buy=0.54,
        p_sell=0.46,
        max_ev=0.02,
        r_default=1.0,
        regime="bear",
        state_in={
            "bars_since_regime_change": 7,
            "research_policy_router_state": {
                "selected_policy": POLICY_NO_TRADE,
                "mandate_level": 0,
                "confidence": 0,
                "dwell_duration": 3,
            },
        },
        cfg=_router_cfg(),
        zone="base",
    )

    assert outcome is not None
    assert outcome.selected_policy == POLICY_NO_TRADE
    assert outcome.no_trade is True
    assert outcome.switch_proposed is True
    assert outcome.switch_blocked is True
    assert outcome.debug["switch_reason"] == "WEAK_PRE_AGED_CONTINUATION_RELEASE_GUARD"


def test_policy_router_allows_second_same_pocket_weak_bar_after_single_veto() -> None:
    blocked = resolve_research_policy_router(
        candidate="LONG",
        conf_val_gate=0.54,
        p_buy=0.54,
        p_sell=0.46,
        max_ev=0.02,
        r_default=1.0,
        regime="bear",
        state_in={
            "bars_since_regime_change": 7,
            "research_policy_router_state": {
                "selected_policy": POLICY_NO_TRADE,
                "mandate_level": 0,
                "confidence": 0,
                "dwell_duration": 3,
            },
        },
        cfg=_router_cfg(),
        zone="base",
    )

    assert blocked is not None
    assert blocked.selected_policy == POLICY_NO_TRADE
    assert blocked.debug["switch_reason"] == "WEAK_PRE_AGED_CONTINUATION_RELEASE_GUARD"

    released = resolve_research_policy_router(
        candidate="LONG",
        conf_val_gate=0.54,
        p_buy=0.54,
        p_sell=0.46,
        max_ev=0.02,
        r_default=1.0,
        regime="bear",
        state_in={
            "bars_since_regime_change": 7,
            "research_policy_router_state": blocked.state,
        },
        cfg=_router_cfg(),
        zone="base",
    )

    assert released is not None
    assert released.selected_policy == POLICY_CONTINUATION
    assert released.no_trade is False
    assert released.switch_blocked is False
    assert released.debug["switch_reason"] == "continuation_state_supported"

    exited = resolve_research_policy_router(
        candidate="LONG",
        conf_val_gate=0.54,
        p_buy=0.54,
        p_sell=0.46,
        max_ev=0.02,
        r_default=1.0,
        regime="bear",
        state_in={
            "bars_since_regime_change": 8,
            "research_policy_router_state": released.state,
        },
        cfg=_router_cfg(),
        zone="base",
    )

    assert exited is not None
    assert exited.selected_policy == POLICY_CONTINUATION
    assert "weak_pre_aged_single_veto_latch" not in exited.state
    assert exited.debug["weak_pre_aged_single_veto_latch"] is False


def test_policy_router_allows_release_once_strong_stability_is_reached() -> None:
    outcome = resolve_research_policy_router(
        candidate="LONG",
        conf_val_gate=0.54,
        p_buy=0.54,
        p_sell=0.46,
        max_ev=0.02,
        r_default=1.0,
        regime="bear",
        state_in={
            "bars_since_regime_change": 8,
            "research_policy_router_state": {
                "selected_policy": POLICY_NO_TRADE,
                "mandate_level": 0,
                "confidence": 0,
                "dwell_duration": 3,
            },
        },
        cfg=_router_cfg(),
        zone="base",
    )

    assert outcome is not None
    assert outcome.selected_policy == POLICY_CONTINUATION
    assert outcome.no_trade is False
    assert outcome.switch_blocked is False
    assert outcome.debug["switch_reason"] == "continuation_state_supported"


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


def test_policy_router_reconsiders_exact_bars7_continuation_signature() -> None:
    outcome = _resolve_bars7_continuation_signature(
        previous_state={
            "selected_policy": POLICY_CONTINUATION,
            "mandate_level": 2,
            "confidence": 2,
            "dwell_duration": 3,
        }
    )

    assert outcome is not None
    assert outcome.selected_policy == POLICY_CONTINUATION
    assert outcome.no_trade is False
    assert outcome.switch_proposed is True
    assert outcome.switch_blocked is True
    assert outcome.debug["switch_reason"] == "confidence_below_threshold"
    assert outcome.debug["raw_target_policy"] == POLICY_DEFENSIVE
    assert outcome.debug["bars7_continuation_persistence_reconsideration_applied"] is True


def test_policy_router_excludes_later_low_zone_rows_from_bars7_helper() -> None:
    outcome = _resolve_bars7_continuation_signature(
        confidence_gate=0.5068924643,
        action_edge=0.0137849287,
        previous_state={
            "selected_policy": POLICY_NO_TRADE,
            "mandate_level": 0,
            "confidence": 0,
            "dwell_duration": 4,
        },
    )

    assert outcome is not None
    assert outcome.selected_policy == POLICY_NO_TRADE
    assert outcome.no_trade is True
    assert outcome.debug["switch_reason"] == "insufficient_evidence"
    assert outcome.debug["raw_target_policy"] == POLICY_NO_TRADE
    assert outcome.debug["bars7_continuation_persistence_reconsideration_applied"] is False


@pytest.mark.parametrize(
    ("confidence_gate", "action_edge"),
    [
        (0.5150000000, 0.0120502401),
        (0.5049000000, 0.0120502401),
        (0.5060251200, 0.0099000000),
        (0.5060251200, 0.0141000000),
    ],
)
def test_policy_router_bars7_continuation_boundaries_fail_closed(
    confidence_gate: float,
    action_edge: float,
) -> None:
    outcome = _resolve_bars7_continuation_signature(
        confidence_gate=confidence_gate,
        action_edge=action_edge,
        previous_state={
            "selected_policy": POLICY_CONTINUATION,
            "mandate_level": 2,
            "confidence": 2,
            "dwell_duration": 3,
        },
    )

    assert outcome is not None
    assert outcome.selected_policy == POLICY_NO_TRADE
    assert outcome.no_trade is True
    assert outcome.debug["switch_reason"] == "insufficient_evidence"
    assert outcome.debug["bars7_continuation_persistence_reconsideration_applied"] is False
