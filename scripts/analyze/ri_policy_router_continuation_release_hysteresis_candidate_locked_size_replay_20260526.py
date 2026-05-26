# ruff: noqa: E402

from __future__ import annotations

import json
import math
import sys
from datetime import UTC, datetime
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
    ri_policy_router_continuation_release_hysteresis_local_packet_20260526 as local_packet,
)

ACTION_POSITION_EQUIVALENCE_RELATIVE = Path(
    "results/evaluation/ri_policy_router_continuation_release_hysteresis_local_action_position_equivalence_2026-05-26.json"
)
OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = (
    "ri_policy_router_continuation_release_hysteresis_candidate_locked_size_replay_2026-05-26.json"
)
STATUS_OK = "continuation_release_hysteresis_candidate_locked_size_replay_generated"
STATUS_FAIL_CLOSED = "continuation_release_hysteresis_candidate_locked_size_replay_fail_closed"
PACKET_STATUS_GAP_EXPIRES = "candidate_locked_size_gap_expires_before_next_shared_entry"
PACKET_STATUS_GAP_PERSISTS = "candidate_locked_size_gap_survives_unlock_boundary"
PACKET_STATUS_REACHES_EXECUTION = "candidate_locked_size_gap_reaches_execution_surface"
FLOAT_TOLERANCE = 1e-9


class CandidateLockedSizeReplayError(RuntimeError):
    pass


def _round_or_none(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 6)


def _float_close(
    left: float | None, right: float | None, *, tolerance: float = FLOAT_TOLERANCE
) -> bool:
    if left is None and right is None:
        return True
    if left is None or right is None:
        return False
    scale = max(1.0, abs(left), abs(right))
    return abs(left - right) <= tolerance * scale


def _parse_timestamp(raw: str) -> datetime:
    normalized = raw.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _coerce_position(payload: Any, *, field_name: str) -> dict[str, Any]:
    row = local_packet._coerce_dict(payload, field_name=field_name)
    return {
        "has_position": local_packet._coerce_bool(
            row.get("has_position"), field_name=f"{field_name}.has_position"
        ),
        "side": local_packet._coerce_optional_str(row.get("side")),
        "current_size": local_packet._coerce_optional_float(row.get("current_size")),
        "entry_time": local_packet._coerce_optional_str(row.get("entry_time")),
    }


def _coerce_effect(payload: Any, *, field_name: str) -> dict[str, Any]:
    row = local_packet._coerce_dict(payload, field_name=field_name)
    return {
        "effect": local_packet._coerce_str(row.get("effect"), field_name=f"{field_name}.effect"),
        "side": local_packet._coerce_optional_str(row.get("side")),
        "effective_size": local_packet._coerce_optional_float(row.get("effective_size")),
    }


def _coerce_surface_row(payload: Any, *, field_name: str) -> dict[str, Any]:
    row = local_packet._coerce_dict(payload, field_name=field_name)
    return {
        "action": local_packet._coerce_str(row.get("action"), field_name=f"{field_name}.action"),
        "size": local_packet._coerce_optional_float(row.get("size")),
        "selected_policy": local_packet._coerce_optional_str(row.get("selected_policy")),
        "switch_reason": local_packet._coerce_optional_str(row.get("switch_reason")),
        "switch_control_mode": local_packet._coerce_optional_str(row.get("switch_control_mode")),
        "bars_since_regime_change": local_packet._coerce_optional_float(
            row.get("bars_since_regime_change")
        ),
        "zone": local_packet._coerce_optional_str(row.get("zone")),
        "action_edge": local_packet._coerce_optional_float(row.get("action_edge")),
        "confidence_gate": local_packet._coerce_optional_float(row.get("confidence_gate")),
        "clarity_score": local_packet._coerce_optional_float(row.get("clarity_score")),
        "position_before": _coerce_position(
            row.get("position_before"), field_name=f"{field_name}.position_before"
        ),
        "trade_event_count_before": int(
            local_packet._coerce_optional_float(row.get("trade_event_count_before")) or 0
        ),
        "execution_effect": _coerce_effect(
            row.get("execution_effect"), field_name=f"{field_name}.execution_effect"
        ),
    }


def _coerce_episode_row(payload: Any, *, field_name: str) -> dict[str, Any]:
    row = local_packet._coerce_dict(payload, field_name=field_name)
    return {
        "timestamp": local_packet._coerce_str(
            row.get("timestamp"), field_name=f"{field_name}.timestamp"
        ),
        "classification": local_packet._coerce_str(
            row.get("classification"), field_name=f"{field_name}.classification"
        ),
        "row_changed": local_packet._coerce_bool(
            row.get("row_changed"), field_name=f"{field_name}.row_changed"
        ),
        "action_changed": local_packet._coerce_bool(
            row.get("action_changed"), field_name=f"{field_name}.action_changed"
        ),
        "size_changed": local_packet._coerce_bool(
            row.get("size_changed"), field_name=f"{field_name}.size_changed"
        ),
        "selected_policy_changed": local_packet._coerce_bool(
            row.get("selected_policy_changed"),
            field_name=f"{field_name}.selected_policy_changed",
        ),
        "switch_reason_changed": local_packet._coerce_bool(
            row.get("switch_reason_changed"),
            field_name=f"{field_name}.switch_reason_changed",
        ),
        "position_before_equivalent": local_packet._coerce_bool(
            row.get("position_before_equivalent"),
            field_name=f"{field_name}.position_before_equivalent",
        ),
        "execution_effect_equivalent": local_packet._coerce_bool(
            row.get("execution_effect_equivalent"),
            field_name=f"{field_name}.execution_effect_equivalent",
        ),
        "baseline": _coerce_surface_row(row.get("baseline"), field_name=f"{field_name}.baseline"),
        "release_zero": _coerce_surface_row(
            row.get("release_zero"), field_name=f"{field_name}.release_zero"
        ),
    }


def _load_candidate_payload() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    payload = local_packet._coerce_dict(
        json.loads((ROOT_DIR / ACTION_POSITION_EQUIVALENCE_RELATIVE).read_text(encoding="utf-8")),
        field_name="candidate_locked_size_replay.payload",
    )
    subject_payloads = local_packet._coerce_dict(
        payload.get("subject_payloads"), field_name="candidate_locked_size_replay.subject_payloads"
    )
    candidate = local_packet._coerce_dict(
        subject_payloads.get("2021-04"),
        field_name="candidate_locked_size_replay.subject_payloads.2021-04",
    )
    row_analyses = [
        _coerce_episode_row(raw_row, field_name=f"candidate_locked_size_replay.row[{index}]")
        for index, raw_row in enumerate(
            local_packet._coerce_list(
                candidate.get("envelope_row_analysis"),
                field_name="candidate_locked_size_replay.envelope_row_analysis",
            )
        )
    ]
    return candidate, row_analyses


def _locked_position_key(row: dict[str, Any]) -> tuple[str, str, float]:
    baseline_position = local_packet._coerce_dict(
        row.get("baseline"), field_name="locked_position_key.baseline"
    )["position_before"]
    release_position = local_packet._coerce_dict(
        row.get("release_zero"), field_name="locked_position_key.release_zero"
    )["position_before"]

    if not bool(baseline_position.get("has_position")) or not bool(
        release_position.get("has_position")
    ):
        raise CandidateLockedSizeReplayError(
            f"Locked-size row is not actually locked at {row['timestamp']}"
        )
    entry_time = local_packet._coerce_optional_str(baseline_position.get("entry_time"))
    if entry_time != local_packet._coerce_optional_str(release_position.get("entry_time")):
        raise CandidateLockedSizeReplayError(
            f"Entry-time drift on locked-size row {row['timestamp']}: {baseline_position} vs {release_position}"
        )
    side = local_packet._coerce_optional_str(baseline_position.get("side"))
    if side != local_packet._coerce_optional_str(release_position.get("side")):
        raise CandidateLockedSizeReplayError(
            f"Position-side drift on locked-size row {row['timestamp']}: {baseline_position} vs {release_position}"
        )
    current_size = local_packet._coerce_optional_float(baseline_position.get("current_size"))
    release_size = local_packet._coerce_optional_float(release_position.get("current_size"))
    if not _float_close(current_size, release_size):
        raise CandidateLockedSizeReplayError(
            f"Locked-size current-size drift on row {row['timestamp']}: {current_size} vs {release_size}"
        )
    if entry_time is None or side is None or current_size is None:
        raise CandidateLockedSizeReplayError(
            f"Locked-size row missing key position metadata at {row['timestamp']}"
        )
    return (entry_time, side, float(current_size))


def _find_unlock_index(rows: list[dict[str, Any]], *, start_index: int) -> int:
    for index in range(start_index, len(rows)):
        baseline_position = rows[index]["baseline"]["position_before"]
        release_position = rows[index]["release_zero"]["position_before"]
        if (not bool(baseline_position.get("has_position"))) and (
            not bool(release_position.get("has_position"))
        ):
            return index
    raise CandidateLockedSizeReplayError(
        f"Could not recover unlock boundary after trigger row {rows[start_index]['timestamp']}"
    )


def _find_first_shared_open_after_unlock(
    rows: list[dict[str, Any]], *, unlock_index: int
) -> int | None:
    for index in range(unlock_index + 1, len(rows)):
        baseline_effect = rows[index]["baseline"]["execution_effect"]
        release_effect = rows[index]["release_zero"]["execution_effect"]
        if (
            str(baseline_effect.get("effect")) == "open_position"
            and str(release_effect.get("effect")) == "open_position"
        ):
            return index
    return None


def _serialize_trace_row(row: dict[str, Any]) -> dict[str, Any]:
    baseline = row["baseline"]
    release_zero = row["release_zero"]
    return {
        "timestamp": str(row["timestamp"]),
        "classification": str(row["classification"]),
        "baseline_action": str(baseline["action"]),
        "release_zero_action": str(release_zero["action"]),
        "baseline_size": _round_or_none(baseline.get("size")),
        "release_zero_size": _round_or_none(release_zero.get("size")),
        "requested_size_gap": _round_or_none(
            (release_zero.get("size") or 0.0) - (baseline.get("size") or 0.0)
            if (baseline.get("size") is not None or release_zero.get("size") is not None)
            else None
        ),
        "baseline_selected_policy": baseline.get("selected_policy"),
        "release_zero_selected_policy": release_zero.get("selected_policy"),
        "baseline_switch_reason": baseline.get("switch_reason"),
        "release_zero_switch_reason": release_zero.get("switch_reason"),
        "baseline_position_has_position": bool(baseline["position_before"].get("has_position")),
        "release_zero_position_has_position": bool(
            release_zero["position_before"].get("has_position")
        ),
        "baseline_effect": baseline["execution_effect"].get("effect"),
        "release_zero_effect": release_zero["execution_effect"].get("effect"),
    }


def _serialize_trigger_row(row: dict[str, Any]) -> dict[str, Any]:
    baseline = row["baseline"]
    release_zero = row["release_zero"]
    current_size = baseline["position_before"].get("current_size")
    baseline_size = baseline.get("size")
    release_zero_size = release_zero.get("size")
    return {
        "timestamp": str(row["timestamp"]),
        "locked_position_entry_time": baseline["position_before"].get("entry_time"),
        "locked_position_side": baseline["position_before"].get("side"),
        "locked_current_size": _round_or_none(current_size),
        "baseline_proposed_size": _round_or_none(baseline_size),
        "release_zero_proposed_size": _round_or_none(release_zero_size),
        "requested_size_gap": _round_or_none(
            None
            if baseline_size is None or release_zero_size is None
            else release_zero_size - baseline_size
        ),
        "baseline_requested_minus_locked": _round_or_none(
            None if baseline_size is None or current_size is None else baseline_size - current_size
        ),
        "release_zero_requested_minus_locked": _round_or_none(
            None
            if release_zero_size is None or current_size is None
            else release_zero_size - current_size
        ),
        "baseline_selected_policy": baseline.get("selected_policy"),
        "release_zero_selected_policy": release_zero.get("selected_policy"),
        "baseline_switch_reason": baseline.get("switch_reason"),
        "release_zero_switch_reason": release_zero.get("switch_reason"),
        "execution_effect": baseline["execution_effect"].get("effect"),
    }


def _build_episode_payload(
    rows: list[dict[str, Any]], *, trigger_indices: list[int]
) -> dict[str, Any]:
    first_trigger_index = trigger_indices[0]
    first_trigger_row = rows[first_trigger_index]
    entry_time, side, current_size = _locked_position_key(first_trigger_row)
    unlock_index = _find_unlock_index(rows, start_index=first_trigger_index)
    first_shared_open_index = _find_first_shared_open_after_unlock(rows, unlock_index=unlock_index)

    episode_rows_until_unlock = rows[first_trigger_index : unlock_index + 1]
    episode_trace_end_index = (
        first_shared_open_index if first_shared_open_index is not None else unlock_index
    )
    episode_trace = rows[first_trigger_index : episode_trace_end_index + 1]
    trigger_rows = [rows[index] for index in trigger_indices]

    max_requested_size_gap = max(
        float(trigger_row["release_zero"]["size"] or 0.0)
        - float(trigger_row["baseline"]["size"] or 0.0)
        for trigger_row in trigger_rows
    )
    unlock_row = rows[unlock_index]
    first_shared_open = (
        rows[first_shared_open_index] if first_shared_open_index is not None else None
    )
    first_trigger_timestamp = str(first_trigger_row["timestamp"])
    unlock_timestamp = str(unlock_row["timestamp"])

    first_shared_entry_size_gap = None
    first_shared_entry_policy_match = None
    if first_shared_open is not None:
        first_shared_entry_size_gap = float(
            first_shared_open["release_zero"]["size"] or 0.0
        ) - float(first_shared_open["baseline"]["size"] or 0.0)
        first_shared_entry_policy_match = local_packet._coerce_optional_str(
            first_shared_open["baseline"].get("selected_policy")
        ) == local_packet._coerce_optional_str(
            first_shared_open["release_zero"].get("selected_policy")
        )

    return {
        "locked_position_key": {
            "entry_time": entry_time,
            "side": side,
            "current_size": _round_or_none(current_size),
        },
        "trigger_row_count": len(trigger_rows),
        "trigger_timestamps": [str(trigger_row["timestamp"]) for trigger_row in trigger_rows],
        "trigger_duration_hours": _round_or_none(
            (
                _parse_timestamp(str(trigger_rows[-1]["timestamp"]))
                - _parse_timestamp(str(trigger_rows[0]["timestamp"]))
            ).total_seconds()
            / 3600.0
        ),
        "max_requested_size_gap": _round_or_none(max_requested_size_gap),
        "max_requested_size_gap_pct_of_locked_size": _round_or_none(
            0.0
            if math.isclose(current_size, 0.0, abs_tol=FLOAT_TOLERANCE)
            else max_requested_size_gap / current_size
        ),
        "rows_until_unlock": len(episode_rows_until_unlock),
        "hours_until_unlock": _round_or_none(
            (
                _parse_timestamp(unlock_timestamp) - _parse_timestamp(first_trigger_timestamp)
            ).total_seconds()
            / 3600.0
        ),
        "router_internal_only_rows_while_locked": len(
            [
                row
                for row in episode_rows_until_unlock
                if str(row["classification"]) == "router_internal_only"
                and bool(row["baseline"]["position_before"].get("has_position"))
            ]
        ),
        "execution_divergence_rows_before_unlock": len(
            [
                row
                for row in episode_rows_until_unlock
                if str(row["classification"])
                in {
                    "flat_entry_divergence",
                    "reverse_candidate_divergence",
                    "position_context_divergence",
                    "execution_divergence_other",
                }
            ]
        ),
        "unlock_boundary": {
            "timestamp": unlock_timestamp,
            "classification": str(unlock_row["classification"]),
            "selected_policy_still_diff": bool(unlock_row["selected_policy_changed"]),
            "switch_reason_still_diff": bool(unlock_row["switch_reason_changed"]),
            "baseline_effect": unlock_row["baseline"]["execution_effect"].get("effect"),
            "release_zero_effect": unlock_row["release_zero"]["execution_effect"].get("effect"),
        },
        "first_shared_open_after_unlock": (
            {
                "timestamp": str(first_shared_open["timestamp"]),
                "baseline_effect": first_shared_open["baseline"]["execution_effect"].get("effect"),
                "release_zero_effect": first_shared_open["release_zero"]["execution_effect"].get(
                    "effect"
                ),
                "baseline_size": _round_or_none(first_shared_open["baseline"].get("size")),
                "release_zero_size": _round_or_none(first_shared_open["release_zero"].get("size")),
                "requested_size_gap": _round_or_none(first_shared_entry_size_gap),
                "selected_policy_match": first_shared_entry_policy_match,
                "hours_after_unlock": _round_or_none(
                    (
                        _parse_timestamp(str(first_shared_open["timestamp"]))
                        - _parse_timestamp(unlock_timestamp)
                    ).total_seconds()
                    / 3600.0
                ),
            }
            if first_shared_open is not None
            else None
        ),
        "gap_resolved_before_next_shared_entry": (
            first_shared_open is not None
            and _float_close(first_shared_entry_size_gap, 0.0)
            and bool(first_shared_entry_policy_match)
        ),
        "trigger_rows": [_serialize_trigger_row(row) for row in trigger_rows],
        "episode_trace": [_serialize_trace_row(row) for row in episode_trace],
    }


def _packet_summary(episodes: list[dict[str, Any]]) -> dict[str, Any]:
    total_trigger_rows = sum(int(episode["trigger_row_count"]) for episode in episodes)
    max_requested_size_gap = max(
        local_packet._coerce_float(
            episode.get("max_requested_size_gap"),
            field_name="locked_size_replay.max_requested_size_gap",
        )
        for episode in episodes
    )
    any_execution_divergence = any(
        int(
            local_packet._coerce_float(
                episode.get("execution_divergence_rows_before_unlock"),
                field_name="locked_size_replay.execution_divergence_rows_before_unlock",
            )
        )
        > 0
        for episode in episodes
    )
    all_resolve_before_reentry = all(
        bool(episode["gap_resolved_before_next_shared_entry"]) for episode in episodes
    )

    if any_execution_divergence:
        status = PACKET_STATUS_REACHES_EXECUTION
        inference = (
            "At least one candidate locked-size episode reaches execution divergence before unlock, so the dormant "
            "size gap is not fully absorbed by the shared open-position context."
        )
    elif all_resolve_before_reentry:
        status = PACKET_STATUS_GAP_EXPIRES
        inference = (
            "The candidate's locked-size gap stays dormant while the same `LONG` remains open, survives into the "
            "shared flat unlock boundary as policy-only drift, and then disappears before the next shared `LONG` "
            "entry. The negative-like signal therefore expires at the unlock/re-entry boundary rather than turning "
            "into execution divergence."
        )
    else:
        status = PACKET_STATUS_GAP_PERSISTS
        inference = (
            "The candidate's locked-size gap does not reach execution divergence before unlock, but it also does not "
            "fully reharmonize by the next shared entry, so a dormant post-unlock carry remains possible."
        )

    return {
        "status": status,
        "subject_id": "2021-04",
        "locked_size_episode_count": len(episodes),
        "total_trigger_row_count": total_trigger_rows,
        "max_requested_size_gap": _round_or_none(max_requested_size_gap),
        "inference": inference,
        "next_hypothesis": (
            "If this chain continues, the next honest slice is a candidate-only dormant-state replay on the same "
            "episode to test whether any non-economic router/debug field remains informative after the locked-size gap "
            "has already expired at re-entry."
        ),
    }


def _build_fail_closed_result(reason: str) -> dict[str, Any]:
    return {
        "audit_version": "ri-policy-router-continuation-release-hysteresis-candidate-locked-size-replay-2026-05-26",
        "base_sha": local_packet._git_head_sha(),
        "status": STATUS_FAIL_CLOSED,
        "observational_only": True,
        "non_authoritative": True,
        "failure_reason": reason,
        "inputs": {
            "action_position_equivalence_artifact": str(ACTION_POSITION_EQUIVALENCE_RELATIVE),
            "working_contract_reference": str(local_packet.WORKING_CONTRACT_REFERENCE),
            "subject_id": "2021-04",
            "focus_surface": "candidate-only locked-position size-gap lifecycle until unlock and next shared entry",
        },
    }


def run_candidate_locked_size_replay() -> dict[str, Any]:
    candidate_payload, row_analyses = _load_candidate_payload()
    row_summary = local_packet._coerce_dict(
        candidate_payload.get("row_summary"), field_name="candidate_locked_size_replay.row_summary"
    )
    expected_trigger_rows = int(
        local_packet._coerce_float(
            row_summary.get("size_diff_absorbed_by_locked_position_rows"),
            field_name="candidate_locked_size_replay.expected_trigger_rows",
        )
    )
    trigger_indices = [
        index
        for index, row in enumerate(row_analyses)
        if str(row["classification"]) == "size_diff_absorbed_by_locked_position"
    ]
    if not trigger_indices:
        raise CandidateLockedSizeReplayError(
            "Candidate action-position artifact no longer contains locked-size trigger rows"
        )
    if len(trigger_indices) != expected_trigger_rows:
        raise CandidateLockedSizeReplayError(
            f"Locked-size trigger count drifted: expected={expected_trigger_rows}, actual={len(trigger_indices)}"
        )

    grouped_trigger_indices: dict[tuple[str, str, float], list[int]] = {}
    for trigger_index in trigger_indices:
        key = _locked_position_key(row_analyses[trigger_index])
        grouped_trigger_indices.setdefault(key, []).append(trigger_index)

    episodes = [
        _build_episode_payload(row_analyses, trigger_indices=indices)
        for _key, indices in sorted(grouped_trigger_indices.items(), key=lambda item: item[1][0])
    ]

    return {
        "audit_version": "ri-policy-router-continuation-release-hysteresis-candidate-locked-size-replay-2026-05-26",
        "base_sha": local_packet._git_head_sha(),
        "status": STATUS_OK,
        "observational_only": True,
        "non_authoritative": True,
        "classification_boundary": {
            "reference_surface": (
                "candidate-only post-processing of the landed action-position-equivalence artifact, limited to the "
                "rows where size differences were absorbed by the same locked position"
            ),
            "question": (
                "For the `2021-04` candidate, does the dormant locked-size gap persist into the next shared entry, or "
                "does it expire while both runs stay trapped in the same open-position context?"
            ),
            "outcome_metrics_observational_only": True,
        },
        "inputs": {
            "action_position_equivalence_artifact": str(ACTION_POSITION_EQUIVALENCE_RELATIVE),
            "working_contract_reference": str(local_packet.WORKING_CONTRACT_REFERENCE),
            "subject_id": "2021-04",
            "focus_surface": "candidate-only locked-position size-gap lifecycle until unlock and next shared entry",
        },
        "subject_payload": {
            "subject_id": "2021-04",
            "month_window": candidate_payload.get("month_window"),
            "envelope_window": candidate_payload.get("envelope_window"),
            "episode_count": len(episodes),
            "episodes": episodes,
        },
        "packet_summary": _packet_summary(episodes),
    }


def main() -> int:
    output_root = ROOT_DIR / OUTPUT_ROOT_RELATIVE
    output_json = output_root / OUTPUT_FILENAME
    try:
        result = run_candidate_locked_size_replay()
    except CandidateLockedSizeReplayError as exc:
        result = _build_fail_closed_result(str(exc))

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = {
        "summary_artifact": str(output_json),
        "status": result.get("packet_summary", {}).get("status", result.get("status")),
        "subject_id": result.get("packet_summary", {}).get("subject_id"),
        "locked_size_episode_count": result.get("packet_summary", {}).get(
            "locked_size_episode_count"
        ),
        "total_trigger_row_count": result.get("packet_summary", {}).get("total_trigger_row_count"),
        "max_requested_size_gap": result.get("packet_summary", {}).get("max_requested_size_gap"),
        "failure_reason": result.get("failure_reason"),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
