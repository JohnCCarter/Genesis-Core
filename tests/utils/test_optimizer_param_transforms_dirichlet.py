from __future__ import annotations

from core.optimizer.param_transforms import (
    _DIRICHLET_MARKER,
    _apply_dirichlet_remainder,
    transform_parameters,
)


def test_dirichlet_remainder_normal() -> None:
    params = {"a": 0.3, "b": 0.3, "c": 0.2, "d": _DIRICHLET_MARKER}

    result = _apply_dirichlet_remainder(params)

    assert abs(result["d"] - 0.2) < 1e-4


def test_dirichlet_remainder_overflow_clamp() -> None:
    params = {"a": 0.5, "b": 0.5, "c": 0.3, "d": _DIRICHLET_MARKER}

    result = _apply_dirichlet_remainder(params)

    assert result["d"] == 0.01


def test_dirichlet_remainder_underflow_clamp() -> None:
    params = {"a": 0.01, "b": 0.01, "c": _DIRICHLET_MARKER}

    result = _apply_dirichlet_remainder(params)

    assert result["c"] == 0.9


def test_dirichlet_no_marker_noop() -> None:
    params = {"a": 0.5, "b": 0.3}

    result = _apply_dirichlet_remainder(params)

    assert result == {"a": 0.5, "b": 0.3}


def test_dirichlet_nested() -> None:
    params = {"weights": {"a": 0.3, "b": 0.4, "c": _DIRICHLET_MARKER}, "other": 42}

    result = _apply_dirichlet_remainder(params)

    assert abs(result["weights"]["c"] - 0.3) < 1e-4
    assert result["other"] == 42


def test_dirichlet_integration_with_transform() -> None:
    raw = {
        "multi_timeframe.regime_intelligence.clarity_score.weights.confidence": 0.3,
        "multi_timeframe.regime_intelligence.clarity_score.weights.edge": 0.25,
        "multi_timeframe.regime_intelligence.clarity_score.weights.ev": 0.2,
        "multi_timeframe.regime_intelligence.clarity_score.weights.regime_alignment": _DIRICHLET_MARKER,
    }

    params, _ = transform_parameters(raw)
    weights = params["multi_timeframe"]["regime_intelligence"]["clarity_score"]["weights"]

    assert abs(weights["regime_alignment"] - 0.25) < 1e-4
    assert (
        abs(
            weights["confidence"]
            + weights["edge"]
            + weights["ev"]
            + weights["regime_alignment"]
            - 1.0
        )
        < 1e-3
    )
