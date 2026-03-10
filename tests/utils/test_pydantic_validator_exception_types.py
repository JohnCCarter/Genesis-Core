from __future__ import annotations

import pytest
from pydantic import ValidationError

from core.config.schema import FeaturePercentileRange, Risk, SignalAdaptationZone, Thresholds


def test_regime_proba_invalid_type_raises_validation_error() -> None:
    with pytest.raises(ValidationError):
        Thresholds.model_validate({"regime_proba": []})


def test_regime_proba_invalid_dict_value_raises_validation_error_not_typeerror() -> None:
    with pytest.raises(ValidationError):
        SignalAdaptationZone.model_validate(
            {"entry_conf_overall": 0.3, "regime_proba": {"balanced": object()}}
        )


def test_risk_map_bad_item_shape_raises_validation_error() -> None:
    with pytest.raises(ValidationError):
        Risk.model_validate({"risk_map": [(0.6,)]})


def test_percentile_bounds_bad_type_raises_validation_error() -> None:
    with pytest.raises(ValidationError):
        FeaturePercentileRange.model_validate({"low": object(), "high": 1.0})
