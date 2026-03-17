from __future__ import annotations

from core.intelligence.collection.interface import IntelligenceCollector
from core.intelligence.evaluation.interface import EvaluationRequest, IntelligenceEvaluator
from core.intelligence.features.interface import (
    FeatureExtractionRequest,
    IntelligenceFeatureExtractor,
)
from core.intelligence.ledger_adapter.interface import (
    IntelligenceLedgerAdapter,
    LedgerPersistenceRequest,
)
from core.intelligence.normalization.interface import (
    IntelligenceNormalizer,
    NormalizationRequest,
)
from core.intelligence.parameter.interface import (
    ParameterAnalysisRequest,
    ParameterIntelligenceAnalyzer,
)
from core.research_orchestrator.models import ResearchResult, ResearchStageOutputs, ResearchTask


class ResearchOrchestrationError(ValueError):
    """Raised when deterministic orchestration cannot satisfy downstream contracts."""


def _validate_task(task: ResearchTask) -> None:
    if not task.task_id.strip():
        raise ResearchOrchestrationError("task_id must be non-empty")
    if not task.approved_parameter_sets:
        raise ResearchOrchestrationError("approved_parameter_sets must not be empty")


def orchestrate_research_task(
    task: ResearchTask,
    *,
    collector: IntelligenceCollector,
    normalizer: IntelligenceNormalizer,
    feature_extractor: IntelligenceFeatureExtractor,
    evaluator: IntelligenceEvaluator,
    parameter_analyzer: ParameterIntelligenceAnalyzer,
    ledger_adapter: IntelligenceLedgerAdapter,
) -> ResearchResult:
    """Run the deterministic research workflow using injected stable components only."""

    _validate_task(task)

    collected_events = collector.collect(task.collection_request)
    if not collected_events:
        raise ResearchOrchestrationError("collection produced no events")

    normalized_events = normalizer.normalize(NormalizationRequest(events=collected_events))
    if not normalized_events:
        raise ResearchOrchestrationError("normalization produced no events")

    feature_sets = feature_extractor.extract(FeatureExtractionRequest(events=normalized_events))
    if not feature_sets:
        raise ResearchOrchestrationError("feature extraction produced no feature sets")

    evaluations = evaluator.evaluate(EvaluationRequest(feature_sets=feature_sets))
    if not evaluations:
        raise ResearchOrchestrationError("evaluation produced no results")

    parameter_recommendations = parameter_analyzer.analyze(
        ParameterAnalysisRequest(
            evaluations=evaluations,
            approved_parameter_sets=task.approved_parameter_sets,
        )
    )
    if not parameter_recommendations:
        raise ResearchOrchestrationError("parameter analysis produced no recommendations")

    persistence_result = ledger_adapter.persist_events(
        LedgerPersistenceRequest(events=normalized_events)
    )
    if not persistence_result.persisted_event_ids:
        raise ResearchOrchestrationError("ledger persistence produced no persisted_event_ids")

    stage_outputs = ResearchStageOutputs(
        collected_events=collected_events,
        normalized_events=normalized_events,
        feature_sets=feature_sets,
        evaluations=evaluations,
        parameter_recommendations=parameter_recommendations,
        persistence_result=persistence_result,
    )
    preferred_parameter_set_ids = tuple(
        recommendation.parameter_set_id
        for recommendation in parameter_recommendations
        if recommendation.advisory_disposition == "preferred"
    )
    return ResearchResult(
        task_id=task.task_id,
        stage_outputs=stage_outputs,
        recommended_parameter_set_ids=tuple(
            recommendation.parameter_set_id for recommendation in parameter_recommendations
        ),
        preferred_parameter_set_ids=preferred_parameter_set_ids,
        top_advisory_parameter_set_id=parameter_recommendations[0].parameter_set_id,
    )
