from __future__ import annotations

import json
from pathlib import Path

from core.strategy.model_registry import ModelRegistry


def test_registry_reads_champion(tmp_path: Path):
    root = tmp_path
    models = root / "config" / "models"
    models.mkdir(parents=True, exist_ok=True)
    # Skriv enkel model JSON
    champ = models / "tBTCUSD_1m.json"
    champ.write_text(
        json.dumps(
            {
                "schema": ["ema", "rsi"],
                "buy": {"w": [1, 0], "b": 0},
                "sell": {"w": [-1, 0], "b": 0},
            }
        ),
        encoding="utf-8",
    )
    # Registry
    reg = models / "registry.json"
    reg.write_text(json.dumps({"tBTCUSD:1m": {"champion": str(champ)}}), encoding="utf-8")

    r = ModelRegistry(root=root, registry_path=reg)
    meta = r.get_meta("tBTCUSD", "1m")
    assert meta and meta.get("schema") == ["ema", "rsi"]


def test_registry_fallback_to_candidate(tmp_path: Path):
    root = tmp_path
    models = root / "config" / "models"
    models.mkdir(parents=True, exist_ok=True)
    # Ingen registry-post, bara kandidatfil
    cand = models / "tETHUSD_1m.json"
    cand.write_text(
        json.dumps(
            {
                "schema": ["ema"],
                "buy": {"w": [0.5], "b": 0},
                "sell": {"w": [-0.5], "b": 0},
            }
        ),
        encoding="utf-8",
    )

    r = ModelRegistry(root=root)
    meta = r.get_meta("tETHUSD", "1m")
    assert meta and meta.get("schema") == ["ema"]
