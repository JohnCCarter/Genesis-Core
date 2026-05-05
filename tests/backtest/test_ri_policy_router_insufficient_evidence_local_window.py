from __future__ import annotations

import pandas as pd
import pytest

from scripts.analyze.ri_policy_router_insufficient_evidence_local_window_20260429 import (
    LocalWindowEvidenceError,
    NormalizedActionDiffRow,
    SubjectBounds,
    _validate_exact_insufficient_evidence_cluster,
    build_local_envelope,
    group_adjacent_timestamps,
    select_exact_rows,
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


def test_group_adjacent_timestamps_uses_inclusive_24h_rule() -> None:
    timestamps = [
        pd.Timestamp("2021-03-26T12:00:00+00:00"),
        pd.Timestamp("2021-03-27T12:00:00+00:00"),
        pd.Timestamp("2021-03-28T15:00:00+00:00"),
    ]

    groups = group_adjacent_timestamps(timestamps, max_gap=pd.Timedelta(hours=24))

    assert groups == [
        [
            pd.Timestamp("2021-03-26T12:00:00+00:00"),
            pd.Timestamp("2021-03-27T12:00:00+00:00"),
        ],
        [pd.Timestamp("2021-03-28T15:00:00+00:00")],
    ]


def test_select_exact_rows_and_validate_cluster_require_exact_match() -> None:
    exact_timestamps = (
        pd.Timestamp("2021-03-26T12:00:00+00:00"),
        pd.Timestamp("2021-03-27T06:00:00+00:00"),
        pd.Timestamp("2021-03-27T15:00:00+00:00"),
        pd.Timestamp("2021-03-28T00:00:00+00:00"),
    )
    rows = [
        _row(
            timestamp=timestamp.isoformat(),
            switch_reason="insufficient_evidence",
            absent_action="LONG",
            enabled_action="NONE",
            selected_policy="RI_no_trade_policy",
        )
        for timestamp in exact_timestamps
    ]
    rows.append(
        _row(
            "2021-03-29T00:00:00+00:00",
            switch_reason="stable_continuation_state",
            absent_action="NONE",
            enabled_action="LONG",
            selected_policy="RI_continuation_policy",
        )
    )

    _validate_exact_insufficient_evidence_cluster(rows, exact_timestamps=exact_timestamps)
    matched = select_exact_rows(
        rows,
        exact_timestamps=exact_timestamps,
        expected_reason="insufficient_evidence",
        expected_action_pair=("LONG", "NONE"),
    )

    assert [row.timestamp for row in matched] == list(exact_timestamps)


def test_select_exact_rows_rejects_wrong_action_pair() -> None:
    rows = [
        _row(
            "2021-03-26T15:00:00+00:00",
            switch_reason="stable_continuation_state",
            absent_action="LONG",
            enabled_action="NONE",
            selected_policy="RI_continuation_policy",
        )
    ]

    with pytest.raises(LocalWindowEvidenceError, match="reason/action validation"):
        select_exact_rows(
            rows,
            exact_timestamps=(pd.Timestamp("2021-03-26T15:00:00+00:00"),),
            expected_reason="stable_continuation_state",
            expected_action_pair=("NONE", "LONG"),
        )


def test_build_local_envelope_extends_target_bounds_by_padding() -> None:
    bounds = build_local_envelope(
        SubjectBounds(
            start=pd.Timestamp("2021-03-26T12:00:00+00:00"),
            end=pd.Timestamp("2021-03-28T00:00:00+00:00"),
        ),
        padding=pd.Timedelta(hours=24),
    )

    assert bounds.start == pd.Timestamp("2021-03-25T12:00:00+00:00")
    assert bounds.end == pd.Timestamp("2021-03-29T00:00:00+00:00")
