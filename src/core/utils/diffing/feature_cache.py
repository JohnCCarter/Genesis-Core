from __future__ import annotations

import hashlib
from collections import deque
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from numbers import Number
from typing import Any

import numpy as np


@dataclass(frozen=True, slots=True)
class IndicatorFingerprint:
    name: str
    params_hash: str
    data_hash: str


class IndicatorCache:
    """Lättviktig in-memory cache för indikatorberäkningar."""

    def __init__(self, max_size: int = 1024) -> None:
        self._store: dict[IndicatorFingerprint, Any] = {}
        self._order: list[IndicatorFingerprint] = []
        self._max_size = max_size

    def _evict_if_needed(self) -> None:
        while len(self._order) > self._max_size:
            oldest = self._order.pop(0)
            self._store.pop(oldest, None)

    def lookup(self, key: IndicatorFingerprint) -> Any | None:
        value = self._store.get(key)
        if value is not None:
            try:
                self._order.remove(key)
            except ValueError:
                pass
            self._order.append(key)
        return value

    def store(self, key: IndicatorFingerprint, value: Any) -> None:
        self._store[key] = value
        if key in self._order:
            self._order.remove(key)
        self._order.append(key)
        self._evict_if_needed()


def _hash_bytes(payload: bytes) -> str:
    # blake2s is significantly faster than sha256 and still deterministic enough for cache keys
    return hashlib.blake2s(payload, digest_size=16).hexdigest()


def _flatten_series(series: Any, limit: int | None = None) -> list[float]:
    """Flatten nested iterables quickly while respecting an optional element limit."""

    keep_last = limit if limit is not None and limit > 0 else None
    collector: deque[float] | list[float]
    if keep_last:
        collector = deque(maxlen=keep_last)
    else:
        collector = []

    def _extend(values: Iterable[Any]) -> None:
        try:
            if keep_last:
                for val in values:
                    collector.append(float(val))
            else:
                collector.extend(float(val) for val in values)
        except Exception:  # nosec B112
            # Best-effort float coercion can skip invalid items
            # Fall back to element-wise insertion if bulk conversion fails
            for val in values:
                try:
                    collector.append(float(val))
                except Exception:  # nosec B112
                    continue

    stack: list[Any] = [series]
    while stack:
        item = stack.pop()
        if item is None:
            continue
        if isinstance(item, dict):
            values = list(item.values())
            if values:
                stack.extend(reversed(values))
            continue
        if isinstance(item, list | tuple):
            if item:
                stack.extend(reversed(item))
            continue
        if isinstance(item, np.ndarray):
            arr = np.asarray(item).reshape(-1)
            if keep_last and arr.size > keep_last:
                arr = arr[-keep_last:]
            _extend(arr)
            continue
        if hasattr(item, "to_numpy"):
            try:
                stack.append(item.to_numpy(copy=False))
                continue
            except Exception:  # nosec B110
                # Non-numpy objects can be skipped silently; later fallbacks handle them
                pass
        if hasattr(item, "tolist") and not isinstance(item, str | bytes):
            try:
                stack.append(item.tolist())
                continue
            except Exception:  # nosec B110
                # Fallback hashers handle the conversion failure later in the pipeline
                pass
        try:
            collector.append(float(item))
        except Exception:  # nosec B112
            # Intentionally skip non-coercible entries
            continue

    return list(collector)


def _hash_iterable(values: Sequence[float], *, precision: int = 10) -> str:
    vals = values
    rounded = ",".join(f"{float(v):.{precision}f}" for v in vals)
    return _hash_bytes(rounded.encode("utf-8"))


def _numeric_array_from(series: Any, limit: int | None = None) -> np.ndarray | None:
    """Attempt to coerce the input into a 1D float64 numpy array."""

    def _maybe_trim(arr: np.ndarray) -> np.ndarray:
        if limit and arr.size > limit:
            return arr[-limit:]
        return arr

    if isinstance(series, np.ndarray):
        try:
            return _maybe_trim(np.asarray(series, dtype=np.float64).reshape(-1))
        except Exception:
            return None

    if hasattr(series, "to_numpy"):
        try:
            arr = np.asarray(series.to_numpy(copy=False), dtype=np.float64).reshape(-1)
            return _maybe_trim(arr)
        except Exception:
            return None

    if isinstance(series, list | tuple) and (not series or isinstance(series[0], Number)):
        try:
            arr = np.asarray(series, dtype=np.float64).reshape(-1)
            return _maybe_trim(arr)
        except Exception:
            return None

    if isinstance(series, Number):
        return _maybe_trim(np.asarray([float(series)], dtype=np.float64))

    return None


def _hash_numeric_sequence(values: np.ndarray, *, precision: int = 10) -> str:
    if values.size == 0:
        return _hash_bytes(b"")
    arr = values.astype(np.float64)
    fmt = f"%.{precision}f"
    formatted = np.char.mod(fmt, arr)
    return _hash_bytes(",".join(formatted.tolist()).encode("utf-8"))


def make_indicator_fingerprint(
    name: str,
    *,
    params: dict[str, Any] | None = None,
    series: Iterable[Any] | None = None,
    precision: int = 10,
    series_limit: int = 256,
) -> IndicatorFingerprint:
    params = params or {}
    params_tuple: tuple[tuple[str, Any], ...] = tuple(sorted(params.items()))
    params_blob = ",".join(f"{k}={v}" for k, v in params_tuple)
    params_hash = _hash_bytes(params_blob.encode("utf-8"))
    data_hash = "none"
    if series is not None:
        if isinstance(series, list | tuple) and series and isinstance(series[0], list | tuple):
            sub_hashes = []
            for sub in series:
                numeric_arr = _numeric_array_from(sub, series_limit)
                if numeric_arr is not None:
                    sub_hashes.append(_hash_numeric_sequence(numeric_arr, precision=precision))
                else:
                    flattened_sub = _flatten_series(sub, limit=series_limit)
                    sub_hashes.append(_hash_iterable(flattened_sub, precision=precision))
            data_hash = _hash_bytes("|".join(sub_hashes).encode("utf-8"))
        else:
            numeric_arr = _numeric_array_from(series, series_limit)
            if numeric_arr is not None:
                data_hash = _hash_numeric_sequence(numeric_arr, precision=precision)
            else:
                flattened = _flatten_series(series, limit=series_limit)
                data_hash = _hash_iterable(flattened, precision=precision)
    return IndicatorFingerprint(name=name, params_hash=params_hash, data_hash=data_hash)
