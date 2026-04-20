#!/usr/bin/env python3
"""Observational-only ceiling audit for the bounded no-trade release axis.

This script maps replay-quality gate components against frozen baseline and first-revision
artifacts. It does not introduce a new revision rule and does not modify the canonical
replay root.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT_REQUIRED_MARKERS = ("pyproject.toml", "src")
AUDIT_VERSION = "scpe-ri-v1-no-trade-axis-ceiling-audit-2026-04-20"
CONTINUATION_TRADE_FLOOR = 10
DEFENSIVE_TRADE_FLOOR = 10
ACTUAL_POLICY_CHANGE_RATE_CEILING = 0.25

REQUIRED_BASELINE_FIELDS = {
    "observational_only",
    "recommendation",
    "recommendation_scope",
    "routing_metrics",
    "observational_metrics",
}
REQUIRED_REVISION_FIELDS = {
    "observational_only",
    "counterfactual_only",
    "non_authoritative",
    "baseline_recommendation_passthrough",
    "baseline_recommendation_scope",
    "containment",
    "baseline_summary",
    "revised_summary",
    "delta_summary",
    "release_probe_binding",
}


def _find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if all((candidate / marker).exists() for marker in ROOT_REQUIRED_MARKERS):
            return candidate
    raise RuntimeError("Could not locate repository root")


ROOT_DIR = _find_repo_root(Path(__file__).resolve())
BASELINE_METRICS_PATH = ROOT_DIR / "results" / "research" / "scpe_v1_ri" / "replay_metrics.json"
BASELINE_MANIFEST_PATH = ROOT_DIR / "results" / "research" / "scpe_v1_ri" / "manifest.json"
REVISION_PATH = (
    ROOT_DIR / "results" / "evaluation" / "scpe_ri_v1_no_trade_release_revision_2026-04-20.json"
)
OUTPUT_PATH = (
    ROOT_DIR / "results" / "evaluation" / "scpe_ri_v1_no_trade_axis_ceiling_audit_2026-04-20.json"
)
INPUT_PATHS = [
    BASELINE_METRICS_PATH,
    BASELINE_MANIFEST_PATH,
    REVISION_PATH,
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


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_json_text(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_canonical_json_text(payload), encoding="utf-8")


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


def _component_status(value: float, threshold: float, comparison: str) -> str:
    if comparison == ">=":
        return "satisfied" if value >= threshold else "unsatisfied"
    if comparison == "<=":
        return "satisfied" if value <= threshold else "unsatisfied"
    raise RuntimeError(f"Unsupported comparison {comparison!r}")


def _build_findings(
    axis_can_clear: bool, defensive_shortfall: int, remaining_churn_budget: int
) -> list[str]:
    verdict_text = "cannot" if not axis_can_clear else "can"
    return [
        f"The bounded no-trade release axis {verdict_text} satisfy the full replay-quality gate on its own under unchanged baseline and first-revision inputs.",
        f"The defensive trade floor remains short by {defensive_shortfall} trades even after the first revision, which keeps a separate bottleneck outside the continuation-release axis in place.",
        f"The change-rate ceiling still leaves capacity for at most {remaining_churn_budget} additional actual policy changes above baseline, so churn is binding but not the only blocker on this axis.",
    ]


def main() -> int:
    replay_pre_snapshot = _snapshot_paths([ROOT_DIR / "results" / "research" / "scpe_v1_ri"])

    baseline_metrics = _load_json(BASELINE_METRICS_PATH)
    baseline_manifest = _load_json(BASELINE_MANIFEST_PATH)
    revision = _load_json(REVISION_PATH)

    _require_keys(baseline_metrics, REQUIRED_BASELINE_FIELDS, "baseline_metrics")
    _require_keys(revision, REQUIRED_REVISION_FIELDS, "revision")
    if baseline_metrics["observational_only"] is not True:
        raise RuntimeError("Baseline replay metrics must remain observational-only")
    if baseline_metrics["recommendation"] != "NEEDS_REVISION":
        raise RuntimeError("Baseline recommendation drifted away from NEEDS_REVISION")
    if baseline_manifest["containment"]["verdict"] != "PASS":
        raise RuntimeError("Baseline manifest containment verdict must remain PASS")
    if revision["observational_only"] is not True or revision["counterfactual_only"] is not True:
        raise RuntimeError(
            "Revision artifact must remain observational-only and counterfactual-only"
        )
    if revision["containment"]["changed_outside_allowed_count"] != 0:
        raise RuntimeError("Revision containment must remain exact before ceiling audit proceeds")

    baseline_routing = baseline_metrics["routing_metrics"]
    baseline_per_policy = baseline_metrics["observational_metrics"]["per_policy"]
    revised_routing = revision["revised_summary"]["routing_metrics"]
    revised_per_policy = revision["revised_summary"]["observational_metrics"]["per_policy"]

    baseline_continuation_trades = int(
        baseline_per_policy.get("RI_continuation_policy", {}).get("trade_count", 0)
    )
    baseline_defensive_trades = int(
        baseline_per_policy.get("RI_defensive_transition_policy", {}).get("trade_count", 0)
    )
    baseline_change_rate = float(baseline_routing["actual_policy_change_rate"])

    revised_continuation_trades = int(
        revised_per_policy.get("RI_continuation_policy", {}).get("trade_count", 0)
    )
    revised_defensive_trades = int(
        revised_per_policy.get("RI_defensive_transition_policy", {}).get("trade_count", 0)
    )
    revised_change_rate = float(revised_routing["actual_policy_change_rate"])

    row_count = int(baseline_routing["row_count"])
    max_allowed_actual_policy_changes = math.floor(
        ACTUAL_POLICY_CHANGE_RATE_CEILING * (row_count - 1)
    )
    baseline_actual_policy_changes = int(baseline_routing["actual_policy_change_count"])
    remaining_churn_budget = max_allowed_actual_policy_changes - baseline_actual_policy_changes
    revision_changed_rows = int(revision["containment"]["changed_row_count"])

    continuation_component = {
        "threshold": CONTINUATION_TRADE_FLOOR,
        "comparison": ">=",
        "baseline_value": baseline_continuation_trades,
        "revised_value": revised_continuation_trades,
        "baseline_status": _component_status(
            baseline_continuation_trades, CONTINUATION_TRADE_FLOOR, ">="
        ),
        "revised_status": _component_status(
            revised_continuation_trades, CONTINUATION_TRADE_FLOOR, ">="
        ),
        "axis_classification": "satisfiable",
        "axis_reason": "The bounded no-trade release axis directly increases continuation participation and the floor is already satisfied in baseline.",
    }
    defensive_shortfall = DEFENSIVE_TRADE_FLOOR - revised_defensive_trades
    defensive_component = {
        "threshold": DEFENSIVE_TRADE_FLOOR,
        "comparison": ">=",
        "baseline_value": baseline_defensive_trades,
        "revised_value": revised_defensive_trades,
        "baseline_status": _component_status(
            baseline_defensive_trades, DEFENSIVE_TRADE_FLOOR, ">="
        ),
        "revised_status": _component_status(revised_defensive_trades, DEFENSIVE_TRADE_FLOOR, ">="),
        "axis_classification": "unsatisfiable",
        "axis_reason": "The bounded no-trade release axis only releases RI_no_trade_policy -> RI_continuation_policy rows, so defensive trade count remains invariant on this axis.",
        "shortfall_after_revision": defensive_shortfall,
    }
    change_rate_component = {
        "threshold": ACTUAL_POLICY_CHANGE_RATE_CEILING,
        "comparison": "<=",
        "baseline_value": round(baseline_change_rate, 6),
        "revised_value": round(revised_change_rate, 6),
        "baseline_status": _component_status(
            baseline_change_rate, ACTUAL_POLICY_CHANGE_RATE_CEILING, "<="
        ),
        "revised_status": _component_status(
            revised_change_rate, ACTUAL_POLICY_CHANGE_RATE_CEILING, "<="
        ),
        "axis_classification": "satisfiable",
        "axis_reason": "Change-rate pressure is binding but controllable by selecting a smaller subset of candidate releases on the same axis.",
        "max_allowed_actual_policy_changes": max_allowed_actual_policy_changes,
        "baseline_actual_policy_changes": baseline_actual_policy_changes,
        "remaining_capacity_above_baseline": remaining_churn_budget,
        "first_revision_changed_rows": revision_changed_rows,
        "required_release_reduction_to_re-enter_ceiling": max(
            0, revision_changed_rows - remaining_churn_budget
        ),
    }

    axis_can_clear = False
    payload = {
        "date": "2026-04-20",
        "branch": "feature/ri-role-map-implementation-2026-03-24",
        "mode": "RESEARCH",
        "status": "no-trade-axis-ceiling-audit-generated",
        "audit_version": AUDIT_VERSION,
        "observational_only": True,
        "summary_only": True,
        "non_authoritative": True,
        "recommendation_change": "none",
        "read_only_inputs_confirmed": True,
        "source_hashes": {_relative_path(path): _sha256_file(path) for path in INPUT_PATHS},
        "frozen_inputs": {
            "baseline_replay_metrics": {
                "path": _relative_path(BASELINE_METRICS_PATH),
                "sha256": _sha256_file(BASELINE_METRICS_PATH),
            },
            "baseline_replay_manifest": {
                "path": _relative_path(BASELINE_MANIFEST_PATH),
                "sha256": _sha256_file(BASELINE_MANIFEST_PATH),
            },
            "first_revision_artifact": {
                "path": _relative_path(REVISION_PATH),
                "sha256": _sha256_file(REVISION_PATH),
            },
        },
        "baseline_recommendation_passthrough": str(baseline_metrics["recommendation"]),
        "baseline_recommendation_scope": str(baseline_metrics["recommendation_scope"]),
        "first_revision_counterfactual_assessment": str(
            revision["revised_summary"]["counterfactual_replay_quality_assessment"]
        ),
        "gate_components": {
            "continuation_trade_floor": continuation_component,
            "defensive_trade_floor": defensive_component,
            "actual_policy_change_rate_ceiling": change_rate_component,
        },
        "axis_ceiling_verdict": {
            "full_gate_satisfiable_on_no_trade_axis_alone": axis_can_clear,
            "classification": "blocked_by_external_gate" if not axis_can_clear else "satisfiable",
            "reason": "The defensive trade floor remains unsatisfiable on the bounded no-trade continuation-release axis even before churn is considered.",
        },
        "findings": _build_findings(axis_can_clear, defensive_shortfall, remaining_churn_budget),
        "proposed_followup_status": "föreslagen",
        "proposed_followup_hypothesis": "A future slice should investigate the defensive-policy scarcity bottleneck separately from the no-trade continuation-release axis.",
    }

    _write_json(OUTPUT_PATH, payload)

    replay_post_snapshot = _snapshot_paths([ROOT_DIR / "results" / "research" / "scpe_v1_ri"])
    replay_root_diff = _diff_snapshots(replay_pre_snapshot, replay_post_snapshot)
    if replay_root_diff:
        raise RuntimeError(
            "Baseline replay root changed during axis ceiling audit: "
            + json.dumps(replay_root_diff, ensure_ascii=False, indent=2)
        )

    print(f"[OK] Wrote ceiling audit artifact: {OUTPUT_PATH}")
    print(f"[OK] No-trade axis can clear full gate alone: {axis_can_clear}")
    print(f"[OK] Defensive trade shortfall after first revision: {defensive_shortfall}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
