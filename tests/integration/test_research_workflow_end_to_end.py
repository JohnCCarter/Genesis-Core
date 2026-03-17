from __future__ import annotations

from core.research_ledger import LedgerEntityType
from tests.helpers.research_system import build_harness


def test_research_workflow_executes_end_to_end(tmp_path) -> None:
    harness = build_harness(tmp_path)

    result = harness.orchestrator.run(harness.task)
    persisted_records = harness.service.storage.list_records(LedgerEntityType.ARTIFACT)

    assert result.task_id == harness.task.task_id
    assert tuple(event.event_id for event in result.stage_outputs.collected_events) == (
        "intel-tbtcusd-20260317-0001",
        "intel-tbtcusd-20260317-0003",
    )
    assert tuple(item.event.event_id for item in result.stage_outputs.normalized_events) == (
        "intel-tbtcusd-20260317-0001",
        "intel-tbtcusd-20260317-0003",
    )
    assert tuple(item.event_id for item in result.stage_outputs.feature_sets) == (
        "intel-tbtcusd-20260317-0001",
        "intel-tbtcusd-20260317-0003",
    )
    assert tuple(item.event_id for item in result.stage_outputs.evaluations) == (
        "intel-tbtcusd-20260317-0001",
        "intel-tbtcusd-20260317-0003",
    )
    assert result.recommended_parameter_set_ids == ("ps-a", "ps-b")
    assert result.preferred_parameter_set_ids == ("ps-a",)
    assert result.top_advisory_parameter_set_id == "ps-a"
    assert result.stage_outputs.persistence_result.persisted_event_ids == (
        "intel-tbtcusd-20260317-0001",
        "intel-tbtcusd-20260317-0003",
    )
    assert tuple(record.entity_id for record in persisted_records) == (
        "ART-2026-0001",
        "ART-2026-0002",
    )
