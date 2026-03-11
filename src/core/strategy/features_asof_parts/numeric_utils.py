from __future__ import annotations


def clip_feature_value(x: float, lo: float, hi: float) -> float:
    if x != x:
        return 0.0
    return max(lo, min(hi, x))
