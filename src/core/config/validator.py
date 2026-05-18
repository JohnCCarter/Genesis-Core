"""Legacy schema-v1 helpers for config checks and top-level diffing.

This module is intentionally legacy/test-only in the current architecture.
It validates only the compact schema-v1 surface and must not be treated as the
runtime-config authority.

Runtime config validation must go through ``ConfigAuthority.validate`` via
``core.api.config``.
"""

from __future__ import annotations

import json
import os
from typing import Any

from jsonschema import Draft7Validator

LEGACY_SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "legacy_schema_v1.json")
# Backward-compatible alias for older imports/tests that still reference SCHEMA_PATH.
SCHEMA_PATH = LEGACY_SCHEMA_PATH

with open(LEGACY_SCHEMA_PATH, encoding="utf-8") as f:
    _SCHEMA = json.load(f)

_VALIDATOR = Draft7Validator(_SCHEMA)


def validate_legacy_config(cfg: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for e in _VALIDATOR.iter_errors(cfg):
        errors.append(e.message)
    return errors


def validate_config(cfg: dict[str, Any]) -> list[str]:
    """Backward-compatible alias for legacy schema-v1 validation."""

    return validate_legacy_config(cfg)


def diff_legacy_config(old: dict[str, Any], new: dict[str, Any]) -> list[dict]:
    changes: list[dict] = []
    keys = set(old.keys()) | set(new.keys())
    for k in sorted(keys):
        ov = old.get(k)
        nv = new.get(k)
        if ov != nv:
            changes.append({"key": k, "old": ov, "new": nv})
    return changes


def diff_config(old: dict[str, Any], new: dict[str, Any]) -> list[dict]:
    """Backward-compatible alias for legacy top-level config diffing."""

    return diff_legacy_config(old, new)


__all__ = [
    "LEGACY_SCHEMA_PATH",
    "SCHEMA_PATH",
    "validate_legacy_config",
    "validate_config",
    "diff_legacy_config",
    "diff_config",
]
