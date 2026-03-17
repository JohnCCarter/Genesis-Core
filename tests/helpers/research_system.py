from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from core.intelligence.collection import CollectionRequest, DeterministicIntelligenceCollector
from core.intelligence.evaluation import DeterministicIntelligenceEvaluator
from core.intelligence.events import IntelligenceEvent, IntelligenceReference
from core.intelligence.features import DeterministicIntelligenceFeatureExtractor
from core.intelligence.ledger_adapter import DeterministicIntelligenceLedgerAdapter
from core.intelligence.normalization import DeterministicIntelligenceNormalizer
from core.intelligence.parameter import (
    ApprovedParameterSet,
    DeterministicParameterIntelligenceAnalyzer,
)
from core.research_ledger import ResearchLedgerService
from core.research_ledger.storage import LedgerStorage
from core.research_orchestrator import DeterministicResearchOrchestrator, ResearchTask


@dataclass(frozen=True, slots=True)
class ResearchSystemHarness:
    input_events: tuple[IntelligenceEvent, ...]
    task: ResearchTask
    orchestrator: DeterministicResearchOrchestrator
    service: ResearchLedgerService


def build_event(
    index: int,
    *,
    source: str = "news",
    asset: str = "tBTCUSD",
    topic: str = "macro",
    confidence: float | None = None,
) -> IntelligenceEvent:
    return IntelligenceEvent(
        event_id=f"intel-tbtcusd-20260317-{index:04d}",
        source=source,
        timestamp=f"2026-03-17T12:{index:02d}:00+00:00",
        asset=asset,
        topic=topic,
        signal_type="observation",
        confidence=confidence if confidence is not None else 0.5 + (index * 0.1),
        references=(
            IntelligenceReference(kind="artifact", ref=f"ART-2026-{index:04d}", label="primary"),
        ),
        summary=f"Research system event {index}.",
    )


def build_parameter_set(
    parameter_set_id: str,
    *,
    sensitivity: float,
    stability: float,
    consistency: float,
) -> ApprovedParameterSet:
    return ApprovedParameterSet(
        parameter_set_id=parameter_set_id,
        parameters={
            "ema_fast": 9,
            "ema_slow": 21,
            "parameter_set_id": parameter_set_id,
        },
        sensitivity_score=sensitivity,
        stability_score=stability,
        consistency_score=consistency,
        source_ledger_entity_ids=(f"ART-2026-{parameter_set_id[-1:]}001",),
        baseline_weight=1.0,
        risk_multiplier=1.0,
    )


def build_task(
    *,
    task_id: str = "research-task-001",
    collection_request: CollectionRequest | None = None,
    approved_parameter_sets: tuple[ApprovedParameterSet, ...] | None = None,
) -> ResearchTask:
    return ResearchTask(
        task_id=task_id,
        collection_request=collection_request
        or CollectionRequest(source="news", asset="tBTCUSD", topic="macro"),
        approved_parameter_sets=approved_parameter_sets
        or (
            build_parameter_set("ps-b", sensitivity=0.55, stability=0.72, consistency=0.68),
            build_parameter_set("ps-a", sensitivity=0.20, stability=0.90, consistency=0.82),
        ),
    )


def build_service(tmp_path: Path) -> ResearchLedgerService:
    return ResearchLedgerService(LedgerStorage(root=tmp_path / "artifacts" / "research_ledger"))


def build_orchestrator(
    *,
    service: ResearchLedgerService,
    input_events: tuple[IntelligenceEvent, ...],
) -> DeterministicResearchOrchestrator:
    return DeterministicResearchOrchestrator(
        collector=DeterministicIntelligenceCollector(events=input_events),
        normalizer=DeterministicIntelligenceNormalizer(),
        feature_extractor=DeterministicIntelligenceFeatureExtractor(),
        evaluator=DeterministicIntelligenceEvaluator(),
        parameter_analyzer=DeterministicParameterIntelligenceAnalyzer(),
        ledger_adapter=DeterministicIntelligenceLedgerAdapter(service=service),
    )


def build_harness(
    tmp_path: Path,
    *,
    input_events: tuple[IntelligenceEvent, ...] | None = None,
    task: ResearchTask | None = None,
) -> ResearchSystemHarness:
    resolved_events = input_events or (
        build_event(2, source="macro"),
        build_event(1, source="news"),
        build_event(3, source="news"),
    )
    resolved_task = task or build_task()
    service = build_service(tmp_path)
    orchestrator = build_orchestrator(service=service, input_events=resolved_events)
    return ResearchSystemHarness(
        input_events=resolved_events,
        task=resolved_task,
        orchestrator=orchestrator,
        service=service,
    )
