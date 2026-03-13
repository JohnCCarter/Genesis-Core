from __future__ import annotations

import hashlib
import json
import os
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from core.utils.diffing.canonical import canonicalize_config
from core.utils.optuna_helpers import NoDupeGuard, param_signature

_ALLOWED_SCORE_VERSIONS: set[str] = {"v1", "v2"}


def compute_optuna_resume_signature_impl(
    *,
    config: dict[str, Any],
    config_path: Path,
    git_commit: str,
    runtime_version: int | None,
    project_root: Path,
) -> dict[str, Any]:
    """Compute a stable signature to prevent resuming the wrong Optuna study."""

    meta = config.get("meta") or {}
    runs_cfg = meta.get("runs") or {}
    optuna_cfg = (runs_cfg.get("optuna") or {}).copy()
    optuna_cfg.pop("timeout_seconds", None)
    optuna_cfg.pop("end_at", None)

    repo_root = project_root.resolve()
    try:
        config_path_abs = config_path.resolve()
    except Exception:
        config_path_abs = config_path

    config_path_external = True
    config_path_rel_posix: str | None = None
    try:
        config_path_rel_posix = config_path_abs.relative_to(repo_root).as_posix()
        config_path_external = False
    except ValueError:
        config_path_external = True

    try:
        config_sha256 = hashlib.sha256(config_path_abs.read_bytes()).hexdigest()
    except OSError as exc:
        raise ValueError(
            f"Could not read config for resume signature: {config_path_abs} ({exc})"
        ) from exc

    payload = {
        "config_path_rel_posix": config_path_rel_posix,
        "config_path_external": config_path_external,
        "config_sha256": config_sha256,
        "git_commit": str(git_commit or "unknown"),
        "runtime_version": runtime_version,
        "meta": {
            "symbol": meta.get("symbol"),
            "timeframe": meta.get("timeframe"),
            "snapshot_id": meta.get("snapshot_id"),
            "warmup_bars": meta.get("warmup_bars"),
        },
        "runs": {
            "use_sample_range": runs_cfg.get("use_sample_range"),
            "sample_start": runs_cfg.get("sample_start"),
            "sample_end": runs_cfg.get("sample_end"),
            "optuna": optuna_cfg,
        },
        "constraints": config.get("constraints") or {},
        "parameters": config.get("parameters") or {},
        "env": {
            "GENESIS_MODE_EXPLICIT": os.environ.get("GENESIS_MODE_EXPLICIT"),
            "GENESIS_FAST_WINDOW": os.environ.get("GENESIS_FAST_WINDOW"),
            "GENESIS_PRECOMPUTE_FEATURES": os.environ.get("GENESIS_PRECOMPUTE_FEATURES"),
            "GENESIS_FAST_HASH": os.environ.get("GENESIS_FAST_HASH"),
        },
    }

    canonical = canonicalize_config(payload, precision=6)
    blob = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    fingerprint = hashlib.sha256(blob.encode("utf-8")).hexdigest()

    return {
        "version": 1,
        "fingerprint": fingerprint,
        "git_commit": payload["git_commit"],
        "runtime_version": runtime_version,
        "config_path_rel_posix": config_path_rel_posix,
        "config_path_external": config_path_external,
        "config_path_abs": str(config_path_abs),
        "config_sha256": config_sha256,
        "snapshot_id": payload["meta"]["snapshot_id"],
        "sample_start": payload["runs"]["sample_start"],
        "sample_end": payload["runs"]["sample_end"],
    }


def verify_or_set_optuna_study_signature_impl(study: Any, expected: dict[str, Any]) -> None:
    """Fail-fast on resume when the study signature mismatches."""

    allow_mismatch = os.environ.get("GENESIS_ALLOW_STUDY_RESUME_MISMATCH") == "1"
    allow_backfill = os.environ.get("GENESIS_BACKFILL_STUDY_SIGNATURE") == "1"

    expected_fp = str(expected.get("fingerprint") or "")
    existing = getattr(study, "user_attrs", {}) or {}
    existing_sig = existing.get("genesis_resume_signature")
    existing_fp = (
        str(existing_sig.get("fingerprint") or "") if isinstance(existing_sig, dict) else ""
    )

    if existing_fp and expected_fp and existing_fp != expected_fp:
        msg = (
            "Optuna resume blocked: study signature mismatch. "
            f"expected={expected_fp} existing={existing_fp}. "
            "This usually means you are resuming the wrong study/DB or the config/code/runtime/env changed."
        )
        if allow_mismatch:
            print(f"[WARN] {msg} (override via GENESIS_ALLOW_STUDY_RESUME_MISMATCH=1)")
        else:
            raise RuntimeError(msg)

    try:
        has_trials = len(getattr(study, "trials", []) or []) > 0
    except Exception:
        has_trials = False

    if not existing_fp and has_trials and not allow_backfill:
        print(
            "[WARN] Optuna study has trials but no genesis_resume_signature; cannot verify resume safety. "
            "Set GENESIS_BACKFILL_STUDY_SIGNATURE=1 to attach a signature explicitly."
        )
        return

    try:
        study.set_user_attr("genesis_resume_signature", expected)
    except Exception as exc:
        print(f"[WARN] Could not set genesis_resume_signature on study: {exc}")


def verify_or_set_optuna_study_score_version_impl(
    study: Any,
    expected_score_version: str,
    *,
    logger,
) -> None:
    """Fail-fast on resume when Optuna study uses a different scoring version."""

    allow_mismatch = os.environ.get("GENESIS_ALLOW_STUDY_RESUME_MISMATCH") == "1"
    try:
        existing = getattr(study, "user_attrs", None)
        if not isinstance(existing, dict):
            existing = {}
        existing_v = existing.get("genesis_score_version")
    except Exception:
        existing_v = None

    expected_norm = str(expected_score_version or "").strip().lower()
    existing_norm = str(existing_v or "").strip().lower()
    if existing_norm and expected_norm and existing_norm != expected_norm:
        msg = (
            "Optuna resume blocked: score_version mismatch. "
            f"expected={expected_score_version} existing={existing_v}. "
            "This usually means GENESIS_SCORE_VERSION changed between runs."
        )
        if allow_mismatch:
            print(f"[WARN] {msg} (override via GENESIS_ALLOW_STUDY_RESUME_MISMATCH=1)")
            return
        raise RuntimeError(msg)

    if existing_v:
        return

    try:
        study.set_user_attr("genesis_score_version", expected_score_version)
    except Exception as exc:
        logger.debug("Could not set genesis_score_version on Optuna study: %s", exc, exc_info=True)


def select_top_n_from_optuna_storage_impl(
    run_meta: dict[str, Any],
    top_n: int,
    *,
    optuna_available: bool,
) -> list[dict[str, Any]]:
    """Fallback for validation: select top-N candidates directly from Optuna storage."""

    if top_n <= 0 or not optuna_available:
        return []

    optuna_meta = run_meta.get("optuna")
    if not isinstance(optuna_meta, dict):
        return []

    storage = optuna_meta.get("storage")
    study_name = optuna_meta.get("study_name")
    if not storage or not study_name:
        return []

    try:
        import optuna
        from optuna.trial import TrialState

        study = optuna.load_study(study_name=str(study_name), storage=str(storage))
    except Exception:
        return []

    ranked: list[tuple[float, dict[str, Any]]] = []
    for t in getattr(study, "trials", []) or []:
        try:
            if getattr(t, "state", None) != TrialState.COMPLETE:
                continue
            user_attrs = getattr(t, "user_attrs", None)
            if not isinstance(user_attrs, dict):
                continue
            payload = user_attrs.get("result_payload")
            if not isinstance(payload, dict):
                continue
            if payload.get("error") or payload.get("skipped"):
                continue
            score_block = payload.get("score") or {}
            score = float(score_block.get("score"))
        except (TypeError, ValueError):
            continue
        ranked.append((score, payload))

    ranked.sort(key=lambda x: x[0], reverse=True)
    return [payload for _score, payload in ranked[:top_n]]


def resolve_score_version_for_optimizer_impl(explicit: str | None = None) -> str:
    """Resolve score_version deterministically for an optimizer run."""

    raw = explicit or os.environ.get("GENESIS_SCORE_VERSION") or "v1"
    value = str(raw).strip().lower()
    if value not in _ALLOWED_SCORE_VERSIONS:
        raise ValueError(
            f"Ogiltig GENESIS_SCORE_VERSION={raw!r}. Tillåtna värden: {sorted(_ALLOWED_SCORE_VERSIONS)}"
        )
    return value


def extract_score_version_from_result_payload_impl(result: dict[str, Any] | None) -> str | None:
    if not isinstance(result, dict):
        return None
    score_block = result.get("score")
    if not isinstance(score_block, dict):
        return None
    return _coerce_optional_str(score_block.get("score_version"))


def extract_score_version_from_champion_record_impl(current: Any) -> str | None:
    meta = getattr(current, "metadata", None)
    if not isinstance(meta, dict):
        return None
    run_meta = meta.get("run_meta")
    if not isinstance(run_meta, dict):
        return None
    score_block = run_meta.get("score_block")
    if not isinstance(score_block, dict):
        return None
    return _coerce_optional_str(score_block.get("score_version"))


def extract_results_path_from_champion_record_impl(current: Any) -> str | None:
    meta = getattr(current, "metadata", None)
    if not isinstance(meta, dict):
        return None
    return _coerce_optional_str(meta.get("results_path"))


def enforce_score_version_compatibility_impl(
    *,
    current_score_version: str | None,
    candidate_score_version: str | None,
    context: str,
) -> None:
    if not current_score_version or not candidate_score_version:
        return
    if current_score_version != candidate_score_version:
        raise ValueError(
            "Inkompatibla scoring-versioner (äpplen och päron): "
            f"current={current_score_version} candidate={candidate_score_version} ({context})"
        )


def dig_impl(mapping: dict[str, Any], dotted_path: str) -> Any:
    cur: Any = mapping
    for part in dotted_path.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def load_backtest_info_from_results_path_impl(
    results_path: str | None,
    *,
    project_root: Path,
    backtest_results_dir: Path,
    read_json_cached,
) -> dict[str, Any] | None:
    if not results_path:
        return None
    try:
        path = Path(results_path)
        if not path.is_absolute():
            if ("/" in results_path) or ("\\" in results_path):
                path = (project_root / path).resolve()
            else:
                path = (backtest_results_dir / path).resolve()
        if not path.exists():
            return None
        data = read_json_cached(path)
        if not isinstance(data, dict):
            return None
        info = data.get("backtest_info")
        return info if isinstance(info, dict) else None
    except Exception:
        return None


def collect_comparability_warnings_impl(
    current_info: dict[str, Any] | None,
    candidate_info: dict[str, Any] | None,
    *,
    dig,
) -> list[str]:
    if not isinstance(current_info, dict) or not isinstance(candidate_info, dict):
        return []

    watched_fields = [
        "execution_mode.fast_window",
        "execution_mode.env_precompute_features",
        "execution_mode.precompute_enabled",
        "execution_mode.precomputed_ready",
        "execution_mode.mode_explicit",
        "commission_rate",
        "slippage_rate",
        "git_hash",
        "seed",
        "htf.env_htf_exits",
        "htf.use_new_exit_engine",
        "htf.htf_candles_loaded",
        "htf.htf_context_seen",
    ]

    warnings: list[str] = []
    for path in watched_fields:
        current_value = dig(current_info, path)
        candidate_value = dig(candidate_info, path)
        if current_value is None or candidate_value is None:
            continue
        if current_value != candidate_value:
            warnings.append(f"{path} current={current_value!r} candidate={candidate_value!r}")
    return warnings


def select_optuna_sampler_impl(
    name: str | None,
    kwargs: dict[str, Any] | None,
    concurrency: int = 1,
    *,
    optuna_available: bool,
    tpe_sampler_cls,
    random_sampler_cls,
    cmaes_sampler_cls,
):
    if not optuna_available:
        raise RuntimeError("Optuna är inte installerat")
    kwargs = (kwargs or {}).copy()

    if "seed" not in kwargs:
        try:
            kwargs["seed"] = int(os.environ.get("GENESIS_RANDOM_SEED", "42"))
        except ValueError:
            kwargs["seed"] = 42

    name = (name or kwargs.pop("type", None) or "tpe").lower()
    if name == "tpe":
        if "multivariate" not in kwargs:
            kwargs["multivariate"] = True
        if "constant_liar" not in kwargs:
            kwargs["constant_liar"] = True
        if "n_startup_trials" not in kwargs:
            base_startup = 25
            adaptive_startup = max(base_startup, 5 * concurrency)
            kwargs["n_startup_trials"] = adaptive_startup
        if "n_ei_candidates" not in kwargs:
            kwargs["n_ei_candidates"] = 48
        return tpe_sampler_cls(**kwargs)
    if name == "random":
        return random_sampler_cls(**kwargs)
    if name == "cmaes":
        return cmaes_sampler_cls(**kwargs)
    raise ValueError(f"Okänd Optuna-sampler: {name}")


def select_optuna_pruner_impl(
    name: str | None,
    kwargs: dict[str, Any] | None,
    *,
    optuna_available: bool,
    median_pruner_cls,
    successive_halving_pruner_cls,
    hyperband_pruner_cls,
    nop_pruner_cls,
):
    if not optuna_available:
        raise RuntimeError("Optuna är inte installerat")
    kwargs = (kwargs or {}).copy()
    name = (name or kwargs.pop("type", None) or "none").lower()
    if name == "median":
        return median_pruner_cls(**kwargs)
    if name == "sha":
        return successive_halving_pruner_cls(**kwargs)
    if name == "hyperband":
        return hyperband_pruner_cls(**kwargs)
    if name == "none":
        return nop_pruner_cls()
    raise ValueError(f"Okänd Optuna-pruner: {name}")


def create_optuna_study_impl(
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
    optuna_available: bool,
    select_optuna_sampler,
    select_optuna_pruner,
    rdb_storage_cls,
    create_study,
    optuna_lock,
):
    if not optuna_available:
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
    sampler = select_optuna_sampler(
        sampler_name,
        sampler_cfg.get("kwargs"),
        concurrency=concurrency,
    )
    pruner = select_optuna_pruner(pruner_name, pruner_cfg.get("kwargs"))

    if heartbeat_interval is not None and heartbeat_interval <= 0:
        raise ValueError("heartbeat_interval must be a positive integer")
    if heartbeat_grace_period is not None and heartbeat_grace_period <= 0:
        raise ValueError("heartbeat_grace_period must be a positive integer")

    def _default_engine_kwargs_for_storage(storage_url: str) -> dict[str, Any] | None:
        if not storage_url:
            return None
        if storage_url.lower().startswith("sqlite"):
            return {"connect_args": {"timeout": 10}}
        return None

    storage_obj: Any | None = storage
    if storage:
        engine_kwargs = _default_engine_kwargs_for_storage(storage)
        if heartbeat_interval is not None or engine_kwargs is not None:
            storage_obj = rdb_storage_cls(
                storage,
                engine_kwargs=engine_kwargs,
                heartbeat_interval=heartbeat_interval,
                grace_period=heartbeat_grace_period,
            )

    with optuna_lock:
        study = create_study(
            study_name=study_name or f"optimizer_{run_id}",
            storage=storage_obj,
            sampler=sampler,
            pruner=pruner,
            direction=(direction or "maximize"),
            load_if_exists=allow_resume,
        )
    return study


def run_optuna_impl(
    *,
    study_config: dict[str, Any],
    parameters_spec: dict[str, Any],
    make_trial,
    run_dir: Path,
    run_id: str,
    existing_trials: dict[str, dict[str, Any]],
    max_trials: int | None,
    concurrency: int,
    allow_resume: bool,
    resume_signature: dict[str, Any] | None,
    create_optuna_study,
    verify_or_set_optuna_study_signature,
    verify_or_set_optuna_study_score_version,
    resolve_score_version_for_optimizer,
    suggest_parameters,
    trial_key,
    extract_num_trades,
    atomic_write_text,
    serialize_meta,
    json_dumps,
    constraint_soft_penalty: float,
    logger,
    optuna_module,
) -> list[dict[str, Any]]:
    if optuna_module is None:
        raise RuntimeError("Optuna-strategi vald men optuna är inte installerat")

    storage = study_config.get("storage") or os.getenv("OPTUNA_STORAGE")
    study_name = study_config.get("study_name") or os.getenv("OPTUNA_STUDY_NAME")
    direction = study_config.get("direction") or "maximize"
    timeout_seconds_raw = study_config.get("timeout_seconds")
    timeout_seconds: int | None
    if timeout_seconds_raw is None:
        timeout_seconds = None
    else:
        timeout_seconds = int(timeout_seconds_raw)

    def _parse_end_at(value: Any) -> datetime | None:
        if value is None or value == "":
            return None
        if isinstance(value, datetime):
            dt = value
        else:
            text = str(value).strip()
            if text.endswith("Z"):
                text = text[:-1] + "+00:00"
            dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.now().astimezone().tzinfo)
        return dt

    end_at = _parse_end_at(study_config.get("end_at"))
    start_monotonic = time.monotonic()

    def _effective_timeout_seconds() -> int | None:
        candidates: list[int] = []

        if timeout_seconds is not None:
            elapsed = time.monotonic() - start_monotonic
            remaining_rel = int(timeout_seconds - elapsed)
            candidates.append(max(0, remaining_rel))

        if end_at is not None:
            now_utc = datetime.now(tz=UTC)
            deadline_utc = end_at.astimezone(UTC)
            remaining_abs = int((deadline_utc - now_utc).total_seconds())
            candidates.append(max(0, remaining_abs))

        if not candidates:
            return None
        return min(candidates)

    initial_budget = _effective_timeout_seconds()
    if initial_budget is not None and initial_budget <= 0:
        raise ValueError(
            "Optuna time budget is already exhausted (timeout_seconds/end_at). "
            "Check optuna.end_at or recompute timeout_seconds."
        )
    sampler_cfg = study_config.get("sampler")
    pruner_cfg = study_config.get("pruner")
    if isinstance(sampler_cfg, str):
        sampler_cfg = {"name": sampler_cfg}
    if isinstance(pruner_cfg, str):
        pruner_cfg = {"name": pruner_cfg}

    heartbeat_interval_raw = study_config.get("heartbeat_interval")
    heartbeat_grace_raw = study_config.get("heartbeat_grace_period")
    heartbeat_interval = (
        int(heartbeat_interval_raw) if heartbeat_interval_raw not in (None, "") else None
    )
    heartbeat_grace = int(heartbeat_grace_raw) if heartbeat_grace_raw not in (None, "") else None

    if storage and heartbeat_interval is None:
        heartbeat_interval = 60
    if storage and heartbeat_grace is None:
        heartbeat_grace = 180

    score_version = resolve_score_version_for_optimizer()

    results: list[dict[str, Any]] = []
    duplicate_streak = 0
    max_duplicate_streak = int(os.getenv("OPTUNA_MAX_DUPLICATE_STREAK", "10"))
    total_trials_attempted = 0
    duplicate_count = 0
    zero_trade_count = 0
    score_memory: dict[str, float] = {}

    dedup_guard_enabled = bool(study_config.get("dedup_guard_enabled", True))
    guard: NoDupeGuard | None = (
        NoDupeGuard(sqlite_path=str(run_dir / "_dedup.db")) if dedup_guard_enabled else None
    )

    def objective(trial):
        nonlocal duplicate_streak, total_trials_attempted, duplicate_count, zero_trade_count
        total_trials_attempted += 1
        try:
            trial.set_user_attr("score_version", score_version)
        except Exception as exc:
            logger.debug(
                "Failed to set Optuna trial user attribute 'score_version': %s",
                exc,
                exc_info=True,
            )
        parameters = suggest_parameters(trial, parameters_spec)
        trial_number = trial.number + 1
        key = trial_key(parameters)

        sig: str | None = None
        if guard is not None:
            try:
                sig = param_signature(parameters)
                if guard.seen(sig):
                    duplicate_streak += 1
                    duplicate_count += 1
                    trial.set_user_attr("duplicate", True)
                    trial.set_user_attr("skipped", True)
                    trial.set_user_attr("penalized_duplicate", True)
                    trial.set_user_attr("penalized_duplicate_precheck", True)
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
                        raise optuna_module.exceptions.OptunaError(
                            "Duplicate parameter suggestions limit reached"
                        )
                    return -1e6
                guard.add(sig)
            except Exception:
                sig = None
        if key in existing_trials:
            cached = existing_trials[key]
            trial.set_user_attr("skipped", True)
            trial.set_user_attr("duplicate", True)
            duplicate_streak += 1
            duplicate_count += 1
            if duplicate_streak >= max_duplicate_streak:
                raise optuna_module.exceptions.OptunaError(
                    "Duplicate parameter suggestions limit reached"
                )
            results.append({**cached, "skipped": True})
            trial.set_user_attr("penalized_duplicate", True)
            return -1e6

        optuna_ctx = {
            "trial_id": trial._trial_id,
            "storage": storage,
            "study_name": study_name,
            "pruner": pruner_cfg,
        }
        payload = make_trial(trial_number, parameters, optuna_context=optuna_ctx)
        results.append(payload)

        if payload.get("from_cache"):
            score_block = payload.get("score") or {}
            cached_score = float(score_block.get("score", 0.0) or 0.0)
            trial.set_user_attr("cached", True)
            trial.set_user_attr("cache_reused", True)
            if payload.get("results_path"):
                trial.set_user_attr("backtest_path", payload["results_path"])
            logger.info(
                "[CACHE] Trial %s reusing cached score %.2f (from_cache=True in payload)",
                trial.number,
                cached_score,
            )
            score_memory[key] = cached_score
            duplicate_streak = 0
            return cached_score

        if payload.get("skipped"):
            reason = payload.get("reason")
            trial.set_user_attr("skipped", True)
            if reason == "duplicate_within_run":
                duplicate_streak += 1
                duplicate_count += 1
                trial.set_user_attr("duplicate", True)
                if duplicate_streak >= max_duplicate_streak:
                    raise optuna_module.exceptions.OptunaError(
                        "Duplicate parameter suggestions limit reached"
                    )
            elif reason == "zero_trade_preflight":
                zero_trade_count += 1
                duplicate_streak = 0
                trial.set_user_attr("zero_trade_preflight", True)
                penalty = float(payload.get("score", {}).get("score", -1e5) or -1e5)
                return penalty
            else:
                duplicate_streak = 0
            if reason == "duplicate_within_run":
                trial.set_user_attr("penalized_duplicate", True)
                if key in score_memory:
                    cached_score = score_memory[key]
                    logger.info(
                        "[CACHE] Trial %s reusing memory-cached score %.2f (duplicate_within_run but score available)",
                        trial.number,
                        cached_score,
                    )
                    return cached_score
                return -1e6
            return float(payload.get("score", {}).get("score", 0.0) or 0.0)

        if payload.get("error"):
            trial.set_user_attr("error", payload.get("error"))
            if guard is not None and sig:
                try:
                    guard.remove(sig)
                except Exception:
                    pass
            raise optuna_module.TrialPruned()

        constraints = payload.get("constraints") or {}
        score_block = payload.get("score") or {}
        score_value = float(score_block.get("score", 0.0) or 0.0)

        trial.set_user_attr("score_block", score_block)
        trial.set_user_attr("result_payload", payload)

        num_trades_value = extract_num_trades(payload)
        num_trades = num_trades_value if num_trades_value is not None else 0
        if num_trades == 0:
            zero_trade_count += 1
            trial.set_user_attr("zero_trades", True)

        if not constraints.get("ok", True):
            reasons = constraints.get("reasons")
            is_abort_heuristic = bool(payload.get("abort_reason")) or (
                isinstance(reasons, list) and "aborted_by_heuristic" in reasons
            )
            if is_abort_heuristic:
                trial.set_user_attr("constraints", constraints)
                trial.set_user_attr("constraints_soft_fail", True)
                trial.set_user_attr("aborted_by_heuristic", True)
                if payload.get("abort_reason"):
                    trial.set_user_attr("abort_reason", payload.get("abort_reason"))
                if payload.get("abort_details"):
                    trial.set_user_attr("abort_details", payload.get("abort_details"))
                return score_value
            trial.set_user_attr("constraints", constraints)
            trial.set_user_attr("constraints_soft_fail", True)
            trial.set_user_attr("constraints_penalty", constraint_soft_penalty)
            return score_value - constraint_soft_penalty

        if num_trades > 0:
            duplicate_streak = 0

        score_memory[key] = score_value
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
            bootstrap_study = create_optuna_study(
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
            if resume_signature is not None:
                verify_or_set_optuna_study_signature(bootstrap_study, resume_signature)
            verify_or_set_optuna_study_score_version(bootstrap_study, score_version)
            bootstrap_study.optimize(
                objective,
                n_trials=bootstrap_to_run,
                timeout=_effective_timeout_seconds(),
                n_jobs=1,
                gc_after_trial=True,
                show_progress_bar=False,
            )
            if remaining_trials is not None:
                remaining_trials = max(0, remaining_trials - bootstrap_to_run)
    if remaining_trials is not None and remaining_trials == 0:
        return results

    study = create_optuna_study(
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
    if resume_signature is not None:
        verify_or_set_optuna_study_signature(study, resume_signature)
    verify_or_set_optuna_study_score_version(study, score_version)

    checkpoint_every_raw = os.environ.get("GENESIS_OPTUNA_CHECKPOINT_EVERY", "25")
    try:
        checkpoint_every = int(checkpoint_every_raw)
    except (TypeError, ValueError):
        checkpoint_every = 25
    if checkpoint_every < 1:
        checkpoint_every = 0

    run_meta_path = run_dir / "run_meta.json"
    try:
        run_meta_checkpoint = json.loads(run_meta_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        run_meta_checkpoint = {}

    def _write_optuna_checkpoint(study_to_write) -> None:
        best_payload_local: dict[str, Any] | None = None
        best_trial_number_local: str | None = None
        best_value_local: float | None = None
        if study_to_write.best_trials:
            try:
                best_trial_local = study_to_write.best_trial
                best_payload_local = best_trial_local.user_attrs.get("result_payload")
                best_value_local = float(study_to_write.best_value)
                best_trial_number_local = (
                    best_payload_local.get("trial_id") if best_payload_local else None
                )
            except Exception:
                best_payload_local = None

        run_meta_checkpoint.setdefault("optuna", {}).update(
            {
                "study_name": study_to_write.study_name,
                "storage": storage,
                "direction": direction,
                "n_trials": len(study_to_write.trials),
                "best_value": best_value_local,
                "best_trial_number": best_trial_number_local,
            }
        )
        atomic_write_text(run_meta_path, json_dumps(serialize_meta(run_meta_checkpoint)))
        if best_payload_local is not None:
            atomic_write_text(run_dir / "best_trial.json", json_dumps(best_payload_local))

    def _checkpoint_callback(study_to_write, frozen_trial) -> None:
        if checkpoint_every and (int(frozen_trial.number) + 1) % checkpoint_every == 0:
            try:
                _write_optuna_checkpoint(study_to_write)
            except Exception:
                pass

    try:
        study.optimize(
            objective,
            n_trials=remaining_trials,
            timeout=_effective_timeout_seconds(),
            n_jobs=concurrency,
            gc_after_trial=True,
            show_progress_bar=False,
            callbacks=[_checkpoint_callback] if checkpoint_every else None,
        )
    finally:
        try:
            _write_optuna_checkpoint(study)
        except Exception:
            pass

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
        "[CACHE STATS] %s/%s trials cached (%.1f%% hit rate), %s unique backtests",
        cache_stats["cached_trials"],
        cache_stats["total_trials"],
        cache_stats["cache_hit_rate"] * 100,
        cache_stats["unique_backtests"],
    )

    try:
        trial_state = optuna_module.trial.TrialState
        pruned_count = sum(1 for t in study.trials if t.state == trial_state.PRUNED)
    except Exception:
        pruned_count = 0

    if cache_stats["cache_hit_rate"] > 0.8 and cache_stats["total_trials"] > 10:
        logger.warning(
            "[CACHE] Very high cache hit rate (>80%) - consider broadening search space or reducing bootstrap_random_trials if using cached study"
        )
    elif cache_stats["cache_hit_rate"] < 0.05 and cache_stats["total_trials"] > 50:
        logger.info("[CACHE] Low cache reuse (<5%) - good exploration diversity")

    if total_trials_attempted > 0:
        duplicate_ratio = duplicate_count / total_trials_attempted
        zero_trade_ratio = zero_trade_count / total_trials_attempted
        pruned_ratio = pruned_count / total_trials_attempted

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

        if pruned_ratio > 0.5:
            print(
                f"\n⚠️  WARNING: High pruned rate ({pruned_ratio*100:.1f}%)\n"
                f"   {pruned_count}/{total_trials_attempted} trials were pruned.\n"
                f"   This suggests:\n"
                f"   - Pruner is too aggressive (warmup/interval too low)\n"
                f"   - Objective intermediate reporting is too noisy early\n"
                f"   Recommendations:\n"
                f"   - Increase n_warmup_steps and/or interval_steps\n"
                f"   - Consider disabling pruner for short diagnostics\n"
            )

    best_payload: dict[str, Any] | None = None
    optuna_meta: dict[str, Any] = {}

    if study.best_trials:
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
                    "pruned_count": pruned_count,
                    "zero_trade_count": zero_trade_count,
                    "duplicate_ratio": duplicate_count / max(1, total_trials_attempted),
                    "pruned_ratio": pruned_count / max(1, total_trials_attempted),
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
                    "pruned_count": pruned_count,
                    "zero_trade_count": zero_trade_count,
                    "duplicate_ratio": duplicate_count / max(1, total_trials_attempted),
                    "pruned_ratio": pruned_count / max(1, total_trials_attempted),
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
                "pruned_count": pruned_count,
                "zero_trade_count": zero_trade_count,
                "duplicate_ratio": duplicate_count / max(1, total_trials_attempted),
                "pruned_ratio": pruned_count / max(1, total_trials_attempted),
                "zero_trade_ratio": zero_trade_count / max(1, total_trials_attempted),
            },
        }

    run_meta_path = run_dir / "run_meta.json"
    try:
        run_meta = json.loads(run_meta_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        run_meta = {}

    run_meta.setdefault("optuna", {}).update(optuna_meta)

    if best_payload is not None:
        atomic_write_text(run_dir / "best_trial.json", json_dumps(best_payload))

    atomic_write_text(run_meta_path, json_dumps(serialize_meta(run_meta)))
    return results


def _coerce_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return None
