"""
Optuna helpers for Genesis-Core
- Deterministic seeds
- Robust storage (SQLite/Postgres) with heartbeat
- High-quality samplers (QMC Sobol or TPE)
- Duplicate-trial prevention (callback + pre-check Ask/Tell)
- Lightweight persistent signature DB (SQLite or Redis optional)
- Env fingerprint + dataset hashing for perfect reproducibility

Usage (quick):

    from core.utils.optuna_helpers import (
        ensure_storage, make_sampler, set_global_seeds,
        NoDupeGuard, no_dupe_callback,
        ask_tell_optimize, param_signature,
        env_fingerprint, dataframe_sha1
    )

    import optuna

    set_global_seeds(42)
    storage = ensure_storage("sqlite:///optuna.db")
    sampler = make_sampler(mode="qmc", seed=42)
    study = optuna.create_study(
        study_name="genesis_opt",
        storage=storage,
        load_if_exists=True,
        direction="maximize",
        sampler=sampler,
    )

    guard = NoDupeGuard(sqlite_path=".optuna_dedup.db")  # or redis_url="redis://localhost:6379/0"

    # Option A: normal optimize with after-the-fact dedup prune
    study.optimize(objective, n_trials=300, callbacks=[no_dupe_callback(guard)], n_jobs=8)

    # Option B (recommended in clusters): ask/tell with pre-check dedup
    ask_tell_optimize(study, objective, n_trials=300, guard=guard)

"""

from __future__ import annotations

import hashlib
import json
import os
import random
import sqlite3
import sys
import threading
import time
from collections.abc import Callable
from contextlib import closing
from dataclasses import dataclass
from typing import Any

import numpy as np

try:
    import optuna
    from optuna.storages import RDBStorage
except Exception as e:  # pragma: no cover
    raise RuntimeError("optuna must be installed to use this module") from e

# --- Seeds & determinism ----------------------------------------------------


def set_global_seeds(seed: int = 42) -> None:
    """Set deterministic seeds for Python, NumPy and hash randomization."""
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    # Torch (optional)
    try:  # pragma: no cover
        import torch

        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    except Exception:
        pass


# --- Storage ----------------------------------------------------------------


def ensure_storage(url: str, heartbeat_interval: int = 60, grace_period: int = 120) -> RDBStorage:
    """Create an Optuna RDBStorage with heartbeat (SQLite/Postgres/MySQL URLs)."""
    return RDBStorage(url=url, heartbeat_interval=heartbeat_interval, grace_period=grace_period)


# --- Samplers ---------------------------------------------------------------


def make_sampler(mode: str = "qmc", seed: int = 42) -> optuna.samplers.BaseSampler:
    """Factory for good default samplers.

    mode="qmc" -> Sobol/QMC (uniform coverage, few duplicates)
    mode="tpe" -> TPE with multivariate + constant liar (parallel friendly)
    """
    m = mode.lower()
    if m == "qmc":
        return optuna.samplers.QMCSampler(qmc_type="sobol", scramble=True, seed=seed)
    if m == "tpe":
        return optuna.samplers.TPESampler(
            seed=seed,
            multivariate=True,
            constant_liar=True,
            n_startup_trials=25,
            n_ei_candidates=48,
        )
    raise ValueError(f"Unknown sampler mode: {mode}")


# --- Parameter signature (stable, nested) -----------------------------------


def _normalize_for_sig(x: Any, precision: int = 10) -> Any:
    if isinstance(x, float):
        return round(x, precision)
    if isinstance(x, (list, tuple)):
        return [_normalize_for_sig(v, precision) for v in x]
    if isinstance(x, dict):
        return {k: _normalize_for_sig(x[k], precision) for k in sorted(x)}
    return x


def param_signature(params: dict[str, Any], precision: int = 10) -> str:
    """Create a stable SHA1 signature for a parameter dict (nested ok)."""
    norm = _normalize_for_sig(params, precision)
    blob = json.dumps(norm, sort_keys=True, separators=(",", ":"))
    return hashlib.sha1(blob.encode()).hexdigest()


# --- Persistent dedup backend -----------------------------------------------


@dataclass
class NoDupeGuard:
    """Persistent set of tried parameter signatures.

    Use either `sqlite_path` (default) or `redis_url`.
    Safe to use across processes.
    """

    sqlite_path: str | None = ".optuna_dedup.db"
    redis_url: str | None = None

    def __post_init__(self) -> None:
        self._lock = threading.Lock()
        self._use_redis = False
        self._redis = None
        if self.redis_url:
            try:  # pragma: no cover
                import redis

                self._redis = redis.StrictRedis.from_url(self.redis_url, decode_responses=True)
                # Test connection
                self._redis.ping()
                self._use_redis = True
            except Exception:
                # Fallback to SQLite if Redis not available
                self._use_redis = False
        if not self._use_redis:
            assert self.sqlite_path is not None
            self._init_sqlite()

    # --- SQLite backend
    def _init_sqlite(self) -> None:
        with closing(sqlite3.connect(self.sqlite_path)) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS dedup_signatures (sig TEXT PRIMARY KEY, ts REAL NOT NULL)"
            )
            conn.commit()

    def _sqlite_seen(self, sig: str) -> bool:
        with closing(sqlite3.connect(self.sqlite_path)) as conn:
            row = conn.execute("SELECT 1 FROM dedup_signatures WHERE sig=?", (sig,)).fetchone()
            return row is not None

    def _sqlite_add(self, sig: str) -> bool:
        with closing(sqlite3.connect(self.sqlite_path)) as conn:
            try:
                conn.execute(
                    "INSERT INTO dedup_signatures(sig, ts) VALUES(?, ?)", (sig, time.time())
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    # --- Redis backend
    def _redis_seen(self, sig: str) -> bool:  # pragma: no cover
        return bool(self._redis.sismember("optuna:dedup", sig))

    def _redis_add(self, sig: str) -> bool:  # pragma: no cover
        return bool(self._redis.sadd("optuna:dedup", sig))  # returns 1 if added, 0 if existed

    # --- Public API
    def seen(self, sig: str) -> bool:
        if self._use_redis:
            return self._redis_seen(sig)
        return self._sqlite_seen(sig)

    def add(self, sig: str) -> bool:
        """Add signature. Returns True if new, False if duplicate."""
        if self._use_redis:
            return self._redis_add(sig)
        return self._sqlite_add(sig)

    def remove(self, sig: str) -> None:
        """Remove signature so future trials can reuse it (best-effort)."""
        if self._use_redis:  # pragma: no cover
            try:
                self._redis.srem("optuna:dedup", sig)
            except Exception:
                pass
            return
        if not self.sqlite_path:
            return
        with closing(sqlite3.connect(self.sqlite_path)) as conn:
            conn.execute("DELETE FROM dedup_signatures WHERE sig=?", (sig,))
            conn.commit()


# --- Callback: prune duplicates after trial finishes ------------------------


def no_dupe_callback(
    guard: NoDupeGuard,
) -> Callable[[optuna.study.Study, optuna.trial.FrozenTrial], None]:
    """Return a callback that prunes a trial if its params were already seen.

    Use this with `study.optimize(..., callbacks=[no_dupe_callback(guard)])`.
    Note: This triggers *after* a trial completes; for zero wasted compute, prefer
    the `ask_tell_optimize` pre-check loop below.
    """

    def _cb(study: optuna.study.Study, trial: optuna.trial.FrozenTrial) -> None:
        sig = param_signature(trial.params)
        # Try to add; if exists -> mark duplicate
        added = guard.add(sig)
        if not added:
            # Mark as pruned duplicate for visibility in UI
            try:
                trial.set_user_attr("duplicate_of", sig)
            except Exception:
                pass
            raise optuna.TrialPruned("Duplicate parameter set (post-hoc)")

    return _cb


# --- Ask/Tell loop with pre-check (preferred in clusters) -------------------


def ask_tell_optimize(
    study: optuna.study.Study,
    objective: Callable[[optuna.trial.Trial], float],
    n_trials: int,
    guard: NoDupeGuard | None = None,
    show_progress: bool = True,
) -> None:
    """Run optimization using ask/tell and skip duplicates *before* evaluation."""
    guard = guard or NoDupeGuard()
    for i in range(n_trials):
        trial = study.ask()
        sig = param_signature(trial.params)
        if guard.seen(sig):
            study.tell(trial, state=optuna.trial.TrialState.PRUNED)
            if show_progress:
                print(f"[{i+1}/{n_trials}] DUPLICATE -> pruned", file=sys.stderr)
            continue
        # reserve the signature to avoid races
        guard.add(sig)
        try:
            value = objective(trial)
            study.tell(trial, value)
            if show_progress:
                print(f"[{i+1}/{n_trials}] value={value:.6f}")
        except optuna.TrialPruned as e:
            study.tell(trial, state=optuna.trial.TrialState.PRUNED)
            if show_progress:
                print(f"[{i+1}/{n_trials}] PRUNED: {e}")
        except Exception as e:  # keep going on failures
            study.tell(trial, state=optuna.trial.TrialState.FAIL)
            guard.remove(sig)
            if show_progress:
                print(f"[{i+1}/{n_trials}] FAIL: {e}", file=sys.stderr)


# --- Reproducibility helpers -------------------------------------------------


def env_fingerprint(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return a dict with Python/lib versions and OS info."""
    import platform

    fp = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
    }
    # Optional libs
    for name in ("numpy", "pandas", "ta", "ccxt", "torch"):
        try:
            mod = __import__(name)
            ver = getattr(mod, "__version__", None)
            if ver:
                fp[name] = ver
        except Exception:
            pass
    if extra:
        fp.update(extra)
    return fp


def dataframe_sha1(df) -> str:
    """Compute a quick SHA1 over a pandas DataFrame index+values (float-safe)."""
    # Lazy import to avoid pandas hard dep
    import pandas as pd  # type: ignore

    if not isinstance(df, pd.DataFrame):
        raise TypeError("dataframe_sha1 expects a pandas.DataFrame")
    # Ensure stable bytes: use numpy view
    arr = np.ascontiguousarray(df.to_numpy(dtype=float))
    h = hashlib.sha1()
    h.update(arr.tobytes())
    # Index and columns add to identity
    h.update(pd.util.hash_pandas_object(df.index, index=True).values.tobytes())
    h.update(pd.util.hash_pandas_object(df.columns, index=True).values.tobytes())
    return h.hexdigest()


# --- Convenience: attach metadata to a running trial ------------------------


def attach_repro_meta(
    trial: optuna.trial.Trial, *, data_hash: str | None = None, notes: str = ""
) -> None:
    """Attach reproducibility metadata to the trial for later debugging."""
    try:
        trial.set_user_attr("env", env_fingerprint())
        if data_hash:
            trial.set_user_attr("data_hash", data_hash)
        if notes:
            trial.set_user_attr("notes", notes)
    except Exception:
        pass


# --- Example objective (remove in prod) -------------------------------------
if __name__ == "__main__":  # Minimal smoke test
    set_global_seeds(42)
    storage = ensure_storage("sqlite:///optuna.db")
    study = optuna.create_study(
        study_name="_smoke_",
        storage=storage,
        load_if_exists=True,
        direction="maximize",
        sampler=make_sampler("qmc", 42),
    )

    def objective(trial: optuna.trial.Trial) -> float:
        x = trial.suggest_float("x", -5, 5)
        y = trial.suggest_float("y", -5, 5)
        attach_repro_meta(trial, notes="smoke-test")
        return -((x - 2) ** 2) - ((y + 3) ** 2) + 10

    guard = NoDupeGuard()
    ask_tell_optimize(study, objective, n_trials=20, guard=guard)
    print("Best:", study.best_trial.value, study.best_trial.params)
