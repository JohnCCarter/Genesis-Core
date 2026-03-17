from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
from pathlib import Path

import pytest

from core.intelligence.collection import CollectionRequest, DeterministicIntelligenceCollector
from core.intelligence.evaluation import DeterministicIntelligenceEvaluator
from core.intelligence.events import IntelligenceEvent, IntelligenceReference
from core.intelligence.features import DeterministicIntelligenceFeatureExtractor
from core.intelligence.ledger_adapter import (
    DeterministicIntelligenceLedgerAdapter,
    LedgerPersistenceRequest,
    LedgerPersistenceResult,
)
from core.intelligence.normalization import DeterministicIntelligenceNormalizer
from core.intelligence.parameter import (
    ApprovedParameterSet,
    DeterministicParameterIntelligenceAnalyzer,
)
from core.research_ledger import LedgerEntityType, ResearchLedgerService
from core.research_ledger.storage import LedgerStorage
from core.research_orchestrator import (
    DeterministicResearchOrchestrator,
    ResearchOrchestrationError,
    ResearchTask,
)


def _event(index: int, *, source: str = "news") -> IntelligenceEvent:
    return IntelligenceEvent(
        event_id=f"intel-tbtcusd-20260317-{index:04d}",
        source=source,
        timestamp=f"2026-03-17T12:{index:02d}:00+00:00",
        asset="tBTCUSD",
        topic="macro",
        signal_type="observation",
        confidence=0.5 + (index * 0.1),
        references=(
            IntelligenceReference(kind="artifact", ref=f"ART-2026-{index:04d}", label="primary"),
        ),
        summary=f"Research workflow event {index}.",
    )


def _parameter_set(
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


def _task() -> ResearchTask:
    return ResearchTask(
        task_id="research-task-001",
        collection_request=CollectionRequest(source="news", asset="tBTCUSD", topic="macro"),
        approved_parameter_sets=(
            _parameter_set("ps-b", sensitivity=0.55, stability=0.72, consistency=0.68),
            _parameter_set("ps-a", sensitivity=0.20, stability=0.90, consistency=0.82),
        ),
    )


class RecordingCollector:
    def __init__(self, inner: DeterministicIntelligenceCollector, calls: list[str]) -> None:
        self.inner = inner
        self.calls = calls

    def collect(self, request: CollectionRequest):
        self.calls.append("collection")
        return self.inner.collect(request)


class RecordingNormalizer:
    def __init__(self, inner: DeterministicIntelligenceNormalizer, calls: list[str]) -> None:
        self.inner = inner
        self.calls = calls

    def normalize(self, request):
        self.calls.append("normalization")
        return self.inner.normalize(request)


class RecordingFeatureExtractor:
    def __init__(
        self,
        inner: DeterministicIntelligenceFeatureExtractor,
        calls: list[str],
    ) -> None:
        self.inner = inner
        self.calls = calls

    def extract(self, request):
        self.calls.append("features")
        return self.inner.extract(request)


class RecordingEvaluator:
    def __init__(self, inner: DeterministicIntelligenceEvaluator, calls: list[str]) -> None:
        self.inner = inner
        self.calls = calls

    def evaluate(self, request):
        self.calls.append("evaluation")
        return self.inner.evaluate(request)


class RecordingParameterAnalyzer:
    def __init__(
        self,
        inner: DeterministicParameterIntelligenceAnalyzer,
        calls: list[str],
    ) -> None:
        self.inner = inner
        self.calls = calls

    def analyze(self, request):
        self.calls.append("parameter")
        return self.inner.analyze(request)


class RecordingLedgerAdapter:
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls
        self.requests: list[LedgerPersistenceRequest] = []

    def persist_events(self, request: LedgerPersistenceRequest) -> LedgerPersistenceResult:
        self.calls.append("ledger")
        self.requests.append(request)
        return LedgerPersistenceResult(
            persisted_event_ids=tuple(item.event.event_id for item in request.events),
            ledger_entity_ids=tuple(
                f"ART-RUN-{index:04d}" for index, _ in enumerate(request.events, start=1)
            ),
        )


def _service(tmp_path: Path) -> ResearchLedgerService:
    return ResearchLedgerService(LedgerStorage(root=tmp_path / "artifacts" / "research_ledger"))


def test_orchestrator_exports_are_available() -> None:
    assert DeterministicResearchOrchestrator.__name__ == "DeterministicResearchOrchestrator"
    assert ResearchTask.__name__ == "ResearchTask"


def test_orchestration_is_deterministic_and_preserves_stage_order_without_mutation() -> None:
    calls: list[str] = []
    events = (_event(2, source="macro"), _event(1, source="news"), _event(3, source="news"))
    task = _task()
    collector = RecordingCollector(DeterministicIntelligenceCollector(events=events), calls)
    normalizer = RecordingNormalizer(DeterministicIntelligenceNormalizer(), calls)
    feature_extractor = RecordingFeatureExtractor(
        DeterministicIntelligenceFeatureExtractor(),
        calls,
    )
    evaluator = RecordingEvaluator(DeterministicIntelligenceEvaluator(), calls)
    parameter_analyzer = RecordingParameterAnalyzer(
        DeterministicParameterIntelligenceAnalyzer(),
        calls,
    )
    ledger_adapter = RecordingLedgerAdapter(calls)
    orchestrator = DeterministicResearchOrchestrator(
        collector=collector,
        normalizer=normalizer,
        feature_extractor=feature_extractor,
        evaluator=evaluator,
        parameter_analyzer=parameter_analyzer,
        ledger_adapter=ledger_adapter,
    )
    before_events = deepcopy(tuple(event.to_payload() for event in events))
    before_task = deepcopy(asdict(task))

    first = orchestrator.run(task)
    second = orchestrator.run(task)

    assert first == second
    assert calls == [
        "collection",
        "normalization",
        "features",
        "evaluation",
        "parameter",
        "ledger",
        "collection",
        "normalization",
        "features",
        "evaluation",
        "parameter",
        "ledger",
    ]
    assert tuple(event.event_id for event in first.stage_outputs.collected_events) == (
        "intel-tbtcusd-20260317-0001",
        "intel-tbtcusd-20260317-0003",
    )
    assert first.recommended_parameter_set_ids == ("ps-a", "ps-b")
    assert first.preferred_parameter_set_ids == ("ps-a",)
    assert first.top_advisory_parameter_set_id == "ps-a"
    assert first.stage_outputs.persistence_result.persisted_event_ids == (
        "intel-tbtcusd-20260317-0001",
        "intel-tbtcusd-20260317-0003",
    )
    assert tuple(event.to_payload() for event in events) == before_events
    assert asdict(task) == before_task
    assert ledger_adapter.requests[0].events is first.stage_outputs.normalized_events


def test_orchestration_persists_validated_events_with_real_adapter(tmp_path: Path) -> None:
    service = _service(tmp_path)
    orchestrator = DeterministicResearchOrchestrator(
        collector=DeterministicIntelligenceCollector(events=(_event(1), _event(2))),
        normalizer=DeterministicIntelligenceNormalizer(),
        feature_extractor=DeterministicIntelligenceFeatureExtractor(),
        evaluator=DeterministicIntelligenceEvaluator(),
        parameter_analyzer=DeterministicParameterIntelligenceAnalyzer(),
        ledger_adapter=DeterministicIntelligenceLedgerAdapter(service=service),
    )

    result = orchestrator.run(_task())
    persisted_records = service.storage.list_records(LedgerEntityType.ARTIFACT)

    assert result.stage_outputs.persistence_result.persisted_event_ids == (
        "intel-tbtcusd-20260317-0001",
        "intel-tbtcusd-20260317-0002",
    )
    assert result.stage_outputs.persistence_result.ledger_entity_ids == (
        "ART-2026-0001",
        "ART-2026-0002",
    )
    assert tuple(record.entity_id for record in persisted_records) == (
        "ART-2026-0001",
        "ART-2026-0002",
    )
    assert tuple(record.metadata["event"]["event_id"] for record in persisted_records) == (
        "intel-tbtcusd-20260317-0001",
        "intel-tbtcusd-20260317-0002",
    )


def test_orchestration_fails_fast_when_collection_produces_no_events() -> None:
    orchestrator = DeterministicResearchOrchestrator(
        collector=DeterministicIntelligenceCollector(events=(_event(1, source="macro"),)),
        normalizer=DeterministicIntelligenceNormalizer(),
        feature_extractor=DeterministicIntelligenceFeatureExtractor(),
        evaluator=DeterministicIntelligenceEvaluator(),
        parameter_analyzer=DeterministicParameterIntelligenceAnalyzer(),
        ledger_adapter=RecordingLedgerAdapter([]),
    )

    with pytest.raises(ResearchOrchestrationError, match="collection produced no events"):
        orchestrator.run(_task())
