from __future__ import annotations

import copy

import pytest

import scripts.analyze.ri_policy_router_insufficient_evidence_d1_2023_06_external_surface_falsifier_20260507 as subject


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


def _make_annual_diff_row(
    timestamp: str,
    *,
    absent_action: str,
    enabled_action: str,
    switch_reason: str,
    zone: str = "low",
    candidate: str = "LONG",
    selected_policy: str = "RI_no_trade_policy",
    previous_policy: str = "RI_continuation_policy",
    bars_since_regime_change: int = 100,
    action_edge: float | None = None,
    confidence_gate: float | None = None,
    clarity_score: float | None = None,
) -> dict[str, object]:
    router_debug: dict[str, object] = {
        "switch_reason": switch_reason,
        "selected_policy": selected_policy,
        "previous_policy": previous_policy,
        "zone": zone,
        "candidate": candidate,
        "bars_since_regime_change": bars_since_regime_change,
    }
    if action_edge is not None:
        router_debug["action_edge"] = action_edge
    if confidence_gate is not None:
        router_debug["confidence_gate"] = confidence_gate
    if clarity_score is not None:
        router_debug["clarity_score"] = clarity_score
    return {
        "timestamp": timestamp,
        "absent": {"action": absent_action},
        "enabled": {
            "action": enabled_action,
            "router_debug": router_debug,
        },
    }


def _build_annual_2023_diff(
    target_rows: list[dict[str, object]],
    antitarget_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    return [*target_rows, *antitarget_rows]


def _base_target_rows() -> list[dict[str, object]]:
    """Two 2023-06 target rows well below all D1 bank ceilings."""
    return [
        _make_annual_diff_row(
            "2023-06-05T00:00:00+00:00",
            absent_action="LONG",
            enabled_action="NONE",
            switch_reason="insufficient_evidence",
            action_edge=0.020000,
            confidence_gate=0.510000,
            clarity_score=35.0,
        ),
        _make_annual_diff_row(
            "2023-06-10T06:00:00+00:00",
            absent_action="LONG",
            enabled_action="NONE",
            switch_reason="insufficient_evidence",
            action_edge=0.025000,
            confidence_gate=0.514000,
            clarity_score=34.0,
        ),
    ]


def _base_antitarget_rows() -> list[dict[str, object]]:
    """One aged-weak row and one continuation row, both above D1 bank ceilings."""
    return [
        _make_annual_diff_row(
            "2023-06-03T12:00:00+00:00",
            absent_action="LONG",
            enabled_action="NONE",
            switch_reason="AGED_WEAK_CONTINUATION_GUARD",
            action_edge=0.060000,
            confidence_gate=0.560000,
            clarity_score=42.0,
        ),
        _make_annual_diff_row(
            "2023-06-15T00:00:00+00:00",
            absent_action="NONE",
            enabled_action="LONG",
            switch_reason="stable_continuation_state",
            action_edge=0.070000,
            confidence_gate=0.570000,
            clarity_score=45.0,
        ),
    ]


# ── Test 1: source_data_unavailable when annual diff is absent ──────────────────────────────


def test_source_data_unavailable_when_annual_diff_missing(monkeypatch) -> None:
    context_clean_artifact = _build_context_clean_artifact()

    def _fake_load_json(path):
        if str(path).endswith("context_clean_selectivity_falsifier_2026-05-05.json"):
            return copy.deepcopy(context_clean_artifact)
        raise FileNotFoundError(f"Simulated missing source: {path}")

    monkeypatch.setattr(subject, "_load_json", _fake_load_json)

    result = subject.run_2023_06_external_surface_falsifier(base_sha="test-base-sha")

    assert result["status"] == subject.STATUS_SOURCE_UNAVAILABLE
    assert "artifact_row_lock" not in result
    assert "field_transport_evaluations" not in result
    assert result["inputs"]["annual_2023_diff_source"]["available"] is False
    assert "2023_enabled_vs_absent_action_diffs.json" in str(
        result["inputs"]["annual_2023_diff_source"]["path"]
    )


# ── Test 2: external_surface_survivor when all target rows pass ─────────────────────────────


def test_external_surface_survivor_when_all_target_rows_pass(monkeypatch) -> None:
    context_clean_artifact = _build_context_clean_artifact()
    target_rows = _base_target_rows()
    antitarget_rows = _base_antitarget_rows()
    annual_diff = _build_annual_2023_diff(target_rows, antitarget_rows)

    def _fake_load_json(path):
        if str(path).endswith("context_clean_selectivity_falsifier_2026-05-05.json"):
            return copy.deepcopy(context_clean_artifact)
        if "2023_enabled_vs_absent_action_diffs.json" in str(path):
            return copy.deepcopy(annual_diff)
        raise AssertionError(f"Unexpected JSON load path: {path}")

    monkeypatch.setattr(subject, "_load_json", _fake_load_json)

    result = subject.run_2023_06_external_surface_falsifier(base_sha="test-base-sha")

    assert result["status"] == subject.STATUS_SURVIVOR
    assert result["artifact_row_lock"]["target_count"] == 2
    assert result["artifact_row_lock"]["antitarget_count"] == 2
    assert result["artifact_row_lock"]["subject_month"] == "2023-06"

    evaluations = result["field_transport_evaluations"]
    action_edge_ev = next(e for e in evaluations if e["field_name"] == "action_edge")
    confidence_gate_ev = next(e for e in evaluations if e["field_name"] == "confidence_gate")
    clarity_raw_ev = next(e for e in evaluations if e["field_name"] == "clarity_raw")
    clarity_score_ev = next(e for e in evaluations if e["field_name"] == "clarity_score")

    # Both admitted claim fields should survive the transport test
    assert action_edge_ev["claim_status"] == "transport_survivor"
    assert action_edge_ev["passes_transport_test"] is True
    assert action_edge_ev["selected_target_summary"]["selected_count"] == 2
    assert action_edge_ev["selected_antitarget_summary"]["selected_count"] == 0

    assert confidence_gate_ev["claim_status"] == "transport_survivor"
    assert confidence_gate_ev["passes_transport_test"] is True

    # clarity_raw is always not_evaluable on this surface
    assert clarity_raw_ev["claim_status"] == "not_evaluable"
    assert clarity_raw_ev["passes_transport_test"] is False
    assert clarity_raw_ev["external_surface_admission"]["status"] == "missing"

    # clarity_score is descriptive-only
    assert clarity_score_ev["descriptive_only"] is True
    assert clarity_score_ev["claim_status"] == "descriptive_only"

    ts = result["transport_summary"]
    assert "action_edge" in ts["admitted_survivor_field_names"]
    assert "confidence_gate" in ts["admitted_survivor_field_names"]
    assert "clarity_raw" in ts["not_evaluable_claim_field_names"]
    assert ts["bounded_signal_present"] is True


# ── Test 3: external_surface_falsified when target rows miss the ceiling ────────────────────


def test_external_surface_falsified_when_target_rows_exceed_ceiling(monkeypatch) -> None:
    context_clean_artifact = _build_context_clean_artifact()

    # Both target rows have action_edge and confidence_gate above the D1 bank ceiling
    target_rows_failing = [
        _make_annual_diff_row(
            "2023-06-05T00:00:00+00:00",
            absent_action="LONG",
            enabled_action="NONE",
            switch_reason="insufficient_evidence",
            action_edge=0.040000,  # above ceiling 0.033803
            confidence_gate=0.530000,  # above ceiling 0.516902
            clarity_score=40.0,
        ),
        _make_annual_diff_row(
            "2023-06-10T06:00:00+00:00",
            absent_action="LONG",
            enabled_action="NONE",
            switch_reason="insufficient_evidence",
            action_edge=0.045000,  # above ceiling 0.033803
            confidence_gate=0.540000,  # above ceiling 0.516902
            clarity_score=41.0,
        ),
    ]
    antitarget_rows = _base_antitarget_rows()
    annual_diff = _build_annual_2023_diff(target_rows_failing, antitarget_rows)

    def _fake_load_json(path):
        if str(path).endswith("context_clean_selectivity_falsifier_2026-05-05.json"):
            return copy.deepcopy(context_clean_artifact)
        if "2023_enabled_vs_absent_action_diffs.json" in str(path):
            return copy.deepcopy(annual_diff)
        raise AssertionError(f"Unexpected JSON load path: {path}")

    monkeypatch.setattr(subject, "_load_json", _fake_load_json)

    result = subject.run_2023_06_external_surface_falsifier(base_sha="test-base-sha")

    assert result["status"] == subject.STATUS_FALSIFIED
    evaluations = result["field_transport_evaluations"]
    action_edge_ev = next(e for e in evaluations if e["field_name"] == "action_edge")
    confidence_gate_ev = next(e for e in evaluations if e["field_name"] == "confidence_gate")

    assert action_edge_ev["claim_status"] == "transport_falsified"
    assert action_edge_ev["passes_transport_test"] is False
    assert action_edge_ev["selected_target_summary"]["selected_count"] == 0

    assert confidence_gate_ev["claim_status"] == "transport_falsified"
    assert confidence_gate_ev["passes_transport_test"] is False

    ts = result["transport_summary"]
    assert "action_edge" in ts["admitted_falsified_field_names"]
    assert "confidence_gate" in ts["admitted_falsified_field_names"]
    assert ts["bounded_signal_present"] is False


# ── Test 4: leaky antitarget causes falsification even when target passes ───────────────────


def test_leaky_antitarget_causes_falsification(monkeypatch) -> None:
    """A leaky antitarget row (value <= ceiling) falsifies the transport test for that field."""
    context_clean_artifact = _build_context_clean_artifact()
    target_rows = _base_target_rows()

    # antitarget row leaks through the action_edge ceiling
    antitarget_with_leak = [
        _make_annual_diff_row(
            "2023-06-03T12:00:00+00:00",
            absent_action="LONG",
            enabled_action="NONE",
            switch_reason="AGED_WEAK_CONTINUATION_GUARD",
            action_edge=0.030000,  # leaks through ceiling 0.033803
            confidence_gate=0.560000,
            clarity_score=42.0,
        ),
    ]
    annual_diff = _build_annual_2023_diff(target_rows, antitarget_with_leak)

    def _fake_load_json(path):
        if str(path).endswith("context_clean_selectivity_falsifier_2026-05-05.json"):
            return copy.deepcopy(context_clean_artifact)
        if "2023_enabled_vs_absent_action_diffs.json" in str(path):
            return copy.deepcopy(annual_diff)
        raise AssertionError(f"Unexpected JSON load path: {path}")

    monkeypatch.setattr(subject, "_load_json", _fake_load_json)

    result = subject.run_2023_06_external_surface_falsifier(base_sha="test-base-sha")

    evaluations = result["field_transport_evaluations"]
    action_edge_ev = next(e for e in evaluations if e["field_name"] == "action_edge")
    confidence_gate_ev = next(e for e in evaluations if e["field_name"] == "confidence_gate")

    # action_edge is falsified because the leaky antitarget row was selected
    assert action_edge_ev["claim_status"] == "transport_falsified"
    assert action_edge_ev["passes_transport_test"] is False
    assert action_edge_ev["exact_transport_shape_match"] is False
    assert action_edge_ev["selected_antitarget_summary"]["selected_count"] == 1
    assert len(action_edge_ev["leaky_antitarget_rows"]) == 1
    assert action_edge_ev["leaky_antitarget_rows"][0]["value"] == pytest.approx(0.030000)

    # confidence_gate still passes because the leaky row is above its ceiling
    assert confidence_gate_ev["claim_status"] == "transport_survivor"
    assert confidence_gate_ev["passes_transport_test"] is True
    assert confidence_gate_ev["selected_antitarget_summary"]["selected_count"] == 0

    # Overall still survivor if at least one admitted claim field passes
    assert result["status"] == subject.STATUS_SURVIVOR


# ── Test 5: row-lock assertions ──────────────────────────────────────────────────────────────


def test_row_lock_records_exact_surface(monkeypatch) -> None:
    context_clean_artifact = _build_context_clean_artifact()
    target_rows = _base_target_rows()
    antitarget_rows = _base_antitarget_rows()
    annual_diff = _build_annual_2023_diff(target_rows, antitarget_rows)

    def _fake_load_json(path):
        if str(path).endswith("context_clean_selectivity_falsifier_2026-05-05.json"):
            return copy.deepcopy(context_clean_artifact)
        if "2023_enabled_vs_absent_action_diffs.json" in str(path):
            return copy.deepcopy(annual_diff)
        raise AssertionError(f"Unexpected JSON load path: {path}")

    monkeypatch.setattr(subject, "_load_json", _fake_load_json)

    result = subject.run_2023_06_external_surface_falsifier(base_sha="test-base-sha")
    lock = result["artifact_row_lock"]

    assert lock["target_count"] == 2
    assert lock["antitarget_count"] == 2
    assert lock["total_count"] == 4
    assert lock["subject_month"] == "2023-06"
    assert lock["subject_zone"] == "low"
    assert lock["target_switch_reason"] == "insufficient_evidence"
    assert sorted(lock["antitarget_switch_reasons"]) == sorted(
        ["AGED_WEAK_CONTINUATION_GUARD", "stable_continuation_state"]
    )
    # Timestamps must be sorted
    target_ts = lock["target_timestamps"]
    assert target_ts == sorted(target_ts)
    antitarget_ts = lock["antitarget_timestamps"]
    assert antitarget_ts == sorted(antitarget_ts)
    # Full surface contains all rows
    assert lock["full_surface_timestamps"] == sorted(
        lock["target_timestamps"] + lock["antitarget_timestamps"]
    )


# ── Test 6: non-june rows are excluded from the surface ─────────────────────────────────────


def test_non_june_rows_excluded(monkeypatch) -> None:
    context_clean_artifact = _build_context_clean_artifact()
    target_rows = _base_target_rows()
    antitarget_rows = _base_antitarget_rows()
    # Add a row from a different month (should be excluded)
    non_june_row = _make_annual_diff_row(
        "2023-07-05T00:00:00+00:00",
        absent_action="LONG",
        enabled_action="NONE",
        switch_reason="insufficient_evidence",
        action_edge=0.015000,
        confidence_gate=0.505000,
        clarity_score=33.0,
    )
    annual_diff = _build_annual_2023_diff(target_rows + [non_june_row], antitarget_rows)

    def _fake_load_json(path):
        if str(path).endswith("context_clean_selectivity_falsifier_2026-05-05.json"):
            return copy.deepcopy(context_clean_artifact)
        if "2023_enabled_vs_absent_action_diffs.json" in str(path):
            return copy.deepcopy(annual_diff)
        raise AssertionError(f"Unexpected JSON load path: {path}")

    monkeypatch.setattr(subject, "_load_json", _fake_load_json)

    result = subject.run_2023_06_external_surface_falsifier(base_sha="test-base-sha")
    # The July row is excluded; target count remains 2
    assert result["artifact_row_lock"]["target_count"] == 2
    assert result["artifact_row_lock"]["total_count"] == 4
