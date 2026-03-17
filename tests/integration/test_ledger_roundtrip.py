from __future__ import annotations

from core.research_ledger import LedgerEntityType, validate_record
from core.research_ledger.models import record_to_dict
from tests.helpers.research_system import build_harness


def test_persisted_artifacts_are_readable_and_valid_in_research_ledger(tmp_path) -> None:
    harness = build_harness(tmp_path)

    result = harness.orchestrator.run(harness.task)
    records = harness.service.storage.list_records(LedgerEntityType.ARTIFACT)
    reloaded_records = tuple(
        harness.service.storage.read_record(LedgerEntityType.ARTIFACT, record.entity_id)
        for record in records
    )

    assert tuple(record.entity_id for record in records) == (
        result.stage_outputs.persistence_result.ledger_entity_ids
    )
    assert tuple(record.metadata["event"]["event_id"] for record in records) == (
        result.stage_outputs.persistence_result.persisted_event_ids
    )
    for record in records:
        validate_record(record)
    assert tuple(record_to_dict(record) for record in records) == tuple(
        record_to_dict(record) for record in reloaded_records
    )
