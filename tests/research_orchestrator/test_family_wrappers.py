from __future__ import annotations

import pytest

from core.intelligence.collection import CollectionRequest
from core.intelligence.evaluation import IntelligenceEvaluation
from core.intelligence.parameter import (
    ApprovedParameterSet,
    DeterministicParameterIntelligenceAnalyzer,
    ParameterAnalysisRequest,
    ParameterAnalysisValidationError,
    ParameterRecommendation,
)
from core.research_orchestrator import (
    FamilyParameterBatch,
    FamilyResearchTask,
    require_explicit_cross_family_override,
    run_family_research_tasks,
)
from core.research_orchestrator.families import analyze_parameter_batches_by_family
from tests.helpers.research_system import build_event, build_orchestrator, build_service


def _parameter_set(parameter_set_id: str) -> ApprovedParameterSet:
    return ApprovedParameterSet(
        parameter_set_id=parameter_set_id,
        parameters={"ema_fast": 9, "ema_slow": 21, "parameter_set_id": parameter_set_id},
        sensitivity_score=0.2,
        stability_score=0.9,
        consistency_score=0.8,
        source_ledger_entity_ids=(f"ART-2026-{parameter_set_id[-1:]}001",),
    )


class _RecordingAnalyzer:
    def __init__(self) -> None:
        self.calls: list[ParameterAnalysisRequest] = []

    def analyze(self, request: ParameterAnalysisRequest):
        self.calls.append(request)
        return tuple(
            ParameterRecommendation(
                parameter_set_id=parameter_set.parameter_set_id,
                advisory_score=0.5,
                sensitivity_score=parameter_set.sensitivity_score,
                stability_score=parameter_set.stability_score,
                consistency_score=parameter_set.consistency_score,
                weighting_suggestion=parameter_set.baseline_weight,
                risk_multiplier_suggestion=parameter_set.risk_multiplier,
                advisory_disposition="review",
                rationale=f"stub:{parameter_set.parameter_set_id}",
                supporting_event_ids=tuple(item.event_id for item in request.evaluations),
                source_ledger_entity_ids=parameter_set.source_ledger_entity_ids,
            )
            for parameter_set in request.approved_parameter_sets
        )


def test_run_family_research_tasks_keeps_results_grouped_by_family(tmp_path) -> None:
    service = build_service(tmp_path)
    orchestrator = build_orchestrator(
        service=service,
        input_events=(build_event(1), build_event(2)),
    )
    collection_request = CollectionRequest(source="news", asset="tBTCUSD", topic="macro")
    tasks = (
        FamilyResearchTask(
            strategy_family="legacy",
            task_id="legacy-task-001",
            collection_request=collection_request,
            approved_parameter_sets=(_parameter_set("ps-legacy"),),
        ),
        FamilyResearchTask(
            strategy_family="ri",
            task_id="ri-task-001",
            collection_request=collection_request,
            approved_parameter_sets=(_parameter_set("ps-ri"),),
        ),
    )

    results = run_family_research_tasks(orchestrator, tasks)

    assert tuple(sorted(results.keys())) == ("legacy", "ri")
    assert results["legacy"][0].task_id == "legacy-task-001"
    assert results["ri"][0].task_id == "ri-task-001"


def test_analyze_parameter_batches_by_family_does_not_mix_families_by_default() -> None:
    evaluations = (
        IntelligenceEvaluation(
            event_id="intel-tbtcusd-20260317-0001",
            disposition="high_priority",
            score=0.8,
            rationale="Family separated",
        ),
    )
    analyzer = DeterministicParameterIntelligenceAnalyzer()
    results = analyze_parameter_batches_by_family(
        analyzer,
        evaluations=evaluations,
        family_batches=(
            FamilyParameterBatch(
                strategy_family="legacy", approved_parameter_sets=(_parameter_set("ps-a"),)
            ),
            FamilyParameterBatch(
                strategy_family="ri", approved_parameter_sets=(_parameter_set("ps-b"),)
            ),
        ),
    )

    assert tuple(sorted(results.keys())) == ("legacy", "ri")
    assert results["legacy"][0].parameter_set_id == "ps-a"
    assert results["ri"][0].parameter_set_id == "ps-b"


def test_analyze_parameter_batches_by_family_merges_same_family_batches_once() -> None:
    evaluations = (
        IntelligenceEvaluation(
            event_id="intel-tbtcusd-20260317-0002",
            disposition="high_priority",
            score=0.8,
            rationale="Same-family batches should aggregate.",
        ),
    )
    analyzer = _RecordingAnalyzer()

    results = analyze_parameter_batches_by_family(
        analyzer,
        evaluations=evaluations,
        family_batches=(
            FamilyParameterBatch(
                strategy_family="legacy",
                approved_parameter_sets=(_parameter_set("ps-a"),),
            ),
            FamilyParameterBatch(
                strategy_family="legacy",
                approved_parameter_sets=(_parameter_set("ps-c"),),
            ),
            FamilyParameterBatch(
                strategy_family="ri",
                approved_parameter_sets=(_parameter_set("ps-b"),),
            ),
        ),
    )

    assert tuple(sorted(results.keys())) == ("legacy", "ri")
    assert [item.parameter_set_id for item in results["legacy"]] == ["ps-a", "ps-c"]
    assert [item.parameter_set_id for item in results["ri"]] == ["ps-b"]
    assert len(analyzer.calls) == 2
    assert [item.parameter_set_id for item in analyzer.calls[0].approved_parameter_sets] == [
        "ps-a",
        "ps-c",
    ]
    assert [item.parameter_set_id for item in analyzer.calls[1].approved_parameter_sets] == [
        "ps-b",
    ]


def test_analyze_parameter_batches_by_family_preserves_duplicate_parameter_set_guard() -> None:
    evaluations = (
        IntelligenceEvaluation(
            event_id="intel-tbtcusd-20260317-0003",
            disposition="high_priority",
            score=0.7,
            rationale="Duplicate ids should still fail deterministically.",
        ),
    )
    analyzer = DeterministicParameterIntelligenceAnalyzer()

    with pytest.raises(
        ParameterAnalysisValidationError, match="parameter_set_id values must be unique"
    ):
        analyze_parameter_batches_by_family(
            analyzer,
            evaluations=evaluations,
            family_batches=(
                FamilyParameterBatch(
                    strategy_family="legacy",
                    approved_parameter_sets=(_parameter_set("ps-a"),),
                ),
                FamilyParameterBatch(
                    strategy_family="legacy",
                    approved_parameter_sets=(_parameter_set("ps-a"),),
                ),
            ),
        )


def test_cross_family_override_wrapper_requires_explicit_override_and_signoff() -> None:
    with pytest.raises(Exception, match="cross_family_promotion"):
        require_explicit_cross_family_override("legacy", "ri")

    require_explicit_cross_family_override(
        "legacy",
        "ri",
        explicit_override=True,
        governance_signoff=True,
    )
