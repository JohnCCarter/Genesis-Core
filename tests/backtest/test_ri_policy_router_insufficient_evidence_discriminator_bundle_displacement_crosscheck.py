from __future__ import annotations

import pytest

from scripts.analyze.ri_policy_router_insufficient_evidence_discriminator_bundle_displacement_crosscheck_20260430 import (
    ACTION_DIFF_ROOT_RELATIVE,
    ALLOWED_OBSERVATIONAL_PROXY_FIELDS,
    CURATED_CANDLES_RELATIVE,
    LocalWindowEvidenceError,
    classify_gap_direction,
    run_displacement_crosscheck,
    select_exact_rows_by_definition,
    summarize_numeric_metric,
)


def _row(
    timestamp: str,
    *,
    switch_reason: str,
    absent_action: str,
    enabled_action: str,
) -> dict[str, object]:
    return {
        "timestamp": timestamp,
        "absent": {"action": absent_action},
        "enabled": {
            "action": enabled_action,
            "router_debug": {
                "switch_reason": switch_reason,
                "zone": "low",
                "selected_policy": "RI_no_trade_policy",
                "raw_target_policy": "RI_no_trade_policy",
                "regime": "balanced",
                "confidence_level": 0,
                "mandate_level": 0,
                "switch_proposed": False,
                "switch_blocked": False,
                "bars_since_regime_change": 12,
                "dwell_duration": 4,
                "action_edge": 0.02,
                "confidence_gate": 0.51,
                "clarity_raw": 0.36,
                "clarity_score": 36,
            },
        },
    }


def test_select_exact_rows_by_definition_requires_exact_match_and_returns_sorted_rows() -> None:
    exact_timestamps = (
        "2021-03-26T12:00:00+00:00",
        "2021-03-27T06:00:00+00:00",
        "2021-03-27T15:00:00+00:00",
    )
    rows = [
        _row(
            "2021-03-27T15:00:00+00:00",
            switch_reason="insufficient_evidence",
            absent_action="LONG",
            enabled_action="NONE",
        ),
        _row(
            "2021-03-26T12:00:00+00:00",
            switch_reason="insufficient_evidence",
            absent_action="LONG",
            enabled_action="NONE",
        ),
        _row(
            "2021-03-27T06:00:00+00:00",
            switch_reason="insufficient_evidence",
            absent_action="LONG",
            enabled_action="NONE",
        ),
        _row(
            "2021-03-29T00:00:00+00:00",
            switch_reason="stable_continuation_state",
            absent_action="NONE",
            enabled_action="LONG",
        ),
    ]

    matched = select_exact_rows_by_definition(
        rows,
        exact_timestamps=exact_timestamps,
        expected_year="2021",
        expected_switch_reason="insufficient_evidence",
        expected_action_pair=("LONG", "NONE"),
    )

    assert [row["timestamp"] for row in matched] == list(exact_timestamps)


def test_select_exact_rows_by_definition_rejects_wrong_switch_reason() -> None:
    with pytest.raises(LocalWindowEvidenceError, match="switch-reason validation"):
        select_exact_rows_by_definition(
            [
                _row(
                    "2025-03-13T15:00:00+00:00",
                    switch_reason="insufficient_evidence",
                    absent_action="NONE",
                    enabled_action="LONG",
                )
            ],
            exact_timestamps=("2025-03-13T15:00:00+00:00",),
            expected_year="2025",
            expected_switch_reason="stable_continuation_state",
            expected_action_pair=("NONE", "LONG"),
        )


@pytest.mark.parametrize(
    ("left_gap", "right_gap", "expected"),
    [
        (1.0, 2.0, "same_positive"),
        (-1.0, -0.5, "same_negative"),
        (0.0, 0.0, "both_zero"),
        (1.0, -1.0, "opposite_or_mixed"),
        (None, 1.0, "missing"),
    ],
)
def test_classify_gap_direction_reports_recurrence_shape(
    left_gap: float | None,
    right_gap: float | None,
    expected: str,
) -> None:
    assert classify_gap_direction(left_gap, right_gap) == expected


def test_summarize_numeric_metric_reports_range_and_positive_share() -> None:
    summary = summarize_numeric_metric([1.0, -2.0, 3.0])

    assert summary == {
        "count": 3,
        "min": -2.0,
        "max": 3.0,
        "mean": 0.666667,
        "median": 1.0,
        "gt_zero_share": 0.666667,
    }


def test_run_displacement_crosscheck_provenance_is_fail_closed() -> None:
    result = run_displacement_crosscheck(base_sha="test-sha")

    assert set(result["inputs"]) == {
        "action_diff_root",
        "negative_year_diff",
        "positive_year_diff",
        "curated_candles",
    }
    assert result["inputs"] == {
        "action_diff_root": str(ACTION_DIFF_ROOT_RELATIVE),
        "negative_year_diff": str(
            ACTION_DIFF_ROOT_RELATIVE / "2021_enabled_vs_absent_action_diffs.json"
        ),
        "positive_year_diff": str(
            ACTION_DIFF_ROOT_RELATIVE / "2025_enabled_vs_absent_action_diffs.json"
        ),
        "curated_candles": str(CURATED_CANDLES_RELATIVE),
    }
    assert result["comparison_contract"]["allowed_observational_proxy_fields"] == list(
        ALLOWED_OBSERVATIONAL_PROXY_FIELDS
    )
