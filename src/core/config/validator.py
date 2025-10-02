from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, List

from jsonschema import Draft7Validator

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema_v1.json")
AUDIT_LOG = os.path.join(os.getcwd(), "logs", "config_audit.log")

with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    _SCHEMA = json.load(f)

_VALIDATOR = Draft7Validator(_SCHEMA)


def validate_config(cfg: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    for e in _VALIDATOR.iter_errors(cfg):
        errors.append(e.message)
    return errors


def diff_config(old: Dict[str, Any], new: Dict[str, Any]) -> List[dict]:
    changes: List[dict] = []
    keys = set(old.keys()) | set(new.keys())
    for k in sorted(keys):
        ov = old.get(k)
        nv = new.get(k)
        if ov != nv:
            changes.append({"key": k, "old": ov, "new": nv})
    return changes


def append_audit(changes: List[dict], user: str = "system") -> None:
    if not changes:
        return
    os.makedirs(os.path.join(os.getcwd(), "logs"), exist_ok=True)
    line = json.dumps(
        {
            "ts": datetime.utcnow().isoformat(),
            "user": user,
            "changes": changes,
            "schema": "v1",
        },
        ensure_ascii=False,
    )
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")
