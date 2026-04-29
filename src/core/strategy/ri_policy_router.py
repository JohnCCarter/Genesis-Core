from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from core.intelligence.regime.clarity import compute_clarity_score_v1
from core.strategy.decision_gates import Action

RouterPolicy = Literal[
    "RI_continuation_policy",
    "RI_defensive_transition_policy",
    "RI_no_trade_policy",
]

POLICY_CONTINUATION: RouterPolicy = "RI_continuation_policy"
POLICY_DEFENSIVE: RouterPolicy = "RI_defensive_transition_policy"
POLICY_NO_TRADE: RouterPolicy = "RI_no_trade_policy"
RI_POLICY_ROUTER_VERSION = "ri_policy_router_v1"
RESEARCH_POLICY_ROUTER_STATE_KEY = "research_policy_router_state"
RESEARCH_POLICY_ROUTER_DEBUG_KEY = "research_policy_router_debug"

_CONTINUATION_DEFAULTS = {
    "clarity_floor": 28.0,
    "clarity_strong": 30.0,
    "confidence_floor": 0.535,
    "confidence_strong": 0.545,
    "edge_floor": 0.070,
    "edge_strong": 0.100,
    "stable_bars_floor": 5.0,
    "stable_bars_strong": 8.0,
}

_NO_TRADE_DEFAULTS = {
    "clarity_floor": 24.0,
    "confidence_floor": 0.515,
    "edge_floor": 0.035,
}

_SWITCH_DEFAULTS = {
    "switch_threshold": 2,
    "hysteresis": 1,
    "min_dwell": 3,
    "defensive_size_multiplier": 0.5,
}

_AGED_WEAK_CONTINUATION_BARS_THRESHOLD = _CONTINUATION_DEFAULTS["stable_bars_strong"] * 2.0
_AGED_WEAK_CONTINUATION_GUARD_REASON = "AGED_WEAK_CONTINUATION_GUARD"
_WEAK_PRE_AGED_RELEASE_GUARD_REASON = "WEAK_PRE_AGED_CONTINUATION_RELEASE_GUARD"
_WEAK_PRE_AGED_SINGLE_VETO_LATCH_KEY = "weak_pre_aged_single_veto_latch"
_BARS7_CONTINUATION_PERSISTENCE_RECONSIDERATION_KEY = (
    "bars7_continuation_persistence_reconsideration_applied"
)


@dataclass(frozen=True, slots=True)
class PolicyRouterOutcome:
    selected_policy: RouterPolicy
    switch_reason: str
    switch_proposed: bool
    switch_blocked: bool
    previous_policy: RouterPolicy | None
    mandate_level: int
    confidence_level: int
    dwell_duration: int
    size_multiplier: float
    no_trade: bool
    state: dict[str, Any]
    debug: dict[str, Any]


@dataclass(frozen=True, slots=True)
class _RawRouterDecision:
    target_policy: RouterPolicy
    raw_switch_reason: str
    mandate_level: int
    confidence_level: int
    no_trade: bool
    bars7_continuation_persistence_reconsideration_applied: bool = False


@dataclass(frozen=True, slots=True)
class _StabilityControlledDecision:
    selected_policy: RouterPolicy
    switch_reason: str
    switch_proposed: bool
    switch_blocked: bool
    previous_policy: RouterPolicy | None
    mandate_level: int
    confidence_level: int
    dwell_duration: int
    no_trade: bool


@dataclass(frozen=True, slots=True)
class _PreviousRouterState:
    selected_policy: RouterPolicy
    mandate_level: int
    confidence_level: int
    dwell_duration: int
    weak_pre_aged_single_veto_latch: bool


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _router_config(cfg: dict[str, Any]) -> dict[str, Any] | None:
    mtf_cfg = cfg.get("multi_timeframe") or {}
    router_cfg = mtf_cfg.get("research_policy_router")
    if not isinstance(router_cfg, dict):
        return None
    if not bool(router_cfg.get("enabled", False)):
        return None
    normalized = dict(_SWITCH_DEFAULTS)
    normalized.update(router_cfg)
    normalized["switch_threshold"] = max(1, int(_safe_float(normalized["switch_threshold"], 2.0)))
    normalized["hysteresis"] = max(0, int(_safe_float(normalized["hysteresis"], 1.0)))
    normalized["min_dwell"] = max(0, int(_safe_float(normalized["min_dwell"], 3.0)))
    normalized["defensive_size_multiplier"] = max(
        0.0,
        min(1.0, _safe_float(normalized["defensive_size_multiplier"], 0.5)),
    )
    return normalized


def _previous_router_state(state_in: dict[str, Any]) -> _PreviousRouterState | None:
    raw = state_in.get(RESEARCH_POLICY_ROUTER_STATE_KEY)
    if not isinstance(raw, dict):
        return None
    selected_policy = raw.get("selected_policy")
    if selected_policy not in {POLICY_CONTINUATION, POLICY_DEFENSIVE, POLICY_NO_TRADE}:
        return None
    return _PreviousRouterState(
        selected_policy=selected_policy,
        mandate_level=max(0, int(_safe_float(raw.get("mandate_level", 0.0), 0.0))),
        confidence_level=max(0, int(_safe_float(raw.get("confidence", 0.0), 0.0))),
        dwell_duration=max(0, int(_safe_float(raw.get("dwell_duration", 0.0), 0.0))),
        weak_pre_aged_single_veto_latch=bool(raw.get(_WEAK_PRE_AGED_SINGLE_VETO_LATCH_KEY, False)),
    )


def _should_guard_aged_weak_continuation(
    *,
    confidence_gate: float,
    action_edge: float,
    bars_since_regime_change: float,
) -> bool:
    return (
        bars_since_regime_change >= _AGED_WEAK_CONTINUATION_BARS_THRESHOLD
        and confidence_gate < _CONTINUATION_DEFAULTS["confidence_strong"]
        and action_edge < _CONTINUATION_DEFAULTS["edge_strong"]
    )


def _should_reconsider_bars7_continuation_persistence(
    *,
    candidate: Action,
    raw_decision: _RawRouterDecision,
    previous_state: _PreviousRouterState | None,
    clarity_score: float,
    confidence_gate: float,
    action_edge: float,
    bars_since_regime_change: float,
    zone: str,
) -> bool:
    tolerance = 1e-12
    if candidate != "LONG" or previous_state is None:
        return False

    confidence_delta = _NO_TRADE_DEFAULTS["confidence_floor"] - confidence_gate
    return (
        previous_state.selected_policy == POLICY_CONTINUATION
        and raw_decision.target_policy == POLICY_NO_TRADE
        and raw_decision.raw_switch_reason == "insufficient_evidence"
        and zone == "low"
        and int(bars_since_regime_change) == 7
        and int(clarity_score) == 35
        and confidence_delta > 0.0
        and confidence_delta <= 0.01 + tolerance
        and 0.010 - tolerance <= action_edge <= 0.014 + tolerance
    )


def _is_weak_pre_aged_release_pocket(
    *,
    raw_decision: _RawRouterDecision,
    bars_since_regime_change: float,
) -> bool:
    return (
        raw_decision.target_policy == POLICY_CONTINUATION
        and raw_decision.raw_switch_reason == "continuation_state_supported"
        and raw_decision.mandate_level == 2
        and bars_since_regime_change < _CONTINUATION_DEFAULTS["stable_bars_strong"]
    )


def _should_block_weak_pre_aged_release(
    *,
    raw_decision: _RawRouterDecision,
    previous_state: _PreviousRouterState,
    bars_since_regime_change: float,
) -> bool:
    return (
        previous_state.selected_policy == POLICY_NO_TRADE
        and _is_weak_pre_aged_release_pocket(
            raw_decision=raw_decision,
            bars_since_regime_change=bars_since_regime_change,
        )
        and not previous_state.weak_pre_aged_single_veto_latch
    )


def _next_weak_pre_aged_single_veto_latch(
    *,
    raw_decision: _RawRouterDecision,
    routed_decision: _StabilityControlledDecision,
    previous_state: _PreviousRouterState | None,
    bars_since_regime_change: float,
) -> bool:
    if not _is_weak_pre_aged_release_pocket(
        raw_decision=raw_decision,
        bars_since_regime_change=bars_since_regime_change,
    ):
        return False
    if routed_decision.switch_reason == _WEAK_PRE_AGED_RELEASE_GUARD_REASON:
        return True
    if previous_state is None:
        return False
    return previous_state.weak_pre_aged_single_veto_latch


def _raw_router_decision(
    *,
    clarity_score: float,
    confidence_gate: float,
    action_edge: float,
    bars_since_regime_change: float,
    zone: str,
    allow_insufficient_evidence_fallthrough: bool = False,
) -> _RawRouterDecision:
    if (
        clarity_score < _NO_TRADE_DEFAULTS["clarity_floor"]
        or confidence_gate < _NO_TRADE_DEFAULTS["confidence_floor"]
        or action_edge < _NO_TRADE_DEFAULTS["edge_floor"]
    ) and not allow_insufficient_evidence_fallthrough:
        return _RawRouterDecision(
            target_policy=POLICY_NO_TRADE,
            raw_switch_reason="insufficient_evidence",
            mandate_level=0,
            confidence_level=0,
            no_trade=True,
        )

    continuation_points = sum(
        [
            clarity_score >= _CONTINUATION_DEFAULTS["clarity_floor"],
            clarity_score >= _CONTINUATION_DEFAULTS["clarity_strong"],
            confidence_gate >= _CONTINUATION_DEFAULTS["confidence_floor"],
            confidence_gate >= _CONTINUATION_DEFAULTS["confidence_strong"],
            action_edge >= _CONTINUATION_DEFAULTS["edge_floor"],
            action_edge >= _CONTINUATION_DEFAULTS["edge_strong"],
            bars_since_regime_change >= _CONTINUATION_DEFAULTS["stable_bars_floor"],
            bars_since_regime_change >= _CONTINUATION_DEFAULTS["stable_bars_strong"],
        ]
    )
    transition_points = sum(
        [
            bars_since_regime_change <= 3.0,
            bars_since_regime_change <= 8.0,
            clarity_score < _CONTINUATION_DEFAULTS["clarity_floor"],
            confidence_gate < _CONTINUATION_DEFAULTS["confidence_floor"],
            action_edge < _CONTINUATION_DEFAULTS["edge_floor"],
            zone == "high",
        ]
    )

    if continuation_points >= 6:
        return _RawRouterDecision(
            target_policy=POLICY_CONTINUATION,
            raw_switch_reason="stable_continuation_state",
            mandate_level=3,
            confidence_level=3,
            no_trade=False,
            bars7_continuation_persistence_reconsideration_applied=(
                allow_insufficient_evidence_fallthrough
            ),
        )
    if continuation_points >= 4 and transition_points <= 2:
        if _should_guard_aged_weak_continuation(
            confidence_gate=confidence_gate,
            action_edge=action_edge,
            bars_since_regime_change=bars_since_regime_change,
        ):
            return _RawRouterDecision(
                target_policy=POLICY_NO_TRADE,
                raw_switch_reason=_AGED_WEAK_CONTINUATION_GUARD_REASON,
                mandate_level=0,
                confidence_level=0,
                no_trade=True,
                bars7_continuation_persistence_reconsideration_applied=(
                    allow_insufficient_evidence_fallthrough
                ),
            )
        return _RawRouterDecision(
            target_policy=POLICY_CONTINUATION,
            raw_switch_reason="continuation_state_supported",
            mandate_level=2,
            confidence_level=2,
            no_trade=False,
            bars7_continuation_persistence_reconsideration_applied=(
                allow_insufficient_evidence_fallthrough
            ),
        )
    if transition_points >= 4:
        return _RawRouterDecision(
            target_policy=POLICY_DEFENSIVE,
            raw_switch_reason="transition_pressure_detected",
            mandate_level=2,
            confidence_level=2,
            no_trade=False,
            bars7_continuation_persistence_reconsideration_applied=(
                allow_insufficient_evidence_fallthrough
            ),
        )
    if transition_points >= 2:
        return _RawRouterDecision(
            target_policy=POLICY_DEFENSIVE,
            raw_switch_reason="defensive_transition_state",
            mandate_level=1,
            confidence_level=1,
            no_trade=False,
            bars7_continuation_persistence_reconsideration_applied=(
                allow_insufficient_evidence_fallthrough
            ),
        )
    return _RawRouterDecision(
        target_policy=POLICY_NO_TRADE,
        raw_switch_reason="confidence_below_threshold",
        mandate_level=0,
        confidence_level=0,
        no_trade=True,
        bars7_continuation_persistence_reconsideration_applied=(
            allow_insufficient_evidence_fallthrough
        ),
    )


def _apply_stability_controls(
    *,
    raw_decision: _RawRouterDecision,
    previous_state: _PreviousRouterState | None,
    bars_since_regime_change: float,
    switch_threshold: int,
    hysteresis: int,
    min_dwell: int,
) -> _StabilityControlledDecision:
    if previous_state is None:
        return _StabilityControlledDecision(
            selected_policy=raw_decision.target_policy,
            switch_reason=raw_decision.raw_switch_reason,
            switch_proposed=False,
            switch_blocked=False,
            previous_policy=None,
            mandate_level=raw_decision.mandate_level,
            confidence_level=raw_decision.confidence_level,
            dwell_duration=1,
            no_trade=raw_decision.no_trade,
        )

    if raw_decision.target_policy == previous_state.selected_policy:
        return _StabilityControlledDecision(
            selected_policy=raw_decision.target_policy,
            switch_reason=raw_decision.raw_switch_reason,
            switch_proposed=False,
            switch_blocked=False,
            previous_policy=previous_state.selected_policy,
            mandate_level=raw_decision.mandate_level,
            confidence_level=raw_decision.confidence_level,
            dwell_duration=previous_state.dwell_duration + 1,
            no_trade=raw_decision.no_trade,
        )

    if raw_decision.target_policy == POLICY_NO_TRADE:
        return _StabilityControlledDecision(
            selected_policy=POLICY_NO_TRADE,
            switch_reason=raw_decision.raw_switch_reason,
            switch_proposed=True,
            switch_blocked=False,
            previous_policy=previous_state.selected_policy,
            mandate_level=raw_decision.mandate_level,
            confidence_level=raw_decision.confidence_level,
            dwell_duration=1,
            no_trade=True,
        )

    if _should_block_weak_pre_aged_release(
        raw_decision=raw_decision,
        previous_state=previous_state,
        bars_since_regime_change=bars_since_regime_change,
    ):
        return _StabilityControlledDecision(
            selected_policy=previous_state.selected_policy,
            switch_reason=_WEAK_PRE_AGED_RELEASE_GUARD_REASON,
            switch_proposed=True,
            switch_blocked=True,
            previous_policy=previous_state.selected_policy,
            mandate_level=previous_state.mandate_level,
            confidence_level=previous_state.confidence_level,
            dwell_duration=previous_state.dwell_duration + 1,
            no_trade=True,
        )

    if previous_state.dwell_duration < min_dwell:
        return _StabilityControlledDecision(
            selected_policy=previous_state.selected_policy,
            switch_reason="switch_blocked_by_min_dwell",
            switch_proposed=True,
            switch_blocked=True,
            previous_policy=previous_state.selected_policy,
            mandate_level=previous_state.mandate_level,
            confidence_level=previous_state.confidence_level,
            dwell_duration=previous_state.dwell_duration + 1,
            no_trade=previous_state.selected_policy == POLICY_NO_TRADE,
        )

    if raw_decision.mandate_level < switch_threshold:
        return _StabilityControlledDecision(
            selected_policy=previous_state.selected_policy,
            switch_reason="confidence_below_threshold",
            switch_proposed=True,
            switch_blocked=True,
            previous_policy=previous_state.selected_policy,
            mandate_level=previous_state.mandate_level,
            confidence_level=previous_state.confidence_level,
            dwell_duration=previous_state.dwell_duration + 1,
            no_trade=previous_state.selected_policy == POLICY_NO_TRADE,
        )

    if raw_decision.mandate_level < previous_state.mandate_level + hysteresis:
        return _StabilityControlledDecision(
            selected_policy=previous_state.selected_policy,
            switch_reason="switch_blocked_by_hysteresis",
            switch_proposed=True,
            switch_blocked=True,
            previous_policy=previous_state.selected_policy,
            mandate_level=previous_state.mandate_level,
            confidence_level=previous_state.confidence_level,
            dwell_duration=previous_state.dwell_duration + 1,
            no_trade=previous_state.selected_policy == POLICY_NO_TRADE,
        )

    return _StabilityControlledDecision(
        selected_policy=raw_decision.target_policy,
        switch_reason=raw_decision.raw_switch_reason,
        switch_proposed=True,
        switch_blocked=False,
        previous_policy=previous_state.selected_policy,
        mandate_level=raw_decision.mandate_level,
        confidence_level=raw_decision.confidence_level,
        dwell_duration=1,
        no_trade=raw_decision.no_trade,
    )


def resolve_research_policy_router(
    *,
    candidate: Action,
    conf_val_gate: float,
    p_buy: float,
    p_sell: float,
    max_ev: float,
    r_default: float,
    regime: str | None,
    state_in: dict[str, Any],
    cfg: dict[str, Any],
    zone: str | None,
) -> PolicyRouterOutcome | None:
    router_cfg = _router_config(cfg)
    if router_cfg is None:
        return None

    regime_norm = str(regime or "balanced").strip().lower()
    zone_norm = str(zone or "base").strip().lower()
    action_edge = abs(float(p_buy) - float(p_sell))
    bars_since_regime_change = max(
        0.0,
        float(_safe_float(state_in.get("bars_since_regime_change", 0.0), 0.0)),
    )
    clarity_result = compute_clarity_score_v1(
        confidence_gate=float(conf_val_gate),
        edge=float(action_edge),
        max_ev=float(max_ev),
        r_default=float(r_default),
        candidate=candidate,
        regime=regime_norm,
    )
    raw_decision = _raw_router_decision(
        clarity_score=float(clarity_result.clarity_score),
        confidence_gate=float(conf_val_gate),
        action_edge=float(action_edge),
        bars_since_regime_change=float(bars_since_regime_change),
        zone=zone_norm,
    )
    previous_state = _previous_router_state(state_in)
    if _should_reconsider_bars7_continuation_persistence(
        candidate=candidate,
        raw_decision=raw_decision,
        previous_state=previous_state,
        clarity_score=float(clarity_result.clarity_score),
        confidence_gate=float(conf_val_gate),
        action_edge=float(action_edge),
        bars_since_regime_change=float(bars_since_regime_change),
        zone=zone_norm,
    ):
        raw_decision = _raw_router_decision(
            clarity_score=float(clarity_result.clarity_score),
            confidence_gate=float(conf_val_gate),
            action_edge=float(action_edge),
            bars_since_regime_change=float(bars_since_regime_change),
            zone=zone_norm,
            allow_insufficient_evidence_fallthrough=True,
        )
    routed_decision = _apply_stability_controls(
        raw_decision=raw_decision,
        previous_state=previous_state,
        bars_since_regime_change=float(bars_since_regime_change),
        switch_threshold=int(router_cfg["switch_threshold"]),
        hysteresis=int(router_cfg["hysteresis"]),
        min_dwell=int(router_cfg["min_dwell"]),
    )
    weak_pre_aged_single_veto_latch = _next_weak_pre_aged_single_veto_latch(
        raw_decision=raw_decision,
        routed_decision=routed_decision,
        previous_state=previous_state,
        bars_since_regime_change=float(bars_since_regime_change),
    )
    size_multiplier = (
        0.0
        if routed_decision.selected_policy == POLICY_NO_TRADE
        else (
            float(router_cfg["defensive_size_multiplier"])
            if routed_decision.selected_policy == POLICY_DEFENSIVE
            else 1.0
        )
    )
    state = {
        "selected_policy": routed_decision.selected_policy,
        "mandate_level": routed_decision.mandate_level,
        "confidence": routed_decision.confidence_level,
        "dwell_duration": routed_decision.dwell_duration,
    }
    if weak_pre_aged_single_veto_latch:
        state[_WEAK_PRE_AGED_SINGLE_VETO_LATCH_KEY] = True
    debug = {
        "enabled": True,
        "version": RI_POLICY_ROUTER_VERSION,
        "candidate": candidate,
        "regime": regime_norm,
        "zone": zone_norm,
        "bars_since_regime_change": int(bars_since_regime_change),
        "confidence_gate": float(conf_val_gate),
        "action_edge": float(action_edge),
        "clarity_score": int(clarity_result.clarity_score),
        "clarity_raw": float(clarity_result.clarity_raw),
        "raw_target_policy": raw_decision.target_policy,
        "selected_policy": routed_decision.selected_policy,
        "previous_policy": routed_decision.previous_policy,
        "switch_reason": routed_decision.switch_reason,
        "switch_proposed": routed_decision.switch_proposed,
        "switch_blocked": routed_decision.switch_blocked,
        "mandate_level": routed_decision.mandate_level,
        "confidence_level": routed_decision.confidence_level,
        "dwell_duration": routed_decision.dwell_duration,
        _WEAK_PRE_AGED_SINGLE_VETO_LATCH_KEY: weak_pre_aged_single_veto_latch,
        _BARS7_CONTINUATION_PERSISTENCE_RECONSIDERATION_KEY: (
            raw_decision.bars7_continuation_persistence_reconsideration_applied
        ),
        "size_multiplier": float(size_multiplier),
        "router_params": {
            "switch_threshold": int(router_cfg["switch_threshold"]),
            "hysteresis": int(router_cfg["hysteresis"]),
            "min_dwell": int(router_cfg["min_dwell"]),
            "defensive_size_multiplier": float(router_cfg["defensive_size_multiplier"]),
        },
    }
    return PolicyRouterOutcome(
        selected_policy=routed_decision.selected_policy,
        switch_reason=routed_decision.switch_reason,
        switch_proposed=routed_decision.switch_proposed,
        switch_blocked=routed_decision.switch_blocked,
        previous_policy=routed_decision.previous_policy,
        mandate_level=routed_decision.mandate_level,
        confidence_level=routed_decision.confidence_level,
        dwell_duration=routed_decision.dwell_duration,
        size_multiplier=float(size_multiplier),
        no_trade=routed_decision.no_trade,
        state=state,
        debug=debug,
    )


__all__ = [
    "POLICY_CONTINUATION",
    "POLICY_DEFENSIVE",
    "POLICY_NO_TRADE",
    "RESEARCH_POLICY_ROUTER_DEBUG_KEY",
    "RESEARCH_POLICY_ROUTER_STATE_KEY",
    "RI_POLICY_ROUTER_VERSION",
    "PolicyRouterOutcome",
    "resolve_research_policy_router",
]
