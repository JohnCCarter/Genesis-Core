from __future__ import annotations

from collections import OrderedDict
from typing import Any

CacheResult = tuple[dict[str, float], dict[str, Any]]


def feature_result_cache_lookup(cache: OrderedDict[str, CacheResult], cache_key: str):
    if cache_key not in cache:
        return None
    value = cache[cache_key]
    try:
        cache.move_to_end(cache_key)
    except Exception:  # nosec B110
        pass
    return value


def feature_result_cache_store(
    cache: OrderedDict[str, CacheResult],
    cache_key: str,
    result: CacheResult,
    max_cache_size: int,
) -> None:
    cache[cache_key] = result
    cache.move_to_end(cache_key)
    try:
        while len(cache) > max_cache_size:
            cache.popitem(last=False)
    except Exception:
        if len(cache) > max_cache_size:
            cache.pop(next(iter(cache)))
