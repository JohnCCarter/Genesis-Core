from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from core.intelligence.events import (
    IntelligenceEvent,
    IntelligenceReference,
    validate_intelligence_event,
)
from core.intelligence.ledger_adapter import (
    DeterministicIntelligenceLedgerAdapter,
    LedgerPersistenceRequest,
    map_validated_event_to_artifact_record,
)
from core.research_ledger import ArtifactKind, LedgerEntityType, ResearchLedgerService
from core.research_ledger.models import record_to_dict
from core.research_ledger.storage import LedgerStorage
from core.strategy.family_registry import StrategyFamilyValidationError


def _event(index: int, *, source: str = "regime_intelligence") -> IntelligenceEvent:
    return IntelligenceEvent(
        event_id=f"intel-tbtcusd-20260316-{index:04d}",
        source=source,
        timestamp=f"2026-03-16T12:{index:02d}:00+00:00",
        asset="tBTCUSD",
        topic="regime",
        signal_type="observation",
        confidence=0.5 + (index * 0.1),
        references=(
            IntelligenceReference(kind="artifact", ref=f"ART-2026-{index:04d}-B", label="second"),
            IntelligenceReference(kind="artifact", ref=f"ART-2026-{index:04d}-A", label="first"),
        ),
        summary=f"Deterministic intelligence event {index}.",
    )


def _validated_event(index: int, *, source: str = "regime_intelligence"):
    return validate_intelligence_event(_event(index, source=source))


def _service(tmp_path: Path) -> ResearchLedgerService:
    return ResearchLedgerService(LedgerStorage(root=tmp_path / "artifacts" / "research_ledger"))


def test_adapter_exports_are_available_from_package_root() -> None:
    assert (
        DeterministicIntelligenceLedgerAdapter.__name__ == "DeterministicIntelligenceLedgerAdapter"
    )
    assert (
        map_validated_event_to_artifact_record.__name__ == "map_validated_event_to_artifact_record"
    )


def test_mapping_preserves_request_serialization_integrity_and_reference_order() -> None:
    validated_event = _validated_event(1)
    before_payload = deepcopy(validated_event.event.to_payload())

    record = map_validated_event_to_artifact_record(validated_event, entity_id="ART-2026-0001")
    payload = record_to_dict(record)

    assert record.entity_type is LedgerEntityType.ARTIFACT
    assert record.artifact_kind is ArtifactKind.INTELLIGENCE_OUTPUT
    assert record.created_at == validated_event.event.timestamp
    assert (
        record.path
        == "intelligence/regime_intelligence/tBTCUSD/regime/intel-tbtcusd-20260316-0001.json"
    )
    assert tuple(ref.metadata["source_ref"] for ref in record.intelligence_refs) == (
        "ART-2026-0001-B",
        "ART-2026-0001-A",
    )
    assert payload["metadata"]["event"] == before_payload
    assert payload["metadata"]["validator_version"] == "intelligence_event.v1"
    assert validated_event.event.to_payload() == before_payload


def test_mapping_adds_strategy_family_to_intelligence_ref_metadata_when_provided() -> None:
    validated_event = _validated_event(1)

    record = map_validated_event_to_artifact_record(
        validated_event,
        entity_id="ART-2026-0001",
        strategy_family="ri",
        strategy_family_source="family_registry_v1",
    )

    assert all(ref.metadata["strategy_family"] == "ri" for ref in record.intelligence_refs)
    assert all(
        ref.metadata["strategy_family_source"] == "family_registry_v1"
        for ref in record.intelligence_refs
    )


def test_persist_events_preserves_tuple_order_and_returns_correct_result(tmp_path: Path) -> None:
    service = _service(tmp_path)
    adapter = DeterministicIntelligenceLedgerAdapter(
        service=service,
        strategy_config={"strategy_family": "legacy"},
        strategy_family="legacy",
    )
    request = LedgerPersistenceRequest(events=(_validated_event(2), _validated_event(1)))
    before_payloads = deepcopy(tuple(item.event.to_payload() for item in request.events))

    result = adapter.persist_events(request)
    persisted_records = service.storage.list_records(LedgerEntityType.ARTIFACT)

    assert result.persisted_event_ids == (
        "intel-tbtcusd-20260316-0002",
        "intel-tbtcusd-20260316-0001",
    )
    assert result.ledger_entity_ids == ("ART-2026-0001", "ART-2026-0002")
    assert tuple(record.entity_id for record in persisted_records) == result.ledger_entity_ids
    assert tuple(record.metadata["event"]["event_id"] for record in persisted_records) == (
        "intel-tbtcusd-20260316-0002",
        "intel-tbtcusd-20260316-0001",
    )
    assert {record.metadata["strategy_family"] for record in persisted_records} == {"legacy"}
    assert {record.metadata["strategy_family_source"] for record in persisted_records} == {
        "family_registry_v1"
    }
    assert {
        ref.metadata["strategy_family"]
        for record in persisted_records
        for ref in record.intelligence_refs
    } == {"legacy"}
    assert {
        ref.metadata["strategy_family_source"]
        for record in persisted_records
        for ref in record.intelligence_refs
    } == {"family_registry_v1"}
    assert tuple(item.event.to_payload() for item in request.events) == before_payloads


def test_repeated_runs_on_fresh_storage_produce_identical_persistence_mapping(
    tmp_path: Path,
) -> None:
    request = LedgerPersistenceRequest(events=(_validated_event(1), _validated_event(2)))

    first_service = _service(tmp_path / "run_one")
    second_service = _service(tmp_path / "run_two")
    first_adapter = DeterministicIntelligenceLedgerAdapter(
        service=first_service,
        strategy_config={"strategy_family": "legacy"},
        strategy_family="legacy",
    )
    second_adapter = DeterministicIntelligenceLedgerAdapter(
        service=second_service,
        strategy_config={"strategy_family": "legacy"},
        strategy_family="legacy",
    )

    first_result = first_adapter.persist_events(request)
    second_result = second_adapter.persist_events(request)
    first_records = tuple(
        record_to_dict(record)
        for record in first_service.storage.list_records(LedgerEntityType.ARTIFACT)
    )
    second_records = tuple(
        record_to_dict(record)
        for record in second_service.storage.list_records(LedgerEntityType.ARTIFACT)
    )

    assert first_result == second_result
    assert first_records == second_records


def test_persist_events_fails_fast_without_strategy_family_context(tmp_path: Path) -> None:
    service = _service(tmp_path)
    adapter = DeterministicIntelligenceLedgerAdapter(service=service)

    with pytest.raises(ValueError, match="strategy_family_context_required"):
        adapter.persist_events(LedgerPersistenceRequest(events=(_validated_event(1),)))

    assert service.storage.list_records(LedgerEntityType.ARTIFACT) == []


def test_persist_events_preserves_invalid_strategy_family_errors(tmp_path: Path) -> None:
    service = _service(tmp_path)
    adapter = DeterministicIntelligenceLedgerAdapter(
        service=service,
        strategy_config={
            "strategy_family": "ri",
            "thresholds": {
                "entry_conf_overall": 0.25,
                "regime_proba": {"balanced": 0.36},
                "signal_adaptation": {
                    "atr_period": 14,
                    "zones": {
                        "low": {"entry_conf_overall": 0.16, "regime_proba": 0.33},
                        "mid": {"entry_conf_overall": 0.40, "regime_proba": 0.51},
                        "high": {"entry_conf_overall": 0.32, "regime_proba": 0.57},
                    },
                },
            },
            "gates": {"hysteresis_steps": 2, "cooldown_bars": 0},
            "multi_timeframe": {"regime_intelligence": {"authority_mode": "regime_module"}},
        },
    )

    with pytest.raises(StrategyFamilyValidationError, match="ri_requires_canonical_gates"):
        adapter.persist_events(LedgerPersistenceRequest(events=(_validated_event(1),)))

    assert service.storage.list_records(LedgerEntityType.ARTIFACT) == []
