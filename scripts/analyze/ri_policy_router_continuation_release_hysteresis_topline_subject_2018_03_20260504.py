# ruff: noqa: E402

import hashlib
import json
import os
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any


def _find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "pyproject.toml").exists() and (candidate / "src").exists():
            return candidate
    raise RuntimeError("Could not locate repository root from probe path")


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [_json_safe(v) for v in value]
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    if isinstance(value, Path):
        return str(value)
    return value


ROOT_DIR = _find_repo_root(Path(__file__).resolve())
SRC_DIR = ROOT_DIR / "src"
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from core.config.authority import ConfigAuthority
from core.strategy.ri_policy_router import RESEARCH_POLICY_ROUTER_DEBUG_KEY
from scripts.run.run_backtest import GenesisPipeline, _deep_merge

os.environ["GENESIS_RANDOM_SEED"] = "42"
os.environ["GENESIS_FAST_WINDOW"] = "1"
os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"
os.environ["GENESIS_PRECOMPUTE_CACHE_WRITE"] = "0"
os.environ["GENESIS_MODE_EXPLICIT"] = "1"
os.environ["GENESIS_FAST_HASH"] = "0"
os.environ["GENESIS_SCORE_VERSION"] = "v2"

SYMBOL = "tBTCUSD"
TIMEFRAME = "3h"
START = "2018-03-01"
END = "2018-03-31"
WARMUP = 120
DATA_SOURCE_POLICY = "curated_only"
EXPECTED_RUNTIME_BASE_SHA = "52b43e82b1c1e1aaceab3a078c62c736b6eea371"  # pragma: allowlist secret
CARRIER_PATH = (
    ROOT_DIR
    / "tmp"
    / "policy_router_evidence"
    / "tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json"
)
ARTIFACT_DIR = (
    ROOT_DIR
    / "results"
    / "backtests"
    / "ri_policy_router_continuation_release_hysteresis_topline_subject_2018_03_20260504"
)
SUMMARY_PATH = ARTIFACT_DIR / "continuation_release_hysteresis_topline_subject_2018_03_summary.json"
ROW_DIFFS_PATH = (
    ARTIFACT_DIR / "continuation_release_hysteresis_topline_subject_2018_03_row_diffs.json"
)
REPRESENTATIVE_LIMIT = 24
EXPECTED_BASELINE_CONTINUATION_RELEASE_TIMESTAMPS = (
    "2018-03-16T09:00:00+00:00",
    "2018-03-16T12:00:00+00:00",
    "2018-03-16T15:00:00+00:00",
    "2018-03-17T03:00:00+00:00",
    "2018-03-17T06:00:00+00:00",
    "2018-03-17T09:00:00+00:00",
    "2018-03-17T12:00:00+00:00",
    "2018-03-17T15:00:00+00:00",
    "2018-03-17T18:00:00+00:00",
    "2018-03-17T21:00:00+00:00",
    "2018-03-18T00:00:00+00:00",
    "2018-03-18T03:00:00+00:00",
)
EXPECTED_RELEASE_ZERO_CONTINUATION_RELEASE_TIMESTAMPS = (
    "2018-03-16T09:00:00+00:00",
    "2018-03-16T12:00:00+00:00",
    "2018-03-16T15:00:00+00:00",
    "2018-03-17T03:00:00+00:00",
    "2018-03-17T06:00:00+00:00",
    "2018-03-17T09:00:00+00:00",
)


def _git_head() -> str:
    return subprocess.check_output(
        ["git", "-C", str(ROOT_DIR), "rev-parse", "HEAD"], text=True
    ).strip()


def _git_status_porcelain() -> list[str]:
    output = subprocess.check_output(
        [
            "git",
            "-C",
            str(ROOT_DIR),
            "status",
            "--short",
            "--untracked-files=all",
        ],
        text=True,
    )
    return [line.strip() for line in output.splitlines() if line.strip()]


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


EVIDENCE_COMMIT_SHA = _git_head()


def _stable_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _load_base_and_carrier_cfg() -> tuple[dict[str, Any], dict[str, Any], ConfigAuthority]:
    authority = ConfigAuthority()
    cfg_obj, _, _ = authority.get()
    base_cfg = cfg_obj.model_dump()
    override_payload = json.loads(CARRIER_PATH.read_text(encoding="utf-8"))
    carrier_cfg = override_payload.get("cfg") or override_payload.get("parameters")
    if not isinstance(carrier_cfg, dict):
        raise SystemExit("Evidence carrier missing cfg/parameters object")
    return base_cfg, carrier_cfg, authority


def _run_case(
    mode: str,
    *,
    base_cfg: dict[str, Any],
    carrier_cfg: dict[str, Any],
    authority: ConfigAuthority,
) -> dict[str, Any]:
    override_cfg = deepcopy(carrier_cfg)
    mtf = override_cfg.setdefault("multi_timeframe", {})
    router_cfg = mtf.setdefault("research_policy_router", {})
    if not isinstance(router_cfg, dict) or not bool(router_cfg.get("enabled", False)):
        raise SystemExit(f"Carrier does not expose enabled research_policy_router for {mode}")

    if mode == "baseline":
        router_cfg.pop("continuation_release_hysteresis", None)
    elif mode == "release_zero":
        router_cfg["continuation_release_hysteresis"] = 0
    else:
        raise ValueError(mode)

    validated_cfg = authority.validate(_deep_merge(base_cfg, override_cfg)).model_dump()

    pipeline = GenesisPipeline()
    pipeline.setup_environment(seed=42)
    engine = pipeline.create_engine(
        symbol=SYMBOL,
        timeframe=TIMEFRAME,
        start_date=START,
        end_date=END,
        warmup_bars=WARMUP,
        data_source_policy=DATA_SOURCE_POLICY,
    )
    if not engine.load_data():
        raise SystemExit(f"BacktestEngine.load_data() failed for {mode}")

    rows: dict[str, dict[str, Any]] = {}
    continuation_release_rows: dict[str, dict[str, Any]] = {}

    def capture(result: dict[str, Any], meta: dict[str, Any] | None, candles: dict[str, Any]):
        timestamps = candles.get("timestamp") or []
        if not timestamps:
            return result, meta
        ts = timestamps[-1]
        ts_text = str(ts.isoformat() if hasattr(ts, "isoformat") else ts)
        decision = (meta or {}).get("decision") or {}
        state_out = decision.get("state_out") or {}
        row = {
            "action": result.get("action"),
            "reasons": decision.get("reasons"),
            "size": decision.get("size"),
            "router_state": state_out.get("research_policy_router_state"),
            "router_debug": state_out.get(RESEARCH_POLICY_ROUTER_DEBUG_KEY),
        }
        rows[ts_text] = _json_safe(row)
        debug = row.get("router_debug") or {}
        if debug.get("switch_control_mode") == "continuation_release":
            continuation_release_rows[ts_text] = _json_safe(row)
        return result, meta

    engine.evaluation_hook = capture
    results = engine.run(policy={"symbol": SYMBOL, "timeframe": TIMEFRAME}, configs=validated_cfg)
    if "error" in results:
        raise SystemExit(f"Backtest run failed for {mode}: {results['error']}")

    backtest_info = results.get("backtest_info") or {}
    execution_mode = backtest_info.get("execution_mode") or {}
    if not execution_mode.get("fast_window"):
        raise SystemExit(f"Execution mode drift for {mode}: fast_window false")
    if str(execution_mode.get("env_precompute_features")) != "1":
        raise SystemExit(f"Execution mode drift for {mode}: env_precompute_features != 1")
    if not execution_mode.get("precompute_enabled"):
        raise SystemExit(f"Execution mode drift for {mode}: precompute_enabled false")
    if str(execution_mode.get("mode_explicit")) != "1":
        raise SystemExit(f"Execution mode drift for {mode}: mode_explicit != 1")

    return {
        "summary": _json_safe(results.get("summary")),
        "position_summary": _json_safe(results.get("position_summary")),
        "metrics": _json_safe(results.get("metrics")),
        "execution_mode": _json_safe(execution_mode),
        "bars_total": _json_safe(backtest_info.get("bars_total")),
        "bars_processed": _json_safe(backtest_info.get("bars_processed")),
        "effective_config_fingerprint": _json_safe(
            backtest_info.get("effective_config_fingerprint")
        ),
        "rows": rows,
        "continuation_release_rows": continuation_release_rows,
    }


def _behavior_row(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    normalized = deepcopy(row)
    debug = normalized.get("router_debug") or {}
    router_params = debug.get("router_params")
    if (
        isinstance(router_params, dict)
        and debug.get("switch_control_mode") != "continuation_release"
    ):
        router_params.pop("continuation_release_hysteresis", None)
    return normalized


def _representative_cluster_rows(
    baseline_rows: dict[str, dict[str, Any]],
    release_zero_rows: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    timestamps = sorted(
        set(EXPECTED_BASELINE_CONTINUATION_RELEASE_TIMESTAMPS)
        | set(EXPECTED_RELEASE_ZERO_CONTINUATION_RELEASE_TIMESTAMPS)
    )
    for timestamp in timestamps:
        output.append(
            {
                "timestamp": timestamp,
                "baseline": baseline_rows.get(timestamp),
                "release_zero": release_zero_rows.get(timestamp),
                "behavior_changed": _behavior_row(baseline_rows.get(timestamp))
                != _behavior_row(release_zero_rows.get(timestamp)),
            }
        )
    return output


def main() -> int:
    if EVIDENCE_COMMIT_SHA != EXPECTED_RUNTIME_BASE_SHA:
        raise SystemExit(
            f"Runtime base SHA drifted: expected {EXPECTED_RUNTIME_BASE_SHA}, actual {EVIDENCE_COMMIT_SHA}"
        )

    base_cfg, carrier_cfg, authority = _load_base_and_carrier_cfg()
    baseline = _run_case(
        "baseline", base_cfg=base_cfg, carrier_cfg=carrier_cfg, authority=authority
    )
    release_zero = _run_case(
        "release_zero",
        base_cfg=base_cfg,
        carrier_cfg=carrier_cfg,
        authority=authority,
    )

    baseline_rows = baseline.pop("rows")
    release_zero_rows = release_zero.pop("rows")
    baseline_release_rows = baseline.pop("continuation_release_rows")
    release_zero_release_rows = release_zero.pop("continuation_release_rows")

    observed_baseline_release_timestamps = tuple(sorted(baseline_release_rows))
    observed_release_zero_release_timestamps = tuple(sorted(release_zero_release_rows))
    if observed_baseline_release_timestamps != EXPECTED_BASELINE_CONTINUATION_RELEASE_TIMESTAMPS:
        raise SystemExit(
            "Baseline continuation-release cluster drifted: "
            f"expected={EXPECTED_BASELINE_CONTINUATION_RELEASE_TIMESTAMPS}, "
            f"actual={observed_baseline_release_timestamps}"
        )
    if (
        observed_release_zero_release_timestamps
        != EXPECTED_RELEASE_ZERO_CONTINUATION_RELEASE_TIMESTAMPS
    ):
        raise SystemExit(
            "Release-zero continuation-release cluster drifted: "
            f"expected={EXPECTED_RELEASE_ZERO_CONTINUATION_RELEASE_TIMESTAMPS}, "
            f"actual={observed_release_zero_release_timestamps}"
        )

    diffs: list[dict[str, Any]] = []
    action_diff_count = 0
    size_diff_count = 0
    selected_policy_diff_count = 0
    switch_reason_diff_count = 0
    behavioral_row_diff_count = 0
    parameter_only_diff_count = 0
    continuation_release_behavioral_diff_count = 0

    for ts in sorted(set(baseline_rows) | set(release_zero_rows)):
        baseline_row = baseline_rows.get(ts)
        release_zero_row = release_zero_rows.get(ts)
        if baseline_row == release_zero_row:
            continue

        baseline_debug = (baseline_row or {}).get("router_debug") or {}
        release_zero_debug = (release_zero_row or {}).get("router_debug") or {}
        continuation_release_involved = (
            baseline_debug.get("switch_control_mode") == "continuation_release"
            or release_zero_debug.get("switch_control_mode") == "continuation_release"
        )
        action_changed = (baseline_row or {}).get("action") != (release_zero_row or {}).get(
            "action"
        )
        size_changed = (baseline_row or {}).get("size") != (release_zero_row or {}).get("size")
        selected_policy_changed = baseline_debug.get("selected_policy") != release_zero_debug.get(
            "selected_policy"
        )
        switch_reason_changed = baseline_debug.get("switch_reason") != release_zero_debug.get(
            "switch_reason"
        )
        behavior_changed = _behavior_row(baseline_row) != _behavior_row(release_zero_row)

        if action_changed:
            action_diff_count += 1
        if size_changed:
            size_diff_count += 1
        if selected_policy_changed:
            selected_policy_diff_count += 1
        if switch_reason_changed:
            switch_reason_diff_count += 1
        if behavior_changed:
            behavioral_row_diff_count += 1
        else:
            parameter_only_diff_count += 1
        if continuation_release_involved and behavior_changed:
            continuation_release_behavioral_diff_count += 1

        diffs.append(
            {
                "timestamp": ts,
                "action_changed": action_changed,
                "size_changed": size_changed,
                "selected_policy_changed": selected_policy_changed,
                "switch_reason_changed": switch_reason_changed,
                "behavior_changed": behavior_changed,
                "continuation_release_involved": continuation_release_involved,
                "baseline": baseline_row,
                "release_zero": release_zero_row,
            }
        )

    dirty_paths = _git_status_porcelain()
    subject_fingerprint = {
        "runtime_base_sha": EXPECTED_RUNTIME_BASE_SHA,
        "evidence_commit_sha": EVIDENCE_COMMIT_SHA,
        "evidence_checkout_clean": len(dirty_paths) == 0,
        "evidence_checkout_dirty_paths": dirty_paths,
        "local_reproducibility_scope": (
            "bounded local research environment with curated_only data present; "
            "not a clean-checkout CI-hermetic claim"
        ),
        "symbol": SYMBOL,
        "timeframe": TIMEFRAME,
        "start": START,
        "end": END,
        "warmup": WARMUP,
        "data_source_policy": DATA_SOURCE_POLICY,
        "carrier_config": str(CARRIER_PATH.relative_to(ROOT_DIR)),
        "carrier_sha256": _file_sha256(CARRIER_PATH),
        "comparison": {
            "baseline": "enabled carrier as-is (implicit shared hysteresis)",
            "release_zero": "same enabled carrier with continuation_release_hysteresis=0",
            "variant_setting": {
                "field": "multi_timeframe.research_policy_router.continuation_release_hysteresis",
                "baseline": "implicit shared hysteresis",
                "release_zero": 0,
            },
        },
        "expected_baseline_continuation_release_timestamps": list(
            EXPECTED_BASELINE_CONTINUATION_RELEASE_TIMESTAMPS
        ),
        "expected_release_zero_continuation_release_timestamps": list(
            EXPECTED_RELEASE_ZERO_CONTINUATION_RELEASE_TIMESTAMPS
        ),
        "env": {
            "GENESIS_RANDOM_SEED": os.environ.get("GENESIS_RANDOM_SEED"),
            "GENESIS_FAST_WINDOW": os.environ.get("GENESIS_FAST_WINDOW"),
            "GENESIS_PRECOMPUTE_FEATURES": os.environ.get("GENESIS_PRECOMPUTE_FEATURES"),
            "GENESIS_PRECOMPUTE_CACHE_WRITE": os.environ.get("GENESIS_PRECOMPUTE_CACHE_WRITE"),
            "GENESIS_MODE_EXPLICIT": os.environ.get("GENESIS_MODE_EXPLICIT"),
            "GENESIS_FAST_HASH": os.environ.get("GENESIS_FAST_HASH"),
            "GENESIS_SCORE_VERSION": os.environ.get("GENESIS_SCORE_VERSION"),
        },
    }

    normalized_summary = {
        "subject_fingerprint": subject_fingerprint,
        "baseline": baseline,
        "release_zero": release_zero,
        "comparison": {
            "all_row_diff_count": len(diffs),
            "action_diff_count": action_diff_count,
            "size_diff_count": size_diff_count,
            "selected_policy_diff_count": selected_policy_diff_count,
            "switch_reason_diff_count": switch_reason_diff_count,
            "behavioral_row_diff_count": behavioral_row_diff_count,
            "parameter_only_diff_count": parameter_only_diff_count,
            "baseline_continuation_release_row_count": len(baseline_release_rows),
            "release_zero_continuation_release_row_count": len(release_zero_release_rows),
            "continuation_release_behavioral_diff_count": continuation_release_behavioral_diff_count,
            "baseline_continuation_release_timestamps": sorted(baseline_release_rows),
            "release_zero_continuation_release_timestamps": sorted(release_zero_release_rows),
            "total_return_diff": (release_zero.get("summary") or {}).get("total_return", 0.0)
            - (baseline.get("summary") or {}).get("total_return", 0.0),
            "final_capital_diff": (release_zero.get("summary") or {}).get("final_capital", 0.0)
            - (baseline.get("summary") or {}).get("final_capital", 0.0),
            "num_trades_diff": (release_zero.get("summary") or {}).get("num_trades", 0)
            - (baseline.get("summary") or {}).get("num_trades", 0),
            "representative_behavioral_diffs": [diff for diff in diffs if diff["behavior_changed"]][
                :REPRESENTATIVE_LIMIT
            ],
            "representative_cluster_rows": _representative_cluster_rows(
                baseline_release_rows,
                release_zero_release_rows,
            ),
        },
    }

    summary_hash = _stable_hash(normalized_summary)
    row_diffs_hash = _stable_hash(diffs)
    summary_payload = {
        **normalized_summary,
        "normalized_summary_hash": summary_hash,
        "row_diffs_hash": row_diffs_hash,
    }

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")
    ROW_DIFFS_PATH.write_text(json.dumps(diffs, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "summary_artifact": str(SUMMARY_PATH),
                "row_diffs_artifact": str(ROW_DIFFS_PATH),
                "normalized_summary_hash": summary_hash,
                "row_diffs_hash": row_diffs_hash,
                "action_diff_count": action_diff_count,
                "size_diff_count": size_diff_count,
                "selected_policy_diff_count": selected_policy_diff_count,
                "switch_reason_diff_count": switch_reason_diff_count,
                "behavioral_row_diff_count": behavioral_row_diff_count,
                "baseline_continuation_release_row_count": len(baseline_release_rows),
                "release_zero_continuation_release_row_count": len(release_zero_release_rows),
                "total_return_diff": normalized_summary["comparison"]["total_return_diff"],
                "final_capital_diff": normalized_summary["comparison"]["final_capital_diff"],
                "num_trades_diff": normalized_summary["comparison"]["num_trades_diff"],
                "evidence_commit_sha": EVIDENCE_COMMIT_SHA,
                "evidence_checkout_clean": len(dirty_paths) == 0,
                "carrier_sha256": subject_fingerprint["carrier_sha256"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
