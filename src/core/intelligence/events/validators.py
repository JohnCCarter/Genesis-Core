from __future__ import annotations

import math
from datetime import datetime
from typing import Any

from core.intelligence.events.models import (
    IntelligenceEvent,
    IntelligenceReference,
    ValidatedIntelligenceEvent,
)


class IntelligenceEventValidationError(ValueError):
    """Raised when an intelligence event violates the canonical event schema."""


def _require_non_empty(value: str | None, *, field_name: str) -> None:
    if value is None or not value.strip():
        raise IntelligenceEventValidationError(f"{field_name} must be non-empty")


def _validate_timestamp(value: str) -> None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise IntelligenceEventValidationError("timestamp must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise IntelligenceEventValidationError("timestamp must include timezone information")


def _validate_reference(reference: IntelligenceReference, *, index: int) -> None:
    _require_non_empty(reference.kind, field_name=f"references[{index}].kind")
    _require_non_empty(reference.ref, field_name=f"references[{index}].ref")


def validate_intelligence_event(event: IntelligenceEvent) -> ValidatedIntelligenceEvent:
    _require_non_empty(event.event_id, field_name="event_id")
    _require_non_empty(event.source, field_name="source")
    _require_non_empty(event.asset, field_name="asset")
    _require_non_empty(event.topic, field_name="topic")
    _require_non_empty(event.signal_type, field_name="signal_type")
    _require_non_empty(event.summary, field_name="summary")
    _validate_timestamp(event.timestamp)
    if not math.isfinite(event.confidence):
        raise IntelligenceEventValidationError("confidence must be finite")
    if event.confidence < 0.0 or event.confidence > 1.0:
        raise IntelligenceEventValidationError("confidence must be between 0.0 and 1.0")
    for index, reference in enumerate(event.references):
        _validate_reference(reference, index=index)
    return ValidatedIntelligenceEvent(event=event)


def validate_intelligence_payload(payload: dict[str, Any]) -> ValidatedIntelligenceEvent:
    return validate_intelligence_event(IntelligenceEvent.from_payload(payload))
