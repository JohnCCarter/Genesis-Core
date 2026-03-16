from __future__ import annotations

from core.intelligence.regime.contracts import (
    ClarityClamp,
    ClarityScoreComponents,
    ClarityScoreRequest,
    ClarityScoreResult,
    ShadowRegimeObservability,
)


def test_clarity_score_request_preserves_legacy_inputs() -> None:
    request = ClarityScoreRequest.from_legacy_inputs(
        confidence_gate=0.505,
        edge=0.6,
        max_ev=0.25,
        r_default=1.0,
        candidate="LONG",
        regime="bull",
        weights={"confidence": "0.5", "edge": None, "ev": -5, "regime_alignment": 1},
    )

    assert request.confidence_gate == 0.505
    assert request.edge == 0.6
    assert request.max_ev == 0.25
    assert request.r_default == 1.0
    assert request.candidate == "LONG"
    assert request.regime == "bull"
    assert request.weights == {
        "confidence": "0.5",
        "edge": None,
        "ev": -5,
        "regime_alignment": 1,
    }


def test_clarity_score_result_to_legacy_payload_preserves_shape() -> None:
    result = ClarityScoreResult(
        components=ClarityScoreComponents(
            confidence=0.5,
            edge=0.2,
            ev=0.2,
            regime_alignment=0.1,
        ),
        weights={"confidence": 0.5, "edge": 0.2, "ev": 0.2, "regime_alignment": 0.1},
        weights_version="weights_v1",
        clarity_raw=0.5,
        clarity_scaled=50.0,
        clarity_score=50,
        clamp=ClarityClamp(),
    )

    payload = result.to_legacy_payload()

    assert tuple(payload.keys()) == (
        "components",
        "weights",
        "weights_version",
        "clarity_raw",
        "clarity_scaled",
        "clarity_score",
        "round_policy",
        "clamp",
    )
    assert payload["round_policy"] == "half_even"
    assert payload["clamp"] == {"min": 0.0, "max": 100.0}


def test_shadow_regime_observability_roundtrip_preserves_shape() -> None:
    payload = {
        "authoritative_source": "regime_unified.detect_regime_unified",
        "shadow_source": "regime.detect_regime_from_candles",
        "authority_mode": "legacy",
        "authority_mode_source": "default_legacy",
        "authority": "ranging",
        "shadow": "bull",
        "mismatch": True,
        "decision_input": False,
    }

    contract = ShadowRegimeObservability.from_payload(payload)

    assert contract.to_payload() == payload
    assert tuple(contract.to_payload().keys()) == (
        "authoritative_source",
        "shadow_source",
        "authority_mode",
        "authority_mode_source",
        "authority",
        "shadow",
        "mismatch",
        "decision_input",
    )
    assert contract.expected_evidence_file_names() == (
        "clarity_histogram.json",
        "clarity_quantiles.json",
        "shadow_samples.ndjson",
    )
