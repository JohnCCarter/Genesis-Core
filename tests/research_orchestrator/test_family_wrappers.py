from __future__ import annotations

import pytest

from core.intelligence.collection import CollectionRequest
from core.intelligence.evaluation import IntelligenceEvaluation
from core.intelligence.parameter import (
    ApprovedParameterSet,
    DeterministicParameterIntelligenceAnalyzer,
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


def test_cross_family_override_wrapper_requires_explicit_override_and_signoff() -> None:
    with pytest.raises(Exception, match="cross_family_promotion"):
        require_explicit_cross_family_override("legacy", "ri")

    require_explicit_cross_family_override(
        "legacy",
        "ri",
        explicit_override=True,
        governance_signoff=True,
    )
