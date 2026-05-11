from __future__ import annotations

import copy

import scripts.analyze.ri_policy_router_2023_12_vs_2017_03_continuation_local_window_concentration_20260506 as subject


def _row(
    timestamp: str,
    *,
    absent_action: str = "NONE",
    enabled_action: str = "LONG",
    zone: str | None = "low",
    switch_reason: str | None = "stable_continuation_state",
    selected_policy: str | None = "RI_continuation_policy",
    previous_policy: str | None = "RI_no_trade_policy",
) -> dict[str, object]:
    return {
        "timestamp": timestamp,
        "enabled": {
            "action": enabled_action,
            "router_debug": {
                "zone": zone,
                "switch_reason": switch_reason,
                "selected_policy": selected_policy,
                "previous_policy": previous_policy,
            },
        },
        "absent": {"action": absent_action},
    }


def _window_rows(year: int, month: int, day: int, count: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    hour = 0
    for index in range(count):
        rows.append(
            _row(
                f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:00:00+00:00",
                previous_policy=None if index == 0 and count > 1 else "RI_no_trade_policy",
            )
        )
        hour += 9
        if hour >= 24:
            day += hour // 24
            hour %= 24
    return rows


def _rows_2017() -> list[dict[str, object]]:
    windows = [
        (1, 4),
        (4, 3),
        (8, 3),
        (12, 2),
        (16, 1),
        (19, 1),
        (22, 1),
        (26, 1),
        (29, 1),
    ]
    rows: list[dict[str, object]] = []
    for day, count in windows:
        rows.extend(_window_rows(2017, 3, day, count))
    rows.append(_row("2017-07-01T00:00:00+00:00"))
    return rows


def _rows_2023() -> list[dict[str, object]]:
    windows = [
        (1, 7),
        (8, 6),
        (14, 3),
        (18, 2),
        (22, 2),
        (27, 1),
        (29, 1),
    ]
    rows: list[dict[str, object]] = []
    for day, count in windows:
        rows.extend(_window_rows(2023, 12, day, count))
    rows.append(_row("2023-06-01T00:00:00+00:00"))
    return rows


def test_continuation_local_window_concentration_accepts_optional_null_and_detects_difference(
    monkeypatch,
) -> None:
    rows_2017 = _rows_2017()
    rows_2023 = _rows_2023()

    def _fake_load_json(path):
        if path == subject.ROOT_DIR / subject.ACTION_DIFF_RELATIVE_BY_SUBJECT["2017-03"]:
            return copy.deepcopy(rows_2017)
        if path == subject.ROOT_DIR / subject.ACTION_DIFF_RELATIVE_BY_SUBJECT["2023-12"]:
            return copy.deepcopy(rows_2023)
        raise AssertionError(f"Unexpected JSON load path: {path}")

    monkeypatch.setattr(subject, "_load_json", _fake_load_json)

    result = subject.run_continuation_local_window_concentration(base_sha="test-sha")

    assert result["status"] == subject.STATUS_DIFFERS
    assert result["subject_summaries"]["2017-03"]["window_size_sequence_desc"] == [
        4,
        3,
        3,
        2,
        1,
        1,
        1,
        1,
        1,
    ]
    assert result["subject_summaries"]["2023-12"]["window_size_sequence_desc"] == [
        7,
        6,
        3,
        2,
        2,
        1,
        1,
    ]
    assert result["subject_summaries"]["2017-03"]["largest_window_share"] == 0.235294
    assert result["subject_summaries"]["2023-12"]["largest_window_share"] == 0.318182
    assert result["subject_summaries"]["2017-03"]["top_two_window_share"] == 0.411765
    assert result["subject_summaries"]["2023-12"]["top_two_window_share"] == 0.590909
    assert result["subject_summaries"]["2017-03"]["rows_with_null_previous_policy"] >= 1
    assert result["subject_summaries"]["2023-12"]["rows_with_null_previous_policy"] >= 1
    assert result["cross_subject_comparison"]["same_window_size_sequence_desc"] is False


def test_continuation_local_window_concentration_fails_closed_when_required_surface_is_missing(
    monkeypatch,
) -> None:
    rows_2023 = _rows_2023()

    def _fake_load_json(path):
        if path == subject.ROOT_DIR / subject.ACTION_DIFF_RELATIVE_BY_SUBJECT["2017-03"]:
            raise FileNotFoundError(path)
        if path == subject.ROOT_DIR / subject.ACTION_DIFF_RELATIVE_BY_SUBJECT["2023-12"]:
            return copy.deepcopy(rows_2023)
        raise AssertionError(f"Unexpected JSON load path: {path}")

    monkeypatch.setattr(subject, "_load_json", _fake_load_json)

    result = subject.run_continuation_local_window_concentration(base_sha="test-sha")

    assert result["status"] == subject.STATUS_FAIL_CLOSED
    assert result["failure_reason"].startswith("Missing fixed continuation surface at ")


def test_continuation_local_window_concentration_rejects_missing_required_family_fields(
    monkeypatch,
) -> None:
    malformed_2017 = _rows_2017()
    malformed_2017[0]["enabled"]["router_debug"]["zone"] = None
    rows_2023 = _rows_2023()

    def _fake_load_json(path):
        if path == subject.ROOT_DIR / subject.ACTION_DIFF_RELATIVE_BY_SUBJECT["2017-03"]:
            return copy.deepcopy(malformed_2017)
        if path == subject.ROOT_DIR / subject.ACTION_DIFF_RELATIVE_BY_SUBJECT["2023-12"]:
            return copy.deepcopy(rows_2023)
        raise AssertionError(f"Unexpected JSON load path: {path}")

    monkeypatch.setattr(subject, "_load_json", _fake_load_json)

    result = subject.run_continuation_local_window_concentration(base_sha="test-sha")

    assert result["status"] == subject.STATUS_FAIL_CLOSED
    assert "zone" in result["failure_reason"]
