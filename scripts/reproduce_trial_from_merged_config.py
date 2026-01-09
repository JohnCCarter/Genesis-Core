"""Reproduce a saved Optuna trial using its merged_config.

This script is designed to answer the question:
"Does the best trial from Optuna reproduce when I run a manual backtest?"

It uses the trial's stored merged_config (if present) so that runtime.json drift
cannot change the effective configuration.

Usage
-----
python scripts/reproduce_trial_from_merged_config.py \
    --trial-json results/hparam_search/run_.../trial_123.json

python scripts/reproduce_trial_from_merged_config.py \
    --trial-json results/hparam_search/run_.../trial_123_config.json

If symbol/timeframe cannot be inferred from the trial payload, pass them explicitly:

python scripts/reproduce_trial_from_merged_config.py \
    --trial-json results/hparam_search/run_.../trial_123.json \
    --symbol tBTCUSD --timeframe 1h

Notes
-----
- This is a utility script; it prints paths and key metrics. It does not change champions.
- It expects the backtest engine to accept a config payload like scripts/run_backtest.py.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _find_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _try_infer_symbol_timeframe_from_results_path(
    results_path: Any,
) -> tuple[str | None, str | None]:
    """Infer symbol/timeframe from a payload results_path like 'tBTCUSD_1h_2.json'."""

    if not isinstance(results_path, str):
        return None, None

    name = Path(results_path).name
    # Format: <symbol>_<timeframe>_<n>.json
    parts = name.split("_")
    if len(parts) < 3:
        return None, None
    symbol = parts[0]
    timeframe = parts[1]
    if not symbol or not timeframe:
        return None, None
    return symbol, timeframe


def _load_trial_and_config(trial_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return (trial_payload, config_payload).

    Accepts either a trial payload json (trial_###.json) or a config json (trial_###_config.json).
    """

    payload = _load_json(trial_path)

    # Case A: user provided trial_###.json
    if (
        trial_path.name.startswith("trial_")
        and trial_path.name.endswith(".json")
        and "_config" not in trial_path.name
    ):
        config_path = trial_path.with_name(trial_path.stem + "_config.json")
        if config_path.exists():
            return payload, _load_json(config_path)
        return payload, payload

    # Case B: user provided trial_###_config.json
    if trial_path.name.startswith("trial_") and trial_path.name.endswith("_config.json"):
        trial_payload_path = trial_path.with_name(trial_path.name.replace("_config.json", ".json"))
        if trial_payload_path.exists():
            return _load_json(trial_payload_path), payload
        return payload, payload

    # Fallback: treat as config-like
    return payload, payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trial-json", required=True, type=str)
    parser.add_argument("--symbol", type=str, default=None)
    parser.add_argument("--timeframe", type=str, default=None)
    parser.add_argument("--start", type=str, default=None)
    parser.add_argument("--end", type=str, default=None)
    parser.add_argument("--warmup", type=int, default=None)
    parser.add_argument("--capital", type=float, default=None)
    parser.add_argument("--commission", type=float, default=None)
    parser.add_argument("--slippage", type=float, default=None)
    parser.add_argument("--fast-window", default=None)
    parser.add_argument("--precompute", default=None)
    parser.add_argument("--seed", default=None)
    args = parser.parse_args()

    repo_root = _find_repo_root()
    trial_path = (
        (repo_root / args.trial_json).resolve()
        if not Path(args.trial_json).is_absolute()
        else Path(args.trial_json)
    )

    if not trial_path.exists():
        print(f"[ERROR] Missing trial json: {trial_path}")
        return 2

    trial_payload, config_payload_in = _load_trial_and_config(trial_path)

    merged_config = config_payload_in.get("merged_config")
    if not isinstance(merged_config, dict):
        merged_config = config_payload_in.get("cfg")
    if not isinstance(merged_config, dict):
        merged_config = trial_payload.get("merged_config")
    if not isinstance(merged_config, dict):
        print(
            "[ERROR] Could not find merged_config/cfg in trial payload; cannot guarantee parity. "
            "Provide a trial_###_config.json file or ensure trial json contains merged_config."
        )
        return 2

    # Build a config payload compatible with scripts/run_backtest.py
    # The repo uses a wrapper structure with keys like cfg/overrides/merged_config.
    config_payload = {
        "cfg": merged_config,
        "merged_config": merged_config,
        "runtime_version": config_payload_in.get("runtime_version")
        or trial_payload.get("runtime_version"),
        "overrides": {},
    }

    # Write a temp config file.
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        cfg_path = tmp_path / "trial_merged_config.json"
        cfg_path.write_text(json.dumps(config_payload, indent=2), encoding="utf-8")

        # Ensure canonical environment if requested (optional overrides).
        env = os.environ.copy()
        if args.fast_window is not None:
            env["GENESIS_FAST_WINDOW"] = str(args.fast_window)
        if args.precompute is not None:
            env["GENESIS_PRECOMPUTE_FEATURES"] = str(args.precompute)
        if args.seed is not None:
            env["GENESIS_RANDOM_SEED"] = str(args.seed)

        # Use the same python interpreter running this script.
        python_exe = sys.executable

        inferred_symbol, inferred_timeframe = _try_infer_symbol_timeframe_from_results_path(
            trial_payload.get("results_path")
        )
        symbol = args.symbol or inferred_symbol or "tBTCUSD"
        timeframe = args.timeframe or inferred_timeframe or "1h"

        cmd = [
            python_exe,
            str(repo_root / "scripts" / "run_backtest.py"),
            "--symbol",
            symbol,
            "--timeframe",
            timeframe,
        ]

        if args.start is not None:
            cmd += ["--start", str(args.start)]
        if args.end is not None:
            cmd += ["--end", str(args.end)]
        if args.warmup is not None:
            cmd += ["--warmup", str(int(args.warmup))]
        if args.capital is not None:
            cmd += ["--capital", str(float(args.capital))]
        if args.commission is not None:
            cmd += ["--commission", str(float(args.commission))]
        if args.slippage is not None:
            cmd += ["--slippage", str(float(args.slippage))]

        # Always pass config-file last so it's easy to see in logs.
        cmd += ["--config-file", str(cfg_path)]

        print("[OK] Reproducing trial using merged_config")
        print(f"[OK] Trial: {trial_path}")
        print(f"[OK] Temp config: {cfg_path}")
        print(f"[OK] Python: {python_exe}")
        print(f"[OK] Command: {' '.join(cmd)}")

        proc = subprocess.run(cmd, cwd=str(repo_root), env=env)
        return int(proc.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
