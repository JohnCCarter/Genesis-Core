from __future__ import annotations

import copy

import scripts.analyze.ri_policy_router_2023_vs_2017_mixed_year_shape_comparison_20260506 as subject


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
            "2017": {
                "window": {
                    "start": "2017-01-01T00:00:00+00:00",
                    "end": "2017-12-31T21:00:00+00:00",
                    "partial_year": False,
                },
                "comparison": {
                    "enabled_total_return_pct": 1.1,
                    "absent_total_return_pct": 1.5,
                    "enabled_profit_factor": 1.6,
                    "absent_profit_factor": 1.9,
                    "enabled_max_drawdown_pct": 0.4,
                    "absent_max_drawdown_pct": 0.6,
                    "enabled_position_net_pnl": 11.0,
                    "absent_position_net_pnl": 15.0,
                    "action_diff_count": 8,
                    "reason_only_diff_count": 3,
                },
            },
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
            },
        }
    }


def _annual_rows_2017() -> list[dict[str, object]]:
    return [
        _row(
            "2017-07-10T00:00:00+00:00",
            absent_action="LONG",
            enabled_action="NONE",
            zone="low",
            switch_reason="insufficient_evidence",
            selected_policy="RI_no_trade_policy",
            previous_policy=None,
        ),
        _row(
            "2017-07-11T00:00:00+00:00",
            absent_action="LONG",
            enabled_action="NONE",
            zone="low",
            switch_reason="AGED_WEAK_CONTINUATION_GUARD",
            selected_policy="RI_no_trade_policy",
            previous_policy="RI_no_trade_policy",
        ),
        _row(
            "2017-02-10T00:00:00+00:00",
            absent_action="NONE",
            enabled_action="LONG",
            zone="low",
            switch_reason="stable_continuation_state",
            selected_policy="RI_continuation_policy",
            previous_policy="RI_no_trade_policy",
        ),
        _row(
            "2017-02-11T00:00:00+00:00",
            absent_action="NONE",
            enabled_action="LONG",
            zone="low",
            switch_reason="stable_continuation_state",
            selected_policy="RI_continuation_policy",
            previous_policy="RI_continuation_policy",
        ),
        _row(
            "2017-07-12T00:00:00+00:00",
            absent_action="NONE",
            enabled_action="LONG",
            zone="low",
            switch_reason="stable_continuation_state",
            selected_policy="RI_continuation_policy",
            previous_policy="RI_no_trade_policy",
        ),
    ]


def _annual_rows_2023() -> list[dict[str, object]]:
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
    ]


def test_mixed_year_shape_comparison_ranks_both_years_and_detects_difference(monkeypatch) -> None:
    summary_payload = _summary_payload()
    annual_rows_2017 = _annual_rows_2017()
    annual_rows_2023 = _annual_rows_2023()

    def _fake_load_json(path):
        if path == subject.ROOT_DIR / subject.ANNUAL_SUMMARY_RELATIVE:
            return copy.deepcopy(summary_payload)
        if path == subject.ROOT_DIR / subject.ANNUAL_DIFF_RELATIVE_BY_YEAR["2017"]:
            return copy.deepcopy(annual_rows_2017)
        if path == subject.ROOT_DIR / subject.ANNUAL_DIFF_RELATIVE_BY_YEAR["2023"]:
            return copy.deepcopy(annual_rows_2023)
        raise AssertionError(f"Unexpected JSON load path: {path}")

    monkeypatch.setattr(subject, "_load_json", _fake_load_json)

    result = subject.run_2023_vs_2017_mixed_year_shape_comparison(base_sha="test-sha")

    assert result["status"] == subject.STATUS_DIFFERS
    assert result["status"] in {
        subject.STATUS_DIFFERS,
        subject.STATUS_OVERLAPS,
        subject.STATUS_FAIL_CLOSED,
    }
    assert result["year_summaries"]["2017"]["primary_top_combined_month"] == {
        "month_number": 7,
        "month_name": "July",
        "count": 3,
        "share_of_counted_rows": 0.6,
    }
    assert result["year_summaries"]["2017"]["primary_top_suppression_month"] == {
        "month_number": 7,
        "month_name": "July",
        "count": 2,
        "share_of_counted_rows": 1.0,
    }
    assert result["year_summaries"]["2017"]["primary_top_continuation_month"] == {
        "month_number": 2,
        "month_name": "February",
        "count": 2,
        "share_of_counted_rows": 0.666667,
    }
    assert result["year_summaries"]["2023"]["primary_top_combined_month"] == {
        "month_number": 12,
        "month_name": "December",
        "count": 3,
        "share_of_counted_rows": 0.5,
    }
    assert result["year_summaries"]["2023"]["primary_top_suppression_month"] == {
        "month_number": 6,
        "month_name": "June",
        "count": 2,
        "share_of_counted_rows": 0.666667,
    }
    assert result["year_summaries"]["2023"]["primary_top_continuation_month"] == {
        "month_number": 12,
        "month_name": "December",
        "count": 2,
        "share_of_counted_rows": 0.666667,
    }
    assert result["cross_year_comparison"] == {
        "primary_top_combined_months": {
            "2017": {
                "month_number": 7,
                "month_name": "July",
                "count": 3,
                "share_of_counted_rows": 0.6,
            },
            "2023": {
                "month_number": 12,
                "month_name": "December",
                "count": 3,
                "share_of_counted_rows": 0.5,
            },
        },
        "primary_top_suppression_months": {
            "2017": {
                "month_number": 7,
                "month_name": "July",
                "count": 2,
                "share_of_counted_rows": 1.0,
            },
            "2023": {
                "month_number": 6,
                "month_name": "June",
                "count": 2,
                "share_of_counted_rows": 0.666667,
            },
        },
        "primary_top_continuation_months": {
            "2017": {
                "month_number": 2,
                "month_name": "February",
                "count": 2,
                "share_of_counted_rows": 0.666667,
            },
            "2023": {
                "month_number": 12,
                "month_name": "December",
                "count": 2,
                "share_of_counted_rows": 0.666667,
            },
        },
        "tied_top_combined_month_numbers": {"2017": [7], "2023": [12]},
        "tied_top_suppression_month_numbers": {"2017": [7], "2023": [6]},
        "tied_top_continuation_month_numbers": {"2017": [2], "2023": [12]},
        "same_top_combined_month_set": False,
        "same_top_suppression_month_set": False,
        "same_top_continuation_month_set": False,
        "year_specific_checks": {
            "2017": {
                "december_is_primary_top_combined": False,
                "june_is_primary_top_suppression": False,
            },
            "2023": {
                "december_is_primary_top_combined": True,
                "december_is_primary_top_continuation": True,
                "june_is_primary_top_suppression": True,
            },
        },
    }


def test_mixed_year_shape_comparison_fails_closed_when_required_surface_is_missing(
    monkeypatch,
) -> None:
    summary_payload = _summary_payload()
    annual_rows_2023 = _annual_rows_2023()

    def _fake_load_json(path):
        if path == subject.ROOT_DIR / subject.ANNUAL_SUMMARY_RELATIVE:
            return copy.deepcopy(summary_payload)
        if path == subject.ROOT_DIR / subject.ANNUAL_DIFF_RELATIVE_BY_YEAR["2017"]:
            raise FileNotFoundError(path)
        if path == subject.ROOT_DIR / subject.ANNUAL_DIFF_RELATIVE_BY_YEAR["2023"]:
            return copy.deepcopy(annual_rows_2023)
        raise AssertionError(f"Unexpected JSON load path: {path}")

    monkeypatch.setattr(subject, "_load_json", _fake_load_json)

    result = subject.run_2023_vs_2017_mixed_year_shape_comparison(base_sha="test-sha")

    assert result["status"] == subject.STATUS_FAIL_CLOSED
    assert result["failure_reason"].startswith("Missing 2017 annual diff surface at ")
    assert (
        result["failure_reason"]
        .replace("\\", "/")
        .endswith(subject.ANNUAL_DIFF_RELATIVE_BY_YEAR["2017"].as_posix())
    )


def test_mixed_year_shape_comparison_rejects_malformed_rows(monkeypatch) -> None:
    summary_payload = _summary_payload()
    broken_rows_2017 = [
        _row(
            "2017-07-10T00:00:00+00:00",
            absent_action="LONG",
            enabled_action="NONE",
            zone=None,
            switch_reason="insufficient_evidence",
            selected_policy="RI_no_trade_policy",
            previous_policy="RI_continuation_policy",
        )
    ]
    annual_rows_2023 = _annual_rows_2023()

    def _fake_load_json(path):
        if path == subject.ROOT_DIR / subject.ANNUAL_SUMMARY_RELATIVE:
            return copy.deepcopy(summary_payload)
        if path == subject.ROOT_DIR / subject.ANNUAL_DIFF_RELATIVE_BY_YEAR["2017"]:
            return copy.deepcopy(broken_rows_2017)
        if path == subject.ROOT_DIR / subject.ANNUAL_DIFF_RELATIVE_BY_YEAR["2023"]:
            return copy.deepcopy(annual_rows_2023)
        raise AssertionError(f"Unexpected JSON load path: {path}")

    monkeypatch.setattr(subject, "_load_json", _fake_load_json)

    result = subject.run_2023_vs_2017_mixed_year_shape_comparison(base_sha="test-sha")

    assert result["status"] == subject.STATUS_FAIL_CLOSED
    assert "router_debug" in result["failure_reason"] or "zone" in result["failure_reason"]
