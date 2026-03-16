from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TypeAlias

from core.intelligence.events.models import IntelligenceEvent

CollectionResult: TypeAlias = tuple[IntelligenceEvent, ...]


@dataclass(frozen=True, slots=True)
class CollectionRequest:
    source: str
    asset: str
    topic: str
    window_start: str | None = None
    window_end: str | None = None


class IntelligenceCollector(Protocol):
    def collect(self, request: CollectionRequest) -> CollectionResult: ...
