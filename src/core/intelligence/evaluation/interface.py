from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TypeAlias

from core.intelligence.features.interface import IntelligenceFeatureSet

EvaluationResult: TypeAlias = tuple["IntelligenceEvaluation", ...]


@dataclass(frozen=True, slots=True)
class IntelligenceEvaluation:
    event_id: str
    disposition: str
    score: float
    rationale: str


@dataclass(frozen=True, slots=True)
class EvaluationRequest:
    feature_sets: tuple[IntelligenceFeatureSet, ...]


class IntelligenceEvaluator(Protocol):
    def evaluate(self, request: EvaluationRequest) -> EvaluationResult: ...
