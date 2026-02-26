import os

import core.pipeline as pipeline_mod
from core.observability.metrics import PIPELINE_COMPONENT_ORDER, pipeline_component_order_hash


def test_pipeline_forces_fast_hash_off_in_canonical_mode(monkeypatch):
    # Avoid loading any local .env in tests (developer convenience only).
    monkeypatch.setattr(pipeline_mod, "load_dotenv", None)

    monkeypatch.setenv("GENESIS_MODE_EXPLICIT", "0")
    monkeypatch.setenv("GENESIS_FAST_HASH", "1")
    monkeypatch.setenv("GENESIS_RANDOM_SEED", "42")

    pipeline_mod.GenesisPipeline().setup_environment(seed=42)

    assert os.environ.get("GENESIS_FAST_HASH") == "0"


def test_pipeline_forces_fast_hash_off_in_canonical_mode_case_insensitive(monkeypatch):
    # Avoid loading any local .env in tests (developer convenience only).
    monkeypatch.setattr(pipeline_mod, "load_dotenv", None)

    monkeypatch.setenv("GENESIS_MODE_EXPLICIT", "0")
    monkeypatch.setenv("GENESIS_FAST_HASH", "TRUE")
    monkeypatch.setenv("GENESIS_RANDOM_SEED", "42")

    pipeline_mod.GenesisPipeline().setup_environment(seed=42)

    assert os.environ.get("GENESIS_FAST_HASH") == "0"


def test_pipeline_allows_fast_hash_in_explicit_mode(monkeypatch):
    # Avoid loading any local .env in tests (developer convenience only).
    monkeypatch.setattr(pipeline_mod, "load_dotenv", None)

    monkeypatch.setenv("GENESIS_MODE_EXPLICIT", "1")
    monkeypatch.setenv("GENESIS_FAST_HASH", "1")
    monkeypatch.setenv("GENESIS_RANDOM_SEED", "42")

    pipeline_mod.GenesisPipeline().setup_environment(seed=42)

    assert os.environ.get("GENESIS_FAST_HASH") == "1"


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
