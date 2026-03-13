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
from core.optimizer.runner_optuna_orchestration import (
    collect_comparability_warnings_impl,
    compute_optuna_resume_signature_impl,
    create_optuna_study_impl,
    dig_impl,
    enforce_score_version_compatibility_impl,
    extract_results_path_from_champion_record_impl,
    extract_score_version_from_champion_record_impl,
    extract_score_version_from_result_payload_impl,
    load_backtest_info_from_results_path_impl,
    resolve_score_version_for_optimizer_impl,
    run_optuna_impl,
    select_optuna_pruner_impl,
    select_optuna_sampler_impl,
    select_top_n_from_optuna_storage_impl,
    verify_or_set_optuna_study_score_version_impl,
    verify_or_set_optuna_study_signature_impl,
)
from core.optimizer.scoring import MetricThresholds, score_backtest
from core.utils.dict_merge import deep_merge_dicts
from core.utils.diffing import summarize_metrics_diff
from core.utils.diffing.canonical import canonicalize_config
from core.utils.diffing.optuna_guard import estimate_zero_trade
from core.utils.diffing.results_diff import diff_backtest_results
from core.utils.diffing.trial_cache import TrialResultCache
from core.utils.env_flags import env_flag_enabled
from core.utils.optuna_helpers import param_signature, set_global_seeds


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
_DEFAULT_CONFIG_RUNTIME_VERSION: int | None = None
_DEFAULT_CONFIG_LOCK = threading.Lock()

# Backtest economics defaults (capital/fees) may be defined in config/backtest_defaults.yaml.
# Optuna trials should not implicitly depend on that file changing during a long run, so we load
# it once (thread-safe) and pin the values into each trial's execution.
_BACKTEST_DEFAULTS_CACHE: dict[str, Any] | None = None
_BACKTEST_DEFAULTS_LOCK = threading.Lock()

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

    Enabled when GENESIS_OPTIMIZER_JSON_CACHE is truthy ("1" or "true",
    case- and whitespace-insensitive).
    """
    use_cache = (os.environ.get("GENESIS_OPTIMIZER_JSON_CACHE") or "").strip().lower() in {
        "1",
        "true",
    }
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


def _compute_optuna_resume_signature(
    *,
    config: dict[str, Any],
    config_path: Path,
    git_commit: str,
    runtime_version: int | None,
) -> dict[str, Any]:
    return compute_optuna_resume_signature_impl(
        config=config,
        config_path=config_path,
        git_commit=git_commit,
        runtime_version=runtime_version,
        project_root=PROJECT_ROOT,
    )


def _verify_or_set_optuna_study_signature(study: Any, expected: dict[str, Any]) -> None:
    return verify_or_set_optuna_study_signature_impl(study, expected)


def _verify_or_set_optuna_study_score_version(study: Any, expected_score_version: str) -> None:
    return verify_or_set_optuna_study_score_version_impl(
        study,
        expected_score_version,
        logger=logger,
    )


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
    global _DEFAULT_CONFIG_RUNTIME_VERSION

    with _DEFAULT_CONFIG_LOCK:
        if _DEFAULT_CONFIG_CACHE is None:
            from core.config.authority import ConfigAuthority

            authority = ConfigAuthority()
            default_cfg_obj, _, runtime_version = authority.get()
            _DEFAULT_CONFIG_CACHE = default_cfg_obj.model_dump()
            _DEFAULT_CONFIG_RUNTIME_VERSION = runtime_version
        return _DEFAULT_CONFIG_CACHE


def _get_default_runtime_version() -> int | None:
    """Return runtime.json version used for the cached default config (if loaded)."""
    # Ensure _DEFAULT_CONFIG_RUNTIME_VERSION is populated when available.
    _ = _get_default_config()
    return _DEFAULT_CONFIG_RUNTIME_VERSION


def _get_backtest_defaults() -> dict[str, Any]:
    """Load config/backtest_defaults.yaml once and cache it.

    Notes:
        - This is used to pin capital/commission/slippage for optimizer trials so that
          long runs are not affected by mid-run edits to the defaults file.
        - Fallbacks are applied in `_get_backtest_economics()`.
    """

    global _BACKTEST_DEFAULTS_CACHE

    with _BACKTEST_DEFAULTS_LOCK:
        if _BACKTEST_DEFAULTS_CACHE is None:
            path = PROJECT_ROOT / "config" / "backtest_defaults.yaml"
            if not path.exists():
                _BACKTEST_DEFAULTS_CACHE = {}
                return _BACKTEST_DEFAULTS_CACHE
            try:
                raw = yaml.safe_load(path.read_text(encoding="utf-8"))
                _BACKTEST_DEFAULTS_CACHE = raw if isinstance(raw, dict) else {}
            except Exception:
                _BACKTEST_DEFAULTS_CACHE = {}
        return _BACKTEST_DEFAULTS_CACHE


def _get_backtest_economics() -> tuple[float, float, float]:
    """Return (capital, commission, slippage) with safe fallbacks."""

    defaults = _get_backtest_defaults()

    def _as_float(key: str, fallback: float) -> float:
        try:
            return float(defaults.get(key, fallback))
        except (TypeError, ValueError):
            return fallback

    capital = _as_float("capital", 10000.0)
    commission = _as_float("commission", 0.002)
    slippage = _as_float("slippage", 0.0005)
    return capital, commission, slippage


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


def _select_top_n_from_optuna_storage(run_meta: dict[str, Any], top_n: int) -> list[dict[str, Any]]:
    return select_top_n_from_optuna_storage_impl(
        run_meta,
        top_n,
        optuna_available=OPTUNA_AVAILABLE,
    )


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
                # Legacy artifacts may contain non-standard floats (Infinity/NaN) written via
                # json.dumps(..., allow_nan=True). orjson rejects these tokens on load.
                # Fall back to stdlib json for backwards-compatible resume.
                try:
                    trial_data = _orjson.loads(content)
                except ValueError:
                    trial_data = json.loads(content)
            else:
                trial_data = json.loads(content)

            # JSON always returns exact dict, but be defensive
            if not isinstance(trial_data, dict):
                continue

            params = trial_data.get("parameters")
            if params:
                key = _trial_key(params)
                existing[key] = trial_data
        except (ValueError, OSError) as exc:
            logger.warning("Skipping unreadable trial artifact %s: %s", trial_path.name, exc)
            continue

    return existing


def _extract_results_path_from_log(log_content: str) -> Path | None:
    """Extract the backtest result JSON path from subprocess logs.

    scripts/run_backtest.py prints:
        [OK] Results saved:\n
        json: <path>\n
        trades_csv: ...

    TradeLogger also prints:
        [SAVED] Results: <path>

    Older code paths may print:
        results: <path>
    """

    import re

    patterns = [
        r"^\s*results:\s*(.+?\.json)\s*$",
        r"^\s*json:\s*(.+?\.json)\s*$",
        r"^\[SAVED\]\s*Results:\s*(.+?\.json)\s*$",
    ]

    for pat in patterns:
        matches = re.findall(pat, log_content, flags=re.MULTILINE)
        if not matches:
            continue
        # Prefer the last match in case multiple backtests ran within the same log.
        candidate = Path(str(matches[-1]).strip())
        if not candidate.is_absolute():
            candidate = PROJECT_ROOT / candidate
        if candidate.exists():
            return candidate
    return None


def _ensure_run_metadata(
    run_dir: Path, config_path: Path, meta: dict[str, Any], run_id: str
) -> None:
    meta_path = run_dir / "run_meta.json"

    repo_root = PROJECT_ROOT
    try:
        config_rel = str(config_path.relative_to(repo_root))
    except ValueError:
        config_rel = str(config_path)

    expected_score_version = _resolve_score_version_for_optimizer()

    if meta_path.exists():
        try:
            existing = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning(
                "Failed to read existing run_meta.json at %s, treating as empty metadata: %s",
                meta_path,
                exc,
            )
            existing = {}
        if not isinstance(existing, dict):
            existing = {}

        expected = {
            "run_id": run_id,
            "config_path": config_rel,
            "snapshot_id": meta.get("snapshot_id"),
            "symbol": meta.get("symbol"),
            "timeframe": meta.get("timeframe"),
            "score_version": expected_score_version,
        }

        mismatches: list[str] = []
        for k, exp in expected.items():
            if exp is None:
                continue
            cur = existing.get(k)
            if cur is None or cur == "":
                continue
            if str(cur) != str(exp):
                mismatches.append(f"{k} existing={cur!r} expected={exp!r}")

        allow_mismatch = os.environ.get("GENESIS_ALLOW_RUN_META_MISMATCH") == "1"
        if mismatches and not allow_mismatch:
            raise ValueError(
                "run_meta.json mismatch (vägrar återanvända run_dir med annan konfig/metadata): "
                + "; ".join(mismatches)
                + ". Override via GENESIS_ALLOW_RUN_META_MISMATCH=1"
            )
        if mismatches and allow_mismatch:
            print(
                "[WARN] run_meta.json mismatch tolerated via GENESIS_ALLOW_RUN_META_MISMATCH=1: "
                + "; ".join(mismatches)
            )

        # Backfill missing fields to improve forensics for older/partial run_meta.json.
        did_change = False
        for k, exp in expected.items():
            if exp is None:
                continue
            if existing.get(k) is None or existing.get(k) == "":
                existing[k] = exp
                did_change = True
        existing.setdefault("raw_meta", meta)
        if did_change:
            existing["updated_at"] = datetime.now(UTC).isoformat()
            _atomic_write_text(meta_path, json.dumps(_serialize_meta(existing), indent=2))
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
    meta_payload = {
        "run_id": run_id,
        "config_path": config_rel,
        "snapshot_id": meta.get("snapshot_id"),
        "symbol": meta.get("symbol"),
        "timeframe": meta.get("timeframe"),
        "score_version": expected_score_version,
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
    """Deep merge override dict into base dict via shared helper."""
    return deep_merge_dicts(base, override)


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
    """Derive (start_date, end_date) from snapshot_id.

    Supported formats (backwards compatible):
        - tTEST_1h_20240101_20240201_v1
        - snap_tBTCUSD_3h_2024-01-02_2024-12-31_v1

    Implementation note:
        Historically we assumed a fixed underscore layout. Newer snapshot_ids may include
        extra tokens (e.g. prefix + symbol + timeframe), so we now locate date-like tokens
        instead of relying on fixed indices.
    """

    if not snapshot_id:
        raise ValueError("trial snapshot_id saknas")

    parts = snapshot_id.split("_")
    if len(parts) < 4:
        raise ValueError("snapshot_id saknar start/end datum")

    import re

    # Prefer extracting the last two date tokens, so prefixes never shift indices.
    date_tokens: list[str] = []
    for p in parts:
        token = p.strip()
        if not token:
            continue
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", token) or re.fullmatch(r"\d{8}", token):
            date_tokens.append(token)

    if len(date_tokens) >= 2:
        return date_tokens[-2], date_tokens[-1]

    # Fallback to the legacy positional convention.
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
        encoding="utf-8",
        errors="replace",
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


def _coerce_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        v = value.strip()
        return v or None
    return None


_ALLOWED_SCORE_VERSIONS: set[str] = {"v1", "v2"}


def _resolve_score_version_for_optimizer(explicit: str | None = None) -> str:
    return resolve_score_version_for_optimizer_impl(explicit)


def _extract_score_version_from_result_payload(result: dict[str, Any] | None) -> str | None:
    return extract_score_version_from_result_payload_impl(result)


def _extract_score_version_from_champion_record(current: Any) -> str | None:
    return extract_score_version_from_champion_record_impl(current)


def _extract_results_path_from_champion_record(current: Any) -> str | None:
    return extract_results_path_from_champion_record_impl(current)


def _enforce_score_version_compatibility(
    *,
    current_score_version: str | None,
    candidate_score_version: str | None,
    context: str,
) -> None:
    return enforce_score_version_compatibility_impl(
        current_score_version=current_score_version,
        candidate_score_version=candidate_score_version,
        context=context,
    )


def _dig(mapping: dict[str, Any], dotted_path: str) -> Any:
    return dig_impl(mapping, dotted_path)


def _load_backtest_info_from_results_path(results_path: str | None) -> dict[str, Any] | None:
    return load_backtest_info_from_results_path_impl(
        results_path,
        project_root=PROJECT_ROOT,
        backtest_results_dir=BACKTEST_RESULTS_DIR,
        read_json_cached=_read_json_cached,
    )


def _collect_comparability_warnings(
    current_info: dict[str, Any] | None,
    candidate_info: dict[str, Any] | None,
) -> list[str]:
    return collect_comparability_warnings_impl(
        current_info,
        candidate_info,
        dig=_dig,
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


def _trial_requests_htf_exits(effective_cfg: dict[str, Any]) -> bool:
    """Return True if the trial config implies HTF exits should be enabled.

    Why:
    - The backtest engine selects the new HTF exit engine based on GENESIS_HTF_EXITS.
    - If we tune/populate htf_exit_config but forget to enable the flag, the whole HTF
        exit dimension becomes a no-op and artifacts will show HTF as not loaded/seen.
    """

    htf_exit_cfg = effective_cfg.get("htf_exit_config")
    return isinstance(htf_exit_cfg, dict) and bool(htf_exit_cfg)


def _run_backtest_direct(
    trial: TrialConfig,
    config_path: Path,
    optuna_context: dict[str, Any] | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> tuple[int, str, dict[str, Any] | None]:
    did_set_htf_exits = False
    prior_htf_exits = os.environ.get("GENESIS_HTF_EXITS")

    try:
        from core.pipeline import GenesisPipeline

        pipeline = GenesisPipeline()

        # Canonical mode for optimizer quality decisions: always run 1/1.
        # IMPORTANT: Direct execution bypasses scripts/run_backtest.py, so we must
        # enforce canonical env + seeding here too (including in worker processes).
        os.environ["GENESIS_MODE_EXPLICIT"] = "0"
        try:
            seed_value = int(os.environ.get("GENESIS_RANDOM_SEED", "42"))
        except ValueError:
            seed_value = 42
        # Unit tests may patch GenesisPipeline with a lightweight dummy that doesn't
        # implement the full pipeline API. In that case, seed globally as fallback.
        setup_env = getattr(pipeline, "setup_environment", None)
        if callable(setup_env):
            setup_env(seed=seed_value)
        else:  # pragma: no cover - exercised via unit tests
            set_global_seeds(seed_value)

        # Load config
        payload = json.loads(config_path.read_text(encoding="utf-8"))
        cfg = payload["cfg"]
        effective_cfg = payload.get("merged_config")
        if not isinstance(effective_cfg, dict):
            effective_cfg = cfg

        # Enable HTF exits when the trial config requests it.
        # Do this before engine creation so BacktestEngine selects the correct engine
        # and attempts to load HTF candles.
        if _trial_requests_htf_exits(effective_cfg) and "GENESIS_HTF_EXITS" not in os.environ:
            os.environ["GENESIS_HTF_EXITS"] = "1"
            did_set_htf_exits = True
        runtime_version_used = payload.get("runtime_version")
        runtime_version_current = _get_default_runtime_version()
        config_provenance: dict[str, object] = {
            "used_runtime_merge": False,
            "runtime_version_current": runtime_version_current,
            "runtime_version_used": runtime_version_used,
            "config_file": str(config_path),
            "config_file_is_complete": isinstance(payload.get("merged_config"), dict),
        }
        overrides = payload.get("overrides", {})

        # Load/Get engine
        # Include dates AND execution mode in cache key to prevent mixed-mode reuse.
        mode_sig = (
            f"fw{os.environ.get('GENESIS_FAST_WINDOW','')}"
            f"pc{os.environ.get('GENESIS_PRECOMPUTE_FEATURES','')}"
            f"htf{os.environ.get('GENESIS_HTF_EXITS','')}"
        )
        cache_key = (
            f"{trial.symbol}_{trial.timeframe}_{trial.start_date}_{trial.end_date}_{mode_sig}"
        )
        with _DATA_LOCK:
            if cache_key not in _DATA_CACHE:
                # Create engine via pipeline
                # This ensures we use the centralized defaults for capital/commission/etc.
                try:
                    engine_loader = pipeline.create_engine(
                        symbol=trial.symbol,
                        timeframe=trial.timeframe,
                        start_date=trial.start_date,
                        end_date=trial.end_date,
                        warmup_bars=trial.warmup_bars,
                        fast_window=True,
                    )
                except TypeError:
                    # Unit tests may patch GenesisPipeline with a minimal dummy that doesn't
                    # accept the fast_window kwarg.
                    engine_loader = pipeline.create_engine(
                        symbol=trial.symbol,
                        timeframe=trial.timeframe,
                        start_date=trial.start_date,
                        end_date=trial.end_date,
                        warmup_bars=trial.warmup_bars,
                    )

                # Critical: Set precompute flag BEFORE load_data() to ensure features are loaded/computed
                if env_flag_enabled(os.getenv("GENESIS_PRECOMPUTE_FEATURES"), default=False):
                    engine_loader.precompute_features = True
                if engine_loader.load_data():
                    # Hard guard: optimizer assumes canonical precompute is available.
                    # If precompute is requested but not ready, fail fast to avoid
                    # silent slow-path runs (incomparable results).
                    if (
                        os.environ.get("GENESIS_PRECOMPUTE_FEATURES") == "1"
                        and hasattr(engine_loader, "_precomputed_features")
                        and not getattr(engine_loader, "_precomputed_features", None)
                    ):
                        _DATA_CACHE[cache_key] = None
                    else:
                        _DATA_CACHE[cache_key] = engine_loader
                else:
                    _DATA_CACHE[cache_key] = None

            engine = _DATA_CACHE[cache_key]

        if engine is None:
            if os.environ.get("GENESIS_PRECOMPUTE_FEATURES") == "1":
                return (
                    1,
                    "Failed to load data or precompute features in canonical mode",
                    None,
                )
            return 1, "Failed to load data", None

        # Update warmup_bars in case it changed between trials
        engine.warmup_bars = trial.warmup_bars

        # Apply overrides (e.g. commission, slippage)
        if "commission" in overrides:
            engine.position_tracker.commission_rate = float(overrides["commission"])
        if "slippage" in overrides:
            engine.position_tracker.slippage_rate = float(overrides["slippage"])

        # Pruning
        pruning_callback = None
        if optuna_context:
            storage = optuna_context.get("storage")
            study_name = optuna_context.get("study_name")
            trial_id = optuna_context.get("trial_id")

            # In-memory/no-storage Optuna runs can't be loaded from a separate process/context.
            # Avoid noisy stacktraces in smoke-reruns when storage is null.
            if storage and study_name and trial_id is not None:
                try:
                    import optuna

                    # IMPORTANT:
                    # optuna.load_study() defaults to MedianPruner when pruner is not provided.
                    # That can silently enable pruning even when the main optimizer run intends
                    # to use NopPruner (no pruning). Always inject the pruner config from the
                    # optimizer context to keep behavior consistent.
                    pruner_cfg = optuna_context.get("pruner")
                    if isinstance(pruner_cfg, dict):
                        pruner_obj = _select_optuna_pruner(
                            pruner_cfg.get("name"), pruner_cfg.get("kwargs")
                        )
                    elif isinstance(pruner_cfg, str):
                        pruner_obj = _select_optuna_pruner(pruner_cfg, None)
                    else:
                        pruner_obj = _select_optuna_pruner(None, None)

                    study = optuna.load_study(
                        study_name=str(study_name),
                        storage=storage,
                        pruner=pruner_obj,
                    )

                    def _cb(step, value):
                        try:
                            t = optuna.trial.Trial(study, int(trial_id))
                            t.report(value, step)
                            return t.should_prune()
                        except Exception:
                            return False

                    pruning_callback = _cb
                except KeyError as err:  # pragma: no cover - expected for in-memory studies
                    logger.warning("Optuna pruning disabled (study not found): %s", err)
                except Exception as err:  # pragma: no cover - defensive guard
                    logger.warning(
                        "Optuna pruning disabled due to setup failure: %s", err, exc_info=True
                    )
        effective_cfg_for_run: dict[str, Any] | Any = effective_cfg
        if isinstance(effective_cfg, dict):
            effective_cfg_for_run = dict(effective_cfg)
            meta_for_run = dict(effective_cfg.get("meta") or {})
            meta_for_run["skip_champion_merge"] = True
            effective_cfg_for_run["meta"] = meta_for_run

        results = engine.run(
            policy={"symbol": trial.symbol, "timeframe": trial.timeframe},
            configs=effective_cfg_for_run,
            verbose=False,
            pruning_callback=pruning_callback,
        )

        # Ensure direct-mode results carry the same reproducibility metadata as subprocess mode.
        # This is required for drift detection and provenance auditing.
        if isinstance(results, dict):
            results.setdefault("config_provenance", config_provenance)
            results.setdefault("merged_config", effective_cfg)
            if runtime_version_used is not None:
                results.setdefault("runtime_version", runtime_version_used)
            if runtime_version_current is not None:
                results.setdefault("runtime_version_current", runtime_version_current)

        return 0, "", results

    except Exception as e:
        import traceback

        return 1, f"{e}\n{traceback.format_exc()}", None

    finally:
        # Restore environment if we temporarily enabled GENESIS_HTF_EXITS.
        if did_set_htf_exits:
            if prior_htf_exits is None:
                os.environ.pop("GENESIS_HTF_EXITS", None)
            else:
                os.environ["GENESIS_HTF_EXITS"] = str(prior_htf_exits)


def _build_backtest_cmd(
    trial: TrialConfig,
    *,
    start_date: str,
    end_date: str,
    capital_default: float,
    commission_default: float,
    slippage_default: float,
    config_file: Path | None,
    optuna_context: dict[str, Any] | None,
) -> list[str]:
    """Build the subprocess command for running a backtest.

    IMPORTANT (Windows/repro): Use sys.executable so the subprocess runs under the
    same interpreter/environment (e.g. venv) as the optimizer, instead of relying
    on PATH-resolved `python` which may point to a different installation.
    """

    cmd = [
        sys.executable,
        "-m",
        "scripts.run.run_backtest",
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
        "--capital",
        str(capital_default),
        "--commission",
        str(commission_default),
        "--slippage",
        str(slippage_default),
        "--fast-window",
        "--precompute-features",
    ]

    if config_file is not None:
        cmd.extend(["--config-file", str(config_file)])

    if optuna_context:
        storage = optuna_context.get("storage")
        study_name = optuna_context.get("study_name")
        trial_id = optuna_context.get("trial_id")
        if storage and study_name and trial_id is not None:
            pruner_cfg = optuna_context.get("pruner")
            pruner_name: str | None = None
            pruner_kwargs: dict[str, Any] | None = None
            if isinstance(pruner_cfg, dict):
                pruner_name = (
                    pruner_cfg.get("name")
                    or pruner_cfg.get("type")
                    or pruner_cfg.get("pruner")
                    or pruner_cfg.get("kind")
                )
                if isinstance(pruner_cfg.get("kwargs"), dict):
                    pruner_kwargs = pruner_cfg.get("kwargs")
            elif isinstance(pruner_cfg, str):
                pruner_name = pruner_cfg

            cmd.extend(
                [
                    "--optuna-trial-id",
                    str(trial_id),
                    "--optuna-storage",
                    str(storage),
                    "--optuna-study-name",
                    str(study_name),
                ]
            )

            # IMPORTANT:
            # scripts/run_backtest uses optuna.load_study for pruning in subprocess mode.
            # optuna.load_study defaults to MedianPruner if pruner is omitted, which can
            # silently enable pruning even when the main optimizer config requests pruner=none.
            if pruner_name:
                cmd.extend(["--optuna-pruner", str(pruner_name)])
            if pruner_kwargs:
                cmd.extend(
                    [
                        "--optuna-pruner-kwargs",
                        json.dumps(pruner_kwargs, separators=(",", ":")),
                    ]
                )

    return cmd


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
    capital_default, commission_default, slippage_default = _get_backtest_economics()

    # Pin scoring-version for the entire trial (and for any subprocess execution).
    score_version = _resolve_score_version_for_optimizer()

    key = _trial_key(trial.parameters)
    fingerprint_digest = key  # _trial_key already returns a SHA256 digest

    # Also compute the Optuna-style signature used by NoDupeGuard for cross-artifact binding.
    try:
        optuna_param_sig = param_signature(trial.parameters)
    except Exception:
        optuna_param_sig = fingerprint_digest

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

        # Optimizer/backtest runs must treat the trial config as authoritative.
        # Prevent BacktestEngine from implicitly merging the current champion.
        meta = dict(merged_cfg.get("meta") or {})
        meta["skip_champion_merge"] = True
        merged_cfg["meta"] = meta
        # Mark this config as "complete" by including merged_config + runtime_version.
        # This lets scripts/run_backtest skip re-merging runtime.json, preventing drift if runtime.json
        # changes during a long optimization run.
        config_payload = {
            "cfg": merged_cfg,
            "merged_config": merged_cfg,
            "runtime_version": _get_default_runtime_version(),
            "run_id": run_id,
            "trial_id": trial_id,
            "parameters": trial.parameters,
            "trial_key": fingerprint_digest,
            "param_signature": optuna_param_sig,
            "score_version": score_version,
            "created_at": datetime.now(UTC).isoformat(),
            "overrides": {
                "capital": capital_default,
                "commission": commission_default,
                "slippage": slippage_default,
            },
        }
        if derived_values:
            config_payload["derived"] = dict(derived_values)
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

    cmd = _build_backtest_cmd(
        trial,
        start_date=start_date,
        end_date=end_date,
        capital_default=capital_default,
        commission_default=commission_default,
        slippage_default=slippage_default,
        config_file=config_file,
        optuna_context=optuna_context,
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

    # Pin scoring version across subprocess/direct execution for deterministic comparability.
    base_env["GENESIS_SCORE_VERSION"] = score_version

    # Windows/stdio hardening: force UTF-8 for the backtest subprocess so its stdout/stderr can
    # be captured and/or written without UnicodeEncodeError/DecodeError surprises.
    base_env.setdefault("PYTHONUTF8", "1")
    base_env.setdefault("PYTHONIOENCODING", "utf-8")

    # Enable HTF exits for this trial when config requests it (unless user already set it).
    if config_file is not None and "GENESIS_HTF_EXITS" not in base_env:
        try:
            payload = json.loads(config_file.read_text(encoding="utf-8"))
            eff_cfg = payload.get("merged_config")
            if not isinstance(eff_cfg, dict):
                eff_cfg = payload.get("cfg")
            if isinstance(eff_cfg, dict) and _trial_requests_htf_exits(eff_cfg):
                base_env["GENESIS_HTF_EXITS"] = "1"
        except Exception:
            # Defensive: never break a trial because we couldn't inspect the config payload.
            pass

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
            # Ensure a log file exists for reproducibility/debugging even in direct mode.
            if not log_file.exists():
                _atomic_write_text(
                    log_file,
                    log
                    or "[INFO] Direct execution: stdout not captured to file.\n"
                    "[INFO] If you need full logs, set GENESIS_FORCE_SHELL=1.\n",
                )
            if returncode == 0 and results_dict:
                # Save results to file to match subprocess behavior
                results_path = output_dir / f"{trial.symbol}_{trial.timeframe}_{trial_id}.json"
                _atomic_write_text(results_path, _json_dumps(results_dict))
        else:
            returncode, log = _exec_backtest(cmd, cwd=PROJECT_ROOT, env=base_env, log_path=log_file)

        last_log_output = log
        attempt_duration = time.perf_counter() - attempt_started
        attempt_durations.append(attempt_duration)
        if returncode == 0:
            # Parse log file to find exact results path (avoids race condition with glob)
            if not results_dict:
                results_path: Path | None = None
                try:
                    log_content = log_file.read_text(encoding="utf-8")
                    results_path = _extract_results_path_from_log(log_content)
                except Exception as e:
                    print(f"[WARN] Could not parse log for results path: {e}")

                if results_path is None:
                    total_duration = time.perf_counter() - trial_started
                    error_payload = {
                        "trial_id": trial_id,
                        "parameters": trial.parameters,
                        "error": "results_path_not_found",
                        "error_details": "Could not locate results JSON path in subprocess logs",
                        "log": log_file.name,
                        "attempts": max_attempts - attempts_remaining,
                        "duration_seconds": total_duration,
                        "attempt_durations": attempt_durations,
                    }
                    if derived_values:
                        error_payload["derived"] = derived_values
                    if config_file is not None:
                        error_payload["config_path"] = config_file.name
                    _atomic_write_text(trial_file, _json_dumps(error_payload))
                    return error_payload

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
                    _atomic_write_text(trial_file, _json_dumps(error_payload))
                    # Returnera error payload så att objective kan lyfta TrialPruned
                    return error_payload
            else:
                results = results_dict
                # results_path is already set in the if block above

            # If the backtest was pruned, propagate as an error payload so Optuna marks the
            # trial as PRUNED (instead of scoring it as a misleading zero-trade run).
            if results.get("error") == "pruned":
                total_duration = time.perf_counter() - trial_started
                pruned_payload = {
                    "trial_id": trial_id,
                    "parameters": trial.parameters,
                    "results_path": results_path.name,
                    "error": "pruned",
                    "pruned_at": results.get("pruned_at"),
                    "metrics": results.get("metrics"),
                    "log": log_file.name,
                    "attempts": max_attempts - attempts_remaining,
                    "duration_seconds": total_duration,
                    "attempt_durations": attempt_durations,
                }
                if derived_values:
                    pruned_payload["derived"] = derived_values
                if config_file is not None:
                    pruned_payload["config_path"] = config_file.name
                _atomic_write_text(trial_file, _json_dumps(pruned_payload))
                return pruned_payload

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
                        "score_version": score_version,
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
                _atomic_write_text(trial_file, _json_dumps(abort_payload))
                return abort_payload

            # Allow overriding scoring hard-failure thresholds via optimizer constraints.
            # This prevents the objective from collapsing to ~-100 when PF<1.0 is expected
            # in early explore stages (the optimizer otherwise gets almost no gradient).
            scoring_thresholds = MetricThresholds()
            if isinstance(constraints_cfg, dict):
                raw_scoring = constraints_cfg.get("scoring_thresholds")
                if isinstance(raw_scoring, dict):
                    if raw_scoring.get("min_trades") is not None:
                        try:
                            scoring_thresholds.min_trades = int(raw_scoring["min_trades"])
                        except (TypeError, ValueError):
                            pass
                    if raw_scoring.get("min_profit_factor") is not None:
                        try:
                            scoring_thresholds.min_profit_factor = float(
                                raw_scoring["min_profit_factor"]
                            )
                        except (TypeError, ValueError):
                            pass
                    if raw_scoring.get("max_max_dd") is not None:
                        try:
                            scoring_thresholds.max_max_dd = float(raw_scoring["max_max_dd"])
                        except (TypeError, ValueError):
                            pass

            score = score_backtest(
                results,
                thresholds=scoring_thresholds,
                score_version=score_version,
            )
            enforcement = enforce_constraints(
                score,
                trial.parameters,
                constraints_cfg=constraints_cfg,
            )
            score_value = score.get("score")
            baseline_block = score.get("baseline") if isinstance(score, dict) else None
            score_version_from_score = None
            if isinstance(baseline_block, dict):
                score_version_from_score = baseline_block.get("score_version")
            score_serializable = {
                "score": score_value,
                "metrics": score.get("metrics"),
                "hard_failures": list(score.get("hard_failures") or []),
                "score_version": score_version_from_score or score_version,
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
    _atomic_write_text(trial_file, _json_dumps(final_payload))
    return final_payload


def _select_optuna_sampler(
    name: str | None,
    kwargs: dict[str, Any] | None,
    concurrency: int = 1,
):
    return select_optuna_sampler_impl(
        name,
        kwargs,
        concurrency=concurrency,
        optuna_available=OPTUNA_AVAILABLE,
        tpe_sampler_cls=TPESampler,
        random_sampler_cls=RandomSampler,
        cmaes_sampler_cls=CmaEsSampler,
    )


def _select_optuna_pruner(
    name: str | None,
    kwargs: dict[str, Any] | None,
):
    return select_optuna_pruner_impl(
        name,
        kwargs,
        optuna_available=OPTUNA_AVAILABLE,
        median_pruner_cls=MedianPruner,
        successive_halving_pruner_cls=SuccessiveHalvingPruner,
        hyperband_pruner_cls=HyperbandPruner,
        nop_pruner_cls=NopPruner,
    )


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
    return create_optuna_study_impl(
        run_id,
        storage,
        study_name,
        sampler_cfg,
        pruner_cfg,
        direction,
        allow_resume,
        concurrency=concurrency,
        heartbeat_interval=heartbeat_interval,
        heartbeat_grace_period=heartbeat_grace_period,
        optuna_available=OPTUNA_AVAILABLE,
        select_optuna_sampler=_select_optuna_sampler,
        select_optuna_pruner=_select_optuna_pruner,
        rdb_storage_cls=RDBStorage,
        create_study=getattr(optuna, "create_study", None),
        optuna_lock=_OPTUNA_LOCK,
    )


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
    resume_signature: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if not OPTUNA_AVAILABLE:
        raise RuntimeError("Optuna-strategi vald men optuna är inte installerat")

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

    return run_optuna_impl(
        study_config=study_config,
        parameters_spec=parameters_spec,
        make_trial=make_trial,
        run_dir=run_dir,
        run_id=run_id,
        existing_trials=existing_trials,
        max_trials=max_trials,
        concurrency=concurrency,
        allow_resume=allow_resume,
        resume_signature=resume_signature,
        create_optuna_study=_create_optuna_study,
        verify_or_set_optuna_study_signature=_verify_or_set_optuna_study_signature,
        verify_or_set_optuna_study_score_version=_verify_or_set_optuna_study_score_version,
        resolve_score_version_for_optimizer=_resolve_score_version_for_optimizer,
        suggest_parameters=_suggest_parameters,
        trial_key=_trial_key,
        extract_num_trades=_extract_num_trades,
        atomic_write_text=_atomic_write_text,
        serialize_meta=_serialize_meta,
        json_dumps=_json_dumps,
        constraint_soft_penalty=CONSTRAINT_SOFT_PENALTY,
        logger=logger,
        optuna_module=optuna,
    )


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
    # Ensure global determinism for the main process
    try:
        seed_val = int(os.environ.get("GENESIS_RANDOM_SEED", "42"))
    except ValueError:
        seed_val = 42
    set_global_seeds(seed_val)

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
    run_dir = (PROJECT_ROOT / "results" / "hparam_search" / run_id_resolved).resolve()

    existing_trials = _load_existing_trials(run_dir) if allow_resume and run_dir.exists() else {}
    seen_param_keys: set[str] = set()
    seen_param_lock = threading.Lock()
    run_dir.mkdir(parents=True, exist_ok=True)
    _ensure_run_metadata(run_dir, config_path.resolve(), meta, run_id_resolved)

    run_meta_path = run_dir / "run_meta.json"
    try:
        run_meta_for_sig = json.loads(run_meta_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        run_meta_for_sig = {}

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
        runtime_version = _get_default_runtime_version()
        resume_signature = _compute_optuna_resume_signature(
            config=config,
            config_path=config_path.resolve(),
            git_commit=str(run_meta_for_sig.get("git_commit", "unknown")),
            runtime_version=runtime_version,
        )
        try:
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
                    resume_signature=resume_signature,
                )
            )
        except ValueError as exc:
            # Robustness: Om Optuna-budgeten är slut (timeout/end_at) vill vi fortfarande
            # kunna köra validation-steget vid resume (där top-N kan hämtas ur storage).
            print(f"[WARN] Optuna kunde inte köras (ValueError): {exc}")
    else:
        raise ValueError(f"Okänd optimizer-strategi: {strategy}")

    run_meta_path = run_dir / "run_meta.json"
    try:
        run_meta = json.loads(run_meta_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        run_meta = {}

    # Optional two-stage flow: explore on the primary window, then validate top-N candidates
    # on a (typically longer/stricter) validation window before champion promotion.
    validation_cfg = runs_cfg.get("validation")
    validation_results: list[dict[str, Any]] | None = None
    if isinstance(validation_cfg, dict) and _as_bool(validation_cfg.get("enabled", True)):
        try:
            top_n_raw = validation_cfg.get("top_n", 0)
            top_n = int(top_n_raw) if top_n_raw is not None else 0
        except (TypeError, ValueError):
            top_n = 0

        if top_n > 0:
            # Rank explore results by score (including soft constraint penalties) and pick top-N
            ranked: list[tuple[float, dict[str, Any]]] = []
            for r in results:
                if r.get("error") or r.get("skipped"):
                    continue
                score_block = r.get("score") or {}
                try:
                    s = float(score_block.get("score"))
                except (TypeError, ValueError):
                    continue
                ranked.append((s, r))
            ranked.sort(key=lambda x: x[0], reverse=True)
            selected = [r for _s, r in ranked[:top_n]]

            # Fallback: Om vi inte har några lokala results (t.ex. resume efter avbrott)
            # försök hämta top-N direkt från Optuna storage.
            if not selected and strategy == OptimizerStrategy.OPTUNA:
                selected = _select_top_n_from_optuna_storage(run_meta, top_n)

            if selected:
                val_start: str | None = None
                val_end: str | None = None
                if _as_bool(validation_cfg.get("use_sample_range")):
                    val_start, val_end = _resolve_sample_range(
                        str(meta.get("snapshot_id", "")),
                        validation_cfg,
                    )

                val_dir = (run_dir / "validation").resolve()
                val_dir.mkdir(parents=True, exist_ok=True)
                val_allow_resume = bool(validation_cfg.get("resume", allow_resume))
                val_existing_trials = {}
                if val_allow_resume and val_dir.exists():
                    val_existing_trials = _load_existing_trials(val_dir)
                val_constraints_cfg = validation_cfg.get("constraints")
                if val_constraints_cfg is None:
                    val_constraints_cfg = config.get("constraints")
                if not isinstance(val_constraints_cfg, dict):
                    val_constraints_cfg = None

                validation_results = []
                for idx, base_result in enumerate(selected, start=1):
                    params = dict(base_result.get("parameters") or {})
                    trial_cfg = TrialConfig(
                        snapshot_id=str(meta.get("snapshot_id", "")),
                        symbol=symbol,
                        timeframe=timeframe,
                        warmup_bars=int(meta.get("warmup_bars", 150)),
                        parameters=params,
                        start_date=val_start,
                        end_date=val_end,
                    )
                    payload = run_trial(
                        trial_cfg,
                        run_id=run_id_resolved,
                        index=idx,
                        run_dir=val_dir,
                        allow_resume=val_allow_resume,
                        existing_trials=val_existing_trials,
                        max_attempts=max_attempts,
                        constraints_cfg=val_constraints_cfg,
                        cache_enabled=True,
                        seen_param_keys=None,
                        seen_param_lock=None,
                        baseline_results=baseline_results_data,
                        baseline_label=baseline_label,
                        optuna_context=None,
                    )
                    if isinstance(payload, dict):
                        payload.setdefault("stage", "validation")
                    validation_results.append(payload)

                # Attach validation metadata to run_meta for traceability
                run_meta.setdefault("validation", {}).update(
                    {
                        "enabled": True,
                        "top_n": top_n,
                        "sample_start": val_start,
                        "sample_end": val_end,
                        "constraints": val_constraints_cfg,
                        "validated": len(validation_results),
                        "validation_dir": str(val_dir),
                    }
                )
                _atomic_write_text(run_meta_path, _json_dumps(_serialize_meta(run_meta)))

    # If validation ran, prefer champion promotion based on validation outcomes.
    results_for_promotion = validation_results if validation_results is not None else results

    # Champion promotion is configurable to avoid accidental updates during smoke/explore runs.
    promotion_cfg = runs_cfg.get("promotion") or {}
    promotion_enabled = _as_bool(promotion_cfg.get("enabled", True))
    try:
        min_improvement = float(promotion_cfg.get("min_improvement", 0.0) or 0.0)
    except (TypeError, ValueError):
        min_improvement = 0.0

    best_candidate: ChampionCandidate | None = None
    best_result: dict[str, Any] | None = None
    for result in results_for_promotion:
        candidate = _candidate_from_result(result)
        if candidate is None:
            continue
        if best_candidate is None or candidate.score > best_candidate.score:
            best_candidate = candidate
            best_result = result

    if best_candidate is not None and promotion_enabled:
        manager = ChampionManager()
        current = manager.load_current(symbol, timeframe)
        should_replace = manager.should_replace(current, best_candidate)
        if should_replace and current is not None and min_improvement > 0:
            try:
                should_replace = best_candidate.score > (float(current.score) + min_improvement)
            except (TypeError, ValueError, AttributeError):
                # If current record can't be parsed, fall back to manager decision.
                should_replace = True

        if should_replace:
            # Comparability guardrails ("äpplen och päron"):
            # - Fail-fast only when BOTH score_version values are known and differ.
            # - Warn-only for execution_mode / fees / git_hash / seed / HTF status drift.
            candidate_score_version = _extract_score_version_from_result_payload(best_result)
            current_score_version = _extract_score_version_from_champion_record(current)
            _enforce_score_version_compatibility(
                current_score_version=current_score_version,
                candidate_score_version=candidate_score_version,
                context=f"promotion:{symbol}:{timeframe}",
            )

            if current is not None and (
                current_score_version is None or candidate_score_version is None
            ):
                print(
                    "[WARN] [Comparable] score_version saknas för jämförelse "
                    f"(current={current_score_version!r}, candidate={candidate_score_version!r})"
                )

            current_info = _load_backtest_info_from_results_path(
                _extract_results_path_from_champion_record(current)
            )
            candidate_info = _load_backtest_info_from_results_path(
                _coerce_optional_str(best_result.get("results_path") if best_result else None)
            )
            drift_warnings = _collect_comparability_warnings(current_info, candidate_info)
            if drift_warnings:
                preview = "; ".join(drift_warnings[:6])
                suffix = "; ..." if len(drift_warnings) > 6 else ""
                print(f"[WARN] [Comparable] drift detected: {preview}{suffix}")

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

    if best_candidate is not None and not promotion_enabled:
        print(f"[Champion] Promotion avstängd via config ({symbol} {timeframe})")

    # Return explore results plus (optional) validation results for reporting.
    if validation_results is not None:
        results.extend(validation_results)

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
