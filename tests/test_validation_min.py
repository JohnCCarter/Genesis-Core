from __future__ import annotations

from core.strategy.validation import brier_score, log_loss


def test_brier_and_logloss_basic():
    probs = [(0.7, 0.2, 0.1), (0.1, 0.8, 0.1), (0.2, 0.2, 0.6)]
    labels = ["buy", "sell", "hold"]
    b = brier_score(probs, labels)
    ll = log_loss(probs, labels)
    assert 0.0 <= b <= 2.0
    assert ll >= 0.0
