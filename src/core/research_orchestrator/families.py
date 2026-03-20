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
from core.strategy.family_registry import (
    StrategyFamily,
    StrategyFamilyValidationError,
    validate_cross_family_promotion,
    validate_strategy_family_name,
)


def _validate_parameter_set_strategy_family(
    parameter_set: ApprovedParameterSet,
    *,
    expected_family: StrategyFamily,
) -> None:
    parameters = parameter_set.parameters
    declared_family = parameters.get("strategy_family") if isinstance(parameters, dict) else None
    if declared_family is None:
        raise StrategyFamilyValidationError("approved_parameter_set_missing_strategy_family")
    resolved_family = validate_strategy_family_name(declared_family)
    if resolved_family != expected_family:
        raise StrategyFamilyValidationError("approved_parameter_set_family_mismatch")


def _validate_parameter_sets_strategy_family(
    approved_parameter_sets: tuple[ApprovedParameterSet, ...],
    *,
    expected_family: StrategyFamily,
) -> None:
    for parameter_set in approved_parameter_sets:
        _validate_parameter_set_strategy_family(
            parameter_set,
            expected_family=expected_family,
        )


@dataclass(frozen=True, slots=True)
class FamilyResearchTask:
    strategy_family: StrategyFamily
    task_id: str
    collection_request: CollectionRequest
    approved_parameter_sets: tuple[ApprovedParameterSet, ...]

    def to_research_task(self) -> ResearchTask:
        _validate_parameter_sets_strategy_family(
            self.approved_parameter_sets,
            expected_family=self.strategy_family,
        )
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


def _sorted_unique_ids(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted({value for value in values if value})


def _ordered_unique_non_null_ids(values: tuple[str | None, ...] | list[str | None]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value is None or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def build_family_run_manifest(
    results_by_family: dict[StrategyFamily, tuple[ResearchResult, ...]],
) -> dict[str, object]:
    """Build a deterministic, machine-readable summary of grouped family research results."""

    families = sorted(results_by_family)
    family_runs: dict[str, dict[str, object]] = {}
    for family in families:
        results = results_by_family[family]
        family_runs[family] = {
            "result_count": len(results),
            "task_ids": [result.task_id for result in results],
            "recommended_parameter_set_ids": _sorted_unique_ids(
                [
                    parameter_set_id
                    for result in results
                    for parameter_set_id in result.recommended_parameter_set_ids
                ]
            ),
            "preferred_parameter_set_ids": _sorted_unique_ids(
                [
                    parameter_set_id
                    for result in results
                    for parameter_set_id in result.preferred_parameter_set_ids
                ]
            ),
            "top_advisory_parameter_set_ids": _ordered_unique_non_null_ids(
                [result.top_advisory_parameter_set_id for result in results]
            ),
        }

    return {
        "families": families,
        "family_runs": family_runs,
    }


def build_family_comparison_summary(
    results_by_family: dict[StrategyFamily, tuple[ResearchResult, ...]],
) -> dict[str, object]:
    """Build an advisory-only deterministic comparison summary over grouped family results.

    This helper does not perform promotion decisions or rejection authority. It only
    summarizes already-grouped family outputs; invalid family combinations fail
    before grouped results are constructed, so `hybrid_probe_findings` remains empty.
    """

    families = sorted(results_by_family)
    intra_family_rankings: dict[str, dict[str, object]] = {}
    cross_family_representatives: list[dict[str, str]] = []

    for family in families:
        results = results_by_family[family]
        top_advisory_parameter_set_ids = _ordered_unique_non_null_ids(
            [result.top_advisory_parameter_set_id for result in results]
        )
        intra_family_rankings[family] = {
            "top_advisory_parameter_set_ids": top_advisory_parameter_set_ids,
            "recommended_parameter_set_ids": _sorted_unique_ids(
                [
                    parameter_set_id
                    for result in results
                    for parameter_set_id in result.recommended_parameter_set_ids
                ]
            ),
            "preferred_parameter_set_ids": _sorted_unique_ids(
                [
                    parameter_set_id
                    for result in results
                    for parameter_set_id in result.preferred_parameter_set_ids
                ]
            ),
        }
        if top_advisory_parameter_set_ids:
            cross_family_representatives.append(
                {
                    "strategy_family": family,
                    "top_advisory_parameter_set_id": top_advisory_parameter_set_ids[0],
                }
            )

    return {
        "families": families,
        "intra_family_rankings": intra_family_rankings,
        "cross_family_representatives": cross_family_representatives,
        "advisory_representatives": list(cross_family_representatives),
        "hybrid_probe_findings": [],
    }


def analyze_parameter_batches_by_family(
    analyzer: ParameterIntelligenceAnalyzer,
    *,
    evaluations,
    family_batches: tuple[FamilyParameterBatch, ...],
) -> dict[StrategyFamily, ParameterAnalysisResult]:
    grouped_parameter_sets: dict[StrategyFamily, list[ApprovedParameterSet]] = {}
    for batch in family_batches:
        _validate_parameter_sets_strategy_family(
            batch.approved_parameter_sets,
            expected_family=batch.strategy_family,
        )
        grouped_parameter_sets.setdefault(batch.strategy_family, []).extend(
            batch.approved_parameter_sets
        )

    return {
        strategy_family: analyzer.analyze(
            ParameterAnalysisRequest(
                evaluations=evaluations,
                approved_parameter_sets=tuple(approved_parameter_sets),
            )
        )
        for strategy_family, approved_parameter_sets in grouped_parameter_sets.items()
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
    "build_family_comparison_summary",
    "build_family_run_manifest",
    "require_explicit_cross_family_override",
    "run_family_research_tasks",
]
