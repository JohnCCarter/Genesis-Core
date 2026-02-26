from __future__ import annotations

import json
from collections.abc import Iterable
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

_DEFAULT_IGNORE_PATHS: frozenset[tuple[str, ...]] = frozenset(
    {
        ("trial_id",),
        ("log",),
        ("log_path",),
        ("results_path",),
        ("from_cache",),
        ("duration_seconds",),
        ("attempt_durations",),
        ("attempts",),
        ("config_path",),
        ("timestamp",),
        ("created_at",),
        ("loaded_at",),
    }
)


_DEFAULT_VOLATILE_KEYS: frozenset[str] = frozenset(
    {
        # Common timestamp / run identifiers
        "ts",
        "timestamp",
        "created_at",
        "loaded_at",
        "run_id",
        "trial_id",
        "error_id",
        # File/log paths and attempt telemetry
        "log",
        "log_path",
        "results_path",
        "config_path",
        "duration_seconds",
        "attempt_durations",
        "attempts",
        # Strategy/runtime meta that is intentionally non-deterministic
        "champion_loaded_at",
    }
)


def scrub_volatile(payload: Any, *, volatile_keys: frozenset[str] | None = None) -> Any:
    """Recursively remove volatile fields from nested payloads.

    This is used to produce stable fingerprints that ignore timestamps/run IDs and
    other non-deterministic metadata.
    """

    keys = _DEFAULT_VOLATILE_KEYS if volatile_keys is None else volatile_keys

    if isinstance(payload, dict):
        out: dict[str, Any] = {}
        for k, v in payload.items():
            if isinstance(k, str) and k in keys:
                continue
            out[k] = scrub_volatile(v, volatile_keys=keys)
        return out

    if isinstance(payload, list):
        return [scrub_volatile(v, volatile_keys=keys) for v in payload]

    if isinstance(payload, tuple):
        return tuple(scrub_volatile(v, volatile_keys=keys) for v in payload)

    return payload


def _round_float(value: float, precision: int) -> float:
    quantize_exp = Decimal("1") / (Decimal(10) ** precision)
    return float(Decimal(str(value)).quantize(quantize_exp, rounding=ROUND_HALF_UP))


def canonicalize_config(
    payload: Any,
    *,
    precision: int = 6,
    ignore_paths: Iterable[Iterable[str]] | None = None,
) -> Any:
    """Return payload in canonical form for hashing/comparison.

    - Floats rounded deterministically (ROUND_HALF_UP)
    - Dicts sorted by key
    - Lists normalised recursively
    - Fields under ignore_paths removed
    """

    if ignore_paths is None:
        ignore_set = _DEFAULT_IGNORE_PATHS
    else:
        ignore_set = _DEFAULT_IGNORE_PATHS.union(tuple(tuple(p) for p in ignore_paths))

    def _should_ignore(path: tuple[str, ...]) -> bool:
        return path in ignore_set

    def _inner(obj: Any, path: tuple[str, ...]) -> Any:
        if _should_ignore(path):
            return None

        if isinstance(obj, float):
            return _round_float(obj, precision)

        if isinstance(obj, int | str | bool) or obj is None:
            return obj

        if isinstance(obj, list | tuple):
            normalized = [_inner(item, path + (str(idx),)) for idx, item in enumerate(obj)]
            return [item for item in normalized if item is not None]

        if isinstance(obj, dict):
            items: list[tuple[str, Any]] = []
            for key in sorted(obj.keys()):
                value = _inner(obj[key], path + (key,))
                if value is not None:
                    items.append((key, value))
            return dict(items)

        # Fallback: stringify to avoid non-serialisable objects exploding hashing
        return str(obj)

    return _inner(payload, ())


def fingerprint_config(payload: Any, *, precision: int = 6) -> str:
    """Compute a stable fingerprint for payload."""

    canonical = canonicalize_config(payload, precision=precision)
    blob = json.dumps(canonical, separators=(",", ":"), sort_keys=True)
    import hashlib

    return hashlib.sha256(blob.encode("utf-8")).hexdigest()
