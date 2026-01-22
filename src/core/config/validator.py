from __future__ import annotations

import json
import os
from typing import Any

from jsonschema import Draft7Validator

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema_v1.json")

with open(SCHEMA_PATH, encoding="utf-8") as f:
    _SCHEMA = json.load(f)

_VALIDATOR = Draft7Validator(_SCHEMA)


def validate_config(cfg: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for e in _VALIDATOR.iter_errors(cfg):
        errors.append(e.message)
    return errors


def diff_config(old: dict[str, Any], new: dict[str, Any]) -> list[dict]:
    changes: list[dict] = []
    keys = set(old.keys()) | set(new.keys())
    for k in sorted(keys):
        ov = old.get(k)
        nv = new.get(k)
        if ov != nv:
            changes.append({"key": k, "old": ov, "new": nv})
    return changes
