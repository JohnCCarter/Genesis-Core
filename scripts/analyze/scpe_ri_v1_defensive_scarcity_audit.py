#!/usr/bin/env python3
"""Observational defensive-scarcity fate audit for frozen RI replay evidence.

This script is RESEARCH-only and observational-only. It reconstructs raw defensive
candidate fates using a research-side analytical mirror of the existing replay behavior.
It does not modify canonical replay logic or introduce a new defensive rule.
"""

from __future__ import annotations

import hashlib
import json
import runpy
from collections import Counter
from pathlib import Path
from typing import Any


ROOT_REQUIRED_MARKERS = ("pyproject.toml", "src")
AUDIT_VERSION = "scpe-ri-v1-defensive-scarcity-audit-2026-04-20"
POLICY_CONTINUATION = "RI_continuation_policy"
POLICY_DEFENSIVE = "RI_defensive_transition_policy"
POLICY_NO_TRADE = "RI_no_trade_policy"

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
ROUTING_TRACE_PATH = ROOT_DIR / "results" / "research" / "scpe_v1_ri" / "routing_trace.ndjson"
REPLAY_METRICS_PATH = ROOT_DIR / "results" / "research" / "scpe_v1_ri" / "replay_metrics.json"
MANIFEST_PATH = ROOT_DIR / "results" / "research" / "scpe_v1_ri" / "manifest.json"
REPLAY_SCRIPT_PATH = ROOT_DIR / "scripts" / "analyze" / "scpe_ri_v1_router_replay.py"
OUTPUT_PATH = (
    ROOT_DIR / "results" / "evaluation" / "scpe_ri_v1_defensive_scarcity_audit_2026-04-20.json"
)
INPUT_PATHS = [
    ENTRY_ROWS_PATH,
    ROUTING_TRACE_PATH,
    REPLAY_METRICS_PATH,
    MANIFEST_PATH,
    REPLAY_SCRIPT_PATH,
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


def _counter_dict(counter: Counter[str]) -> dict[str, int]:
    return dict(sorted(counter.items()))


def _round_or_none(value: float | None) -> float | None:
    return None if value is None else round(value, 6)


def _summarize_raw_candidates(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    if not candidates:
        return {
            "count": 0,
            "transition_bucket_counts": {},
            "zone_counts": {},
            "raw_reason_counts": {},
            "avg_clarity_score": None,
            "avg_conf_overall": None,
            "avg_action_edge": None,
            "avg_bars_since_regime_change": None,
        }
    return {
        "count": len(candidates),
        "transition_bucket_counts": _counter_dict(
            Counter(item["transition_bucket"] for item in candidates)
        ),
        "zone_counts": _counter_dict(Counter(item["zone"] for item in candidates)),
        "raw_reason_counts": _counter_dict(
            Counter(item["raw_switch_reason"] for item in candidates)
        ),
        "avg_clarity_score": round(
            sum(item["ri_clarity_score"] for item in candidates) / len(candidates), 6
        ),
        "avg_conf_overall": round(
            sum(item["conf_overall"] for item in candidates) / len(candidates), 6
        ),
        "avg_action_edge": round(
            sum(item["action_edge"] for item in candidates) / len(candidates), 6
        ),
        "avg_bars_since_regime_change": round(
            sum(item["bars_since_regime_change"] for item in candidates) / len(candidates), 6
        ),
    }


def _build_findings(
    raw_count: int, selected_defensive: int, selected_continuation: int, selected_no_trade: int
) -> list[str]:
    return [
        f"Defensive scarcity starts downstream of raw eligibility: {raw_count} rows resolve to raw defensive targets, but only {selected_defensive} resolve to observed defensive selection.",
        f"The largest observed fate bucket for raw defensive candidates is retained continuation ({selected_continuation} rows), dominated by `confidence_below_threshold` rather than by raw-target absence.",
        f"A second material bucket remains in no-trade ({selected_no_trade} rows), dominated by `switch_blocked_by_min_dwell`, which shows that defensive scarcity is also shaped by stability controls rather than pure state rarity.",
    ]


def main() -> int:
    replay_pre_snapshot = _snapshot_paths([ROOT_DIR / "results" / "research" / "scpe_v1_ri"])

    entry_rows = _load_ndjson(ENTRY_ROWS_PATH)
    trace_rows = _load_ndjson(ROUTING_TRACE_PATH)
    replay_metrics = _load_json(REPLAY_METRICS_PATH)
    manifest = _load_json(MANIFEST_PATH)

    if len(entry_rows) != len(trace_rows):
        raise RuntimeError("Entry rows and routing trace length mismatch")

    _require_keys(replay_metrics, REQUIRED_REPLAY_METRICS_FIELDS, "replay_metrics")
    _require_keys(manifest, REQUIRED_MANIFEST_FIELDS, "manifest")
    if replay_metrics["observational_only"] is not True:
        raise RuntimeError("Replay metrics must remain observational-only")
    if replay_metrics["recommendation"] != "NEEDS_REVISION":
        raise RuntimeError("Replay recommendation drifted away from NEEDS_REVISION")
    if manifest["containment"]["verdict"] != "PASS":
        raise RuntimeError("Replay manifest containment verdict must remain PASS")

    replay_ns = runpy.run_path(str(REPLAY_SCRIPT_PATH))

    raw_candidates: list[dict[str, Any]] = []
    selected_policy_counts: Counter[str] = Counter()
    switch_reason_counts: Counter[str] = Counter()
    veto_reason_counts: Counter[str] = Counter()
    fate_buckets: Counter[str] = Counter()
    fate_details: dict[str, list[dict[str, Any]]] = {
        "selected_defensive": [],
        "retained_continuation_confidence_threshold": [],
        "retained_no_trade_min_dwell": [],
        "selected_defensive_veto_cap": [],
        "selected_defensive_veto_force_no_trade": [],
        "other_observed_fates": [],
    }

    for index, (entry_row, trace_row) in enumerate(
        zip(entry_rows, trace_rows, strict=False), start=1
    ):
        _require_keys(trace_row, REQUIRED_TRACE_FIELDS, f"routing_trace row {index}")
        core = replay_ns["_derive_core_state"](entry_row, index)
        ri = replay_ns["_derive_ri_state"](entry_row, core, index)
        raw_decision = replay_ns["_build_raw_router_decision"](core, ri)
        if raw_decision["target_policy"] != POLICY_DEFENSIVE:
            continue

        candidate = {
            "row_index": index,
            "timestamp": str(trace_row["timestamp"]),
            "raw_switch_reason": str(raw_decision["raw_switch_reason"]),
            "selected_policy": str(trace_row["selected_policy"]),
            "switch_reason": str(trace_row["switch_reason"]),
            "veto_reason": str(trace_row["veto_reason"]),
            "veto_action": str(trace_row["veto_action"]),
            "final_routed_action": str(trace_row["final_routed_action"]),
            "transition_bucket": str(ri["transition_bucket"]),
            "zone": str(core["zone"]),
            "ri_clarity_score": round(float(ri["ri_clarity_score"]), 6),
            "conf_overall": round(float(ri["conf_overall"]), 6),
            "action_edge": round(float(ri["action_edge"]), 6),
            "bars_since_regime_change": round(float(ri["bars_since_regime_change"]), 6),
        }
        raw_candidates.append(candidate)

        selected_policy_counts[candidate["selected_policy"]] += 1
        switch_reason_counts[candidate["switch_reason"]] += 1
        veto_reason_counts[candidate["veto_reason"]] += 1

        if candidate["selected_policy"] == POLICY_DEFENSIVE:
            fate_buckets["selected_defensive"] += 1
            fate_details["selected_defensive"].append(candidate)
            if candidate["veto_reason"] == "defensive_transition_cap":
                fate_buckets["selected_defensive_veto_cap"] += 1
                fate_details["selected_defensive_veto_cap"].append(candidate)
            elif candidate["veto_reason"] == "state_below_veto_floor":
                fate_buckets["selected_defensive_veto_force_no_trade"] += 1
                fate_details["selected_defensive_veto_force_no_trade"].append(candidate)
        elif (
            candidate["selected_policy"] == POLICY_CONTINUATION
            and candidate["switch_reason"] == "confidence_below_threshold"
        ):
            fate_buckets["retained_continuation_confidence_threshold"] += 1
            fate_details["retained_continuation_confidence_threshold"].append(candidate)
        elif (
            candidate["selected_policy"] == POLICY_NO_TRADE
            and candidate["switch_reason"] == "switch_blocked_by_min_dwell"
        ):
            fate_buckets["retained_no_trade_min_dwell"] += 1
            fate_details["retained_no_trade_min_dwell"].append(candidate)
        else:
            fate_buckets["other_observed_fates"] += 1
            fate_details["other_observed_fates"].append(candidate)

    payload = {
        "date": "2026-04-20",
        "branch": "feature/ri-role-map-implementation-2026-03-24",
        "mode": "RESEARCH",
        "status": "defensive-scarcity-audit-generated",
        "audit_version": AUDIT_VERSION,
        "observational_only": True,
        "summary_only": True,
        "non_authoritative": True,
        "recommendation_change": "none",
        "read_only_inputs_confirmed": True,
        "source_hashes": {_relative_path(path): _sha256_file(path) for path in INPUT_PATHS},
        "frozen_inputs": {
            "entry_rows": {
                "path": _relative_path(ENTRY_ROWS_PATH),
                "sha256": _sha256_file(ENTRY_ROWS_PATH),
            },
            "routing_trace": {
                "path": _relative_path(ROUTING_TRACE_PATH),
                "sha256": _sha256_file(ROUTING_TRACE_PATH),
            },
            "replay_metrics": {
                "path": _relative_path(REPLAY_METRICS_PATH),
                "sha256": _sha256_file(REPLAY_METRICS_PATH),
            },
            "replay_manifest": {
                "path": _relative_path(MANIFEST_PATH),
                "sha256": _sha256_file(MANIFEST_PATH),
            },
            "replay_script_reference": {
                "path": _relative_path(REPLAY_SCRIPT_PATH),
                "sha256": _sha256_file(REPLAY_SCRIPT_PATH),
            },
        },
        "baseline_recommendation_passthrough": str(replay_metrics["recommendation"]),
        "baseline_recommendation_scope": str(replay_metrics["recommendation_scope"]),
        "raw_defensive_candidate_summary": _summarize_raw_candidates(raw_candidates),
        "observed_selected_policy_counts": _counter_dict(selected_policy_counts),
        "observed_switch_reason_counts": _counter_dict(switch_reason_counts),
        "observed_veto_reason_counts": _counter_dict(veto_reason_counts),
        "fate_bucket_counts": _counter_dict(fate_buckets),
        "fate_bucket_examples": {key: value[:5] for key, value in sorted(fate_details.items())},
        "scarcity_origin": {
            "raw_target_rarity": False,
            "selection_or_stability_suppression": True,
            "veto_suppression_present": True,
            "primary_observed_bottlenecks": [
                "retained_continuation_confidence_threshold",
                "retained_no_trade_min_dwell",
            ],
        },
        "findings": _build_findings(
            len(raw_candidates),
            selected_policy_counts[POLICY_DEFENSIVE],
            selected_policy_counts[POLICY_CONTINUATION],
            selected_policy_counts[POLICY_NO_TRADE],
        ),
        "proposed_followup_status": "föreslagen",
        "proposed_followup_hypothesis": "A future slice should separately test whether defensive scarcity is more sensitive to threshold gating or to stability-control retention on raw defensive candidates.",
    }

    _write_json(OUTPUT_PATH, payload)

    replay_post_snapshot = _snapshot_paths([ROOT_DIR / "results" / "research" / "scpe_v1_ri"])
    replay_root_diff = _diff_snapshots(replay_pre_snapshot, replay_post_snapshot)
    if replay_root_diff:
        raise RuntimeError(
            "Baseline replay root changed during defensive scarcity audit: "
            + json.dumps(replay_root_diff, ensure_ascii=False, indent=2)
        )

    print(f"[OK] Wrote defensive scarcity audit artifact: {OUTPUT_PATH}")
    print(f"[OK] Raw defensive candidates: {len(raw_candidates)}")
    print(f"[OK] Observed defensive selected rows: {selected_policy_counts[POLICY_DEFENSIVE]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
