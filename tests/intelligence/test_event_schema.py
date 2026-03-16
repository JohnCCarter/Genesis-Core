from __future__ import annotations

import pytest

from core.intelligence.collection.interface import CollectionRequest, IntelligenceCollector
from core.intelligence.evaluation.interface import (
    EvaluationRequest,
    IntelligenceEvaluation,
    IntelligenceEvaluator,
)
from core.intelligence.events.models import IntelligenceEvent, IntelligenceReference
from core.intelligence.events.validators import (
    IntelligenceEventValidationError,
    validate_intelligence_event,
    validate_intelligence_payload,
)
from core.intelligence.features.interface import (
    FeatureExtractionRequest,
    IntelligenceFeatureExtractor,
    IntelligenceFeatureSet,
)
from core.intelligence.ledger_adapter.interface import (
    IntelligenceLedgerAdapter,
    LedgerPersistenceRequest,
    LedgerPersistenceResult,
)
from core.intelligence.normalization.interface import (
    IntelligenceNormalizer,
    NormalizationRequest,
)


def _event() -> IntelligenceEvent:
    return IntelligenceEvent(
        event_id="intel-tbtcusd-20260316-0001",
        source="regime_intelligence",
        timestamp="2026-03-16T12:00:00+00:00",
        asset="tBTCUSD",
        topic="regime",
        signal_type="observation",
        confidence=0.85,
        references=(IntelligenceReference(kind="artifact", ref="ART-2026-0001", label="primary"),),
        summary="Deterministic regime event.",
    )


def test_intelligence_event_serialization_is_deterministic() -> None:
    event = _event()

    first = event.to_json()
    second = event.to_json()

    assert first == second
    assert first.endswith("\n")
    assert '"event_id": "intel-tbtcusd-20260316-0001"' in first


def test_validate_intelligence_event_accepts_valid_event() -> None:
    validated = validate_intelligence_event(_event())

    assert validated.event.event_id == "intel-tbtcusd-20260316-0001"
    assert validated.validator_version == "intelligence_event.v1"


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({**_event().to_payload(), "source": ""}, "source must be non-empty"),
        ({**_event().to_payload(), "timestamp": "2026-03-16T12:00:00"}, "timezone"),
        ({**_event().to_payload(), "confidence": 1.5}, "confidence must be between 0.0 and 1.0"),
        (
            {
                **_event().to_payload(),
                "references": [{"kind": "artifact", "ref": ""}],
            },
            r"references\[0\]\.ref must be non-empty",
        ),
    ],
)
def test_validate_intelligence_payload_rejects_invalid_payload(
    payload: dict[str, object],
    message: str,
) -> None:
    with pytest.raises(IntelligenceEventValidationError, match=message):
        validate_intelligence_payload(payload)


def test_interface_surfaces_import_smoke() -> None:
    assert CollectionRequest.__name__ == "CollectionRequest"
    assert IntelligenceCollector.__name__ == "IntelligenceCollector"
    assert NormalizationRequest.__name__ == "NormalizationRequest"
    assert IntelligenceNormalizer.__name__ == "IntelligenceNormalizer"
    assert FeatureExtractionRequest.__name__ == "FeatureExtractionRequest"
    assert IntelligenceFeatureSet.__name__ == "IntelligenceFeatureSet"
    assert IntelligenceFeatureExtractor.__name__ == "IntelligenceFeatureExtractor"
    assert EvaluationRequest.__name__ == "EvaluationRequest"
    assert IntelligenceEvaluation.__name__ == "IntelligenceEvaluation"
    assert IntelligenceEvaluator.__name__ == "IntelligenceEvaluator"
    assert LedgerPersistenceRequest.__name__ == "LedgerPersistenceRequest"
    assert LedgerPersistenceResult.__name__ == "LedgerPersistenceResult"
    assert IntelligenceLedgerAdapter.__name__ == "IntelligenceLedgerAdapter"
