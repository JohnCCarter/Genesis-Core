from __future__ import annotations

import itertools
import json
import subprocess  # nosec B404 - subprocess usage reviewed for controlled command execution
import time
from collections.abc import Iterable
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from core.optimizer.constraints import enforce_constraints
from core.optimizer.scoring import MetricThresholds, score_backtest

ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "results" / "hparam_search"


@dataclass(slots=True)
class TrialConfig:
    snapshot_id: str
    symbol: str
    timeframe: str
    warmup_bars: int
    parameters: dict[str, Any]


def load_search_config(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict):
        raise ValueError("search config måste vara YAML-mapp")
    return data


def _trial_key(params: dict[str, Any]) -> str:
    return json.dumps(params, sort_keys=True, separators=(",", ":"))


def _load_existing_trials(run_dir: Path) -> dict[str, dict[str, Any]]:
    existing: dict[str, dict[str, Any]] = {}
    for trial_path in sorted(run_dir.glob("trial_*.json")):
        try:
            trial_data = json.loads(trial_path.read_text())
            params = trial_data.get("parameters") or {}
            key = _trial_key(params)
            existing[key] = trial_data
        except (json.JSONDecodeError, OSError):
            continue
    return existing


def _ensure_run_metadata(
    run_dir: Path, config_path: Path, meta: dict[str, Any], run_id: str
) -> None:
    meta_path = run_dir / "run_meta.json"
    if meta_path.exists():
        return
    commit = "unknown"
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip()
    except (subprocess.SubprocessError, OSError):
        commit = "unknown"
    meta_payload = {
        "run_id": run_id,
        "config_path": (
            str(config_path.relative_to(ROOT)) if config_path.is_absolute() else str(config_path)
        ),
        "snapshot_id": meta.get("snapshot_id"),
        "symbol": meta.get("symbol"),
        "timeframe": meta.get("timeframe"),
        "started_at": datetime.now(UTC).isoformat(),
        "git_commit": commit,
        "raw_meta": meta,
    }
    meta_path.write_text(json.dumps(meta_payload, indent=2), encoding="utf-8")


def expand_parameters(spec: dict[str, Any]) -> Iterable[dict[str, Any]]:
    base: dict[str, Any] = {}
    grids: list[tuple[str, list[Any]]] = []
    for key, sub in spec.items():
        if isinstance(sub, dict) and sub.get("type") == "grid":
            grids.append((key, list(sub.get("values") or [])))
        elif isinstance(sub, dict) and sub.get("type") == "fixed":
            base[key] = sub.get("value")
        else:
            base[key] = sub
    if not grids:
        yield base
        return
    keys, values = zip(*grids, strict=True)
    for combo in itertools.product(*values):
        config = dict(base)
        config.update(dict(zip(keys, combo, strict=True)))
        yield config


def _derive_dates(snapshot_id: str) -> tuple[str, str]:
    if not snapshot_id:
        raise ValueError("trial snapshot_id saknas")
    parts = snapshot_id.split("_")
    if len(parts) < 4:
        raise ValueError("snapshot_id saknar start/end datum")
    return parts[2], parts[3]


def _exec_backtest(cmd: list[str]) -> tuple[int, str]:
    with subprocess.Popen(  # nosec B603
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=ROOT,
    ) as proc:
        log = proc.communicate()[0]
        return proc.returncode, log


def run_trial(
    trial: TrialConfig,
    *,
    run_id: str,
    index: int,
    run_dir: Path,
    allow_resume: bool,
    existing_trials: dict[str, dict[str, Any]],
    max_attempts: int = 2,
) -> dict[str, Any]:
    key = _trial_key(trial.parameters)
    if allow_resume and key in existing_trials:
        existing = existing_trials[key]
        return {
            "trial_id": existing.get("trial_id"),
            "parameters": trial.parameters,
            "skipped": True,
            "reason": "already_completed",
            "results_path": existing.get("results_path"),
        }

    start_date, end_date = _derive_dates(trial.snapshot_id)
    output_dir = run_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    trial_id = f"trial_{index:03d}"
    trial_file = output_dir / f"{trial_id}.json"
    log_file = output_dir / f"{trial_id}.log"
    cmd = [
        "python",
        "scripts/run_backtest.py",
        "--symbol",
        trial.symbol,
        "--timeframe",
        trial.timeframe,
        "--start",
        start_date,
        "--end",
        end_date,
        "--warmup",
        str(trial.warmup_bars),
    ]

    attempts_remaining = max(1, max_attempts)
    final_payload: dict[str, Any] | None = None
    while attempts_remaining > 0:
        attempts_remaining -= 1
        returncode, log = _exec_backtest(cmd)
        if returncode == 0:
            results_path = sorted(
                (ROOT / "results" / "backtests").glob(f"{trial.symbol}_{trial.timeframe}_*.json")
            )[-1]
            results = json.loads(results_path.read_text())
            score = score_backtest(results, thresholds=MetricThresholds())
            enforcement = enforce_constraints(score, trial.parameters)
            final_payload = {
                "trial_id": trial_id,
                "parameters": trial.parameters,
                "results_path": results_path.name,
                "score": score,
                "constraints": enforcement.__dict__,
                "log": log_file.name,
                "attempts": max_attempts - attempts_remaining,
            }
            break
        final_payload = {
            "trial_id": trial_id,
            "parameters": trial.parameters,
            "error": "backtest_failed",
            "log_path": log_file.name,
            "attempts": max_attempts - attempts_remaining,
        }
        retry_wait = min(5 * (max_attempts - attempts_remaining), 60)
        if attempts_remaining > 0:
            print(f"[Runner] Backtest fail, retry om {retry_wait}s")
            time.sleep(retry_wait)

    log_file.write_text(log if "log" in locals() else "", encoding="utf-8")
    if final_payload is None:
        final_payload = {
            "trial_id": trial_id,
            "parameters": trial.parameters,
            "error": "unknown",
            "log_path": log_file.name,
            "attempts": max_attempts,
        }
    trial_file.write_text(json.dumps(final_payload, indent=2), encoding="utf-8")
    return final_payload


def _create_run_id(proposed: str | None = None) -> str:
    if proposed:
        return proposed
    return datetime.now(UTC).strftime("run_%Y%m%d_%H%M%S")


def _submit_trials(
    executor: ThreadPoolExecutor,
    params_list: list[dict[str, Any]],
    trial_cfg_builder,
) -> list[Future]:
    futures: list[Future] = []
    for idx, params in enumerate(params_list, start=1):
        futures.append(executor.submit(trial_cfg_builder, idx, params))
    return futures


def run_optimizer(config_path: Path, *, run_id: str | None = None) -> list[dict[str, Any]]:
    config = load_search_config(config_path)
    meta = config.get("meta") or {}
    parameters = config.get("parameters") or {}
    runs_cfg = meta.get("runs") or {}
    max_trials = int(runs_cfg.get("max_trials", 0)) or None
    allow_resume = bool(runs_cfg.get("resume", True))
    concurrency = max(1, int(runs_cfg.get("max_concurrent", 1)))
    max_attempts = max(1, int(runs_cfg.get("max_attempts", 2)))
    run_id_resolved = _create_run_id(run_id)
    run_dir = (RESULTS_DIR / run_id_resolved).resolve()
    existing_trials = _load_existing_trials(run_dir) if allow_resume and run_dir.exists() else {}
    run_dir.mkdir(parents=True, exist_ok=True)
    _ensure_run_metadata(run_dir, config_path.resolve(), meta, run_id_resolved)

    params_list = list(expand_parameters(parameters))
    if max_trials is not None:
        params_list = params_list[:max_trials]

    def make_trial(idx: int, params: dict[str, Any]) -> dict[str, Any]:
        trial_cfg = TrialConfig(
            snapshot_id=meta.get("snapshot_id", ""),
            symbol=meta.get("symbol", "tBTCUSD"),
            timeframe=meta.get("timeframe", "1h"),
            warmup_bars=int(meta.get("warmup_bars", 150)),
            parameters=params,
        )
        return run_trial(
            trial_cfg,
            run_id=run_id_resolved,
            index=idx,
            run_dir=run_dir,
            allow_resume=allow_resume,
            existing_trials=existing_trials,
            max_attempts=max_attempts,
        )

    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        if concurrency == 1:
            for idx, params in enumerate(params_list, start=1):
                results.append(make_trial(idx, params))
        else:
            futures = _submit_trials(executor, params_list, make_trial)
            for future in as_completed(futures):
                results.append(future.result())
    return results
