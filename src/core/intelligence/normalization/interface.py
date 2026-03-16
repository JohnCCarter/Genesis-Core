from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TypeAlias

from core.intelligence.events.models import IntelligenceEvent, ValidatedIntelligenceEvent

NormalizationResult: TypeAlias = tuple[ValidatedIntelligenceEvent, ...]


@dataclass(frozen=True, slots=True)
class NormalizationRequest:
    events: tuple[IntelligenceEvent, ...]


class IntelligenceNormalizer(Protocol):
    def normalize(self, request: NormalizationRequest) -> NormalizationResult: ...
