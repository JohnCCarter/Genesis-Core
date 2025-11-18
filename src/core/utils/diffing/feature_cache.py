from __future__ import annotations

import hashlib
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Any


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
    return hashlib.sha256(payload).hexdigest()


def _flatten_series(series: Iterable[Any]) -> Sequence[float]:
    flattened: list[float] = []
    for item in series:
        # Treat nested Python sequences or array-like (e.g., numpy.ndarray) as sub-series
        if isinstance(item, list | tuple):
            flattened.extend(_flatten_series(item))
        elif hasattr(item, "tolist"):
            try:
                flattened.extend(_flatten_series(item.tolist()))
            except Exception:
                # Fallback to scalar conversion if tolist() is not appropriate
                flattened.append(float(item))
        else:
            flattened.append(float(item))
    return flattened


def _hash_iterable(
    values: Iterable[float], *, precision: int = 10, limit: int | None = None
) -> str:
    vals = list(values)
    if limit is not None and limit > 0:
        vals = vals[-limit:]
    rounded = ",".join(f"{float(v):.{precision}f}" for v in vals)
    return _hash_bytes(rounded.encode("utf-8"))


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
                flattened_sub = _flatten_series(sub)
                sub_hashes.append(
                    _hash_iterable(flattened_sub, precision=precision, limit=series_limit)
                )
            data_hash = _hash_bytes("|".join(sub_hashes).encode("utf-8"))
        else:
            flattened = _flatten_series(series)
            data_hash = _hash_iterable(flattened, precision=precision, limit=series_limit)
    return IndicatorFingerprint(name=name, params_hash=params_hash, data_hash=data_hash)
