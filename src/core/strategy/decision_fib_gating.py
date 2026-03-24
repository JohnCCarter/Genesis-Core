from __future__ import annotations

from collections.abc import Callable
from typing import Any

from core.strategy.decision_fib_gating_helpers import (
    _summarize_fib_debug,
    apply_htf_fib_gate,
    apply_ltf_fib_gate,
    build_ltf_override_debug,
    prepare_override_context,
)
from core.strategy.decision_gates import Action


def apply_fib_gating(
    *,
    policy_symbol: str,
    policy_timeframe: str,
    candidate: Action,
    confidence: dict[str, float] | None,
    cfg: dict[str, Any],
    state_in: dict[str, Any],
    state_out: dict[str, Any],
    reasons: list[str],
    versions: dict[str, Any],
    regime_str: str,
    use_htf_block: bool,
    allow_ltf_override_cfg: bool,
    ltf_override_threshold: float,
    adaptive_cfg: dict[str, Any],
    override_state: dict[str, Any],
    logger: Any,
    log_decision_event: Callable[..., None],
    log_fib_flow: Callable[..., None],
) -> tuple[Action | None, dict[str, Any] | None]:
    ltf_entry_cfg = (cfg.get("ltf_fib") or {}).get("entry") or {}
    override_context_ref: dict[str, Any | None] = {"data": None}

    override_context = prepare_override_context(
        ltf_entry_cfg=ltf_entry_cfg,
        confidence=confidence,
        candidate=candidate,
        adaptive_cfg=adaptive_cfg,
        override_state=override_state,
        allow_ltf_override_cfg=allow_ltf_override_cfg,
        ltf_override_threshold=ltf_override_threshold,
        regime_str=regime_str,
    )
    override_context_ref["data"] = override_context if override_context else {}
    state_out["ltf_override_debug"] = build_ltf_override_debug(
        override_context=override_context,
        candidate=candidate,
        confidence=confidence,
        adaptive_cfg=adaptive_cfg,
        ltf_override_threshold=ltf_override_threshold,
        regime_str=regime_str,
    )

    fib_action, fib_meta = apply_htf_fib_gate(
        policy_symbol=policy_symbol,
        policy_timeframe=policy_timeframe,
        candidate=candidate,
        cfg=cfg,
        state_in=state_in,
        state_out=state_out,
        reasons=reasons,
        versions=versions,
        use_htf_block=use_htf_block,
        ltf_entry_cfg=ltf_entry_cfg,
        confidence=confidence,
        override_context=override_context_ref.get("data"),
        allow_ltf_override_cfg=allow_ltf_override_cfg,
        ltf_override_threshold=ltf_override_threshold,
        logger=logger,
        log_decision_event=log_decision_event,
        log_fib_flow=log_fib_flow,
    )
    if fib_action is not None:
        return fib_action, fib_meta

    fib_action, fib_meta = apply_ltf_fib_gate(
        policy_symbol=policy_symbol,
        policy_timeframe=policy_timeframe,
        candidate=candidate,
        ltf_entry_cfg=ltf_entry_cfg,
        state_in=state_in,
        state_out=state_out,
        reasons=reasons,
        versions=versions,
        logger=logger,
        log_decision_event=log_decision_event,
        log_fib_flow=log_fib_flow,
    )
    if fib_action is not None:
        return fib_action, fib_meta

    state_out["fib_gate_summary"] = {
        "candidate": candidate,
        "htf": _summarize_fib_debug(state_out.get("htf_fib_entry_debug")),
        "ltf": _summarize_fib_debug(state_out.get("ltf_fib_entry_debug")),
    }
    return None, None
