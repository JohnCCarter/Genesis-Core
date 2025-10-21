from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
import yaml

from core.optimizer.runner import run_optimizer


@pytest.fixture()
def search_config_tmp(tmp_path: Path) -> Path:
    config = {
        "meta": {
            "symbol": "tTEST",
            "timeframe": "1h",
            "snapshot_id": "tTEST_1h_20240101_20240201_v1",
            "warmup_bars": 50,
            "runs": {
                "max_trials": 2,
                "resume": False,
            },
        },
        "parameters": {
            "thresholds": {
                "entry_conf_overall": {
                    "type": "grid",
                    "values": [0.4, 0.5],
                }
            }
        },
    }
    config_path = tmp_path / "search.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    return config_path


def test_run_optimizer_updates_champion(tmp_path: Path, search_config_tmp: Path) -> None:
    results_root = tmp_path / "results" / "hparam_search"
    run_meta_payload = {
        "git_commit": "abc123",
        "snapshot_id": "tTEST_1h_20240101_20240201_v1",
    }

    trial_queue = {
        1: {
            "trial_id": "trial_001",
            "parameters": {"thresholds": {"entry_conf_overall": 0.4}},
            "score": {
                "score": 120.0,
                "metrics": {"sharpe_ratio": 0.5},
                "hard_failures": [],
            },
            "constraints": {"ok": True, "reasons": []},
            "results_path": "test_results.json",
        },
        2: {
            "trial_id": "trial_002",
            "parameters": {"thresholds": {"entry_conf_overall": 0.5}},
            "score": {
                "score": 80.0,
                "metrics": {"sharpe_ratio": 0.2},
                "hard_failures": ["MAX_DD_TOO_HIGH"],
            },
            "constraints": {"ok": False, "reasons": ["MAX_DD_TOO_HIGH"]},
            "results_path": "test_results_bad.json",
        },
    }

    def fake_run_trial(*args: Any, **kwargs: Any) -> dict[str, Any]:
        index = kwargs.get("index")
        return trial_queue.get(
            index,
            {
                "trial_id": f"trial_extra_{index}",
                "parameters": {},
                "score": {"score": 0.0, "metrics": {}, "hard_failures": []},
                "constraints": {"ok": False},
            },
        )

    def fake_ensure(run_dir: Path, *_args: Any, **_kwargs: Any) -> None:
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "run_meta.json").write_text(json.dumps(run_meta_payload), encoding="utf-8")

    with (
        patch("core.optimizer.runner.RESULTS_DIR", results_root),
        patch(
            "core.optimizer.runner.expand_parameters",
            return_value=[
                {"thresholds": {"entry_conf_overall": 0.4}},
                {"thresholds": {"entry_conf_overall": 0.5}},
            ],
        ),
        patch("core.optimizer.runner.run_trial", side_effect=fake_run_trial),
        patch("core.optimizer.runner._ensure_run_metadata", side_effect=fake_ensure),
        patch("core.optimizer.runner.ChampionManager") as manager_cls,
        patch("core.strategy.champion_loader.CHAMPIONS_DIR", tmp_path / "champions"),
    ):
        manager_instance = manager_cls.return_value
        manager_instance.load_current.return_value = None
        manager_instance.should_replace.return_value = True

        results = run_optimizer(search_config_tmp, run_id="run_test")

        assert len(results) == 2
        manager_instance.write_champion.assert_called_once()
        call_kwargs = manager_instance.write_champion.call_args.kwargs
        assert call_kwargs["run_id"] == "run_test"
        assert call_kwargs["candidate"].score == pytest.approx(120.0)
        assert call_kwargs["snapshot_id"] == run_meta_payload["snapshot_id"]
