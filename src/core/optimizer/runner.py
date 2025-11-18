from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import threading
import time
from collections.abc import Iterable
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import yaml

try:  # optional faster JSON
    import orjson as _orjson  # type: ignore

    def _json_dumps(obj: Any) -> str:
        return _orjson.dumps(obj).decode("utf-8")

except Exception:  # pragma: no cover

    def _json_dumps(obj: Any) -> str:
        return json.dumps(obj, indent=2)


from core.optimizer.champion import ChampionCandidate, ChampionManager
from core.optimizer.constraints import enforce_constraints
from core.optimizer.param_transforms import transform_parameters
from core.optimizer.scoring import MetricThresholds, score_backtest
from core.utils.diffing import summarize_metrics_diff
from core.utils.diffing.canonical import canonicalize_config
from core.utils.diffing.optuna_guard import estimate_zero_trade
from core.utils.diffing.results_diff import diff_backtest_results
from core.utils.diffing.trial_cache import TrialResultCache
from core.utils.optuna_helpers import NoDupeGuard, param_signature

try:
    import optuna
    from optuna import Trial
    from optuna.pruners import (
        HyperbandPruner,
        MedianPruner,
        NopPruner,
        SuccessiveHalvingPruner,
    )
    from optuna.samplers import CmaEsSampler, RandomSampler, TPESampler
    from optuna.storages import RDBStorage
    from optuna.trial import TrialState

    OPTUNA_AVAILABLE = True
except ModuleNotFoundError:  # pragma: no cover - handled at runtime
    optuna = None
    Trial = Any
    TrialState = Any
    OPTUNA_AVAILABLE = False


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESULTS_DIR = PROJECT_ROOT / "results" / "hparam_search"
BACKTEST_RESULTS_DIR = PROJECT_ROOT / "results" / "backtests"

_OPTUNA_LOCK = threading.Lock()
_SIMPLE_CATEGORICAL_TYPES = (type(None), bool, int, float, str)
_COMPLEX_CHOICE_PREFIX = "__optuna_complex__"

# Performance: Cache for trial key generation to avoid repeated JSON serialization
_TRIAL_KEY_CACHE: dict[int, str] = {}
_TRIAL_KEY_CACHE_LOCK = threading.Lock()


def _atomic_write_text(path: Path, payload: str, *, encoding: str = "utf-8") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding=encoding, delete=False, dir=path.parent) as tmp:
        tmp.write(payload)
    Path(tmp.name).replace(path)


class OptimizerStrategy:
    GRID = "grid"
    OPTUNA = "optuna"


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
    # Läs alltid som UTF-8 (matchar preflight/validator) för att undvika Windows default-encoding-problem.
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:
        raise ValueError(f"Kunde inte läsa config-filen: {path} ({exc})") from exc
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError("search config måste vara YAML-mapp")
    return data


def _trial_key(params: dict[str, Any]) -> str:
    """Generate canonical key for trial parameters with caching."""
    canonical = canonicalize_config(params or {})
    key = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()

    with _TRIAL_KEY_CACHE_LOCK:
        cached = _TRIAL_KEY_CACHE.get(digest)
        if cached is not None:
            return cached
        if len(_TRIAL_KEY_CACHE) > 10000:
            items = list(_TRIAL_KEY_CACHE.items())
            _TRIAL_KEY_CACHE.clear()
            _TRIAL_KEY_CACHE.update(items[-8000:])
        _TRIAL_KEY_CACHE[digest] = key

    return key


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, int | float):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


def _validate_date_range(start: str, end: str, *, message: str | None = None) -> None:
    if start > end:
        raise ValueError(message or "start_date måste vara mindre än eller lika med end_date")


def _normalize_date(value: Any, field_name: str) -> str:
    if isinstance(value, date):
        return value.isoformat()
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
    start_raw = runs_cfg.get("sample_start")
    end_raw = runs_cfg.get("sample_end")
    if start_raw is None and end_raw is None:
        start, end = _derive_dates(snapshot_id)
        _validate_date_range(start, end)
        return start, end
    if start_raw is None or end_raw is None:
        raise ValueError("Både sample_start och sample_end måste anges om någon av dem är satt")
    start = _normalize_date(start_raw, "sample_start")
    end = _normalize_date(end_raw, "sample_end")
    _validate_date_range(
        start,
        end,
        message="sample_start måste vara mindre än eller lika med sample_end",
    )
    return start, end


def _load_existing_trials(run_dir: Path) -> dict[str, dict[str, Any]]:
    """Load existing trials with optimized file I/O.

    Performance optimization: Batch read operations and use more efficient
    JSON parsing with pre-allocated dictionary.
    """
    existing: dict[str, dict[str, Any]] = {}
    trial_paths = sorted(run_dir.glob("trial_*.json"))

    # Performance: Pre-allocate dictionary size hint if we know count
    if trial_paths:
        existing = dict.fromkeys(range(len(trial_paths)))
        existing.clear()  # Keep capacity but clear keys

    for trial_path in trial_paths:
        try:
            # Performance: Read file once, parse once
            content = trial_path.read_text(encoding="utf-8")
            trial_data = json.loads(content)
            params = trial_data.get("parameters")
            if params:
                key = _trial_key(params)
                existing[key] = trial_data
        except (json.JSONDecodeError, OSError):
            # Skip corrupted files silently
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
                cwd=Path(__file__).resolve().parents[3],
                capture_output=True,
                text=True,
                check=True,
            )
            commit = completed.stdout.strip()
        except subprocess.SubprocessError:
            commit = "unknown"
    try:
        config_rel = str(config_path.relative_to(Path(__file__).resolve().parents[3]))
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
    _atomic_write_text(meta_path, json.dumps(_serialize_meta(meta_payload), indent=2))


def _serialize_meta(meta_payload: dict[str, Any]) -> dict[str, Any]:
    serialized = {}
    for key, value in meta_payload.items():
        if isinstance(value, dict):
            serialized[key] = _serialize_meta(value)
        elif isinstance(value, list):
            serialized[key] = [_serialize_meta(v) if isinstance(v, dict) else v for v in value]
        elif isinstance(value, datetime | date):
            serialized[key] = value.isoformat()
        else:
            serialized[key] = value
    return serialized


def _deep_merge(base: dict, override: dict) -> dict:
    """Deep merge override dict into base dict."""
    merged = dict(base)
    for key, value in (override or {}).items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _expand_value(node: Any) -> list[Any]:
    if isinstance(node, dict):
        node_type = node.get("type")
        if node_type == "grid":
            values = node.get("values") or []
            # Performance: Only deepcopy if values contain mutable containers
            # Most grid values are primitives (int, float, str, bool) which don't need deepcopy
            if values:
                return [copy.deepcopy(v) if isinstance(v, (dict, list)) else v for v in values]
        if node_type == "fixed":
            value = node.get("value")
            # Performance: Only deepcopy mutable containers
            if isinstance(value, (dict, list)):
                return [copy.deepcopy(value)]
            return [value]
        # Nested dict without explicit type – expand recursively
        return list(_expand_dict(node))
    if isinstance(node, list):
        return [copy.deepcopy(node)]
    return [node]  # Performance: Primitives don't need deepcopy


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


def _estimate_optuna_search_space(spec: dict[str, Any]) -> dict[str, Any]:
    """Estimate the size and diversity of the Optuna search space.

    Returns diagnostics about potential degeneracy issues.
    """

    def _count_choices(node: dict[str, Any], prefix: str = "") -> dict[str, int]:
        counts = {}
        for key, value in (node or {}).items():
            path = f"{prefix}.{key}" if prefix else key
            if value is None:
                continue
            if isinstance(value, dict) and "type" not in value:
                counts.update(_count_choices(value, path))
                continue
            node_type = (value or {}).get("type", "grid")
            if node_type == "fixed":
                counts[path] = 1
            elif node_type == "grid":
                options = value.get("values") or []
                counts[path] = len(options)
            elif node_type in ("float", "int"):
                low = float(value.get("low", 0))
                high = float(value.get("high", 1))
                step = value.get("step")
                if step:
                    # Discretized space
                    counts[path] = int((high - low) / float(step)) + 1
                else:
                    # Continuous space - mark as "infinite"
                    counts[path] = -1  # continuous
            elif node_type == "loguniform":
                counts[path] = -1  # continuous
        return counts

    param_counts = _count_choices(spec)

    # Calculate total combinations (only for discrete params)
    discrete_params = {k: v for k, v in param_counts.items() if v > 0}
    continuous_params = {k: v for k, v in param_counts.items() if v < 0}

    total_combinations = 1
    for count in discrete_params.values():
        total_combinations *= count

    # Detect potential issues
    issues = []
    if total_combinations < 10 and not continuous_params:
        issues.append("Search space very small (<10 combinations)")

    narrow_params = [k for k, v in discrete_params.items() if v <= 2]
    if len(narrow_params) > len(discrete_params) * 0.7:
        issues.append(f"Many parameters have ≤2 choices: {narrow_params[:3]}")

    return {
        "total_discrete_combinations": total_combinations if not continuous_params else None,
        "discrete_params": len(discrete_params),
        "continuous_params": len(continuous_params),
        "param_choice_counts": param_counts,
        "potential_issues": issues,
    }


def _derive_dates(snapshot_id: str) -> tuple[str, str]:
    if not snapshot_id:
        raise ValueError("trial snapshot_id saknas")
    parts = snapshot_id.split("_")
    if len(parts) < 4:
        raise ValueError("snapshot_id saknar start/end datum")
    return parts[2], parts[3]


def _exec_backtest(
    cmd: list[str], *, cwd: Path, env: dict[str, str] | None = None, log_path: Path | None = None
) -> tuple[int, str]:
    """
    Execute backtest as subprocess.

    If log_path is provided, stream stdout/stderr directly to file to minimize memory usage.
    Returns (returncode, log_text). When log_path is used, log_text will be an empty string.
    """
    if log_path is not None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "w", encoding="utf-8") as log_file:
            with subprocess.Popen(  # nosec B603
                cmd,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=str(cwd),
                env=env,
            ) as proc:
                proc.wait()
                return proc.returncode, ""
    # Fallback: capture to memory
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
    constraints_cfg: dict[str, Any | None] | None = None,
    cache_enabled: bool = False,
    seen_param_keys: set[str] | None = None,
    seen_param_lock: threading.Lock | None = None,
    baseline_results: dict[str, Any] | None = None,
    baseline_label: str | None = None,
) -> dict[str, Any]:
    key = _trial_key(trial.parameters)
    fingerprint_digest = hashlib.sha256(key.encode("utf-8")).hexdigest()

    if allow_resume and key in existing_trials:
        if seen_param_keys is not None:
            if seen_param_lock:
                with seen_param_lock:
                    seen_param_keys.add(key)
            else:
                seen_param_keys.add(key)
        existing = existing_trials[key]
        return {
            "trial_id": existing.get("trial_id"),
            "parameters": trial.parameters,
            "skipped": True,
            "reason": "already_completed",
            "results_path": existing.get("results_path"),
        }

    duplicate_detected = False
    if seen_param_keys is not None:
        if seen_param_lock:
            with seen_param_lock:
                if key in seen_param_keys:
                    duplicate_detected = True
                else:
                    seen_param_keys.add(key)
        else:
            if key in seen_param_keys:
                duplicate_detected = True
            else:
                seen_param_keys.add(key)

    trial_id = f"trial_{index:03d}"
    if duplicate_detected:
        return {
            "trial_id": trial_id,
            "parameters": trial.parameters,
            "skipped": True,
            "reason": "duplicate_within_run",
        }

    output_dir = run_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    trial_file = output_dir / f"{trial_id}.json"
    log_file = output_dir / f"{trial_id}.log"

    zero_trade_estimate = estimate_zero_trade(trial.parameters or {})
    if not zero_trade_estimate.ok:
        payload = {
            "trial_id": trial_id,
            "parameters": trial.parameters,
            "skipped": True,
            "reason": "zero_trade_preflight",
            "details": zero_trade_estimate.reason,
            "score": {"score": -1e5},
        }
        print(
            "[Runner] Trial "
            f"{trial_id} pruned by zero-trade preflight: {zero_trade_estimate.reason}"
        )
        _atomic_write_text(trial_file, _json_dumps(payload))
        return payload
    config_file: Path | None = None
    derived_values: dict[str, Any] = {}
    if trial.parameters:
        config_file = output_dir / f"{trial_id}_config.json"

        # Load default config and merge with trial parameters
        from core.config.authority import ConfigAuthority

        authority = ConfigAuthority()
        default_cfg_obj, _, _ = authority.get()
        default_cfg = default_cfg_obj.model_dump()

        # Deep merge trial parameters into default config
        transformed_params, derived_values = transform_parameters(trial.parameters)
        merged_cfg = _deep_merge(default_cfg, transformed_params)
        config_payload = {"cfg": merged_cfg}
        _atomic_write_text(config_file, _json_dumps(config_payload))

    cache: TrialResultCache | None = None
    cached_payload: dict[str, Any] | None = None
    if cache_enabled:
        cache = TrialResultCache(run_dir / "_cache")
        cached_payload = cache.lookup(fingerprint_digest)
        if cached_payload is not None:
            payload = dict(cached_payload)
            payload.update(
                {
                    "trial_id": trial_id,
                    "parameters": trial.parameters,
                    "from_cache": True,
                }
            )
            if config_file is not None:
                payload.setdefault("config_path", config_file.name)
            if not payload.get("parameters"):
                payload["parameters"] = trial.parameters
            diff_payload = payload.get("diff_vs_baseline")
            if diff_payload:
                summary = diff_payload.get("summary")
                label = diff_payload.get("label", "baseline")
                if summary:
                    print(f"[Diff/Cache] Trial {trial_id} vs {label}:\n{summary}")
                else:
                    print(f"[Diff/Cache] Trial {trial_id} vs {label}: no metric deltas")
            _atomic_write_text(trial_file, _json_dumps(payload))
            return payload

    if trial.start_date and trial.end_date:
        start_date, end_date = trial.start_date, trial.end_date
    else:
        start_date, end_date = _derive_dates(trial.snapshot_id)
    _validate_date_range(
        start_date,
        end_date,
        message="start_date måste vara mindre än eller lika med end_date",
    )

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
    # Opt-in performance flags via environment variables
    if os.environ.get("GENESIS_FAST_WINDOW"):
        cmd.append("--fast-window")
    if os.environ.get("GENESIS_PRECOMPUTE_FEATURES"):
        cmd.append("--precompute-features")
    if config_file is not None:
        cmd.extend(["--config-file", str(config_file)])

    attempts_remaining = max(1, max_attempts)
    final_payload: dict[str, Any] | None = None
    trial_started = time.perf_counter()
    attempt_durations: list[float] = []
    last_log_output = ""

    # Deterministic seed for subprocess backtests unless explicitly overridden
    base_env = dict(os.environ)
    if "GENESIS_RANDOM_SEED" not in base_env or not str(base_env["GENESIS_RANDOM_SEED"]).strip():
        base_env["GENESIS_RANDOM_SEED"] = "42"

    while attempts_remaining > 0:
        attempt_started = time.perf_counter()
        attempts_remaining -= 1
        returncode, log = _exec_backtest(
            cmd, cwd=Path(__file__).resolve().parents[3], env=base_env, log_path=log_file
        )
        last_log_output = log
        attempt_duration = time.perf_counter() - attempt_started
        attempt_durations.append(attempt_duration)
        if returncode == 0:
            results_path = sorted(
                (Path(__file__).resolve().parents[3] / "results" / "backtests").glob(
                    f"{trial.symbol}_{trial.timeframe}_*.json"
                )
            )[-1]
            results = json.loads(results_path.read_text(encoding="utf-8"))
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
            if derived_values:
                final_payload.setdefault("derived", derived_values)
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

    # If we didn't stream, persist the captured log
    if last_log_output:
        _atomic_write_text(log_file, last_log_output)
    if final_payload is None:
        final_payload = {
            "trial_id": trial_id,
            "parameters": trial.parameters,
            "error": "unknown",
            "log_path": log_file.name,
            "attempts": max_attempts,
        }
    elif derived_values and "derived" not in final_payload:
        final_payload["derived"] = derived_values

    if (
        baseline_results is not None
        and final_payload is not None
        and not final_payload.get("error")
        and final_payload.get("results_path")
    ):
        new_results_path = BACKTEST_RESULTS_DIR / str(final_payload["results_path"])
        if new_results_path.exists():
            try:
                new_results = json.loads(new_results_path.read_text(encoding="utf-8"))
                diff_payload = diff_backtest_results(baseline_results, new_results)
                summary = summarize_metrics_diff(diff_payload.get("metrics", {}))
                label = baseline_label or "baseline"
                final_payload["diff_vs_baseline"] = {
                    "label": label,
                    "metrics": diff_payload.get("metrics"),
                    "trades": diff_payload.get("trades"),
                    "summary": summary,
                }
                if summary:
                    print(f"[Diff] Trial {trial_id} vs {label}:\n{summary}")
                else:
                    print(f"[Diff] Trial {trial_id} vs {label}: no metric deltas")
            except (OSError, json.JSONDecodeError) as exc:
                print(
                    f"[WARN] Kunde inte diff:a mot baseline ({baseline_label or 'baseline'}): {exc}"
                )
        else:
            print(f"[WARN] Kunde inte hitta resultatfil för diff: {new_results_path}")
    if cache_enabled and cache is not None and final_payload and not final_payload.get("error"):
        cache_snapshot = dict(final_payload)
        cache_snapshot.pop("trial_id", None)
        cache_snapshot.pop("from_cache", None)
        cache_snapshot["parameters"] = trial.parameters
        cache.store(fingerprint_digest, cache_snapshot)
    _atomic_write_text(trial_file, json.dumps(final_payload, indent=2))
    return final_payload


def _select_optuna_sampler(
    name: str | None,
    kwargs: dict[str, Any] | None,
    concurrency: int = 1,
):
    if not OPTUNA_AVAILABLE:
        raise RuntimeError("Optuna är inte installerat")
    kwargs = (kwargs or {}).copy()
    name = (name or kwargs.pop("name", None) or kwargs.pop("type", None) or "tpe").lower()
    if name == "tpe":
        # Apply better defaults for TPE to avoid degeneracy
        if "multivariate" not in kwargs:
            kwargs["multivariate"] = True
        if "constant_liar" not in kwargs:
            kwargs["constant_liar"] = True
        if "n_startup_trials" not in kwargs:
            # Scale startup trials with concurrency to reduce duplicates
            # More workers = more simultaneous samples = need more random exploration
            base_startup = 25
            adaptive_startup = max(base_startup, 5 * concurrency)
            kwargs["n_startup_trials"] = adaptive_startup
        if "n_ei_candidates" not in kwargs:
            # More candidates for better exploration
            kwargs["n_ei_candidates"] = 48
        return TPESampler(**kwargs)
    if name == "random":
        return RandomSampler(**kwargs)
    if name == "cmaes":
        return CmaEsSampler(**kwargs)
    raise ValueError(f"Okänd Optuna-sampler: {name}")


def _select_optuna_pruner(
    name: str | None,
    kwargs: dict[str, Any] | None,
):
    if not OPTUNA_AVAILABLE:
        raise RuntimeError("Optuna är inte installerat")
    kwargs = (kwargs or {}).copy()
    name = (name or kwargs.pop("name", None) or kwargs.pop("type", None) or "median").lower()
    if name == "median":
        return MedianPruner(**kwargs)
    if name == "sha":
        return SuccessiveHalvingPruner(**kwargs)
    if name == "hyperband":
        return HyperbandPruner(**kwargs)
    if name == "none":
        return NopPruner()
    raise ValueError(f"Okänd Optuna-pruner: {name}")


def _create_optuna_study(
    run_id: str,
    storage: str | None,
    study_name: str | None,
    sampler_cfg: dict[str, Any] | None,
    pruner_cfg: dict[str, Any] | None,
    direction: str | None,
    allow_resume: bool,
    concurrency: int = 1,
    *,
    heartbeat_interval: int | None = None,
    heartbeat_grace_period: int | None = None,
):
    if not OPTUNA_AVAILABLE:
        raise RuntimeError("Optuna är inte installerat")
    sampler_cfg = sampler_cfg or {}
    pruner_cfg = pruner_cfg or {}
    sampler_name = (
        sampler_cfg.get("name")
        or sampler_cfg.get("type")
        or sampler_cfg.get("sampler")
        or sampler_cfg.get("kind")
    )
    pruner_name = (
        pruner_cfg.get("name")
        or pruner_cfg.get("type")
        or pruner_cfg.get("pruner")
        or pruner_cfg.get("kind")
    )
    sampler = _select_optuna_sampler(
        sampler_name, sampler_cfg.get("kwargs"), concurrency=concurrency
    )
    pruner = _select_optuna_pruner(pruner_name, pruner_cfg.get("kwargs"))
    storage_obj: Any | None = storage
    if storage and heartbeat_interval:
        storage_obj = RDBStorage(
            storage,
            heartbeat_interval=heartbeat_interval,
            grace_period=heartbeat_grace_period,
        )

    with _OPTUNA_LOCK:
        study = optuna.create_study(
            study_name=study_name or f"optimizer_{run_id}",
            storage=storage_obj,
            sampler=sampler,
            pruner=pruner,
            direction=(direction or "maximize"),
            load_if_exists=allow_resume,
        )
    return study


def _suggest_parameters(trial, spec: dict[str, Any]) -> dict[str, Any]:
    # Performance: Cache for decimal calculation to avoid repeated string operations
    _step_decimals_cache: dict[float, int] = {}

    def _prepare_categorical_options(options: Iterable[Any]) -> tuple[list[Any], dict[str, Any]]:
        normalized: list[Any] = []
        decoder: dict[str, Any] = {}
        for idx, option in enumerate(options):
            if isinstance(option, _SIMPLE_CATEGORICAL_TYPES):
                normalized.append(option)
                continue
            encoded = (
                f"{_COMPLEX_CHOICE_PREFIX}{idx}__"
                f"{json.dumps(option, sort_keys=True, separators=(',', ':'))}"
            )
            normalized.append(encoded)
            decoder[encoded] = option
        return normalized, decoder

    def _get_step_decimals(step_float: float) -> int:
        """Get number of decimals for a step value with caching."""
        if step_float not in _step_decimals_cache:
            step_str = str(step_float)
            if "." in step_str:
                decimals = len(step_str.split(".")[1])
            else:
                decimals = 0
            _step_decimals_cache[step_float] = decimals
        return _step_decimals_cache[step_float]

    def _recurse(node: dict[str, Any], prefix: str = "") -> dict[str, Any]:
        resolved: dict[str, Any] = {}
        for key, value in (node or {}).items():
            path = f"{prefix}.{key}" if prefix else key
            if value is None:
                raise ValueError(f"parameter {path} saknar definition i YAML")
            if isinstance(value, dict) and "type" not in value:
                resolved[key] = _recurse(value, path)
                continue
            node_type = (value or {}).get("type", "grid")
            if node_type == "fixed":
                resolved[key] = value.get("value")
            elif node_type == "grid":
                options = value.get("values")
                if not options:
                    raise ValueError(f"grid-parameter {path} saknar values")
                normalized, decoder = _prepare_categorical_options(list(options))
                suggest_name = path if not decoder else f"{path}__encoded"
                raw_choice = trial.suggest_categorical(suggest_name, normalized)
                resolved[key] = decoder.get(raw_choice, raw_choice)
            elif node_type == "float":
                low = float(value.get("low"))
                high = float(value.get("high"))
                step = value.get("step")
                log = bool(value.get("log"))
                if step is not None:
                    step_float = float(step)
                    raw_value = trial.suggest_float(path, low, high, step=step_float, log=log)
                    # Performance: Use cached decimal calculation
                    decimals = _get_step_decimals(step_float)
                    # Round till rätt antal decimaler baserat på step
                    resolved[key] = round(round(raw_value / step_float) * step_float, decimals)
                else:
                    resolved[key] = trial.suggest_float(path, low, high, log=log)
            elif node_type == "int":
                low = int(value.get("low"))
                high = int(value.get("high"))
                step = int(value.get("step", 1))
                resolved[key] = trial.suggest_int(path, low, high, step=step)
            elif node_type == "loguniform":
                low = float(value.get("low"))
                high = float(value.get("high"))
                resolved[key] = trial.suggest_float(path, low, high, log=True)
            else:
                raise ValueError(f"Okänd parameter-typ '{node_type}' för {path}")
        return resolved

    return _recurse(spec or {})


def _run_optuna(
    study_config: dict[str, Any],
    parameters_spec: dict[str, Any],
    make_trial,
    run_dir: Path,
    run_id: str,
    existing_trials: dict[str, dict[str, Any]],
    max_trials: int | None,
    concurrency: int,
    allow_resume: bool,
) -> list[dict[str, Any]]:
    if not OPTUNA_AVAILABLE:
        raise RuntimeError("Optuna-strategi vald men optuna är inte installerat")

    # Validate search space before starting
    space_diagnostics = _estimate_optuna_search_space(parameters_spec)
    if space_diagnostics["potential_issues"]:
        print("\n⚠️  Search space warnings:")
        for issue in space_diagnostics["potential_issues"]:
            print(f"   - {issue}")
        print(f"   Discrete params: {space_diagnostics['discrete_params']}")
        print(f"   Continuous params: {space_diagnostics['continuous_params']}")
        if space_diagnostics["total_discrete_combinations"]:
            print(
                f"   Total discrete combinations: {space_diagnostics['total_discrete_combinations']}"
            )
        print()

    storage = study_config.get("storage") or os.getenv("OPTUNA_STORAGE")
    study_name = study_config.get("study_name") or os.getenv("OPTUNA_STUDY_NAME")
    direction = study_config.get("direction") or "maximize"
    timeout = study_config.get("timeout_seconds")
    sampler_cfg = study_config.get("sampler")
    pruner_cfg = study_config.get("pruner")
    if isinstance(sampler_cfg, str):
        sampler_cfg = {"name": sampler_cfg}
    if isinstance(pruner_cfg, str):
        pruner_cfg = {"name": pruner_cfg}

    heartbeat_interval = study_config.get("heartbeat_interval")
    heartbeat_grace = study_config.get("heartbeat_grace_period")
    heartbeat_interval = int(heartbeat_interval) if heartbeat_interval else None
    heartbeat_grace = int(heartbeat_grace) if heartbeat_grace else None

    results: list[dict[str, Any]] = []
    duplicate_streak = 0
    max_duplicate_streak = int(os.getenv("OPTUNA_MAX_DUPLICATE_STREAK", "10"))
    total_trials_attempted = 0
    duplicate_count = 0
    zero_trade_count = 0

    # Fast duplicate precheck using persistent guard (SQLite WAL-backed)
    dedup_guard_enabled = bool(study_config.get("dedup_guard_enabled", True))
    guard: NoDupeGuard | None = (
        NoDupeGuard(sqlite_path=str(run_dir / "_dedup.db")) if dedup_guard_enabled else None
    )

    def objective(trial):
        nonlocal duplicate_streak, total_trials_attempted, duplicate_count, zero_trade_count
        total_trials_attempted += 1
        parameters = _suggest_parameters(trial, parameters_spec)
        trial_number = trial.number + 1
        key = _trial_key(parameters)

        # Pre-check duplicates across workers/runs using stable param signature
        sig: str | None = None
        if guard is not None:
            try:
                sig = param_signature(parameters)
                if guard.seen(sig):
                    duplicate_streak += 1
                    duplicate_count += 1
                    trial.set_user_attr("duplicate", True)
                    # For backward‑compatibility with tests and diagnostics,
                    # mark both generic and precheck-specific attributes.
                    trial.set_user_attr("penalized_duplicate", True)
                    trial.set_user_attr("penalized_duplicate_precheck", True)
                    # Advance trial stream via make_trial (cheap in-run duplicate detection),
                    # then override result as prechecked duplicate to avoid optimizer degeneracy.
                    payload = make_trial(trial_number, parameters)
                    payload = dict(payload or {})
                    payload["trial_id"] = f"trial_{trial_number:03d}"
                    payload["parameters"] = parameters
                    payload["skipped"] = True
                    payload.setdefault("reason", "duplicate_guard_precheck")
                    results.append(payload)
                    if duplicate_streak >= max_duplicate_streak:
                        raise optuna.exceptions.OptunaError(
                            "Duplicate parameter suggestions limit reached"
                        )
                    return -1e6
                # Reserve signature to avoid concurrent duplicates
                guard.add(sig)
            except Exception:
                # Best-effort guard; continue without precheck on guard failure
                sig = None
        if key in existing_trials:
            cached = existing_trials[key]
            trial.set_user_attr("skipped", True)
            trial.set_user_attr("duplicate", True)
            duplicate_streak += 1
            duplicate_count += 1
            if duplicate_streak >= max_duplicate_streak:
                raise optuna.exceptions.OptunaError("Duplicate parameter suggestions limit reached")
            results.append({**cached, "skipped": True})
            # Penalize duplicates heavily so sampler moves away from same params
            trial.set_user_attr("penalized_duplicate", True)
            return -1e6

        payload = make_trial(trial_number, parameters)
        results.append(payload)

        if payload.get("skipped"):
            reason = payload.get("reason")
            trial.set_user_attr("skipped", True)
            if reason == "duplicate_within_run":
                duplicate_streak += 1
                duplicate_count += 1
                trial.set_user_attr("duplicate", True)
                if duplicate_streak >= max_duplicate_streak:
                    raise optuna.exceptions.OptunaError(
                        "Duplicate parameter suggestions limit reached"
                    )
            elif reason == "zero_trade_preflight":
                zero_trade_count += 1
                duplicate_streak = 0
                trial.set_user_attr("zero_trade_preflight", True)
                penalty = float(payload.get("score", {}).get("score", -1e5) or -1e5)
                return penalty
            else:
                # Only reset streak for non-duplicate skips
                duplicate_streak = 0
            # Penalize in-run duplicates to avoid degeneracy
            if reason == "duplicate_within_run":
                trial.set_user_attr("penalized_duplicate", True)
                return -1e6
            # Other skip reasons (e.g., already_completed) can report neutral score
            return float(payload.get("score", {}).get("score", 0.0) or 0.0)

        if payload.get("error"):
            trial.set_user_attr("error", payload.get("error"))
            # Release reserved signature to allow future attempts if run failed
            if guard is not None and sig:
                try:
                    guard.remove(sig)
                except Exception:
                    pass
            # Don't reset duplicate streak on errors
            raise optuna.TrialPruned()

        constraints = payload.get("constraints") or {}
        score_block = payload.get("score") or {}
        score_value = float(score_block.get("score", 0.0) or 0.0)

        # Check for zero trades to track this issue
        metrics = score_block.get("metrics", {})
        num_trades = int(metrics.get("num_trades", 0))
        if num_trades == 0:
            zero_trade_count += 1
            trial.set_user_attr("zero_trades", True)

        # Mjuk constraints: returnera straffad poäng istället för att pruna,
        # så att Optuna kan ranka försök och fortsätta utforskning.
        if not constraints.get("ok", True):
            trial.set_user_attr("constraints", constraints)
            trial.set_user_attr("constraints_soft_fail", True)
            # Stor negativ straff men lämna utrymme för rankning
            return score_value - 1e3

        # Only reset duplicate streak on successful, non-zero-trade trials
        if num_trades > 0:
            duplicate_streak = 0

        trial.set_user_attr("score_block", score_block)
        trial.set_user_attr("result_payload", payload)
        return score_value

    remaining_trials = None if max_trials is None else max(0, max_trials)
    bootstrap_requested_raw = study_config.get("bootstrap_random_trials")
    bootstrap_requested = int(bootstrap_requested_raw) if bootstrap_requested_raw else 0
    bootstrap_seed_raw = study_config.get("bootstrap_seed")
    random_kwargs: dict[str, Any] = {}
    if bootstrap_seed_raw is not None:
        try:
            random_kwargs["seed"] = int(bootstrap_seed_raw)
        except (TypeError, ValueError):
            pass
    if bootstrap_requested > 0:
        bootstrap_to_run = bootstrap_requested
        if remaining_trials is not None:
            bootstrap_to_run = min(bootstrap_to_run, remaining_trials)
        if bootstrap_to_run > 0:
            print(
                f"[Optuna] Bootstrapper {bootstrap_to_run} random-trials (RandomSampler) innan "
                f"huvudsamplern (temporär concurrency=1)"
            )
            bootstrap_sampler_cfg = {"name": "random", "kwargs": random_kwargs}
            bootstrap_study = _create_optuna_study(
                run_id=run_id,
                storage=storage,
                study_name=study_name,
                sampler_cfg=bootstrap_sampler_cfg,
                pruner_cfg=pruner_cfg,
                direction=direction,
                allow_resume=True,
                concurrency=1,
                heartbeat_interval=heartbeat_interval,
                heartbeat_grace_period=heartbeat_grace,
            )
            bootstrap_study.optimize(
                objective,
                n_trials=bootstrap_to_run,
                timeout=None,
                n_jobs=1,
                gc_after_trial=True,
                show_progress_bar=False,
            )
            if remaining_trials is not None:
                remaining_trials = max(0, remaining_trials - bootstrap_to_run)
    if remaining_trials is not None and remaining_trials == 0:
        return results

    study = _create_optuna_study(
        run_id=run_id,
        storage=storage,
        study_name=study_name,
        sampler_cfg=sampler_cfg,
        pruner_cfg=pruner_cfg,
        direction=direction,
        allow_resume=allow_resume or bootstrap_requested > 0,
        concurrency=concurrency,
        heartbeat_interval=heartbeat_interval,
        heartbeat_grace_period=heartbeat_grace,
    )

    study.optimize(
        objective,
        n_trials=remaining_trials,
        timeout=timeout,
        n_jobs=concurrency,
        gc_after_trial=True,
        show_progress_bar=False,  # Performance: Disable progress bar for batch runs
    )

    # Diagnostic warnings for duplicate and zero-trade issues
    if total_trials_attempted > 0:
        duplicate_ratio = duplicate_count / total_trials_attempted
        zero_trade_ratio = zero_trade_count / total_trials_attempted

        if duplicate_ratio > 0.5:
            print(
                f"\n⚠️  WARNING: High duplicate rate ({duplicate_ratio*100:.1f}%)\n"
                f"   {duplicate_count}/{total_trials_attempted} trials were duplicates.\n"
                f"   This suggests:\n"
                f"   - Search space may be too narrow\n"
                f"   - Float step sizes causing parameter collapse\n"
                f"   - TPE sampler degenerating\n"
            )
            if concurrency > 4:
                print(
                    f"   - High concurrency (n_jobs={concurrency}) increases duplicates\n"
                    f"     This is normal with parallel optimization + discrete spaces\n"
                )
            print(
                f"   Recommendations:\n"
                f"   - Widen parameter ranges\n"
                f"   - Increase n_startup_trials (try {max(25, 5 * concurrency)}+)\n"
            )
            if concurrency > 4:
                print(
                    f"   - Reduce max_concurrent to {max(2, concurrency // 2)} for discrete spaces\n"
                )
            print(
                "   - Use multivariate=true in TPE sampler\n"
                "   - Consider removing or loosening step sizes\n"
            )

        if zero_trade_ratio > 0.5:
            print(
                f"\n⚠️  WARNING: High zero-trade rate ({zero_trade_ratio*100:.1f}%)\n"
                f"   {zero_trade_count}/{total_trials_attempted} trials produced 0 trades.\n"
                f"   This suggests:\n"
                f"   - Entry confidence thresholds too high\n"
                f"   - Fibonacci gates too strict\n"
                f"   - Multi-timeframe filtering too aggressive\n"
                f"   Recommendations:\n"
                f"   - Lower entry_conf_overall (try 0.25-0.35)\n"
                f"   - Widen fibonacci tolerance_atr ranges\n"
                f"   - Enable LTF override when HTF blocks\n"
                f"   - Run smoke test (2-5 trials) before long runs\n"
            )

    # Performance: Batch metadata updates to reduce file I/O
    best_payload: dict[str, Any] | None = None
    optuna_meta: dict[str, Any] = {}

    if study.best_trials:  # finns åtminstone en icke-prunad trial
        try:
            best_trial = study.best_trial
            best_payload = best_trial.user_attrs.get("result_payload")
            optuna_meta = {
                "study_name": study.study_name,
                "storage": storage,
                "direction": direction,
                "n_trials": len(study.trials),
                "best_value": study.best_value,
                "best_trial_number": best_payload.get("trial_id") if best_payload else None,
                "diagnostics": {
                    "total_trials_attempted": total_trials_attempted,
                    "duplicate_count": duplicate_count,
                    "zero_trade_count": zero_trade_count,
                    "duplicate_ratio": duplicate_count / max(1, total_trials_attempted),
                    "zero_trade_ratio": zero_trade_count / max(1, total_trials_attempted),
                },
            }
        except ValueError:
            best_payload = None
            optuna_meta = {
                "study_name": study.study_name,
                "storage": storage,
                "direction": direction,
                "n_trials": len(study.trials),
                "best_value": None,
                "best_trial_number": None,
                "diagnostics": {
                    "total_trials_attempted": total_trials_attempted,
                    "duplicate_count": duplicate_count,
                    "zero_trade_count": zero_trade_count,
                    "duplicate_ratio": duplicate_count / max(1, total_trials_attempted),
                    "zero_trade_ratio": zero_trade_count / max(1, total_trials_attempted),
                },
            }
    else:
        optuna_meta = {
            "study_name": study.study_name,
            "storage": storage,
            "direction": direction,
            "n_trials": len(study.trials),
            "best_value": None,
            "best_trial_number": None,
            "diagnostics": {
                "total_trials_attempted": total_trials_attempted,
                "duplicate_count": duplicate_count,
                "zero_trade_count": zero_trade_count,
                "duplicate_ratio": duplicate_count / max(1, total_trials_attempted),
                "zero_trade_ratio": zero_trade_count / max(1, total_trials_attempted),
            },
        }

    # Performance: Single file read/write for metadata
    run_meta_path = run_dir / "run_meta.json"
    try:
        run_meta = json.loads(run_meta_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        run_meta = {}

    run_meta.setdefault("optuna", {}).update(optuna_meta)

    # Performance: Write best trial and metadata in sequence to avoid conflicts
    if best_payload is not None:
        best_json_path = run_dir / "best_trial.json"
        _atomic_write_text(best_json_path, _json_dumps(best_payload))

    _atomic_write_text(run_meta_path, _json_dumps(_serialize_meta(run_meta)))

    return results


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
    strategy = (runs_cfg.get("strategy") or OptimizerStrategy.GRID).lower()

    sample_start: str | None = None
    sample_end: str | None = None
    if _as_bool(runs_cfg.get("use_sample_range")):
        sample_start, sample_end = _resolve_sample_range(meta.get("snapshot_id", ""), runs_cfg)

    # Hantera max_trials: null (None) för att köra tills timeout
    max_trials_raw = runs_cfg.get("max_trials")
    if max_trials_raw is None:
        max_trials = None  # Kör tills timeout
    else:
        max_trials = int(max_trials_raw) or None  # 0 blir None
    allow_resume = bool(runs_cfg.get("resume", True))
    # Concurrency: allow env override for quick tuning without YAML edits
    env_conc = os.environ.get("GENESIS_MAX_CONCURRENT")
    if env_conc is not None:
        try:
            concurrency = max(1, int(env_conc))
        except ValueError:
            concurrency = max(1, int(runs_cfg.get("max_concurrent", 1)))
    else:
        concurrency = max(1, int(runs_cfg.get("max_concurrent", 1)))
    max_attempts = max(1, int(runs_cfg.get("max_attempts", 2)))
    run_id_resolved = _create_run_id(run_id)
    run_dir = (
        Path(__file__).resolve().parents[3] / "results" / "hparam_search" / run_id_resolved
    ).resolve()
    existing_trials = _load_existing_trials(run_dir) if allow_resume and run_dir.exists() else {}
    seen_param_keys: set[str] = set()
    seen_param_lock = threading.Lock()
    run_dir.mkdir(parents=True, exist_ok=True)
    _ensure_run_metadata(run_dir, config_path.resolve(), meta, run_id_resolved)

    symbol = str(meta.get("symbol", "tBTCUSD"))
    timeframe = str(meta.get("timeframe", "1h"))

    baseline_results_path_cfg = meta.get("baseline_results_path") or runs_cfg.get(
        "baseline_results_path"
    )
    baseline_results_data: dict[str, Any] | None = None
    baseline_label: str | None = None
    if baseline_results_path_cfg:
        candidate_path = Path(baseline_results_path_cfg)
        if not candidate_path.is_absolute():
            candidate_path = PROJECT_ROOT / candidate_path
        if candidate_path.exists():
            try:
                baseline_results_data = json.loads(candidate_path.read_text(encoding="utf-8"))
                baseline_label = candidate_path.name
                print(f"[Baseline] Loaded comparison results from {candidate_path}")
            except json.JSONDecodeError as exc:
                print(f"[WARN] baseline_results_path ogiltig JSON ({candidate_path}): {exc}")
        else:
            print(f"[WARN] baseline_results_path hittades inte: {candidate_path}")

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
            cache_enabled=True,
            seen_param_keys=seen_param_keys,
            seen_param_lock=seen_param_lock,
            baseline_results=baseline_results_data,
            baseline_label=baseline_label,
        )

    results: list[dict[str, Any]] = []

    if strategy == OptimizerStrategy.GRID:
        params_list = list(expand_parameters(parameters))
        if max_trials is not None:
            params_list = params_list[:max_trials]

        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            if concurrency == 1:
                for idx, params in enumerate(params_list, start=1):
                    results.append(make_trial(idx, params))
            else:
                futures = _submit_trials(executor, params_list, make_trial)
                for future in as_completed(futures):
                    results.append(future.result())
    elif strategy == OptimizerStrategy.OPTUNA:
        results.extend(
            _run_optuna(
                study_config=runs_cfg.get("optuna") or {},
                parameters_spec=parameters,
                make_trial=make_trial,
                run_dir=run_dir,
                run_id=run_id_resolved,
                existing_trials=existing_trials,
                max_trials=max_trials,
                concurrency=concurrency,
                allow_resume=allow_resume,
            )
        )
    else:
        raise ValueError(f"Okänd optimizer-strategi: {strategy}")

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
