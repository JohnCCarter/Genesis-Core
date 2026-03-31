from __future__ import annotations

import copy
import logging
from typing import Any, Literal

from core.strategy.decision_fib_gating import apply_fib_gating
from core.strategy.decision_gates import apply_post_fib_gates, safe_float, select_candidate
from core.strategy.decision_sizing import apply_sizing
from core.strategy.fib_logging import log_fib_flow
from core.utils.logging_redaction import get_logger

Action = Literal["LONG", "SHORT", "NONE"]

_LOG = get_logger(__name__)

_FEATURE_ATTRIBUTION_REQUEST_KEY = "feature_attribution"
_FEATURE_ATTRIBUTION_REQUEST_KEYS = frozenset({"selected_row_label", "mode"})
_FEATURE_ATTRIBUTION_INVALID_REQUEST = "FEATURE_ATTRIBUTION_INVALID_REQUEST"
_FEATURE_ATTRIBUTION_MIN_EDGE_ROW = "Minimum-edge gate seam"
_FEATURE_ATTRIBUTION_HYSTERESIS_ROW = "Hysteresis gate seam"
_FEATURE_ATTRIBUTION_COOLDOWN_ROW = "Cooldown gate seam"
_FEATURE_ATTRIBUTION_HTF_BLOCK_ROW = "HTF block seam"
_FEATURE_ATTRIBUTION_SUPPORTED_ROWS = frozenset(
    {
        _FEATURE_ATTRIBUTION_MIN_EDGE_ROW,
        _FEATURE_ATTRIBUTION_HYSTERESIS_ROW,
        _FEATURE_ATTRIBUTION_COOLDOWN_ROW,
        _FEATURE_ATTRIBUTION_HTF_BLOCK_ROW,
    }
)
_FEATURE_ATTRIBUTION_NEUTRALIZE_MODE = "neutralize"


def _sanitize_context(value: Any) -> Any:
    if isinstance(value, str | int | float | bool) or value is None:
        return value
    if isinstance(value, list | tuple):
        return [_sanitize_context(v) for v in value[:5]]
    if isinstance(value, dict):
        return {str(k): _sanitize_context(v) for k, v in list(value.items())[:8]}
    return str(value)


def _log_decision_event(event: str, **context: Any) -> None:
    if not _LOG.isEnabledFor(logging.DEBUG):
        return

    try:
        payload = {k: _sanitize_context(v) for k, v in context.items()}
        _LOG.debug("[DECISION] %s %s", event, payload)
    except Exception:  # pragma: no cover
        _LOG.debug("[DECISION] %s", event)


def _none_result(
    versions: dict[str, Any],
    reasons: list[str],
    state_out: dict[str, Any],
) -> tuple[Action, dict[str, Any]]:
    return "NONE", {
        "versions": versions,
        "reasons": reasons,
        "state_out": state_out,
    }


def _resolve_feature_attribution_request(
    policy: dict[str, Any],
    *,
    reasons: list[str],
    versions: dict[str, Any],
    state_out: dict[str, Any],
) -> tuple[str | None, tuple[Action, dict[str, Any]] | None]:
    request = policy.get(_FEATURE_ATTRIBUTION_REQUEST_KEY)
    if request is None:
        return None, None

    if not isinstance(request, dict) or set(request) != _FEATURE_ATTRIBUTION_REQUEST_KEYS:
        reasons.append(_FEATURE_ATTRIBUTION_INVALID_REQUEST)
        _log_decision_event("FEATURE_ATTRIBUTION_INVALID_REQUEST", request=request)
        return None, _none_result(versions, reasons, state_out)

    selected_row_label = request.get("selected_row_label")
    mode = request.get("mode")

    if (
        selected_row_label not in _FEATURE_ATTRIBUTION_SUPPORTED_ROWS
        or mode != _FEATURE_ATTRIBUTION_NEUTRALIZE_MODE
    ):
        reasons.append(_FEATURE_ATTRIBUTION_INVALID_REQUEST)
        _log_decision_event(
            "FEATURE_ATTRIBUTION_INVALID_REQUEST",
            request=request,
            selected_row_label=selected_row_label,
            mode=mode,
        )
        return None, _none_result(versions, reasons, state_out)

    return str(selected_row_label), None


def _with_min_edge_neutralized(cfg: dict[str, Any]) -> dict[str, Any]:
    thresholds = dict(cfg.get("thresholds") or {})
    thresholds["min_edge"] = 0.0
    cfg_overridden = dict(cfg)
    cfg_overridden["thresholds"] = thresholds
    return cfg_overridden


def _with_hysteresis_neutralized(cfg: dict[str, Any]) -> dict[str, Any]:
    gates = dict(cfg.get("gates") or {})
    gates["hysteresis_steps"] = 1
    cfg_overridden = dict(cfg)
    cfg_overridden["gates"] = gates
    return cfg_overridden


def _with_cooldown_neutralized(cfg: dict[str, Any]) -> dict[str, Any]:
    gates = dict(cfg.get("gates") or {})
    gates["cooldown_bars"] = 0
    cfg_overridden = dict(cfg)
    cfg_overridden["gates"] = gates
    return cfg_overridden


def _with_cooldown_state_neutralized(state_in: dict[str, Any]) -> dict[str, Any]:
    state_overridden = dict(state_in)
    state_overridden["cooldown_remaining"] = 0
    return state_overridden


def decide(
    policy: dict[str, Any],
    *,
    probas: dict[str, float] | None,
    confidence: dict[str, float] | None,
    regime: str | None,
    htf_regime: str | None = None,
    state: dict[str, Any] | None,
    risk_ctx: dict[str, Any] | None,
    cfg: dict[str, Any] | None,
) -> tuple[Action, dict[str, Any]]:
    """Beslutsfunktion (pure) med strikt gate-ordning."""
    log_fib_flow(
        "[FIB-FLOW] decide() called with cfg keys: %s",
        list((cfg or {}).keys())[:15],
        logger=_LOG,
    )

    reasons: list[str] = []
    versions: dict[str, Any] = {"decision": "v1"}
    cfg = dict(cfg or {})
    mtf_cfg = dict(cfg.get("multi_timeframe") or {})
    policy_symbol = str(policy.get("symbol") or "UNKNOWN")
    policy_timeframe = str(policy.get("timeframe") or "UNKNOWN")
    use_htf_block = bool(mtf_cfg.get("use_htf_block", True))
    allow_ltf_override_cfg = bool(mtf_cfg.get("allow_ltf_override"))
    ltf_override_threshold = safe_float(mtf_cfg.get("ltf_override_threshold", 0.85), 0.85)
    adaptive_cfg = dict(mtf_cfg.get("ltf_override_adaptive") or {})
    state_in = copy.deepcopy(state or {})
    state_out: dict[str, Any] = copy.deepcopy(state_in)
    override_state_in = state_in.get("ltf_override_state")
    override_state: dict[str, Any] = {}
    if isinstance(override_state_in, dict):
        for key, value in override_state_in.items():
            if isinstance(value, list):
                override_state[key] = list(value)
            else:
                override_state[key] = value
    state_out["ltf_override_state"] = override_state

    selected_feature_attribution_row, invalid_request_result = _resolve_feature_attribution_request(
        policy,
        reasons=reasons,
        versions=versions,
        state_out=state_out,
    )
    if invalid_request_result is not None:
        return invalid_request_result

    action, meta, candidate_data = select_candidate(
        policy=policy,
        probas=probas,
        regime=regime,
        risk_ctx=risk_ctx,
        cfg=cfg,
        state_in=state_in,
        state_out=state_out,
        reasons=reasons,
        versions=versions,
        log_decision_event=_log_decision_event,
    )
    if action is not None:
        return action, meta

    candidate = candidate_data["candidate"]
    fib_use_htf_block = use_htf_block
    if selected_feature_attribution_row == _FEATURE_ATTRIBUTION_HTF_BLOCK_ROW:
        fib_use_htf_block = False

    fib_action, fib_meta = apply_fib_gating(
        policy_symbol=policy_symbol,
        policy_timeframe=policy_timeframe,
        candidate=candidate,
        confidence=confidence,
        cfg=cfg,
        state_in=state_in,
        state_out=state_out,
        reasons=reasons,
        versions=versions,
        regime_str=candidate_data["regime_str"],
        use_htf_block=fib_use_htf_block,
        allow_ltf_override_cfg=allow_ltf_override_cfg,
        ltf_override_threshold=ltf_override_threshold,
        adaptive_cfg=adaptive_cfg,
        override_state=override_state,
        logger=_LOG,
        log_decision_event=_log_decision_event,
        log_fib_flow=log_fib_flow,
    )
    if fib_action is not None:
        return fib_action, fib_meta

    post_fib_cfg = cfg
    post_fib_state_in = state_in
    if selected_feature_attribution_row == _FEATURE_ATTRIBUTION_MIN_EDGE_ROW:
        post_fib_cfg = _with_min_edge_neutralized(cfg)
    elif selected_feature_attribution_row == _FEATURE_ATTRIBUTION_HYSTERESIS_ROW:
        post_fib_cfg = _with_hysteresis_neutralized(cfg)
    elif selected_feature_attribution_row == _FEATURE_ATTRIBUTION_COOLDOWN_ROW:
        post_fib_cfg = _with_cooldown_neutralized(cfg)
        post_fib_state_in = _with_cooldown_state_neutralized(state_in)

    action, meta, confidence_data = apply_post_fib_gates(
        candidate=candidate,
        confidence=confidence,
        cfg=post_fib_cfg,
        state_in=post_fib_state_in,
        state_out=state_out,
        reasons=reasons,
        versions=versions,
        default_thr=candidate_data["default_thr"],
        p_buy=candidate_data["p_buy"],
        p_sell=candidate_data["p_sell"],
        log_decision_event=_log_decision_event,
    )
    if action is not None:
        return action, meta

    size, conf_val_gate = apply_sizing(
        candidate=candidate,
        confidence=confidence or {},
        regime=regime,
        htf_regime=htf_regime,
        state_in=state_in,
        state_out=state_out,
        cfg=cfg,
        p_buy=candidate_data["p_buy"],
        p_sell=candidate_data["p_sell"],
        r_default=candidate_data["R"],
        max_ev=candidate_data["max_ev"],
        logger=_LOG,
        sanitize_context=_sanitize_context,
    )

    if size <= 0.0:
        _log_decision_event(
            "SIZE_ZERO",
            candidate=candidate,
            confidence=confidence_data["conf_val_gate"],
            risk_map=(cfg.get("risk") or {}).get("risk_map", []),
        )

    state_out["last_action"] = candidate
    if selected_feature_attribution_row == _FEATURE_ATTRIBUTION_COOLDOWN_ROW:
        state_out.pop("cooldown_remaining", None)

    cooldown_bars = int((post_fib_cfg.get("gates") or {}).get("cooldown_bars") or 0)
    if cooldown_bars > 0:
        state_out["cooldown_remaining"] = cooldown_bars

    state_out["zone_debug"] = candidate_data["zone_debug"]
    reasons.append("ENTRY_LONG" if candidate == "LONG" else "ENTRY_SHORT")

    meta = {
        "versions": versions,
        "reasons": reasons,
        "size": size,
        "state_out": state_out,
    }

    _log_decision_event(
        "ENTRY",
        candidate=candidate,
        size=size,
        confidence=conf_val_gate,
        cooldown=state_out.get("cooldown_remaining"),
    )
    return candidate, meta
