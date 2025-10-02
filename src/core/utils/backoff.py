from __future__ import annotations

import secrets


def exponential_backoff_delay(
    attempt: int,
    *,
    base_delay: float = 0.5,
    max_backoff: float = 10.0,
    jitter_min_ms: int = 100,
    jitter_max_ms: int = 400,
) -> float:
    """Beräkna liten exponentiell backoff med säker jitter.

    - attempt: 1-baserat försök (1,2,3...); clampas till >= 0 i exponent.
    - base_delay: grundfördröjning som exponentieras och clampas mot max_backoff.
    - max_backoff: översta taket för fördröjning.
    - jitter: läggs på i millisekunder, [jitter_min_ms, jitter_max_ms].
    """
    if attempt < 0:
        attempt = 0
    base = min(base_delay * (2**attempt), max_backoff)
    jitter = (
        jitter_min_ms + secrets.randbelow(max(1, (jitter_max_ms - jitter_min_ms + 1)))
    ) / 1000.0
    delay = base + jitter
    # tillåt lite spill över max_backoff för jitter
    return min(delay, max_backoff + 0.5)
