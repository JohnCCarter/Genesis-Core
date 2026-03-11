from __future__ import annotations

from typing import Any


def indicator_cache_lookup(indicator_cache: Any, enabled: bool, key: Any):
    if not enabled:
        return None
    return indicator_cache.lookup(key)


def indicator_cache_store(indicator_cache: Any, enabled: bool, key: Any, value: Any) -> None:
    if enabled:
        indicator_cache.store(key, value)
