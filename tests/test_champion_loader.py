from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.strategy.champion_loader import ChampionLoader


@pytest.fixture()
def champions_dir(tmp_path: Path) -> Path:
    return tmp_path / "champions"


def test_load_fallback_to_baseline(champions_dir: Path) -> None:
    loader = ChampionLoader(champions_dir=champions_dir)
    cfg = loader.load("tTEST", "1h")
    assert cfg.config["htf_exit_config"]["enable_partials"] is True
    assert cfg.source.startswith("baseline")


def test_load_champion_file(champions_dir: Path) -> None:
    loader = ChampionLoader(champions_dir=champions_dir)
    champions_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "parameters": {
            "thresholds": {"entry_conf_overall": 0.55},
            "meta": {"note": "local"},
        }
    }
    path = champions_dir / "tTEST_1h.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    cfg = loader.load("tTEST", "1h")
    assert cfg.config["thresholds"]["entry_conf_overall"] == 0.55
    assert cfg.source.endswith("tTEST_1h.json")


def test_load_cached(champions_dir: Path) -> None:
    loader = ChampionLoader(champions_dir=champions_dir)
    cfg1 = loader.load("tTEST", "1h")
    cfg2 = loader.load_cached("tTEST", "1h")
    assert cfg1.checksum == cfg2.checksum


def test_load_reload_on_change(champions_dir: Path, tmp_path: Path) -> None:
    loader = ChampionLoader(champions_dir=champions_dir)
    champions_dir.mkdir(parents=True, exist_ok=True)
    path = champions_dir / "tTEST_1h.json"
    path.write_text(
        json.dumps({"parameters": {"thresholds": {"entry_conf_overall": 0.5}}}),
        encoding="utf-8",
    )
    loader.load("tTEST", "1h")
    path.write_text(
        json.dumps({"parameters": {"thresholds": {"entry_conf_overall": 0.6}}}),
        encoding="utf-8",
    )
    reloaded = loader.load_cached("tTEST", "1h")
    assert reloaded.config["thresholds"]["entry_conf_overall"] == 0.6
