# ruff: noqa: E402

import hashlib
import json
import os
import subprocess
import sys
from copy import deepcopy
from datetime import date, timedelta
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
WARMUP = 120
DATA_SOURCE_POLICY = "curated_only"
AVAILABLE_DATA_MIN = "2016-06-06T12:00:00"
AVAILABLE_DATA_MAX = "2026-04-15T09:00:00"
GRID_START = date(2016, 7, 1)
GRID_END = date(2026, 3, 31)
WINDOW_FAMILY = "full_calendar_month"
STRIDE_MONTHS = 1
EXPECTED_MAX_WINDOWS = 117
TOP_WINDOW_LIMIT = 12
EXPECTED_BASE_SHA = "52b43e82b1c1e1aaceab3a078c62c736b6eea371"  # pragma: allowlist secret
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
    / "ri_policy_router_continuation_release_hysteresis_monthly_inventory_20260504"
)
SUMMARY_PATH = ARTIFACT_DIR / "continuation_release_hysteresis_monthly_inventory_summary.json"
WINDOWS_PATH = ARTIFACT_DIR / "continuation_release_hysteresis_monthly_inventory_windows.json"


def _git_head() -> str:
    return subprocess.check_output(
        ["git", "-C", str(ROOT_DIR), "rev-parse", "HEAD"], text=True
    ).strip()


HEAD_SHA = _git_head()


def _load_base_and_carrier_cfg() -> tuple[dict[str, Any], dict[str, Any], ConfigAuthority]:
    authority = ConfigAuthority()
    cfg_obj, _, _ = authority.get()
    base_cfg = cfg_obj.model_dump()
    override_payload = json.loads(CARRIER_PATH.read_text(encoding="utf-8"))
    carrier_cfg = override_payload.get("cfg") or override_payload.get("parameters")
    if not isinstance(carrier_cfg, dict):
        raise SystemExit("Evidence carrier missing cfg/parameters object")
    return base_cfg, carrier_cfg, authority


def _month_end(current: date) -> date:
    if current.month == 12:
        return date(current.year, 12, 31)
    return date(current.year, current.month + 1, 1) - timedelta(days=1)


def _add_month(current: date) -> date:
    if current.month == 12:
        return date(current.year + 1, 1, 1)
    return date(current.year, current.month + 1, 1)


def _month_windows() -> list[dict[str, str]]:
    current = GRID_START
    windows: list[dict[str, str]] = []
    while current <= GRID_END:
        end = _month_end(current)
        windows.append(
            {
                "label": f"{current.year:04d}-{current.month:02d}",
                "start": current.isoformat(),
                "end": end.isoformat(),
            }
        )
        current = _add_month(current)
    if len(windows) != EXPECTED_MAX_WINDOWS:
        raise SystemExit(
            f"Monthly grid drifted: expected {EXPECTED_MAX_WINDOWS}, got {len(windows)}"
        )
    return windows


def _run_case(
    mode: str,
    *,
    start_date: str,
    end_date: str,
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
        start_date=start_date,
        end_date=end_date,
        warmup_bars=WARMUP,
        data_source_policy=DATA_SOURCE_POLICY,
    )
    if not engine.load_data():
        raise SystemExit(f"BacktestEngine.load_data() failed for {mode} {start_date}..{end_date}")

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
        raise SystemExit(
            f"Backtest run failed for {mode} {start_date}..{end_date}: {results['error']}"
        )

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
        "metrics": _json_safe(results.get("metrics")),
        "position_summary": _json_safe(results.get("position_summary")),
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


def _topline_changed(baseline_summary: dict[str, Any], release_summary: dict[str, Any]) -> bool:
    keys = (
        "final_capital",
        "total_return",
        "total_return_usd",
        "num_trades",
        "profit_factor",
        "max_drawdown",
    )
    return any(baseline_summary.get(key) != release_summary.get(key) for key in keys)


def _window_compare(
    window: dict[str, str],
    base_cfg: dict[str, Any],
    carrier_cfg: dict[str, Any],
    authority: ConfigAuthority,
) -> dict[str, Any]:
    baseline = _run_case(
        "baseline",
        start_date=window["start"],
        end_date=window["end"],
        base_cfg=base_cfg,
        carrier_cfg=carrier_cfg,
        authority=authority,
    )
    release_zero = _run_case(
        "release_zero",
        start_date=window["start"],
        end_date=window["end"],
        base_cfg=base_cfg,
        carrier_cfg=carrier_cfg,
        authority=authority,
    )

    baseline_rows = baseline.pop("rows")
    release_zero_rows = release_zero.pop("rows")
    baseline_release_rows = baseline.pop("continuation_release_rows")
    release_zero_release_rows = release_zero.pop("continuation_release_rows")

    all_row_diff_count = 0
    action_diff_count = 0
    size_diff_count = 0
    selected_policy_diff_count = 0
    switch_reason_diff_count = 0
    behavioral_row_diff_count = 0
    parameter_only_diff_count = 0
    continuation_release_behavioral_diff_count = 0
    first_action_diff_timestamp: str | None = None

    for ts in sorted(set(baseline_rows) | set(release_zero_rows)):
        baseline_row = baseline_rows.get(ts)
        release_zero_row = release_zero_rows.get(ts)
        if baseline_row == release_zero_row:
            continue
        all_row_diff_count += 1
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
            if first_action_diff_timestamp is None:
                first_action_diff_timestamp = ts
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

    baseline_summary = baseline.get("summary") or {}
    release_summary = release_zero.get("summary") or {}
    baseline_release_timestamps = sorted(baseline_release_rows)
    release_zero_release_timestamps = sorted(release_zero_release_rows)
    topline_changed = _topline_changed(baseline_summary, release_summary)
    total_return_diff = (release_summary.get("total_return") or 0.0) - (
        baseline_summary.get("total_return") or 0.0
    )
    final_capital_diff = (release_summary.get("final_capital") or 0.0) - (
        baseline_summary.get("final_capital") or 0.0
    )
    num_trades_diff = (release_summary.get("num_trades") or 0) - (
        baseline_summary.get("num_trades") or 0
    )

    return {
        "label": window["label"],
        "window_start": window["start"],
        "window_end": window["end"],
        "baseline_execution_mode": baseline.get("execution_mode"),
        "release_zero_execution_mode": release_zero.get("execution_mode"),
        "baseline_bars_processed": baseline.get("bars_processed"),
        "release_zero_bars_processed": release_zero.get("bars_processed"),
        "baseline_summary": baseline_summary,
        "release_zero_summary": release_summary,
        "baseline_position_summary": baseline.get("position_summary"),
        "release_zero_position_summary": release_zero.get("position_summary"),
        "baseline_metrics": baseline.get("metrics"),
        "release_zero_metrics": release_zero.get("metrics"),
        "baseline_config_fingerprint": baseline.get("effective_config_fingerprint"),
        "release_zero_config_fingerprint": release_zero.get("effective_config_fingerprint"),
        "all_row_diff_count": all_row_diff_count,
        "action_diff_count": action_diff_count,
        "size_diff_count": size_diff_count,
        "selected_policy_diff_count": selected_policy_diff_count,
        "switch_reason_diff_count": switch_reason_diff_count,
        "behavioral_row_diff_count": behavioral_row_diff_count,
        "parameter_only_diff_count": parameter_only_diff_count,
        "baseline_continuation_release_row_count": len(baseline_release_timestamps),
        "release_zero_continuation_release_row_count": len(release_zero_release_timestamps),
        "continuation_release_behavioral_diff_count": continuation_release_behavioral_diff_count,
        "baseline_continuation_release_timestamps": baseline_release_timestamps,
        "release_zero_continuation_release_timestamps": release_zero_release_timestamps,
        "topline_changed": topline_changed,
        "total_return_diff": total_return_diff,
        "final_capital_diff": final_capital_diff,
        "num_trades_diff": num_trades_diff,
        "first_action_diff_timestamp": first_action_diff_timestamp,
    }


def _ranking_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        -row["action_diff_count"],
        -int(row["topline_changed"]),
        -abs(row["total_return_diff"]),
        -abs(row["final_capital_diff"]),
        -abs(row["num_trades_diff"]),
        -row["size_diff_count"],
        -row["selected_policy_diff_count"],
        -row["behavioral_row_diff_count"],
        -row["continuation_release_behavioral_diff_count"],
        -row["baseline_continuation_release_row_count"],
        row["window_start"],
    )


def _stable_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _inventory_definition() -> dict[str, Any]:
    return {
        "base_sha": EXPECTED_BASE_SHA,
        "actual_head_sha": HEAD_SHA,
        "local_reproducibility_scope": (
            "bounded local research environment with curated_only data present; "
            "not a clean-checkout CI-hermetic claim"
        ),
        "symbol": SYMBOL,
        "timeframe": TIMEFRAME,
        "warmup": WARMUP,
        "data_source_policy": DATA_SOURCE_POLICY,
        "carrier_config": str(CARRIER_PATH.relative_to(ROOT_DIR)),
        "available_data_bounds": {
            "min": AVAILABLE_DATA_MIN,
            "max": AVAILABLE_DATA_MAX,
        },
        "grid": {
            "family": WINDOW_FAMILY,
            "date_bounds": {
                "start": GRID_START.isoformat(),
                "end": GRID_END.isoformat(),
            },
            "stride_months": STRIDE_MONTHS,
            "max_windows": EXPECTED_MAX_WINDOWS,
            "partial_edge_months_excluded": ["2016-06", "2026-04"],
        },
        "comparison": {
            "baseline": "enabled carrier as-is (implicit shared hysteresis)",
            "release_zero": "same enabled carrier with continuation_release_hysteresis=0",
        },
        "skill_usage": [
            "genesis_backtest_verify",
            "python_engineering",
        ],
        "ranking_tie_break_order": [
            "action_diff_count desc",
            "topline_changed desc",
            "abs(total_return_diff) desc",
            "abs(final_capital_diff) desc",
            "abs(num_trades_diff) desc",
            "size_diff_count desc",
            "selected_policy_diff_count desc",
            "behavioral_row_diff_count desc",
            "continuation_release_behavioral_diff_count desc",
            "baseline_continuation_release_row_count desc",
            "window_start asc",
        ],
        "do_not_repeat": [
            "Do not reopen December 2023 fail-B carrier as a continuation_release subject; it is closed as non-exercising.",
            "Do not treat January 2024 2024-01-01..2024-01-20 as unresolved; it is already closed as exercising-but-topline-null.",
            "Do not use partial-edge months 2016-06 or 2026-04 in this bounded monthly inventory.",
        ],
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


def main() -> int:
    if HEAD_SHA != EXPECTED_BASE_SHA:
        raise SystemExit(f"Base SHA drifted: expected {EXPECTED_BASE_SHA}, actual {HEAD_SHA}")

    base_cfg, carrier_cfg, authority = _load_base_and_carrier_cfg()
    windows = _month_windows()
    window_rows = [
        _window_compare(window, base_cfg=base_cfg, carrier_cfg=carrier_cfg, authority=authority)
        for window in windows
    ]

    seam_active_windows = [
        row
        for row in window_rows
        if row["baseline_continuation_release_row_count"] > 0
        or row["release_zero_continuation_release_row_count"] > 0
        or row["continuation_release_behavioral_diff_count"] > 0
    ]
    ranked_windows = sorted(seam_active_windows, key=_ranking_key)
    for index, row in enumerate(ranked_windows, start=1):
        row["rank"] = index

    inventory_definition = _inventory_definition()
    normalized_summary = {
        "inventory_definition": inventory_definition,
        "window_count": len(window_rows),
        "seam_active_window_count": len(seam_active_windows),
        "ranked_windows": ranked_windows[:TOP_WINDOW_LIMIT],
    }
    normalized_summary_hash = _stable_hash(normalized_summary)

    summary_payload = {
        **normalized_summary,
        "normalized_summary_hash": normalized_summary_hash,
    }

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")
    WINDOWS_PATH.write_text(json.dumps(window_rows, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "summary_artifact": str(SUMMARY_PATH),
                "windows_artifact": str(WINDOWS_PATH),
                "window_count": len(window_rows),
                "seam_active_window_count": len(seam_active_windows),
                "top_ranked_window": ranked_windows[0] if ranked_windows else None,
                "normalized_summary_hash": normalized_summary_hash,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
