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


def _json_dumps_canonical(data: dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class ConfigAuthority:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or RUNTIME_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)

    def _read(self) -> tuple[int, dict[str, Any]]:
        if not self.path.exists():
            # Seed empty defaults
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

    def _persist_atomic(self, new_cfg: RuntimeConfig, expected_version: int) -> RuntimeSnapshot:
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

        # audit
        try:
            audit = {
                "ts": time.time(),
                "expected_version": expected_version,
                "new_version": next_version,
            }
            with open(AUDIT_LOG, "a", encoding="utf-8") as af:
                af.write(json.dumps(audit, ensure_ascii=False) + "\n")
        except Exception as e:
            _LOGGER.debug("audit_write_error: %s", e)

        h = self._hash_cfg(cfg_canon)
        return RuntimeSnapshot(version=next_version, hash=h, cfg=new_cfg)

    def propose_update(self, patch: dict[str, Any], *, actor: str, expected_version: int) -> RuntimeSnapshot:
        # whitelist enforcement
        wl_top = {"thresholds", "gates", "risk", "ev"}
        for k in patch.keys():
            if k not in wl_top:
                raise ValueError("non_whitelisted_field")

        # merge on top of current cfg
        cur = self.load().cfg.model_dump_canonical()
        merged = {**cur, **patch}
        try:
            new_cfg = RuntimeConfig(**merged)
        except ValidationError as e:
            raise ValueError("validation_error") from e
        return self._persist_atomic(new_cfg, expected_version)


