from __future__ import annotations

from core.optimizer.param_transforms import BASE_RISK_MAP, transform_parameters


def test_transform_parameters_sets_default_risk_map_when_missing() -> None:
    params, derived = transform_parameters({"risk": {}})

    assert params["risk"]["risk_map"] == [[c, s] for c, s in BASE_RISK_MAP]
    assert derived == {}


def test_transform_parameters_applies_deltas_monotonic() -> None:
    params, derived = transform_parameters(
        {
            "risk": {
                "risk_map_deltas": {
                    # Push conf_1 left of conf_0, and push sizes down/up.
                    "conf_0": 0.0,
                    "size_0": -0.01,
                    "conf_1": -0.20,
                    "size_1": 0.0,
                    "conf_2": 0.0,
                    "size_2": 0.01,
                }
            }
        }
    )

    risk_map = params["risk"]["risk_map"]
    # Sorted by confidence
    assert risk_map == sorted(risk_map, key=lambda x: x[0])

    # Sizes monotonic non-decreasing
    sizes = [p[1] for p in risk_map]
    assert sizes == sorted(sizes)

    assert derived["risk"]["risk_map"] == risk_map
