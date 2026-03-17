from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime

from core.intelligence.events.models import ValidatedIntelligenceEvent
from core.intelligence.ledger_adapter.interface import (
    IntelligenceLedgerAdapter,
    LedgerPersistenceRequest,
    LedgerPersistenceResult,
)
from core.research_ledger import (
    ArtifactKind,
    ArtifactRecord,
    IntelligenceRef,
    LedgerEntityType,
    ResearchLedgerService,
)

_PATH_ROOT = "intelligence"
_PATH_SEGMENT_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")


def _timestamp_year(value: str) -> int:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.year


def _path_segment(value: str) -> str:
    sanitized = _PATH_SEGMENT_PATTERN.sub("-", value.strip()).strip("-")
    return sanitized or "unknown"


def _record_path(validated_event: ValidatedIntelligenceEvent) -> str:
    event = validated_event.event
    return (
        f"{_PATH_ROOT}/{_path_segment(event.source)}/{_path_segment(event.asset)}/"
        f"{_path_segment(event.topic)}/{event.event_id}.json"
    )


def _intelligence_refs(
    validated_event: ValidatedIntelligenceEvent,
) -> tuple[IntelligenceRef, ...]:
    event = validated_event.event
    return tuple(
        IntelligenceRef(
            module=event.source,
            ref_kind=reference.kind,
            label=reference.label,
            metadata={
                "event_id": event.event_id,
                "source_ref": reference.ref,
            },
        )
        for reference in event.references
    )


def map_validated_event_to_artifact_record(
    validated_event: ValidatedIntelligenceEvent,
    *,
    entity_id: str,
) -> ArtifactRecord:
    """Map a validated intelligence event into a canonical ledger artifact record."""

    event = validated_event.event
    return ArtifactRecord(
        entity_id=entity_id,
        entity_type=LedgerEntityType.ARTIFACT,
        created_at=event.timestamp,
        artifact_kind=ArtifactKind.INTELLIGENCE_OUTPUT,
        path=_record_path(validated_event),
        metadata={
            "event": event.to_payload(),
            "validator_version": validated_event.validator_version,
        },
        intelligence_refs=_intelligence_refs(validated_event),
    )


@dataclass(frozen=True, slots=True)
class DeterministicIntelligenceLedgerAdapter(IntelligenceLedgerAdapter):
    service: ResearchLedgerService

    def persist_events(self, request: LedgerPersistenceRequest) -> LedgerPersistenceResult:
        persisted_event_ids: list[str] = []
        ledger_entity_ids: list[str] = []

        for validated_event in request.events:
            entity_id = self.service.allocate_id(
                LedgerEntityType.ARTIFACT,
                year=_timestamp_year(validated_event.event.timestamp),
            )
            record = map_validated_event_to_artifact_record(
                validated_event,
                entity_id=entity_id,
            )
            persisted = self.service.append_artifact(record)
            persisted_event_ids.append(validated_event.event.event_id)
            ledger_entity_ids.append(persisted.entity_id)

        return LedgerPersistenceResult(
            persisted_event_ids=tuple(persisted_event_ids),
            ledger_entity_ids=tuple(ledger_entity_ids),
        )
