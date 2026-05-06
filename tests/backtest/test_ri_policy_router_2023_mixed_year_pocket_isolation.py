from __future__ import annotations

import copy

import scripts.analyze.ri_policy_router_2023_mixed_year_pocket_isolation_20260506 as subject


def _row(
    timestamp: str,
    *,
    absent_action: str,
    enabled_action: str,
    zone: str | None = None,
    switch_reason: str | None = None,
    selected_policy: str | None = None,
    previous_policy: str | None = None,
) -> dict[str, object]:
    debug = None
    if (
        zone is not None
        or switch_reason is not None
        or selected_policy is not None
        or previous_policy is not None
    ):
        debug = {
            "zone": zone,
            "switch_reason": switch_reason,
            "selected_policy": selected_policy,
            "previous_policy": previous_policy,
            "candidate": "LONG",
        }
    return {
        "timestamp": timestamp,
        "enabled": {
            "action": enabled_action,
            "router_debug": debug,
        },
        "absent": {
            "action": absent_action,
        },
    }


def _summary_payload() -> dict[str, object]:
    return {
        "years": {
            "2023": {
                "window": {
                    "start": "2023-01-01T00:00:00+00:00",
                    "end": "2023-12-31T21:00:00+00:00",
                    "partial_year": False,
                },
                "comparison": {
                    "enabled_total_return_pct": 1.0,
                    "absent_total_return_pct": 2.0,
                    "enabled_profit_factor": 1.5,
                    "absent_profit_factor": 2.0,
                    "enabled_max_drawdown_pct": 0.5,
                    "absent_max_drawdown_pct": 0.7,
                    "enabled_position_net_pnl": 10.0,
                    "absent_position_net_pnl": 20.0,
                    "action_diff_count": 10,
                    "reason_only_diff_count": 5,
                },
            }
        }
    }


def _annual_rows() -> list[dict[str, object]]:
    return [
        _row(
            "2023-06-10T00:00:00+00:00",
            absent_action="LONG",
            enabled_action="NONE",
            zone="low",
            switch_reason="insufficient_evidence",
            selected_policy="RI_no_trade_policy",
            previous_policy="RI_continuation_policy",
        ),
        _row(
            "2023-06-11T00:00:00+00:00",
            absent_action="LONG",
            enabled_action="NONE",
            zone="low",
            switch_reason="AGED_WEAK_CONTINUATION_GUARD",
            selected_policy="RI_no_trade_policy",
            previous_policy="RI_no_trade_policy",
        ),
        _row(
            "2023-12-20T03:00:00+00:00",
            absent_action="LONG",
            enabled_action="NONE",
            zone="low",
            switch_reason="insufficient_evidence",
            selected_policy="RI_no_trade_policy",
            previous_policy="RI_continuation_policy",
        ),
        _row(
            "2023-12-21T18:00:00+00:00",
            absent_action="LONG",
            enabled_action="NONE",
            zone="mid",
            switch_reason="insufficient_evidence",
            selected_policy="RI_no_trade_policy",
            previous_policy="RI_no_trade_policy",
        ),
        _row(
            "2023-12-22T09:00:00+00:00",
            absent_action="LONG",
            enabled_action="NONE",
            zone="high",
            switch_reason="AGED_WEAK_CONTINUATION_GUARD",
            selected_policy="RI_no_trade_policy",
            previous_policy="RI_no_trade_policy",
        ),
        _row(
            "2023-12-23T00:00:00+00:00",
            absent_action="NONE",
            enabled_action="LONG",
            zone="low",
            switch_reason="stable_continuation_state",
            selected_policy="RI_continuation_policy",
            previous_policy="RI_no_trade_policy",
        ),
        _row(
            "2023-12-24T00:00:00+00:00",
            absent_action="NONE",
            enabled_action="LONG",
            zone="low",
            switch_reason="stable_continuation_state",
            selected_policy="RI_continuation_policy",
            previous_policy="RI_continuation_policy",
        ),
        _row(
            "2023-01-05T00:00:00+00:00",
            absent_action="NONE",
            enabled_action="LONG",
            zone="low",
            switch_reason="stable_continuation_state",
            selected_policy="RI_continuation_policy",
            previous_policy="RI_no_trade_policy",
        ),
        _row(
            "2023-12-28T09:00:00+00:00",
            absent_action="LONG",
            enabled_action="NONE",
            zone="mid",
            switch_reason="AGED_WEAK_CONTINUATION_GUARD",
            selected_policy="RI_no_trade_policy",
            previous_policy="RI_no_trade_policy",
        ),
        _row(
            "2023-12-30T21:00:00+00:00",
            absent_action="LONG",
            enabled_action="NONE",
            zone="high",
            switch_reason="AGED_WEAK_CONTINUATION_GUARD",
            selected_policy="RI_no_trade_policy",
            previous_policy="RI_no_trade_policy",
        ),
    ]


def test_mixed_year_pocket_isolation_ranks_months_and_tracks_anchor_overlap(monkeypatch) -> None:
    summary_payload = _summary_payload()
    annual_rows = _annual_rows()

    def _fake_load_json(path):
        if path == subject.ROOT_DIR / subject.ANNUAL_SUMMARY_RELATIVE:
            return copy.deepcopy(summary_payload)
        if path == subject.ROOT_DIR / subject.ANNUAL_2023_DIFF_RELATIVE:
            return copy.deepcopy(annual_rows)
        raise AssertionError(f"Unexpected JSON load path: {path}")

    monkeypatch.setattr(subject, "_load_json", _fake_load_json)

    result = subject.run_2023_mixed_year_pocket_isolation(base_sha="test-sha")

    assert result["status"] == "december_is_top_shared_shape_month"
    assert result["shared_shape_summary"] == {
        "counted_row_count": 6,
        "top_combined_month": {
            "month": "2023-12",
            "count": 3,
            "share_of_counted_rows": 0.5,
        },
        "top_suppression_month": {
            "month": "2023-06",
            "count": 2,
            "share_of_counted_rows": 0.666667,
        },
        "top_continuation_month": {
            "month": "2023-12",
            "count": 2,
            "share_of_counted_rows": 0.666667,
        },
        "december_combined_rank": 1,
        "december_is_top_month": True,
        "december_combined_count": 3,
        "december_share_of_total": 0.5,
    }
    assert result["month_rankings"] == {
        "combined": [
            {"month": "2023-12", "count": 3, "share_of_counted_rows": 0.5},
            {"month": "2023-06", "count": 2, "share_of_counted_rows": 0.333333},
            {"month": "2023-01", "count": 1, "share_of_counted_rows": 0.166667},
        ],
        "suppression": [
            {"month": "2023-06", "count": 2, "share_of_counted_rows": 0.666667},
            {"month": "2023-12", "count": 1, "share_of_counted_rows": 0.333333},
        ],
        "continuation_displacement": [
            {"month": "2023-12", "count": 2, "share_of_counted_rows": 0.666667},
            {"month": "2023-01", "count": 1, "share_of_counted_rows": 0.333333},
        ],
    }
    assert result["december_anchor_rows"] == {
        "configured_anchor_timestamps": list(subject.DECEMBER_ANCHOR_TIMESTAMPS),
        "seen_on_annual_surface": [
            {
                "timestamp": "2023-12-20T03:00:00+00:00",
                "family_name": "suppression",
                "absent_action": "LONG",
                "enabled_action": "NONE",
                "switch_reason": "insufficient_evidence",
                "selected_policy": "RI_no_trade_policy",
                "previous_policy": "RI_continuation_policy",
                "zone": "low",
                "candidate": "LONG",
                "bars_since_regime_change": None,
                "matches_shared_shape": True,
            },
            {
                "timestamp": "2023-12-21T18:00:00+00:00",
                "family_name": None,
                "absent_action": "LONG",
                "enabled_action": "NONE",
                "switch_reason": "insufficient_evidence",
                "selected_policy": "RI_no_trade_policy",
                "previous_policy": "RI_no_trade_policy",
                "zone": "mid",
                "candidate": "LONG",
                "bars_since_regime_change": None,
                "matches_shared_shape": False,
            },
            {
                "timestamp": "2023-12-22T09:00:00+00:00",
                "family_name": None,
                "absent_action": "LONG",
                "enabled_action": "NONE",
                "switch_reason": "AGED_WEAK_CONTINUATION_GUARD",
                "selected_policy": "RI_no_trade_policy",
                "previous_policy": "RI_no_trade_policy",
                "zone": "high",
                "candidate": "LONG",
                "bars_since_regime_change": None,
                "matches_shared_shape": False,
            },
            {
                "timestamp": "2023-12-28T09:00:00+00:00",
                "family_name": None,
                "absent_action": "LONG",
                "enabled_action": "NONE",
                "switch_reason": "AGED_WEAK_CONTINUATION_GUARD",
                "selected_policy": "RI_no_trade_policy",
                "previous_policy": "RI_no_trade_policy",
                "zone": "mid",
                "candidate": "LONG",
                "bars_since_regime_change": None,
                "matches_shared_shape": False,
            },
            {
                "timestamp": "2023-12-30T21:00:00+00:00",
                "family_name": None,
                "absent_action": "LONG",
                "enabled_action": "NONE",
                "switch_reason": "AGED_WEAK_CONTINUATION_GUARD",
                "selected_policy": "RI_no_trade_policy",
                "previous_policy": "RI_no_trade_policy",
                "zone": "high",
                "candidate": "LONG",
                "bars_since_regime_change": None,
                "matches_shared_shape": False,
            },
        ],
        "matching_shared_shape": [
            {
                "timestamp": "2023-12-20T03:00:00+00:00",
                "month": "2023-12",
                "family_name": "suppression",
                "absent_action": "LONG",
                "enabled_action": "NONE",
                "switch_reason": "insufficient_evidence",
                "selected_policy": "RI_no_trade_policy",
                "previous_policy": "RI_continuation_policy",
                "zone": "low",
                "candidate": "LONG",
                "bars_since_regime_change": None,
            }
        ],
        "missing_from_annual_surface": [],
        "seen_but_not_matching_shared_shape": [
            "2023-12-21T18:00:00+00:00",
            "2023-12-22T09:00:00+00:00",
            "2023-12-28T09:00:00+00:00",
            "2023-12-30T21:00:00+00:00",
        ],
    }


def test_mixed_year_pocket_isolation_fails_closed_when_2023_surface_is_missing(monkeypatch) -> None:
    def _fake_load_json(path):
        raise FileNotFoundError(path)

    monkeypatch.setattr(subject, "_load_json", _fake_load_json)

    result = subject.run_2023_mixed_year_pocket_isolation(base_sha="test-sha")

    assert result["status"] == "fail_closed_missing_2023_annual_surface"
    assert result["failure_reason"].startswith("Missing annual summary surface at ")
    assert result["failure_reason"].endswith(
        "results\\backtests\\ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only\\enabled_vs_absent_all_years_summary.json"
    )


def test_mixed_year_pocket_isolation_rejects_malformed_candidate_rows(monkeypatch) -> None:
    summary_payload = _summary_payload()
    broken_rows = [
        _row(
            "2023-12-20T03:00:00+00:00",
            absent_action="LONG",
            enabled_action="NONE",
            zone=None,
            switch_reason="insufficient_evidence",
            selected_policy="RI_no_trade_policy",
            previous_policy="RI_continuation_policy",
        )
    ]

    def _fake_load_json(path):
        if path == subject.ROOT_DIR / subject.ANNUAL_SUMMARY_RELATIVE:
            return copy.deepcopy(summary_payload)
        if path == subject.ROOT_DIR / subject.ANNUAL_2023_DIFF_RELATIVE:
            return copy.deepcopy(broken_rows)
        raise AssertionError(f"Unexpected JSON load path: {path}")

    monkeypatch.setattr(subject, "_load_json", _fake_load_json)

    result = subject.run_2023_mixed_year_pocket_isolation(base_sha="test-sha")

    assert result["status"] == "fail_closed_missing_2023_annual_surface"
    assert "router_debug" in result["failure_reason"] or "zone" in result["failure_reason"]
