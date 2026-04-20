#!/usr/bin/env python3
"""Descriptive release-envelope probe for blocked no-trade exits.

This script is research-only and read-only with respect to the replay root. It measures
how many blocked exits from `RI_no_trade_policy` already sit inside the frozen successful
release cohort's observed categorical and numeric support envelope.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from statistics import median
from typing import Any


POLICY_NO_TRADE = "RI_no_trade_policy"
ROOT_REQUIRED_MARKERS = ("pyproject.toml", "src")
PROBE_VERSION = "scpe-ri-v1-no-trade-release-probe-2026-04-20"

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
REQUIRED_REPLAY_METRICS_FIELDS = {
    "observational_only",
    "recommendation",
    "recommendation_scope",
    "routing_metrics",
    "observational_metrics",
}
REQUIRED_MANIFEST_FIELDS = {"containment", "recommendation", "recommendation_scope", "row_count"}
REQUIRED_AUDIT_FIELDS = {
    "observational_only",
    "summary_only",
    "non_authoritative",
    "recommendation_passthrough",
    "previous_no_trade_rows",
    "blocked_exit_from_no_trade",
    "successful_exit_from_no_trade",
}
ALLOWED_TRACE_FIELDS = REQUIRED_TRACE_FIELDS
ALLOWED_RI_STATE_FIELDS = REQUIRED_RI_STATE_FIELDS
ALLOWED_CORE_STATE_FIELDS = REQUIRED_CORE_STATE_FIELDS
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
ALLOWED_AUDIT_FIELDS = REQUIRED_AUDIT_FIELDS | {
    "audit_version",
    "branch",
    "date",
    "findings",
    "mode",
    "no_trade_segments",
    "quiet_no_trade_stay",
    "recommendation_change_attempted",
    "recommendation_scope",
    "row_count",
    "source_hashes",
    "source_replay_root",
    "status",
    "blocked_vs_successful_state_delta",
    "upstream_reference",
}

ROOT_DIR = None
REPLAY_ROOT = None
OUTPUT_PATH = None
ROUTING_TRACE_PATH = None
REPLAY_METRICS_PATH = None
MANIFEST_PATH = None
AUDIT_PATH = None
INPUT_PATHS = None


def _find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if all((candidate / marker).exists() for marker in ROOT_REQUIRED_MARKERS):
            return candidate
    raise RuntimeError("Could not locate repository root")


ROOT_DIR = _find_repo_root(Path(__file__).resolve())
REPLAY_ROOT = ROOT_DIR / "results" / "research" / "scpe_v1_ri"
OUTPUT_PATH = (
    ROOT_DIR / "results" / "evaluation" / "scpe_ri_v1_no_trade_release_probe_2026-04-20.json"
)
ROUTING_TRACE_PATH = REPLAY_ROOT / "routing_trace.ndjson"
REPLAY_METRICS_PATH = REPLAY_ROOT / "replay_metrics.json"
MANIFEST_PATH = REPLAY_ROOT / "manifest.json"
AUDIT_PATH = (
    ROOT_DIR / "results" / "evaluation" / "scpe_ri_v1_no_trade_min_dwell_audit_2026-04-20.json"
)
INPUT_PATHS = [
    ROUTING_TRACE_PATH,
    REPLAY_METRICS_PATH,
    MANIFEST_PATH,
    AUDIT_PATH,
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


def _validate_inputs(
    trace_rows: list[dict[str, Any]],
    replay_metrics: dict[str, Any],
    replay_manifest: dict[str, Any],
    audit_payload: dict[str, Any],
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

    _require_keys(replay_metrics, REQUIRED_REPLAY_METRICS_FIELDS, "replay_metrics")
    _require_exact_keys(replay_metrics, ALLOWED_REPLAY_METRICS_FIELDS, "replay_metrics")
    _require_keys(replay_manifest, REQUIRED_MANIFEST_FIELDS, "manifest")
    _require_exact_keys(replay_manifest, ALLOWED_MANIFEST_FIELDS, "manifest")
    _require_keys(audit_payload, REQUIRED_AUDIT_FIELDS, "no_trade_audit")
    _require_exact_keys(audit_payload, ALLOWED_AUDIT_FIELDS, "no_trade_audit")

    if replay_metrics["observational_only"] is not True:
        raise RuntimeError("replay_metrics observational_only must remain true")
    if replay_metrics["recommendation"] != "NEEDS_REVISION":
        raise RuntimeError(
            "Release probe must not upgrade or reinterpret the replay recommendation; "
            f"expected NEEDS_REVISION, got {replay_metrics['recommendation']!r}"
        )
    if audit_payload["observational_only"] is not True or audit_payload["summary_only"] is not True:
        raise RuntimeError("no_trade_audit must remain observational-only and summary-only")


def _blocked_exit_from_no_trade(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        row
        for row in rows
        if row["previous_policy"] == POLICY_NO_TRADE
        and row["selected_policy"] == POLICY_NO_TRADE
        and bool(row["switch_proposed"])
        and bool(row["switch_blocked"])
        and row["switch_reason"] == "switch_blocked_by_min_dwell"
    ]


def _successful_exit_from_no_trade(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        row
        for row in rows
        if row["previous_policy"] == POLICY_NO_TRADE and row["selected_policy"] != POLICY_NO_TRADE
    ]


def _numeric_envelope(success_rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    if not success_rows:
        raise RuntimeError("Successful release cohort is empty")
    metrics = {
        "ri_clarity_score": [
            _as_float(row["ri_state"]["ri_clarity_score"], "ri_clarity_score")
            for row in success_rows
        ],
        "conf_overall": [
            _as_float(row["ri_state"]["conf_overall"], "conf_overall") for row in success_rows
        ],
        "action_edge": [
            _as_float(row["ri_state"]["action_edge"], "action_edge") for row in success_rows
        ],
        "bars_since_regime_change": [
            _as_float(row["ri_state"]["bars_since_regime_change"], "bars_since_regime_change")
            for row in success_rows
        ],
    }
    return {
        name: {
            "min": round(min(values), 6),
            "median": round(float(median(values)), 6),
            "max": round(max(values), 6),
        }
        for name, values in metrics.items()
    }


def _categorical_envelope(success_rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    return {
        "clarity_bucket": sorted({str(row["ri_state"]["clarity_bucket"]) for row in success_rows}),
        "confidence_bucket": sorted(
            {str(row["ri_state"]["confidence_bucket"]) for row in success_rows}
        ),
        "edge_bucket": sorted({str(row["ri_state"]["edge_bucket"]) for row in success_rows}),
        "transition_bucket": sorted(
            {str(row["ri_state"]["transition_bucket"]) for row in success_rows}
        ),
        "zone": sorted({str(row["core_state"]["zone"]) for row in success_rows}),
        "target_policy": sorted({str(row["selected_policy"]) for row in success_rows}),
    }


def _row_matches_categorical_envelope(row: dict[str, Any], envelope: dict[str, list[str]]) -> bool:
    return (
        str(row["ri_state"]["clarity_bucket"]) in envelope["clarity_bucket"]
        and str(row["ri_state"]["confidence_bucket"]) in envelope["confidence_bucket"]
        and str(row["ri_state"]["edge_bucket"]) in envelope["edge_bucket"]
        and str(row["ri_state"]["transition_bucket"]) in envelope["transition_bucket"]
        and str(row["core_state"]["zone"]) in envelope["zone"]
    )


def _row_matches_numeric_envelope(
    row: dict[str, Any], envelope: dict[str, dict[str, float]]
) -> bool:
    checks = {
        "ri_clarity_score": _as_float(row["ri_state"]["ri_clarity_score"], "ri_clarity_score"),
        "conf_overall": _as_float(row["ri_state"]["conf_overall"], "conf_overall"),
        "action_edge": _as_float(row["ri_state"]["action_edge"], "action_edge"),
        "bars_since_regime_change": _as_float(
            row["ri_state"]["bars_since_regime_change"], "bars_since_regime_change"
        ),
    }
    return all(
        envelope[name]["min"] <= value <= envelope[name]["max"] for name, value in checks.items()
    )


def _row_matches_release_floor(row: dict[str, Any], envelope: dict[str, dict[str, float]]) -> bool:
    return (
        _as_float(row["ri_state"]["ri_clarity_score"], "ri_clarity_score")
        >= envelope["ri_clarity_score"]["median"]
        and _as_float(row["ri_state"]["conf_overall"], "conf_overall")
        >= envelope["conf_overall"]["median"]
        and _as_float(row["ri_state"]["action_edge"], "action_edge")
        >= envelope["action_edge"]["median"]
    )


def _mismatch_reason_counts(
    rows: list[dict[str, Any]],
    categorical: dict[str, list[str]],
    numeric: dict[str, dict[str, float]],
) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for row in rows:
        if str(row["ri_state"]["clarity_bucket"]) not in categorical["clarity_bucket"]:
            counter["clarity_bucket_outside_success_support"] += 1
        if str(row["ri_state"]["confidence_bucket"]) not in categorical["confidence_bucket"]:
            counter["confidence_bucket_outside_success_support"] += 1
        if str(row["ri_state"]["edge_bucket"]) not in categorical["edge_bucket"]:
            counter["edge_bucket_outside_success_support"] += 1
        if str(row["core_state"]["zone"]) not in categorical["zone"]:
            counter["zone_outside_success_support"] += 1
        if (
            _as_float(row["ri_state"]["ri_clarity_score"], "ri_clarity_score")
            < numeric["ri_clarity_score"]["min"]
        ):
            counter["clarity_below_success_min"] += 1
        if (
            _as_float(row["ri_state"]["conf_overall"], "conf_overall")
            < numeric["conf_overall"]["min"]
        ):
            counter["confidence_below_success_min"] += 1
        if _as_float(row["ri_state"]["action_edge"], "action_edge") < numeric["action_edge"]["min"]:
            counter["edge_below_success_min"] += 1
    return _counter_dict(counter)


def _build_findings(
    blocked_count: int,
    categorical_count: int,
    numeric_count: int,
    floor_count: int,
    both_count: int,
) -> list[str]:
    findings: list[str] = []
    findings.append(
        f"Blocked no-trade exits remain a material cohort: {blocked_count} rows are still held by `switch_blocked_by_min_dwell`."
    )
    findings.append(
        f"Categorical support overlap is high relative to blocked size: {categorical_count} of {blocked_count} blocked exits sit inside the successful-release categorical envelope."
    )
    findings.append(
        f"Numeric overlap is narrower but still material: {numeric_count} of {blocked_count} blocked exits sit inside the successful-release min/max numeric envelope."
    )
    findings.append(
        f"Release-strength floor matches remain bounded: {floor_count} of {blocked_count} blocked exits are at or above the successful-release medians for clarity, confidence, and edge; {both_count} satisfy both the categorical and numeric envelope simultaneously."
    )
    return findings


def main() -> int:
    pre_snapshot = _snapshot_paths([REPLAY_ROOT])

    trace_rows = _load_ndjson(ROUTING_TRACE_PATH)
    replay_metrics = _load_json(REPLAY_METRICS_PATH)
    replay_manifest = _load_json(MANIFEST_PATH)
    audit_payload = _load_json(AUDIT_PATH)

    _validate_inputs(trace_rows, replay_metrics, replay_manifest, audit_payload)

    blocked_rows = _blocked_exit_from_no_trade(trace_rows)
    success_rows = _successful_exit_from_no_trade(trace_rows)

    expected_blocked = int(
        audit_payload["previous_no_trade_rows"]["blocked_exit_from_no_trade_count"]
    )
    expected_success = int(
        audit_payload["previous_no_trade_rows"]["successful_exit_from_no_trade_count"]
    )
    if len(blocked_rows) != expected_blocked or len(success_rows) != expected_success:
        raise RuntimeError(
            "Release probe cohort counts drifted from the frozen no-trade audit: "
            f"blocked={len(blocked_rows)} expected={expected_blocked}, success={len(success_rows)} expected={expected_success}"
        )

    categorical = _categorical_envelope(success_rows)
    numeric = _numeric_envelope(success_rows)

    categorical_matches = [
        row for row in blocked_rows if _row_matches_categorical_envelope(row, categorical)
    ]
    numeric_matches = [row for row in blocked_rows if _row_matches_numeric_envelope(row, numeric)]
    floor_matches = [row for row in blocked_rows if _row_matches_release_floor(row, numeric)]
    both_matches = [
        row
        for row in blocked_rows
        if _row_matches_categorical_envelope(row, categorical)
        and _row_matches_numeric_envelope(row, numeric)
    ]

    payload = {
        "date": "2026-04-20",
        "branch": "feature/ri-role-map-implementation-2026-03-24",
        "mode": "RESEARCH",
        "status": "no-trade-release-probe-generated",
        "probe_version": PROBE_VERSION,
        "source_replay_root": _relative_path(REPLAY_ROOT),
        "source_audit_path": _relative_path(AUDIT_PATH),
        "observational_only": True,
        "summary_only": True,
        "non_authoritative": True,
        "recommendation_passthrough": replay_metrics["recommendation"],
        "recommendation_scope": replay_metrics["recommendation_scope"],
        "recommendation_change_attempted": False,
        "source_hashes": {_relative_path(path): _sha256_file(path) for path in INPUT_PATHS},
        "cohort_counts": {
            "blocked_exit_from_no_trade": len(blocked_rows),
            "successful_exit_from_no_trade": len(success_rows),
        },
        "successful_release_envelope": {
            "categorical": categorical,
            "numeric": numeric,
        },
        "blocked_exit_matches": {
            "categorical_envelope_match_count": len(categorical_matches),
            "categorical_envelope_match_share": round(
                len(categorical_matches) / len(blocked_rows), 6
            ),
            "numeric_envelope_match_count": len(numeric_matches),
            "numeric_envelope_match_share": round(len(numeric_matches) / len(blocked_rows), 6),
            "release_strength_floor_match_count": len(floor_matches),
            "release_strength_floor_match_share": round(len(floor_matches) / len(blocked_rows), 6),
            "categorical_and_numeric_match_count": len(both_matches),
            "categorical_and_numeric_match_share": round(len(both_matches) / len(blocked_rows), 6),
        },
        "blocked_exit_mismatch_reasons": _mismatch_reason_counts(
            blocked_rows, categorical, numeric
        ),
        "findings": _build_findings(
            len(blocked_rows),
            len(categorical_matches),
            len(numeric_matches),
            len(floor_matches),
            len(both_matches),
        ),
        "upstream_reference": {
            "audit_blocked_exit_count": expected_blocked,
            "audit_successful_exit_count": expected_success,
            "replay_recommendation": replay_metrics["recommendation"],
            "replay_manifest_containment_verdict": replay_manifest["containment"]["verdict"],
        },
    }
    _write_json(OUTPUT_PATH, payload)

    post_snapshot = _snapshot_paths([REPLAY_ROOT])
    replay_root_diff = _diff_snapshots(pre_snapshot, post_snapshot)
    if replay_root_diff:
        raise RuntimeError(
            "Replay root changed during release probe run: "
            + json.dumps(replay_root_diff, ensure_ascii=False, indent=2)
        )

    print(f"[OK] Wrote release probe artifact: {OUTPUT_PATH}")
    print(f"[OK] Blocked no-trade exits: {len(blocked_rows)}")
    print(f"[OK] Replay recommendation preserved: {replay_metrics['recommendation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
