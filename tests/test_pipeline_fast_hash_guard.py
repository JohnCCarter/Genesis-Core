import os


def test_pipeline_forces_fast_hash_off_in_canonical_mode(monkeypatch):
    # Avoid loading any local .env in tests (developer convenience only).
    import core.pipeline as pipeline_mod

    monkeypatch.setattr(pipeline_mod, "load_dotenv", None)

    from core.pipeline import GenesisPipeline

    monkeypatch.setenv("GENESIS_MODE_EXPLICIT", "0")
    monkeypatch.setenv("GENESIS_FAST_HASH", "1")
    monkeypatch.setenv("GENESIS_RANDOM_SEED", "42")

    GenesisPipeline().setup_environment(seed=42)

    assert os.environ.get("GENESIS_FAST_HASH") == "0"


def test_pipeline_forces_fast_hash_off_in_canonical_mode_case_insensitive(monkeypatch):
    # Avoid loading any local .env in tests (developer convenience only).
    import core.pipeline as pipeline_mod

    monkeypatch.setattr(pipeline_mod, "load_dotenv", None)

    from core.pipeline import GenesisPipeline

    monkeypatch.setenv("GENESIS_MODE_EXPLICIT", "0")
    monkeypatch.setenv("GENESIS_FAST_HASH", "TRUE")
    monkeypatch.setenv("GENESIS_RANDOM_SEED", "42")

    GenesisPipeline().setup_environment(seed=42)

    assert os.environ.get("GENESIS_FAST_HASH") == "0"


def test_pipeline_allows_fast_hash_in_explicit_mode(monkeypatch):
    # Avoid loading any local .env in tests (developer convenience only).
    import core.pipeline as pipeline_mod

    monkeypatch.setattr(pipeline_mod, "load_dotenv", None)

    from core.pipeline import GenesisPipeline

    monkeypatch.setenv("GENESIS_MODE_EXPLICIT", "1")
    monkeypatch.setenv("GENESIS_FAST_HASH", "1")
    monkeypatch.setenv("GENESIS_RANDOM_SEED", "42")

    GenesisPipeline().setup_environment(seed=42)

    assert os.environ.get("GENESIS_FAST_HASH") == "1"
