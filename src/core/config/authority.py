from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from core.config.schema import RuntimeConfig, RuntimeSnapshot
from core.utils.logging_redaction import get_logger

_LOGGER = get_logger(__name__)
RUNTIME_PATH = Path.cwd() / "config" / "runtime.json"
AUDIT_LOG = Path.cwd() / "logs" / "config_audit.jsonl"
MAX_AUDIT_SIZE = 5 * 1024 * 1024  # 5 MB
SEED_PATH = Path.cwd() / "config" / "runtime.seed.json"


def _json_dumps_canonical(data: dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class ConfigAuthority:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or RUNTIME_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)

    def _read(self) -> tuple[int, dict[str, Any]]:
        if not self.path.exists():
            # Seed från seed-fil om den finns, annars default RuntimeConfig
            if SEED_PATH.exists():
                try:
                    data = json.loads(SEED_PATH.read_text(encoding="utf-8"))
                    v = int(data.get("version") or 0)
                    cfg_raw = data.get("cfg") or {}
                    _ = RuntimeConfig(**cfg_raw)  # validera
                    return v, cfg_raw
                except Exception as e:
                    _LOGGER.debug("seed_read_error: %s", e)
            cfg = RuntimeConfig().model_dump_canonical()
            return 0, cfg
        data = json.loads(self.path.read_text(encoding="utf-8"))
        version = int(data.get("version") or 0)
        cfg = data.get("cfg") or {}
        return version, cfg

    def _hash_cfg(self, cfg: dict[str, Any]) -> str:
        return _json_dumps_canonical(cfg)

    def load(self) -> RuntimeSnapshot:
        version, cfg_raw = self._read()
        cfg = RuntimeConfig(**cfg_raw)
        cfg_canon = cfg.model_dump_canonical()
        h = self._hash_cfg(cfg_canon)
        return RuntimeSnapshot(version=version, hash=h, cfg=cfg)

    def validate(self, proposal: dict[str, Any]) -> RuntimeConfig:
        return RuntimeConfig(**proposal)

    def get(self) -> tuple[RuntimeConfig, str, int]:
        snap = self.load()
        return snap.cfg, snap.hash, snap.version

    def _persist_atomic(
        self,
        new_cfg: RuntimeConfig,
        expected_version: int,
        *,
        actor: str = "system",
        changed_paths: list[str] | None = None,
        hash_before: str | None = None,
    ) -> RuntimeSnapshot:
        # optimistic lock
        cur_version, _ = self._read()
        if cur_version != expected_version:
            raise RuntimeError("version_conflict")

        next_version = cur_version + 1
        cfg_canon = new_cfg.model_dump_canonical()
        payload = {
            "version": next_version,
            "cfg": cfg_canon,
        }
        data = _json_dumps_canonical(payload)
        tmp = self.path.with_suffix(self.path.suffix + f".tmp.{os.getpid()}")

        with open(tmp, "w", encoding="utf-8") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, self.path)
        try:
            dir_fd = os.open(self.path.parent, os.O_DIRECTORY)
            os.fsync(dir_fd)
            os.close(dir_fd)
        except Exception:
            pass

        # hash & audit
        h = self._hash_cfg(cfg_canon)
        try:
            # simple rotation if file too large
            try:
                if AUDIT_LOG.exists() and AUDIT_LOG.stat().st_size > MAX_AUDIT_SIZE:
                    rotated = AUDIT_LOG.with_suffix(AUDIT_LOG.suffix + ".1")
                    if rotated.exists():
                        rotated.unlink(missing_ok=True)  # type: ignore[arg-type]
                    AUDIT_LOG.rename(rotated)
            except Exception:
                pass
            audit = {
                "ts": time.time(),
                "actor": actor,
                "expected_version": expected_version,
                "new_version": next_version,
                "hash_before": hash_before,
                "hash_after": h,
                "paths": changed_paths or [],
            }
            with open(AUDIT_LOG, "a", encoding="utf-8") as af:
                af.write(json.dumps(audit, ensure_ascii=False) + "\n")
        except Exception as e:
            _LOGGER.debug("audit_write_error: %s", e)

        return RuntimeSnapshot(version=next_version, hash=h, cfg=new_cfg)

    def propose_update(
        self, patch: dict[str, Any], *, actor: str, expected_version: int
    ) -> RuntimeSnapshot:
        # whitelist enforcement (path-based)
        def _enforce_whitelist(p: dict[str, Any]) -> None:
            for k, v in (p or {}).items():
                if k not in {"thresholds", "gates", "risk", "ev"}:
                    raise ValueError("non_whitelisted_field")
                if k == "risk":
                    if not isinstance(v, dict) or any(subk != "risk_map" for subk in v.keys()):
                        raise ValueError("non_whitelisted_field:risk")
                if k == "ev":
                    if not isinstance(v, dict) or any(subk != "R_default" for subk in v.keys()):
                        raise ValueError("non_whitelisted_field:ev")

        _enforce_whitelist(patch)

        # merge on top of current cfg
        current_cfg = self.load().cfg
        cur = current_cfg.model_dump_canonical()
        merged = {**cur, **patch}
        try:
            new_cfg = RuntimeConfig(**merged)
        except ValidationError as e:
            raise ValueError("validation_error") from e

        # diff paths for audit
        def _diff_paths(a: Any, b: Any, prefix: str = "") -> list[str]:
            paths: list[str] = []
            if isinstance(a, dict) and isinstance(b, dict):
                keys = set(a.keys()) | set(b.keys())
                for key in keys:
                    sub = prefix + ("." if prefix else "") + str(key)
                    if key not in a or key not in b:
                        paths.append(sub)
                    else:
                        paths.extend(_diff_paths(a[key], b[key], sub))
            elif isinstance(a, list) and isinstance(b, list):
                if a != b:
                    paths.append(prefix)
            else:
                if a != b:
                    paths.append(prefix)
            return paths

        old_hash = self._hash_cfg(cur)
        changed = _diff_paths(cur, new_cfg.model_dump_canonical())
        return self._persist_atomic(
            new_cfg,
            expected_version,
            actor=actor,
            changed_paths=changed,
            hash_before=old_hash,
        )
