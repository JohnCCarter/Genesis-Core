from __future__ import annotations

import copy
import json
import shutil
import subprocess  # nosec B404
import time
from collections.abc import Iterable
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from core.optimizer.champion import ChampionCandidate, ChampionManager
from core.optimizer.constraints import enforce_constraints
from core.optimizer.scoring import MetricThresholds, score_backtest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = PROJECT_ROOT / "src"
RESULTS_DIR = PROJECT_ROOT / "results" / "hparam_search"


@dataclass(slots=True)
class TrialConfig:
    snapshot_id: str
    symbol: str
    timeframe: str
    warmup_bars: int
    parameters: dict[str, Any]
    start_date: str | None = None
    end_date: str | None = None


def load_search_config(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict):
        raise ValueError("search config måste vara YAML-mapp")
    return data


def _trial_key(params: dict[str, Any]) -> str:
    return json.dumps(params, sort_keys=True, separators=(",", ":"))


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


def _normalize_date(value: Any, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} måste vara sträng, fick {type(value).__name__}")
    candidate = value.strip()
    if not candidate:
        raise ValueError(f"{field_name} får inte vara tom")
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise ValueError(f"Ogiltigt datumformat för {field_name}: {value}") from exc
    return parsed.date().isoformat()


def _resolve_sample_range(snapshot_id: str, runs_cfg: dict[str, Any]) -> tuple[str, str]:
    _as_bool(runs_cfg.get("use_sample_range"))  # preserved behaviour, bool conversion
    start_raw = runs_cfg.get("sample_start")
    end_raw = runs_cfg.get("sample_end")
    if start_raw is None or end_raw is None:
        return _derive_dates(snapshot_id)
    start = _normalize_date(start_raw, "sample_start")
    end = _normalize_date(end_raw, "sample_end")
    if start > end:
        raise ValueError("sample_start måste vara mindre än eller lika med sample_end")
    return start, end


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
    git_executable = shutil.which("git")
    if git_executable:
        try:
            completed = subprocess.run(  # nosec B603
                [git_executable, "rev-parse", "HEAD"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            commit = completed.stdout.strip()
        except subprocess.SubprocessError:
            commit = "unknown"
    try:
        config_rel = str(config_path.relative_to(PROJECT_ROOT))
    except ValueError:
        config_rel = str(config_path)
    meta_payload = {
        "run_id": run_id,
        "config_path": config_rel,
        "snapshot_id": meta.get("snapshot_id"),
        "symbol": meta.get("symbol"),
        "timeframe": meta.get("timeframe"),
        "started_at": datetime.now(UTC).isoformat(),
        "git_commit": commit,
        "raw_meta": meta,
    }
    meta_path.write_text(json.dumps(meta_payload, indent=2), encoding="utf-8")


def _expand_value(node: Any) -> list[Any]:
    if isinstance(node, dict):
        node_type = node.get("type")
        if node_type == "grid":
            values = node.get("values") or []
            return [copy.deepcopy(v) for v in values]
        if node_type == "fixed":
            return [copy.deepcopy(node.get("value"))]
        # Nested dict without explicit type – expand recursively
        return list(_expand_dict(node))
    if isinstance(node, list):
        return [copy.deepcopy(node)]
    return [copy.deepcopy(node)]


def _expand_dict(spec: dict[str, Any]) -> Iterable[dict[str, Any]]:
    items = [(key, _expand_value(value)) for key, value in spec.items()]

    def _recurse(idx: int, current: dict[str, Any]) -> Iterable[dict[str, Any]]:
        if idx >= len(items):
            yield current
            return
        key, values = items[idx]
        for value in values:
            next_config = dict(current)
            next_config[key] = value
            yield from _recurse(idx + 1, next_config)

    yield from _recurse(0, {})


def expand_parameters(spec: dict[str, Any]) -> Iterable[dict[str, Any]]:
    if not spec:
        yield {}
        return
    yield from _expand_dict(spec)


def _derive_dates(snapshot_id: str) -> tuple[str, str]:
    if not snapshot_id:
        raise ValueError("trial snapshot_id saknas")
    parts = snapshot_id.split("_")
    if len(parts) < 4:
        raise ValueError("snapshot_id saknar start/end datum")
    return parts[2], parts[3]


def _exec_backtest(
    cmd: list[str], *, cwd: Path, env: dict[str, str] | None = None
) -> tuple[int, str]:
    with subprocess.Popen(  # nosec B603
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=str(cwd),
        env=env,
    ) as proc:
        log = proc.communicate()[0]
        return proc.returncode, log


def _candidate_from_result(result: dict[str, Any]) -> ChampionCandidate | None:
    if result.get("error") or result.get("skipped"):
        return None
    score_block = result.get("score") or {}
    constraints_block = result.get("constraints") or {}
    hard_failures = list(score_block.get("hard_failures") or [])
    constraints_ok = bool(constraints_block.get("ok"))
    if not constraints_ok or hard_failures:
        return None
    try:
        score_value = float(score_block.get("score"))
    except (TypeError, ValueError):
        return None
    return ChampionCandidate(
        parameters=dict(result.get("parameters") or {}),
        score=score_value,
        metrics=dict(score_block.get("metrics") or {}),
        constraints_ok=constraints_ok,
        constraints=dict(constraints_block),
        hard_failures=hard_failures,
        trial_id=str(result.get("trial_id", "")),
        results_path=str(result.get("results_path", "")),
    )


def run_trial(
    trial: TrialConfig,
    *,
    run_id: str,
    index: int,
    run_dir: Path,
    allow_resume: bool,
    existing_trials: dict[str, dict[str, Any]],
    max_attempts: int = 2,
    constraints_cfg: dict[str, Any] | None = None,
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

    output_dir = run_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    trial_id = f"trial_{index:03d}"
    trial_file = output_dir / f"{trial_id}.json"
    log_file = output_dir / f"{trial_id}.log"
    config_file: Path | None = None
    if trial.parameters:
        config_file = output_dir / f"{trial_id}_config.json"
        config_payload = {"cfg": trial.parameters}
        config_file.write_text(json.dumps(config_payload, indent=2), encoding="utf-8")
    if trial.start_date and trial.end_date:
        start_date, end_date = trial.start_date, trial.end_date
        if start_date > end_date:
            raise ValueError("start_date måste vara mindre än eller lika med end_date")
    else:
        start_date, end_date = _derive_dates(trial.snapshot_id)
    cmd = [
        "python",
        "-m",
        "scripts.run_backtest",
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
    if config_file is not None:
        cmd.extend(["--config-file", str(config_file)])

    attempts_remaining = max(1, max_attempts)
    final_payload: dict[str, Any] | None = None
    trial_started = time.perf_counter()
    attempt_durations: list[float] = []
    while attempts_remaining > 0:
        attempt_started = time.perf_counter()
        attempts_remaining -= 1
        returncode, log = _exec_backtest(cmd, cwd=PROJECT_ROOT)
        attempt_duration = time.perf_counter() - attempt_started
        attempt_durations.append(attempt_duration)
        if returncode == 0:
            results_path = sorted(
                (PROJECT_ROOT / "results" / "backtests").glob(
                    f"{trial.symbol}_{trial.timeframe}_*.json"
                )
            )[-1]
            results = json.loads(results_path.read_text())
            score = score_backtest(results, thresholds=MetricThresholds())
            enforcement = enforce_constraints(
                score,
                trial.parameters,
                constraints_cfg=constraints_cfg,
            )
            score_value = score.get("score")
            score_serializable = {
                "score": score_value,
                "metrics": score.get("metrics"),
                "hard_failures": list(score.get("hard_failures") or []),
            }
            total_duration = time.perf_counter() - trial_started
            final_payload = {
                "trial_id": trial_id,
                "parameters": trial.parameters,
                "results_path": results_path.name,
                "score": score_serializable,
                "constraints": {
                    "ok": enforcement.ok,
                    "reasons": enforcement.reasons,
                },
                "log": log_file.name,
                "attempts": max_attempts - attempts_remaining,
                "duration_seconds": total_duration,
                "attempt_durations": attempt_durations,
            }
            if config_file is not None:
                final_payload["config_path"] = config_file.name
            print(
                f"[Runner] Trial {trial_id} klar på {total_duration:.1f}s" f" (score={score_value})"
            )
            break
        final_payload = {
            "trial_id": trial_id,
            "parameters": trial.parameters,
            "error": "backtest_failed",
            "log_path": log_file.name,
            "attempts": max_attempts - attempts_remaining,
            "duration_seconds": time.perf_counter() - trial_started,
            "attempt_durations": attempt_durations,
        }
        if config_file is not None:
            final_payload["config_path"] = config_file.name
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
    sample_start: str | None = None
    sample_end: str | None = None
    if runs_cfg:
        if runs_cfg.get("sample_start") or runs_cfg.get("sample_end"):
            start_candidate = runs_cfg.get("sample_start")
            end_candidate = runs_cfg.get("sample_end")
            if start_candidate is None or end_candidate is None:
                raise ValueError(
                    "Både sample_start och sample_end måste anges om någon av dem är satt"
                )
            sample_start = _normalize_date(start_candidate, "sample_start")
            sample_end = _normalize_date(end_candidate, "sample_end")
            if sample_start > sample_end:
                raise ValueError("sample_start måste vara mindre än eller lika med sample_end")
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

    symbol = str(meta.get("symbol", "tBTCUSD"))
    timeframe = str(meta.get("timeframe", "1h"))

    def make_trial(idx: int, params: dict[str, Any]) -> dict[str, Any]:
        trial_cfg = TrialConfig(
            snapshot_id=meta.get("snapshot_id", ""),
            symbol=symbol,
            timeframe=timeframe,
            warmup_bars=int(meta.get("warmup_bars", 150)),
            parameters=params,
            start_date=sample_start,
            end_date=sample_end,
        )
        return run_trial(
            trial_cfg,
            run_id=run_id_resolved,
            index=idx,
            run_dir=run_dir,
            allow_resume=allow_resume,
            existing_trials=existing_trials,
            max_attempts=max_attempts,
            constraints_cfg=config.get("constraints"),
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

    run_meta_path = run_dir / "run_meta.json"
    try:
        run_meta = json.loads(run_meta_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        run_meta = {}

    best_candidate: ChampionCandidate | None = None
    best_result: dict[str, Any] | None = None
    for result in results:
        candidate = _candidate_from_result(result)
        if candidate is None:
            continue
        if best_candidate is None or candidate.score > best_candidate.score:
            best_candidate = candidate
            best_result = result

    if best_candidate is not None:
        manager = ChampionManager()
        current = manager.load_current(symbol, timeframe)
        if manager.should_replace(current, best_candidate):
            metadata_extra: dict[str, Any] = {
                "run_dir": str(run_dir),
                "config_path": str(config_path),
                "raw_run_meta": run_meta,
            }
            if best_result is not None:
                metadata_extra.update(
                    {
                        "constraints": best_result.get("constraints"),
                        "score_block": best_result.get("score"),
                    }
                )
            manager.write_champion(
                symbol=symbol,
                timeframe=timeframe,
                candidate=best_candidate,
                run_id=run_id_resolved,
                git_commit=str(run_meta.get("git_commit", "unknown")),
                snapshot_id=str(run_meta.get("snapshot_id") or meta.get("snapshot_id", "")),
                run_meta=metadata_extra,
            )
            print(
                f"[Champion] Uppdaterad champion för {symbol} {timeframe} (score {best_candidate.score:.2f})"
            )
        else:
            print(
                f"[Champion] Ingen uppdatering: befintlig champion bättre eller constraints fel ({symbol} {timeframe})"
            )

    return results
