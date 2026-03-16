from __future__ import annotations

from typing import Any

from core.intelligence.regime.contracts import (
    ClarityScoreComponents,
    ClarityScoreRequest,
    ClarityScoreResult,
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
    return {key: value / total for key, value in normalized.items()}


def _round_half_even_0_100(value: float) -> int:
    clamped = max(0.0, min(100.0, float(value)))
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
) -> ClarityScoreResult:
    request = ClarityScoreRequest.from_legacy_inputs(
        confidence_gate=confidence_gate,
        edge=edge,
        max_ev=max_ev,
        r_default=r_default,
        candidate=candidate,
        regime=regime,
        weights=weights,
        weights_version=weights_version,
    )

    candidate_norm = str(request.candidate or "").strip().upper()
    regime_norm = str(request.regime or "balanced").strip().lower()

    confidence_component = _clamp01(request.confidence_gate)
    edge_component = _clamp01(request.edge)

    ev_denom = abs(float(request.r_default)) if abs(float(request.r_default)) > 1e-12 else 1.0
    ev_component = _clamp01(request.max_ev / ev_denom)

    if regime_norm in {"bull", "trend"}:
        regime_alignment_component = 1.0 if candidate_norm == "LONG" else 0.0
    elif regime_norm == "bear":
        regime_alignment_component = 1.0 if candidate_norm == "SHORT" else 0.0
    else:
        regime_alignment_component = 0.5

    use_weights = _normalize_weights(dict(request.weights or {}))
    raw = (
        use_weights["confidence"] * confidence_component
        + use_weights["edge"] * edge_component
        + use_weights["ev"] * ev_component
        + use_weights["regime_alignment"] * regime_alignment_component
    )
    clarity_raw = _clamp01(raw)
    clarity_scaled = clarity_raw * 100.0
    clarity_score = _round_half_even_0_100(clarity_scaled)

    return ClarityScoreResult(
        components=ClarityScoreComponents(
            confidence=confidence_component,
            edge=edge_component,
            ev=ev_component,
            regime_alignment=regime_alignment_component,
        ),
        weights=use_weights,
        weights_version=request.weights_version,
        clarity_raw=clarity_raw,
        clarity_scaled=clarity_scaled,
        clarity_score=clarity_score,
    )
