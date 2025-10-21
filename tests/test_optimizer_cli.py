from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import optimizer
from scripts.optimizer import summarize_run


@pytest.fixture()
def run_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "results" / "hparam_search" / "run_test"
    root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(optimizer, "RESULTS_DIR", root.parent)
    (root / "run_meta.json").write_text(
        json.dumps(
            {
                "run_id": "run_test",
                "symbol": "tTEST",
                "timeframe": "1h",
                "snapshot_id": "test_snapshot",
                "git_commit": "abc123",
            }
        ),
        encoding="utf-8",
    )
    payload = {
        "trial_id": "trial_001",
        "parameters": {"thresholds": {"entry_conf_overall": 0.4}},
        "score": {
            "score": 125.0,
            "metrics": {
                "sharpe_ratio": 0.6,
                "total_return": 12.3,
                "profit_factor": 1.8,
                "num_trades": 45,
            },
            "hard_failures": [],
        },
        "constraints": {"ok": True},
        "results_path": "test.json",
    }
    (root / "trial_001.json").write_text(json.dumps(payload), encoding="utf-8")
    return root


def test_summarize_run(run_dir: Path) -> None:
    summary = summarize_run("run_test")
    assert summary["meta"]["symbol"] == "tTEST"
    assert summary["counts"]["total"] == 1
    assert summary["best_trial"]["trial_id"] == "trial_001"
