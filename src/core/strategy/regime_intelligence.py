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

    Contract:
    - all components normalized to [0,1]
    - weighted sum with non-negative normalized weights
    - score conversion uses explicit half-even rounding policy
    """

    candidate_norm = str(candidate or "").strip().upper()
    regime_norm = str(regime or "balanced").strip().lower()

    confidence_component = _clamp01(confidence_gate)
    edge_component = _clamp01(edge)

    ev_denom = abs(float(r_default)) if abs(float(r_default)) > 1e-12 else 1.0
    ev_component = _clamp01(max_ev / ev_denom)

    if regime_norm in {"bull", "trend"}:
        regime_alignment_component = 1.0 if candidate_norm == "LONG" else 0.0
    elif regime_norm == "bear":
        regime_alignment_component = 1.0 if candidate_norm == "SHORT" else 0.0
    else:
        regime_alignment_component = 0.5

    use_weights = _normalize_weights(dict(weights or {}))
    raw = (
        use_weights["confidence"] * confidence_component
        + use_weights["edge"] * edge_component
        + use_weights["ev"] * ev_component
        + use_weights["regime_alignment"] * regime_alignment_component
    )
    clarity_raw = _clamp01(raw)
    clarity_scaled = clarity_raw * 100.0
    clarity_score = _round_half_even_0_100(clarity_scaled)

    return {
        "components": {
            "confidence": confidence_component,
            "edge": edge_component,
            "ev": ev_component,
            "regime_alignment": regime_alignment_component,
        },
        "weights": use_weights,
        "weights_version": weights_version,
        "clarity_raw": clarity_raw,
        "clarity_scaled": clarity_scaled,
        "clarity_score": clarity_score,
        "round_policy": "half_even",
        "clamp": {"min": 0.0, "max": 100.0},
    }


def compute_htf_regime(
    htf_fib_data: dict[str, Any] | None,
    current_price: float | None = None,
) -> str:
    """Compute regime from HTF (1D) Fibonacci context for defensive sizing."""
    if not htf_fib_data or not isinstance(htf_fib_data, dict):
        return "unknown"

    if not htf_fib_data.get("available"):
        return "unknown"

    if current_price is None or current_price <= 0:
        return "unknown"

    swing_high = _safe_float(htf_fib_data.get("swing_high"))
    swing_low = _safe_float(htf_fib_data.get("swing_low"))

    if swing_high is None or swing_low is None:
        return "unknown"

    if swing_high <= swing_low:
        return "unknown"

    swing_range = swing_high - swing_low
    position_in_range = (current_price - swing_low) / swing_range

    if position_in_range >= 0.618:
        return "bull"
    elif position_in_range <= 0.382:
        return "bear"
    else:
        return "ranging"


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
    pre = dict(configs.get("precomputed_features") or {})
    ema50 = pre.get("ema_50")
    closes = candles.get("close") if isinstance(candles, dict) else None

    ema_idx: int | None = None
    if "_global_index" in configs:
        try:
            ema_idx = int(configs.get("_global_index"))
        except (TypeError, ValueError):
            ema_idx = None
    if ema_idx is None and closes is not None:
        ema_idx = len(closes) - 1

    if (
        isinstance(ema50, list | tuple)
        and (closes is not None)
        and (ema_idx is not None)
        and 0 <= ema_idx < len(ema50)
    ):
        current_price = float(closes[-1])
        current_ema = float(ema50[ema_idx])
        if current_ema != 0:
            trend = (current_price - current_ema) / current_ema
            if trend > 0.02:
                return "bull"
            elif trend < -0.02:
                return "bear"
            else:
                return "ranging"
        return "balanced"

    from core.strategy import regime_unified as _regime_unified

    return _regime_unified.detect_regime_unified(candles, ema_period=50)


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
        normalized = str(observed).strip().lower() if observed is not None else ""
        if normalized in {"bull", "bear", "ranging", "balanced"}:
            return normalized
        return "balanced"

    return _detect_authoritative_regime_legacy(candles, configs)
