from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ModelRegistry:
    """Minimal modellregister med champion/challenger-stöd.

    - Registry JSON-format (ex):
      {
        "tBTCUSD:1m": {
          "champion": "config/models/tBTCUSD_1m.json",
          "challenger": "config/models/tBTCUSD_1m_alt.json"
        }
      }
    - Om ingen post finns: försök per-symbol/tf fil i config/models/<SYMBOL>_<TF>.json
    - Fallback: None
    """

    def __init__(self, root: Path | None = None, registry_path: Path | None = None) -> None:
        self.root = root or Path(__file__).resolve().parents[3]
        self.registry_path = registry_path or (self.root / "config" / "models" / "registry.json")
        self._cache: dict[str, tuple[dict[str, Any], float]] = {}

    def _read_json(self, p: Path) -> dict[str, Any] | None:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else None
        except Exception:
            return None

    def _get_registry(self) -> dict[str, Any]:
        try:
            return self._read_json(self.registry_path) or {}
        except Exception:
            return {}

    def _candidate_model_path(self, symbol: str, timeframe: str) -> Path | None:
        fname = f"{symbol}_{timeframe}.json"
        p = self.root / "config" / "models" / fname
        return p if p.exists() else None

    def _load_model_meta(self, path: Path) -> dict[str, Any] | None:
        try:
            stat = path.stat()
            mtime = float(stat.st_mtime)
            key = str(path)
            cached = self._cache.get(key)
            if cached and abs(cached[1] - mtime) < 1e-6:
                return cached[0]
            meta = self._read_json(path)
            if meta is not None:
                self._cache[key] = (meta, mtime)
            return meta
        except Exception:
            return self._read_json(path)

    def get_meta(self, symbol: str, timeframe: str) -> dict[str, Any] | None:
        key = f"{symbol}:{timeframe}"
        reg = self._get_registry()
        entry = reg.get(key) if isinstance(reg, dict) else None
        if isinstance(entry, dict):
            champ = entry.get("champion")
            if isinstance(champ, str):
                p = Path(champ)
                if not p.is_absolute():
                    p = self.root / champ
                meta = self._load_model_meta(p)
                if meta is not None:
                    # Gammal struktur: direkt schema/buy/sell i roten
                    if isinstance(meta, dict) and (
                        "schema" in meta and "buy" in meta and "sell" in meta
                    ):
                        return meta
                    # Ny struktur: modell innehåller timeframes, plocka rätt timeframe
                    if isinstance(meta, dict) and timeframe in meta:
                        return meta[timeframe]
                    # Fallback till 1m om timeframe saknas
                    if isinstance(meta, dict) and "1m" in meta:
                        return meta["1m"]
        # Fallback: direkt fil per symbol/tf (gammal struktur)
        cand = self._candidate_model_path(symbol, timeframe)
        if cand:
            return self._load_model_meta(cand)
        return None
