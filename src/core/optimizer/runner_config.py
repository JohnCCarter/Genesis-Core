from __future__ import annotations

import copy
import hashlib
import json
import logging
import os
import shutil
import subprocess
import tempfile
import threading
import time
from collections import OrderedDict
from collections.abc import Callable, Iterable
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

from core.optimizer.param_transforms import transform_parameters
from core.utils.dict_merge import deep_merge_dicts
from core.utils.diffing.canonical import canonicalize_config
from core.utils.optuna_helpers import param_signature

PROJECT_ROOT = Path(__file__).resolve().parents[3]
logger = logging.getLogger(__name__)

_TRIAL_KEY_CACHE: dict[int, str] = {}
_TRIAL_KEY_CACHE_LOCK = threading.Lock()

_DEFAULT_CONFIG_CACHE: dict[str, Any] | None = None
_DEFAULT_CONFIG_RUNTIME_VERSION: int | None = None
_DEFAULT_CONFIG_LOCK = threading.Lock()

_BACKTEST_DEFAULTS_CACHE: dict[str, Any] | None = None
_BACKTEST_DEFAULTS_LOCK = threading.Lock()

_JSON_CACHE: OrderedDict[str, tuple[int, Any]] = OrderedDict()
try:
    _JSON_CACHE_MAX = int(os.environ.get("GENESIS_OPTIMIZER_JSON_CACHE_SIZE", "256"))
except Exception:
    _JSON_CACHE_MAX = 256


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


@dataclass(slots=True)
class TrialIdentity:
    trial_id: str
    key: str
    fingerprint_digest: str
    optuna_param_sig: str


@dataclass(slots=True)
class TrialArtifacts:
    output_dir: Path
    trial_file: Path
    log_file: Path
    config_file: Path | None


@dataclass(slots=True)
class PreparedTrialConfig:
    config_file: Path | None
    derived_values: dict[str, Any]


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
    if callable(iso):
        return iso()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


def _load_json_with_retries(path: Path, retries: int = 3, delay: float = 0.1) -> Any:
    """Read JSON from disk with small retry loop; salvage on trailing garbage."""

    last_error: json.JSONDecodeError | None = None
    for attempt in range(retries):
        text = path.read_text(encoding="utf-8")
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:  # pragma: no cover - IO race eller korrupt fil
            last_error = exc
            if "Extra data" in str(exc):
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
                            print(
                                f"[WARN] Salvaged partial JSON från {path.name} (trailing data borttagen)"
                            )
                            return salvaged
                        except json.JSONDecodeError:
                            pass
            if attempt + 1 < retries:
                time.sleep(delay)
            else:
                raise
    raise last_error  # pragma: no cover


def _read_json_cached(
    path: Path,
    *,
    load_json_with_retries_fn: Callable[[Path, int, float], Any] | None = None,
    json_cache: OrderedDict[str, tuple[int, Any]] | None = None,
    json_cache_max: int | None = None,
) -> Any:
    """Read JSON with optional mtime-based in-memory cache."""

    use_cache = (os.environ.get("GENESIS_OPTIMIZER_JSON_CACHE") or "").strip().lower() in {
        "1",
        "true",
    }
    loader = load_json_with_retries_fn or _load_json_with_retries
    cache = json_cache if json_cache is not None else _JSON_CACHE
    cache_max = _JSON_CACHE_MAX if json_cache_max is None else json_cache_max

    if not use_cache:
        return loader(path, 3, 0.1)

    key = str(path.resolve())
    try:
        mtime = path.stat().st_mtime_ns
    except OSError:
        return json.loads(path.read_text(encoding="utf-8"))

    cached = cache.get(key)
    if cached is not None:
        cached_mtime, cached_obj = cached
        if cached_mtime == mtime:
            try:
                cache.move_to_end(key)
            except Exception:  # nosec B110
                pass
            return cached_obj

    obj = loader(path, 3, 0.1)
    cache[key] = (mtime, obj)
    try:
        while len(cache) > cache_max:
            cache.popitem(last=False)
    except Exception:
        if len(cache) > cache_max:
            cache.pop(next(iter(cache)))
    return obj


def _atomic_write_text(path: Path, payload: str, *, encoding: str = "utf-8") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding=encoding, delete=False, dir=path.parent) as tmp:
        tmp.write(payload)
    Path(tmp.name).replace(path)


def load_search_config(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:
        raise ValueError(f"Kunde inte läsa config-filen: {path} ({exc})") from exc
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError("search config måste vara YAML-mapp")
    return data


def _trial_key(
    params: dict[str, Any],
    *,
    trial_key_cache: dict[int, str] | None = None,
    trial_key_cache_lock: threading.Lock | None = None,
) -> str:
    """Generate canonical key for trial parameters with caching."""

    try:
        key = json.dumps(params, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    except (TypeError, ValueError):
        canonical = canonicalize_config(params or {})
        key = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()

    cache = trial_key_cache if trial_key_cache is not None else _TRIAL_KEY_CACHE
    lock = trial_key_cache_lock if trial_key_cache_lock is not None else _TRIAL_KEY_CACHE_LOCK
    with lock:
        cached = cache.get(digest)
        if cached is not None:
            return cached
        if len(cache) > 10000:
            items = list(cache.items())
            cache.clear()
            cache.update(items[-8000:])
        cache[digest] = digest
        return digest


def _get_default_config(
    *,
    default_config_cache: dict[str, Any] | None = None,
    default_config_lock: threading.Lock | None = None,
    set_default_config_state_fn: Callable[[dict[str, Any], int | None], None] | None = None,
) -> dict[str, Any]:
    global _DEFAULT_CONFIG_CACHE
    global _DEFAULT_CONFIG_RUNTIME_VERSION

    lock = default_config_lock or _DEFAULT_CONFIG_LOCK
    with lock:
        current_cache = (
            _DEFAULT_CONFIG_CACHE if set_default_config_state_fn is None else default_config_cache
        )
        if current_cache is None:
            from core.config.authority import ConfigAuthority

            authority = ConfigAuthority()
            default_cfg_obj, _, runtime_version = authority.get()
            loaded = default_cfg_obj.model_dump()
            if set_default_config_state_fn is None:
                _DEFAULT_CONFIG_CACHE = loaded
                _DEFAULT_CONFIG_RUNTIME_VERSION = runtime_version
            else:
                set_default_config_state_fn(loaded, runtime_version)
            return loaded
        return current_cache


def _get_default_runtime_version() -> int | None:
    _ = _get_default_config()
    return _DEFAULT_CONFIG_RUNTIME_VERSION


def _get_backtest_defaults(
    *,
    backtest_defaults_cache: dict[str, Any] | None = None,
    backtest_defaults_lock: threading.Lock | None = None,
    set_backtest_defaults_state_fn: Callable[[dict[str, Any]], None] | None = None,
    project_root: Path | None = None,
) -> dict[str, Any]:
    global _BACKTEST_DEFAULTS_CACHE

    lock = backtest_defaults_lock or _BACKTEST_DEFAULTS_LOCK
    repo_root = project_root or PROJECT_ROOT
    with lock:
        current_cache = (
            _BACKTEST_DEFAULTS_CACHE
            if set_backtest_defaults_state_fn is None
            else backtest_defaults_cache
        )
        if current_cache is None:
            path = repo_root / "config" / "backtest_defaults.yaml"
            if not path.exists():
                loaded = {}
                if set_backtest_defaults_state_fn is None:
                    _BACKTEST_DEFAULTS_CACHE = loaded
                else:
                    set_backtest_defaults_state_fn(loaded)
                return loaded
            try:
                raw = yaml.safe_load(path.read_text(encoding="utf-8"))
                loaded = raw if isinstance(raw, dict) else {}
            except Exception:
                loaded = {}
            if set_backtest_defaults_state_fn is None:
                _BACKTEST_DEFAULTS_CACHE = loaded
            else:
                set_backtest_defaults_state_fn(loaded)
            return loaded
        return current_cache


def _get_backtest_economics() -> tuple[float, float, float]:
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


def _resolve_sample_range(
    snapshot_id: str,
    runs_cfg: dict[str, Any],
    *,
    derive_dates_fn: Callable[[str], tuple[str, str]] | None = None,
    validate_date_range_fn: Callable[[str, str], None] | None = None,
    normalize_date_fn: Callable[[Any, str], str] | None = None,
) -> tuple[str, str]:
    start_raw = runs_cfg.get("sample_start")
    end_raw = runs_cfg.get("sample_end")
    derive_dates = derive_dates_fn or _derive_dates
    validate_date_range = validate_date_range_fn or _validate_date_range
    normalize_date = normalize_date_fn or _normalize_date

    if start_raw is None and end_raw is None:
        start, end = derive_dates(snapshot_id)
        validate_date_range(start, end)
        return start, end
    if start_raw is None or end_raw is None:
        raise ValueError("Både sample_start och sample_end måste anges om någon av dem är satt")
    start = normalize_date(start_raw, "sample_start")
    end = normalize_date(end_raw, "sample_end")
    validate_date_range(
        start,
        end,
        message="sample_start måste vara mindre än eller lika med sample_end",
    )
    return start, end


def _load_existing_trials(
    run_dir: Path,
    *,
    trial_key_fn: Callable[[dict[str, Any]], str] | None = None,
) -> dict[str, dict[str, Any]]:
    trial_paths = sorted(run_dir.glob("trial_*.json"))
    if not trial_paths:
        return {}

    key_fn = trial_key_fn or _trial_key
    existing: dict[str, dict[str, Any]] = {}
    for trial_path in trial_paths:
        try:
            content = trial_path.read_text(encoding="utf-8")
            trial_data = json.loads(content)
            if not isinstance(trial_data, dict):
                continue
            params = trial_data.get("parameters")
            if params:
                key = key_fn(params)
                existing[key] = trial_data
        except (ValueError, OSError) as exc:
            logger.warning("Skipping unreadable trial artifact %s: %s", trial_path.name, exc)
            continue
    return existing


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


def _ensure_run_metadata(
    run_dir: Path,
    config_path: Path,
    meta: dict[str, Any],
    run_id: str,
    *,
    resolve_score_version_fn: Callable[[], str],
    atomic_write_text_fn: Callable[[Path, str], None] | None = None,
    serialize_meta_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
    project_root: Path | None = None,
) -> None:
    meta_path = run_dir / "run_meta.json"
    repo_root = project_root or PROJECT_ROOT
    write_text = atomic_write_text_fn or _atomic_write_text
    serialize_meta = serialize_meta_fn or _serialize_meta

    try:
        config_rel = str(config_path.relative_to(repo_root))
    except ValueError:
        config_rel = str(config_path)

    expected_score_version = resolve_score_version_fn()

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
        for key, exp in expected.items():
            if exp is None:
                continue
            cur = existing.get(key)
            if cur is None or cur == "":
                continue
            if str(cur) != str(exp):
                mismatches.append(f"{key} existing={cur!r} expected={exp!r}")

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

        did_change = False
        for key, exp in expected.items():
            if exp is None:
                continue
            if existing.get(key) is None or existing.get(key) == "":
                existing[key] = exp
                did_change = True
        existing.setdefault("raw_meta", meta)
        if did_change:
            existing["updated_at"] = datetime.now(UTC).isoformat()
            write_text(meta_path, json.dumps(serialize_meta(existing), indent=2))
        return

    commit = "unknown"
    git_executable = shutil.which("git")
    if git_executable:
        try:
            completed = subprocess.run(  # nosec B603
                [git_executable, "rev-parse", "HEAD"],
                cwd=repo_root,
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
    write_text(meta_path, json.dumps(serialize_meta(meta_payload), indent=2))


def _deep_merge(base: dict, override: dict) -> dict:
    return deep_merge_dicts(base, override)


def _expand_value(node: Any) -> list[Any]:
    def _clone_value(value: Any) -> Any:
        value_type = type(value)
        if value_type in (int, float, str, bool, type(None), bytes):
            return value
        if value_type is tuple:
            return tuple(_clone_value(x) for x in value)
        if value_type is list:
            return [_clone_value(x) for x in value]
        if value_type is dict:
            return {k: _clone_value(val) for k, val in value.items()}
        return copy.deepcopy(value)

    if isinstance(node, dict):
        node_type = node.get("type")
        if node_type == "grid":
            values = node.get("values") or []
            return [_clone_value(v) for v in values]
        if node_type == "fixed":
            return [_clone_value(node.get("value"))]
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
    def _count_choices(node: dict[str, Any], prefix: str = "") -> dict[str, int]:
        counts = {}
        for key, value in (node or {}).items():
            path = f"{prefix}.{key}" if prefix else key
            if value is None:
                continue
            if isinstance(value, dict) and "type" not in value:
                counts.update(_count_choices(value, path))
                continue
            if not isinstance(value, dict):
                counts[path] = 1
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
                    counts[path] = int((high - low) / float(step)) + 1
                else:
                    counts[path] = -1
            elif node_type == "loguniform":
                counts[path] = -1
        return counts

    param_counts = _count_choices(spec)
    discrete_params = {k: v for k, v in param_counts.items() if v > 0}
    continuous_params = {k: v for k, v in param_counts.items() if v < 0}

    total_combinations = 1
    for count in discrete_params.values():
        total_combinations *= count

    issues = []
    if total_combinations < 10 and not continuous_params:
        issues.append("Search space very small (<10 combinations)")

    narrow_params = [k for k, v in discrete_params.items() if v <= 2]
    if discrete_params and len(narrow_params) > len(discrete_params) * 0.7:
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

    import re

    date_tokens: list[str] = []
    for part in parts:
        token = part.strip()
        if not token:
            continue
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", token) or re.fullmatch(r"\d{8}", token):
            date_tokens.append(token)

    if len(date_tokens) >= 2:
        return date_tokens[-2], date_tokens[-1]

    return parts[2], parts[3]


def prepare_trial_identity(
    trial: TrialConfig,
    *,
    index: int,
    trial_key_fn: Callable[[dict[str, Any]], str] | None = None,
    param_signature_fn: Callable[[dict[str, Any]], str] | None = None,
) -> TrialIdentity:
    key_fn = trial_key_fn or _trial_key
    signature_fn = param_signature_fn or param_signature

    key = key_fn(trial.parameters)
    fingerprint_digest = key
    try:
        optuna_param_sig = signature_fn(trial.parameters)
    except Exception:
        optuna_param_sig = fingerprint_digest

    return TrialIdentity(
        trial_id=f"trial_{index:03d}",
        key=key,
        fingerprint_digest=fingerprint_digest,
        optuna_param_sig=optuna_param_sig,
    )


def prepare_trial_artifacts(
    run_dir: Path, *, trial_id: str, has_parameters: bool
) -> TrialArtifacts:
    output_dir = run_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    config_file = output_dir / f"{trial_id}_config.json" if has_parameters else None
    return TrialArtifacts(
        output_dir=output_dir,
        trial_file=output_dir / f"{trial_id}.json",
        log_file=output_dir / f"{trial_id}.log",
        config_file=config_file,
    )


def prepare_trial_config_payload(
    trial: TrialConfig,
    *,
    run_id: str,
    score_version: str,
    identity: TrialIdentity,
    artifacts: TrialArtifacts,
    capital_default: float,
    commission_default: float,
    slippage_default: float,
    json_dumps_fn: Callable[[Any], str],
    get_default_config_fn: Callable[[], dict[str, Any]] | None = None,
    get_default_runtime_version_fn: Callable[[], int | None] | None = None,
    deep_merge_fn: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]] | None = None,
    transform_parameters_fn: (
        Callable[[dict[str, Any]], tuple[dict[str, Any], dict[str, Any]]] | None
    ) = None,
    atomic_write_text_fn: Callable[[Path, str], None] | None = None,
) -> PreparedTrialConfig:
    if not trial.parameters or artifacts.config_file is None:
        return PreparedTrialConfig(config_file=None, derived_values={})

    get_default_config = get_default_config_fn or _get_default_config
    get_default_runtime_version = get_default_runtime_version_fn or _get_default_runtime_version
    deep_merge = deep_merge_fn or _deep_merge
    transform = transform_parameters_fn or transform_parameters
    write_text = atomic_write_text_fn or _atomic_write_text

    default_cfg = get_default_config()
    transformed_params, derived_values = transform(trial.parameters)
    merged_cfg = deep_merge(default_cfg, transformed_params)

    meta = dict(merged_cfg.get("meta") or {})
    meta["skip_champion_merge"] = True
    merged_cfg["meta"] = meta

    config_payload = {
        "cfg": merged_cfg,
        "merged_config": merged_cfg,
        "runtime_version": get_default_runtime_version(),
        "run_id": run_id,
        "trial_id": identity.trial_id,
        "parameters": trial.parameters,
        "trial_key": identity.fingerprint_digest,
        "param_signature": identity.optuna_param_sig,
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

    write_text(artifacts.config_file, json_dumps_fn(config_payload))
    return PreparedTrialConfig(config_file=artifacts.config_file, derived_values=derived_values)


def materialize_cached_trial_payload(
    cached_payload: dict[str, Any],
    *,
    identity: TrialIdentity,
    parameters: dict[str, Any],
    config_file: Path | None,
) -> dict[str, Any]:
    payload = dict(cached_payload)
    payload.update(
        {
            "trial_id": identity.trial_id,
            "parameters": parameters,
            "from_cache": True,
        }
    )
    if config_file is not None:
        payload.setdefault("config_path", config_file.name)
    if not payload.get("parameters"):
        payload["parameters"] = parameters
    return payload


def prepare_cache_snapshot(
    final_payload: dict[str, Any], *, parameters: dict[str, Any]
) -> dict[str, Any]:
    cache_snapshot = dict(final_payload)
    cache_snapshot.pop("trial_id", None)
    cache_snapshot.pop("from_cache", None)
    cache_snapshot["parameters"] = parameters
    return cache_snapshot
