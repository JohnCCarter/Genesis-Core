from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from core.intelligence.events import (
    IntelligenceEvent,
    IntelligenceReference,
    validate_intelligence_event,
)
from core.intelligence.ledger_adapter import (
    IntelligenceLedgerAdapter,
    LedgerPersistenceRequest,
    LedgerPersistenceResult,
)


def _event(index: int) -> IntelligenceEvent:
    return IntelligenceEvent(
        event_id=f"intel-tbtcusd-20260316-{index:04d}",
        source="regime_intelligence",
        timestamp=f"2026-03-16T12:{index:02d}:00+00:00",
        asset="tBTCUSD",
        topic="regime",
        signal_type="observation",
        confidence=0.5 + (index * 0.1),
        references=(
            IntelligenceReference(kind="artifact", ref=f"ART-2026-{index:04d}", label="primary"),
        ),
        summary=f"Deterministic event {index}.",
    )


def _validated_event(index: int):
    return validate_intelligence_event(_event(index))


def test_ledger_adapter_package_exports_are_available() -> None:
    assert LedgerPersistenceRequest.__name__ == "LedgerPersistenceRequest"
    assert LedgerPersistenceResult.__name__ == "LedgerPersistenceResult"
    assert IntelligenceLedgerAdapter.__name__ == "IntelligenceLedgerAdapter"


def test_persistence_request_is_shallow_frozen_and_preserves_tuple_identity() -> None:
    validated_events = (_validated_event(1), _validated_event(2))
    request = LedgerPersistenceRequest(events=validated_events)

    assert request.events is validated_events

    with pytest.raises(FrozenInstanceError):
        request.events = (_validated_event(3),)


def test_persistence_request_preserves_explicit_event_ordering() -> None:
    validated_events = (_validated_event(2), _validated_event(1))
    request = LedgerPersistenceRequest(events=validated_events)

    assert tuple(item.event.event_id for item in request.events) == (
        "intel-tbtcusd-20260316-0002",
        "intel-tbtcusd-20260316-0001",
    )


def test_persistence_result_defaults_to_empty_ledger_entity_ids_and_is_frozen() -> None:
    result = LedgerPersistenceResult(persisted_event_ids=("intel-tbtcusd-20260316-0001",))

    assert result.ledger_entity_ids == ()

    with pytest.raises(FrozenInstanceError):
        result.persisted_event_ids = ()


def test_protocol_smoke_allows_minimal_contract_only_adapter() -> None:
    class _Adapter:
        def persist_events(self, request: LedgerPersistenceRequest) -> LedgerPersistenceResult:
            return LedgerPersistenceResult(
                persisted_event_ids=tuple(item.event.event_id for item in request.events),
            )

    adapter: IntelligenceLedgerAdapter = _Adapter()
    request = LedgerPersistenceRequest(events=(_validated_event(1), _validated_event(2)))

    result = adapter.persist_events(request)

    assert result.persisted_event_ids == (
        "intel-tbtcusd-20260316-0001",
        "intel-tbtcusd-20260316-0002",
    )
    assert result.ledger_entity_ids == ()
