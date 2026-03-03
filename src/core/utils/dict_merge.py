from __future__ import annotations

from typing import Any


def deep_merge_dicts(base: dict[str, Any], override: dict[str, Any] | None) -> dict[str, Any]:
    """Deep-merge ``override`` into ``base`` with stack-safe dict semantics.

    Semantics:
    - nested dict + nested dict => recursive merge
    - all other values => override replacement
    - input mappings are not mutated
    """

    merged = dict(base)
    if not override:
        return merged

    stack: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]] = [(merged, base, override)]
    while stack:
        target, base_current, override_current = stack.pop()
        for key, value in override_current.items():
            base_value = base_current.get(key)
            if isinstance(base_value, dict) and isinstance(value, dict):
                child = dict(base_value)
                target[key] = child
                stack.append((child, base_value, value))
            else:
                target[key] = value
    return merged
