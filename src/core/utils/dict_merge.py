from __future__ import annotations

from typing import Any


def deep_merge_dicts(base: dict[str, Any], override: dict[str, Any] | None) -> dict[str, Any]:
    """Deep-merge ``override`` into ``base`` with recursive dict semantics.

    Semantics:
    - nested dict + nested dict => recursive merge
    - all other values => override replacement
    - input mappings are not mutated
    """

    merged = dict(base)
    for key, value in (override or {}).items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = deep_merge_dicts(merged[key], value)
        else:
            merged[key] = value
    return merged
