from __future__ import annotations

from dataclasses import FrozenInstanceError
from typing import get_origin

import pytest

from core.intelligence.collection import CollectionRequest, CollectionResult, IntelligenceCollector
from core.intelligence.evaluation import (
    EvaluationRequest,
    EvaluationResult,
    IntelligenceEvaluation,
    IntelligenceEvaluator,
)
from core.intelligence.events import (
    IntelligenceEvent,
    IntelligenceReference,
    validate_intelligence_event,
)
from core.intelligence.features import (
    FeatureExtractionRequest,
    FeatureExtractionResult,
    IntelligenceFeatureExtractor,
    IntelligenceFeatureSet,
)
from core.intelligence.normalization import (
    IntelligenceNormalizer,
    NormalizationRequest,
    NormalizationResult,
)


def _event(index: int, *, source: str = "regime_intelligence") -> IntelligenceEvent:
    return IntelligenceEvent(
        event_id=f"intel-tbtcusd-20260316-{index:04d}",
        source=source,
        timestamp=f"2026-03-16T12:{index:02d}:00+00:00",
        asset="tBTCUSD",
        topic="regime",
        signal_type="observation",
        confidence=0.5 + (index * 0.1),
        references=(
            IntelligenceReference(kind="artifact", ref=f"ART-2026-{index:04d}", label="primary"),
        ),
        summary=f"Deterministic event {index}.",
    )


def test_package_root_exports_are_available() -> None:
    assert CollectionRequest.__name__ == "CollectionRequest"
    assert IntelligenceCollector.__name__ == "IntelligenceCollector"
    assert NormalizationRequest.__name__ == "NormalizationRequest"
    assert IntelligenceNormalizer.__name__ == "IntelligenceNormalizer"
    assert FeatureExtractionRequest.__name__ == "FeatureExtractionRequest"
    assert IntelligenceFeatureSet.__name__ == "IntelligenceFeatureSet"
    assert IntelligenceFeatureExtractor.__name__ == "IntelligenceFeatureExtractor"
    assert EvaluationRequest.__name__ == "EvaluationRequest"
    assert IntelligenceEvaluation.__name__ == "IntelligenceEvaluation"
    assert IntelligenceEvaluator.__name__ == "IntelligenceEvaluator"


def test_stage_result_aliases_remain_tuple_based() -> None:
    assert get_origin(CollectionResult) is tuple
    assert get_origin(NormalizationResult) is tuple
    assert get_origin(FeatureExtractionResult) is tuple
    assert get_origin(EvaluationResult) is tuple


@pytest.mark.parametrize(
    ("request_factory", "field_name", "replacement"),
    [
        (
            lambda: CollectionRequest(source="news", asset="tBTCUSD", topic="macro"),
            "asset",
            "tETHUSD",
        ),
        (lambda: NormalizationRequest(events=(_event(1),)), "events", (_event(2),)),
        (
            lambda: FeatureExtractionRequest(events=(validate_intelligence_event(_event(1)),)),
            "events",
            (validate_intelligence_event(_event(2)),),
        ),
        (
            lambda: EvaluationRequest(
                feature_sets=(
                    IntelligenceFeatureSet(
                        event_id="intel-tbtcusd-20260316-0001",
                        feature_namespace="prep.v1",
                        features={"confidence": 0.6},
                    ),
                )
            ),
            "feature_sets",
            (),
        ),
    ],
)
def test_contract_requests_are_shallow_frozen(
    request_factory: object,
    field_name: str,
    replacement: object,
) -> None:
    request = request_factory()

    with pytest.raises(FrozenInstanceError):
        setattr(request, field_name, replacement)


def test_stage_contracts_preserve_explicit_tuple_ordering() -> None:
    collected_events = (_event(2, source="macro"), _event(1, source="news"))
    normalization_request = NormalizationRequest(events=collected_events)

    normalized_events = tuple(
        validate_intelligence_event(event) for event in normalization_request.events
    )
    feature_request = FeatureExtractionRequest(events=normalized_events)

    feature_sets = tuple(
        IntelligenceFeatureSet(
            event_id=validated.event.event_id,
            feature_namespace="prep.v1",
            features={
                "confidence": validated.event.confidence,
                "source": validated.event.source,
                "topic": validated.event.topic,
            },
        )
        for validated in feature_request.events
    )
    evaluation_request = EvaluationRequest(feature_sets=feature_sets)
    evaluations = tuple(
        IntelligenceEvaluation(
            event_id=feature_set.event_id,
            disposition="unwired",
            score=float(index),
            rationale=f"Stage contract only for {feature_set.event_id}",
        )
        for index, feature_set in enumerate(evaluation_request.feature_sets, start=1)
    )

    assert tuple(event.event_id for event in collected_events) == (
        "intel-tbtcusd-20260316-0002",
        "intel-tbtcusd-20260316-0001",
    )
    assert tuple(item.event.event_id for item in normalized_events) == (
        "intel-tbtcusd-20260316-0002",
        "intel-tbtcusd-20260316-0001",
    )
    assert tuple(item.event_id for item in feature_sets) == (
        "intel-tbtcusd-20260316-0002",
        "intel-tbtcusd-20260316-0001",
    )
    assert tuple(item.event_id for item in evaluations) == (
        "intel-tbtcusd-20260316-0002",
        "intel-tbtcusd-20260316-0001",
    )


def test_stage_contract_construction_does_not_rebind_input_tuples() -> None:
    collected_events = (_event(1), _event(2))
    normalization_request = NormalizationRequest(events=collected_events)
    normalized_events = tuple(
        validate_intelligence_event(event) for event in normalization_request.events
    )
    feature_request = FeatureExtractionRequest(events=normalized_events)

    assert normalization_request.events is collected_events
    assert feature_request.events is normalized_events
    assert feature_request.events[0].event.references[0].ref == "ART-2026-0001"
