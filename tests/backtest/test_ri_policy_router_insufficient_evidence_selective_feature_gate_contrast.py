from __future__ import annotations

import pytest

from scripts.analyze.ri_policy_router_insufficient_evidence_selective_feature_gate_contrast_20260430 import (
    LocalWindowEvidenceError,
    _require_router_debug,
    select_exact_target_rows,
    summarize_numeric_metric,
)


def _target_row(timestamp: str) -> dict[str, object]:
    return {
        "timestamp": timestamp,
        "absent": {"action": "LONG"},
        "enabled": {
            "action": "NONE",
            "reasons": ["ZONE:low@0.160", "RESEARCH_POLICY_ROUTER_NO_TRADE"],
            "router_debug": {
                "switch_reason": "insufficient_evidence",
                "selected_policy": "RI_no_trade_policy",
                "raw_target_policy": "RI_no_trade_policy",
                "previous_policy": "RI_no_trade_policy",
                "zone": "low",
                "candidate": "LONG",
                "bars_since_regime_change": 72,
                "action_edge": 0.02,
                "confidence_gate": 0.51,
                "clarity_raw": 0.36,
                "clarity_score": 36,
                "confidence_level": 0,
                "mandate_level": 0,
                "dwell_duration": 4,
                "regime": "balanced",
                "switch_proposed": False,
                "switch_blocked": False,
                "size_multiplier": 0.0,
            },
        },
    }


def test_select_exact_target_rows_requires_exact_match_and_returns_sorted_rows() -> None:
    exact_timestamps = (
        "2021-03-26T12:00:00+00:00",
        "2021-03-27T06:00:00+00:00",
        "2021-03-27T15:00:00+00:00",
    )
    rows = [
        _target_row("2021-03-27T15:00:00+00:00"),
        _target_row("2021-03-26T12:00:00+00:00"),
        _target_row("2021-03-27T06:00:00+00:00"),
        _target_row("2021-03-29T00:00:00+00:00"),
    ]

    matched = select_exact_target_rows(
        rows,
        exact_timestamps=exact_timestamps,
        expected_year="2021",
    )

    assert [row["timestamp"] for row in matched] == list(exact_timestamps)


def test_require_router_debug_rejects_missing_required_field() -> None:
    row = _target_row("2021-03-26T12:00:00+00:00")
    del row["enabled"]["router_debug"]["confidence_gate"]  # type: ignore[index]

    with pytest.raises(LocalWindowEvidenceError, match="missing required router_debug fields"):
        _require_router_debug(row)  # type: ignore[arg-type]


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
