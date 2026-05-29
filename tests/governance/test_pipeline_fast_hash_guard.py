import os

import pytest

import core.pipeline as pipeline_mod
from core.observability.metrics import PIPELINE_COMPONENT_ORDER, pipeline_component_order_hash


@pytest.mark.parametrize(
    ("genesis_mode_explicit", "genesis_fast_hash", "expected_fast_hash"),
    [
        pytest.param("0", "1", "0", id="canonical-forces-off"),
        pytest.param("0", "TRUE", "0", id="canonical-forces-off-case-insensitive"),
        pytest.param("1", "1", "1", id="explicit-allows-fast-hash"),
    ],
)
def test_pipeline_fast_hash_guard(
    monkeypatch,
    genesis_mode_explicit,
    genesis_fast_hash,
    expected_fast_hash,
):
    # Avoid loading any local .env in tests (developer convenience only).
    monkeypatch.setattr(pipeline_mod, "load_dotenv", None)

    original_env = os.environ.copy()

    try:
        for key in ("GENESIS_FAST_WINDOW", "GENESIS_PRECOMPUTE_FEATURES", "PYTHONHASHSEED"):
            os.environ.pop(key, None)

        os.environ["GENESIS_MODE_EXPLICIT"] = genesis_mode_explicit
        os.environ["GENESIS_FAST_HASH"] = genesis_fast_hash
        os.environ["GENESIS_RANDOM_SEED"] = "42"

        pipeline_mod.GenesisPipeline().setup_environment(seed=42)

        assert os.environ.get("GENESIS_FAST_HASH") == expected_fast_hash
    finally:
        os.environ.clear()
        os.environ.update(original_env)


def test_pipeline_component_order_hash_contract_is_stable():
    expected_order = (
        "features",
        "proba",
        "confidence",
        "regime",
        "decision",
    )
    assert PIPELINE_COMPONENT_ORDER == expected_order
    assert pipeline_component_order_hash() == "200a25070a6f7fe4"
