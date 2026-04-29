#!/usr/bin/env python3
"""Summary-only diagnostics for the tracked SCPE RI V1 replay outputs.

This script is research-only and read-only with respect to the replay root. It explains
why the replay still lands on `NEEDS_REVISION` by decomposing policy support, blocked
switches, and veto/no-trade sources using existing replay artifacts only.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


POLICY_CONTINUATION = "RI_continuation_policy"
POLICY_DEFENSIVE = "RI_defensive_transition_policy"
POLICY_NO_TRADE = "RI_no_trade_policy"
FINAL_ACTION_NONE = "NONE"

ROOT_REQUIRED_MARKERS = ("pyproject.toml", "src")
DIAGNOSTICS_VERSION = "scpe-ri-v1-router-diagnostics-2026-04-20"

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

REQUIRED_RI_STATE_FIELDS = {
    "ri_clarity_score",
    "ri_clarity_raw",
    "bars_since_regime_change",
    "action_edge",
    "conf_overall",
    "clarity_bucket",
    "confidence_bucket",
    "transition_bucket",
    "edge_bucket",
}

REQUIRED_POLICY_TRACE_FIELDS = {
    "policy_counts",
    "switch_reason_counts",
    "proposed_switch_count",
    "blocked_switch_count",
    "actual_policy_change_count",
    "actual_policy_change_rate",
    "segments",
}

REQUIRED_VETO_TRACE_FIELDS = {"action_counts", "reason_counts", "veto_version", "veto_rate"}
REQUIRED_REPLAY_METRICS_FIELDS = {
    "observational_only",
    "recommendation",
    "recommendation_scope",
    "routing_metrics",
    "observational_metrics",
}
ALLOWED_TRACE_FIELDS = REQUIRED_TRACE_FIELDS
ALLOWED_RI_STATE_FIELDS = REQUIRED_RI_STATE_FIELDS
ALLOWED_POLICY_TRACE_FIELDS = REQUIRED_POLICY_TRACE_FIELDS | {
    "router_version",
    "metrics_semantics_version",
    "no_trade_count",
    "average_dwell_by_policy",
    "blocked_switch_rate",
    "proposed_switch_rate",
    "time_share_by_policy",
}
ALLOWED_VETO_TRACE_FIELDS = REQUIRED_VETO_TRACE_FIELDS
ALLOWED_REPLAY_METRICS_FIELDS = REQUIRED_REPLAY_METRICS_FIELDS | {
    "router_version",
    "field_allowlist_version",
    "metrics_semantics_version",
    "not_used_for_routing",
}
ALLOWED_MANIFEST_FIELDS = {
    "field_allowlist_version",
    "router_version",
    "veto_version",
    "metrics_semantics_version",
    "approved_output_dir",
    "approved_output_files",
    "written_files",
    "input_hashes",
    "output_hashes",
    "observational_only",
    "recommendation_scope",
    "containment",
    "row_count",
    "recommendation",
}


def _find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if all((candidate / marker).exists() for marker in ROOT_REQUIRED_MARKERS):
            return candidate
    raise RuntimeError("Could not locate repository root")


ROOT_DIR = _find_repo_root(Path(__file__).resolve())
REPLAY_ROOT = ROOT_DIR / "results" / "research" / "scpe_v1_ri"
OUTPUT_PATH = ROOT_DIR / "results" / "evaluation" / "scpe_ri_v1_router_diagnostics_2026-04-20.json"
ROUTING_TRACE_PATH = REPLAY_ROOT / "routing_trace.ndjson"
POLICY_TRACE_PATH = REPLAY_ROOT / "policy_trace.json"
VETO_TRACE_PATH = REPLAY_ROOT / "veto_trace.json"
REPLAY_METRICS_PATH = REPLAY_ROOT / "replay_metrics.json"
MANIFEST_PATH = REPLAY_ROOT / "manifest.json"
SUMMARY_PATH = REPLAY_ROOT / "summary.md"

INPUT_PATHS = [
    ROUTING_TRACE_PATH,
    POLICY_TRACE_PATH,
    VETO_TRACE_PATH,
    REPLAY_METRICS_PATH,
    MANIFEST_PATH,
    SUMMARY_PATH,
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


def _require_exact_keys(payload: dict[str, Any], allowed: set[str], label: str) -> None:
    unexpected = sorted(set(payload) - allowed)
    if unexpected:
        raise RuntimeError(f"{label} has unexpected keys: {unexpected}")


def _as_float(value: Any, label: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"{label} must be numeric, got {value!r}") from exc


def _round_or_none(value: float | None) -> float | None:
    return None if value is None else round(value, 6)


def _counter_dict(counter: Counter[str]) -> dict[str, int]:
    return dict(sorted(counter.items()))


def _policy_rows(trace_rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in trace_rows:
        grouped[str(row["selected_policy"])].append(row)
    return dict(grouped)


def _distribution(
    rows: list[dict[str, Any]], getter: str, nested: str | None = None
) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for row in rows:
        value = row[getter] if nested is None else row[getter][nested]
        counter[str(value)] += 1
    return _counter_dict(counter)


def _average(values: list[float]) -> float | None:
    return None if not values else round(mean(values), 6)


def _build_policy_summary(trace_rows: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for policy, rows in sorted(_policy_rows(trace_rows).items()):
        trades = [row for row in rows if row["final_routed_action"] != FINAL_ACTION_NONE]
        forced_no_trade = [
            row
            for row in rows
            if row["selected_policy"] != POLICY_NO_TRADE
            and row["final_routed_action"] == FINAL_ACTION_NONE
        ]
        non_pass_veto = [row for row in rows if row["veto_action"] != "pass"]
        summary[policy] = {
            "row_count": len(rows),
            "row_share": round(len(rows) / len(trace_rows), 6),
            "trade_count": len(trades),
            "forced_no_trade_count": len(forced_no_trade),
            "non_pass_veto_count": len(non_pass_veto),
            "non_pass_veto_rate": round(len(non_pass_veto) / len(rows), 6),
            "avg_clarity_score": _average(
                [_as_float(row["ri_state"]["ri_clarity_score"], "ri_clarity_score") for row in rows]
            ),
            "avg_conf_overall": _average(
                [_as_float(row["ri_state"]["conf_overall"], "conf_overall") for row in rows]
            ),
            "avg_action_edge": _average(
                [_as_float(row["ri_state"]["action_edge"], "action_edge") for row in rows]
            ),
            "avg_bars_since_regime_change": _average(
                [
                    _as_float(
                        row["ri_state"]["bars_since_regime_change"],
                        "bars_since_regime_change",
                    )
                    for row in rows
                ]
            ),
            "transition_bucket_counts": _distribution(rows, "ri_state", "transition_bucket"),
            "clarity_bucket_counts": _distribution(rows, "ri_state", "clarity_bucket"),
            "confidence_bucket_counts": _distribution(rows, "ri_state", "confidence_bucket"),
            "zone_counts": _distribution(rows, "core_state", "zone"),
            "veto_action_counts": _distribution(rows, "veto_action"),
            "veto_reason_counts": _distribution(rows, "veto_reason"),
        }
    return summary


def _build_switch_summary(trace_rows: list[dict[str, Any]]) -> dict[str, Any]:
    proposed_rows = [row for row in trace_rows if bool(row["switch_proposed"])]
    blocked_rows = [row for row in trace_rows if bool(row["switch_blocked"])]
    actual_changes = sum(
        1
        for previous_row, current_row in zip(trace_rows, trace_rows[1:], strict=False)
        if previous_row["selected_policy"] != current_row["selected_policy"]
    )
    blocked_reasons = Counter(str(row["switch_reason"]) for row in blocked_rows)
    proposed_reasons = Counter(str(row["switch_reason"]) for row in proposed_rows)
    return {
        "proposed_switch_count": len(proposed_rows),
        "blocked_switch_count": len(blocked_rows),
        "actual_policy_change_count": actual_changes,
        "blocked_share_of_proposed": _round_or_none(
            None if not proposed_rows else len(blocked_rows) / len(proposed_rows)
        ),
        "actual_change_share_of_proposed": _round_or_none(
            None if not proposed_rows else actual_changes / len(proposed_rows)
        ),
        "blocked_reason_counts": _counter_dict(blocked_reasons),
        "proposed_reason_counts": _counter_dict(proposed_reasons),
        "blocked_previous_policy_counts": _counter_dict(
            Counter(str(row["previous_policy"]) for row in blocked_rows)
        ),
    }


def _build_no_trade_summary(trace_rows: list[dict[str, Any]]) -> dict[str, Any]:
    router_selected_no_trade = [
        row for row in trace_rows if row["selected_policy"] == POLICY_NO_TRADE
    ]
    veto_forced_no_trade = [
        row
        for row in trace_rows
        if row["selected_policy"] != POLICY_NO_TRADE
        and row["final_routed_action"] == FINAL_ACTION_NONE
    ]
    total_final_no_trade = [
        row for row in trace_rows if row["final_routed_action"] == FINAL_ACTION_NONE
    ]
    return {
        "router_selected_no_trade_rows": len(router_selected_no_trade),
        "veto_forced_no_trade_on_non_no_trade_rows": len(veto_forced_no_trade),
        "total_final_no_trade_rows": len(total_final_no_trade),
        "router_selected_share_of_final_no_trade": _round_or_none(
            None
            if not total_final_no_trade
            else len(router_selected_no_trade) / len(total_final_no_trade)
        ),
        "veto_forced_share_of_final_no_trade": _round_or_none(
            None
            if not total_final_no_trade
            else len(veto_forced_no_trade) / len(total_final_no_trade)
        ),
        "forced_no_trade_by_selected_policy": _counter_dict(
            Counter(str(row["selected_policy"]) for row in veto_forced_no_trade)
        ),
    }


def _build_veto_summary(trace_rows: list[dict[str, Any]]) -> dict[str, Any]:
    action_counts = Counter(str(row["veto_action"]) for row in trace_rows)
    reason_counts = Counter(str(row["veto_reason"]) for row in trace_rows)
    by_policy = {}
    for policy, rows in sorted(_policy_rows(trace_rows).items()):
        non_pass_count = sum(1 for row in rows if row["veto_action"] != "pass")
        force_no_trade_count = sum(1 for row in rows if row["veto_action"] == "force_no_trade")
        by_policy[policy] = {
            "non_pass_veto_rate": round(non_pass_count / len(rows), 6),
            "force_no_trade_rate": round(force_no_trade_count / len(rows), 6),
        }
    return {
        "action_counts": _counter_dict(action_counts),
        "reason_counts": _counter_dict(reason_counts),
        "non_pass_veto_rows": sum(
            count for action, count in action_counts.items() if action != "pass"
        ),
        "non_pass_veto_rate": round(
            sum(count for action, count in action_counts.items() if action != "pass")
            / len(trace_rows),
            6,
        ),
        "by_selected_policy": by_policy,
    }


def _build_distinctness_summary(
    trace_rows: list[dict[str, Any]], policy_summary: dict[str, Any]
) -> dict[str, Any]:
    continuation = policy_summary.get(POLICY_CONTINUATION)
    defensive = policy_summary.get(POLICY_DEFENSIVE)
    if continuation is None or defensive is None:
        raise RuntimeError("Expected continuation and defensive policy summaries to exist")

    defensive_rows = _policy_rows(trace_rows).get(POLICY_DEFENSIVE, [])
    continuation_rows = _policy_rows(trace_rows).get(POLICY_CONTINUATION, [])

    defensive_transition_heavy = sum(
        1 for row in defensive_rows if row["ri_state"]["transition_bucket"] in {"acute", "recent"}
    )
    continuation_transition_heavy = sum(
        1
        for row in continuation_rows
        if row["ri_state"]["transition_bucket"] in {"acute", "recent"}
    )

    sample_status = "sample_insufficient" if defensive["row_count"] < 10 else "sample_adequate"
    transition_share_defensive = _round_or_none(
        None if not defensive_rows else defensive_transition_heavy / len(defensive_rows)
    )
    transition_share_continuation = _round_or_none(
        None if not continuation_rows else continuation_transition_heavy / len(continuation_rows)
    )

    return {
        "defensive_sample_status": sample_status,
        "defensive_row_count": defensive["row_count"],
        "defensive_row_share": defensive["row_share"],
        "defensive_trade_count": defensive["trade_count"],
        "transition_heavy_share": {
            POLICY_DEFENSIVE: transition_share_defensive,
            POLICY_CONTINUATION: transition_share_continuation,
        },
        "avg_metric_delta_defensive_minus_continuation": {
            "clarity_score": round(
                defensive["avg_clarity_score"] - continuation["avg_clarity_score"],
                6,
            ),
            "conf_overall": round(
                defensive["avg_conf_overall"] - continuation["avg_conf_overall"],
                6,
            ),
            "action_edge": round(
                defensive["avg_action_edge"] - continuation["avg_action_edge"],
                6,
            ),
            "bars_since_regime_change": round(
                defensive["avg_bars_since_regime_change"]
                - continuation["avg_bars_since_regime_change"],
                6,
            ),
        },
    }


def _build_findings(
    trace_rows: list[dict[str, Any]],
    policy_summary: dict[str, Any],
    switch_summary: dict[str, Any],
    no_trade_summary: dict[str, Any],
    distinctness_summary: dict[str, Any],
) -> list[str]:
    findings: list[str] = []
    defensive = policy_summary[POLICY_DEFENSIVE]
    continuation = policy_summary[POLICY_CONTINUATION]

    findings.append(
        "Defensive policy support is sparse: "
        f"{defensive['row_count']} rows ({defensive['row_share']}) and {defensive['trade_count']} trades."
    )

    if switch_summary["blocked_reason_counts"]:
        top_reason, top_count = max(
            switch_summary["blocked_reason_counts"].items(), key=lambda item: item[1]
        )
        findings.append(
            "Blocked switches are dominated by explicit stability controls: "
            f"{top_reason} accounts for {top_count} of {switch_summary['blocked_switch_count']} blocked rows."
        )

    findings.append(
        "Final no-trade is driven primarily by direct router no-trade selection rather than downstream veto: "
        f"{no_trade_summary['router_selected_no_trade_rows']} of {no_trade_summary['total_final_no_trade_rows']} final no-trade rows "
        "come from `RI_no_trade_policy`."
    )

    findings.append(
        "Continuation remains the dominant routed posture: "
        f"{continuation['row_count']} rows ({continuation['row_share']}) with non-pass veto rate {continuation['non_pass_veto_rate']}."
    )

    findings.append(
        "Defensive state evidence differs structurally from continuation, but the sample remains too small for strong distinctness claims: "
        f"transition-heavy share {distinctness_summary['transition_heavy_share'][POLICY_DEFENSIVE]} vs "
        f"{distinctness_summary['transition_heavy_share'][POLICY_CONTINUATION]}."
    )
    return findings


def _validate_inputs(
    trace_rows: list[dict[str, Any]],
    policy_trace: dict[str, Any],
    veto_trace: dict[str, Any],
    replay_metrics: dict[str, Any],
    replay_manifest: dict[str, Any],
) -> None:
    for index, row in enumerate(trace_rows, start=1):
        _require_keys(row, REQUIRED_TRACE_FIELDS, f"routing_trace row {index}")
        _require_exact_keys(row, ALLOWED_TRACE_FIELDS, f"routing_trace row {index}")
        _require_keys(
            row["ri_state"], REQUIRED_RI_STATE_FIELDS, f"routing_trace row {index}.ri_state"
        )
        _require_exact_keys(
            row["ri_state"],
            ALLOWED_RI_STATE_FIELDS,
            f"routing_trace row {index}.ri_state",
        )
        if str(row["family_tag"]) != "RI":
            raise RuntimeError(
                f"routing_trace row {index} has unexpected family_tag {row['family_tag']!r}"
            )

    _require_keys(policy_trace, REQUIRED_POLICY_TRACE_FIELDS, "policy_trace")
    _require_exact_keys(policy_trace, ALLOWED_POLICY_TRACE_FIELDS, "policy_trace")
    _require_keys(veto_trace, REQUIRED_VETO_TRACE_FIELDS, "veto_trace")
    _require_exact_keys(veto_trace, ALLOWED_VETO_TRACE_FIELDS, "veto_trace")
    _require_keys(replay_metrics, REQUIRED_REPLAY_METRICS_FIELDS, "replay_metrics")
    _require_exact_keys(replay_metrics, ALLOWED_REPLAY_METRICS_FIELDS, "replay_metrics")
    _require_keys(
        replay_manifest, {"containment", "recommendation", "recommendation_scope"}, "manifest"
    )
    _require_exact_keys(replay_manifest, ALLOWED_MANIFEST_FIELDS, "manifest")

    if replay_metrics["observational_only"] is not True:
        raise RuntimeError("replay_metrics observational_only must remain true")
    if replay_metrics["recommendation"] != "NEEDS_REVISION":
        raise RuntimeError(
            "Diagnostics slice must not upgrade or reinterpret the replay recommendation; "
            f"expected NEEDS_REVISION, got {replay_metrics['recommendation']!r}"
        )


def main() -> int:
    pre_snapshot = _snapshot_paths([REPLAY_ROOT])

    trace_rows = _load_ndjson(ROUTING_TRACE_PATH)
    policy_trace = _load_json(POLICY_TRACE_PATH)
    veto_trace = _load_json(VETO_TRACE_PATH)
    replay_metrics = _load_json(REPLAY_METRICS_PATH)
    replay_manifest = _load_json(MANIFEST_PATH)

    _validate_inputs(trace_rows, policy_trace, veto_trace, replay_metrics, replay_manifest)

    policy_summary = _build_policy_summary(trace_rows)
    switch_summary = _build_switch_summary(trace_rows)
    no_trade_summary = _build_no_trade_summary(trace_rows)
    veto_summary = _build_veto_summary(trace_rows)
    distinctness_summary = _build_distinctness_summary(trace_rows, policy_summary)
    findings = _build_findings(
        trace_rows,
        policy_summary,
        switch_summary,
        no_trade_summary,
        distinctness_summary,
    )

    payload = {
        "date": "2026-04-20",
        "branch": "feature/ri-role-map-implementation-2026-03-24",
        "mode": "RESEARCH",
        "status": "diagnostics-generated",
        "diagnostics_version": DIAGNOSTICS_VERSION,
        "source_replay_root": _relative_path(REPLAY_ROOT),
        "observational_only": True,
        "summary_only": True,
        "non_authoritative": True,
        "recommendation_passthrough": replay_metrics["recommendation"],
        "recommendation_scope": replay_metrics["recommendation_scope"],
        "recommendation_change_attempted": False,
        "row_count": len(trace_rows),
        "source_hashes": {_relative_path(path): _sha256_file(path) for path in INPUT_PATHS},
        "policy_summary": policy_summary,
        "switch_summary": switch_summary,
        "no_trade_summary": no_trade_summary,
        "veto_summary": veto_summary,
        "distinctness_summary": distinctness_summary,
        "findings": findings,
        "upstream_reference": {
            "replay_metrics_recommendation": replay_metrics["recommendation"],
            "replay_manifest_recommendation": replay_manifest.get("recommendation"),
            "replay_manifest_containment_verdict": replay_manifest.get("containment", {}).get(
                "verdict"
            ),
        },
    }
    _write_json(OUTPUT_PATH, payload)

    post_snapshot = _snapshot_paths([REPLAY_ROOT])
    replay_root_diff = _diff_snapshots(pre_snapshot, post_snapshot)
    if replay_root_diff:
        raise RuntimeError(
            "Replay root changed during diagnostics run: "
            + json.dumps(replay_root_diff, ensure_ascii=False, indent=2)
        )

    print(f"[OK] Wrote diagnostics artifact: {OUTPUT_PATH}")
    print(f"[OK] Row count: {len(trace_rows)}")
    print(f"[OK] Replay recommendation preserved: {replay_metrics['recommendation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
