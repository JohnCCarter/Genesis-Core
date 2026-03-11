from __future__ import annotations

from typing import Any


def log_precompute_status(
    already_logged: bool,
    logger: Any,
    use_precompute: bool,
    pre: dict[str, Any],
    lookup_idx: int,
    window_start_idx: int,
) -> bool:
    """Log once about whether precompute data is available and return updated log state."""
    if already_logged or not logger:
        return already_logged
    try:
        keys_sample = sorted(pre.keys())[:10]
    except Exception:
        keys_sample = []
    logger.debug(
        "precompute_status use_precompute=%s lookup_idx=%s window_start_idx=%s pre_keys=%s",
        use_precompute,
        lookup_idx,
        window_start_idx,
        keys_sample,
    )
    return True
