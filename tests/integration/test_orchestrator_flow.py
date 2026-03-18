from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict

from core.intelligence.collection import CollectionRequest, DeterministicIntelligenceCollector
from core.intelligence.evaluation import DeterministicIntelligenceEvaluator
from core.intelligence.events import IntelligenceEvent
from core.intelligence.features import DeterministicIntelligenceFeatureExtractor
from core.intelligence.ledger_adapter import (
    DeterministicIntelligenceLedgerAdapter,
    LedgerPersistenceRequest,
)
from core.intelligence.normalization import DeterministicIntelligenceNormalizer
from core.intelligence.parameter import DeterministicParameterIntelligenceAnalyzer
from core.research_ledger import ResearchLedgerService
from core.research_orchestrator import DeterministicResearchOrchestrator
from tests.helpers.research_system import build_event, build_service, build_task


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
    def __init__(self, inner: DeterministicIntelligenceFeatureExtractor, calls: list[str]) -> None:
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
    def __init__(self, inner: DeterministicParameterIntelligenceAnalyzer, calls: list[str]) -> None:
        self.inner = inner
        self.calls = calls

    def analyze(self, request):
        self.calls.append("parameter")
        return self.inner.analyze(request)


class RecordingLedgerAdapter:
    def __init__(self, inner: DeterministicIntelligenceLedgerAdapter, calls: list[str]) -> None:
        self.inner = inner
        self.calls = calls
        self.requests: list[LedgerPersistenceRequest] = []

    def persist_events(self, request: LedgerPersistenceRequest):
        self.calls.append("ledger")
        self.requests.append(request)
        return self.inner.persist_events(request)


def test_orchestrator_preserves_stage_and_event_order_without_mutation(tmp_path) -> None:
    calls: list[str] = []
    events: tuple[IntelligenceEvent, ...] = (
        build_event(2, source="macro"),
        build_event(1, source="news"),
        build_event(3, source="news"),
    )
    task = build_task()
    service: ResearchLedgerService = build_service(tmp_path)
    orchestrator = DeterministicResearchOrchestrator(
        collector=RecordingCollector(DeterministicIntelligenceCollector(events=events), calls),
        normalizer=RecordingNormalizer(DeterministicIntelligenceNormalizer(), calls),
        feature_extractor=RecordingFeatureExtractor(
            DeterministicIntelligenceFeatureExtractor(),
            calls,
        ),
        evaluator=RecordingEvaluator(DeterministicIntelligenceEvaluator(), calls),
        parameter_analyzer=RecordingParameterAnalyzer(
            DeterministicParameterIntelligenceAnalyzer(),
            calls,
        ),
        ledger_adapter=RecordingLedgerAdapter(
            DeterministicIntelligenceLedgerAdapter(
                service=service,
                strategy_config={"strategy_family": "legacy"},
                strategy_family="legacy",
            ),
            calls,
        ),
    )
    before_events = deepcopy(tuple(event.to_payload() for event in events))
    before_task = deepcopy(asdict(task))

    result = orchestrator.run(task)

    assert calls == [
        "collection",
        "normalization",
        "features",
        "evaluation",
        "parameter",
        "ledger",
    ]
    assert tuple(event.event_id for event in result.stage_outputs.collected_events) == (
        "intel-tbtcusd-20260317-0001",
        "intel-tbtcusd-20260317-0003",
    )
    assert tuple(item.event.event_id for item in result.stage_outputs.normalized_events) == (
        "intel-tbtcusd-20260317-0001",
        "intel-tbtcusd-20260317-0003",
    )
    assert tuple(event.to_payload() for event in events) == before_events
    assert asdict(task) == before_task
