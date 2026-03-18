from __future__ import annotations

from dataclasses import dataclass

from core.intelligence.collection.interface import CollectionRequest
from core.intelligence.parameter import (
    ApprovedParameterSet,
    ParameterAnalysisRequest,
    ParameterAnalysisResult,
    ParameterIntelligenceAnalyzer,
)
from core.research_orchestrator.models import ResearchResult, ResearchTask
from core.research_orchestrator.orchestrator import DeterministicResearchOrchestrator
from core.strategy.family_registry import StrategyFamily, validate_cross_family_promotion


@dataclass(frozen=True, slots=True)
class FamilyResearchTask:
    strategy_family: StrategyFamily
    task_id: str
    collection_request: CollectionRequest
    approved_parameter_sets: tuple[ApprovedParameterSet, ...]

    def to_research_task(self) -> ResearchTask:
        return ResearchTask(
            task_id=self.task_id,
            collection_request=self.collection_request,
            approved_parameter_sets=self.approved_parameter_sets,
        )


@dataclass(frozen=True, slots=True)
class FamilyParameterBatch:
    strategy_family: StrategyFamily
    approved_parameter_sets: tuple[ApprovedParameterSet, ...]


def run_family_research_tasks(
    orchestrator: DeterministicResearchOrchestrator,
    tasks: tuple[FamilyResearchTask, ...],
) -> dict[StrategyFamily, tuple[ResearchResult, ...]]:
    grouped: dict[StrategyFamily, list[ResearchResult]] = {}
    for family_task in tasks:
        grouped.setdefault(family_task.strategy_family, []).append(
            orchestrator.run(family_task.to_research_task())
        )
    return {family: tuple(results) for family, results in grouped.items()}


def analyze_parameter_batches_by_family(
    analyzer: ParameterIntelligenceAnalyzer,
    *,
    evaluations,
    family_batches: tuple[FamilyParameterBatch, ...],
) -> dict[StrategyFamily, ParameterAnalysisResult]:
    return {
        batch.strategy_family: analyzer.analyze(
            ParameterAnalysisRequest(
                evaluations=evaluations,
                approved_parameter_sets=batch.approved_parameter_sets,
            )
        )
        for batch in family_batches
    }


def require_explicit_cross_family_override(
    source_family: StrategyFamily,
    target_family: StrategyFamily,
    *,
    explicit_override: bool = False,
    governance_signoff: bool = False,
) -> None:
    validate_cross_family_promotion(
        source_family,
        target_family,
        explicit_override=explicit_override,
        governance_signoff=governance_signoff,
    )


__all__ = [
    "FamilyParameterBatch",
    "FamilyResearchTask",
    "analyze_parameter_batches_by_family",
    "require_explicit_cross_family_override",
    "run_family_research_tasks",
]
