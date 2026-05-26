# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


def _find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "pyproject.toml").exists() and (candidate / "src").exists():
            return candidate
    raise RuntimeError("Could not locate repository root from probe path")


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(inner) for key, inner in value.items()}
    if isinstance(value, list | tuple):
        return [_json_safe(inner) for inner in value]
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    if isinstance(value, Path):
        return str(value)
    return value


def _parse_timestamp(raw: str) -> datetime:
    normalized = raw.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _normalize_timestamp_text(raw: Any) -> str:
    if raw is None:
        raise ValueError("timestamp is required")
    if hasattr(raw, "isoformat"):
        return _parse_timestamp(str(raw.isoformat())).isoformat()
    return _parse_timestamp(str(raw)).isoformat()


def _git_head_sha() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT_DIR,
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return "unknown"
    return result.stdout.strip() or "unknown"


ROOT_DIR = _find_repo_root(Path(__file__).resolve())
SRC_DIR = ROOT_DIR / "src"
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from core.config.authority import ConfigAuthority
from core.strategy.ri_policy_router import (
    RESEARCH_POLICY_ROUTER_DEBUG_KEY,
    RESEARCH_POLICY_ROUTER_STATE_KEY,
)
from scripts.run.run_backtest import GenesisPipeline, _build_decision_row, _deep_merge

os.environ["GENESIS_RANDOM_SEED"] = "42"
os.environ["GENESIS_FAST_WINDOW"] = "1"
os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"
os.environ["GENESIS_PRECOMPUTE_CACHE_WRITE"] = "0"
os.environ["GENESIS_MODE_EXPLICIT"] = "1"
os.environ["GENESIS_FAST_HASH"] = "0"
os.environ["GENESIS_SCORE_VERSION"] = "v2"

SYMBOL = "tBTCUSD"
TIMEFRAME = "3h"
WARMUP = 120
WARMUP_BUFFER_DAYS = 30
END_BUFFER_DAYS = 1
DATA_SOURCE_POLICY = "curated_only"
SOURCE_ARTIFACT_RELATIVE = Path(
    "results/evaluation/ri_policy_router_2023_12_vs_2024_fixed_window_phase_contrast_2026-05-25.json"
)
CARRIER_PATH = (
    ROOT_DIR
    / "tmp"
    / "policy_router_evidence"
    / "tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json"
)
OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = (
    "feature_attribution_post_phase14_ri_decision_surface_fixed_three_cohort_2026-05-26.json"
)
STATUS_OK = "feature_attribution_ri_decision_surface_fixed_three_cohort_generated"
STATUS_FAIL_CLOSED = "feature_attribution_ri_decision_surface_fixed_three_cohort_fail_closed"
SOURCE_EXPECTED_STATUS = "fixed_window_phase_contrast_generated"
WORKING_CONTRACT_REFERENCE = Path("GENESIS_WORKING_CONTRACT.md")

COHORT_SPECS = {
    "less_hostile_clean_continuation": {
        "source_key": "continuation_2023_wave_one",
        "display_name": "2023-12 wave 1",
    },
    "weak_clean_continuation": {
        "source_key": "continuation_2023_wave_two",
        "display_name": "2023-12 wave 2",
    },
    "blocked_dominant_mixed_pocket": {
        "source_key": "harmful_2024_regression_target",
        "display_name": "2024 harmful target",
    },
}


class DecisionSurfaceError(RuntimeError):
    """Raised when the bounded decision-surface extraction cannot be completed safely."""


@dataclass(frozen=True)
class CohortWindow:
    cohort_label: str
    source_key: str
    display_name: str
    start_date: str
    end_date: str
    exact_timestamps: tuple[str, ...]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Emit schema-compatible RI decision rows for the fixed three-cohort surface used by "
            "the attribution-layer foundation work."
        )
    )
    parser.add_argument(
        "--base-sha",
        required=True,
        help="Exact repository HEAD SHA for provenance in the emitted artifact.",
    )
    parser.add_argument(
        "--source-artifact-relative",
        default=str(SOURCE_ARTIFACT_RELATIVE),
        help="Repo-relative fixed-window phase-contrast artifact defining the exact cohorts.",
    )
    parser.add_argument(
        "--output-root-relative",
        default=str(OUTPUT_ROOT_RELATIVE),
        help="Repo-relative output directory for the emitted JSON artifact.",
    )
    parser.add_argument(
        "--summary-filename",
        default=OUTPUT_FILENAME,
        help="Filename to use for the emitted JSON artifact.",
    )
    return parser.parse_args()


def _coerce_dict(value: Any, *, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DecisionSurfaceError(
            f"Expected object for {field_name}, got {type(value).__name__}: {value!r}"
        )
    return value


def _coerce_list(value: Any, *, field_name: str) -> list[Any]:
    if not isinstance(value, list):
        raise DecisionSurfaceError(
            f"Expected list for {field_name}, got {type(value).__name__}: {value!r}"
        )
    return value


def _coerce_str(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise DecisionSurfaceError(f"Expected non-empty string for {field_name}, got {value!r}")
    return value


def _load_source_artifact(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise DecisionSurfaceError(f"Source artifact not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise DecisionSurfaceError("Source artifact is not a JSON object")
    if payload.get("status") != SOURCE_EXPECTED_STATUS:
        raise DecisionSurfaceError(f"Unexpected source artifact status: {payload.get('status')!r}")
    cohorts = payload.get("cohorts")
    if not isinstance(cohorts, dict):
        raise DecisionSurfaceError("Source artifact missing cohorts payload")
    return payload


def _extract_cohort_windows(payload: dict[str, Any]) -> dict[str, CohortWindow]:
    cohorts_payload = payload["cohorts"]
    extracted: dict[str, CohortWindow] = {}
    for cohort_label, spec in COHORT_SPECS.items():
        cohort = cohorts_payload.get(spec["source_key"])
        if not isinstance(cohort, dict):
            raise DecisionSurfaceError(f"Source artifact missing cohort {spec['source_key']!r}")
        rows = _coerce_list(cohort.get("rows"), field_name=f"{spec['source_key']}.rows")
        timestamps = tuple(
            sorted(
                _normalize_timestamp_text(
                    _coerce_str(row.get("timestamp"), field_name=f"{spec['source_key']}.timestamp")
                )
                for row in rows
            )
        )
        if not timestamps:
            raise DecisionSurfaceError(f"Cohort {spec['source_key']!r} contains no timestamps")
        if len(set(timestamps)) != len(timestamps):
            raise DecisionSurfaceError(
                f"Cohort {spec['source_key']!r} contains duplicate timestamps: {timestamps}"
            )
        parsed = [_parse_timestamp(timestamp) for timestamp in timestamps]
        requested_start_date = (parsed[0] - timedelta(days=WARMUP_BUFFER_DAYS)).date().isoformat()
        extracted[cohort_label] = CohortWindow(
            cohort_label=cohort_label,
            source_key=spec["source_key"],
            display_name=spec["display_name"],
            start_date=requested_start_date,
            end_date=(parsed[-1] + timedelta(days=END_BUFFER_DAYS)).date().isoformat(),
            exact_timestamps=timestamps,
        )
    return extracted


def _load_base_and_carrier_cfg() -> tuple[dict[str, Any], dict[str, Any], ConfigAuthority]:
    authority = ConfigAuthority()
    cfg_obj, _, _ = authority.get()
    base_cfg = cfg_obj.model_dump()
    override_payload = json.loads(CARRIER_PATH.read_text(encoding="utf-8"))
    carrier_cfg = override_payload.get("cfg") or override_payload.get("parameters")
    if not isinstance(carrier_cfg, dict):
        raise DecisionSurfaceError("Evidence carrier missing cfg/parameters object")
    return base_cfg, carrier_cfg, authority


def _count_field(rows: list[dict[str, Any]], field_name: str) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        value = row.get(field_name)
        label = str(value) if value not in {None, ""} else "<missing>"
        counts[label] += 1
    return dict(sorted(counts.items()))


def _count_router_debug_field(rows: list[dict[str, Any]], field_name: str) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        debug = row.get("router_debug") or {}
        value = debug.get(field_name) if isinstance(debug, dict) else None
        label = str(value) if value not in {None, ""} else "<missing>"
        counts[label] += 1
    return dict(sorted(counts.items()))


def _decision_identity_key(row: dict[str, Any]) -> str:
    stable_fields = ("row_id", "bar_index", "timestamp", "symbol", "timeframe")
    parts: list[str] = []
    for field_name in stable_fields:
        value = row.get(field_name)
        if value is not None and value != "":
            parts.append(f"{field_name}={value}")
    if not parts:
        raise DecisionSurfaceError(f"Could not build decision identity key from row: {row}")
    return "|".join(parts)


def _validate_execution_mode(execution_mode: dict[str, Any], *, cohort_label: str) -> None:
    if not execution_mode.get("fast_window"):
        raise DecisionSurfaceError(f"Execution mode drift for {cohort_label}: fast_window false")
    if str(execution_mode.get("env_precompute_features")) != "1":
        raise DecisionSurfaceError(
            f"Execution mode drift for {cohort_label}: env_precompute_features != 1"
        )
    if not execution_mode.get("precompute_enabled"):
        raise DecisionSurfaceError(
            f"Execution mode drift for {cohort_label}: precompute_enabled false"
        )
    if str(execution_mode.get("mode_explicit")) != "1":
        raise DecisionSurfaceError(f"Execution mode drift for {cohort_label}: mode_explicit != 1")


def _run_cohort_surface(
    cohort: CohortWindow,
    *,
    base_sha: str,
    base_cfg: dict[str, Any],
    carrier_cfg: dict[str, Any],
    authority: ConfigAuthority,
) -> dict[str, Any]:
    override_cfg = deepcopy(carrier_cfg)
    mtf = override_cfg.setdefault("multi_timeframe", {})
    router_cfg = mtf.setdefault("research_policy_router", {})
    if not isinstance(router_cfg, dict) or not bool(router_cfg.get("enabled", False)):
        raise DecisionSurfaceError(
            f"Carrier does not expose enabled research_policy_router for {cohort.cohort_label}"
        )

    validated_cfg = authority.validate(_deep_merge(base_cfg, override_cfg)).model_dump()

    pipeline = GenesisPipeline()
    pipeline.setup_environment(seed=42)
    engine = pipeline.create_engine(
        symbol=SYMBOL,
        timeframe=TIMEFRAME,
        start_date=cohort.start_date,
        end_date=cohort.end_date,
        warmup_bars=WARMUP,
        data_source_policy=DATA_SOURCE_POLICY,
    )
    if not engine.load_data():
        raise DecisionSurfaceError(
            f"BacktestEngine.load_data() failed for cohort {cohort.cohort_label}"
        )

    rows_by_timestamp: dict[str, dict[str, Any]] = {}

    def capture(result: dict[str, Any], meta: dict[str, Any] | None, candles: dict[str, Any]):
        timestamps = candles.get("timestamp") or []
        if not timestamps:
            return result, meta
        timestamp_text = _normalize_timestamp_text(timestamps[-1])
        safe_result = result if isinstance(result, dict) else {}
        safe_meta = meta if isinstance(meta, dict) else {}
        safe_candles = candles if isinstance(candles, dict) else {}
        decision = safe_meta.get("decision") or {}
        state_out = decision.get("state_out") or {}
        row = {
            **_build_decision_row(
                symbol=SYMBOL,
                timeframe=TIMEFRAME,
                result=safe_result,
                meta=safe_meta,
                candles=safe_candles,
            ),
            "base_sha": base_sha,
            "mode_label": "baseline",
            "component_toggle_label": "carrier_as_is",
            "start_date": cohort.start_date,
            "end_date": cohort.end_date,
            "warmup_bars": WARMUP,
            "cohort_label": cohort.cohort_label,
            "cohort_display_name": cohort.display_name,
            "source_cohort_key": cohort.source_key,
            "router_state": _json_safe(state_out.get(RESEARCH_POLICY_ROUTER_STATE_KEY)),
            "router_debug": _json_safe(state_out.get(RESEARCH_POLICY_ROUTER_DEBUG_KEY)),
        }
        rows_by_timestamp[timestamp_text] = _json_safe(row)
        return result, meta

    engine.evaluation_hook = capture
    results = engine.run(policy={"symbol": SYMBOL, "timeframe": TIMEFRAME}, configs=validated_cfg)
    if "error" in results:
        raise DecisionSurfaceError(
            f"Backtest run failed for cohort {cohort.cohort_label}: {results['error']}"
        )

    backtest_info = results.get("backtest_info") or {}
    execution_mode = _coerce_dict(
        backtest_info.get("execution_mode") or {},
        field_name=f"{cohort.cohort_label}.execution_mode",
    )
    _validate_execution_mode(execution_mode, cohort_label=cohort.cohort_label)
    effective_config_fingerprint = backtest_info.get("effective_config_fingerprint")

    missing_timestamps = [
        timestamp for timestamp in cohort.exact_timestamps if timestamp not in rows_by_timestamp
    ]
    if missing_timestamps:
        raise DecisionSurfaceError(
            f"Missing expected timestamps for cohort {cohort.cohort_label}: {missing_timestamps}"
        )

    exact_rows = [deepcopy(rows_by_timestamp[timestamp]) for timestamp in cohort.exact_timestamps]
    for row in exact_rows:
        row["effective_config_fingerprint"] = _json_safe(effective_config_fingerprint)
        row["data_source_policy"] = DATA_SOURCE_POLICY
        row["decision_identity_key"] = _decision_identity_key(row)

    duplicate_identity_keys = [
        identity_key
        for identity_key, count in Counter(
            str(row.get("decision_identity_key")) for row in exact_rows
        ).items()
        if count > 1
    ]
    if duplicate_identity_keys:
        raise DecisionSurfaceError(
            "Duplicate decision identity keys inside cohort "
            f"{cohort.cohort_label}: {duplicate_identity_keys}"
        )

    return {
        "cohort_label": cohort.cohort_label,
        "display_name": cohort.display_name,
        "source_key": cohort.source_key,
        "window": {
            "start_date": cohort.start_date,
            "end_date": cohort.end_date,
            "exact_timestamp_count": len(cohort.exact_timestamps),
            "exact_timestamps": list(cohort.exact_timestamps),
        },
        "run_context": {
            "execution_mode": _json_safe(execution_mode),
            "effective_config_fingerprint": _json_safe(effective_config_fingerprint),
            "bars_total": _json_safe(backtest_info.get("bars_total")),
            "bars_processed": _json_safe(backtest_info.get("bars_processed")),
        },
        "summary": {
            "all_window_row_count": len(rows_by_timestamp),
            "exact_row_count": len(exact_rows),
            "action_counts": _count_field(exact_rows, "action"),
            "selected_policy_counts": _count_router_debug_field(exact_rows, "selected_policy"),
            "switch_reason_counts": _count_router_debug_field(exact_rows, "switch_reason"),
        },
        "decision_rows": exact_rows,
    }


def _build_fail_closed_result(
    *,
    base_sha: str,
    reason: str,
    source_artifact_relative: str,
) -> dict[str, Any]:
    return {
        "audit_version": "feature-attribution-post-phase14-ri-decision-surface-fixed-three-cohort-2026-05-26",
        "base_sha": base_sha,
        "actual_head_sha": _git_head_sha(),
        "status": STATUS_FAIL_CLOSED,
        "observational_only": True,
        "non_authoritative": True,
        "failure_reason": reason,
        "inputs": {
            "source_artifact": source_artifact_relative,
            "carrier_path": str(CARRIER_PATH.relative_to(ROOT_DIR)),
            "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
        },
    }


def run_decision_surface(
    *,
    base_sha: str,
    source_artifact_relative: Path,
) -> dict[str, Any]:
    try:
        payload = _load_source_artifact(ROOT_DIR / source_artifact_relative)
        cohort_windows = _extract_cohort_windows(payload)
        base_cfg, carrier_cfg, authority = _load_base_and_carrier_cfg()
        cohort_payloads = {
            cohort_label: _run_cohort_surface(
                cohort_window,
                base_sha=base_sha,
                base_cfg=base_cfg,
                carrier_cfg=carrier_cfg,
                authority=authority,
            )
            for cohort_label, cohort_window in cohort_windows.items()
        }
    except DecisionSurfaceError as exc:
        return _build_fail_closed_result(
            base_sha=base_sha,
            reason=str(exc),
            source_artifact_relative=str(source_artifact_relative),
        )

    decision_rows = [
        row
        for cohort_label in COHORT_SPECS
        for row in cohort_payloads[cohort_label]["decision_rows"]
    ]
    duplicate_identity_keys = [
        identity_key
        for identity_key, count in Counter(
            str(row.get("decision_identity_key")) for row in decision_rows
        ).items()
        if count > 1
    ]
    if duplicate_identity_keys:
        return _build_fail_closed_result(
            base_sha=base_sha,
            reason=(
                "Duplicate decision identity keys across cohorts: " f"{duplicate_identity_keys}"
            ),
            source_artifact_relative=str(source_artifact_relative),
        )

    return {
        "audit_version": "feature-attribution-post-phase14-ri-decision-surface-fixed-three-cohort-2026-05-26",
        "base_sha": base_sha,
        "actual_head_sha": _git_head_sha(),
        "status": STATUS_OK,
        "observational_only": True,
        "non_authoritative": True,
        "classification_boundary": {
            "source_surface": "fixed exact cohort timestamps reused from the fixed-window phase-contrast artifact",
            "schema_target": "decision_row only",
            "excluded_row_families_in_this_slice": [
                "execution_row",
                "trade_row",
                "ledger_impact_row",
            ],
            "same_stack_off_vs_on_ready_identity_fields": [
                "row_id",
                "bar_index",
                "timestamp",
                "entry_time",
                "position_id",
                "symbol",
                "timeframe",
            ],
        },
        "inputs": {
            "source_artifact": str(source_artifact_relative),
            "carrier_path": str(CARRIER_PATH.relative_to(ROOT_DIR)),
            "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
            "symbol": SYMBOL,
            "timeframe": TIMEFRAME,
            "warmup_bars": WARMUP,
            "data_source_policy": DATA_SOURCE_POLICY,
            "mode_label": "baseline",
            "component_toggle_label": "carrier_as_is",
            "env": {
                "GENESIS_RANDOM_SEED": os.environ.get("GENESIS_RANDOM_SEED"),
                "GENESIS_FAST_WINDOW": os.environ.get("GENESIS_FAST_WINDOW"),
                "GENESIS_PRECOMPUTE_FEATURES": os.environ.get("GENESIS_PRECOMPUTE_FEATURES"),
                "GENESIS_PRECOMPUTE_CACHE_WRITE": os.environ.get("GENESIS_PRECOMPUTE_CACHE_WRITE"),
                "GENESIS_MODE_EXPLICIT": os.environ.get("GENESIS_MODE_EXPLICIT"),
                "GENESIS_FAST_HASH": os.environ.get("GENESIS_FAST_HASH"),
                "GENESIS_SCORE_VERSION": os.environ.get("GENESIS_SCORE_VERSION"),
            },
        },
        "decision_row_schema_fields": {
            "observed_fields": [
                "row_id",
                "bar_index",
                "timestamp",
                "symbol",
                "timeframe",
                "action",
                "reasons",
                "size",
                "router_state",
                "router_debug",
                "base_sha",
                "effective_config_fingerprint",
                "start_date",
                "end_date",
                "warmup_bars",
                "mode_label",
                "component_toggle_label",
            ],
            "derived_fields": [
                "decision_identity_key",
                "cohort_label",
                "cohort_display_name",
                "source_cohort_key",
            ],
        },
        "cohorts": {
            cohort_label: {
                "display_name": payload["display_name"],
                "source_key": payload["source_key"],
                "window": payload["window"],
                "run_context": payload["run_context"],
                "summary": payload["summary"],
            }
            for cohort_label, payload in cohort_payloads.items()
        },
        "decision_rows": decision_rows,
    }


def main() -> int:
    args = _parse_args()
    source_artifact_relative = Path(args.source_artifact_relative)
    output_root = ROOT_DIR / Path(args.output_root_relative)
    output_json = output_root / args.summary_filename
    result = run_decision_surface(
        base_sha=args.base_sha,
        source_artifact_relative=source_artifact_relative,
    )

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "summary_artifact": str(output_json),
                "status": result["status"],
                "decision_row_count": len(result.get("decision_rows") or []),
                "cohort_labels": list((result.get("cohorts") or {}).keys()),
                "failure_reason": result.get("failure_reason"),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
