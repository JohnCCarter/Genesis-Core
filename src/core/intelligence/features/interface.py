from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, TypeAlias

from core.intelligence.events.models import JsonObject, ValidatedIntelligenceEvent

FeatureExtractionResult: TypeAlias = tuple["IntelligenceFeatureSet", ...]


@dataclass(frozen=True, slots=True)
class IntelligenceFeatureSet:
    event_id: str
    feature_namespace: str
    features: JsonObject = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class FeatureExtractionRequest:
    events: tuple[ValidatedIntelligenceEvent, ...]


class IntelligenceFeatureExtractor(Protocol):
    def extract(self, request: FeatureExtractionRequest) -> FeatureExtractionResult: ...
