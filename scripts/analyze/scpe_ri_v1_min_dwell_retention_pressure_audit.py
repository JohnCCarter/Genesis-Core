#!/usr/bin/env python3
"""Observational min-dwell retention pressure audit for frozen RI replay evidence.

This script is RESEARCH-only and observational-only. It profiles the raw defensive
candidates that are retained in no-trade via `switch_blocked_by_min_dwell` using a
research-side analytical mirror of the existing replay behavior. It does not modify
canonical replay logic or propose a new dwell rule.
"""

from __future__ import annotations

import hashlib
import json
import runpy
from collections import Counter
from pathlib import Path
from typing import Any


ROOT_REQUIRED_MARKERS = ("pyproject.toml", "src")
AUDIT_VERSION = "scpe-ri-v1-min-dwell-retention-pressure-audit-2026-04-20"
POLICY_CONTINUATION = "RI_continuation_policy"
POLICY_DEFENSIVE = "RI_defensive_transition_policy"
POLICY_NO_TRADE = "RI_no_trade_policy"

EXPECTED_FROZEN_HASHES = {
    "entry_rows": "a8712bf723444269576fa5fc8363b7c7d680b654fe79ded8cc6dd17df5c6857a",  # pragma: allowlist secret
    "routing_trace": "d01ebc7457da902fcdcff93ea78eadf5036be464908a2b45c0cdb7bfb0f61da8",  # pragma: allowlist secret
    "replay_metrics": "f46cc0e1fb0418b6fe8b1759571cb9e967343595c9be85378d09e28492dcfe60",  # pragma: allowlist secret
    "replay_manifest": "273f16d3247e71327d15aeecac2ecdbed37238b9133fb7aefe45450a5b59b322",  # pragma: allowlist secret
    "replay_script_reference": "6f9d93f26ab5544a51cd1546f68f405596ad82e5341dbe8c352eba049b462b06",  # pragma: allowlist secret
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

METRIC_FIELDS = [
    "ri_clarity_score",
    "conf_overall",
    "action_edge",
    "bars_since_regime_change",
]

SELECTOR_DEFINITIONS = {
    "raw_defensive_candidates": "raw target policy = RI_defensive_transition_policy",
    "min_dwell_retained": (
        "raw target policy = RI_defensive_transition_policy AND "
        "selected_policy = RI_no_trade_policy AND switch_reason = switch_blocked_by_min_dwell"
    ),
    "threshold_retained": (
        "raw target policy = RI_defensive_transition_policy AND "
        "selected_policy = RI_continuation_policy AND switch_reason = confidence_below_threshold"
    ),
    "selected_defensive": (
        "raw target policy = RI_defensive_transition_policy AND "
        "selected_policy = RI_defensive_transition_policy"
    ),
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
ROUTING_TRACE_PATH = ROOT_DIR / "results" / "research" / "scpe_v1_ri" / "routing_trace.ndjson"
REPLAY_METRICS_PATH = ROOT_DIR / "results" / "research" / "scpe_v1_ri" / "replay_metrics.json"
MANIFEST_PATH = ROOT_DIR / "results" / "research" / "scpe_v1_ri" / "manifest.json"
REPLAY_SCRIPT_PATH = ROOT_DIR / "scripts" / "analyze" / "scpe_ri_v1_router_replay.py"
OUTPUT_PATH = (
    ROOT_DIR
    / "results"
    / "evaluation"
    / "scpe_ri_v1_min_dwell_retention_pressure_audit_2026-04-20.json"
)
INPUT_PATHS = {
    "entry_rows": ENTRY_ROWS_PATH,
    "routing_trace": ROUTING_TRACE_PATH,
    "replay_metrics": REPLAY_METRICS_PATH,
    "replay_manifest": MANIFEST_PATH,
    "replay_script_reference": REPLAY_SCRIPT_PATH,
}


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


def _round6(value: float) -> float:
    return round(float(value), 6)


def _validate_frozen_inputs() -> dict[str, dict[str, str]]:
    observed: dict[str, dict[str, str]] = {}
    for label, path in INPUT_PATHS.items():
        actual = _sha256_file(path)
        observed[label] = {"path": _relative_path(path), "sha256": actual}
        expected = EXPECTED_FROZEN_HASHES[label]
        if actual != expected:
            raise RuntimeError(
                f"Frozen input hash mismatch for {label}: expected {expected}, observed {actual}"
            )
    return observed


def _build_candidate_row(
    index: int,
    core: dict[str, Any],
    ri: dict[str, Any],
    raw_decision: dict[str, Any],
    trace_row: dict[str, Any],
) -> dict[str, Any]:
    return {
        "row_index": index,
        "timestamp": str(trace_row["timestamp"]),
        "selected_policy": str(trace_row["selected_policy"]),
        "switch_reason": str(trace_row["switch_reason"]),
        "veto_reason": str(trace_row["veto_reason"]),
        "veto_action": str(trace_row["veto_action"]),
        "final_routed_action": str(trace_row["final_routed_action"]),
        "raw_switch_reason": str(raw_decision["raw_switch_reason"]),
        "raw_mandate_level": int(raw_decision["mandate_level"]),
        "zone": str(core["zone"]),
        "transition_bucket": str(ri["transition_bucket"]),
        "ri_clarity_score": _round6(ri["ri_clarity_score"]),
        "conf_overall": _round6(ri["conf_overall"]),
        "action_edge": _round6(ri["action_edge"]),
        "bars_since_regime_change": _round6(ri["bars_since_regime_change"]),
    }


def _sort_examples(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda item: (
            -float(item["action_edge"]),
            -float(item["conf_overall"]),
            -float(item["ri_clarity_score"]),
            int(item["row_index"]),
        ),
    )


def _metric_summary(rows: list[dict[str, Any]]) -> dict[str, float | None]:
    summary: dict[str, float | None] = {}
    for field in METRIC_FIELDS:
        if not rows:
            summary[f"avg_{field}"] = None
            summary[f"min_{field}"] = None
            summary[f"max_{field}"] = None
            continue
        values = [float(row[field]) for row in rows]
        summary[f"avg_{field}"] = _round6(sum(values) / len(values))
        summary[f"min_{field}"] = _round6(min(values))
        summary[f"max_{field}"] = _round6(max(values))
    return summary


def _bucket_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "count": len(rows),
        **_metric_summary(rows),
        "zone_counts": _counter_dict(Counter(str(row["zone"]) for row in rows)),
        "transition_bucket_counts": _counter_dict(
            Counter(str(row["transition_bucket"]) for row in rows)
        ),
        "selected_policy_counts": _counter_dict(
            Counter(str(row["selected_policy"]) for row in rows)
        ),
        "switch_reason_counts": _counter_dict(Counter(str(row["switch_reason"]) for row in rows)),
        "veto_reason_counts": _counter_dict(Counter(str(row["veto_reason"]) for row in rows)),
        "raw_switch_reason_counts": _counter_dict(
            Counter(str(row["raw_switch_reason"]) for row in rows)
        ),
        "raw_mandate_level_counts": _counter_dict(
            Counter(str(row["raw_mandate_level"]) for row in rows)
        ),
    }


def _delta_summary(primary: dict[str, Any], comparator: dict[str, Any]) -> dict[str, float | None]:
    deltas: dict[str, float | None] = {}
    for field in METRIC_FIELDS:
        primary_avg = primary.get(f"avg_{field}")
        comparator_avg = comparator.get(f"avg_{field}")
        if primary_avg is None or comparator_avg is None:
            deltas[f"delta_avg_{field}"] = None
        else:
            deltas[f"delta_avg_{field}"] = _round6(float(primary_avg) - float(comparator_avg))
    return deltas


def main() -> int:
    replay_pre_snapshot = _snapshot_paths([ROOT_DIR / "results" / "research" / "scpe_v1_ri"])

    frozen_inputs = _validate_frozen_inputs()
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

    raw_defensive_rows: list[dict[str, Any]] = []
    min_dwell_retained_rows: list[dict[str, Any]] = []
    threshold_retained_rows: list[dict[str, Any]] = []
    selected_defensive_rows: list[dict[str, Any]] = []

    for index, (entry_row, trace_row) in enumerate(
        zip(entry_rows, trace_rows, strict=False), start=1
    ):
        _require_keys(trace_row, REQUIRED_TRACE_FIELDS, f"routing_trace row {index}")
        if str(entry_row.get("timestamp")) != str(trace_row.get("timestamp")):
            raise RuntimeError(
                f"Row identity drift at index {index}: entry timestamp {entry_row.get('timestamp')!r} "
                f"!= trace timestamp {trace_row.get('timestamp')!r}"
            )
        core = replay_ns["_derive_core_state"](entry_row, index)
        ri = replay_ns["_derive_ri_state"](entry_row, core, index)
        raw_decision = replay_ns["_build_raw_router_decision"](core, ri)
        if raw_decision["target_policy"] != POLICY_DEFENSIVE:
            continue

        candidate = _build_candidate_row(index, core, ri, raw_decision, trace_row)
        raw_defensive_rows.append(candidate)

        if (
            candidate["selected_policy"] == POLICY_NO_TRADE
            and candidate["switch_reason"] == "switch_blocked_by_min_dwell"
        ):
            min_dwell_retained_rows.append(candidate)
        if (
            candidate["selected_policy"] == POLICY_CONTINUATION
            and candidate["switch_reason"] == "confidence_below_threshold"
        ):
            threshold_retained_rows.append(candidate)
        if candidate["selected_policy"] == POLICY_DEFENSIVE:
            selected_defensive_rows.append(candidate)

    comparator_summaries = {
        "raw_defensive_candidates": _bucket_summary(raw_defensive_rows),
        "min_dwell_retained": _bucket_summary(min_dwell_retained_rows),
        "threshold_retained": _bucket_summary(threshold_retained_rows),
        "selected_defensive": _bucket_summary(selected_defensive_rows),
    }

    payload = {
        "date": "2026-04-20",
        "branch": "feature/ri-role-map-implementation-2026-03-24",
        "mode": "RESEARCH",
        "status": "min-dwell-retention-pressure-audit-generated",
        "audit_version": AUDIT_VERSION,
        "observational_only": True,
        "summary_only": True,
        "non_authoritative": True,
        "recommendation_change": "none",
        "read_only_inputs_confirmed": True,
        "selector_definitions": SELECTOR_DEFINITIONS,
        "frozen_inputs": frozen_inputs,
        "source_hashes": {
            _relative_path(Path(__file__).resolve()): _sha256_file(Path(__file__).resolve())
        },
        "baseline_recommendation_passthrough": str(replay_metrics["recommendation"]),
        "baseline_recommendation_scope": str(replay_metrics["recommendation_scope"]),
        "comparator_summaries": comparator_summaries,
        "min_dwell_examples_sorted": _sort_examples(min_dwell_retained_rows)[:5],
        "comparison_deltas": {
            "min_dwell_vs_raw_defensive": _delta_summary(
                comparator_summaries["min_dwell_retained"],
                comparator_summaries["raw_defensive_candidates"],
            ),
            "min_dwell_vs_threshold": _delta_summary(
                comparator_summaries["min_dwell_retained"],
                comparator_summaries["threshold_retained"],
            ),
            "min_dwell_vs_selected_defensive": _delta_summary(
                comparator_summaries["min_dwell_retained"],
                comparator_summaries["selected_defensive"],
            ),
        },
        "descriptive_guardrails": {
            "report_only_interpretation_labels": [
                "near-miss",
                "materially weaker",
                "mixed",
                "overlapping",
            ],
            "script_emits_metrics_only": True,
            "no_dwell_rule_proposal": True,
            "no_replay_quality_reinterpretation": True,
        },
        "findings": [
            "Min-dwell-retained rows are emitted as a descriptive comparator bucket only; the script does not classify them as near-miss or materially weaker.",
            "Comparator cohorts are derived from the same frozen reconstruction surface and do not define an alternative acceptance policy.",
            "The report may interpret the emitted metric deltas, but the artifact remains non-authoritative and observational-only.",
        ],
    }

    _write_json(OUTPUT_PATH, payload)

    replay_post_snapshot = _snapshot_paths([ROOT_DIR / "results" / "research" / "scpe_v1_ri"])
    replay_root_diff = _diff_snapshots(replay_pre_snapshot, replay_post_snapshot)
    if replay_root_diff:
        raise RuntimeError(
            "Baseline replay root changed during min-dwell retention pressure audit: "
            + json.dumps(replay_root_diff, ensure_ascii=False, indent=2)
        )

    print(f"[OK] Wrote min-dwell retention pressure artifact: {OUTPUT_PATH}")
    print(f"[OK] Min-dwell-retained rows: {len(min_dwell_retained_rows)}")
    print(f"[OK] Threshold-retained comparator rows: {len(threshold_retained_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
