from __future__ import annotations

import os
import random

import numpy as np
import pytest

from core.utils.random_seeds import set_global_seeds as set_seed_helper

optuna_helpers = pytest.importorskip("core.utils.optuna_helpers")


def _sample_rng_payload(seed_setter) -> dict[str, object]:
    seed_setter(123)
    payload: dict[str, object] = {
        "python": random.random(),
        "numpy": float(np.random.random()),
        "pythonhashseed": os.environ.get("PYTHONHASHSEED"),
    }

    try:
        import torch

        payload["torch_available"] = True
        payload["torch"] = float(torch.rand(1).item())
        payload["cudnn_deterministic"] = bool(torch.backends.cudnn.deterministic)
        payload["cudnn_benchmark"] = bool(torch.backends.cudnn.benchmark)
    except (ImportError, OSError):
        payload["torch_available"] = False

    return payload


def test_set_global_seeds_matches_optuna_helper_behavior() -> None:
    legacy_payload = _sample_rng_payload(optuna_helpers.set_global_seeds)
    helper_payload = _sample_rng_payload(set_seed_helper)

    assert helper_payload == legacy_payload
