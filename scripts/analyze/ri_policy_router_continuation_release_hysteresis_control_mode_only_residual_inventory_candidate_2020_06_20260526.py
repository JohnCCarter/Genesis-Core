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
    ri_policy_router_continuation_release_hysteresis_candidate_dormant_field_decay_20260526 as field_decay,
)
from scripts.analyze import (
    ri_policy_router_continuation_release_hysteresis_candidate_locked_size_replay_20260526 as candidate_replay,
)
from scripts.analyze import (
    ri_policy_router_continuation_release_hysteresis_local_action_position_equivalence_candidate_2020_06_20260526 as action_2020_06,
)
from scripts.analyze import (
    ri_policy_router_continuation_release_hysteresis_local_packet_20260526 as local_packet,
)

SUBJECT_IDS = (
    action_2020_06.NEGATIVE_CANDIDATE.subject_id,
    action_2020_06.POSITIVE_CONTROL.subject_id,
)
ACTION_POSITION_EQUIVALENCE_RELATIVE = Path(
    "results/evaluation/ri_policy_router_continuation_release_hysteresis_local_action_position_equivalence_candidate_2020_06_2026-05-26.json"
)
OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = "ri_policy_router_continuation_release_hysteresis_control_mode_only_residual_inventory_candidate_2020_06_2026-05-26.json"
STATUS_OK = "continuation_release_hysteresis_control_mode_only_residual_inventory_candidate_2020_06_generated"
STATUS_FAIL_CLOSED = "continuation_release_hysteresis_control_mode_only_residual_inventory_candidate_2020_06_fail_closed"
PACKET_STATUS_CANDIDATE_ONLY = (
    "candidate_only_control_mode_residual_rows_persist_after_locked_size_gap_candidate_2020_06"
)
PACKET_STATUS_SHARED = "control_mode_residual_rows_shared_across_candidate_and_control"
PACKET_STATUS_ABSENT = "no_control_mode_only_residual_rows_found"


class Candidate202006ControlModeResidualInventoryError(RuntimeError):
    pass


def _round_or_none(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 6)


def _load_action_position_subjects() -> dict[str, dict[str, Any]]:
    payload = local_packet._coerce_dict(
        json.loads((ROOT_DIR / ACTION_POSITION_EQUIVALENCE_RELATIVE).read_text(encoding="utf-8")),
        field_name="candidate_2020_06_control_mode_only_inventory.action_position.payload",
    )
    subject_payloads = local_packet._coerce_dict(
        payload.get("subject_payloads"),
        field_name="candidate_2020_06_control_mode_only_inventory.action_position.subject_payloads",
    )
    subjects: dict[str, dict[str, Any]] = {}
    for subject_id in SUBJECT_IDS:
        subject_payload = local_packet._coerce_dict(
            subject_payloads.get(subject_id),
            field_name=(
                f"candidate_2020_06_control_mode_only_inventory.action_position.subject_payloads.{subject_id}"
            ),
        )
        row_analyses = [
            candidate_replay._coerce_episode_row(
                raw_row,
                field_name=(
                    f"candidate_2020_06_control_mode_only_inventory.action_position.subject_payloads.{subject_id}.row[{index}]"
                ),
            )
            for index, raw_row in enumerate(
                local_packet._coerce_list(
                    subject_payload.get("envelope_row_analysis"),
                    field_name=(
                        f"candidate_2020_06_control_mode_only_inventory.action_position.subject_payloads.{subject_id}.envelope_row_analysis"
                    ),
                )
            )
        ]
        subjects[subject_id] = {
            "month_window": subject_payload.get("month_window"),
            "envelope_window": subject_payload.get("envelope_window"),
            "row_analyses": row_analyses,
        }
    return subjects


def _load_candidate_last_locked_size_timestamp(subject_payload: dict[str, Any]) -> str:
    locked_rows = [
        row
        for row in subject_payload["row_analyses"]
        if str(row["classification"]) == "size_diff_absorbed_by_locked_position"
    ]
    if not locked_rows:
        raise Candidate202006ControlModeResidualInventoryError(
            "Candidate 2020-06 action-position artifact no longer contains locked-size rows"
        )
    return str(locked_rows[-1]["timestamp"])


def _diff_fields(row: dict[str, Any]) -> list[str]:
    diff_fields: list[str] = []
    for field_name in field_decay.FIELD_SEQUENCE:
        baseline_value = field_decay._field_value(row["baseline"], field_name)
        release_zero_value = field_decay._field_value(row["release_zero"], field_name)
        if not field_decay._values_equal(baseline_value, release_zero_value):
            diff_fields.append(field_name)
    return diff_fields


def _serialize_row(
    row: dict[str, Any], *, candidate_last_locked_size_timestamp: str | None
) -> dict[str, Any]:
    baseline = row["baseline"]
    release_zero = row["release_zero"]
    timestamp = str(row["timestamp"])
    at_or_after_last_locked_size = False
    if candidate_last_locked_size_timestamp is not None:
        at_or_after_last_locked_size = candidate_replay._parse_timestamp(
            timestamp
        ) > candidate_replay._parse_timestamp(candidate_last_locked_size_timestamp)

    return {
        "timestamp": timestamp,
        "classification": str(row["classification"]),
        "at_or_after_candidate_last_locked_size_row": at_or_after_last_locked_size,
        "baseline_action": str(baseline["action"]),
        "release_zero_action": str(release_zero["action"]),
        "baseline_execution_effect": baseline["execution_effect"].get("effect"),
        "release_zero_execution_effect": release_zero["execution_effect"].get("effect"),
        "baseline_switch_control_mode": baseline.get("switch_control_mode"),
        "release_zero_switch_control_mode": release_zero.get("switch_control_mode"),
        "baseline_selected_policy": baseline.get("selected_policy"),
        "release_zero_selected_policy": release_zero.get("selected_policy"),
        "baseline_switch_reason": baseline.get("switch_reason"),
        "release_zero_switch_reason": release_zero.get("switch_reason"),
        "baseline_size": _round_or_none(baseline.get("size")),
        "release_zero_size": _round_or_none(release_zero.get("size")),
        "baseline_position_has_position": bool(baseline["position_before"].get("has_position")),
        "release_zero_position_has_position": bool(
            release_zero["position_before"].get("has_position")
        ),
    }


def _build_subject_payload(
    subject_id: str,
    subject_payload: dict[str, Any],
    *,
    candidate_last_locked_size_timestamp: str,
) -> dict[str, Any]:
    rows = list(subject_payload["row_analyses"])
    control_mode_only_rows = [row for row in rows if _diff_fields(row) == ["switch_control_mode"]]
    serialized_rows = [
        _serialize_row(
            row,
            candidate_last_locked_size_timestamp=(
                candidate_last_locked_size_timestamp
                if subject_id == action_2020_06.NEGATIVE_CANDIDATE.subject_id
                else None
            ),
        )
        for row in control_mode_only_rows
    ]
    return {
        "subject_id": subject_id,
        "month_window": subject_payload.get("month_window"),
        "envelope_window": subject_payload.get("envelope_window"),
        "control_mode_only_row_count": len(serialized_rows),
        "all_rows_after_candidate_last_locked_size_row": (
            all(bool(row["at_or_after_candidate_last_locked_size_row"]) for row in serialized_rows)
            if subject_id == action_2020_06.NEGATIVE_CANDIDATE.subject_id and serialized_rows
            else None
        ),
        "classification_counts": {
            classification: len(
                [row for row in serialized_rows if row["classification"] == classification]
            )
            for classification in sorted({row["classification"] for row in serialized_rows})
        },
        "rows": serialized_rows,
    }


def _build_packet_summary(subject_payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    candidate_payload = subject_payloads[action_2020_06.NEGATIVE_CANDIDATE.subject_id]
    control_payload = subject_payloads[action_2020_06.POSITIVE_CONTROL.subject_id]
    candidate_count = int(candidate_payload["control_mode_only_row_count"])
    control_count = int(control_payload["control_mode_only_row_count"])
    candidate_timestamps = [row["timestamp"] for row in candidate_payload["rows"]]

    if candidate_count == 0 and control_count == 0:
        status = PACKET_STATUS_ABSENT
        inference = (
            "Neither the 2020-06 candidate nor the 2023-05 control retains any rows where `switch_control_mode` is "
            "the only surviving diff field, so the breadcrumb disappears before a dedicated inventory is needed."
        )
    elif candidate_count > 0 and control_count == 0:
        status = PACKET_STATUS_CANDIDATE_ONLY
        inference = (
            "Only the `2020-06` candidate retains rows where `switch_control_mode` is the sole remaining diff field. "
            "Those rows appear after the last locked-size row while action, selected policy, switch reason, size, "
            "position context, and execution effect already match."
        )
    else:
        status = PACKET_STATUS_SHARED
        inference = (
            "Rows where `switch_control_mode` is the sole remaining diff field appear in both the candidate and the "
            "control, so the breadcrumb is not candidate-specific inside the exact local envelopes."
        )

    return {
        "status": status,
        "candidate_control_mode_only_row_count": candidate_count,
        "control_control_mode_only_row_count": control_count,
        "candidate_first_timestamp": candidate_timestamps[0] if candidate_timestamps else None,
        "candidate_last_timestamp": candidate_timestamps[-1] if candidate_timestamps else None,
        "candidate_all_rows_after_last_locked_size_row": candidate_payload.get(
            "all_rows_after_candidate_last_locked_size_row"
        ),
        "inference": inference,
        "next_hypothesis": (
            "If this breadcrumb remains the only surviving candidate-specific residual after the locked-size gap "
            "disappears, the next honest slice is direct semantics or candidate-only state-decay around those late "
            "control-mode rows rather than another attempt to claim execution harm."
        ),
    }


def _build_fail_closed_result(reason: str) -> dict[str, Any]:
    return {
        "audit_version": (
            "ri-policy-router-continuation-release-hysteresis-control-mode-only-residual-inventory-candidate-2020-06-2026-05-26"
        ),
        "base_sha": local_packet._git_head_sha(),
        "status": STATUS_FAIL_CLOSED,
        "observational_only": True,
        "non_authoritative": True,
        "failure_reason": reason,
        "inputs": {
            "action_position_equivalence_artifact": str(ACTION_POSITION_EQUIVALENCE_RELATIVE),
            "working_contract_reference": str(local_packet.WORKING_CONTRACT_REFERENCE),
            "subjects": list(SUBJECT_IDS),
            "focus_surface": "rows where switch_control_mode is the only surviving diff field after the candidate locked-size gap disappears",
        },
    }


def run_candidate_2020_06_control_mode_only_residual_inventory() -> dict[str, Any]:
    subject_sources = _load_action_position_subjects()
    candidate_last_locked_size_timestamp = _load_candidate_last_locked_size_timestamp(
        subject_sources[action_2020_06.NEGATIVE_CANDIDATE.subject_id]
    )
    subject_payloads = {
        subject_id: _build_subject_payload(
            subject_id,
            subject_sources[subject_id],
            candidate_last_locked_size_timestamp=candidate_last_locked_size_timestamp,
        )
        for subject_id in SUBJECT_IDS
    }

    return {
        "audit_version": (
            "ri-policy-router-continuation-release-hysteresis-control-mode-only-residual-inventory-candidate-2020-06-2026-05-26"
        ),
        "base_sha": local_packet._git_head_sha(),
        "status": STATUS_OK,
        "observational_only": True,
        "non_authoritative": True,
        "classification_boundary": {
            "reference_surface": (
                "artifact-only inventory over the landed 2020-06 action-position-equivalence artifact, limited to rows "
                "where `switch_control_mode` is the sole surviving diff field"
            ),
            "question": (
                "Inside the exact local envelopes, after the last 2020-06 locked-size row, are control-mode-only "
                "residual rows unique to the candidate or also present in the fixed 2023-05 control?"
            ),
            "outcome_metrics_observational_only": True,
        },
        "inputs": {
            "action_position_equivalence_artifact": str(ACTION_POSITION_EQUIVALENCE_RELATIVE),
            "working_contract_reference": str(local_packet.WORKING_CONTRACT_REFERENCE),
            "subjects": list(SUBJECT_IDS),
            "focus_surface": "rows where switch_control_mode is the only surviving diff field after the candidate locked-size gap disappears",
        },
        "subject_payloads": subject_payloads,
        "packet_summary": _build_packet_summary(subject_payloads),
    }


def main() -> int:
    output_root = ROOT_DIR / OUTPUT_ROOT_RELATIVE
    output_json = output_root / OUTPUT_FILENAME
    try:
        result = run_candidate_2020_06_control_mode_only_residual_inventory()
    except Candidate202006ControlModeResidualInventoryError as exc:
        result = _build_fail_closed_result(str(exc))

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    packet_summary = local_packet._coerce_optional_dict(result.get("packet_summary")) or {}
    summary = {
        "summary_artifact": str(output_json),
        "status": packet_summary.get("status", result.get("status")),
        "candidate_control_mode_only_row_count": packet_summary.get(
            "candidate_control_mode_only_row_count"
        ),
        "control_control_mode_only_row_count": packet_summary.get(
            "control_control_mode_only_row_count"
        ),
        "candidate_first_timestamp": packet_summary.get("candidate_first_timestamp"),
        "candidate_last_timestamp": packet_summary.get("candidate_last_timestamp"),
        "failure_reason": result.get("failure_reason"),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
