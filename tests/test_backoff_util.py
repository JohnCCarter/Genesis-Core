from __future__ import annotations


from core.utils.backoff import exponential_backoff_delay


def test_backoff_monotonic_bounded():
    d1 = exponential_backoff_delay(1, base_delay=0.5, max_backoff=1.0)
    d3 = exponential_backoff_delay(3, base_delay=0.5, max_backoff=1.0)
    d6 = exponential_backoff_delay(6, base_delay=0.5, max_backoff=1.0)
    assert 0.1 <= d1 <= 1.5
    assert d3 <= 1.5
    assert d6 <= 1.6
