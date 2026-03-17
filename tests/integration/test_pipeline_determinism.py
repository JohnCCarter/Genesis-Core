from __future__ import annotations

from core.research_ledger import LedgerEntityType
from core.research_ledger.models import record_to_dict
from tests.helpers.research_system import build_event, build_harness


def test_research_workflow_replay_is_identical_on_fresh_storage(tmp_path) -> None:
    input_events = (
        build_event(1, confidence=0.8),
        build_event(2, confidence=0.7),
    )
    first_harness = build_harness(tmp_path / "run_one", input_events=input_events)
    second_harness = build_harness(tmp_path / "run_two", input_events=input_events)

    first_result = first_harness.orchestrator.run(first_harness.task)
    second_result = second_harness.orchestrator.run(second_harness.task)
    first_records = tuple(
        record_to_dict(record)
        for record in first_harness.service.storage.list_records(LedgerEntityType.ARTIFACT)
    )
    second_records = tuple(
        record_to_dict(record)
        for record in second_harness.service.storage.list_records(LedgerEntityType.ARTIFACT)
    )

    assert first_result == second_result
    assert first_result.stage_outputs.persistence_result.persisted_event_ids == (
        "intel-tbtcusd-20260317-0001",
        "intel-tbtcusd-20260317-0002",
    )
    assert (
        first_result.stage_outputs.persistence_result
        == second_result.stage_outputs.persistence_result
    )
    assert first_records == second_records
