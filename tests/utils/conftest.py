from __future__ import annotations

from collections.abc import Iterator

import pytest

import core.indicators.htf_fibonacci as htf
import core.indicators.htf_fibonacci_data as htf_data


@pytest.fixture(autouse=True)
def _isolate_htf_fibonacci_caches() -> Iterator[None]:
    """Reset HTF module caches around each utils test to avoid order dependence."""
    htf._htf_context_cache.clear()
    htf_data._candles_cache.clear()
    yield
    htf._htf_context_cache.clear()
    htf_data._candles_cache.clear()
