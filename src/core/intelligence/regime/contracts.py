from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar


@dataclass(frozen=True, slots=True)
class ClarityClamp:
    min: float = 0.0
    max: float = 100.0

    def to_legacy_payload(self) -> dict[str, float]:
        return {"min": float(self.min), "max": float(self.max)}


@dataclass(frozen=True, slots=True)
class ClarityScoreComponents:
    confidence: float
    edge: float
    ev: float
    regime_alignment: float

    def to_legacy_payload(self) -> dict[str, float]:
        return {
            "confidence": float(self.confidence),
            "edge": float(self.edge),
            "ev": float(self.ev),
            "regime_alignment": float(self.regime_alignment),
        }


@dataclass(frozen=True, slots=True)
class ClarityScoreRequest:
    confidence_gate: float
    edge: float
    max_ev: float
    r_default: float
    candidate: str
    regime: str
    weights: dict[str, Any] | None = None
    weights_version: str = "weights_v1"

    @classmethod
    def from_legacy_inputs(
        cls,
        *,
        confidence_gate: float,
        edge: float,
        max_ev: float,
        r_default: float,
        candidate: str,
        regime: str,
        weights: dict[str, Any] | None = None,
        weights_version: str = "weights_v1",
    ) -> ClarityScoreRequest:
        return cls(
            confidence_gate=confidence_gate,
            edge=edge,
            max_ev=max_ev,
            r_default=r_default,
            candidate=candidate,
            regime=regime,
            weights=weights,
            weights_version=weights_version,
        )


@dataclass(frozen=True, slots=True)
class ClarityScoreResult:
    components: ClarityScoreComponents
    weights: dict[str, float]
    weights_version: str
    clarity_raw: float
    clarity_scaled: float
    clarity_score: int
    round_policy: str = "half_even"
    clamp: ClarityClamp = ClarityClamp()

    def to_legacy_payload(self) -> dict[str, Any]:
        return {
            "components": self.components.to_legacy_payload(),
            "weights": {key: float(value) for key, value in self.weights.items()},
            "weights_version": str(self.weights_version),
            "clarity_raw": float(self.clarity_raw),
            "clarity_scaled": float(self.clarity_scaled),
            "clarity_score": int(self.clarity_score),
            "round_policy": str(self.round_policy),
            "clamp": self.clamp.to_legacy_payload(),
        }


@dataclass(frozen=True, slots=True)
class ShadowRegimeObservability:
    authoritative_source: str
    shadow_source: str
    authority_mode: str
    authority_mode_source: str
    authority: str
    shadow: str | None
    mismatch: bool | None
    decision_input: bool

    _EVIDENCE_FILE_NAMES: ClassVar[tuple[str, ...]] = (
        "clarity_histogram.json",
        "clarity_quantiles.json",
        "shadow_samples.ndjson",
    )

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> ShadowRegimeObservability:
        shadow = payload.get("shadow")
        mismatch = payload.get("mismatch")
        return cls(
            authoritative_source=str(payload["authoritative_source"]),
            shadow_source=str(payload["shadow_source"]),
            authority_mode=str(payload["authority_mode"]),
            authority_mode_source=str(payload["authority_mode_source"]),
            authority=str(payload["authority"]),
            shadow=(str(shadow) if shadow is not None else None),
            mismatch=(bool(mismatch) if mismatch is not None else None),
            decision_input=bool(payload["decision_input"]),
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "authoritative_source": str(self.authoritative_source),
            "shadow_source": str(self.shadow_source),
            "authority_mode": str(self.authority_mode),
            "authority_mode_source": str(self.authority_mode_source),
            "authority": str(self.authority),
            "shadow": (str(self.shadow) if self.shadow is not None else None),
            "mismatch": self.mismatch,
            "decision_input": bool(self.decision_input),
        }

    @classmethod
    def expected_evidence_file_names(cls) -> tuple[str, ...]:
        return cls._EVIDENCE_FILE_NAMES
