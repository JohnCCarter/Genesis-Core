from __future__ import annotations

from dataclasses import dataclass

from core.intelligence.collection.interface import CollectionRequest, CollectionResult
from core.intelligence.evaluation.interface import EvaluationResult
from core.intelligence.features.interface import FeatureExtractionResult
from core.intelligence.ledger_adapter.interface import LedgerPersistenceResult
from core.intelligence.normalization.interface import NormalizationResult
from core.intelligence.parameter.interface import ApprovedParameterSet, ParameterAnalysisResult


@dataclass(frozen=True, slots=True)
class ResearchTask:
    task_id: str
    collection_request: CollectionRequest
    approved_parameter_sets: tuple[ApprovedParameterSet, ...]


@dataclass(frozen=True, slots=True)
class ResearchStageOutputs:
    collected_events: CollectionResult
    normalized_events: NormalizationResult
    feature_sets: FeatureExtractionResult
    evaluations: EvaluationResult
    parameter_recommendations: ParameterAnalysisResult
    persistence_result: LedgerPersistenceResult


@dataclass(frozen=True, slots=True)
class ResearchResult:
    task_id: str
    stage_outputs: ResearchStageOutputs
    recommended_parameter_set_ids: tuple[str, ...]
    preferred_parameter_set_ids: tuple[str, ...]
    top_advisory_parameter_set_id: str | None
