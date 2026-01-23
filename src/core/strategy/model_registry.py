from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.utils import is_case_sensitive_directory
from core.utils.logging_redaction import get_logger

_LOGGER = get_logger(__name__)


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
        self._registry_cache: dict[str, Any] | None = None
        self._registry_mtime: float | None = None
        self._warned_unsafe_month_paths_mtime: float | None = None

    def _warn_if_unsafe_month_paths(self, registry: dict[str, Any], *, mtime: float) -> None:
        """Warn once per registry mtime if monthly model paths are unsafe on this FS.

        On case-insensitive filesystems (common on Windows/macOS), "*_1M.json" can alias
        to "*_1m.json" which is a different timeframe. Monthly files should use "*_1mo.json".
        """

        if self._warned_unsafe_month_paths_mtime == mtime:
            return

        models_dir = self.root / "config" / "models"
        if is_case_sensitive_directory(models_dir):
            self._warned_unsafe_month_paths_mtime = mtime
            return

        unsafe: list[str] = []
        for key, entry in registry.items():
            if not isinstance(entry, dict):
                continue
            champ = entry.get("champion")
            if not isinstance(champ, str):
                continue
            if champ.endswith("_1M.json"):
                unsafe.append(f"{key} -> {champ}")

        if unsafe:
            sample = "; ".join(unsafe[:5])
            more = "" if len(unsafe) <= 5 else f" (+{len(unsafe) - 5} more)"
            _LOGGER.warning(
                "Model registry contains monthly champion paths ending with '_1M.json' on a "
                "case-insensitive filesystem. This is unsafe because it can alias to minute models "
                "('_1m.json'). Use '*_1mo.json' for monthly model filenames and update registry paths. "
                "Examples: %s%s",
                sample,
                more,
            )

        self._warned_unsafe_month_paths_mtime = mtime

    def _read_json(self, p: Path) -> dict[str, Any] | None:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else None
        except Exception:
            return None

    def _get_registry(self) -> dict[str, Any]:
        """Get registry with caching based on file mtime."""
        try:
            if self.registry_path.exists():
                mtime = self.registry_path.stat().st_mtime
                if self._registry_cache is not None and self._registry_mtime == mtime:
                    return self._registry_cache
                registry = self._read_json(self.registry_path) or {}
                self._warn_if_unsafe_month_paths(registry, mtime=float(mtime))
                self._registry_cache = registry
                self._registry_mtime = mtime
                return registry
            return {}
        except Exception:
            return {}

    def _candidate_model_path(self, symbol: str, timeframe: str) -> Path | None:
        models_dir = self.root / "config" / "models"

        timeframes: list[str]
        if timeframe in {"1M", "1mo"}:
            # On case-insensitive filesystems, "1M" aliases to "1m" and is unsafe.
            timeframes = ["1mo"]
            if is_case_sensitive_directory(models_dir):
                timeframes.append("1M")
        else:
            timeframes = [timeframe]

        for tf in timeframes:
            fname = f"{symbol}_{tf}.json"
            p = models_dir / fname
            if p.exists():
                return p
        return None

    def _timeframe_aliases(self, timeframe: str) -> list[str]:
        if timeframe == "1M":
            return ["1M", "1mo"]
        if timeframe == "1mo":
            return ["1mo", "1M"]
        return [timeframe]

    def _month_model_path_candidates(self, path: Path) -> list[Path]:
        """Return safe path candidates for monthly models.

        On case-insensitive filesystems, we must never try a "*_1M.json" path since
        it can alias to the minute model ("*_1m.json").
        """

        models_dir = self.root / "config" / "models"
        case_sensitive = is_case_sensitive_directory(models_dir)

        name = path.name
        if name.endswith("_1M.json"):
            safe = path.with_name(name[: -len("_1M.json")] + "_1mo.json")
            return [safe] if not case_sensitive else [safe, path]
        if name.endswith("_1mo.json"):
            legacy = path.with_name(name[: -len("_1mo.json")] + "_1M.json")
            return [path, legacy] if case_sensitive else [path]

        # Unknown naming, try as-is.
        return [path]

    def _load_model_meta(self, path: Path) -> dict[str, Any] | None:
        try:
            stat = path.stat()
            mtime = float(stat.st_mtime)
            key = str(path)
            cached = self._cache.get(key)
            # Improved cache invalidation: exact mtime match required
            if cached and cached[1] == mtime:
                return cached[0]
            meta = self._read_json(path)
            if meta is not None:
                self._cache[key] = (meta, mtime)
            return meta
        except Exception:
            return self._read_json(path)

    def clear_cache(self) -> None:
        """Clear model cache. Call after updating model files."""
        self._cache.clear()
        self._registry_cache = None
        self._registry_mtime = None

    def get_meta(self, symbol: str, timeframe: str) -> dict[str, Any] | None:
        reg = self._get_registry()
        tf_candidates = self._timeframe_aliases(timeframe)

        for tf in tf_candidates:
            key = f"{symbol}:{tf}"
            entry = reg.get(key) if isinstance(reg, dict) else None
            if not isinstance(entry, dict):
                continue

            champ = entry.get("champion")
            if not isinstance(champ, str):
                continue

            p = Path(champ)
            if not p.is_absolute():
                p = self.root / champ

            paths_to_try = [p]
            if tf in {"1M", "1mo"}:
                paths_to_try = self._month_model_path_candidates(p)

            meta: dict[str, Any] | None = None
            for cand_path in paths_to_try:
                meta = self._load_model_meta(cand_path)
                if meta is not None:
                    break

            if meta is None:
                continue

            # Gammal struktur: direkt schema/buy/sell i roten
            if isinstance(meta, dict) and ("schema" in meta and "buy" in meta and "sell" in meta):
                return meta

            # Ny struktur: modell innehåller timeframes, plocka rätt timeframe (med alias stöd)
            if isinstance(meta, dict):
                for k in tf_candidates:
                    if k in meta:
                        return meta[k]

                # Fallback till 1m om timeframe saknas (men inte för månads-timeframes)
                if timeframe not in {"1M", "1mo"} and "1m" in meta:
                    return meta["1m"]
        # Fallback: direkt fil per symbol/tf (gammal struktur)
        for tf in tf_candidates:
            cand = self._candidate_model_path(symbol, tf)
            if cand:
                meta = self._load_model_meta(cand)
                if isinstance(meta, dict) and (
                    "schema" in meta and "buy" in meta and "sell" in meta
                ):
                    return meta
                if isinstance(meta, dict):
                    for k in tf_candidates:
                        if k in meta:
                            return meta[k]
                    if timeframe not in {"1M", "1mo"} and "1m" in meta:
                        return meta["1m"]
        return None
