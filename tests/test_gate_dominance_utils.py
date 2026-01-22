from __future__ import annotations

from scripts.analyze_gate_dominance import _percentile, select_blocker_reason


def test_select_blocker_reason_prefers_last_non_zone() -> None:
    reasons = ["ZONE:base@0.700", "EV_NEG", "HTF_FIB_UNAVAILABLE"]
    blocker, had_zone = select_blocker_reason(reasons)
    assert blocker == "HTF_FIB_UNAVAILABLE"
    assert had_zone is True


def test_select_blocker_reason_falls_back_to_zone_when_only_zone() -> None:
    reasons = ["ZONE:mid@0.280"]
    blocker, had_zone = select_blocker_reason(reasons)
    assert blocker == "ZONE:mid@0.280"
    assert had_zone is True


def test_select_blocker_reason_empty() -> None:
    blocker, had_zone = select_blocker_reason([])
    assert blocker == "NO_REASON"
    assert had_zone is False


def test_percentile_basic() -> None:
    vals = [1, 2, 3, 4, 5]
    assert _percentile(vals, 0.0) == 1
    assert _percentile(vals, 1.0) == 5
    # With the current rounding scheme, p95 should hit the max for small lists
    assert _percentile(vals, 0.95) == 5
