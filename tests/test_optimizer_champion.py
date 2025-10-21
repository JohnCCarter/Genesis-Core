"""Tester för champion-hantering."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.optimizer.champion import ChampionCandidate, ChampionManager


@pytest.fixture()
def tmp_champion_dir(tmp_path: Path) -> Path:
    return tmp_path / "champions"


def _make_candidate(score: float, *, ok: bool = True) -> ChampionCandidate:
    return ChampionCandidate(
        parameters={"foo": "bar"},
        score=score,
        metrics={"sharpe_ratio": 1.23},
        constraints_ok=ok,
        constraints={"ok": ok},
        hard_failures=[],
        trial_id="trial_001",
        results_path="results/backtests/example.json",
    )


def test_should_replace_accepts_better_candidate(tmp_champion_dir: Path) -> None:
    manager = ChampionManager(champions_dir=tmp_champion_dir)
    current = manager.write_champion(
        symbol="tTEST",
        timeframe="1h",
        candidate=_make_candidate(100.0),
        run_id="run_1",
        git_commit="abc123",
        snapshot_id="snapshot_v1",
    )

    better = _make_candidate(120.0)

    assert manager.should_replace(current, better) is True


def test_should_replace_rejects_constraint_failure(tmp_champion_dir: Path) -> None:
    manager = ChampionManager(champions_dir=tmp_champion_dir)
    current = None
    failing = ChampionCandidate(
        parameters={},
        score=200.0,
        metrics={},
        constraints_ok=False,
        constraints={"ok": False},
        hard_failures=["MAX_DD_TOO_HIGH"],
        trial_id="trial_002",
        results_path="results/backtests/example.json",
    )

    assert manager.should_replace(current, failing) is False


def test_write_champion_creates_backup(tmp_champion_dir: Path) -> None:
    manager = ChampionManager(champions_dir=tmp_champion_dir)
    candidate = _make_candidate(150.0)
    manager.write_champion(
        symbol="tTEST",
        timeframe="1h",
        candidate=candidate,
        run_id="run_initial",
        git_commit="abc123",
        snapshot_id="snapshot_v1",
        run_meta={"note": "initial"},
    )

    # Update with better candidate
    better = _make_candidate(200.0)
    manager.write_champion(
        symbol="tTEST",
        timeframe="1h",
        candidate=better,
        run_id="run_updated",
        git_commit="def456",
        snapshot_id="snapshot_v2",
        run_meta={"note": "updated"},
    )

    champion_path = manager._champion_path("tTEST", "1h")
    backup_dir = manager.champions_dir / "backup"

    assert champion_path.exists()
    assert any(backup_dir.glob("tTEST_1h_*.json"))

    record = json.loads(champion_path.read_text(encoding="utf-8"))
    assert record["score"] == pytest.approx(200.0)
    assert record["metadata"]["run_meta"]["note"] == "updated"
