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
from core.strategy.family_registry import (
    STRATEGY_FAMILY_SOURCE,
    StrategyFamily,
    StrategyFamilyValidationError,
    resolve_strategy_family,
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
    strategy_config: dict | None = None
    strategy_family: StrategyFamily | None = None
    strategy_family_source: str = STRATEGY_FAMILY_SOURCE

    def persist_events(self, request: LedgerPersistenceRequest) -> LedgerPersistenceResult:
        resolved_strategy_family = self.strategy_family
        if resolved_strategy_family is None:
            try:
                resolved_strategy_family = resolve_strategy_family(dict(self.strategy_config or {}))
            except StrategyFamilyValidationError as exc:
                raise ValueError("strategy_family_context_required") from exc

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
            persisted = self.service.append_record_with_strategy_family(
                record,
                config=self.strategy_config,
                strategy_family=resolved_strategy_family,
                strategy_family_source=self.strategy_family_source,
            )
            persisted_event_ids.append(validated_event.event.event_id)
            ledger_entity_ids.append(persisted.entity_id)

        return LedgerPersistenceResult(
            persisted_event_ids=tuple(persisted_event_ids),
            ledger_entity_ids=tuple(ledger_entity_ids),
        )
