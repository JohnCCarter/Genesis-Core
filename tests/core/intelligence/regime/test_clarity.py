from __future__ import annotations

import pytest

from core.intelligence.regime.clarity import compute_clarity_score_v1


def test_compute_clarity_score_v1_preserves_known_half_even_case() -> None:
    result = compute_clarity_score_v1(
        confidence_gate=0.505,
        edge=0.6,
        max_ev=0.6,
        r_default=1.0,
        candidate="LONG",
        regime="bull",
        weights={
            "confidence": 1.0,
            "edge": 0.0,
            "ev": 0.0,
            "regime_alignment": 0.0,
        },
    )

    assert result.clarity_raw == pytest.approx(0.505)
    assert result.clarity_scaled == pytest.approx(50.5)
    assert result.clarity_score == 50
    assert result.round_policy == "half_even"


def test_compute_clarity_score_v1_normalizes_weights_permissively() -> None:
    result = compute_clarity_score_v1(
        confidence_gate=0.8,
        edge=0.3,
        max_ev=0.4,
        r_default=1.0,
        candidate="short",
        regime="bear",
        weights={"confidence": "2.0", "edge": None, "ev": -5, "regime_alignment": 2},
    )

    assert result.weights == {
        "confidence": pytest.approx(0.5),
        "edge": pytest.approx(0.0),
        "ev": pytest.approx(0.0),
        "regime_alignment": pytest.approx(0.5),
    }
    assert result.components.regime_alignment == pytest.approx(1.0)


def test_clarity_result_emits_expected_legacy_payload_shape() -> None:
    kwargs = {
        "confidence_gate": 0.505,
        "edge": 0.1,
        "max_ev": 0.25,
        "r_default": 1.0,
        "candidate": "LONG",
        "regime": "balanced",
        "weights": {
            "confidence": "0.5",
            "edge": None,
            "ev": -1,
            "regime_alignment": "0.5",
        },
        "weights_version": "weights_v1",
    }

    result = compute_clarity_score_v1(**kwargs)
    legacy_payload = result.to_legacy_payload()

    assert legacy_payload == result.to_legacy_payload()
