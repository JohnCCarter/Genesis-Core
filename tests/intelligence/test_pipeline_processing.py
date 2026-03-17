from __future__ import annotations

from copy import deepcopy
from dataclasses import FrozenInstanceError

import pytest

from core.intelligence.collection import (
    CollectionProcessingError,
    CollectionRequest,
    DeterministicIntelligenceCollector,
    collect_events,
)
from core.intelligence.evaluation import (
    HIGH_PRIORITY_THRESHOLD,
    MONITOR_THRESHOLD,
    DeterministicIntelligenceEvaluator,
    EvaluationRequest,
    evaluate_feature_sets,
)
from core.intelligence.events import IntelligenceEvent, IntelligenceReference
from core.intelligence.features import (
    FEATURE_NAMESPACE_V1,
    DeterministicIntelligenceFeatureExtractor,
    FeatureExtractionRequest,
    extract_features,
)
from core.intelligence.normalization import (
    DeterministicIntelligenceNormalizer,
    NormalizationRequest,
    normalize_events,
)


def _event(
    index: int,
    *,
    source: str = "news",
    asset: str = "tBTCUSD",
    topic: str = "macro",
    timestamp: str | None = None,
    confidence: float = 0.5,
    summary: str | None = None,
) -> IntelligenceEvent:
    return IntelligenceEvent(
        event_id=f"intel-tbtcusd-20260317-{index:04d}",
        source=source,
        timestamp=timestamp or f"2026-03-17T12:{index:02d}:00+00:00",
        asset=asset,
        topic=topic,
        signal_type="observation",
        confidence=confidence,
        references=(
            IntelligenceReference(kind="artifact", ref=f"ART-2026-{index:04d}", label="primary"),
        ),
        summary=summary or f"Deterministic processing event {index}.",
    )


def test_collection_preserves_explicit_input_ordering_while_filtering() -> None:
    events = (
        _event(2, source="macro"),
        _event(1, source="news"),
        _event(3, source="news"),
    )
    request = CollectionRequest(source="news", asset="tBTCUSD", topic="macro")

    collected = collect_events(events, request)

    assert collected == (events[1], events[2])
    assert collected[0] is events[1]
    assert collected[1] is events[2]


def test_collection_window_filter_is_timezone_aware_and_inclusive() -> None:
    events = (
        _event(1, timestamp="2026-03-17T11:59:59+00:00"),
        _event(2, timestamp="2026-03-17T12:00:00+00:00"),
        _event(3, timestamp="2026-03-17T12:30:00+00:00"),
        _event(4, timestamp="2026-03-17T13:00:00+00:00"),
        _event(5, timestamp="2026-03-17T13:00:01+00:00"),
    )
    request = CollectionRequest(
        source="news",
        asset="tBTCUSD",
        topic="macro",
        window_start="2026-03-17T12:00:00+00:00",
        window_end="2026-03-17T13:00:00+00:00",
    )

    collected = collect_events(events, request)

    assert tuple(event.event_id for event in collected) == (
        "intel-tbtcusd-20260317-0002",
        "intel-tbtcusd-20260317-0003",
        "intel-tbtcusd-20260317-0004",
    )


def test_collection_rejects_inverted_window_range() -> None:
    request = CollectionRequest(
        source="news",
        asset="tBTCUSD",
        topic="macro",
        window_start="2026-03-17T13:00:00+00:00",
        window_end="2026-03-17T12:00:00+00:00",
    )

    with pytest.raises(CollectionProcessingError, match="window_start"):
        collect_events((_event(1),), request)


def test_collector_class_preserves_constructor_tuple_identity() -> None:
    events = (_event(1), _event(2))
    collector = DeterministicIntelligenceCollector(events=events)

    assert collector.events is events
    with pytest.raises(FrozenInstanceError):
        collector.events = (_event(3),)


def test_normalization_preserves_order_and_event_identity() -> None:
    events = (_event(2, source="macro"), _event(1, source="news"))

    normalized = normalize_events(events)

    assert tuple(item.event.event_id for item in normalized) == (
        "intel-tbtcusd-20260317-0002",
        "intel-tbtcusd-20260317-0001",
    )
    assert normalized[0].event is events[0]
    assert normalized[1].event is events[1]


def test_feature_extraction_is_deterministic_and_non_mutating() -> None:
    events = (_event(1, confidence=0.8, summary="alpha beta gamma"), _event(2, confidence=0.4))
    normalized = normalize_events(events)
    before_payload = tuple(event.to_payload() for event in events)

    first = extract_features(normalized)
    second = extract_features(normalized)

    assert first == second
    assert tuple(item.event_id for item in first) == (
        "intel-tbtcusd-20260317-0001",
        "intel-tbtcusd-20260317-0002",
    )
    assert all(item.feature_namespace == FEATURE_NAMESPACE_V1 for item in first)
    assert first[0].features == {
        "asset": "tBTCUSD",
        "confidence": 0.8,
        "has_references": True,
        "primary_reference_kind": "artifact",
        "primary_reference_ref": "ART-2026-0001",
        "reference_count": 1,
        "signal_type": "observation",
        "source": "news",
        "summary_length": 16,
        "summary_word_count": 3,
        "timestamp": "2026-03-17T12:01:00+00:00",
        "topic": "macro",
        "validator_version": "intelligence_event.v1",
    }
    assert tuple(event.to_payload() for event in events) == before_payload


def test_evaluation_is_deterministic_with_pinned_threshold_semantics() -> None:
    events = (
        _event(1, confidence=0.8, summary="alpha beta gamma"),
        _event(2, confidence=0.3, summary="short summary"),
    )
    feature_sets = extract_features(normalize_events(events))

    first = evaluate_feature_sets(feature_sets)
    second = evaluate_feature_sets(feature_sets)

    assert HIGH_PRIORITY_THRESHOLD == 0.75
    assert MONITOR_THRESHOLD == 0.45
    assert first == second
    assert tuple(item.event_id for item in first) == (
        "intel-tbtcusd-20260317-0001",
        "intel-tbtcusd-20260317-0002",
    )
    assert first[0].score == 0.7775
    assert first[0].disposition == "high_priority"
    assert first[0].rationale == (
        "namespace=intelligence.processing.features.v1;"
        "confidence=0.800000;reference_count=1;summary_word_count=3;"
        "score=0.777500;disposition=high_priority"
    )
    assert first[1].score == 0.325
    assert first[1].disposition == "ignore"


def test_processing_stage_exports_are_available_from_package_roots() -> None:
    assert DeterministicIntelligenceCollector.__name__ == "DeterministicIntelligenceCollector"
    assert DeterministicIntelligenceNormalizer.__name__ == "DeterministicIntelligenceNormalizer"
    assert DeterministicIntelligenceFeatureExtractor.__name__ == (
        "DeterministicIntelligenceFeatureExtractor"
    )
    assert DeterministicIntelligenceEvaluator.__name__ == "DeterministicIntelligenceEvaluator"


def test_processing_pipeline_repeated_runs_produce_identical_outputs() -> None:
    input_events = (
        _event(2, source="macro", confidence=0.61, summary="macro event stable output"),
        _event(1, source="news", confidence=0.72, summary="news event stable output"),
    )
    request = CollectionRequest(source="news", asset="tBTCUSD", topic="macro")
    collector = DeterministicIntelligenceCollector(events=input_events)
    normalizer = DeterministicIntelligenceNormalizer()
    extractor = DeterministicIntelligenceFeatureExtractor()
    evaluator = DeterministicIntelligenceEvaluator()
    before_events = deepcopy(tuple(event.to_payload() for event in input_events))

    first_collected = collector.collect(request)
    first_normalized = normalizer.normalize(NormalizationRequest(events=first_collected))
    first_features = extractor.extract(FeatureExtractionRequest(events=first_normalized))
    first_evaluations = evaluator.evaluate(EvaluationRequest(feature_sets=first_features))

    second_collected = collector.collect(request)
    second_normalized = normalizer.normalize(NormalizationRequest(events=second_collected))
    second_features = extractor.extract(FeatureExtractionRequest(events=second_normalized))
    second_evaluations = evaluator.evaluate(EvaluationRequest(feature_sets=second_features))

    assert first_collected == second_collected == (input_events[1],)
    assert first_normalized == second_normalized
    assert first_features == second_features
    assert first_evaluations == second_evaluations
    assert tuple(event.to_payload() for event in input_events) == before_events
