# ruff: noqa: E402

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def _find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "pyproject.toml").exists() and (candidate / "src").exists():
            return candidate
    raise RuntimeError("Could not locate repository root from probe path")


ROOT_DIR = _find_repo_root(Path(__file__).resolve())
SRC_DIR = ROOT_DIR / "src"
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from scripts.analyze import (
    ri_policy_router_continuation_release_hysteresis_local_action_position_equivalence_20260526 as action_base,
)
from scripts.analyze import (
    ri_policy_router_continuation_release_hysteresis_local_envelope_cancellation_candidate_2024_01_20260526 as envelope_2024_01,
)
from scripts.analyze import (
    ri_policy_router_continuation_release_hysteresis_local_packet_candidate_2024_01_20260526 as packet_2024_01,
)

NEGATIVE_CANDIDATE = packet_2024_01.NEGATIVE_CANDIDATE
POSITIVE_CONTROL = packet_2024_01.POSITIVE_CONTROL
SUBJECT_DEFINITIONS = (NEGATIVE_CANDIDATE, POSITIVE_CONTROL)
LOCAL_PACKET_RELATIVE = Path(
    "results/evaluation/ri_policy_router_continuation_release_hysteresis_local_packet_candidate_2024_01_2026-05-26.json"
)
LOCAL_ENVELOPE_RELATIVE = Path(
    "results/evaluation/ri_policy_router_continuation_release_hysteresis_local_envelope_cancellation_candidate_2024_01_2026-05-26.json"
)
OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = "ri_policy_router_continuation_release_hysteresis_local_action_position_equivalence_candidate_2024_01_2026-05-26.json"
STATUS_OK = (
    "continuation_release_hysteresis_local_action_position_equivalence_candidate_2024_01_generated"
)
STATUS_FAIL_CLOSED = "continuation_release_hysteresis_local_action_position_equivalence_candidate_2024_01_fail_closed"


class Candidate202401ActionPositionEquivalenceError(RuntimeError):
    pass


def _subject_payload(
    spec: envelope_2024_01.envelope_base.EnvelopeSubjectSpec,
    *,
    exact_envelope_timestamps: tuple[str, ...],
    base_cfg: dict[str, Any],
    carrier_cfg: dict[str, Any],
    authority: Any,
) -> dict[str, Any]:
    baseline = action_base._run_case_with_action_position_rows(
        "baseline",
        start_date=spec.month_start,
        end_date=spec.month_end,
        base_cfg=base_cfg,
        carrier_cfg=carrier_cfg,
        authority=authority,
    )
    release_zero = action_base._run_case_with_action_position_rows(
        "release_zero",
        start_date=spec.month_start,
        end_date=spec.month_end,
        base_cfg=base_cfg,
        carrier_cfg=carrier_cfg,
        authority=authority,
    )

    observed_baseline_timestamps = tuple(baseline["continuation_release_timestamps"])
    observed_release_zero_timestamps = tuple(release_zero["continuation_release_timestamps"])
    if observed_baseline_timestamps != spec.baseline_timestamps:
        raise Candidate202401ActionPositionEquivalenceError(
            f"Baseline continuation-release timestamps drifted for {spec.subject_id}: "
            f"expected={spec.baseline_timestamps}, actual={observed_baseline_timestamps}"
        )
    if observed_release_zero_timestamps != spec.release_zero_timestamps:
        raise Candidate202401ActionPositionEquivalenceError(
            f"Release-zero continuation-release timestamps drifted for {spec.subject_id}: "
            f"expected={spec.release_zero_timestamps}, actual={observed_release_zero_timestamps}"
        )

    baseline_summary = action_base.local_packet._coerce_dict(
        baseline.get("summary"), field_name=f"{spec.subject_id}.baseline.summary"
    )
    release_zero_summary = action_base.local_packet._coerce_dict(
        release_zero.get("summary"), field_name=f"{spec.subject_id}.release_zero.summary"
    )
    total_return_diff = action_base.local_packet._coerce_float(
        release_zero_summary.get("total_return"),
        field_name=f"{spec.subject_id}.release_zero.total_return",
    ) - action_base.local_packet._coerce_float(
        baseline_summary.get("total_return"),
        field_name=f"{spec.subject_id}.baseline.total_return",
    )
    final_capital_diff = action_base.local_packet._coerce_float(
        release_zero_summary.get("final_capital"),
        field_name=f"{spec.subject_id}.release_zero.final_capital",
    ) - action_base.local_packet._coerce_float(
        baseline_summary.get("final_capital"),
        field_name=f"{spec.subject_id}.baseline.final_capital",
    )
    if not action_base.math.isclose(
        total_return_diff, spec.inventory_total_return_diff, abs_tol=1e-12
    ):
        raise Candidate202401ActionPositionEquivalenceError(
            f"Monthly total return diff drifted for {spec.subject_id}: "
            f"expected={spec.inventory_total_return_diff}, actual={total_return_diff}"
        )
    if not action_base.math.isclose(
        final_capital_diff, spec.inventory_final_capital_diff, abs_tol=1e-9
    ):
        raise Candidate202401ActionPositionEquivalenceError(
            f"Monthly final capital diff drifted for {spec.subject_id}: "
            f"expected={spec.inventory_final_capital_diff}, actual={final_capital_diff}"
        )

    baseline_rows = action_base.local_packet._coerce_dict(
        baseline.get("rows"), field_name=f"{spec.subject_id}.baseline.rows"
    )
    release_zero_rows = action_base.local_packet._coerce_dict(
        release_zero.get("rows"), field_name=f"{spec.subject_id}.release_zero.rows"
    )

    available_timestamps = set(baseline_rows) | set(release_zero_rows)
    missing_timestamps = [
        timestamp
        for timestamp in exact_envelope_timestamps
        if timestamp not in available_timestamps
    ]
    if missing_timestamps:
        raise Candidate202401ActionPositionEquivalenceError(
            f"Envelope timestamps missing for {spec.subject_id}: {missing_timestamps}"
        )
    if len(exact_envelope_timestamps) != spec.envelope_row_count:
        raise Candidate202401ActionPositionEquivalenceError(
            f"Envelope row-count drift for {spec.subject_id}: expected={spec.envelope_row_count}, actual={len(exact_envelope_timestamps)}"
        )

    row_analyses = [
        action_base._analyze_envelope_row(
            str(timestamp),
            baseline_rows.get(str(timestamp)),
            release_zero_rows.get(str(timestamp)),
        )
        for timestamp in exact_envelope_timestamps
    ]
    row_summary = action_base._row_summary(row_analyses)

    return {
        "subject_id": spec.subject_id,
        "role": spec.role,
        "month_window": {
            "start": spec.month_start,
            "end": spec.month_end,
            "inventory_total_return_diff": action_base._round_or_none(
                spec.inventory_total_return_diff
            ),
            "inventory_final_capital_diff": action_base._round_or_none(
                spec.inventory_final_capital_diff
            ),
        },
        "envelope_window": {
            "start": spec.envelope_start,
            "end": spec.envelope_end,
            "row_count": spec.envelope_row_count,
            "span_hours": action_base._round_or_none(
                (
                    action_base.local_packet._parse_timestamp(spec.envelope_end)
                    - action_base.local_packet._parse_timestamp(spec.envelope_start)
                ).total_seconds()
                / 3600.0
            ),
            "exact_timestamps": list(exact_envelope_timestamps),
        },
        "continuation_release_timestamp_validation": {
            "baseline_matches_local_packet": True,
            "release_zero_matches_local_packet": True,
        },
        "monthly_reproduction": {
            "top_line_sign": action_base.local_packet._sign_label(total_return_diff),
            "rerun_total_return_diff": action_base._round_or_none(total_return_diff),
            "rerun_final_capital_diff": action_base._round_or_none(final_capital_diff),
            "matches_local_packet_total_return_diff": True,
            "matches_local_packet_final_capital_diff": True,
        },
        "row_summary": row_summary,
        "envelope_row_analysis": row_analyses,
    }


def _packet_summary(subject_payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    candidate = action_base.local_packet._coerce_dict(
        subject_payloads.get(NEGATIVE_CANDIDATE.subject_id),
        field_name=f"candidate_2024_01_equivalence.subject_payloads.{NEGATIVE_CANDIDATE.subject_id}",
    )
    control = action_base.local_packet._coerce_dict(
        subject_payloads.get(POSITIVE_CONTROL.subject_id),
        field_name=f"candidate_2024_01_equivalence.subject_payloads.{POSITIVE_CONTROL.subject_id}",
    )
    candidate_summary = action_base.local_packet._coerce_dict(
        candidate.get("row_summary"),
        field_name=f"{NEGATIVE_CANDIDATE.subject_id}.row_summary",
    )
    control_summary = action_base.local_packet._coerce_dict(
        control.get("row_summary"),
        field_name=f"{POSITIVE_CONTROL.subject_id}.row_summary",
    )

    candidate_execution_divergence_rows = int(
        action_base.local_packet._coerce_float(
            candidate_summary.get("execution_divergence_rows"),
            field_name=f"{NEGATIVE_CANDIDATE.subject_id}.execution_divergence_rows",
        )
    )
    control_execution_divergence_rows = int(
        action_base.local_packet._coerce_float(
            control_summary.get("execution_divergence_rows"),
            field_name=f"{POSITIVE_CONTROL.subject_id}.execution_divergence_rows",
        )
    )
    candidate_locked_size_rows = int(
        action_base.local_packet._coerce_float(
            candidate_summary.get("size_diff_absorbed_by_locked_position_rows"),
            field_name=f"{NEGATIVE_CANDIDATE.subject_id}.size_diff_absorbed_by_locked_position_rows",
        )
    )
    control_locked_size_rows = int(
        action_base.local_packet._coerce_float(
            control_summary.get("size_diff_absorbed_by_locked_position_rows"),
            field_name=f"{POSITIVE_CONTROL.subject_id}.size_diff_absorbed_by_locked_position_rows",
        )
    )
    candidate_router_internal_rows = int(
        action_base.local_packet._coerce_float(
            candidate_summary.get("router_internal_only_rows"),
            field_name=f"{NEGATIVE_CANDIDATE.subject_id}.router_internal_only_rows",
        )
    )
    control_router_internal_rows = int(
        action_base.local_packet._coerce_float(
            control_summary.get("router_internal_only_rows"),
            field_name=f"{POSITIVE_CONTROL.subject_id}.router_internal_only_rows",
        )
    )

    if candidate_execution_divergence_rows == 0 and control_execution_divergence_rows == 0:
        status = action_base.PACKET_STATUS_BOTH_ABSORBED
        inference = (
            "Both `2024-01` and `2023-05` keep the same execution-effect class on every exact envelope row. The "
            "new 2024 candidate's extra negative-like structure therefore still lives before execution, mainly as "
            "locked-position size/policy asymmetry rather than action or trade-path divergence."
        )
    elif candidate_execution_divergence_rows == 0:
        status = action_base.PACKET_STATUS_CANDIDATE_ABSORBED
        inference = (
            "`2024-01` stays absorbed before execution surface even though the control shows execution-surface "
            "divergence. The widened 2024 candidate's retained asymmetry remains pre-execution rather than economic."
        )
    else:
        status = action_base.PACKET_STATUS_CANDIDATE_DIVERGES
        inference = (
            "`2024-01` reaches execution-surface divergence inside the bounded envelope, so the retained local "
            "asymmetry is no longer confined to router-internal or locked-position state alone."
        )

    return {
        "status": status,
        "candidate_subject_id": NEGATIVE_CANDIDATE.subject_id,
        "control_subject_id": POSITIVE_CONTROL.subject_id,
        "candidate_execution_divergence_rows": candidate_execution_divergence_rows,
        "control_execution_divergence_rows": control_execution_divergence_rows,
        "candidate_locked_position_size_diff_rows": candidate_locked_size_rows,
        "control_locked_position_size_diff_rows": control_locked_size_rows,
        "candidate_router_internal_only_rows": candidate_router_internal_rows,
        "control_router_internal_only_rows": control_router_internal_rows,
        "inference": inference,
        "next_hypothesis": (
            "If this chain continues, the next honest slice is a candidate-only residual inventory around the rows "
            "where `2024-01` keeps locked-position size asymmetry, to test whether the widened 2024 case also "
            "collapses to a descriptive breadcrumb after execution-equivalent absorption."
        ),
    }


def _build_fail_closed_result(reason: str) -> dict[str, Any]:
    return {
        "audit_version": (
            "ri-policy-router-continuation-release-hysteresis-local-action-position-equivalence-candidate-2024-01-2026-05-26"
        ),
        "base_sha": action_base.local_packet._git_head_sha(),
        "status": STATUS_FAIL_CLOSED,
        "observational_only": True,
        "non_authoritative": True,
        "failure_reason": reason,
        "inputs": {
            "local_packet_artifact": str(LOCAL_PACKET_RELATIVE),
            "local_envelope_artifact": str(LOCAL_ENVELOPE_RELATIVE),
            "carrier_path": str(action_base.local_packet.CARRIER_PATH.relative_to(ROOT_DIR)),
            "working_contract_reference": str(action_base.local_packet.WORKING_CONTRACT_REFERENCE),
            "subjects": [definition.subject_id for definition in SUBJECT_DEFINITIONS],
            "focus_surface": "action, size, and pre-execution position equivalence inside the exact local envelope",
        },
    }


def run_candidate_2024_01_local_action_position_equivalence() -> dict[str, Any]:
    envelope_specs = envelope_2024_01._load_local_packet_specs()
    exact_envelope_timestamps = envelope_2024_01._load_exact_envelope_timestamps()
    base_cfg, carrier_cfg, authority = action_base.local_packet._load_base_and_carrier_cfg()
    subject_payloads = {
        definition.subject_id: _subject_payload(
            envelope_specs[definition.subject_id],
            exact_envelope_timestamps=exact_envelope_timestamps[definition.subject_id],
            base_cfg=base_cfg,
            carrier_cfg=carrier_cfg,
            authority=authority,
        )
        for definition in SUBJECT_DEFINITIONS
    }

    return {
        "audit_version": (
            "ri-policy-router-continuation-release-hysteresis-local-action-position-equivalence-candidate-2024-01-2026-05-26"
        ),
        "base_sha": action_base.local_packet._git_head_sha(),
        "status": STATUS_OK,
        "observational_only": True,
        "non_authoritative": True,
        "classification_boundary": {
            "reference_surface": (
                "exact local envelopes imported from the landed `2024-01` local envelope slice, rerun on the same "
                "carrier and compared only on action, size, and pre-execution position equivalence"
            ),
            "question": (
                "Inside the exact `2024-01` and `2023-05` local envelopes, do the retained baseline-vs-release_zero "
                "differences actually reach execution surface, or are they absorbed while both runs face the same "
                "pre-execution position context?"
            ),
            "outcome_metrics_observational_only": True,
        },
        "inputs": {
            "local_packet_artifact": str(LOCAL_PACKET_RELATIVE),
            "local_envelope_artifact": str(LOCAL_ENVELOPE_RELATIVE),
            "carrier_path": str(action_base.local_packet.CARRIER_PATH.relative_to(ROOT_DIR)),
            "working_contract_reference": str(action_base.local_packet.WORKING_CONTRACT_REFERENCE),
            "subjects": [definition.subject_id for definition in SUBJECT_DEFINITIONS],
            "comparison": {
                "baseline": "enabled carrier as-is (implicit shared hysteresis)",
                "release_zero": "same enabled carrier with continuation_release_hysteresis=0",
                "focus_surface": "action, size, router labels, and pre-execution position state",
                "negative_like_candidate": NEGATIVE_CANDIDATE.subject_id,
                "positive_control": POSITIVE_CONTROL.subject_id,
            },
        },
        "subject_payloads": subject_payloads,
        "packet_summary": _packet_summary(subject_payloads),
    }


def main() -> int:
    output_root = ROOT_DIR / action_base.OUTPUT_ROOT_RELATIVE
    output_json = output_root / OUTPUT_FILENAME
    try:
        result = run_candidate_2024_01_local_action_position_equivalence()
    except action_base.LocalActionPositionEquivalenceError as exc:
        result = _build_fail_closed_result(str(exc))
    except Candidate202401ActionPositionEquivalenceError as exc:
        result = _build_fail_closed_result(str(exc))

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    packet_summary = (
        action_base.local_packet._coerce_optional_dict(result.get("packet_summary")) or {}
    )
    summary = {
        "summary_artifact": str(output_json),
        "status": packet_summary.get("status", result.get("status")),
        "candidate_execution_divergence_rows": packet_summary.get(
            "candidate_execution_divergence_rows"
        ),
        "control_execution_divergence_rows": packet_summary.get(
            "control_execution_divergence_rows"
        ),
        "candidate_subject_id": packet_summary.get("candidate_subject_id"),
        "control_subject_id": packet_summary.get("control_subject_id"),
        "failure_reason": result.get("failure_reason"),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
