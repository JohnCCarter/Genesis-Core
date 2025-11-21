"""Champion loader med validering och fallback."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import timeframe_configs  # noqa: E402

CHAMPIONS_DIR = ROOT / "config" / "strategy" / "champions"


@dataclass(slots=True)
class ChampionConfig:
    config: dict[str, Any]
    source: str
    version: str
    checksum: str
    loaded_at: str


@dataclass(slots=True)
class _CacheEntry:
    config: ChampionConfig
    mtime: float | None
    exists: bool


class ChampionLoader:
    """Hantera laddning av champion-konfig med validering och fallback."""

    def __init__(self, *, champions_dir: Path | None = None) -> None:
        self.champions_dir = champions_dir or CHAMPIONS_DIR
        self.champions_dir.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, _CacheEntry] = {}

    def _champion_path(self, symbol: str, timeframe: str) -> Path:
        return self.champions_dir / f"{symbol}_{timeframe}.json"

    def _compute_checksum(self, data: dict[str, Any]) -> str:
        payload = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return sha256(payload.encode("utf-8")).hexdigest()

    def _load_json(self, path: Path) -> dict[str, Any] | None:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    def _validate_champion(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        # Support multiple formats:
        # 1. {"parameters": {...}} or {"config": {...}} (top-level)
        # 2. {"cfg": {"parameters": {...}}} (wrapped format)
        config = payload.get("parameters") or payload.get("config")
        if not isinstance(config, dict):
            # Try wrapped format
            cfg_wrapper = payload.get("cfg", {})
            if isinstance(cfg_wrapper, dict):
                config = cfg_wrapper.get("parameters") or cfg_wrapper.get("config")
        if not isinstance(config, dict):
            return None
        return config

    def _build_config(
        self,
        *,
        symbol: str,
        timeframe: str,
        config_data: dict[str, Any],
        source: str,
        version: str,
    ) -> ChampionConfig:
        checksum = self._compute_checksum(config_data)
        return ChampionConfig(
            config=config_data,
            source=source,
            version=version,
            checksum=checksum,
            loaded_at=datetime.now(UTC).isoformat(),
        )

    def _load_from_disk(self, symbol: str, timeframe: str) -> _CacheEntry:
        champion_path = self._champion_path(symbol, timeframe)
        config_data: dict[str, Any] | None = None
        source = "baseline"
        version = "baseline"
        mtime: float | None = None
        exists = False

        if champion_path.exists():
            payload = self._load_json(champion_path)
            if payload:
                config_candidate = self._validate_champion(payload)
                if config_candidate:
                    config_data = config_candidate
                    try:
                        source = str(champion_path.relative_to(ROOT))
                    except ValueError:
                        source = str(champion_path)
                    version = str(payload.get("created_at", "unknown"))
                    exists = True
                    try:
                        mtime = champion_path.stat().st_mtime
                    except OSError:
                        mtime = None
        if config_data is None:
            fallback_source = timeframe
            try:
                config_data = timeframe_configs.get_timeframe_config(timeframe)
            except ValueError:
                config_data = timeframe_configs.get_timeframe_config("1h")
                fallback_source = "fallback_1h"
            version = "baseline"
            source = f"baseline:{fallback_source}"
            exists = False
            mtime = None
        config = self._build_config(
            symbol=symbol,
            timeframe=timeframe,
            config_data=config_data,
            source=source,
            version=version,
        )
        entry = _CacheEntry(config=config, mtime=mtime, exists=exists)
        return entry

    def load(self, symbol: str, timeframe: str) -> ChampionConfig:
        entry = self._load_from_disk(symbol, timeframe)
        key = f"{symbol}:{timeframe}"
        self._cache[key] = entry
        return entry.config

    def _needs_reload(self, symbol: str, timeframe: str, entry: _CacheEntry) -> bool:
        path = self._champion_path(symbol, timeframe)
        exists = path.exists()
        try:
            mtime = path.stat().st_mtime if exists else None
        except OSError:
            mtime = None

        # Check if file existence changed
        if entry.exists != exists:
            return True
        
        # Check if file was modified (only if it exists)
        if exists and entry.mtime != mtime:
            return True
        
        return False

    def load_cached(self, symbol: str, timeframe: str) -> ChampionConfig:
        key = f"{symbol}:{timeframe}"
        entry = self._cache.get(key)
        if entry is None:
            return self.load(symbol, timeframe)
        if self._needs_reload(symbol, timeframe, entry):
            # Reload from disk and update cache
            new_entry = self._load_from_disk(symbol, timeframe)
            self._cache[key] = new_entry
            return new_entry.config
        return entry.config
