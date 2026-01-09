from __future__ import annotations

import os

from core.pipeline import GenesisPipeline


def test_pipeline_enforces_canonical_mode_by_default(monkeypatch):
    """Canonical policy: unless explicitly requested, enforce 1/1.

    This prevents sticky shells/env from accidentally running quality decisions in 0/0.
    """

    # Simulate a "sticky" non-canonical environment from a previous debug run.
    monkeypatch.setenv("GENESIS_FAST_WINDOW", "0")
    monkeypatch.setenv("GENESIS_PRECOMPUTE_FEATURES", "0")
    monkeypatch.delenv("GENESIS_MODE_EXPLICIT", raising=False)

    pipeline = GenesisPipeline()
    pipeline.setup_environment(seed=42)

    assert os.environ.get("GENESIS_FAST_WINDOW") == "1"
    assert os.environ.get("GENESIS_PRECOMPUTE_FEATURES") == "1"


def test_pipeline_respects_explicit_debug_mode(monkeypatch):
    """If caller explicitly requests a non-canonical mode, don't override it."""

    monkeypatch.setenv("GENESIS_FAST_WINDOW", "0")
    monkeypatch.setenv("GENESIS_PRECOMPUTE_FEATURES", "0")
    monkeypatch.setenv("GENESIS_MODE_EXPLICIT", "1")

    pipeline = GenesisPipeline()
    pipeline.setup_environment(seed=42)

    assert os.environ.get("GENESIS_FAST_WINDOW") == "0"
    assert os.environ.get("GENESIS_PRECOMPUTE_FEATURES") == "0"
