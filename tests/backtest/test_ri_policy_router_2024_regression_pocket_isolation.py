from __future__ import annotations

import pandas as pd
import pytest

from scripts.analyze.ri_policy_router_2024_regression_pocket_isolation_20260430 import (
    EXPECTED_TARGET_REASON_COUNTS,
    LocalWindowEvidenceError,
    label_pocket_cohort,
    select_exact_target_rows,
)
from scripts.analyze.ri_policy_router_insufficient_evidence_local_window_20260429 import (
    NormalizedActionDiffRow,
)


def _row(
    timestamp: str,
    *,
    switch_reason: str,
    absent_action: str,
    enabled_action: str,
    selected_policy: str,
) -> NormalizedActionDiffRow:
    return NormalizedActionDiffRow(
        timestamp=pd.Timestamp(timestamp),
        switch_reason=switch_reason,
        absent_action=absent_action,
        enabled_action=enabled_action,
        selected_policy=selected_policy,
        raw_target_policy=selected_policy,
        previous_policy="baseline_absent",
        zone="low",
        candidate="LONG",
        bars_since_regime_change=72,
        action_edge=0.25,
        confidence_gate=0.8,
        clarity_score=0.6,
    )


def test_select_exact_target_rows_requires_exact_2024_reason_signature() -> None:
    exact_timestamps = (
        pd.Timestamp("2024-11-28T15:00:00+00:00"),
        pd.Timestamp("2024-11-29T00:00:00+00:00"),
        pd.Timestamp("2024-11-29T09:00:00+00:00"),
        pd.Timestamp("2024-11-29T18:00:00+00:00"),
        pd.Timestamp("2024-11-30T03:00:00+00:00"),
        pd.Timestamp("2024-11-30T12:00:00+00:00"),
        pd.Timestamp("2024-11-30T21:00:00+00:00"),
        pd.Timestamp("2024-12-01T15:00:00+00:00"),
        pd.Timestamp("2024-12-02T00:00:00+00:00"),
    )
    rows = [
        _row(
            timestamp.isoformat(),
            switch_reason=(
                "AGED_WEAK_CONTINUATION_GUARD"
                if index < EXPECTED_TARGET_REASON_COUNTS["AGED_WEAK_CONTINUATION_GUARD"]
                else "insufficient_evidence"
            ),
            absent_action="LONG",
            enabled_action="NONE",
            selected_policy="RI_no_trade_policy",
        )
        for index, timestamp in enumerate(exact_timestamps)
    ]

    matched = select_exact_target_rows(
        rows,
        exact_timestamps=exact_timestamps,
        expected_reason_counts=EXPECTED_TARGET_REASON_COUNTS,
    )

    assert [row.timestamp for row in matched] == list(exact_timestamps)


def test_select_exact_target_rows_rejects_reason_signature_drift() -> None:
    exact_timestamps = (
        pd.Timestamp("2024-11-28T15:00:00+00:00"),
        pd.Timestamp("2024-11-29T00:00:00+00:00"),
    )
    rows = [
        _row(
            "2024-11-28T15:00:00+00:00",
            switch_reason="AGED_WEAK_CONTINUATION_GUARD",
            absent_action="LONG",
            enabled_action="NONE",
            selected_policy="RI_no_trade_policy",
        ),
        _row(
            "2024-11-29T00:00:00+00:00",
            switch_reason="AGED_WEAK_CONTINUATION_GUARD",
            absent_action="LONG",
            enabled_action="NONE",
            selected_policy="RI_no_trade_policy",
        ),
    ]

    with pytest.raises(LocalWindowEvidenceError, match="reason-signature validation"):
        select_exact_target_rows(
            rows,
            exact_timestamps=exact_timestamps,
            expected_reason_counts={
                "AGED_WEAK_CONTINUATION_GUARD": 1,
                "insufficient_evidence": 1,
            },
        )


def test_label_pocket_cohort_keeps_stable_context_separate() -> None:
    target_timestamp = pd.Timestamp("2024-11-28T15:00:00+00:00")
    comparison_timestamp = pd.Timestamp("2024-12-01T00:00:00+00:00")
    stable_context_timestamp = pd.Timestamp("2024-12-01T06:00:00+00:00")
    other_timestamp = pd.Timestamp("2024-12-02T06:00:00+00:00")

    assert (
        label_pocket_cohort(
            _row(
                target_timestamp.isoformat(),
                switch_reason="insufficient_evidence",
                absent_action="LONG",
                enabled_action="NONE",
                selected_policy="RI_no_trade_policy",
            ),
            target_timestamps={target_timestamp},
            comparison_timestamps={comparison_timestamp},
            stable_context_timestamps={stable_context_timestamp},
        )
        == "regression_target"
    )
    assert (
        label_pocket_cohort(
            _row(
                comparison_timestamp.isoformat(),
                switch_reason="stable_continuation_state",
                absent_action="NONE",
                enabled_action="LONG",
                selected_policy="RI_continuation_policy",
            ),
            target_timestamps={target_timestamp},
            comparison_timestamps={comparison_timestamp},
            stable_context_timestamps={stable_context_timestamp},
        )
        == "stable_continuation_displacement_comparison"
    )
    assert (
        label_pocket_cohort(
            _row(
                stable_context_timestamp.isoformat(),
                switch_reason="stable_continuation_state",
                absent_action="LONG",
                enabled_action="NONE",
                selected_policy="RI_no_trade_policy",
            ),
            target_timestamps={target_timestamp},
            comparison_timestamps={comparison_timestamp},
            stable_context_timestamps={stable_context_timestamp},
        )
        == "stable_continuation_blocked_context"
    )
    assert (
        label_pocket_cohort(
            _row(
                other_timestamp.isoformat(),
                switch_reason="AGED_WEAK_CONTINUATION_GUARD",
                absent_action="LONG",
                enabled_action="NONE",
                selected_policy="RI_no_trade_policy",
            ),
            target_timestamps={target_timestamp},
            comparison_timestamps={comparison_timestamp},
            stable_context_timestamps={stable_context_timestamp},
        )
        == "context_only"
    )
