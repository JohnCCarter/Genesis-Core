from __future__ import annotations

from typing import Any


def remap_precomputed_features(
    pre: dict[str, Any], window_start_idx: int, lookup_idx: int
) -> tuple[dict[str, Any], int]:
    """Remappa precompute till lokalt fönster när backtestet startar mitt i historiken.

    Returnerar (remappad_pre, remappat_lookup_idx). Vid fel återgår vi till tom pre
    och behåller original-index så att slow path tar över.
    """
    if not pre or window_start_idx <= 0:
        return pre, lookup_idx

    try:
        local_lookup_idx = lookup_idx - window_start_idx
        if local_lookup_idx < 0:
            return {}, lookup_idx

        remapped: dict[str, Any] = {}
        # Standardserier: klipp bort prefixet före window_start_idx
        for key, val in pre.items():
            if isinstance(val, list | tuple):
                if len(val) <= window_start_idx:
                    continue
                remapped[key] = list(val[window_start_idx:])
            else:
                remapped[key] = val

        # Remappa fib-svängar (behåll endast de som finns inom fönstret och offset:a index)
        def _remap_swings(idx_key: str, px_key: str) -> None:
            idxs = pre.get(idx_key)
            pxs = pre.get(px_key)
            if not (isinstance(idxs, list | tuple) and isinstance(pxs, list | tuple)):
                return
            new_idx: list[int] = []
            new_px: list[float] = []
            for i, p in zip(idxs, pxs, strict=False):
                try:
                    if i < window_start_idx:
                        continue
                    new_idx.append(int(i - window_start_idx))
                    new_px.append(float(p))
                except (TypeError, ValueError):
                    continue
            if new_idx and len(new_idx) == len(new_px):
                remapped[idx_key] = new_idx
                remapped[px_key] = new_px

        _remap_swings("fib_high_idx", "fib_high_px")
        _remap_swings("fib_low_idx", "fib_low_px")

        return remapped, local_lookup_idx
    except Exception:
        return {}, lookup_idx
