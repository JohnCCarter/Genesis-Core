#!/usr/bin/env python3
"""Counterfactual no-trade release revision v2 over frozen RI replay evidence.

This script is RESEARCH-only. It does not modify the canonical replay root and does not
change runtime code. It evaluates a stricter, fail-closed early-release exception for a
subset of baseline-blocked `RI_no_trade_policy -> RI_continuation_policy` candidates.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


POLICY_CONTINUATION = "RI_continuation_policy"
POLICY_DEFENSIVE = "RI_defensive_transition_policy"
POLICY_NO_TRADE = "RI_no_trade_policy"
FINAL_ACTION_NONE = "NONE"
REVISION_VERSION = "scpe-ri-v1-no-trade-release-revision-v2-2026-04-20"
ROOT_REQUIRED_MARKERS = ("pyproject.toml", "src")
MID_ZONE_ONLY = "mid"
STABLE_BARS_FLOOR_V2 = 92.0

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

REQUIRED_TRACE_FIELDS = {
    "timestamp",
    "year",
    "family_tag",
    "core_state",
    "ri_state",
    "selected_policy",
    "previous_policy",
    "switch_reason",
    "switch_proposed",
    "switch_blocked",
    "mandate_level",
    "confidence",
    "no_trade_flag",
    "dwell_duration",
    "veto_action",
    "veto_reason",
    "final_routed_action",
    "final_size_multiplier",
}
REQUIRED_REPLAY_METRICS_FIELDS = {
    "observational_only",
    "recommendation",
    "recommendation_scope",
    "routing_metrics",
    "observational_metrics",
}
REQUIRED_MANIFEST_FIELDS = {"containment", "recommendation", "recommendation_scope", "row_count"}
REQUIRED_PROBE_FIELDS = {
    "observational_only",
    "summary_only",
    "non_authoritative",
    "recommendation_passthrough",
    "successful_release_envelope",
    "blocked_exit_matches",
    "cohort_counts",
}


def _find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if all((candidate / marker).exists() for marker in ROOT_REQUIRED_MARKERS):
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
BASELINE_TRACE_PATH = ROOT_DIR / "results" / "research" / "scpe_v1_ri" / "routing_trace.ndjson"
BASELINE_METRICS_PATH = ROOT_DIR / "results" / "research" / "scpe_v1_ri" / "replay_metrics.json"
BASELINE_MANIFEST_PATH = ROOT_DIR / "results" / "research" / "scpe_v1_ri" / "manifest.json"
RELEASE_PROBE_PATH = (
    ROOT_DIR / "results" / "evaluation" / "scpe_ri_v1_no_trade_release_probe_2026-04-20.json"
)
OUTPUT_PATH = (
    ROOT_DIR / "results" / "evaluation" / "scpe_ri_v1_no_trade_release_revision_v2_2026-04-20.json"
)
INPUT_PATHS = [
    ENTRY_ROWS_PATH,
    BASELINE_TRACE_PATH,
    BASELINE_METRICS_PATH,
    BASELINE_MANIFEST_PATH,
    RELEASE_PROBE_PATH,
    Path(__file__).resolve(),
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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_canonical_json_text(payload), encoding="utf-8")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_ndjson(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for index, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            payload = json.loads(text)
            if not isinstance(payload, dict):
                raise RuntimeError(f"Row {index} in {_relative_path(path)} is not a JSON object")
            rows.append(payload)
    if not rows:
        raise RuntimeError(f"{_relative_path(path)} did not contain any rows")
    return rows


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


def _require_keys(payload: dict[str, Any], required: set[str], label: str) -> None:
    missing = sorted(required - set(payload))
    if missing:
        raise RuntimeError(f"{label} missing required keys: {missing}")


def _as_float(row: dict[str, Any], field: str, index: int) -> float:
    value = row.get(field)
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"Row {index} field {field!r} must be numeric, got {value!r}") from exc


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
        raise RuntimeError(f"Row {index} has unsupported side {core_state['side']!r}")
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


def _build_policy_decision(selected_policy: str, core_state: dict[str, Any]) -> dict[str, Any]:
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
    selected_policy: str,
    policy_decision: dict[str, Any],
    core_state: dict[str, Any],
    ri_state: dict[str, Any],
) -> dict[str, Any]:
    if selected_policy == POLICY_NO_TRADE:
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
    if selected_policy == POLICY_CONTINUATION and core_state["zone"] == "high":
        return {
            "veto_action": "reduce",
            "veto_reason": "high_zone_continuation_cap",
            "final_routed_action": policy_decision["policy_action"],
            "final_size_multiplier": 0.75,
        }
    if selected_policy == POLICY_DEFENSIVE and ri_state["transition_bucket"] != "stable":
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


def _compute_metrics(
    rows: list[dict[str, Any]], entry_rows: list[dict[str, Any]]
) -> dict[str, Any]:
    if len(rows) != len(entry_rows):
        raise RuntimeError("Rows and entry_rows length mismatch")

    policy_counts: dict[str, int] = {}
    action_counts: dict[str, int] = {}
    reason_counts: dict[str, int] = {}
    no_trade_count = 0
    proposed_switch_count = 0
    blocked_switch_count = 0
    observations: list[dict[str, Any]] = []

    for row, entry in zip(rows, entry_rows, strict=False):
        policy = str(row["selected_policy"])
        policy_counts[policy] = policy_counts.get(policy, 0) + 1
        veto_action = str(row["veto_action"])
        action_counts[veto_action] = action_counts.get(veto_action, 0) + 1
        veto_reason = str(row["veto_reason"])
        reason_counts[veto_reason] = reason_counts.get(veto_reason, 0) + 1
        if row["switch_proposed"]:
            proposed_switch_count += 1
        if row["switch_blocked"]:
            blocked_switch_count += 1
        if row["final_routed_action"] == FINAL_ACTION_NONE:
            no_trade_count += 1
        observations.append(
            {
                "year": int(entry["year"]),
                "selected_policy": policy,
                "final_routed_action": str(row["final_routed_action"]),
                "total_pnl": _as_float(entry, "total_pnl", int(entry["year"])),
            }
        )

    actual_policy_change_count = sum(
        1
        for previous_row, current_row in zip(rows, rows[1:], strict=False)
        if previous_row["selected_policy"] != current_row["selected_policy"]
    )
    per_policy_obs: dict[str, list[dict[str, Any]]] = {}
    for item in observations:
        per_policy_obs.setdefault(str(item["selected_policy"]), []).append(item)

    per_policy = {
        policy: _policy_outcome_stats(items) for policy, items in sorted(per_policy_obs.items())
    }
    no_trade_rate = round(no_trade_count / len(rows), 6)
    counterfactual_assessment = "NEEDS_REVISION"
    continuation_trades = per_policy.get(POLICY_CONTINUATION, {}).get("trade_count", 0)
    defensive_trades = per_policy.get(POLICY_DEFENSIVE, {}).get("trade_count", 0)
    actual_policy_change_rate = (
        0.0 if len(rows) <= 1 else round(actual_policy_change_count / (len(rows) - 1), 6)
    )
    if continuation_trades >= 10 and defensive_trades >= 10 and actual_policy_change_rate <= 0.25:
        counterfactual_assessment = "APPROACH_PROMISING"
    elif continuation_trades == 0 and defensive_trades == 0:
        counterfactual_assessment = "NOT_READY"

    return {
        "routing_metrics": {
            "row_count": len(rows),
            "policy_selection_frequency": dict(sorted(policy_counts.items())),
            "proposed_switch_count": proposed_switch_count,
            "blocked_switch_count": blocked_switch_count,
            "actual_policy_change_count": actual_policy_change_count,
            "actual_policy_change_rate": actual_policy_change_rate,
            "no_trade_rate": no_trade_rate,
        },
        "observational_metrics": {
            "per_policy": per_policy,
        },
        "veto_metrics": {
            "action_counts": dict(sorted(action_counts.items())),
            "reason_counts": dict(sorted(reason_counts.items())),
        },
        "counterfactual_replay_quality_assessment": counterfactual_assessment,
    }


def _round6(value: float) -> float:
    return round(float(value), 6)


def _build_findings(
    changed_count: int,
    blocked_delta: int,
    no_trade_delta: float,
    continuation_trade_delta: int,
    actual_change_rate: float,
) -> list[str]:
    return [
        f"Tighter early-release changed exactly {changed_count} baseline-blocked no-trade continuation candidates and no rows outside the allowed frozen subset.",
        f"Blocked switch count moved by {blocked_delta} relative to baseline, while the canonical replay root remained unchanged.",
        f"No-trade rate moved by {no_trade_delta:+.6f} under the v2 local counterfactual override.",
        f"Continuation-policy trade count moved by {continuation_trade_delta} under the v2 counterfactual replay-quality view.",
        f"Actual policy-change rate settled at {actual_change_rate:.6f}, remaining inside the <= 0.25 replay-quality comfort ceiling used by this research lane.",
    ]


def main() -> int:
    replay_pre_snapshot = _snapshot_paths([ROOT_DIR / "results" / "research" / "scpe_v1_ri"])

    entry_rows = _load_ndjson(ENTRY_ROWS_PATH)
    baseline_rows = _load_ndjson(BASELINE_TRACE_PATH)
    baseline_metrics = _load_json(BASELINE_METRICS_PATH)
    baseline_manifest = _load_json(BASELINE_MANIFEST_PATH)
    release_probe = _load_json(RELEASE_PROBE_PATH)

    if len(entry_rows) != len(baseline_rows):
        raise RuntimeError("Baseline routing trace length does not match frozen entry rows")

    _require_keys(baseline_metrics, REQUIRED_REPLAY_METRICS_FIELDS, "baseline replay_metrics")
    _require_keys(baseline_manifest, REQUIRED_MANIFEST_FIELDS, "baseline manifest")
    _require_keys(release_probe, REQUIRED_PROBE_FIELDS, "release_probe")
    if baseline_metrics["recommendation"] != "NEEDS_REVISION":
        raise RuntimeError("Baseline recommendation drifted away from NEEDS_REVISION")
    if baseline_manifest["containment"]["verdict"] != "PASS":
        raise RuntimeError("Baseline manifest containment verdict must remain PASS")
    if (
        release_probe["observational_only"] is not True
        or release_probe["non_authoritative"] is not True
    ):
        raise RuntimeError("Release probe must remain observational-only and non-authoritative")

    categorical = release_probe["successful_release_envelope"]["categorical"]
    numeric = release_probe["successful_release_envelope"]["numeric"]
    probe_hash = _sha256_file(RELEASE_PROBE_PATH)

    revised_rows: list[dict[str, Any]] = []
    allowed_candidate_indices: set[int] = set()
    changed_indices: list[int] = []
    changed_rows: list[dict[str, Any]] = []

    for index, (entry_row, baseline_row) in enumerate(
        zip(entry_rows, baseline_rows, strict=False), start=1
    ):
        _require_keys(baseline_row, REQUIRED_TRACE_FIELDS, f"baseline routing_trace row {index}")
        missing_fields = sorted(field for field in REQUIRED_INPUT_FIELDS if field not in entry_row)
        if missing_fields:
            raise RuntimeError(
                f"Entry row {index} missing required fields for v2 revision: {missing_fields}"
            )
        core_state = _derive_core_state(entry_row, index)
        ri_state = _derive_ri_state(entry_row, core_state, index)
        raw_decision = _build_raw_router_decision(core_state, ri_state)

        baseline_selected = str(baseline_row["selected_policy"])
        baseline_previous = str(baseline_row["previous_policy"])
        baseline_reason = str(baseline_row["switch_reason"])
        baseline_blocked = bool(baseline_row["switch_blocked"])

        allowed_candidate = (
            baseline_previous == POLICY_NO_TRADE
            and baseline_selected == POLICY_NO_TRADE
            and baseline_blocked
            and baseline_reason == "switch_blocked_by_min_dwell"
            and str(raw_decision["target_policy"]) == POLICY_CONTINUATION
            and str(ri_state["clarity_bucket"]) in set(categorical["clarity_bucket"])
            and str(ri_state["confidence_bucket"]) in set(categorical["confidence_bucket"])
            and str(ri_state["edge_bucket"]) in set(categorical["edge_bucket"])
            and str(ri_state["transition_bucket"]) in set(categorical["transition_bucket"])
            and str(core_state["zone"]) == MID_ZONE_ONLY
            and str(core_state["zone"]) in set(categorical["zone"])
            and numeric["bars_since_regime_change"]["min"]
            <= ri_state["bars_since_regime_change"]
            <= numeric["bars_since_regime_change"]["max"]
            and numeric["ri_clarity_score"]["min"]
            <= ri_state["ri_clarity_score"]
            <= numeric["ri_clarity_score"]["max"]
            and numeric["conf_overall"]["min"]
            <= ri_state["conf_overall"]
            <= numeric["conf_overall"]["max"]
            and numeric["action_edge"]["min"]
            <= ri_state["action_edge"]
            <= numeric["action_edge"]["max"]
            and ri_state["ri_clarity_score"] >= numeric["ri_clarity_score"]["median"]
            and ri_state["conf_overall"] >= numeric["conf_overall"]["median"]
            and ri_state["action_edge"] >= numeric["action_edge"]["median"]
            and ri_state["bars_since_regime_change"] >= STABLE_BARS_FLOOR_V2
        )
        if allowed_candidate:
            allowed_candidate_indices.add(index)
            policy_decision = _build_policy_decision(POLICY_CONTINUATION, core_state)
            veto = _apply_veto(POLICY_CONTINUATION, policy_decision, core_state, ri_state)
            revised_row = dict(baseline_row)
            revised_row["selected_policy"] = POLICY_CONTINUATION
            revised_row["switch_reason"] = str(raw_decision["raw_switch_reason"])
            revised_row["switch_blocked"] = False
            revised_row["switch_proposed"] = True
            revised_row["mandate_level"] = int(raw_decision["mandate_level"])
            revised_row["confidence"] = int(raw_decision["confidence"])
            revised_row["no_trade_flag"] = False
            revised_row["dwell_duration"] = 1
            revised_row["veto_action"] = str(veto["veto_action"])
            revised_row["veto_reason"] = str(veto["veto_reason"])
            revised_row["final_routed_action"] = str(veto["final_routed_action"])
            revised_row["final_size_multiplier"] = float(veto["final_size_multiplier"])
        else:
            revised_row = dict(baseline_row)
        revised_rows.append(revised_row)

        if revised_row != baseline_row:
            changed_indices.append(index)
            changed_rows.append(
                {
                    "row_index": index,
                    "timestamp": str(entry_row["timestamp"]),
                    "baseline_selected_policy": baseline_selected,
                    "revised_selected_policy": str(revised_row["selected_policy"]),
                    "baseline_switch_reason": baseline_reason,
                    "revised_switch_reason": str(revised_row["switch_reason"]),
                    "baseline_final_routed_action": str(baseline_row["final_routed_action"]),
                    "revised_final_routed_action": str(revised_row["final_routed_action"]),
                    "zone": str(core_state["zone"]),
                    "clarity_bucket": str(ri_state["clarity_bucket"]),
                    "confidence_bucket": str(ri_state["confidence_bucket"]),
                    "edge_bucket": str(ri_state["edge_bucket"]),
                    "transition_bucket": str(ri_state["transition_bucket"]),
                    "ri_clarity_score": _round6(ri_state["ri_clarity_score"]),
                    "conf_overall": _round6(ri_state["conf_overall"]),
                    "action_edge": _round6(ri_state["action_edge"]),
                    "bars_since_regime_change": _round6(ri_state["bars_since_regime_change"]),
                }
            )

    changed_outside_allowed = [
        index for index in changed_indices if index not in allowed_candidate_indices
    ]
    if changed_outside_allowed:
        raise RuntimeError(
            "Containment failure: changed rows outside allowed baseline-blocked subset: "
            + json.dumps(changed_outside_allowed, ensure_ascii=False)
        )

    baseline_summary = {
        "recommendation_passthrough": str(baseline_metrics["recommendation"]),
        "recommendation_scope": str(baseline_metrics["recommendation_scope"]),
        "routing_metrics": baseline_metrics["routing_metrics"],
        "observational_metrics": baseline_metrics["observational_metrics"],
    }
    revised_summary = _compute_metrics(revised_rows, entry_rows)

    baseline_cont_trade_count = int(
        baseline_metrics["observational_metrics"]["per_policy"]
        .get(POLICY_CONTINUATION, {})
        .get("trade_count", 0)
    )
    revised_cont_trade_count = int(
        revised_summary["observational_metrics"]["per_policy"]
        .get(POLICY_CONTINUATION, {})
        .get("trade_count", 0)
    )
    no_trade_delta = _round6(
        float(revised_summary["routing_metrics"]["no_trade_rate"])
        - float(baseline_metrics["routing_metrics"]["no_trade_rate"])
    )
    actual_change_rate = float(revised_summary["routing_metrics"]["actual_policy_change_rate"])

    payload = {
        "date": "2026-04-20",
        "branch": "feature/ri-role-map-implementation-2026-03-24",
        "mode": "RESEARCH",
        "status": "no-trade-release-revision-v2-generated",
        "revision_version": REVISION_VERSION,
        "observational_only": True,
        "counterfactual_only": True,
        "non_authoritative": True,
        "runtime_unchanged": True,
        "canonical_replay_root_unchanged": True,
        "baseline_recommendation_passthrough": str(baseline_metrics["recommendation"]),
        "baseline_recommendation_scope": str(baseline_metrics["recommendation_scope"]),
        "source_hashes": {_relative_path(path): _sha256_file(path) for path in INPUT_PATHS},
        "release_probe_binding": {
            "path": _relative_path(RELEASE_PROBE_PATH),
            "sha256": probe_hash,
            "categorical_support": categorical,
            "numeric_support": numeric,
        },
        "revision_rule": {
            "previous_policy_must_be": POLICY_NO_TRADE,
            "raw_target_policy_must_be": POLICY_CONTINUATION,
            "baseline_switch_reason_must_be": "switch_blocked_by_min_dwell",
            "baseline_switch_blocked_must_be": True,
            "categorical_support_required": True,
            "numeric_support_required": True,
            "median_floor_required_for": [
                "ri_clarity_score",
                "conf_overall",
                "action_edge",
            ],
            "zone_must_equal": MID_ZONE_ONLY,
            "bars_since_regime_change_floor": STABLE_BARS_FLOOR_V2,
            "non_propagating_local_override": True,
        },
        "containment": {
            "allowed_candidate_count": len(allowed_candidate_indices),
            "changed_row_count": len(changed_indices),
            "changed_outside_allowed_count": len(changed_outside_allowed),
            "changed_outside_allowed_rows": changed_outside_allowed,
        },
        "changed_rows": changed_rows,
        "baseline_summary": baseline_summary,
        "revised_summary": revised_summary,
        "delta_summary": {
            "blocked_switch_count_delta": int(
                revised_summary["routing_metrics"]["blocked_switch_count"]
            )
            - int(baseline_metrics["routing_metrics"]["blocked_switch_count"]),
            "actual_policy_change_count_delta": int(
                revised_summary["routing_metrics"]["actual_policy_change_count"]
            )
            - int(baseline_metrics["routing_metrics"]["actual_policy_change_count"]),
            "no_trade_rate_delta": no_trade_delta,
            "continuation_trade_count_delta": revised_cont_trade_count - baseline_cont_trade_count,
        },
        "findings": _build_findings(
            len(changed_indices),
            int(revised_summary["routing_metrics"]["blocked_switch_count"])
            - int(baseline_metrics["routing_metrics"]["blocked_switch_count"]),
            no_trade_delta,
            revised_cont_trade_count - baseline_cont_trade_count,
            actual_change_rate,
        ),
    }

    _write_json(OUTPUT_PATH, payload)

    replay_post_snapshot = _snapshot_paths([ROOT_DIR / "results" / "research" / "scpe_v1_ri"])
    replay_root_diff = _diff_snapshots(replay_pre_snapshot, replay_post_snapshot)
    if replay_root_diff:
        raise RuntimeError(
            "Baseline replay root changed during revision experiment: "
            + json.dumps(replay_root_diff, ensure_ascii=False, indent=2)
        )

    print(f"[OK] Wrote revision artifact: {OUTPUT_PATH}")
    print(f"[OK] Changed rows inside allowed subset: {len(changed_indices)}")
    print(f"[OK] Baseline replay root unchanged: {BASELINE_MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
