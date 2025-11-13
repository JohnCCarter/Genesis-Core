from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class TrialFingerprint:
    fingerprint: str
    canonical: str
    raw: dict[str, Any]


class TrialResultCache:
    """Disk-backed cache med trådsäkerhet för Optuna-trials."""

    def __init__(self, cache_dir: Path) -> None:
        self._cache_dir = cache_dir
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
        path = self._path_for(fingerprint)
        snapshot = json.dumps(payload, indent=2, sort_keys=True)
        with self._lock:
            path.write_text(snapshot, encoding="utf-8")
