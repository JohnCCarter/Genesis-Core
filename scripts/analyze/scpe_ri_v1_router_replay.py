#!/usr/bin/env python3
"""Deterministic RI-only SCPE replay over frozen research evidence.

This module promotes the previously verified scratch replay into a tracked analysis
script without changing routing semantics. It remains research-only, reads only the
frozen Phase C evidence surface, and writes only the approved replay artifacts under
`results/research/scpe_v1_ri/`.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any


POLICY_CONTINUATION = "RI_continuation_policy"
POLICY_DEFENSIVE = "RI_defensive_transition_policy"
POLICY_NO_TRADE = "RI_no_trade_policy"
FINAL_ACTION_NONE = "NONE"

FIELD_ALLOWLIST_VERSION = "scpe-ri-v1-field-allowlist-2026-04-20"
ELIGIBILITY_VERSION = "scpe-ri-v1-eligibility-2026-04-20"
ROUTER_VERSION = "scpe-ri-v1-router-2026-04-20"
VETO_VERSION = "scpe-ri-v1-veto-2026-04-20"
METRICS_SEMANTICS_VERSION = "scpe-ri-v1-metric-semantics-2026-04-20b"

CORE_STATE_FIELDS = [
    "timestamp",
    "year",
    "side",
    "zone",
    "htf_regime",
    "current_atr_used",
    "atr_period_used",
]

RI_STATE_FIELDS = [
    "ri_clarity_score",
    "ri_clarity_raw",
    "bars_since_regime_change",
    "proba_edge",
    "conf_overall",
]

OBSERVATIONAL_ONLY_FIELDS = [
    "total_pnl",
    "total_commission",
    "entry_atr",
    "fwd_4_atr",
    "fwd_8_atr",
    "fwd_16_atr",
    "mfe_16_atr",
    "mae_16_atr",
    "continuation_score",
]

REQUIRED_INPUT_FIELDS = CORE_STATE_FIELDS + RI_STATE_FIELDS + OBSERVATIONAL_ONLY_FIELDS

APPROVED_OUTPUT_FILENAMES = [
    "input_manifest.json",
    "routing_trace.ndjson",
    "state_trace.json",
    "policy_trace.json",
    "veto_trace.json",
    "replay_metrics.json",
    "summary.md",
    "manifest.json",
]

ROUTER_PARAMS = {
    "switch_threshold": 2,
    "hysteresis": 1,
    "min_dwell": 3,
    "continuation": {
        "clarity_floor": 28.0,
        "clarity_strong": 30.0,
        "confidence_floor": 0.535,
        "confidence_strong": 0.545,
        "edge_floor": 0.070,
        "edge_strong": 0.100,
        "stable_bars_floor": 5.0,
        "stable_bars_strong": 8.0,
    },
    "no_trade": {
        "clarity_floor": 24.0,
        "confidence_floor": 0.515,
        "edge_floor": 0.035,
    },
}


@dataclass(frozen=True)
class SourceSpec:
    label: str
    path: Path


def _find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "pyproject.toml").exists() and (candidate / "src").exists():
            return candidate
    raise RuntimeError("Could not locate repository root")


ROOT_DIR = _find_repo_root(Path(__file__).resolve())
ENTRY_ROWS_PATH = (
    ROOT_DIR
    / "results"
    / "research"
    / "ri_advisory_environment_fit"
    / "phase3_phasec_evidence_capture_v2_2026-04-17"
    / "entry_rows.ndjson"
)
CAPTURE_SUMMARY_PATH = (
    ROOT_DIR
    / "results"
    / "research"
    / "ri_advisory_environment_fit"
    / "phase3_phasec_evidence_capture_v2_2026-04-17"
    / "capture_summary.json"
)
CAPTURE_MANIFEST_PATH = (
    ROOT_DIR
    / "results"
    / "research"
    / "ri_advisory_environment_fit"
    / "phase3_phasec_evidence_capture_v2_2026-04-17"
    / "manifest.json"
)
OUTPUT_DIR = ROOT_DIR / "results" / "research" / "scpe_v1_ri"

INPUT_SOURCES = [
    SourceSpec("entry_rows", ENTRY_ROWS_PATH),
    SourceSpec("capture_summary", CAPTURE_SUMMARY_PATH),
    SourceSpec("capture_manifest", CAPTURE_MANIFEST_PATH),
    SourceSpec("replay_script", Path(__file__).resolve()),
]


def _relative_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT_DIR.resolve()).as_posix()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_json_text(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(_canonical_json_text(payload), encoding="utf-8")


def _write_ndjson(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
            handle.write("\n")


def _ensure_output_scope(output_dir: Path, approved_files: list[Path]) -> None:
    approved_resolved = {path.resolve() for path in approved_files}
    if output_dir.exists():
        unexpected = [
            _relative_path(path)
            for path in output_dir.rglob("*")
            if path.is_file() and path.resolve() not in approved_resolved
        ]
        if unexpected:
            raise RuntimeError(
                "Output directory already contains unexpected files: " + ", ".join(unexpected)
            )


def _snapshot_paths(paths: list[Path]) -> dict[str, dict[str, int]]:
    snapshot: dict[str, dict[str, int]] = {}
    for base in paths:
        resolved = base.resolve()
        if resolved.is_file():
            stat = resolved.stat()
            snapshot[_relative_path(resolved)] = {
                "size": int(stat.st_size),
                "mtime_ns": int(stat.st_mtime_ns),
            }
            continue
        if not resolved.exists():
            continue
        for item in sorted(path for path in resolved.rglob("*") if path.is_file()):
            stat = item.stat()
            snapshot[_relative_path(item)] = {
                "size": int(stat.st_size),
                "mtime_ns": int(stat.st_mtime_ns),
            }
    return snapshot


def _diff_snapshots(
    before: dict[str, dict[str, int]], after: dict[str, dict[str, int]]
) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for rel_path in sorted(set(before) | set(after)):
        if rel_path not in before:
            events.append({"event": "create", "path": rel_path})
            continue
        if rel_path not in after:
            events.append({"event": "delete", "path": rel_path})
            continue
        if before[rel_path] != after[rel_path]:
            events.append({"event": "modify", "path": rel_path})
    return events


def _sort_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(events, key=lambda item: (item["path"], item["event"]))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_entry_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for index, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            payload = json.loads(text)
            if not isinstance(payload, dict):
                raise ValueError(f"Row {index} must be a JSON object")
            rows.append(payload)
    if not rows:
        raise RuntimeError("entry_rows.ndjson did not contain any replay rows")
    return rows


def _require_fields(row: dict[str, Any], index: int) -> None:
    missing = [field for field in REQUIRED_INPUT_FIELDS if field not in row]
    if missing:
        raise ValueError(f"Row {index} missing required fields: {missing}")


def _as_float(row: dict[str, Any], field: str, index: int) -> float:
    value = row.get(field)
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Row {index} field {field!r} must be numeric, got {value!r}") from exc
    return numeric


def _as_int(row: dict[str, Any], field: str, index: int) -> int:
    return int(_as_float(row, field, index))


def _action_edge(side: str, proba_edge: float) -> float:
    return proba_edge if side == "LONG" else -proba_edge


def _bucket_clarity(score: float) -> str:
    if score >= 30.0:
        return "high"
    if score >= 26.0:
        return "mid"
    return "low"


def _bucket_confidence(confidence: float) -> str:
    if confidence >= 0.545:
        return "high"
    if confidence >= 0.525:
        return "mid"
    return "low"


def _bucket_transition(bars_since_change: float) -> str:
    if bars_since_change <= 3.0:
        return "acute"
    if bars_since_change <= 8.0:
        return "recent"
    return "stable"


def _bucket_edge(edge_value: float) -> str:
    if edge_value >= 0.100:
        return "strong"
    if edge_value >= 0.055:
        return "mid"
    return "weak"


def _derive_core_state(row: dict[str, Any], index: int) -> dict[str, Any]:
    core_state = {
        "timestamp": str(row["timestamp"]),
        "year": _as_int(row, "year", index),
        "side": str(row["side"]),
        "zone": str(row["zone"]),
        "htf_regime": str(row["htf_regime"]),
        "current_atr_used": _as_float(row, "current_atr_used", index),
        "atr_period_used": _as_float(row, "atr_period_used", index),
    }
    if core_state["side"] not in {"LONG", "SHORT"}:
        raise ValueError(f"Row {index} has unsupported side {core_state['side']!r}")
    return core_state


def _derive_ri_state(row: dict[str, Any], core_state: dict[str, Any], index: int) -> dict[str, Any]:
    raw_edge = _as_float(row, "proba_edge", index)
    action_edge = _action_edge(core_state["side"], raw_edge)
    ri_state = {
        "ri_clarity_score": _as_float(row, "ri_clarity_score", index),
        "ri_clarity_raw": _as_float(row, "ri_clarity_raw", index),
        "bars_since_regime_change": _as_float(row, "bars_since_regime_change", index),
        "proba_edge": raw_edge,
        "action_edge": action_edge,
        "conf_overall": _as_float(row, "conf_overall", index),
    }
    ri_state["clarity_bucket"] = _bucket_clarity(ri_state["ri_clarity_score"])
    ri_state["confidence_bucket"] = _bucket_confidence(ri_state["conf_overall"])
    ri_state["transition_bucket"] = _bucket_transition(ri_state["bars_since_regime_change"])
    ri_state["edge_bucket"] = _bucket_edge(ri_state["action_edge"])
    return ri_state


def _build_raw_router_decision(
    core_state: dict[str, Any], ri_state: dict[str, Any]
) -> dict[str, Any]:
    no_trade_cfg = ROUTER_PARAMS["no_trade"]
    continuation_cfg = ROUTER_PARAMS["continuation"]

    clarity = ri_state["ri_clarity_score"]
    confidence = ri_state["conf_overall"]
    edge_value = ri_state["action_edge"]
    stable_bars = ri_state["bars_since_regime_change"]

    if (
        clarity < no_trade_cfg["clarity_floor"]
        or confidence < no_trade_cfg["confidence_floor"]
        or edge_value < no_trade_cfg["edge_floor"]
    ):
        return {
            "target_policy": POLICY_NO_TRADE,
            "raw_switch_reason": "insufficient_evidence",
            "mandate_level": 0,
            "confidence": 0,
            "no_trade_flag": True,
        }

    continuation_points = sum(
        [
            clarity >= continuation_cfg["clarity_floor"],
            clarity >= continuation_cfg["clarity_strong"],
            confidence >= continuation_cfg["confidence_floor"],
            confidence >= continuation_cfg["confidence_strong"],
            edge_value >= continuation_cfg["edge_floor"],
            edge_value >= continuation_cfg["edge_strong"],
            stable_bars >= continuation_cfg["stable_bars_floor"],
            stable_bars >= continuation_cfg["stable_bars_strong"],
        ]
    )

    transition_points = sum(
        [
            stable_bars <= 3.0,
            stable_bars <= 8.0,
            clarity < continuation_cfg["clarity_floor"],
            confidence < continuation_cfg["confidence_floor"],
            edge_value < continuation_cfg["edge_floor"],
            core_state["zone"] == "high",
        ]
    )

    if continuation_points >= 6:
        return {
            "target_policy": POLICY_CONTINUATION,
            "raw_switch_reason": "stable_continuation_state",
            "mandate_level": 3,
            "confidence": 3,
            "no_trade_flag": False,
        }
    if continuation_points >= 4 and transition_points <= 2:
        return {
            "target_policy": POLICY_CONTINUATION,
            "raw_switch_reason": "continuation_state_supported",
            "mandate_level": 2,
            "confidence": 2,
            "no_trade_flag": False,
        }
    if transition_points >= 4:
        return {
            "target_policy": POLICY_DEFENSIVE,
            "raw_switch_reason": "transition_pressure_detected",
            "mandate_level": 2,
            "confidence": 2,
            "no_trade_flag": False,
        }
    if transition_points >= 2:
        return {
            "target_policy": POLICY_DEFENSIVE,
            "raw_switch_reason": "defensive_transition_state",
            "mandate_level": 1,
            "confidence": 1,
            "no_trade_flag": False,
        }
    return {
        "target_policy": POLICY_NO_TRADE,
        "raw_switch_reason": "confidence_below_threshold",
        "mandate_level": 0,
        "confidence": 0,
        "no_trade_flag": True,
    }


def _apply_stability_control(
    raw_decision: dict[str, Any], previous_route: dict[str, Any] | None
) -> dict[str, Any]:
    route = dict(raw_decision)
    route["previous_policy"] = None if previous_route is None else previous_route["selected_policy"]
    route["switch_proposed"] = False
    route["switch_blocked"] = False

    if previous_route is None:
        route["selected_policy"] = raw_decision["target_policy"]
        route["switch_reason"] = raw_decision["raw_switch_reason"]
        route["dwell_duration"] = 1
        return route

    prev_policy = str(previous_route["selected_policy"])
    prev_dwell = int(previous_route["dwell_duration"])
    prev_mandate = int(previous_route["mandate_level"])
    target_policy = str(raw_decision["target_policy"])

    if target_policy == prev_policy:
        route["selected_policy"] = target_policy
        route["switch_reason"] = raw_decision["raw_switch_reason"]
        route["dwell_duration"] = prev_dwell + 1
        return route

    route["switch_proposed"] = True
    if target_policy == POLICY_NO_TRADE:
        route["selected_policy"] = POLICY_NO_TRADE
        route["switch_reason"] = raw_decision["raw_switch_reason"]
        route["dwell_duration"] = 1
        return route

    if prev_dwell < ROUTER_PARAMS["min_dwell"]:
        route["selected_policy"] = prev_policy
        route["switch_reason"] = "switch_blocked_by_min_dwell"
        route["switch_blocked"] = True
        route["dwell_duration"] = prev_dwell + 1
        route["mandate_level"] = prev_mandate
        route["confidence"] = int(previous_route["confidence"])
        route["no_trade_flag"] = prev_policy == POLICY_NO_TRADE
        return route

    if int(raw_decision["mandate_level"]) < int(ROUTER_PARAMS["switch_threshold"]):
        route["selected_policy"] = prev_policy
        route["switch_reason"] = "confidence_below_threshold"
        route["switch_blocked"] = True
        route["dwell_duration"] = prev_dwell + 1
        route["mandate_level"] = prev_mandate
        route["confidence"] = int(previous_route["confidence"])
        route["no_trade_flag"] = prev_policy == POLICY_NO_TRADE
        return route

    if int(raw_decision["mandate_level"]) < prev_mandate + int(ROUTER_PARAMS["hysteresis"]):
        route["selected_policy"] = prev_policy
        route["switch_reason"] = "switch_blocked_by_hysteresis"
        route["switch_blocked"] = True
        route["dwell_duration"] = prev_dwell + 1
        route["mandate_level"] = prev_mandate
        route["confidence"] = int(previous_route["confidence"])
        route["no_trade_flag"] = prev_policy == POLICY_NO_TRADE
        return route

    route["selected_policy"] = target_policy
    route["switch_reason"] = raw_decision["raw_switch_reason"]
    route["dwell_duration"] = 1
    return route


def _build_policy_decision(route: dict[str, Any], core_state: dict[str, Any]) -> dict[str, Any]:
    selected_policy = str(route["selected_policy"])
    if selected_policy == POLICY_NO_TRADE:
        return {
            "policy_action": FINAL_ACTION_NONE,
            "policy_posture": "no_trade",
            "policy_size_multiplier": 0.0,
        }
    if selected_policy == POLICY_CONTINUATION:
        return {
            "policy_action": core_state["side"],
            "policy_posture": "continuation",
            "policy_size_multiplier": 1.0,
        }
    return {
        "policy_action": core_state["side"],
        "policy_posture": "defensive",
        "policy_size_multiplier": 0.5,
    }


def _apply_veto(
    route: dict[str, Any],
    policy_decision: dict[str, Any],
    core_state: dict[str, Any],
    ri_state: dict[str, Any],
) -> dict[str, Any]:
    if route["selected_policy"] == POLICY_NO_TRADE:
        return {
            "veto_action": "force_no_trade",
            "veto_reason": "policy_no_trade",
            "final_routed_action": FINAL_ACTION_NONE,
            "final_size_multiplier": 0.0,
        }

    if ri_state["action_edge"] < 0.050 or ri_state["conf_overall"] < 0.520:
        return {
            "veto_action": "force_no_trade",
            "veto_reason": "state_below_veto_floor",
            "final_routed_action": FINAL_ACTION_NONE,
            "final_size_multiplier": 0.0,
        }

    if route["selected_policy"] == POLICY_CONTINUATION and core_state["zone"] == "high":
        return {
            "veto_action": "reduce",
            "veto_reason": "high_zone_continuation_cap",
            "final_routed_action": policy_decision["policy_action"],
            "final_size_multiplier": 0.75,
        }

    if route["selected_policy"] == POLICY_DEFENSIVE and ri_state["transition_bucket"] != "stable":
        return {
            "veto_action": "cap",
            "veto_reason": "defensive_transition_cap",
            "final_routed_action": policy_decision["policy_action"],
            "final_size_multiplier": 0.35,
        }

    return {
        "veto_action": "pass",
        "veto_reason": "no_veto",
        "final_routed_action": policy_decision["policy_action"],
        "final_size_multiplier": float(policy_decision["policy_size_multiplier"]),
    }


def _compact_core_state(core_state: dict[str, Any]) -> dict[str, Any]:
    return {
        "side": core_state["side"],
        "zone": core_state["zone"],
        "htf_regime": core_state["htf_regime"],
        "current_atr_used": round(core_state["current_atr_used"], 6),
        "atr_period_used": round(core_state["atr_period_used"], 6),
    }


def _compact_ri_state(ri_state: dict[str, Any]) -> dict[str, Any]:
    return {
        "ri_clarity_score": round(ri_state["ri_clarity_score"], 6),
        "ri_clarity_raw": round(ri_state["ri_clarity_raw"], 6),
        "bars_since_regime_change": round(ri_state["bars_since_regime_change"], 6),
        "action_edge": round(ri_state["action_edge"], 6),
        "conf_overall": round(ri_state["conf_overall"], 6),
        "clarity_bucket": ri_state["clarity_bucket"],
        "confidence_bucket": ri_state["confidence_bucket"],
        "transition_bucket": ri_state["transition_bucket"],
        "edge_bucket": ri_state["edge_bucket"],
    }


def _build_trace_row(
    row: dict[str, Any],
    core_state: dict[str, Any],
    ri_state: dict[str, Any],
    route: dict[str, Any],
    veto: dict[str, Any],
) -> dict[str, Any]:
    return {
        "timestamp": str(row["timestamp"]),
        "year": int(row["year"]),
        "family_tag": "RI",
        "core_state": _compact_core_state(core_state),
        "ri_state": _compact_ri_state(ri_state),
        "selected_policy": str(route["selected_policy"]),
        "previous_policy": route["previous_policy"],
        "switch_reason": str(route["switch_reason"]),
        "switch_proposed": bool(route["switch_proposed"]),
        "switch_blocked": bool(route["switch_blocked"]),
        "mandate_level": int(route["mandate_level"]),
        "confidence": int(route["confidence"]),
        "no_trade_flag": bool(route["no_trade_flag"]),
        "dwell_duration": int(route["dwell_duration"]),
        "veto_action": str(veto["veto_action"]),
        "veto_reason": str(veto["veto_reason"]),
        "final_routed_action": str(veto["final_routed_action"]),
        "final_size_multiplier": float(veto["final_size_multiplier"]),
    }


def _hash_outputs(paths: list[Path]) -> dict[str, str]:
    return {_relative_path(path): _sha256_file(path) for path in sorted(paths)}


def _compute_segments(trace_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    segments: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for row in trace_rows:
        policy = str(row["selected_policy"])
        if current is None or current["policy"] != policy:
            if current is not None:
                segments.append(current)
            current = {
                "policy": policy,
                "count": 1,
                "start_timestamp": row["timestamp"],
                "end_timestamp": row["timestamp"],
            }
            continue
        current["count"] += 1
        current["end_timestamp"] = row["timestamp"]
    if current is not None:
        segments.append(current)
    return segments


def _state_trace(trace_rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts_by_year: dict[str, dict[str, int]] = {}
    for row in trace_rows:
        year_key = str(row["year"])
        bucket = counts_by_year.setdefault(year_key, {})
        ri_state = row["ri_state"]
        for key in ["clarity_bucket", "confidence_bucket", "transition_bucket", "edge_bucket"]:
            label = f"{key}:{ri_state[key]}"
            bucket[label] = bucket.get(label, 0) + 1
    return {
        "field_allowlist_version": FIELD_ALLOWLIST_VERSION,
        "row_count": len(trace_rows),
        "counts_by_year": counts_by_year,
    }


def _policy_trace(trace_rows: list[dict[str, Any]]) -> dict[str, Any]:
    policy_counts: dict[str, int] = {}
    switch_reason_counts: dict[str, int] = {}
    proposed_switch_count = 0
    blocked_switch_count = 0
    no_trade_count = 0

    for row in trace_rows:
        policy = str(row["selected_policy"])
        reason = str(row["switch_reason"])
        policy_counts[policy] = policy_counts.get(policy, 0) + 1
        switch_reason_counts[reason] = switch_reason_counts.get(reason, 0) + 1
        if row["switch_proposed"]:
            proposed_switch_count += 1
        if row["switch_blocked"]:
            blocked_switch_count += 1
        if (
            row["selected_policy"] == POLICY_NO_TRADE
            or row["final_routed_action"] == FINAL_ACTION_NONE
        ):
            no_trade_count += 1

    segments = _compute_segments(trace_rows)
    dwell_by_policy: dict[str, list[int]] = {}
    for segment in segments:
        dwell_by_policy.setdefault(segment["policy"], []).append(int(segment["count"]))

    avg_dwell = {
        policy: round(mean(lengths), 6) for policy, lengths in sorted(dwell_by_policy.items())
    }
    time_share = {
        policy: round(count / len(trace_rows), 6) for policy, count in sorted(policy_counts.items())
    }
    actual_policy_change_count = sum(
        1
        for previous_row, current_row in zip(trace_rows, trace_rows[1:], strict=False)
        if previous_row["selected_policy"] != current_row["selected_policy"]
    )
    proposed_switch_rate = (
        0.0 if len(trace_rows) <= 1 else round(proposed_switch_count / (len(trace_rows) - 1), 6)
    )
    blocked_switch_rate = (
        0.0 if len(trace_rows) <= 1 else round(blocked_switch_count / (len(trace_rows) - 1), 6)
    )
    actual_policy_change_rate = (
        0.0
        if len(trace_rows) <= 1
        else round(actual_policy_change_count / (len(trace_rows) - 1), 6)
    )

    return {
        "router_version": ROUTER_VERSION,
        "metrics_semantics_version": METRICS_SEMANTICS_VERSION,
        "policy_counts": dict(sorted(policy_counts.items())),
        "switch_reason_counts": dict(sorted(switch_reason_counts.items())),
        "proposed_switch_count": proposed_switch_count,
        "proposed_switch_rate": proposed_switch_rate,
        "blocked_switch_count": blocked_switch_count,
        "blocked_switch_rate": blocked_switch_rate,
        "actual_policy_change_count": actual_policy_change_count,
        "actual_policy_change_rate": actual_policy_change_rate,
        "no_trade_count": no_trade_count,
        "average_dwell_by_policy": avg_dwell,
        "time_share_by_policy": time_share,
        "segments": segments,
    }


def _veto_trace(trace_rows: list[dict[str, Any]]) -> dict[str, Any]:
    action_counts: dict[str, int] = {}
    reason_counts: dict[str, int] = {}
    for row in trace_rows:
        action = str(row["veto_action"])
        reason = str(row["veto_reason"])
        action_counts[action] = action_counts.get(action, 0) + 1
        reason_counts[reason] = reason_counts.get(reason, 0) + 1
    return {
        "veto_version": VETO_VERSION,
        "action_counts": dict(sorted(action_counts.items())),
        "reason_counts": dict(sorted(reason_counts.items())),
        "veto_rate": round(
            sum(count for action, count in action_counts.items() if action != "pass")
            / len(trace_rows),
            6,
        ),
    }


def _policy_outcome_stats(observations: list[dict[str, Any]]) -> dict[str, Any]:
    trades = [item for item in observations if item["final_routed_action"] != FINAL_ACTION_NONE]
    wins = [item["total_pnl"] for item in trades if item["total_pnl"] > 0]
    losses = [item["total_pnl"] for item in trades if item["total_pnl"] < 0]
    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))
    profit_factor = None if gross_loss == 0 else round(gross_profit / gross_loss, 6)
    return {
        "row_count": len(observations),
        "trade_count": len(trades),
        "winrate": None if not trades else round(len(wins) / len(trades), 6),
        "average_win": None if not wins else round(sum(wins) / len(wins), 6),
        "average_loss": None if not losses else round(sum(losses) / len(losses), 6),
        "profit_factor": profit_factor,
    }


def _replay_metrics(
    trace_rows: list[dict[str, Any]],
    observations: list[dict[str, Any]],
    policy_trace: dict[str, Any],
    veto_trace: dict[str, Any],
) -> dict[str, Any]:
    by_policy: dict[str, list[dict[str, Any]]] = {}
    by_year: dict[str, list[dict[str, Any]]] = {}
    for item in observations:
        by_policy.setdefault(str(item["selected_policy"]), []).append(item)
        by_year.setdefault(str(item["year"]), []).append(item)

    per_policy = {policy: _policy_outcome_stats(rows) for policy, rows in sorted(by_policy.items())}
    per_year = {year: _policy_outcome_stats(rows) for year, rows in sorted(by_year.items())}

    continuation_trades = per_policy.get(POLICY_CONTINUATION, {}).get("trade_count", 0)
    defensive_trades = per_policy.get(POLICY_DEFENSIVE, {}).get("trade_count", 0)
    no_trade_rate = round(
        sum(1 for row in trace_rows if row["final_routed_action"] == FINAL_ACTION_NONE)
        / len(trace_rows),
        6,
    )

    if (
        continuation_trades >= 10
        and defensive_trades >= 10
        and policy_trace["actual_policy_change_rate"] <= 0.25
    ):
        recommendation = "APPROACH_PROMISING"
    elif continuation_trades == 0 and defensive_trades == 0:
        recommendation = "NOT_READY"
    else:
        recommendation = "NEEDS_REVISION"

    return {
        "router_version": ROUTER_VERSION,
        "field_allowlist_version": FIELD_ALLOWLIST_VERSION,
        "metrics_semantics_version": METRICS_SEMANTICS_VERSION,
        "observational_only": True,
        "not_used_for_routing": OBSERVATIONAL_ONLY_FIELDS,
        "recommendation_scope": "observed_replay_quality_only",
        "routing_metrics": {
            "row_count": len(trace_rows),
            "policy_selection_frequency": policy_trace["policy_counts"],
            "proposed_switch_count": policy_trace["proposed_switch_count"],
            "proposed_switch_rate": policy_trace["proposed_switch_rate"],
            "blocked_switch_count": policy_trace["blocked_switch_count"],
            "blocked_switch_rate": policy_trace["blocked_switch_rate"],
            "actual_policy_change_count": policy_trace["actual_policy_change_count"],
            "actual_policy_change_rate": policy_trace["actual_policy_change_rate"],
            "average_dwell_by_policy": policy_trace["average_dwell_by_policy"],
            "veto_rate": veto_trace["veto_rate"],
            "no_trade_rate": no_trade_rate,
            "time_share_by_policy": policy_trace["time_share_by_policy"],
        },
        "observational_metrics": {
            "per_policy": per_policy,
            "per_year": per_year,
        },
        "recommendation": recommendation,
    }


def _build_summary(metrics: dict[str, Any], trace_rows: list[dict[str, Any]]) -> str:
    routing = metrics["routing_metrics"]
    year_metrics = metrics["observational_metrics"]["per_year"]
    return (
        "\n".join(
            [
                "# SCPE RI V1 router replay summary",
                "",
                "Mode: RESEARCH",
                "Scope: RI-only, research-only, default unchanged, no runtime integration",
                "",
                "## What was built",
                "",
                "- Deterministic replay of frozen RI evidence rows through an RI-only router.",
                "- Three explicit policies: continuation, defensive transition, no-trade.",
                "- Downstream veto limited to pass/reduce/cap/veto/force no-trade.",
                "",
                "## Explicit exclusions",
                "",
                "- No runtime integration",
                "- No backtest execution integration",
                "- No cross-family routing",
                "- No use of realized outcome columns in routing logic",
                "",
                "## Router behavior",
                "",
                f"- row_count: `{routing['row_count']}`",
                f"- proposed_switch_count: `{routing['proposed_switch_count']}`",
                f"- proposed_switch_rate: `{routing['proposed_switch_rate']}` (proposal pressure, includes blocked switch attempts)",
                f"- blocked_switch_count: `{routing['blocked_switch_count']}`",
                f"- blocked_switch_rate: `{routing['blocked_switch_rate']}`",
                f"- actual_policy_change_count: `{routing['actual_policy_change_count']}`",
                f"- actual_policy_change_rate: `{routing['actual_policy_change_rate']}`",
                f"- veto_rate: `{routing['veto_rate']}`",
                f"- no_trade_rate: `{routing['no_trade_rate']}`",
                f"- time_share_by_policy: `{routing['time_share_by_policy']}`",
                "",
                "## 2024 vs 2025",
                "",
                f"- 2024: `{year_metrics.get('2024', {})}`",
                f"- 2025: `{year_metrics.get('2025', {})}`",
                "",
                "## Stability findings",
                "",
                f"- blocked_switch_rows: `{sum(1 for row in trace_rows if row['switch_blocked'])}`",
                f"- actual_policy_change_rows: `{sum(1 for previous_row, current_row in zip(trace_rows, trace_rows[1:], strict=False) if previous_row['selected_policy'] != current_row['selected_policy'])}`",
                f"- no_trade_rows: `{sum(1 for row in trace_rows if row['final_routed_action'] == FINAL_ACTION_NONE)}`",
                "",
                "## Risks",
                "",
                "- Observational metrics are conditional only and do not prove integrated execution edge.",
                "- Policy distinctness still depends on whether continuation and defensive routed subsets stay materially different.",
                "- Veto dominance remains a failure mode if no-trade or overrides dominate routed decisions.",
                "",
                "## Recommendation",
                "",
                "- This recommendation applies to observed replay quality only.",
                "- It is not runtime-readiness evidence, promotion evidence, or deployment approval.",
                f"- `{metrics['recommendation']}`",
            ]
        )
        + "\n"
    )


def main() -> int:
    approved_files = [OUTPUT_DIR / name for name in APPROVED_OUTPUT_FILENAMES]
    _ensure_output_scope(OUTPUT_DIR, approved_files)

    watched_paths = [
        OUTPUT_DIR,
        ROOT_DIR / "docs",
        ROOT_DIR / "scripts",
        ROOT_DIR / "src",
        ROOT_DIR / "tests",
        ROOT_DIR / "config",
        ROOT_DIR / "artifacts",
        ROOT_DIR / "logs",
        ROOT_DIR / "cache",
    ] + [spec.path for spec in INPUT_SOURCES]

    pre_snapshot = _snapshot_paths(watched_paths)
    capture_summary = _load_json(CAPTURE_SUMMARY_PATH)
    input_rows = _load_entry_rows(ENTRY_ROWS_PATH)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    input_manifest_path = OUTPUT_DIR / "input_manifest.json"
    routing_trace_path = OUTPUT_DIR / "routing_trace.ndjson"
    state_trace_path = OUTPUT_DIR / "state_trace.json"
    policy_trace_path = OUTPUT_DIR / "policy_trace.json"
    veto_trace_path = OUTPUT_DIR / "veto_trace.json"
    replay_metrics_path = OUTPUT_DIR / "replay_metrics.json"
    summary_path = OUTPUT_DIR / "summary.md"
    manifest_path = OUTPUT_DIR / "manifest.json"

    approved_output_files = [
        input_manifest_path,
        routing_trace_path,
        state_trace_path,
        policy_trace_path,
        veto_trace_path,
        replay_metrics_path,
        summary_path,
        manifest_path,
    ]

    schema_fields = sorted({key for row in input_rows for key in row.keys()})
    ignored_fields = sorted(set(schema_fields) - set(CORE_STATE_FIELDS) - set(RI_STATE_FIELDS))

    input_manifest = {
        "field_allowlist_version": FIELD_ALLOWLIST_VERSION,
        "eligibility_version": ELIGIBILITY_VERSION,
        "router_version": ROUTER_VERSION,
        "veto_version": VETO_VERSION,
        "metrics_semantics_version": METRICS_SEMANTICS_VERSION,
        "approved_output_files": [_relative_path(path) for path in approved_output_files],
        "core_state_fields": CORE_STATE_FIELDS,
        "ri_state_fields": RI_STATE_FIELDS,
        "observational_only_fields": OBSERVATIONAL_ONLY_FIELDS,
        "input_schema_fields": schema_fields,
        "ignored_input_fields": ignored_fields,
        "router_params": ROUTER_PARAMS,
        "sources": [
            {
                "label": spec.label,
                "path": _relative_path(spec.path),
                "sha256": _sha256_file(spec.path),
            }
            for spec in INPUT_SOURCES
        ],
        "upstream_capture": {
            "capture_summary": capture_summary,
            "capture_manifest_path": _relative_path(CAPTURE_MANIFEST_PATH),
            "capture_manifest_sha256": _sha256_file(CAPTURE_MANIFEST_PATH),
            "capture_summary_sha256": _sha256_file(CAPTURE_SUMMARY_PATH),
        },
        "eligible_row_count": len(input_rows),
    }
    _write_json(input_manifest_path, input_manifest)

    trace_rows: list[dict[str, Any]] = []
    observations: list[dict[str, Any]] = []
    previous_route: dict[str, Any] | None = None

    for index, row in enumerate(input_rows, start=1):
        _require_fields(row, index)
        core_state = _derive_core_state(row, index)
        ri_state = _derive_ri_state(row, core_state, index)
        raw_decision = _build_raw_router_decision(core_state, ri_state)
        route = _apply_stability_control(raw_decision, previous_route)
        policy_decision = _build_policy_decision(route, core_state)
        veto = _apply_veto(route, policy_decision, core_state, ri_state)
        trace_row = _build_trace_row(row, core_state, ri_state, route, veto)
        trace_rows.append(trace_row)
        observations.append(
            {
                "year": int(row["year"]),
                "selected_policy": str(trace_row["selected_policy"]),
                "final_routed_action": str(trace_row["final_routed_action"]),
                "total_pnl": _as_float(row, "total_pnl", index),
            }
        )
        previous_route = {
            "selected_policy": trace_row["selected_policy"],
            "mandate_level": trace_row["mandate_level"],
            "confidence": trace_row["confidence"],
            "dwell_duration": trace_row["dwell_duration"],
        }

    _write_ndjson(routing_trace_path, trace_rows)
    state_trace = _state_trace(trace_rows)
    policy_trace = _policy_trace(trace_rows)
    veto_trace = _veto_trace(trace_rows)
    replay_metrics = _replay_metrics(trace_rows, observations, policy_trace, veto_trace)

    _write_json(state_trace_path, state_trace)
    _write_json(policy_trace_path, policy_trace)
    _write_json(veto_trace_path, veto_trace)
    _write_json(replay_metrics_path, replay_metrics)
    summary_path.write_text(_build_summary(replay_metrics, trace_rows), encoding="utf-8")

    output_hashes = _hash_outputs(
        [
            input_manifest_path,
            routing_trace_path,
            state_trace_path,
            policy_trace_path,
            veto_trace_path,
            replay_metrics_path,
            summary_path,
        ]
    )

    diff_events = _diff_snapshots(pre_snapshot, _snapshot_paths(watched_paths))
    approved_rel = {_relative_path(path) for path in approved_output_files}
    manifest_rel = _relative_path(manifest_path)
    manifest_event = {
        "event": "modify" if manifest_rel in pre_snapshot else "create",
        "path": manifest_rel,
    }
    if not any(event["path"] == manifest_rel for event in diff_events):
        diff_events.append(manifest_event)
    diff_events = _sort_events(diff_events)
    unexpected_events = [event for event in diff_events if event["path"] not in approved_rel]

    manifest = {
        "field_allowlist_version": FIELD_ALLOWLIST_VERSION,
        "router_version": ROUTER_VERSION,
        "veto_version": VETO_VERSION,
        "metrics_semantics_version": METRICS_SEMANTICS_VERSION,
        "approved_output_dir": _relative_path(OUTPUT_DIR),
        "approved_output_files": sorted(approved_rel),
        "written_files": sorted(approved_rel),
        "input_hashes": {
            _relative_path(spec.path): _sha256_file(spec.path) for spec in INPUT_SOURCES
        },
        "output_hashes": output_hashes,
        "observational_only": True,
        "recommendation_scope": "observed_replay_quality_only",
        "containment": {
            "verdict": "PASS" if not unexpected_events else "FAIL",
            "events": diff_events,
            "unexpected_events": unexpected_events,
            "allowed_change_rule": (
                "Only the eight approved files in results/research/scpe_v1_ri may be created or "
                "modified; no external write is allowed."
            ),
        },
        "row_count": len(trace_rows),
        "recommendation": replay_metrics["recommendation"],
    }
    _write_json(manifest_path, manifest)

    post_manifest_events = _sort_events(
        _diff_snapshots(pre_snapshot, _snapshot_paths(watched_paths))
    )
    post_manifest_unexpected = [
        event for event in post_manifest_events if event["path"] not in approved_rel
    ]
    if post_manifest_unexpected:
        raise RuntimeError(
            "Containment failure outside approved outputs: "
            + json.dumps(post_manifest_unexpected, ensure_ascii=False, indent=2)
        )

    print(f"[OK] Wrote replay root: {OUTPUT_DIR}")
    print(f"[OK] Row count: {len(trace_rows)}")
    print(f"[OK] Recommendation: {replay_metrics['recommendation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
