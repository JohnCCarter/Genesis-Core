"""Champion loader med validering och fallback."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

from config import timeframe_configs

ROOT = Path(__file__).resolve().parents[3]
CHAMPIONS_DIR = ROOT / "config" / "strategy" / "champions"


@dataclass(slots=True)
class ChampionConfig:
    config: dict[str, Any]
    source: str
    version: str
    checksum: str
    loaded_at: str


class ChampionLoader:
    """Hantera laddning av champion-konfig med validering och fallback."""

    def __init__(self, *, champions_dir: Path | None = None) -> None:
        self.champions_dir = champions_dir or CHAMPIONS_DIR
        self.champions_dir.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, ChampionConfig] = {}

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
        config = payload.get("parameters") or payload.get("config")
        if not isinstance(config, dict):
            return None
        return config

    def load(self, symbol: str, timeframe: str) -> ChampionConfig:
        key = f"{symbol}:{timeframe}"
        champion_path = self._champion_path(symbol, timeframe)
        config_data: dict[str, Any] | None = None
        source = "baseline"
        version = "baseline"
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
        if config_data is None:
            config_data = timeframe_configs.get_timeframe_config(timeframe)
            version = "baseline"
            source = f"baseline:{timeframe}"
        checksum = self._compute_checksum(config_data)
        result = ChampionConfig(
            config=config_data,
            source=source,
            version=version,
            checksum=checksum,
            loaded_at=datetime.now(UTC).isoformat(),
        )
        self._cache[key] = result
        return result

    def load_cached(self, symbol: str, timeframe: str) -> ChampionConfig:
        key = f"{symbol}:{timeframe}"
        cached = self._cache.get(key)
        if cached:
            return cached
        return self.load(symbol, timeframe)
