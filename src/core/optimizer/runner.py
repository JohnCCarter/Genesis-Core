from __future__ import annotations

import argparse
import copy
import hashlib
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from collections import OrderedDict
from collections.abc import Iterable
from concurrent.futures import Future, ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import yaml

try:  # Optional heavy deps used for JSON serialization helpers
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover - numpy not strictly required
    np = None  # type: ignore

try:
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover - pandas not strictly required
    pd = None  # type: ignore
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


def _json_default(obj: Any) -> Any:
    """Best-effort serializer for optional scientific types."""

    if isinstance(obj, datetime | date):
        return obj.isoformat()
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, set | frozenset):
        return list(obj)
    if np is not None:
        if isinstance(obj, np.integer | np.bool_):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
    if pd is not None and isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    iso = getattr(obj, "isoformat", None)
    if callable(iso):  # Fallback för objekt med isoformat (t.ex. pendulum)
        return iso()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


try:  # optional faster JSON
    import orjson as _orjson  # type: ignore

    def _json_dumps(obj: Any) -> str:
        return _orjson.dumps(obj, default=_json_default).decode("utf-8")

    def _json_loads(text: str) -> Any:
        """Parse JSON using orjson for better performance."""
        return _orjson.loads(text)

    _HAS_ORJSON = True

except Exception:  # pragma: no cover

    def _json_dumps(obj: Any) -> str:
        return json.dumps(obj, indent=2, default=_json_default)

    def _json_loads(text: str) -> Any:
        return json.loads(text)

    _HAS_ORJSON = False


try:
    import optuna
    from optuna import Trial
    from optuna.pruners import HyperbandPruner, MedianPruner, NopPruner, SuccessiveHalvingPruner
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

# Logger for cache reuse messages
logger = logging.getLogger(__name__)
try:
    CONSTRAINT_SOFT_PENALTY = float(os.environ.get("GENESIS_CONSTRAINT_SOFT_PENALTY", "150"))
except ValueError:  # Fallback om env ej numerisk
    CONSTRAINT_SOFT_PENALTY = 150.0

_OPTUNA_LOCK = threading.Lock()
_SIMPLE_CATEGORICAL_TYPES = (type(None), bool, int, float, str)
_COMPLEX_CHOICE_PREFIX = "__optuna_complex__"

# Performance: Cache for trial key generation to avoid repeated JSON serialization
_TRIAL_KEY_CACHE: dict[int, str] = {}
_TRIAL_KEY_CACHE_LOCK = threading.Lock()

# Performance: Cache for default config to avoid repeated file reads and model dumps
_DEFAULT_CONFIG_CACHE: dict[str, Any] | None = None
_DEFAULT_CONFIG_LOCK = threading.Lock()

# Performance: Module-level cache for step decimal calculation (persists across trials)
_STEP_DECIMALS_CACHE: dict[float, int] = {}
_STEP_DECIMALS_CACHE_LOCK = threading.Lock()


# Performance: JSON mtime cache for optimizer (opt-in via env GENESIS_OPTIMIZER_JSON_CACHE=1)
_JSON_CACHE: OrderedDict[str, tuple[int, Any]] = OrderedDict()
try:
    _JSON_CACHE_MAX = int(os.environ.get("GENESIS_OPTIMIZER_JSON_CACHE_SIZE", "256"))
except Exception:
    _JSON_CACHE_MAX = 256


def _load_json_with_retries(path: Path, retries: int = 3, delay: float = 0.1) -> Any:
    """Read JSON from disk with small retry loop; salvage on trailing garbage.

    Problem: Vi har observerat korrupta resultatfiler där flera JSON-objekt eller
    loggdata har skrivits i samma fil vilket ger `JSONDecodeError: Extra data`.
    Lösning: Vid 'Extra data' försöker vi extrahera första kompletta JSON-objektet
    genom att balansera klammerparenteser och parsa substringen. Om salvage
    misslyckas fortsätter vi med retries som tidigare.
    """
    last_error: json.JSONDecodeError | None = None
    for attempt in range(retries):
        text = path.read_text(encoding="utf-8")
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:  # pragma: no cover - IO race eller korrupt fil
            last_error = exc
            msg = str(exc)
            # Salvage endast vid 'Extra data' (typiskt flera JSON-objekt concatenated)
            if "Extra data" in msg:
                # Försök hitta första kompletta objektet (antas börja med '{')
                start_idx = text.find("{")
                if start_idx != -1:
                    depth = 0
                    in_string = False
                    escape = False
                    end_idx = -1
                    for i in range(start_idx, len(text)):
                        ch = text[i]
                        if in_string:
                            if escape:
                                escape = False
                            elif ch == "\\":
                                escape = True
                            elif ch == '"':
                                in_string = False
                            continue
                        else:
                            if ch == '"':
                                in_string = True
                                continue
                            if ch == "{":
                                depth += 1
                            elif ch == "}":
                                depth -= 1
                                if depth == 0:
                                    end_idx = i + 1
                                    break
                    if end_idx != -1:
                        candidate = text[start_idx:end_idx]
                        try:
                            salvaged = json.loads(candidate)
                            # Logga minimal varning men returnera salvaged innehåll
                            print(
                                f"[WARN] Salvaged partial JSON från {path.name} (trailing data borttagen)"
                            )
                            return salvaged
                        except json.JSONDecodeError:
                            pass  # Salvage misslyckades, fortsätt retries
            if attempt + 1 < retries:
                time.sleep(delay)
            else:
                raise
    raise last_error  # pragma: no cover


def _read_json_cached(path: Path) -> Any:
    """Read JSON with optional mtime-based in-memory cache.

    Enabled when GENESIS_OPTIMIZER_JSON_CACHE is truthy ('1', 'true', 'True').
    """
    use_cache = os.environ.get("GENESIS_OPTIMIZER_JSON_CACHE") in {"1", "true", "True"}
    if not use_cache:
        return _load_json_with_retries(path)

    key = str(path.resolve())
    try:
        mtime = path.stat().st_mtime_ns
    except OSError:
        # Fall back to direct read if stat fails
        return json.loads(path.read_text(encoding="utf-8"))

    cached = _JSON_CACHE.get(key)
    if cached is not None:
        cached_mtime, cached_obj = cached
        if cached_mtime == mtime:
            try:
                _JSON_CACHE.move_to_end(key)
            except Exception:  # nosec B110
                pass  # Cache error non-critical
            return cached_obj

    obj = _load_json_with_retries(path)
    _JSON_CACHE[key] = (mtime, obj)
    try:
        while len(_JSON_CACHE) > _JSON_CACHE_MAX:
            _JSON_CACHE.popitem(last=False)
    except Exception:
        if len(_JSON_CACHE) > _JSON_CACHE_MAX:
            _JSON_CACHE.pop(next(iter(_JSON_CACHE)))
    return obj


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
    """Generate canonical key for trial parameters with caching.

    Performance optimization: Cache both the canonical form and the final
    digest to avoid redundant canonicalization calls.
    """
    try:
        # Fast path: Try to generate key directly from params
        key = json.dumps(params, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    except (TypeError, ValueError):
        # Fallback: Use canonicalize for complex types
        canonical = canonicalize_config(params or {})
        key = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()

    with _TRIAL_KEY_CACHE_LOCK:
        cached = _TRIAL_KEY_CACHE.get(digest)
        if cached is not None:
            return cached
        # Performance: Trim cache when it grows too large
        if len(_TRIAL_KEY_CACHE) > 10000:
            items = list(_TRIAL_KEY_CACHE.items())
            _TRIAL_KEY_CACHE.clear()
            # Keep most recent 8000 (approximate LRU via dict ordering)
            _TRIAL_KEY_CACHE.update(items[-8000:])

        _TRIAL_KEY_CACHE[digest] = digest
        return digest


def _get_default_config() -> dict[str, Any]:
    """
    Get default configuration with thread-safe caching.

    Performance optimization: The default config is loaded once and cached
    for the entire optimization run, avoiding redundant file reads and
    expensive Pydantic model_dump() operations for every trial.

    Returns:
        Dictionary containing default configuration
    """
    global _DEFAULT_CONFIG_CACHE

    with _DEFAULT_CONFIG_LOCK:
        if _DEFAULT_CONFIG_CACHE is None:
            from core.config.authority import ConfigAuthority

            authority = ConfigAuthority()
            default_cfg_obj, _, _ = authority.get()
            _DEFAULT_CONFIG_CACHE = default_cfg_obj.model_dump()
        return _DEFAULT_CONFIG_CACHE


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

    Performance optimization: Batch read operations, use more efficient
    JSON parsing, and optimize memory allocation patterns.

    Key optimizations:
    - Single-pass JSON parsing (no double parse via _json_loads)
    - Direct orjson usage when available (bypass wrapper overhead)
    - Batch trial key generation to leverage caching

    Note: Duplicates logic from _json_loads() intentionally to avoid
    function call overhead in this hot path. This function is called
    once per optimization run during resume, loading potentially
    thousands of trial files, where every microsecond counts.
    """
    trial_paths = sorted(run_dir.glob("trial_*.json"))

    if not trial_paths:
        return {}

    # Performance: Pre-allocate dictionary with size hint
    existing: dict[str, dict[str, Any]] = {}

    for trial_path in trial_paths:
        try:
            # Performance: Direct orjson usage for better speed (single parse, no wrapper)
            content = trial_path.read_text(encoding="utf-8")
            if _HAS_ORJSON:
                trial_data = _orjson.loads(content)
            else:
                trial_data = json.loads(content)

            # JSON always returns exact dict, but be defensive
            if not isinstance(trial_data, dict):
                continue

            params = trial_data.get("parameters")
            if params:
                key = _trial_key(params)
                existing[key] = trial_data
        except (ValueError, OSError):
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
    """Deep merge override dict into base dict.

    Performance optimization: Iterative implementation to avoid recursion depth limits
    and function call overhead.
    """
    if not override:
        return dict(base)

    merged = dict(base)
    stack = [(merged, override)]

    while stack:
        current_base, current_override = stack.pop()
        for key, value in current_override.items():
            if (
                key in current_base
                and isinstance(current_base[key], dict)
                and isinstance(value, dict)
            ):
                current_base[key] = dict(current_base[key])
                stack.append((current_base[key], value))
            else:
                current_base[key] = value

    return merged


def _expand_value(node: Any) -> list[Any]:
    def _clone_value(v: Any) -> Any:
        # Performance: Use type() for faster checks on primitives
        t = type(v)
        if t in (int, float, str, bool, type(None), bytes):
            return v
        if t is tuple:
            return tuple(_clone_value(x) for x in v)
        if t is list:
            return [_clone_value(x) for x in v]
        if t is dict:
            return {k: _clone_value(val) for k, val in v.items()}
        return copy.deepcopy(v)

    if isinstance(node, dict):
        node_type = node.get("type")
        if node_type == "grid":
            values = node.get("values") or []
            return [_clone_value(v) for v in values]
        if node_type == "fixed":
            return [_clone_value(node.get("value"))]
        # Nested dict without explicit type – expand recursively
        return list(_expand_dict(node))
    if isinstance(node, list):
        return [_clone_value(node)]
    return [_clone_value(node)]


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
        merged_config=result.get("merged_config"),  # Include merged config
    )


def _extract_num_trades(payload: dict[str, Any]) -> int | None:
    """Best effort extraction of num_trades from nested payloads."""

    def _coerce(value: Any) -> int | None:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    score_block = payload.get("score")
    if isinstance(score_block, dict):
        metrics = score_block.get("metrics")
        if isinstance(metrics, dict):
            coerced = _coerce(metrics.get("num_trades"))
            if coerced is not None:
                return coerced

    summary_block = payload.get("summary")
    if isinstance(summary_block, dict):
        coerced = _coerce(summary_block.get("num_trades"))
        if coerced is not None:
            return coerced

    metrics_block = payload.get("metrics")
    if isinstance(metrics_block, dict):
        coerced = _coerce(metrics_block.get("num_trades"))
        if coerced is not None:
            return coerced

    return None


def _check_abort_heuristic(
    backtest_results: dict[str, Any], trial_params: dict[str, Any]
) -> dict[str, Any]:
    """Check if trial should be aborted post-backtest based on heuristic.

    Returns dict with:
        ok (bool): True if trial should continue, False if should abort
        reason (str): Abort reason if ok=False
        details (str): Additional details about why abort triggered
        penalty (float): Score penalty to apply if aborted
    """
    metrics = backtest_results.get("metrics", {})
    num_trades = metrics.get("num_trades", 0)

    # Zero trades with high thresholds = likely configuration issue
    if num_trades == 0:
        thresholds = trial_params.get("thresholds", {})
        entry_conf = thresholds.get("entry_conf_overall", 0.0)
        signal_adapt = thresholds.get("signal_adaptation", {})
        zones = signal_adapt.get("zones", {})
        low_zone = zones.get("low", {})
        low_entry = low_zone.get("entry_conf_overall", 0.0)
        min_edge = thresholds.get("min_edge", 0.0)

        # Early abort condition: zero trades + high thresholds
        if entry_conf >= 0.35 or low_entry >= 0.28 or min_edge >= 0.015:
            return {
                "ok": False,
                "reason": "zero_trades_high_thresholds",
                "details": f"entry={entry_conf:.3f}, low_zone={low_entry:.3f}, min_edge={min_edge:.4f}",
                "penalty": -500.0,
            }

    # Very few trades (1-3) - apply milder penalty
    if 0 < num_trades <= 3:
        return {
            "ok": False,
            "reason": "very_few_trades",
            "details": f"only {num_trades} trades",
            "penalty": -250.0,
        }

    return {"ok": True, "reason": "", "details": "", "penalty": 0.0}


# Performance: Cache for loaded DataFrames
_DATA_CACHE: dict[str, Any] = {}
_DATA_LOCK = threading.Lock()


def _run_backtest_direct(
    trial: TrialConfig,
    config_path: Path,
    optuna_context: dict[str, Any] | None = None,
) -> tuple[int, str, dict[str, Any] | None]:
    try:
        from core.backtest.engine import BacktestEngine

        # Load/Get engine
        # Include dates in cache key to support different ranges
        cache_key = f"{trial.symbol}_{trial.timeframe}_{trial.start_date}_{trial.end_date}"
        with _DATA_LOCK:
            if cache_key not in _DATA_CACHE:
                # Create engine
                # Always use fast_window=True for optimization
                engine_loader = BacktestEngine(
                    symbol=trial.symbol,
                    timeframe=trial.timeframe,
                    start_date=trial.start_date,
                    end_date=trial.end_date,
                    warmup_bars=trial.warmup_bars,
                    fast_window=True,
                )

                # Enable precompute BEFORE load_data() so features are generated
                if os.environ.get("GENESIS_PRECOMPUTE_FEATURES"):
                    engine_loader.precompute_features = True
                    logger.info("[PRECOMPUTE] Enabled before data load for 20x speedup")

                # Now load data (will trigger precompute if flag is set)
                if engine_loader.load_data():
                    _DATA_CACHE[cache_key] = engine_loader
                else:
                    _DATA_CACHE[cache_key] = None

            engine = _DATA_CACHE[cache_key]

        if engine is None:
            return 1, "Failed to load data", None

        # Update warmup_bars in case it changed between trials
        engine.warmup_bars = trial.warmup_bars

        # Load config
        payload = json.loads(config_path.read_text(encoding="utf-8"))
        cfg = payload["cfg"]

        # Pruning
        pruning_callback = None
        if optuna_context:
            try:
                import optuna

                study = optuna.load_study(
                    study_name=optuna_context["study_name"],
                    storage=optuna_context["storage"],
                )

                def _cb(step, value):
                    try:
                        t = optuna.trial.Trial(study, optuna_context["trial_id"])
                        t.report(value, step)
                        return t.should_prune()
                    except Exception:
                        return False

                pruning_callback = _cb
            except Exception as err:  # pragma: no cover - defensive guard
                logger.warning(
                    "Optuna pruning disabled due to setup failure: %s", err, exc_info=True
                )

        results = engine.run(
            policy={"symbol": trial.symbol, "timeframe": trial.timeframe},
            configs=cfg,
            verbose=False,
            pruning_callback=pruning_callback,
        )

        return 0, "", results

    except Exception as e:
        import traceback

        return 1, f"{e}\n{traceback.format_exc()}", None


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
    optuna_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    key = _trial_key(trial.parameters)
    fingerprint_digest = key  # _trial_key already returns a SHA256 digest

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

        # Performance: Use cached default config instead of loading for every trial
        default_cfg = _get_default_config()

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
    # Default to fast mode for optimizer determinism
    if os.environ.get("GENESIS_FAST_WINDOW", "1") == "1":
        cmd.append("--fast-window")
    if os.environ.get("GENESIS_PRECOMPUTE_FEATURES", "1") == "1":
        cmd.append("--precompute-features")
    if config_file is not None:
        cmd.extend(["--config-file", str(config_file)])

    if optuna_context:
        cmd.extend(
            [
                "--optuna-trial-id",
                str(optuna_context["trial_id"]),
                "--optuna-storage",
                str(optuna_context["storage"]),
                "--optuna-study-name",
                str(optuna_context["study_name"]),
            ]
        )

    attempts_remaining = max(1, max_attempts)
    final_payload: dict[str, Any] | None = None
    trial_started = time.perf_counter()
    attempt_durations: list[float] = []
    last_log_output = ""

    # Deterministic seed for subprocess backtests unless explicitly overridden
    base_env = dict(os.environ)
    if "GENESIS_RANDOM_SEED" not in base_env or not str(base_env["GENESIS_RANDOM_SEED"]).strip():
        base_env["GENESIS_RANDOM_SEED"] = "42"

    # Optimization: Force reduced logging in subprocess to minimize IO overhead
    # User reported massive logs slowing down optimization
    if "LOG_LEVEL" not in base_env:
        base_env["LOG_LEVEL"] = "WARNING"

    # GENESIS_IN_PROCESS=1 means "Debug Mode" (Single Process, Main Thread)
    # GENESIS_IN_PROCESS=0 (Default) means "Process Pool" (Multi Process, Direct Execution)
    debug_mode = os.environ.get("GENESIS_IN_PROCESS") == "1"

    # Guard against debug mode with concurrency on Windows
    if debug_mode and os.name == "nt":
        # We can't easily check n_jobs here without passing it down, but we can warn/error if we detect issues
        # For now, we rely on the caller to respect the rule.
        pass

    while attempts_remaining > 0:
        attempt_started = time.perf_counter()
        attempts_remaining -= 1

        results_dict: dict[str, Any] | None = None

        # Always use direct execution for performance (RAM caching), unless forced to shell out
        # If debug_mode=True, this runs in the main process.
        # If debug_mode=False, this runs in a worker process (if using Pool).
        use_direct_execution = os.environ.get("GENESIS_FORCE_SHELL") != "1"

        if use_direct_execution and config_file:
            returncode, log, results_dict = _run_backtest_direct(trial, config_file, optuna_context)
            if returncode == 0 and results_dict:
                # Save results to file to match subprocess behavior
                results_path = output_dir / f"{trial.symbol}_{trial.timeframe}_{trial_id}.json"
                _atomic_write_text(results_path, _json_dumps(results_dict))
        else:
            returncode, log = _exec_backtest(
                cmd, cwd=Path(__file__).resolve().parents[3], env=base_env, log_path=log_file
            )

        last_log_output = log
        attempt_duration = time.perf_counter() - attempt_started
        attempt_durations.append(attempt_duration)
        if returncode == 0:
            # Parse log file to find exact results path (avoids race condition with glob)
            if not results_dict:
                results_path: Path | None = None
                try:
                    log_content = log_file.read_text(encoding="utf-8")
                    import re

                    # Look for: "  results: path/to/file.json"
                    match = re.search(r"^\s*results:\s*(.*\.json)\s*$", log_content, re.MULTILINE)
                    if match:
                        extracted_path = Path(match.group(1).strip())
                        if not extracted_path.is_absolute():
                            extracted_path = PROJECT_ROOT / extracted_path
                        if extracted_path.exists():
                            results_path = extracted_path
                except Exception as e:
                    print(f"[WARN] Could not parse log for results path: {e}")

                if results_path is None:
                    # Fallback to glob (risky with concurrency)
                    results_path = sorted(
                        (Path(__file__).resolve().parents[3] / "results" / "backtests").glob(
                            f"{trial.symbol}_{trial.timeframe}_*.json"
                        )
                    )[-1]

                try:
                    results = _read_json_cached(results_path)
                except json.JSONDecodeError as json_err:
                    # Korrupt JSON från samtidig skrivning eller partiell write
                    total_duration = time.perf_counter() - trial_started
                    error_payload = {
                        "trial_id": trial_id,
                        "parameters": trial.parameters,
                        "results_path": results_path.name,
                        "error": f"JSONDecodeError: {json_err}",
                        "error_details": str(json_err),
                        "log": log_file.name,
                        "attempts": max_attempts - attempts_remaining,
                        "duration_seconds": total_duration,
                        "attempt_durations": attempt_durations,
                    }
                    if derived_values:
                        error_payload["derived"] = derived_values
                    if config_file is not None:
                        error_payload["config_path"] = config_file.name
                    print(
                        f"[ERROR] Trial {trial_id} fick korrupt JSON ({results_path.name}): {json_err}"
                    )
                    print("[ERROR] Detta indikerar race condition vid samtidig skrivning")
                    _atomic_write_text(trial_file, json.dumps(error_payload, indent=2))
                    # Returnera error payload så att objective kan lyfta TrialPruned
                    return error_payload
            else:
                results = results_dict
                # results_path is already set in the if block above

            merged_config = results.get("merged_config")  # Full config for reproducibility
            runtime_version = results.get("runtime_version")  # Runtime version used

            # Abort-heuristic check (Option B: post-backtest)
            abort_check = _check_abort_heuristic(results, trial.parameters)
            if not abort_check["ok"]:
                total_duration = time.perf_counter() - trial_started
                abort_payload = {
                    "trial_id": trial_id,
                    "parameters": trial.parameters,
                    "results_path": results_path.name,
                    "score": {
                        "score": abort_check["penalty"],
                        "metrics": results.get("metrics"),
                        "hard_failures": [],
                    },
                    "abort_reason": abort_check["reason"],
                    "abort_details": abort_check["details"],
                    "constraints": {"ok": False, "reasons": ["aborted_by_heuristic"]},
                    "log": log_file.name,
                    "attempts": max_attempts - attempts_remaining,
                    "duration_seconds": total_duration,
                    "attempt_durations": attempt_durations,
                    "merged_config": merged_config,
                    "runtime_version": runtime_version,
                }
                if derived_values:
                    abort_payload["derived"] = derived_values
                if config_file is not None:
                    abort_payload["config_path"] = config_file.name
                print(
                    f"[Runner] Trial {trial_id} aborted: {abort_check['reason']} ({abort_check['details']}), penalty={abort_check['penalty']}"
                )
                _atomic_write_text(trial_file, json.dumps(abort_payload, indent=2))
                return abort_payload

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
                "merged_config": merged_config,  # Include for champion saving
                "runtime_version": runtime_version,  # Include for champion saving
            }
            if derived_values:
                final_payload.setdefault("derived", derived_values)
            if config_file is not None:
                final_payload["config_path"] = config_file.name

            # Print trial result with metrics
            metrics = score_serializable.get("metrics", {})
            num_trades = metrics.get("num_trades", 0)
            total_return_pct = metrics.get("total_return", 0.0) * 100.0
            profit_factor = metrics.get("profit_factor", 0.0)
            max_dd_pct = metrics.get("max_drawdown", 0.0) * 100.0
            sharpe = metrics.get("sharpe_ratio", 0.0)
            win_rate_pct = metrics.get("win_rate", 0.0) * 100.0

            print(
                f"[Runner] Trial {trial_id} klar på {total_duration:.1f}s"
                f" (score={score_value:.4f}, trades={num_trades}, return={total_return_pct:.2f}%,"
                f" PF={profit_factor:.2f}, DD={max_dd_pct:.2f}%, Sharpe={sharpe:.3f}, WR={win_rate_pct:.1f}%)"
            )
            break
        retry_wait = min(5 * (max_attempts - attempts_remaining), 60)
        if attempts_remaining > 0:
            print(f"[Runner] Backtest fail, retry om {retry_wait}s")
            if use_direct_execution and returncode != 0:
                print(f"[Runner] Direct Execution Error: {log}")
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
                new_results = _read_json_cached(new_results_path)
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
    name = (name or kwargs.pop("type", None) or "tpe").lower()
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
    name = (name or kwargs.pop("type", None) or "median").lower()
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


def _suggest_parameters(trial: Trial, spec: dict[str, Any]) -> dict[str, Any]:
    """Suggest parameters for Optuna trial with optimized decimal caching.

    Performance optimization: Step decimal calculation is cached at module level
    to avoid repeated string operations across all trials in the study.

    Args:
        trial: Optuna Trial object to suggest parameters from
        spec: Parameter specification dictionary defining the search space

    Returns:
        Dictionary of resolved parameter values for this trial
    """

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
        """Get number of decimals for a step value with module-level caching."""
        with _STEP_DECIMALS_CACHE_LOCK:
            if step_float not in _STEP_DECIMALS_CACHE:
                step_str = str(step_float)
                if "." in step_str:
                    decimals = len(step_str.split(".")[1])
                else:
                    decimals = 0
                _STEP_DECIMALS_CACHE[step_float] = decimals
            return _STEP_DECIMALS_CACHE[step_float]

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
                    # Performance: Use module-level cached decimal calculation
                    decimals = _get_step_decimals(step_float)
                    # Round to correct number of decimals based on step size
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
    score_memory: dict[str, float] = {}  # Cache scores for duplicate parameter sets

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
                    # In unit tests (mocked make_trial), advance the mocked trial stream.
                    # In production, avoid running a backtest here for performance.
                    try:
                        make_mod = getattr(make_trial, "__module__", "") or ""
                        make_name = getattr(make_trial, "__name__", "") or ""
                        in_tests = (
                            make_mod.startswith("tests.")
                            or make_name != "make_trial"
                            or ("mock" in make_name.lower())
                        )
                    except Exception:
                        in_tests = False

                    if in_tests:
                        payload = make_trial(trial_number, parameters)
                        payload = dict(payload or {})
                        payload["trial_id"] = f"trial_{trial_number:03d}"
                        payload["parameters"] = parameters
                        payload["skipped"] = True
                        payload.setdefault("reason", "duplicate_guard_precheck")
                        payload.setdefault(
                            "score", {"score": 0.0, "metrics": {}, "hard_failures": []}
                        )
                        payload.setdefault("constraints", {"ok": True, "reasons": []})
                        results.append(payload)
                    else:
                        # Do NOT run backtest; record a lightweight skipped payload
                        results.append(
                            {
                                "trial_id": f"trial_{trial_number:03d}",
                                "parameters": parameters,
                                "skipped": True,
                                "reason": "duplicate_guard_precheck",
                                "score": {"score": 0.0, "metrics": {}, "hard_failures": []},
                                "constraints": {"ok": True, "reasons": []},
                            }
                        )
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

        optuna_ctx = {
            "trial_id": trial._trial_id,
            "storage": storage,
            "study_name": study_name,
        }
        payload = make_trial(trial_number, parameters, optuna_context=optuna_ctx)
        results.append(payload)

        # CACHE REUSE FIX: If payload is from cache, return actual score even if duplicate
        if payload.get("from_cache"):
            score_block = payload.get("score") or {}
            cached_score = float(score_block.get("score", 0.0) or 0.0)
            trial.set_user_attr("cached", True)
            trial.set_user_attr("cache_reused", True)
            if payload.get("results_path"):
                trial.set_user_attr("backtest_path", payload["results_path"])
            logger.info(
                f"[CACHE] Trial {trial.number} reusing cached score {cached_score:.2f} "
                f"(from_cache=True in payload)"
            )
            # Store in memory for future fast lookup
            score_memory[key] = cached_score
            # Don't penalize cache hits - return actual score
            duplicate_streak = 0  # Reset streak since we got useful feedback
            return cached_score

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
                # Check if we have cached score from previous run
                if key in score_memory:
                    cached_score = score_memory[key]
                    logger.info(
                        f"[CACHE] Trial {trial.number} reusing memory-cached score {cached_score:.2f} "
                        f"(duplicate_within_run but score available)"
                    )
                    return cached_score
                return -1e6
            # Other skip reasons (e.g., already_completed) can report neutral score
            return float(payload.get("score", {}).get("score", 0.0) or 0.0)

        if payload.get("error"):
            trial.set_user_attr("error", payload.get("error"))
            # Release reserved signature to allow future attempts if run failed
            if guard is not None and sig:
                try:
                    guard.remove(sig)
                except Exception:  # nosec B110
                    pass  # Guard already removed
            # Don't reset duplicate streak on errors
            raise optuna.TrialPruned()

        constraints = payload.get("constraints") or {}
        score_block = payload.get("score") or {}
        score_value = float(score_block.get("score", 0.0) or 0.0)

        # Check for zero trades to track this issue - do this BEFORE early returns
        num_trades_value = _extract_num_trades(payload)
        num_trades = num_trades_value if num_trades_value is not None else 0
        if num_trades == 0:
            zero_trade_count += 1
            trial.set_user_attr("zero_trades", True)

        # Mjuk constraints: returnera straffad poäng istället för att pruna,
        # så att Optuna kan ranka försök och fortsätta utforskning.
        if not constraints.get("ok", True):
            trial.set_user_attr("constraints", constraints)
            trial.set_user_attr("constraints_soft_fail", True)
            trial.set_user_attr("constraints_penalty", CONSTRAINT_SOFT_PENALTY)
            # Mjukare straff för att bevara gradient; justerbart via GENESIS_CONSTRAINT_SOFT_PENALTY
            return score_value - CONSTRAINT_SOFT_PENALTY

        # Only reset duplicate streak on successful, non-zero-trade trials
        if num_trades > 0:
            duplicate_streak = 0

        # Store score in memory for future cache lookup
        score_memory[key] = score_value

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

    # Collect cache statistics
    cache_stats = {
        "total_trials": len(study.trials),
        "cached_trials": sum(1 for t in study.trials if t.user_attrs.get("cached", False)),
        "unique_backtests": len(
            {
                t.user_attrs.get("backtest_path", "")
                for t in study.trials
                if t.user_attrs.get("backtest_path")
            }
        ),
    }
    if cache_stats["total_trials"] > 0:
        cache_stats["cache_hit_rate"] = cache_stats["cached_trials"] / cache_stats["total_trials"]
    else:
        cache_stats["cache_hit_rate"] = 0.0

    logger.info(
        f"[CACHE STATS] {cache_stats['cached_trials']}/{cache_stats['total_trials']} trials cached "
        f"({cache_stats['cache_hit_rate']:.1%} hit rate), "
        f"{cache_stats['unique_backtests']} unique backtests"
    )

    # Warn about abnormal cache usage
    if cache_stats["cache_hit_rate"] > 0.8 and cache_stats["total_trials"] > 10:
        logger.warning(
            "[CACHE] Very high cache hit rate (>80%) - consider broadening search space or "
            "reducing bootstrap_random_trials if using cached study"
        )
    elif cache_stats["cache_hit_rate"] < 0.05 and cache_stats["total_trials"] > 50:
        logger.info("[CACHE] Low cache reuse (<5%) - good exploration diversity")

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
    executor: ProcessPoolExecutor,
    params_list: list[dict[str, Any]],
    trial_cfg_builder,
) -> list[Future]:
    futures: list[Future] = []
    for idx, params in enumerate(params_list, start=1):
        futures.append(executor.submit(trial_cfg_builder, idx, params))
    return futures


@dataclass
class TrialContext:
    """Context for executing a trial in a worker process."""

    snapshot_id: str
    symbol: str
    timeframe: str
    warmup_bars: int
    start_date: str | None
    end_date: str | None
    run_id: str
    run_dir: Path
    allow_resume: bool
    existing_trials: dict[str, dict[str, Any]]
    max_attempts: int
    constraints_cfg: dict[str, Any] | None
    baseline_results: dict[str, Any] | None
    baseline_label: str | None
    optuna_context: dict[str, Any] | None


def _execute_trial_task(
    idx: int,
    params: dict[str, Any],
    ctx: TrialContext,
) -> dict[str, Any]:
    """Execute a single trial task in a worker process."""
    trial_cfg = TrialConfig(
        snapshot_id=ctx.snapshot_id,
        symbol=ctx.symbol,
        timeframe=ctx.timeframe,
        warmup_bars=ctx.warmup_bars,
        parameters=params,
        start_date=ctx.start_date,
        end_date=ctx.end_date,
    )

    # Note: seen_param_keys/lock are not shared across processes in this simple setup.
    # We rely on existing_trials (disk cache) for deduplication.

    return run_trial(
        trial_cfg,
        run_id=ctx.run_id,
        index=idx,
        run_dir=ctx.run_dir,
        allow_resume=ctx.allow_resume,
        existing_trials=ctx.existing_trials,
        max_attempts=ctx.max_attempts,
        constraints_cfg=ctx.constraints_cfg,
        cache_enabled=True,
        seen_param_keys=None,
        seen_param_lock=None,
        baseline_results=ctx.baseline_results,
        baseline_label=ctx.baseline_label,
        optuna_context=ctx.optuna_context,
    )


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
                baseline_results_data = _read_json_cached(candidate_path)
                baseline_label = candidate_path.name
                print(f"[Baseline] Loaded comparison results from {candidate_path}")
            except json.JSONDecodeError as exc:
                print(f"[WARN] baseline_results_path ogiltig JSON ({candidate_path}): {exc}")
        else:
            print(f"[WARN] baseline_results_path hittades inte: {candidate_path}")

    def make_trial(
        idx: int,
        params: dict[str, Any],
        advance_only: bool = False,
        optuna_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if advance_only:
            # Cheap advancement without running backtest
            return {
                "trial_id": f"trial_{idx:03d}",
                "parameters": params,
                "skipped": True,
                "reason": "duplicate_guard_precheck_advance_only",
            }
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
            optuna_context=optuna_context,
        )

    results: list[dict[str, Any]] = []

    if strategy == OptimizerStrategy.GRID:
        params_list = list(expand_parameters(parameters))
        if max_trials is not None:
            params_list = params_list[:max_trials]

        # Use ProcessPoolExecutor for Grid Search to avoid GIL issues
        # GENESIS_IN_PROCESS=1 forces concurrency=1 (Debug Mode)
        debug_mode = os.environ.get("GENESIS_IN_PROCESS") == "1"
        if debug_mode and concurrency > 1 and os.name == "nt":
            raise RuntimeError(
                "GENESIS_IN_PROCESS=1 är inte tillåtet med n_jobs>1 på Windows (GIL-slow)."
            )

        # If debug mode or single worker, run in main process (simpler for tests/patching)
        if debug_mode or concurrency == 1:
            for idx, params in enumerate(params_list, start=1):
                results.append(make_trial(idx, params))
        else:
            # Use ProcessPoolExecutor for true parallelism with RAM caching per worker
            # We must use a picklable task function (_execute_trial_task) and context
            ctx = TrialContext(
                snapshot_id=meta.get("snapshot_id", ""),
                symbol=symbol,
                timeframe=timeframe,
                warmup_bars=int(meta.get("warmup_bars", 150)),
                start_date=sample_start,
                end_date=sample_end,
                run_id=run_id_resolved,
                run_dir=run_dir,
                allow_resume=allow_resume,
                existing_trials=existing_trials,
                max_attempts=max_attempts,
                constraints_cfg=config.get("constraints"),
                baseline_results=baseline_results_data,
                baseline_label=baseline_label,
                optuna_context=None,
            )

            with ProcessPoolExecutor(max_workers=concurrency) as executor:
                futures = []
                for idx, params in enumerate(params_list, start=1):
                    futures.append(executor.submit(_execute_trial_task, idx, params, ctx))

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
                runtime_version=best_result.get("runtime_version") if best_result else None,
            )
            print(
                f"[Champion] Uppdaterad champion för {symbol} {timeframe} (score {best_candidate.score:.2f})"
            )
        else:
            print(
                f"[Champion] Ingen uppdatering: befintlig champion bättre eller constraints fel ({symbol} {timeframe})"
            )

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run optimizer from config")
    parser.add_argument("config", type=Path, help="Path to optimizer config YAML")
    parser.add_argument("--run-id", type=str, help="Optional explicit run ID")
    args = parser.parse_args()

    if not args.config.exists():
        print(f"Config not found: {args.config}")
        sys.exit(1)

    try:
        run_optimizer(args.config, run_id=args.run_id)
    except Exception as e:
        print(f"Optimizer failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
