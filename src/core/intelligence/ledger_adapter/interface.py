from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from core.intelligence.events.models import ValidatedIntelligenceEvent


@dataclass(frozen=True, slots=True)
class LedgerPersistenceRequest:
    events: tuple[ValidatedIntelligenceEvent, ...]


@dataclass(frozen=True, slots=True)
class LedgerPersistenceResult:
    persisted_event_ids: tuple[str, ...]
    ledger_entity_ids: tuple[str, ...] = ()


class IntelligenceLedgerAdapter(Protocol):
    def persist_events(self, request: LedgerPersistenceRequest) -> LedgerPersistenceResult: ...
