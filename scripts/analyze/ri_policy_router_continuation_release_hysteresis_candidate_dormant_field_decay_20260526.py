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
    ri_policy_router_continuation_release_hysteresis_candidate_locked_size_replay_20260526 as candidate_replay,
)
from scripts.analyze import (
    ri_policy_router_continuation_release_hysteresis_local_packet_20260526 as local_packet,
)

LOCKED_SIZE_REPLAY_RELATIVE = Path(
    "results/evaluation/ri_policy_router_continuation_release_hysteresis_candidate_locked_size_replay_2026-05-26.json"
)
OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = (
    "ri_policy_router_continuation_release_hysteresis_candidate_dormant_field_decay_2026-05-26.json"
)
STATUS_OK = "continuation_release_hysteresis_candidate_dormant_field_decay_generated"
STATUS_FAIL_CLOSED = "continuation_release_hysteresis_candidate_dormant_field_decay_fail_closed"
PACKET_STATUS_CONTROL_MODE_ONLY = "dormant_state_decays_to_control_mode_only"
PACKET_STATUS_MULTI_FIELD = "residual_multi_field_signature_retained"
PACKET_STATUS_FULLY_CONVERGED = "dormant_state_fully_converged_by_reentry"
FIELD_SEQUENCE = (
    "selected_policy",
    "switch_reason",
    "switch_control_mode",
    "size",
    "zone",
    "bars_since_regime_change",
    "clarity_score",
    "confidence_gate",
    "action_edge",
    "action",
    "execution_effect",
)
PHASE_ORDER = {
    "locked_size_trigger": 0,
    "locked_router_internal": 1,
    "unlock_boundary": 2,
    "first_shared_open_after_unlock": 3,
    "other": 4,
}


class CandidateDormantFieldDecayError(RuntimeError):
    pass


def _round_or_none(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 6)


def _normalize_value(value: Any) -> Any:
    if isinstance(value, float):
        return _round_or_none(value)
    return value


def _values_equal(left: Any, right: Any) -> bool:
    if isinstance(left, float) or isinstance(right, float):
        if left is None or right is None:
            return left is right
        return candidate_replay._float_close(float(left), float(right))
    return left == right


def _load_locked_size_replay_episode() -> dict[str, Any]:
    payload = local_packet._coerce_dict(
        json.loads((ROOT_DIR / LOCKED_SIZE_REPLAY_RELATIVE).read_text(encoding="utf-8")),
        field_name="candidate_dormant_field_decay.locked_size_replay.payload",
    )
    subject_payload = local_packet._coerce_dict(
        payload.get("subject_payload"),
        field_name="candidate_dormant_field_decay.locked_size_replay.subject_payload",
    )
    episodes = local_packet._coerce_list(
        subject_payload.get("episodes"),
        field_name="candidate_dormant_field_decay.locked_size_replay.episodes",
    )
    if len(episodes) != 1:
        raise CandidateDormantFieldDecayError(
            f"Expected exactly one locked-size episode, found {len(episodes)}"
        )
    return local_packet._coerce_dict(
        episodes[0], field_name="candidate_dormant_field_decay.locked_size_replay.episode"
    )


def _field_value(surface_row: dict[str, Any], field_name: str) -> Any:
    if field_name == "execution_effect":
        return local_packet._coerce_dict(
            surface_row.get("execution_effect"),
            field_name=f"candidate_dormant_field_decay.{field_name}.execution_effect",
        ).get("effect")
    return surface_row.get(field_name)


def _phase_name(
    row: dict[str, Any],
    *,
    trigger_timestamps: set[str],
    unlock_timestamp: str,
    reentry_timestamp: str | None,
) -> str:
    timestamp = str(row["timestamp"])
    if timestamp in trigger_timestamps:
        return "locked_size_trigger"
    if timestamp == unlock_timestamp:
        return "unlock_boundary"
    if reentry_timestamp is not None and timestamp == reentry_timestamp:
        return "first_shared_open_after_unlock"
    if str(row["classification"]) == "router_internal_only" and bool(
        row["baseline"]["position_before"].get("has_position")
    ):
        return "locked_router_internal"
    return "other"


def _build_matrix_row(
    row: dict[str, Any],
    *,
    trigger_timestamps: set[str],
    unlock_timestamp: str,
    reentry_timestamp: str | None,
) -> dict[str, Any]:
    baseline = row["baseline"]
    release_zero = row["release_zero"]
    field_matrix: dict[str, dict[str, Any]] = {}
    diff_fields: list[str] = []
    matched_fields: list[str] = []

    for field_name in FIELD_SEQUENCE:
        baseline_value = _field_value(baseline, field_name)
        release_zero_value = _field_value(release_zero, field_name)
        differs = not _values_equal(baseline_value, release_zero_value)
        field_matrix[field_name] = {
            "baseline": _normalize_value(baseline_value),
            "release_zero": _normalize_value(release_zero_value),
            "differs": differs,
        }
        if differs:
            diff_fields.append(field_name)
        else:
            matched_fields.append(field_name)

    return {
        "timestamp": str(row["timestamp"]),
        "phase": _phase_name(
            row,
            trigger_timestamps=trigger_timestamps,
            unlock_timestamp=unlock_timestamp,
            reentry_timestamp=reentry_timestamp,
        ),
        "classification": str(row["classification"]),
        "row_changed": bool(row["row_changed"]),
        "baseline_position_has_position": bool(baseline["position_before"].get("has_position")),
        "release_zero_position_has_position": bool(
            release_zero["position_before"].get("has_position")
        ),
        "diff_field_count": len(diff_fields),
        "diff_fields": diff_fields,
        "matched_fields": matched_fields,
        "field_matrix": field_matrix,
    }


def _common_fields(rows: list[dict[str, Any]]) -> list[str]:
    if not rows:
        return []
    common = set(rows[0]["diff_fields"])
    for row in rows[1:]:
        common &= set(row["diff_fields"])
    return [field for field in FIELD_SEQUENCE if field in common]


def _union_fields(rows: list[dict[str, Any]]) -> list[str]:
    union: set[str] = set()
    for row in rows:
        union |= set(row["diff_fields"])
    return [field for field in FIELD_SEQUENCE if field in union]


def _build_packet_summary(matrix_rows: list[dict[str, Any]]) -> dict[str, Any]:
    trigger_rows = [row for row in matrix_rows if row["phase"] == "locked_size_trigger"]
    unlock_rows = [row for row in matrix_rows if row["phase"] == "unlock_boundary"]
    reentry_rows = [row for row in matrix_rows if row["phase"] == "first_shared_open_after_unlock"]

    if len(unlock_rows) != 1:
        raise CandidateDormantFieldDecayError(
            f"Expected exactly one unlock row in field-decay matrix, found {len(unlock_rows)}"
        )
    if len(reentry_rows) > 1:
        raise CandidateDormantFieldDecayError(
            f"Expected at most one re-entry row in field-decay matrix, found {len(reentry_rows)}"
        )

    trigger_common_fields = _common_fields(trigger_rows)
    trigger_union_fields = _union_fields(trigger_rows)
    unlock_fields = list(unlock_rows[0]["diff_fields"])
    reentry_fields = list(reentry_rows[0]["diff_fields"]) if reentry_rows else []

    if not reentry_fields:
        status = PACKET_STATUS_FULLY_CONVERGED
        inference = (
            "All candidate-only dormant field differences fully converge by the first shared open-position row, "
            "including router/debug fields."
        )
    elif reentry_fields == ["switch_control_mode"]:
        status = PACKET_STATUS_CONTROL_MODE_ONLY
        inference = (
            "The candidate's dormant field drift decays from size and policy label differences on the locked trigger "
            "rows, to policy-label-only drift at unlock, and finally to `switch_control_mode` alone at the first "
            "shared re-entry. The surviving residual is therefore a router breadcrumb rather than a decision or "
            "execution signal."
        )
    else:
        status = PACKET_STATUS_MULTI_FIELD
        inference = (
            "At least one multi-field residual signature survives into the first shared re-entry, so the candidate's "
            "dormant state has not decayed to a single router breadcrumb."
        )

    return {
        "status": status,
        "subject_id": "2021-04",
        "episode_row_count": len(matrix_rows),
        "trigger_row_count": len(trigger_rows),
        "trigger_common_diff_fields": trigger_common_fields,
        "trigger_union_diff_fields": trigger_union_fields,
        "unlock_diff_fields": unlock_fields,
        "reentry_diff_fields": reentry_fields,
        "inference": inference,
        "next_hypothesis": (
            "If this chain continues, the next honest step is not another post-unlock replay. It is a decision about "
            "whether the last `switch_control_mode` breadcrumb is useful enough to study further, or whether the "
            "candidate should be retired in favor of a new widening target."
        ),
    }


def _build_fail_closed_result(reason: str) -> dict[str, Any]:
    return {
        "audit_version": "ri-policy-router-continuation-release-hysteresis-candidate-dormant-field-decay-2026-05-26",
        "base_sha": local_packet._git_head_sha(),
        "status": STATUS_FAIL_CLOSED,
        "observational_only": True,
        "non_authoritative": True,
        "failure_reason": reason,
        "inputs": {
            "action_position_equivalence_artifact": str(
                candidate_replay.ACTION_POSITION_EQUIVALENCE_RELATIVE
            ),
            "locked_size_replay_artifact": str(LOCKED_SIZE_REPLAY_RELATIVE),
            "working_contract_reference": str(local_packet.WORKING_CONTRACT_REFERENCE),
            "subject_id": "2021-04",
            "focus_surface": "candidate-only dormant field decay inside the single locked-size episode",
        },
    }


def run_candidate_dormant_field_decay() -> dict[str, Any]:
    candidate_payload, row_analyses = candidate_replay._load_candidate_payload()
    episode = _load_locked_size_replay_episode()

    trace_rows = local_packet._coerce_list(
        episode.get("episode_trace"),
        field_name="candidate_dormant_field_decay.locked_size_replay.episode_trace",
    )
    trace_timestamps = [
        local_packet._coerce_str(
            local_packet._coerce_dict(
                trace_row,
                field_name=f"candidate_dormant_field_decay.episode_trace[{index}]",
            ).get("timestamp"),
            field_name=f"candidate_dormant_field_decay.episode_trace[{index}].timestamp",
        )
        for index, trace_row in enumerate(trace_rows)
    ]
    trigger_rows = local_packet._coerce_list(
        episode.get("trigger_rows"),
        field_name="candidate_dormant_field_decay.locked_size_replay.trigger_rows",
    )
    trigger_timestamps = {
        local_packet._coerce_str(
            local_packet._coerce_dict(
                trigger_row,
                field_name=f"candidate_dormant_field_decay.trigger_row[{index}]",
            ).get("timestamp"),
            field_name=f"candidate_dormant_field_decay.trigger_row[{index}].timestamp",
        )
        for index, trigger_row in enumerate(trigger_rows)
    }
    unlock_boundary = local_packet._coerce_dict(
        episode.get("unlock_boundary"),
        field_name="candidate_dormant_field_decay.locked_size_replay.unlock_boundary",
    )
    unlock_timestamp = local_packet._coerce_str(
        unlock_boundary.get("timestamp"),
        field_name="candidate_dormant_field_decay.locked_size_replay.unlock_boundary.timestamp",
    )
    reentry_payload = local_packet._coerce_optional_dict(
        episode.get("first_shared_open_after_unlock")
    )
    reentry_timestamp = None
    if reentry_payload is not None:
        reentry_timestamp = local_packet._coerce_str(
            reentry_payload.get("timestamp"),
            field_name="candidate_dormant_field_decay.locked_size_replay.first_shared_open_after_unlock.timestamp",
        )

    row_by_timestamp = {str(row["timestamp"]): row for row in row_analyses}
    missing_timestamps = [
        timestamp for timestamp in trace_timestamps if timestamp not in row_by_timestamp
    ]
    if missing_timestamps:
        raise CandidateDormantFieldDecayError(
            f"Candidate action-position artifact is missing trace rows for timestamps: {missing_timestamps}"
        )

    matrix_rows = [
        _build_matrix_row(
            row_by_timestamp[timestamp],
            trigger_timestamps=trigger_timestamps,
            unlock_timestamp=unlock_timestamp,
            reentry_timestamp=reentry_timestamp,
        )
        for timestamp in trace_timestamps
    ]

    phase_counts = {
        phase_name: len([row for row in matrix_rows if row["phase"] == phase_name])
        for phase_name in sorted(PHASE_ORDER, key=PHASE_ORDER.get)
        if any(row["phase"] == phase_name for row in matrix_rows)
    }

    return {
        "audit_version": "ri-policy-router-continuation-release-hysteresis-candidate-dormant-field-decay-2026-05-26",
        "base_sha": local_packet._git_head_sha(),
        "status": STATUS_OK,
        "observational_only": True,
        "non_authoritative": True,
        "classification_boundary": {
            "reference_surface": (
                "candidate-only post-processing of the landed action-position-equivalence artifact plus the locked-size "
                "replay artifact, limited to the single `2021-04` locked-size episode"
            ),
            "question": (
                "After the candidate's dormant size gap has already been shown to expire before the next shared entry, "
                "which exact non-economic fields still differ on the trigger rows, the unlock row, and the first shared "
                "re-entry row?"
            ),
            "outcome_metrics_observational_only": True,
        },
        "inputs": {
            "action_position_equivalence_artifact": str(
                candidate_replay.ACTION_POSITION_EQUIVALENCE_RELATIVE
            ),
            "locked_size_replay_artifact": str(LOCKED_SIZE_REPLAY_RELATIVE),
            "working_contract_reference": str(local_packet.WORKING_CONTRACT_REFERENCE),
            "subject_id": "2021-04",
            "focus_surface": "candidate-only dormant field decay inside the single locked-size episode",
        },
        "subject_payload": {
            "subject_id": "2021-04",
            "month_window": candidate_payload.get("month_window"),
            "envelope_window": candidate_payload.get("envelope_window"),
            "field_sequence": list(FIELD_SEQUENCE),
            "phase_counts": phase_counts,
            "field_decay_matrix": matrix_rows,
        },
        "packet_summary": _build_packet_summary(matrix_rows),
    }


def main() -> int:
    output_root = ROOT_DIR / OUTPUT_ROOT_RELATIVE
    output_json = output_root / OUTPUT_FILENAME
    try:
        result = run_candidate_dormant_field_decay()
    except CandidateDormantFieldDecayError as exc:
        result = _build_fail_closed_result(str(exc))

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    packet_summary = local_packet._coerce_optional_dict(result.get("packet_summary")) or {}
    summary = {
        "summary_artifact": str(output_json),
        "status": packet_summary.get("status", result.get("status")),
        "subject_id": packet_summary.get("subject_id"),
        "episode_row_count": packet_summary.get("episode_row_count"),
        "unlock_diff_fields": packet_summary.get("unlock_diff_fields"),
        "reentry_diff_fields": packet_summary.get("reentry_diff_fields"),
        "failure_reason": result.get("failure_reason"),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
