from __future__ import annotations

from core.intelligence.events.models import IntelligenceEvent
from core.intelligence.events.validators import validate_intelligence_event
from core.intelligence.normalization.interface import (
    IntelligenceNormalizer,
    NormalizationRequest,
    NormalizationResult,
)


def normalize_events(events: tuple[IntelligenceEvent, ...]) -> NormalizationResult:
    """Validate intelligence events deterministically without rebinding or mutation."""

    return tuple(validate_intelligence_event(event) for event in events)


class DeterministicIntelligenceNormalizer(IntelligenceNormalizer):
    def normalize(self, request: NormalizationRequest) -> NormalizationResult:
        return normalize_events(request.events)
