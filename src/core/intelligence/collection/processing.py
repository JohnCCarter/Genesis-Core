from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from core.intelligence.collection.interface import (
    CollectionRequest,
    CollectionResult,
    IntelligenceCollector,
)
from core.intelligence.events.models import IntelligenceEvent


class CollectionProcessingError(ValueError):
    """Raised when deterministic collection filtering cannot be completed."""


def _parse_timestamp(value: str, *, field_name: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise CollectionProcessingError(f"{field_name} must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise CollectionProcessingError(f"{field_name} must include timezone information")
    return parsed


def collect_events(
    events: tuple[IntelligenceEvent, ...],
    request: CollectionRequest,
) -> CollectionResult:
    """Filter intelligence events deterministically while preserving explicit input order."""

    window_start = (
        _parse_timestamp(request.window_start, field_name="window_start")
        if request.window_start is not None
        else None
    )
    window_end = (
        _parse_timestamp(request.window_end, field_name="window_end")
        if request.window_end is not None
        else None
    )
    if window_start is not None and window_end is not None and window_start > window_end:
        raise CollectionProcessingError("window_start must be less than or equal to window_end")

    filtered: list[IntelligenceEvent] = []
    for event in events:
        if event.source != request.source:
            continue
        if event.asset != request.asset:
            continue
        if event.topic != request.topic:
            continue

        if window_start is not None or window_end is not None:
            event_timestamp = _parse_timestamp(event.timestamp, field_name="event.timestamp")
            if window_start is not None and event_timestamp < window_start:
                continue
            if window_end is not None and event_timestamp > window_end:
                continue

        filtered.append(event)

    return tuple(filtered)


@dataclass(frozen=True, slots=True)
class DeterministicIntelligenceCollector(IntelligenceCollector):
    events: tuple[IntelligenceEvent, ...]

    def collect(self, request: CollectionRequest) -> CollectionResult:
        return collect_events(self.events, request)
