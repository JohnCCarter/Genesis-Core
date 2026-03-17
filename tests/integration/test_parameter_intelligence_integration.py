from __future__ import annotations

from tests.helpers.research_system import build_harness


def test_parameter_intelligence_outputs_attach_to_research_result(tmp_path) -> None:
    harness = build_harness(tmp_path)

    result = harness.orchestrator.run(harness.task)
    recommendations = result.stage_outputs.parameter_recommendations
    evaluation_ids = tuple(item.event_id for item in result.stage_outputs.evaluations)

    assert (
        tuple(item.parameter_set_id for item in recommendations)
        == result.recommended_parameter_set_ids
    )
    assert (
        tuple(
            item.parameter_set_id
            for item in recommendations
            if item.advisory_disposition == "preferred"
        )
        == result.preferred_parameter_set_ids
    )
    assert result.top_advisory_parameter_set_id == recommendations[0].parameter_set_id
    assert all(
        item.advisory_disposition in {"preferred", "review", "defer"} for item in recommendations
    )
    assert all(item.supporting_event_ids == evaluation_ids for item in recommendations)
    assert tuple(item.source_ledger_entity_ids for item in recommendations) == (
        ("ART-2026-a001",),
        ("ART-2026-b001",),
    )
