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
    ri_policy_router_continuation_release_hysteresis_local_envelope_cancellation_candidate_2020_06_20260526 as envelope_2020_06,
)
from scripts.analyze import (
    ri_policy_router_continuation_release_hysteresis_local_packet_candidate_2020_06_20260526 as packet_2020_06,
)

NEGATIVE_CANDIDATE = packet_2020_06.NEGATIVE_CANDIDATE
POSITIVE_CONTROL = packet_2020_06.POSITIVE_CONTROL
SUBJECT_DEFINITIONS = (NEGATIVE_CANDIDATE, POSITIVE_CONTROL)
LOCAL_PACKET_RELATIVE = Path(
    "results/evaluation/ri_policy_router_continuation_release_hysteresis_local_packet_candidate_2020_06_2026-05-26.json"
)
LOCAL_ENVELOPE_RELATIVE = Path(
    "results/evaluation/ri_policy_router_continuation_release_hysteresis_local_envelope_cancellation_candidate_2020_06_2026-05-26.json"
)
OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = "ri_policy_router_continuation_release_hysteresis_local_action_position_equivalence_candidate_2020_06_2026-05-26.json"
STATUS_OK = (
    "continuation_release_hysteresis_local_action_position_equivalence_candidate_2020_06_generated"
)
STATUS_FAIL_CLOSED = "continuation_release_hysteresis_local_action_position_equivalence_candidate_2020_06_fail_closed"


class Candidate202006ActionPositionEquivalenceError(RuntimeError):
    pass


def _packet_summary(subject_payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    candidate = action_base.local_packet._coerce_dict(
        subject_payloads.get(NEGATIVE_CANDIDATE.subject_id),
        field_name=f"candidate_2020_06_equivalence.subject_payloads.{NEGATIVE_CANDIDATE.subject_id}",
    )
    control = action_base.local_packet._coerce_dict(
        subject_payloads.get(POSITIVE_CONTROL.subject_id),
        field_name=f"candidate_2020_06_equivalence.subject_payloads.{POSITIVE_CONTROL.subject_id}",
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
            "Both `2020-06` and `2023-05` keep the same execution-effect class on every envelope row. The new "
            "candidate's extra negative-like structure therefore still lives before execution, mainly as locked-"
            "position size/policy asymmetry rather than action or trade-path divergence."
        )
    elif candidate_execution_divergence_rows == 0:
        status = action_base.PACKET_STATUS_CANDIDATE_ABSORBED
        inference = (
            "`2020-06` stays absorbed before execution surface even though the control shows execution-surface "
            "divergence. The new candidate's retained asymmetry remains pre-execution rather than economic."
        )
    else:
        status = action_base.PACKET_STATUS_CANDIDATE_DIVERGES
        inference = (
            "`2020-06` reaches execution-surface divergence inside the bounded envelope, so the retained local "
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
            "If this chain continues, the next honest slice is a candidate-only local replay around the rows where "
            "locked-position size asymmetry persists, to test whether `2020-06` also collapses into a dormant "
            "post-reentry breadcrumb or carries a different non-economic state path."
        ),
    }


def _build_fail_closed_result(reason: str) -> dict[str, Any]:
    return {
        "audit_version": (
            "ri-policy-router-continuation-release-hysteresis-local-action-position-equivalence-candidate-2020-06-2026-05-26"
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


def run_candidate_2020_06_local_action_position_equivalence() -> dict[str, Any]:
    envelope_specs = envelope_2020_06._load_local_packet_specs()
    base_cfg, carrier_cfg, authority = action_base.local_packet._load_base_and_carrier_cfg()
    subject_payloads = {
        definition.subject_id: action_base._subject_payload(
            envelope_specs[definition.subject_id],
            base_cfg=base_cfg,
            carrier_cfg=carrier_cfg,
            authority=authority,
        )
        for definition in SUBJECT_DEFINITIONS
    }

    return {
        "audit_version": (
            "ri-policy-router-continuation-release-hysteresis-local-action-position-equivalence-candidate-2020-06-2026-05-26"
        ),
        "base_sha": action_base.local_packet._git_head_sha(),
        "status": STATUS_OK,
        "observational_only": True,
        "non_authoritative": True,
        "classification_boundary": {
            "reference_surface": (
                "exact local envelopes imported from the landed `2020-06` local packet, rerun on the same carrier "
                "and compared only on action, size, and pre-execution position equivalence"
            ),
            "question": (
                "Inside the exact `2020-06` and `2023-05` local envelopes, do the retained baseline-vs-release_zero "
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
        result = run_candidate_2020_06_local_action_position_equivalence()
    except action_base.LocalActionPositionEquivalenceError as exc:
        result = _build_fail_closed_result(str(exc))
    except Candidate202006ActionPositionEquivalenceError as exc:
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
