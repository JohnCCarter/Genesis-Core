from __future__ import annotations

from core.intelligence.events.models import JsonObject, ValidatedIntelligenceEvent
from core.intelligence.features.interface import (
    FeatureExtractionRequest,
    FeatureExtractionResult,
    IntelligenceFeatureExtractor,
    IntelligenceFeatureSet,
)

FEATURE_NAMESPACE_V1 = "intelligence.processing.features.v1"


def _feature_payload(validated_event: ValidatedIntelligenceEvent) -> JsonObject:
    event = validated_event.event
    references = event.references
    primary_reference = references[0] if references else None
    summary = event.summary.strip()

    return {
        "asset": event.asset,
        "confidence": float(event.confidence),
        "has_references": bool(references),
        "primary_reference_kind": (
            str(primary_reference.kind) if primary_reference is not None else None
        ),
        "primary_reference_ref": (
            str(primary_reference.ref) if primary_reference is not None else None
        ),
        "reference_count": len(references),
        "signal_type": event.signal_type,
        "source": event.source,
        "summary_length": len(summary),
        "summary_word_count": len(summary.split()),
        "timestamp": event.timestamp,
        "topic": event.topic,
        "validator_version": validated_event.validator_version,
    }


def extract_features(
    events: tuple[ValidatedIntelligenceEvent, ...],
) -> FeatureExtractionResult:
    """Derive deterministic feature sets from validated intelligence events."""

    return tuple(
        IntelligenceFeatureSet(
            event_id=validated_event.event.event_id,
            feature_namespace=FEATURE_NAMESPACE_V1,
            features=_feature_payload(validated_event),
        )
        for validated_event in events
    )


class DeterministicIntelligenceFeatureExtractor(IntelligenceFeatureExtractor):
    def extract(self, request: FeatureExtractionRequest) -> FeatureExtractionResult:
        return extract_features(request.events)
