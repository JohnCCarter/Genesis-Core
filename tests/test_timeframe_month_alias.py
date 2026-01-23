from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.strategy.model_registry import ModelRegistry
from core.utils import get_candles_path, is_case_sensitive_directory


def test_get_candles_path_accepts_1M_and_1mo_aliases(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    candles_dir = Path("data/curated/v1/candles")
    candles_dir.mkdir(parents=True, exist_ok=True)

    expected = candles_dir / "tBTCUSD_1mo.parquet"
    expected.write_bytes(b"")

    assert get_candles_path("tBTCUSD", "1M") == expected
    assert get_candles_path("tBTCUSD", "1mo") == expected


def test_get_candles_path_falls_back_to_legacy_1M_only_on_case_sensitive_fs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    candles_dir = Path("data/curated/v1/candles")
    candles_dir.mkdir(parents=True, exist_ok=True)

    # Only create the legacy/Bitfinex-style filename.
    legacy = candles_dir / "tBTCUSD_1M.parquet"
    legacy.write_bytes(b"")

    if not is_case_sensitive_directory(Path("data")):
        pytest.skip("Case-insensitive filesystem: 1M filename is unsafe / aliases to 1m")

    assert get_candles_path("tBTCUSD", "1M") == legacy
    assert get_candles_path("tBTCUSD", "1mo") == legacy


def test_model_registry_monthly_never_aliases_to_minute_model(tmp_path: Path) -> None:
    root = tmp_path
    models_dir = root / "config" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    # Simulate a real Windows/macOS repo: minute model exists, monthly model uses 1mo.
    minute_model = {
        "schema": ["minute"],
        "buy": {"w": [0.0], "b": 0.0},
        "sell": {"w": [0.0], "b": 0.0},
    }
    month_model = {
        "schema": ["month"],
        "buy": {"w": [1.0], "b": 1.0},
        "sell": {"w": [1.0], "b": 1.0},
    }

    (models_dir / "tBTCUSD_1m.json").write_text(json.dumps(minute_model), encoding="utf-8")
    (models_dir / "tBTCUSD_1mo.json").write_text(json.dumps(month_model), encoding="utf-8")

    # Registry still uses the Bitfinex timeframe key and an unsafe filename.
    registry = {"tBTCUSD:1M": {"champion": "config/models/tBTCUSD_1M.json"}}
    (models_dir / "registry.json").write_text(json.dumps(registry), encoding="utf-8")

    reg = ModelRegistry(root=root)

    assert reg.get_meta("tBTCUSD", "1M") == month_model
    assert reg.get_meta("tBTCUSD", "1mo") == month_model

    # Safety regression: asking for monthly must NOT silently fall back to 1m.
    (models_dir / "tBTCUSD_1mo.json").unlink()
    reg.clear_cache()
    assert reg.get_meta("tBTCUSD", "1M") is None


def test_model_registry_warns_on_unsafe_month_paths_on_case_insensitive_fs(
    tmp_path: Path, caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Force case-insensitive behavior for the models directory.
    monkeypatch.setattr(
        "core.strategy.model_registry.is_case_sensitive_directory",
        lambda _p: False,
    )

    root = tmp_path
    models_dir = root / "config" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    registry = {"tBTCUSD:1M": {"champion": "config/models/tBTCUSD_1M.json"}}
    (models_dir / "registry.json").write_text(json.dumps(registry), encoding="utf-8")

    caplog.set_level("WARNING")
    reg = ModelRegistry(root=root)
    _ = reg.get_meta("tBTCUSD", "1M")

    assert any(
        "unsafe" in rec.message.lower() and "_1m.json" in rec.message for rec in caplog.records
    )
