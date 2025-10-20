from __future__ import annotations

import itertools
import json
import subprocess
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from core.optimizer.constraints import enforce_constraints
from core.optimizer.scoring import MetricThresholds, score_backtest

ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "results" / "hparam_search"


@dataclass(slots=True)
class TrialConfig:
    snapshot_id: str
    symbol: str
    timeframe: str
    warmup_bars: int
    parameters: dict[str, Any]


def load_search_config(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict):
        raise ValueError("search config måste vara YAML-mapp")
    return data


def expand_parameters(spec: dict[str, Any]) -> Iterable[dict[str, Any]]:
    base: dict[str, Any] = {}
    grids: list[tuple[str, list[Any]]] = []
    for key, sub in spec.items():
        if isinstance(sub, dict) and sub.get("type") == "grid":
            grids.append((key, list(sub.get("values") or [])))
        elif isinstance(sub, dict) and sub.get("type") == "fixed":
            base[key] = sub.get("value")
        else:
            base[key] = sub
    if not grids:
        yield base
        return
    keys, values = zip(*grids, strict=True)
    for combo in itertools.product(*values):
        config = dict(base)
        config.update(dict(zip(keys, combo, strict=True)))
        yield config


def run_trial(trial: TrialConfig, *, run_id: str, index: int) -> dict[str, Any]:
    output_dir = RESULTS_DIR / run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    trial_id = f"trial_{index:03d}"
    trial_file = output_dir / f"{trial_id}.json"
    cmd = [
        "python",
        "scripts/run_backtest.py",
        "--symbol",
        trial.symbol,
        "--timeframe",
        trial.timeframe,
        "--start",
        trial.snapshot_id.split("_")[2],
        "--end",
        trial.snapshot_id.split("_")[3],
        "--warmup",
        str(trial.warmup_bars),
    ]
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as proc:
        log = proc.communicate()[0]
        if proc.returncode != 0:
            return {"error": "backtest_failed", "log": log, "trial": trial.parameters}
    results_path = sorted((ROOT / "results" / "backtests").glob(f"{trial.symbol}_{trial.timeframe}_*.json"))[-1]
    results = json.loads(results_path.read_text())
    score = score_backtest(results, thresholds=MetricThresholds())
    enforcement = enforce_constraints(score, trial.parameters)
    payload = {
        "trial_id": trial_id,
        "parameters": trial.parameters,
        "results_path": results_path.name,
        "score": score,
        "constraints": enforcement.__dict__,
        "log": output_dir.joinpath(f"{trial_id}.log").name,
    }
    (output_dir / f"{trial_id}.log").write_text(log, encoding="utf-8")
    trial_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def run_optimizer(config_path: Path, *, run_id: str | None = None) -> list[dict[str, Any]]:
    config = load_search_config(config_path)
    meta = config.get("meta") or {}
    parameters = config.get("parameters") or {}
    run_id = run_id or config_path.stem
    trials: list[dict[str, Any]] = []
    for index, params in enumerate(expand_parameters(parameters), start=1):
        trial_cfg = TrialConfig(
            snapshot_id=meta.get("snapshot_id", ""),
            symbol=meta.get("symbol", "tBTCUSD"),
            timeframe=meta.get("timeframe", "1h"),
            warmup_bars=int(meta.get("warmup_bars", 150)),
            parameters=params,
        )
        trials.append(run_trial(trial_cfg, run_id=run_id, index=index))
    return trials
