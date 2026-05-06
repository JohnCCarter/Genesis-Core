from __future__ import annotations

import copy

import scripts.analyze.ri_policy_router_insufficient_evidence_d1_late_2024_external_surface_falsifier_20260506 as subject


def _build_context_clean_artifact() -> dict[str, object]:
    def _field(
        field_name: str,
        *,
        target_bank_ceiling: float,
        descriptive_only: bool,
        source_timestamps: list[str],
    ) -> dict[str, object]:
        return {
            "admission": {
                "missing_timestamps": [],
                "row_count_checked": 33,
                "status": "evaluable",
            },
            "claim_status": "evaluated",
            "context_bank_min": target_bank_ceiling + 0.01,
            "context_bank_min_source_timestamps": ["2019-06-12T06:00:00+00:00"],
            "descriptive_only": descriptive_only,
            "excluded_from_pass_fail": descriptive_only,
            "field_name": field_name,
            "global_separation_margin": 0.01,
            "leaky_context_timestamps": [],
            "passes_context_clean_test": True,
            "surface_extrema": {},
            "target_bank_ceiling": target_bank_ceiling,
            "target_bank_ceiling_source_timestamps": source_timestamps,
        }

    return {
        "audit_version": "test-context-clean-artifact",
        "base_sha": "context-clean-sha",
        "status": "bounded_context_clean_selectivity_present",
        "field_context_clean_evaluations": [
            _field(
                "action_edge",
                target_bank_ceiling=0.033803,
                descriptive_only=False,
                source_timestamps=["2019-06-14T00:00:00+00:00"],
            ),
            _field(
                "confidence_gate",
                target_bank_ceiling=0.516902,
                descriptive_only=False,
                source_timestamps=["2019-06-14T00:00:00+00:00"],
            ),
            _field(
                "clarity_raw",
                target_bank_ceiling=0.364914,
                descriptive_only=False,
                source_timestamps=["2019-06-14T00:00:00+00:00"],
            ),
            _field(
                "clarity_score",
                target_bank_ceiling=36.0,
                descriptive_only=True,
                source_timestamps=["2019-06-14T00:00:00+00:00"],
            ),
        ],
    }


def _late_2024_row(
    timestamp: str,
    *,
    switch_reason: str,
    absent_action: str,
    enabled_action: str,
    action_edge: float,
    confidence_gate: float,
    clarity_score: float,
) -> dict[str, object]:
    return {
        "timestamp": timestamp,
        "absent_action": absent_action,
        "enabled_action": enabled_action,
        "action_pair": f"{absent_action}->{enabled_action}",
        "switch_reason": switch_reason,
        "selected_policy": "RI_no_trade_policy",
        "raw_target_policy": "RI_no_trade_policy",
        "previous_policy": "RI_continuation_policy",
        "zone": "low",
        "candidate": "LONG",
        "bars_since_regime_change": 281,
        "action_edge": action_edge,
        "confidence_gate": confidence_gate,
        "clarity_score": clarity_score,
        "fwd_4_close_return_pct": -0.25,
        "fwd_8_close_return_pct": -0.5,
        "fwd_16_close_return_pct": -0.75,
        "mfe_16_pct": 0.5,
        "mae_16_pct": -1.5,
    }


def _build_late_2024_pocket_artifact() -> dict[str, object]:
    target_rows = [
        _late_2024_row(
            subject.TARGET_TIMESTAMPS[0],
            switch_reason="insufficient_evidence",
            absent_action="LONG",
            enabled_action="NONE",
            action_edge=0.020001,
            confidence_gate=0.510001,
            clarity_score=36.0,
        ),
        _late_2024_row(
            subject.TARGET_TIMESTAMPS[1],
            switch_reason="insufficient_evidence",
            absent_action="LONG",
            enabled_action="NONE",
            action_edge=0.022001,
            confidence_gate=0.512001,
            clarity_score=36.0,
        ),
        _late_2024_row(
            subject.TARGET_TIMESTAMPS[2],
            switch_reason="insufficient_evidence",
            absent_action="LONG",
            enabled_action="NONE",
            action_edge=0.034101,
            confidence_gate=0.517201,
            clarity_score=36.0,
        ),
        _late_2024_row(
            subject.TARGET_TIMESTAMPS[3],
            switch_reason="insufficient_evidence",
            absent_action="LONG",
            enabled_action="NONE",
            action_edge=0.030001,
            confidence_gate=0.515001,
            clarity_score=36.0,
        ),
        _late_2024_row(
            subject.TARGET_TIMESTAMPS[4],
            switch_reason="insufficient_evidence",
            absent_action="LONG",
            enabled_action="NONE",
            action_edge=0.031001,
            confidence_gate=0.513001,
            clarity_score=36.0,
        ),
    ]
    aged_weak_rows = [
        _late_2024_row(
            subject.AGED_WEAK_SIBLING_TIMESTAMPS[0],
            switch_reason="AGED_WEAK_CONTINUATION_GUARD",
            absent_action="LONG",
            enabled_action="NONE",
            action_edge=0.050001,
            confidence_gate=0.530001,
            clarity_score=37.0,
        ),
        _late_2024_row(
            subject.AGED_WEAK_SIBLING_TIMESTAMPS[1],
            switch_reason="AGED_WEAK_CONTINUATION_GUARD",
            absent_action="LONG",
            enabled_action="NONE",
            action_edge=0.051001,
            confidence_gate=0.531001,
            clarity_score=37.0,
        ),
        _late_2024_row(
            subject.AGED_WEAK_SIBLING_TIMESTAMPS[2],
            switch_reason="AGED_WEAK_CONTINUATION_GUARD",
            absent_action="LONG",
            enabled_action="NONE",
            action_edge=0.052001,
            confidence_gate=0.532001,
            clarity_score=38.0,
        ),
        _late_2024_row(
            subject.AGED_WEAK_SIBLING_TIMESTAMPS[3],
            switch_reason="AGED_WEAK_CONTINUATION_GUARD",
            absent_action="LONG",
            enabled_action="NONE",
            action_edge=0.053001,
            confidence_gate=0.533001,
            clarity_score=38.0,
        ),
    ]
    stable_displacement_rows = [
        _late_2024_row(
            subject.STABLE_DISPLACEMENT_TIMESTAMPS[0],
            switch_reason="stable_continuation_state",
            absent_action="NONE",
            enabled_action="LONG",
            action_edge=0.054001,
            confidence_gate=0.534001,
            clarity_score=37.0,
        )
    ]
    stable_blocked_rows = [
        _late_2024_row(
            subject.STABLE_BLOCKED_CONTEXT_TIMESTAMPS[0],
            switch_reason="stable_continuation_state",
            absent_action="LONG",
            enabled_action="NONE",
            action_edge=0.055001,
            confidence_gate=0.535001,
            clarity_score=38.0,
        )
    ]

    return {
        "audit_version": "test-late-2024-pocket-artifact",
        "base_sha": "late-2024-pocket-sha",
        "status": "test-surface",
        "artifact_row_lock": {
            "target_timestamp_count": 9,
            "comparison_timestamp_count": 1,
            "stable_context_timestamp_count": 1,
            "target_reason_counts": {
                "AGED_WEAK_CONTINUATION_GUARD": 4,
                "insufficient_evidence": 5,
            },
        },
        "cohorts": {
            "regression_target": {
                "rows": [*target_rows, *aged_weak_rows],
            },
            "stable_continuation_displacement_comparison": {
                "rows": stable_displacement_rows,
            },
            "stable_continuation_blocked_context": {
                "rows": stable_blocked_rows,
            },
        },
    }


def test_external_surface_falsifier_locks_surface_and_keeps_clarity_score_descriptive_only(
    monkeypatch,
) -> None:
    context_clean_artifact = _build_context_clean_artifact()
    late_2024_artifact = _build_late_2024_pocket_artifact()

    def _fake_load_json(path):
        if path == subject.ROOT_DIR / subject.CONTEXT_CLEAN_ARTIFACT_RELATIVE:
            return copy.deepcopy(context_clean_artifact)
        if path == subject.ROOT_DIR / subject.LATE_2024_SOURCE_ARTIFACT_RELATIVE:
            return copy.deepcopy(late_2024_artifact)
        raise AssertionError(f"Unexpected JSON load path: {path}")

    monkeypatch.setattr(subject, "_load_json", _fake_load_json)

    result = subject.run_late_2024_external_surface_falsifier(base_sha="test-base-sha")

    assert result["artifact_row_lock"] == {
        "target_count": 5,
        "antitarget_count": 6,
        "total_count": 11,
        "target_timestamps": list(subject.TARGET_TIMESTAMPS),
        "antitarget_timestamps": [
            *subject.AGED_WEAK_SIBLING_TIMESTAMPS,
            *subject.STABLE_DISPLACEMENT_TIMESTAMPS,
            *subject.STABLE_BLOCKED_CONTEXT_TIMESTAMPS,
        ],
        "full_surface_timestamps": [
            "2024-11-28T15:00:00+00:00",
            "2024-11-29T00:00:00+00:00",
            "2024-11-29T09:00:00+00:00",
            "2024-11-29T18:00:00+00:00",
            "2024-11-30T03:00:00+00:00",
            "2024-11-30T12:00:00+00:00",
            "2024-11-30T21:00:00+00:00",
            "2024-12-01T00:00:00+00:00",
            "2024-12-01T06:00:00+00:00",
            "2024-12-01T15:00:00+00:00",
            "2024-12-02T00:00:00+00:00",
        ],
        "additional_unlabeled_rows": 0,
    }

    action_edge = next(
        evaluation
        for evaluation in result["field_transport_evaluations"]
        if evaluation["field_name"] == "action_edge"
    )
    confidence_gate = next(
        evaluation
        for evaluation in result["field_transport_evaluations"]
        if evaluation["field_name"] == "confidence_gate"
    )
    clarity_raw = next(
        evaluation
        for evaluation in result["field_transport_evaluations"]
        if evaluation["field_name"] == "clarity_raw"
    )
    clarity_score = next(
        evaluation
        for evaluation in result["field_transport_evaluations"]
        if evaluation["field_name"] == "clarity_score"
    )

    assert action_edge["claim_status"] == "transport_falsified"
    assert action_edge["selected_target_summary"]["selected_count"] == 4
    assert action_edge["selected_antitarget_summary"]["selected_count"] == 0
    assert action_edge["missed_target_rows"] == [
        {
            "timestamp": "2024-11-30T03:00:00+00:00",
            "value": 0.034101,
            "switch_reason": "insufficient_evidence",
        }
    ]

    assert confidence_gate["claim_status"] == "transport_falsified"
    assert confidence_gate["selected_target_summary"]["selected_count"] == 4
    assert confidence_gate["selected_antitarget_summary"]["selected_count"] == 0

    assert clarity_raw["claim_status"] == "not_evaluable"
    assert clarity_raw["external_surface_admission"] == {
        "status": "missing",
        "missing_timestamps": [
            "2024-11-28T15:00:00+00:00",
            "2024-11-29T00:00:00+00:00",
            "2024-11-29T09:00:00+00:00",
            "2024-11-29T18:00:00+00:00",
            "2024-11-30T03:00:00+00:00",
            "2024-11-30T12:00:00+00:00",
            "2024-11-30T21:00:00+00:00",
            "2024-12-01T00:00:00+00:00",
            "2024-12-01T06:00:00+00:00",
            "2024-12-01T15:00:00+00:00",
            "2024-12-02T00:00:00+00:00",
        ],
        "row_count_checked": 11,
    }

    assert clarity_score["descriptive_only"] is True
    assert clarity_score["exact_transport_shape_match"] is True
    assert clarity_score["passes_transport_test"] is False

    assert result["status"] == "external_surface_falsified"
    assert result["transport_summary"] == {
        "admitted_survivor_field_names": [],
        "admitted_falsified_field_names": ["action_edge", "confidence_gate"],
        "not_evaluable_claim_field_names": ["clarity_raw"],
        "descriptive_shape_match_field_names": ["clarity_score"],
        "best_partial_claim_field": action_edge,
        "bounded_signal_present": False,
    }
