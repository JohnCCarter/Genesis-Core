from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TypeAlias

from core.intelligence.evaluation.interface import IntelligenceEvaluation
from core.intelligence.events.models import JsonObject

ParameterAnalysisResult: TypeAlias = tuple["ParameterRecommendation", ...]


@dataclass(frozen=True, slots=True)
class ApprovedParameterSet:
    parameter_set_id: str
    parameters: JsonObject
    sensitivity_score: float
    stability_score: float
    consistency_score: float
    source_ledger_entity_ids: tuple[str, ...] = ()
    baseline_weight: float = 1.0
    risk_multiplier: float = 1.0


@dataclass(frozen=True, slots=True)
class ParameterAnalysisRequest:
    evaluations: tuple[IntelligenceEvaluation, ...]
    approved_parameter_sets: tuple[ApprovedParameterSet, ...]


@dataclass(frozen=True, slots=True)
class ParameterRecommendation:
    parameter_set_id: str
    advisory_score: float
    sensitivity_score: float
    stability_score: float
    consistency_score: float
    weighting_suggestion: float
    risk_multiplier_suggestion: float
    advisory_disposition: str
    rationale: str
    supporting_event_ids: tuple[str, ...]
    source_ledger_entity_ids: tuple[str, ...] = ()


class ParameterIntelligenceAnalyzer(Protocol):
    def analyze(self, request: ParameterAnalysisRequest) -> ParameterAnalysisResult: ...
