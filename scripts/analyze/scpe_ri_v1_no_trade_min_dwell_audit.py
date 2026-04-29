#!/usr/bin/env python3
"""Summary-only audit of RI no-trade persistence and min-dwell lock behavior.

This script is research-only and read-only with respect to the replay root. It audits
how often the replay remains in `RI_no_trade_policy`, how often attempted exits are
blocked by `min_dwell`, and what descriptive state differences appear between blocked
and successful no-trade exits.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from statistics import mean, median
from typing import Any


POLICY_NO_TRADE = "RI_no_trade_policy"
ROOT_REQUIRED_MARKERS = ("pyproject.toml", "src")
AUDIT_VERSION = "scpe-ri-v1-no-trade-min-dwell-audit-2026-04-20"

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
REQUIRED_CORE_STATE_FIELDS = {"side", "zone", "htf_regime", "current_atr_used", "atr_period_used"}
REQUIRED_POLICY_TRACE_FIELDS = {
    "policy_counts",
    "switch_reason_counts",
    "proposed_switch_count",
    "blocked_switch_count",
    "actual_policy_change_count",
    "actual_policy_change_rate",
    "segments",
}
REQUIRED_REPLAY_METRICS_FIELDS = {
    "observational_only",
    "recommendation",
    "recommendation_scope",
    "routing_metrics",
    "observational_metrics",
}
REQUIRED_MANIFEST_FIELDS = {"containment", "recommendation", "recommendation_scope", "row_count"}
ALLOWED_TRACE_FIELDS = REQUIRED_TRACE_FIELDS
ALLOWED_RI_STATE_FIELDS = REQUIRED_RI_STATE_FIELDS
ALLOWED_CORE_STATE_FIELDS = REQUIRED_CORE_STATE_FIELDS
ALLOWED_POLICY_TRACE_FIELDS = REQUIRED_POLICY_TRACE_FIELDS | {
    "router_version",
    "metrics_semantics_version",
    "no_trade_count",
    "average_dwell_by_policy",
    "blocked_switch_rate",
    "proposed_switch_rate",
    "time_share_by_policy",
}
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
OUTPUT_PATH = (
    ROOT_DIR / "results" / "evaluation" / "scpe_ri_v1_no_trade_min_dwell_audit_2026-04-20.json"
)
ROUTING_TRACE_PATH = REPLAY_ROOT / "routing_trace.ndjson"
POLICY_TRACE_PATH = REPLAY_ROOT / "policy_trace.json"
REPLAY_METRICS_PATH = REPLAY_ROOT / "replay_metrics.json"
MANIFEST_PATH = REPLAY_ROOT / "manifest.json"
INPUT_PATHS = [
    ROUTING_TRACE_PATH,
    POLICY_TRACE_PATH,
    REPLAY_METRICS_PATH,
    MANIFEST_PATH,
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


def _length_stats(lengths: list[int]) -> dict[str, Any]:
    if not lengths:
        return {"count": 0, "min": None, "median": None, "mean": None, "max": None, "histogram": {}}
    return {
        "count": len(lengths),
        "min": min(lengths),
        "median": int(median(lengths)),
        "mean": round(mean(lengths), 6),
        "max": max(lengths),
        "histogram": _counter_dict(Counter(str(length) for length in lengths)),
    }


def _bucket_distribution(rows: list[dict[str, Any]], family: str, key: str) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for row in rows:
        counter[str(row[family][key])] += 1
    return _counter_dict(counter)


def _state_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {
            "count": 0,
            "avg_clarity_score": None,
            "avg_conf_overall": None,
            "avg_action_edge": None,
            "avg_bars_since_regime_change": None,
            "clarity_bucket_counts": {},
            "confidence_bucket_counts": {},
            "transition_bucket_counts": {},
            "edge_bucket_counts": {},
            "zone_counts": {},
            "year_counts": {},
        }
    return {
        "count": len(rows),
        "avg_clarity_score": round(
            mean(
                _as_float(row["ri_state"]["ri_clarity_score"], "ri_clarity_score") for row in rows
            ),
            6,
        ),
        "avg_conf_overall": round(
            mean(_as_float(row["ri_state"]["conf_overall"], "conf_overall") for row in rows), 6
        ),
        "avg_action_edge": round(
            mean(_as_float(row["ri_state"]["action_edge"], "action_edge") for row in rows), 6
        ),
        "avg_bars_since_regime_change": round(
            mean(
                _as_float(row["ri_state"]["bars_since_regime_change"], "bars_since_regime_change")
                for row in rows
            ),
            6,
        ),
        "clarity_bucket_counts": _bucket_distribution(rows, "ri_state", "clarity_bucket"),
        "confidence_bucket_counts": _bucket_distribution(rows, "ri_state", "confidence_bucket"),
        "transition_bucket_counts": _bucket_distribution(rows, "ri_state", "transition_bucket"),
        "edge_bucket_counts": _bucket_distribution(rows, "ri_state", "edge_bucket"),
        "zone_counts": _bucket_distribution(rows, "core_state", "zone"),
        "year_counts": _counter_dict(Counter(str(row["year"]) for row in rows)),
    }


def _validate_inputs(
    trace_rows: list[dict[str, Any]],
    policy_trace: dict[str, Any],
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
            row["ri_state"], ALLOWED_RI_STATE_FIELDS, f"routing_trace row {index}.ri_state"
        )
        _require_keys(
            row["core_state"], REQUIRED_CORE_STATE_FIELDS, f"routing_trace row {index}.core_state"
        )
        _require_exact_keys(
            row["core_state"], ALLOWED_CORE_STATE_FIELDS, f"routing_trace row {index}.core_state"
        )
        if str(row["family_tag"]) != "RI":
            raise RuntimeError(
                f"routing_trace row {index} has unexpected family_tag {row['family_tag']!r}"
            )

    _require_keys(policy_trace, REQUIRED_POLICY_TRACE_FIELDS, "policy_trace")
    _require_exact_keys(policy_trace, ALLOWED_POLICY_TRACE_FIELDS, "policy_trace")
    _require_keys(replay_metrics, REQUIRED_REPLAY_METRICS_FIELDS, "replay_metrics")
    _require_exact_keys(replay_metrics, ALLOWED_REPLAY_METRICS_FIELDS, "replay_metrics")
    _require_keys(replay_manifest, REQUIRED_MANIFEST_FIELDS, "manifest")
    _require_exact_keys(replay_manifest, ALLOWED_MANIFEST_FIELDS, "manifest")

    if replay_metrics["observational_only"] is not True:
        raise RuntimeError("replay_metrics observational_only must remain true")
    if replay_metrics["recommendation"] != "NEEDS_REVISION":
        raise RuntimeError(
            "Audit slice must not upgrade or reinterpret the replay recommendation; "
            f"expected NEEDS_REVISION, got {replay_metrics['recommendation']!r}"
        )


def _no_trade_segments(policy_trace: dict[str, Any]) -> list[dict[str, Any]]:
    segments = policy_trace["segments"]
    if not isinstance(segments, list):
        raise RuntimeError("policy_trace segments must be a list")
    return [segment for segment in segments if segment.get("policy") == POLICY_NO_TRADE]


def _build_findings(
    no_trade_segment_lengths: list[int],
    blocked_exit_rows: list[dict[str, Any]],
    successful_exit_rows: list[dict[str, Any]],
    quiet_stay_rows: list[dict[str, Any]],
    previous_no_trade_rows: list[dict[str, Any]],
) -> list[str]:
    findings: list[str] = []
    findings.append(
        "No-trade persistence is episodic rather than a single monolith: "
        f"{len(no_trade_segment_lengths)} no-trade segments span {sum(no_trade_segment_lengths)} rows."
    )
    findings.append(
        "Rows following a previous no-trade state are dominated by blocked or quiet persistence rather than releases: "
        f"blocked={len(blocked_exit_rows)}, successful_exit={len(successful_exit_rows)}, quiet_stay={len(quiet_stay_rows)}."
    )
    findings.append(
        "Blocked exits from no-trade are explicitly min-dwell bound by construction in this slice: "
        f"{len(blocked_exit_rows)} rows match `switch_blocked_by_min_dwell` while staying in `RI_no_trade_policy`."
    )
    findings.append(
        "Successful exits from no-trade are sparse relative to all rows with previous no-trade: "
        f"{len(successful_exit_rows)} of {len(previous_no_trade_rows)} previous-no-trade rows release to another policy."
    )
    return findings


def main() -> int:
    pre_snapshot = _snapshot_paths([REPLAY_ROOT])

    trace_rows = _load_ndjson(ROUTING_TRACE_PATH)
    policy_trace = _load_json(POLICY_TRACE_PATH)
    replay_metrics = _load_json(REPLAY_METRICS_PATH)
    replay_manifest = _load_json(MANIFEST_PATH)

    _validate_inputs(trace_rows, policy_trace, replay_metrics, replay_manifest)

    no_trade_segments = _no_trade_segments(policy_trace)
    no_trade_segment_lengths = [int(segment["count"]) for segment in no_trade_segments]

    previous_no_trade_rows = [
        row for row in trace_rows if row["previous_policy"] == POLICY_NO_TRADE
    ]
    blocked_exit_rows = [
        row
        for row in previous_no_trade_rows
        if row["selected_policy"] == POLICY_NO_TRADE
        and bool(row["switch_proposed"])
        and bool(row["switch_blocked"])
        and row["switch_reason"] == "switch_blocked_by_min_dwell"
    ]
    successful_exit_rows = [
        row for row in previous_no_trade_rows if row["selected_policy"] != POLICY_NO_TRADE
    ]
    quiet_stay_rows = [
        row
        for row in previous_no_trade_rows
        if row["selected_policy"] == POLICY_NO_TRADE and not bool(row["switch_proposed"])
    ]
    other_previous_no_trade_rows = [
        row
        for row in previous_no_trade_rows
        if row not in blocked_exit_rows
        and row not in successful_exit_rows
        and row not in quiet_stay_rows
    ]

    successful_exit_target_counts = _counter_dict(
        Counter(str(row["selected_policy"]) for row in successful_exit_rows)
    )

    blocked_state_summary = _state_summary(blocked_exit_rows)
    successful_state_summary = _state_summary(successful_exit_rows)
    quiet_state_summary = _state_summary(quiet_stay_rows)

    payload = {
        "date": "2026-04-20",
        "branch": "feature/ri-role-map-implementation-2026-03-24",
        "mode": "RESEARCH",
        "status": "no-trade-min-dwell-audit-generated",
        "audit_version": AUDIT_VERSION,
        "source_replay_root": _relative_path(REPLAY_ROOT),
        "observational_only": True,
        "summary_only": True,
        "non_authoritative": True,
        "recommendation_passthrough": replay_metrics["recommendation"],
        "recommendation_scope": replay_metrics["recommendation_scope"],
        "recommendation_change_attempted": False,
        "row_count": len(trace_rows),
        "source_hashes": {_relative_path(path): _sha256_file(path) for path in INPUT_PATHS},
        "no_trade_segments": {
            "segment_count": len(no_trade_segments),
            "row_count_total": sum(no_trade_segment_lengths),
            "length_stats": _length_stats(no_trade_segment_lengths),
        },
        "previous_no_trade_rows": {
            "count": len(previous_no_trade_rows),
            "share_of_all_rows": round(len(previous_no_trade_rows) / len(trace_rows), 6),
            "blocked_exit_from_no_trade_count": len(blocked_exit_rows),
            "successful_exit_from_no_trade_count": len(successful_exit_rows),
            "quiet_no_trade_stay_count": len(quiet_stay_rows),
            "other_previous_no_trade_count": len(other_previous_no_trade_rows),
            "blocked_exit_share": _round_or_none(
                None
                if not previous_no_trade_rows
                else len(blocked_exit_rows) / len(previous_no_trade_rows)
            ),
            "successful_exit_share": _round_or_none(
                None
                if not previous_no_trade_rows
                else len(successful_exit_rows) / len(previous_no_trade_rows)
            ),
            "quiet_stay_share": _round_or_none(
                None
                if not previous_no_trade_rows
                else len(quiet_stay_rows) / len(previous_no_trade_rows)
            ),
        },
        "blocked_exit_from_no_trade": {
            "state_summary": blocked_state_summary,
            "switch_reason_counts": _counter_dict(
                Counter(str(row["switch_reason"]) for row in blocked_exit_rows)
            ),
            "veto_reason_counts": _counter_dict(
                Counter(str(row["veto_reason"]) for row in blocked_exit_rows)
            ),
        },
        "successful_exit_from_no_trade": {
            "state_summary": successful_state_summary,
            "target_policy_counts": successful_exit_target_counts,
            "veto_reason_counts": _counter_dict(
                Counter(str(row["veto_reason"]) for row in successful_exit_rows)
            ),
        },
        "quiet_no_trade_stay": {
            "state_summary": quiet_state_summary,
            "veto_reason_counts": _counter_dict(
                Counter(str(row["veto_reason"]) for row in quiet_stay_rows)
            ),
        },
        "blocked_vs_successful_state_delta": {
            "clarity_score": _round_or_none(
                None
                if blocked_state_summary["avg_clarity_score"] is None
                or successful_state_summary["avg_clarity_score"] is None
                else blocked_state_summary["avg_clarity_score"]
                - successful_state_summary["avg_clarity_score"]
            ),
            "conf_overall": _round_or_none(
                None
                if blocked_state_summary["avg_conf_overall"] is None
                or successful_state_summary["avg_conf_overall"] is None
                else blocked_state_summary["avg_conf_overall"]
                - successful_state_summary["avg_conf_overall"]
            ),
            "action_edge": _round_or_none(
                None
                if blocked_state_summary["avg_action_edge"] is None
                or successful_state_summary["avg_action_edge"] is None
                else blocked_state_summary["avg_action_edge"]
                - successful_state_summary["avg_action_edge"]
            ),
            "bars_since_regime_change": _round_or_none(
                None
                if blocked_state_summary["avg_bars_since_regime_change"] is None
                or successful_state_summary["avg_bars_since_regime_change"] is None
                else blocked_state_summary["avg_bars_since_regime_change"]
                - successful_state_summary["avg_bars_since_regime_change"]
            ),
        },
        "findings": _build_findings(
            no_trade_segment_lengths,
            blocked_exit_rows,
            successful_exit_rows,
            quiet_stay_rows,
            previous_no_trade_rows,
        ),
        "upstream_reference": {
            "replay_recommendation": replay_metrics["recommendation"],
            "replay_manifest_containment_verdict": replay_manifest["containment"]["verdict"],
            "diagnostic_anchor": {
                "router_selected_no_trade_rows": 50,
                "blocked_switch_count": 49,
                "min_dwell_block_count": 32,
            },
        },
    }
    _write_json(OUTPUT_PATH, payload)

    post_snapshot = _snapshot_paths([REPLAY_ROOT])
    replay_root_diff = _diff_snapshots(pre_snapshot, post_snapshot)
    if replay_root_diff:
        raise RuntimeError(
            "Replay root changed during audit run: "
            + json.dumps(replay_root_diff, ensure_ascii=False, indent=2)
        )

    print(f"[OK] Wrote no-trade audit artifact: {OUTPUT_PATH}")
    print(f"[OK] Previous no-trade rows: {len(previous_no_trade_rows)}")
    print(f"[OK] Replay recommendation preserved: {replay_metrics['recommendation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
