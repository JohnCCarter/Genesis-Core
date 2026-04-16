#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


def _find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "pyproject.toml").exists() and (candidate / "src").exists():
            return candidate
    raise RuntimeError("Could not locate repository root")


ROOT_DIR = _find_repo_root(Path(__file__).resolve())
SRC_DIR = ROOT_DIR / "src"
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from core.backtest.metrics import calculate_metrics  # noqa: E402
from core.config.authority import ConfigAuthority  # noqa: E402
from core.optimizer.scoring import score_backtest  # noqa: E402
from core.pipeline import GenesisPipeline  # noqa: E402

HEAD_PIN = "8e23ddb45d08784e8a8a340f83334f5842505e0e"
DEFAULT_CANDIDATE_900_CONFIG = (
    ROOT_DIR
    / "results"
    / "research"
    / "fa_v2_adaptation_off"
    / "phase15_bull_high_persistence_override"
    / "current_atr_selective_900_validation_2026-04-15"
    / "candidate_900_cfg.json"
)
DEFAULT_ENV_PROFILE_SUMMARY = (
    ROOT_DIR
    / "results"
    / "research"
    / "fa_v2_adaptation_off"
    / "phase15_bull_high_persistence_override"
    / "current_atr_900_env_profile_2026-04-16"
    / "env_summary.json"
)
CANONICAL_ENV = {
    "GENESIS_RANDOM_SEED": "42",
    "GENESIS_FAST_WINDOW": "1",
    "GENESIS_PRECOMPUTE_FEATURES": "1",
    "GENESIS_MODE_EXPLICIT": "1",
    "GENESIS_FAST_HASH": "0",
    "SYMBOL_MODE": "realistic",
}
YEAR_WINDOWS = {
    "2024": ("2024-01-02", "2024-12-31"),
    "2025": ("2025-01-01", "2025-12-31"),
}
SIZE_TOLERANCE = 1e-12


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _normalize_timestamp(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    iso = getattr(value, "isoformat", None)
    if callable(iso):
        try:
            return str(iso())
        except Exception:
            return str(value)
    return str(value)


def _extract_decision_reasons(meta: dict[str, Any]) -> list[Any]:
    decision = (meta or {}).get("decision") or {}
    reasons = decision.get("reasons")
    if reasons is None:
        return []
    if isinstance(reasons, list):
        return reasons
    return [reasons]


def _extract_decision_size(meta: dict[str, Any]) -> float | None:
    decision = (meta or {}).get("decision") or {}
    raw_size = decision.get("size")
    if raw_size is None:
        return None
    try:
        return float(raw_size)
    except (TypeError, ValueError):
        return None


def _build_decision_row(
    *,
    symbol: str,
    timeframe: str,
    result: dict[str, Any],
    meta: dict[str, Any],
    candles: dict[str, Any],
) -> dict[str, Any]:
    timestamps = candles.get("timestamp") or []
    timestamp_value = timestamps[-1] if timestamps else None
    bar_index = candles.get("bar_index")
    action = str((result or {}).get("action") or "").strip().upper()
    reasons = _extract_decision_reasons(meta)
    size = _extract_decision_size(meta)
    return {
        "row_id": f"{symbol}|{timeframe}|{bar_index}",
        "bar_index": bar_index,
        "timestamp": _normalize_timestamp(timestamp_value),
        "symbol": symbol,
        "timeframe": timeframe,
        "action": action,
        "reasons": reasons,
        "size": size,
    }


def _compose_decision_row_capture_hook(
    *,
    symbol: str,
    timeframe: str,
    row_sink: list[dict[str, Any]],
    upstream_hook: Any | None,
):
    def hook(result: dict[str, Any], meta: dict[str, Any], candles: dict[str, Any]):
        if upstream_hook is not None:
            result, meta = upstream_hook(result, meta, candles)

        row_sink.append(
            _build_decision_row(
                symbol=symbol,
                timeframe=timeframe,
                result=result if isinstance(result, dict) else {},
                meta=meta if isinstance(meta, dict) else {},
                candles=candles if isinstance(candles, dict) else {},
            )
        )
        return result, meta

    return hook


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in (override or {}).items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _load_effective_config(config_file: Path) -> dict[str, Any]:
    authority = ConfigAuthority()
    runtime_cfg_obj, _, _runtime_version = authority.get()
    runtime_cfg = runtime_cfg_obj.model_dump()
    payload = json.loads(config_file.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("config file must be a JSON object")

    merged_cfg = payload.get("merged_config")
    if isinstance(merged_cfg, dict):
        validated = authority.validate(merged_cfg)
        return validated.model_dump()

    override_cfg = payload.get("cfg") or payload.get("parameters")
    if not isinstance(override_cfg, dict):
        raise ValueError("config file must contain 'merged_config' or 'cfg'")

    merged = _deep_merge(runtime_cfg, override_cfg)
    validated = authority.validate(merged)
    return validated.model_dump()


def _relative_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT_DIR.resolve()).as_posix()


def _normalize_rel_path(value: str) -> str:
    return value.replace("\\", "/").strip()


def _run_git_command(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT_DIR,
        check=True,
        capture_output=True,
        text=True,
    )


def _resolve_git_sha() -> str:
    try:
        return _run_git_command("rev-parse", "HEAD").stdout.strip()
    except Exception as exc:
        raise RuntimeError("Unable to resolve git HEAD") from exc


def _get_git_status_short() -> list[str]:
    completed = _run_git_command("status", "--short")
    lines = [line.rstrip() for line in completed.stdout.splitlines() if line.strip()]
    return lines


def _extract_status_paths(status_line: str) -> list[str]:
    if len(status_line) < 4:
        return []
    payload = status_line[3:].strip()
    if not payload:
        return []
    if " -> " in payload:
        before, after = payload.split(" -> ", 1)
        return [_normalize_rel_path(before), _normalize_rel_path(after)]
    return [_normalize_rel_path(payload)]


def _validate_clean_preflight(
    *,
    status_lines: list[str],
    allowed_scope_paths: set[str],
) -> None:
    out_of_scope: list[dict[str, Any]] = []
    for line in status_lines:
        paths = _extract_status_paths(line)
        if not paths:
            continue
        if any(path not in allowed_scope_paths for path in paths):
            out_of_scope.append({"status": line[:2], "paths": paths, "raw": line})
    if out_of_scope:
        raise RuntimeError(
            "Preflight blocked: working tree already has modified or untracked paths outside "
            "this packet scope: " + json.dumps(out_of_scope, indent=2)
        )


def _apply_canonical_env() -> dict[str, str]:
    resolved: dict[str, str] = {}
    for key, value in CANONICAL_ENV.items():
        if not str(os.environ.get(key, "")).strip():
            os.environ[key] = value
        resolved[key] = str(os.environ.get(key, "")).strip()
    missing = [key for key, value in resolved.items() if not value]
    if missing:
        raise RuntimeError(
            "Missing required replay-affecting environment values after canonical env apply: "
            + ", ".join(missing)
        )
    return resolved


def _snapshot_path_entries(paths: list[Path]) -> dict[str, dict[str, int]]:
    snapshot: dict[str, dict[str, int]] = {}
    for path in paths:
        resolved = path.resolve()
        if resolved.is_file():
            stat = resolved.stat()
            snapshot[_relative_path(resolved)] = {
                "size": int(stat.st_size),
                "mtime_ns": int(stat.st_mtime_ns),
            }
            continue
        if not resolved.exists():
            continue
        for file_path in sorted(item for item in resolved.rglob("*") if item.is_file()):
            stat = file_path.stat()
            snapshot[_relative_path(file_path)] = {
                "size": int(stat.st_size),
                "mtime_ns": int(stat.st_mtime_ns),
            }
    return snapshot


def _diff_snapshots(
    before: dict[str, dict[str, int]],
    after: dict[str, dict[str, int]],
) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for rel_path in sorted(set(before) | set(after)):
        if rel_path not in before:
            events.append({"path": rel_path, "event": "create"})
            continue
        if rel_path not in after:
            events.append({"path": rel_path, "event": "delete"})
            continue
        if before[rel_path] != after[rel_path]:
            events.append({"path": rel_path, "event": "modify"})
    return events


def _ensure_output_scope(output_dir: Path, approved_files: list[Path]) -> None:
    output_dir_resolved = output_dir.resolve()
    approved_resolved = {item.resolve() for item in approved_files}
    for file_path in approved_files:
        resolved = file_path.resolve()
        if resolved.parent != output_dir_resolved:
            raise ValueError(
                f"Approved output file must live directly under output_dir: {file_path}"
            )
    if output_dir.exists():
        unexpected = [
            _relative_path(path)
            for path in output_dir.rglob("*")
            if path.is_file() and path.resolve() not in approved_resolved
        ]
        if unexpected:
            raise RuntimeError(
                "Output directory already contains unexpected files outside packet scope: "
                + ", ".join(unexpected)
            )


def _clone_config_with_threshold(source_cfg: dict[str, Any], threshold: float) -> dict[str, Any]:
    cloned = json.loads(json.dumps(source_cfg))
    mtf_cfg = cloned.setdefault("multi_timeframe", {})
    override_cfg = mtf_cfg.setdefault(
        "research_current_atr_high_vol_multiplier_override",
        {
            "enabled": True,
            "current_atr_threshold": threshold,
            "high_vol_multiplier_override": 1.0,
        },
    )
    override_cfg["enabled"] = True
    override_cfg["current_atr_threshold"] = float(threshold)
    override_cfg["high_vol_multiplier_override"] = 1.0
    return cloned


def _build_candidate_config_artifact(
    *,
    candidate_900_payload: dict[str, Any],
    candidate_900_rel: str,
    env_profile_summary_rel: str,
    git_sha: str,
    threshold: float,
    candidate_cfg: dict[str, Any],
) -> dict[str, Any]:
    artifact = json.loads(json.dumps(candidate_900_payload))
    metadata = dict(artifact.get("metadata") or {})
    metadata["source_candidate_900_config"] = candidate_900_rel
    metadata["env_profile_summary_source"] = env_profile_summary_rel
    metadata["intended_effective_delta"] = [
        "multi_timeframe.research_current_atr_high_vol_multiplier_override.enabled=true",
        (
            "multi_timeframe.research_current_atr_high_vol_multiplier_override"
            f".current_atr_threshold={float(threshold)}"
        ),
        (
            "multi_timeframe.research_current_atr_high_vol_multiplier_override"
            ".high_vol_multiplier_override=1.0"
        ),
    ]
    metadata["note"] = (
        "Dedicated 1435.209570 policy-validation candidate cloned from the approved 900 "
        "candidate config for observational research only."
    )
    artifact["created_at"] = "2026-04-16T00:00:00Z"
    artifact["run_id"] = (
        "research_bull_high_persistence_override_3h_min_size_001_"
        "current_atr_selective_vol_mult_1435_policy_validation"
    )
    artifact["git_commit"] = git_sha
    artifact["score"] = 0.0
    artifact["metrics"] = {}
    artifact["metadata"] = metadata
    artifact["cfg"] = candidate_cfg
    return artifact


def _run_variant(
    *,
    symbol: str,
    timeframe: str,
    start_date: str,
    end_date: str,
    cfg: dict[str, Any],
) -> dict[str, Any]:
    pipeline = GenesisPipeline()
    defaults = pipeline.defaults
    seed_value = int(os.environ.get("GENESIS_RANDOM_SEED", "42"))
    pipeline.setup_environment(seed=seed_value)

    warmup_bars = int(cfg.get("warmup_bars", defaults.get("warmup", 120)) or 0)
    engine = pipeline.create_engine(
        symbol=symbol,
        timeframe=timeframe,
        start_date=start_date,
        end_date=end_date,
        capital=float(defaults.get("capital", 10000.0)),
        commission=float(defaults.get("commission", 0.002)),
        slippage=float(defaults.get("slippage", 0.0005)),
        warmup_bars=warmup_bars,
    )

    decision_rows: list[dict[str, Any]] = []
    engine.evaluation_hook = _compose_decision_row_capture_hook(
        symbol=symbol,
        timeframe=timeframe,
        row_sink=decision_rows,
        upstream_hook=engine.evaluation_hook,
    )

    if not engine.load_data():
        raise RuntimeError("engine.load_data() failed")

    results = engine.run(
        policy={"symbol": symbol, "timeframe": timeframe},
        configs=cfg,
        verbose=False,
    )
    if "error" in results:
        raise RuntimeError(str(results["error"]))

    metrics = calculate_metrics(results, prefer_summary=False)
    score_payload = score_backtest(results)
    return {
        "decision_rows": decision_rows,
        "metrics": {
            "score": float(score_payload.get("score") or 0.0),
            "total_pnl": float(metrics.get("total_pnl", 0.0) or 0.0),
            "return_pct": float(metrics.get("total_return", 0.0) or 0.0),
            "win_rate": float(metrics.get("win_rate", 0.0) or 0.0),
            "max_drawdown_pct": float(metrics.get("max_drawdown_pct", 0.0) or 0.0),
            "profit_factor": float(metrics.get("profit_factor", 0.0) or 0.0),
            "trade_count": int(metrics.get("total_trades", 0) or 0),
        },
    }


def _normalize_reason_value(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _compare_decision_rows(
    rows_a: list[dict[str, Any]],
    rows_b: list[dict[str, Any]],
    *,
    sample_limit: int = 10,
) -> dict[str, Any]:
    map_a = {str(row.get("row_id")): row for row in rows_a}
    map_b = {str(row.get("row_id")): row for row in rows_b}

    changed_count = 0
    action_changes = 0
    reason_changes = 0
    size_changes = 0
    added_count = 0
    removed_count = 0
    sample: list[dict[str, Any]] = []

    for row_id in sorted(set(map_a) | set(map_b)):
        row_a = map_a.get(row_id)
        row_b = map_b.get(row_id)
        if row_a is None:
            changed_count += 1
            added_count += 1
            if len(sample) < sample_limit:
                sample.append(
                    {
                        "row_id": row_id,
                        "event": "added",
                        "timestamp": row_b.get("timestamp") if row_b else "",
                    }
                )
            continue
        if row_b is None:
            changed_count += 1
            removed_count += 1
            if len(sample) < sample_limit:
                sample.append(
                    {
                        "row_id": row_id,
                        "event": "removed",
                        "timestamp": row_a.get("timestamp") if row_a else "",
                    }
                )
            continue

        action_diff = str(row_a.get("action") or "") != str(row_b.get("action") or "")
        reasons_diff = _normalize_reason_value(row_a.get("reasons")) != _normalize_reason_value(
            row_b.get("reasons")
        )
        size_a = row_a.get("size")
        size_b = row_b.get("size")
        if size_a is None and size_b is None:
            size_diff = False
        elif size_a is None or size_b is None:
            size_diff = True
        else:
            size_diff = abs(float(size_a) - float(size_b)) > SIZE_TOLERANCE

        if action_diff or reasons_diff or size_diff:
            changed_count += 1
            action_changes += int(action_diff)
            reason_changes += int(reasons_diff)
            size_changes += int(size_diff)
            if len(sample) < sample_limit:
                sample.append(
                    {
                        "row_id": row_id,
                        "timestamp": row_a.get("timestamp") or row_b.get("timestamp") or "",
                        "action_a": row_a.get("action"),
                        "action_b": row_b.get("action"),
                        "size_a": size_a,
                        "size_b": size_b,
                        "reasons_a": row_a.get("reasons"),
                        "reasons_b": row_b.get("reasons"),
                    }
                )

    return {
        "changed_count": changed_count,
        "action_changes": action_changes,
        "reason_changes": reason_changes,
        "size_changes": size_changes,
        "added_count": added_count,
        "removed_count": removed_count,
        "sample": sample,
    }


def _activation_set(
    reference_rows: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
) -> set[str]:
    reference_map = {str(row.get("row_id")): row for row in reference_rows}
    candidate_map = {str(row.get("row_id")): row for row in candidate_rows}
    active: set[str] = set()
    for row_id in set(reference_map) | set(candidate_map):
        row_ref = reference_map.get(row_id)
        row_candidate = candidate_map.get(row_id)
        if row_ref is None or row_candidate is None:
            active.add(row_id)
            continue
        size_ref = row_ref.get("size")
        size_candidate = row_candidate.get("size")
        if size_ref is None and size_candidate is None:
            continue
        if size_ref is None or size_candidate is None:
            active.add(row_id)
            continue
        if abs(float(size_ref) - float(size_candidate)) > SIZE_TOLERANCE:
            active.add(row_id)
    return active


def _compare_activation_sets(
    *,
    reference_rows: list[dict[str, Any]],
    candidate_900_rows: list[dict[str, Any]],
    candidate_1435_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    active_900 = _activation_set(reference_rows, candidate_900_rows)
    active_1435 = _activation_set(reference_rows, candidate_1435_rows)
    return {
        "derivation": "size_delta_vs_baseline_090",
        "candidate_900_active_count": len(active_900),
        "candidate_1435_active_count": len(active_1435),
        "shared_active_count": len(active_900 & active_1435),
        "candidate_900_only_count": len(active_900 - active_1435),
        "candidate_1435_only_count": len(active_1435 - active_900),
    }


def _metric_deltas(base: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    return {
        "score": float(target["score"] - base["score"]),
        "total_pnl": float(target["total_pnl"] - base["total_pnl"]),
        "return_pct": float(target["return_pct"] - base["return_pct"]),
        "win_rate": float(target["win_rate"] - base["win_rate"]),
        "max_drawdown_pct": float(target["max_drawdown_pct"] - base["max_drawdown_pct"]),
        "profit_factor": float(target["profit_factor"] - base["profit_factor"]),
        "trade_count": int(target["trade_count"] - base["trade_count"]),
    }


def _build_year_summary(
    *,
    year: str,
    symbol: str,
    timeframe: str,
    baseline_cfg: dict[str, Any],
    candidate_900_cfg: dict[str, Any],
    candidate_1435_cfg: dict[str, Any],
    always_100_cfg: dict[str, Any],
) -> dict[str, Any]:
    start_date, end_date = YEAR_WINDOWS[year]
    baseline_payload = _run_variant(
        symbol=symbol,
        timeframe=timeframe,
        start_date=start_date,
        end_date=end_date,
        cfg=baseline_cfg,
    )
    candidate_900_payload = _run_variant(
        symbol=symbol,
        timeframe=timeframe,
        start_date=start_date,
        end_date=end_date,
        cfg=candidate_900_cfg,
    )
    candidate_1435_payload = _run_variant(
        symbol=symbol,
        timeframe=timeframe,
        start_date=start_date,
        end_date=end_date,
        cfg=candidate_1435_cfg,
    )
    always_100_payload = _run_variant(
        symbol=symbol,
        timeframe=timeframe,
        start_date=start_date,
        end_date=end_date,
        cfg=always_100_cfg,
    )

    baseline_metrics = baseline_payload["metrics"]
    candidate_900_metrics = candidate_900_payload["metrics"]
    candidate_1435_metrics = candidate_1435_payload["metrics"]
    always_100_metrics = always_100_payload["metrics"]

    return {
        "window": {"start_date": start_date, "end_date": end_date},
        "variants": {
            "baseline_090": baseline_metrics,
            "candidate_900": candidate_900_metrics,
            "candidate_1435": candidate_1435_metrics,
            "always_100": always_100_metrics,
        },
        "candidate_900": {
            "threshold": 900.0,
            "delta_vs_baseline_090": _metric_deltas(baseline_metrics, candidate_900_metrics),
            "delta_vs_always_100": _metric_deltas(always_100_metrics, candidate_900_metrics),
            "diff_vs_baseline_090": _compare_decision_rows(
                baseline_payload["decision_rows"],
                candidate_900_payload["decision_rows"],
            ),
            "diff_vs_always_100": _compare_decision_rows(
                always_100_payload["decision_rows"],
                candidate_900_payload["decision_rows"],
            ),
        },
        "candidate_1435": {
            "threshold": 1435.20957,
            "delta_vs_baseline_090": _metric_deltas(baseline_metrics, candidate_1435_metrics),
            "delta_vs_candidate_900": _metric_deltas(candidate_900_metrics, candidate_1435_metrics),
            "delta_vs_always_100": _metric_deltas(always_100_metrics, candidate_1435_metrics),
            "diff_vs_baseline_090": _compare_decision_rows(
                baseline_payload["decision_rows"],
                candidate_1435_payload["decision_rows"],
            ),
            "diff_vs_candidate_900": _compare_decision_rows(
                candidate_900_payload["decision_rows"],
                candidate_1435_payload["decision_rows"],
            ),
            "diff_vs_always_100": _compare_decision_rows(
                always_100_payload["decision_rows"],
                candidate_1435_payload["decision_rows"],
            ),
            "override_activation_comparison_vs_candidate_900": _compare_activation_sets(
                reference_rows=baseline_payload["decision_rows"],
                candidate_900_rows=candidate_900_payload["decision_rows"],
                candidate_1435_rows=candidate_1435_payload["decision_rows"],
            ),
        },
    }


def _render_metrics_table(year_payload: dict[str, Any]) -> str:
    variants = year_payload["variants"]
    lines = [
        "| Variant | Score | Total PnL | Return | Win rate | Max DD | PF | Trades |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for label, key in (
        ("baseline `0.90`", "baseline_090"),
        ("candidate `900`", "candidate_900"),
        ("candidate `1435.209570`", "candidate_1435"),
        ("always `1.00`", "always_100"),
    ):
        metrics = variants[key]
        lines.append(
            "| "
            + label
            + " | "
            + f"`{metrics['score']:.4f}` | "
            + f"`{metrics['total_pnl']:.4f}` | "
            + f"`{metrics['return_pct']:.2f}%` | "
            + f"`{metrics['win_rate']:.2f}%` | "
            + f"`{metrics['max_drawdown_pct']:.2f}%` | "
            + f"`{metrics['profit_factor']:.2f}` | "
            + f"`{metrics['trade_count']}` |"
        )
    return "\n".join(lines)


def _render_activation_summary(year_payload: dict[str, Any]) -> str:
    activation = year_payload["candidate_1435"]["override_activation_comparison_vs_candidate_900"]
    lines = [
        "| Activation-set comparison | Count |",
        "| --- | ---: |",
        f"| candidate `900` active rows | `{activation['candidate_900_active_count']}` |",
        f"| candidate `1435` active rows | `{activation['candidate_1435_active_count']}` |",
        f"| shared active rows | `{activation['shared_active_count']}` |",
        f"| `900`-only active rows | `{activation['candidate_900_only_count']}` |",
        f"| `1435`-only active rows | `{activation['candidate_1435_only_count']}` |",
        "",
        f"Derivation: `{activation['derivation']}`",
    ]
    return "\n".join(lines)


def _build_recommendation(summary: dict[str, Any]) -> dict[str, str]:
    y2024 = summary["years"].get("2024")
    y2025 = summary["years"].get("2025")
    if not y2024 or not y2025:
        return {
            "recommendation": "retain baseline",
            "rationale": "Incomplete year coverage prevents a packet-compliant recommendation.",
        }

    c1435_2024 = y2024["variants"]["candidate_1435"]
    c1435_2025 = y2025["variants"]["candidate_1435"]
    c900_2024 = y2024["variants"]["candidate_900"]
    c900_2025 = y2025["variants"]["candidate_900"]
    baseline_2024 = y2024["variants"]["baseline_090"]
    baseline_2025 = y2025["variants"]["baseline_090"]
    activation_2025 = y2025["candidate_1435"]["override_activation_comparison_vs_candidate_900"]

    stronger_than_baseline = (
        c1435_2024["score"] > baseline_2024["score"]
        and c1435_2025["score"] > baseline_2025["score"]
    )
    stronger_than_900_on_blind = c1435_2025["score"] >= c900_2025["score"]
    narrower_than_900 = (
        activation_2025["candidate_1435_active_count"]
        < activation_2025["candidate_900_active_count"]
    )

    if stronger_than_baseline and stronger_than_900_on_blind and narrower_than_900:
        return {
            "recommendation": "carry 1435 forward as narrower research candidate",
            "rationale": (
                "Candidate 1435 stays above baseline on both windows while matching or beating "
                "candidate 900 on the blind 2025 window with a narrower activation set."
            ),
        }

    if c900_2024["score"] > c1435_2024["score"] or c900_2025["score"] > c1435_2025["score"]:
        return {
            "recommendation": "retain 900 as stronger bounded candidate",
            "rationale": (
                "Candidate 1435 does not clearly dominate the already-validated 900 candidate "
                "across the discovery/blind comparison surface."
            ),
        }

    return {
        "recommendation": "retain baseline",
        "rationale": (
            "Neither narrowed candidate evidence nor bounded-candidate comparison clears the bar "
            "above the locked baseline strongly enough for the next policy step."
        ),
    }


def _build_closeout(summary: dict[str, Any]) -> str:
    recommendation = _build_recommendation(summary)
    lines = [
        "# Current-ATR 1435 policy validation",
        "",
        "Date: 2026-04-16",
        "Mode: RESEARCH",
        f"Branch/commit: `{summary['git_sha']}`",
        "",
        "## Purpose",
        "",
        (
            "Run a dedicated replay-validation for the narrowed runtime-implementable policy "
            "candidate `current_atr >= 1435.209570`, compared against locked baseline `0.90`, "
            "the already validated `900` candidate, and an always-`1.00` anchor."
        ),
        "",
        "## Sources",
        "",
        f"- candidate `900` source: `{summary['candidate_900_source']}`",
        f"- observational discovery summary: `{summary['env_profile_summary_source']}`",
        f"- candidate `1435` artifact: `{summary['candidate_config_artifact']}`",
    ]

    for year, year_payload in summary["years"].items():
        candidate_1435 = year_payload["candidate_1435"]
        lines.extend(
            [
                "",
                f"## {year}",
                "",
                f"Window: `{year_payload['window']['start_date']}` -> `{year_payload['window']['end_date']}`",
                "",
                _render_metrics_table(year_payload),
                "",
                "### Candidate `1435.209570` deltas",
                "",
                (
                    "- vs baseline `0.90`: "
                    f"score `{candidate_1435['delta_vs_baseline_090']['score']:+.4f}`, "
                    f"total pnl `{candidate_1435['delta_vs_baseline_090']['total_pnl']:+.4f}`, "
                    f"return `{candidate_1435['delta_vs_baseline_090']['return_pct']:+.2f}pp`, "
                    f"win rate `{candidate_1435['delta_vs_baseline_090']['win_rate']:+.2f}pp`, "
                    f"max DD `{candidate_1435['delta_vs_baseline_090']['max_drawdown_pct']:+.2f}pp`, "
                    f"PF `{candidate_1435['delta_vs_baseline_090']['profit_factor']:+.2f}`"
                ),
                (
                    "- vs candidate `900`: "
                    f"score `{candidate_1435['delta_vs_candidate_900']['score']:+.4f}`, "
                    f"total pnl `{candidate_1435['delta_vs_candidate_900']['total_pnl']:+.4f}`, "
                    f"return `{candidate_1435['delta_vs_candidate_900']['return_pct']:+.2f}pp`, "
                    f"win rate `{candidate_1435['delta_vs_candidate_900']['win_rate']:+.2f}pp`, "
                    f"max DD `{candidate_1435['delta_vs_candidate_900']['max_drawdown_pct']:+.2f}pp`, "
                    f"PF `{candidate_1435['delta_vs_candidate_900']['profit_factor']:+.2f}`"
                ),
                "",
                "### Decision drift",
                "",
                (
                    "- vs baseline `0.90`: "
                    f"changed rows `{candidate_1435['diff_vs_baseline_090']['changed_count']}`, "
                    f"action drift `{candidate_1435['diff_vs_baseline_090']['action_changes']}`, "
                    f"reason drift `{candidate_1435['diff_vs_baseline_090']['reason_changes']}`, "
                    f"size drift `{candidate_1435['diff_vs_baseline_090']['size_changes']}`"
                ),
                (
                    "- vs candidate `900`: "
                    f"changed rows `{candidate_1435['diff_vs_candidate_900']['changed_count']}`, "
                    f"action drift `{candidate_1435['diff_vs_candidate_900']['action_changes']}`, "
                    f"reason drift `{candidate_1435['diff_vs_candidate_900']['reason_changes']}`, "
                    f"size drift `{candidate_1435['diff_vs_candidate_900']['size_changes']}`"
                ),
                "",
                "### Override activation comparison vs `900`",
                "",
                _render_activation_summary(year_payload),
            ]
        )

    y2024 = summary["years"].get("2024")
    y2025 = summary["years"].get("2025")
    if y2024 and y2025:
        lines.extend(
            [
                "",
                "## Expected conclusion questions",
                "",
                (
                    "- Does `candidate_1435` outperform baseline `0.90`? "
                    f"2024=`{'yes' if y2024['variants']['candidate_1435']['score'] > y2024['variants']['baseline_090']['score'] else 'no'}`, "
                    f"2025=`{'yes' if y2025['variants']['candidate_1435']['score'] > y2025['variants']['baseline_090']['score'] else 'no'}`."
                ),
                (
                    "- Does it improve or degrade versus `candidate_900`? "
                    f"2024 score delta=`{y2024['candidate_1435']['delta_vs_candidate_900']['score']:+.4f}`, "
                    f"2025 score delta=`{y2025['candidate_1435']['delta_vs_candidate_900']['score']:+.4f}`."
                ),
                (
                    "- Does it merely concentrate uplift into fewer trades? "
                    f"2024 activation rows `1435={y2024['candidate_1435']['override_activation_comparison_vs_candidate_900']['candidate_1435_active_count']}` vs "
                    f"`900={y2024['candidate_1435']['override_activation_comparison_vs_candidate_900']['candidate_900_active_count']}`, "
                    f"2025 activation rows `1435={y2025['candidate_1435']['override_activation_comparison_vs_candidate_900']['candidate_1435_active_count']}` vs "
                    f"`900={y2025['candidate_1435']['override_activation_comparison_vs_candidate_900']['candidate_900_active_count']}`."
                ),
                (
                    "- Is the result stable enough to justify a later, separate deployment-policy discussion? "
                    f"Packet recommendation: `{recommendation['recommendation']}`."
                ),
            ]
        )

    lines.extend(
        [
            "",
            "## Recommendation",
            "",
            f"- `{recommendation['recommendation']}`",
            f"- {recommendation['rationale']}",
            "",
            "## Evidence discipline",
            "",
            "- This note is observational replay research only.",
            "- It does not change runtime defaults or recommend direct deployment.",
            "- Any later policy or runtime proposal must happen through a separate packeted slice.",
        ]
    )
    return "\n".join(lines) + "\n"


def _build_manifest(
    *,
    args: argparse.Namespace,
    git_sha: str,
    pre_git_status_short: list[str],
    post_git_status_short: list[str],
    env_values: dict[str, str],
    approved_files: list[Path],
    watched_paths: list[Path],
    diff_events: list[dict[str, Any]],
    anchor_sources: dict[str, str],
) -> dict[str, Any]:
    approved_rel = [_relative_path(path) for path in approved_files]
    unexpected_events = [event for event in diff_events if event["path"] not in approved_rel]
    return {
        "git_sha": git_sha,
        "head_pin": HEAD_PIN,
        "command_line": [sys.executable, *sys.argv],
        "effective_env": env_values,
        "preflight_git_status_short": pre_git_status_short,
        "postflight_git_status_short": post_git_status_short,
        "approved_output_dir": _relative_path(args.output_dir),
        "approved_output_files": approved_rel,
        "written_files": approved_rel,
        "candidate_1435_threshold": float(args.threshold),
        "years": list(args.years),
        "anchor_sources": anchor_sources,
        "env_profile_summary_source": _relative_path(args.env_profile_summary),
        "watched_paths": [_relative_path(path) for path in watched_paths if path.exists()],
        "containment": {
            "verdict": "PASS" if not unexpected_events else "FAIL",
            "events": diff_events,
            "unexpected_events": unexpected_events,
            "allowed_change_rule": (
                "Only the approved output files may be created or modified; cache or audit-log "
                "side effects must still appear explicitly in events and become failures unless "
                "they are packet-approved output files."
            ),
        },
        "evidence_note": (
            "This validation is observational replay research only and does not change default behavior."
        ),
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a dedicated replay validation for the current_atr >= 1435.209570 candidate"
    )
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--timeframe", required=True)
    parser.add_argument("--years", nargs="+", required=True, choices=sorted(YEAR_WINDOWS))
    parser.add_argument("--threshold", required=True, type=float)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--manifest-out", required=True, type=Path)
    parser.add_argument("--summary-out", required=True, type=Path)
    parser.add_argument("--closeout-out", required=True, type=Path)
    parser.add_argument("--config-out", required=True, type=Path)
    parser.add_argument(
        "--candidate-900-config",
        type=Path,
        default=DEFAULT_CANDIDATE_900_CONFIG,
        help="Existing candidate_900 config JSON artifact to use as the anchor source.",
    )
    parser.add_argument(
        "--env-profile-summary",
        type=Path,
        default=DEFAULT_ENV_PROFILE_SUMMARY,
        help="Observational env-profile summary artifact to cite in the dedicated validation outputs.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    approved_files = [args.manifest_out, args.summary_out, args.closeout_out, args.config_out]
    _ensure_output_scope(args.output_dir, approved_files)

    git_sha = _resolve_git_sha()
    if git_sha != HEAD_PIN:
        raise RuntimeError(
            f"HEAD pin mismatch: expected {HEAD_PIN}, got {git_sha}. Refuse to run fail-closed."
        )

    allowed_scope_paths = {
        _normalize_rel_path(
            _relative_path(
                ROOT_DIR
                / "docs"
                / "governance"
                / "current_atr_1435_policy_validation_packet_2026-04-16.md"
            )
        ),
        _normalize_rel_path(_relative_path(Path(__file__))),
        *{_normalize_rel_path(_relative_path(path)) for path in approved_files},
    }
    pre_git_status_short = _get_git_status_short()
    _validate_clean_preflight(
        status_lines=pre_git_status_short,
        allowed_scope_paths=allowed_scope_paths,
    )

    env_values = _apply_canonical_env()
    watched_paths = [
        args.output_dir,
        ROOT_DIR / "config" / "runtime.json",
        ROOT_DIR / "config" / "strategy",
        ROOT_DIR / "logs" / "config_audit.jsonl",
        ROOT_DIR / "cache",
    ]
    pre_snapshot = _snapshot_path_entries(watched_paths)

    candidate_900_payload = json.loads(args.candidate_900_config.read_text(encoding="utf-8"))
    if not isinstance(candidate_900_payload, dict):
        raise ValueError("candidate_900 config payload must be a JSON object")

    metadata = dict(candidate_900_payload.get("metadata") or {})
    baseline_source = metadata.get("baseline_source")
    if not isinstance(baseline_source, str):
        raise ValueError("candidate_900 metadata must include baseline_source")

    baseline_cfg = _load_effective_config(ROOT_DIR / baseline_source)
    candidate_900_cfg = _load_effective_config(args.candidate_900_config)
    candidate_1435_cfg = _clone_config_with_threshold(candidate_900_cfg, args.threshold)
    always_100_cfg = _clone_config_with_threshold(candidate_900_cfg, 0.0)

    artifact_cfg_source = candidate_900_payload.get("cfg")
    if isinstance(artifact_cfg_source, dict):
        candidate_artifact_cfg = _clone_config_with_threshold(artifact_cfg_source, args.threshold)
    else:
        candidate_artifact_cfg = candidate_1435_cfg

    args.output_dir.mkdir(parents=True, exist_ok=True)
    config_artifact = _build_candidate_config_artifact(
        candidate_900_payload=candidate_900_payload,
        candidate_900_rel=_relative_path(args.candidate_900_config),
        env_profile_summary_rel=_relative_path(args.env_profile_summary),
        git_sha=git_sha,
        threshold=args.threshold,
        candidate_cfg=candidate_artifact_cfg,
    )
    args.config_out.write_text(json.dumps(config_artifact, indent=2), encoding="utf-8")

    summary = {
        "git_sha": git_sha,
        "symbol": args.symbol,
        "timeframe": args.timeframe,
        "threshold": float(args.threshold),
        "candidate_900_source": _relative_path(args.candidate_900_config),
        "env_profile_summary_source": _relative_path(args.env_profile_summary),
        "candidate_config_artifact": _relative_path(args.config_out),
        "anchor_sources": {
            "baseline_090": baseline_source,
            "candidate_900": _relative_path(args.candidate_900_config),
            "always_100": "derived_in_process_from_candidate_900_cfg_with_threshold_0.0",
        },
        "years": {},
    }
    for year in args.years:
        summary["years"][year] = _build_year_summary(
            year=year,
            symbol=args.symbol,
            timeframe=args.timeframe,
            baseline_cfg=baseline_cfg,
            candidate_900_cfg=candidate_900_cfg,
            candidate_1435_cfg=candidate_1435_cfg,
            always_100_cfg=always_100_cfg,
        )

    args.summary_out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    args.closeout_out.write_text(_build_closeout(summary), encoding="utf-8")
    args.manifest_out.write_text("{}\n", encoding="utf-8")

    diff_events = _diff_snapshots(pre_snapshot, _snapshot_path_entries(watched_paths))
    post_git_status_short = _get_git_status_short()
    manifest = _build_manifest(
        args=args,
        git_sha=git_sha,
        pre_git_status_short=pre_git_status_short,
        post_git_status_short=post_git_status_short,
        env_values=env_values,
        approved_files=approved_files,
        watched_paths=watched_paths,
        diff_events=diff_events,
        anchor_sources=summary["anchor_sources"],
    )
    args.manifest_out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    verification_events = _diff_snapshots(pre_snapshot, _snapshot_path_entries(watched_paths))
    unexpected_events = [
        event
        for event in verification_events
        if event["path"] not in {_relative_path(path) for path in approved_files}
    ]
    if unexpected_events:
        raise RuntimeError(
            "Containment failure: unexpected create/modify/delete outside approved output files: "
            + json.dumps(unexpected_events, indent=2)
        )

    print(f"[OK] Wrote candidate config: {args.config_out}")
    print(f"[OK] Wrote replay summary: {args.summary_out}")
    print(f"[OK] Wrote closeout note: {args.closeout_out}")
    print(f"[OK] Wrote manifest: {args.manifest_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
