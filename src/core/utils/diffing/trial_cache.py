"""Trial result caching helpers."""

from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

__all__ = ["TrialFingerprint", "TrialResultCache"]


@dataclass(slots=True)
class TrialFingerprint:
    """Canonical fingerprint for a trial configuration."""

    fingerprint: str
    canonical: str
    raw: dict[str, Any]


class TrialResultCache:
    """Disk-backed cache with basic thread-safety for Optuna trials."""

    def __init__(self, cache_dir: Path) -> None:
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def _path_for(self, fingerprint: str) -> Path:
        return self._cache_dir / f"{fingerprint}.json"

    def lookup(self, fingerprint: str) -> dict[str, Any] | None:
        path = self._path_for(fingerprint)
        if not path.exists():
            return None
        try:
            text = path.read_text(encoding="utf-8")
            return json.loads(text)
        except (json.JSONDecodeError, OSError):
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass
            return None

    def store(self, fingerprint: str, payload: dict[str, Any]) -> None:
        snapshot = json.dumps(payload, indent=2, sort_keys=True)
        path = self._path_for(fingerprint)
        with self._lock:
            path.write_text(snapshot, encoding="utf-8")

    def clear(self) -> int:
        """Remove all cached payloads."""

        removed = 0
        for cache_file in self._cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
                removed += 1
            except OSError:
                pass
        return removed
