from __future__ import annotations

from typing import Any

from core.config.authority_mode_resolver import (
    AUTHORITY_MODE_REGIME_MODULE as _AUTHORITY_MODE_REGIME_MODULE,
)
from core.config.authority_mode_resolver import (
    resolve_authority_mode_permissive as _resolve_authority_mode_permissive,
)
from core.config.authority_mode_resolver import (
    resolve_authority_mode_with_source_permissive as _resolve_authority_mode_with_source_permissive,
)
from core.intelligence.regime.authority import (
    detect_authoritative_regime_legacy as _detect_intelligence_authoritative_regime_legacy,
)
from core.intelligence.regime.authority import (
    normalize_authoritative_regime as _normalize_intelligence_authoritative_regime,
)
from core.intelligence.regime.clarity import (
    compute_clarity_score_v1 as _compute_intelligence_clarity_score_v1,
)
from core.intelligence.regime.htf import (
    compute_htf_regime as _compute_intelligence_htf_regime,
)


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _normalize_weights(weights: dict[str, Any]) -> dict[str, float]:
    normalized: dict[str, float] = {}
    for key in ("confidence", "edge", "ev", "regime_alignment"):
        raw = _safe_float(weights.get(key))
        normalized[key] = max(0.0, float(raw if raw is not None else 0.0))
    total = sum(normalized.values())
    if total <= 0.0:
        return {
            "confidence": 0.5,
            "edge": 0.2,
            "ev": 0.2,
            "regime_alignment": 0.1,
        }
    return {k: v / total for k, v in normalized.items()}


def _round_half_even_0_100(value: float) -> int:
    clamped = max(0.0, min(100.0, float(value)))
    # Python round() is deterministic bankers rounding (half-even).
    return int(round(clamped))


def compute_clarity_score_v1(
    *,
    confidence_gate: float,
    edge: float,
    max_ev: float,
    r_default: float,
    candidate: str,
    regime: str,
    weights: dict[str, Any] | None = None,
    weights_version: str = "weights_v1",
) -> dict[str, Any]:
    """Compute deterministic clarity score in [0,100] for sizing-only modulation.

    Legacy public shim retained for runtime compatibility during tranche-1
    migration to the intelligence layer.
    """

    return _compute_intelligence_clarity_score_v1(
        confidence_gate=confidence_gate,
        edge=edge,
        max_ev=max_ev,
        r_default=r_default,
        candidate=candidate,
        regime=regime,
        weights=weights,
        weights_version=weights_version,
    ).to_legacy_payload()


def compute_htf_regime(
    htf_fib_data: dict[str, Any] | None,
    current_price: float | None = None,
) -> str:
    """Legacy public shim retained for runtime compatibility during HTF tranche migration."""

    return _compute_intelligence_htf_regime(
        htf_fib_data,
        current_price=current_price,
    )


def detect_shadow_regime_from_regime_module(candles: dict[str, Any]) -> str | None:
    """Compute regime.py observer value in shadow-only mode."""
    try:
        from core.strategy.regime import detect_regime_from_candles

        return str(detect_regime_from_candles(candles))
    except Exception:
        return None


def resolve_authority_mode_with_source(configs: dict[str, Any] | None) -> tuple[str, str]:
    return _resolve_authority_mode_with_source_permissive(configs)


def resolve_authority_mode(configs: dict[str, Any] | None) -> str:
    """Resolve configured regime authority mode with safe legacy fallback."""

    return _resolve_authority_mode_permissive(configs)


def _detect_authoritative_regime_legacy(
    candles: dict[str, Any],
    configs: dict[str, Any],
) -> str:
    from core.strategy import regime_unified as _regime_unified

    return _detect_intelligence_authoritative_regime_legacy(
        candles,
        configs,
        fallback_detect_regime_unified=lambda fallback_candles: _regime_unified.detect_regime_unified(
            fallback_candles,
            ema_period=50,
        ),
    )


def detect_authoritative_regime(
    candles: dict[str, Any],
    configs: dict[str, Any],
) -> str:
    """Return authoritative regime for evaluate decision path.

    Default authority path is legacy (precomputed EMA50 / regime_unified).
    When configured with `multi_timeframe.regime_intelligence.authority_mode=regime_module`
    (or compatibility alias `regime_unified.authority_mode=regime_module`),
    authority switches explicitly to `regime.detect_regime_from_candles`.
    """
    authority_mode = resolve_authority_mode(configs)
    if authority_mode == _AUTHORITY_MODE_REGIME_MODULE:
        observed = detect_shadow_regime_from_regime_module(candles)
        return _normalize_intelligence_authoritative_regime(observed)

    return _detect_authoritative_regime_legacy(candles, configs)


def compute_risk_state_multiplier(
    *,
    cfg: dict[str, Any],
    equity_drawdown_pct: float,
    bars_since_regime_change: int,
) -> dict[str, Any]:
    """Compute position size multiplier based on current risk state.

    Returns a dict with 'multiplier' (float in [0.05, 1.0]) plus debug keys.
    """
    if not cfg or not bool(cfg.get("enabled", False)):
        return {
            "enabled": False,
            "multiplier": 1.0,
            "drawdown_mult": 1.0,
            "transition_mult": 1.0,
            "equity_drawdown_pct": equity_drawdown_pct,
            "bars_since_regime_change": bars_since_regime_change,
        }

    dd_cfg = dict(cfg.get("drawdown_guard") or {})
    soft_thr = float(dd_cfg.get("soft_threshold", 0.03))
    hard_thr = float(dd_cfg.get("hard_threshold", 0.06))
    soft_mult = float(dd_cfg.get("soft_mult", 0.70))
    hard_mult = float(dd_cfg.get("hard_mult", 0.40))

    # Linear interpolation between thresholds
    dd = float(equity_drawdown_pct)
    if dd <= 0.0:
        drawdown_mult = 1.0
    elif dd >= hard_thr:
        drawdown_mult = hard_mult
    elif dd >= soft_thr:
        t = (dd - soft_thr) / max(hard_thr - soft_thr, 1e-9)
        drawdown_mult = soft_mult + t * (hard_mult - soft_mult)
    else:
        t = dd / max(soft_thr, 1e-9)
        drawdown_mult = 1.0 + t * (soft_mult - 1.0)

    tr_cfg = dict(cfg.get("transition_guard") or {})
    transition_mult = 1.0
    if bool(tr_cfg.get("enabled", True)):
        guard_bars = int(tr_cfg.get("guard_bars", 4))
        if 0 < bars_since_regime_change <= guard_bars:
            transition_mult = float(tr_cfg.get("mult", 0.60))

    multiplier = max(0.05, min(1.0, drawdown_mult * transition_mult))

    return {
        "enabled": True,
        "multiplier": multiplier,
        "drawdown_mult": drawdown_mult,
        "transition_mult": transition_mult,
        "equity_drawdown_pct": dd,
        "bars_since_regime_change": bars_since_regime_change,
    }
