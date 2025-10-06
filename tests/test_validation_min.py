from __future__ import annotations

from core.strategy.validation import brier_score, ks_statistic, log_loss, psi


def test_brier_and_logloss_basic():
    probs = [(0.7, 0.2, 0.1), (0.1, 0.8, 0.1), (0.2, 0.2, 0.6)]
    labels = ["buy", "sell", "hold"]
    b = brier_score(probs, labels)
    ll = log_loss(probs, labels)
    assert 0.0 <= b <= 2.0
    assert ll >= 0.0


def test_psi_and_ks_basic():
    exp = [0.1, 0.2, 0.3, 0.4, 0.5]
    act = [0.15, 0.25, 0.35, 0.45, 0.55]
    p = psi(exp, act, bins=5)
    k = ks_statistic(exp, act)
    assert p >= 0.0
    assert 0.0 <= k <= 1.0
