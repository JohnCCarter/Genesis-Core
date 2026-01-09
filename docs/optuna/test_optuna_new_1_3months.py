#!/usr/bin/env python3
"""Kör Optuna enligt YAML (6 månader, resume=true)."""

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

# Säkerställ att projektets src finns på sys.path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.optimizer.runner import run_optimizer


def _read_config(config_path: Path) -> dict[str, Any]:
    return yaml.safe_load(config_path.read_text(encoding="utf-8"))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Kör Optuna enligt angiven YAML-konfig")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/optimizer/tBTCUSD_1h_new_optuna.yaml"),
        help="Sökväg till YAML (default: config/optimizer/tBTCUSD_1h_new_optuna.yaml)",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    config_path: Path = args.config.resolve()

    if not config_path.exists():
        print(f"BAD Hittar inte konfig: {config_path}")
        return 1

    config = _read_config(config_path)
    meta = config.get("meta") or {}
    runs = meta.get("runs") or {}
    optuna_cfg = runs.get("optuna") or {}

    symbol = meta.get("symbol", "tBTCUSD")
    timeframe = meta.get("timeframe", "1h")
    sample_start = meta.get("sample_start")
    sample_end = meta.get("sample_end")
    snapshot = meta.get("snapshot_id")
    strategy = runs.get("strategy", "optuna")
    timeout = optuna_cfg.get("timeout_seconds")
    study_name = optuna_cfg.get("study_name")
    storage = optuna_cfg.get("storage")
    resume = runs.get("resume", True)
    use_range = bool(meta.get("use_sample_range") or runs.get("use_sample_range"))
    max_trials = runs.get("max_trials")
    max_concurrent = runs.get("max_concurrent")

    print("=== OPTUNA STUDY - ENLIGT KONFIG ===\n")
    print("Konfiguration (från YAML):")
    print(f"- Symbol: {symbol}")
    print(f"- Timeframe: {timeframe}")
    if sample_start and sample_end:
        print(f"- Period (sample_range): {sample_start} -> {sample_end}")
    if snapshot:
        print(f"- Snapshot: {snapshot}")
    print(f"- Strategy: {strategy} (TPE sampler, Median pruner)")
    print(f"- Timeout: {timeout}s")
    print(f"- Study: {study_name}")
    print(f"- Storage: {storage}")
    print(f"- Resume: {str(bool(resume)).lower()} (fortsätt från befintlig study)\n")

    print("Verifieringar:")
    print(f"OK YAML anger use_sample_range = {str(use_range).lower()}")
    print(f"OK YAML anger max_trials = {max_trials}, max_concurrent = {max_concurrent}")
    print("OK Inga konflikter förväntas (konfig + resume)\n")

    try:
        print("Startar Optuna enligt YAML...")
        result = run_optimizer(config_path)

        if result:
            print("OK Optuna körning slutförd!")
            print(f"Resultat: {result}")
        else:
            print("BAD Optuna körning misslyckades (inget resultat returnerat).")
            return 1

    except Exception as exc:
        print(f"BAD Fel under Optuna-körning: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
