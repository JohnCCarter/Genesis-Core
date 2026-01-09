#!/usr/bin/env python3
"""
High-level automation to precompute features, curate them, and run training/validation.

Usage examples:
    python scripts/sync_precompute_and_train.py --symbol tBTCUSD --timeframe 1h
    python scripts/sync_precompute_and_train.py --all --version v17
"""

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Iterable
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
PRECOMPUTE_SCRIPT = PROJECT_ROOT / "scripts" / "precompute_features_v17.py"
PRECOMPUTE_SCRIPT_V17 = PROJECT_ROOT / "scripts" / "precompute_features_v17.py"
PRECOMPUTE_SCRIPT_V18 = PROJECT_ROOT / "scripts" / "precompute_features_v18.py"
CURATE_SCRIPT = PROJECT_ROOT / "scripts" / "curate_features.py"
TRAIN_SCRIPT = PROJECT_ROOT / "scripts" / "train_model.py"
VALIDATE_SCRIPT = PROJECT_ROOT / "scripts" / "validate_holdout.py"
REGISTRY_PATH = PROJECT_ROOT / "config" / "models" / "registry.json"


def load_registry_pairs() -> list[tuple[str, str]]:
    if not REGISTRY_PATH.exists():
        raise FileNotFoundError(f"Model registry not found: {REGISTRY_PATH}")

    data = json.loads(REGISTRY_PATH.read_text())
    pairs: set[tuple[str, str]] = set()
    for key in data.keys():
        if ":" not in key:
            continue
        symbol, timeframe = key.split(":", 1)
        pairs.add((symbol, timeframe))

    if not pairs:
        raise ValueError("No symbol:timeframe pairs found in registry.json")

    return sorted(pairs)


def run_cmd(
    cmd: list[str], *, capture_output: bool = False
) -> tuple[int, subprocess.CompletedProcess | None]:
    print(f"[RUN] {' '.join(cmd)}")
    if capture_output:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode, result
    return subprocess.call(cmd), None


def iter_targets(
    symbol: str | None, timeframe: str | None, all_: bool
) -> Iterable[tuple[str, str]]:
    if all_:
        yield from load_registry_pairs()
        return

    if not symbol or not timeframe:
        raise ValueError("--symbol and --timeframe required unless --all is set")

    yield symbol, timeframe


def main() -> int:
    parser = argparse.ArgumentParser(description="Precompute, curate, and train pipeline")
    parser.add_argument("--symbol", help="Symbol, e.g. tBTCUSD")
    parser.add_argument("--timeframe", help="Timeframe, e.g. 1h")
    parser.add_argument(
        "--all", action="store_true", help="Process symbol/timeframes from registry.json"
    )
    parser.add_argument("--version", default="v17", help="Feature version suffix")
    parser.add_argument(
        "--feature-version",
        default="v17",
        choices=["v17", "v18"],
        help="Precompute feature version",
    )
    parser.add_argument("--skip-train", action="store_true", help="Skip training step")
    parser.add_argument("--skip-validate", action="store_true", help="Skip validation step")

    args = parser.parse_args()

    try:
        targets = list(iter_targets(args.symbol, args.timeframe, args.all))
    except ValueError as exc:
        parser.error(str(exc))

    for symbol, timeframe in targets:
        print(f"\n=== PROCESSING {symbol} {timeframe} ===")

        precompute_cmd = [
            sys.executable,
            str(PRECOMPUTE_SCRIPT_V18 if args.feature_version == "v18" else PRECOMPUTE_SCRIPT_V17),
            "--symbol",
            symbol,
            "--timeframe",
            timeframe,
        ]
        if run_cmd(precompute_cmd)[0] != 0:
            print("[ERROR] Precompute failed, aborting.")
            return 1

        curate_cmd = [
            sys.executable,
            str(CURATE_SCRIPT),
            "--symbol",
            symbol,
            "--timeframe",
            timeframe,
            "--version",
            args.feature_version,
        ]
        if run_cmd(curate_cmd)[0] != 0:
            print("[ERROR] Curate failed, aborting.")
            return 1

        model_path: str | None = None

        if not args.skip_train:
            train_cmd = [
                sys.executable,
                str(TRAIN_SCRIPT),
                "--symbol",
                symbol,
                "--timeframe",
                timeframe,
                "--save-provenance",
                "--feature-version",
                args.feature_version,
            ]
            code, result = run_cmd(train_cmd, capture_output=True)
            if code != 0:
                print("[ERROR] Training failed, aborting.")
                return 1

            if result and result.stdout:
                match = re.search(r"Model saved:\s*(.+)", result.stdout)
                if match:
                    model_path = match.group(1).strip()

            if not model_path:
                print("[ERROR] Could not determine model path from training output.")
                return 1

        if not args.skip_validate:
            if not model_path:
                print("[WARN] No model path from training; attempting default location.")
                model_path = f"results/models/{symbol}_{timeframe}_v3.json"

            validate_cmd = [
                sys.executable,
                str(VALIDATE_SCRIPT),
                "--model",
                model_path,
                "--symbol",
                symbol,
                "--timeframe",
                timeframe,
            ]
            if run_cmd(validate_cmd)[0] != 0:
                print("[ERROR] Validation failed, aborting.")
                return 1

    print("\n[SUCCESS] Sync pipeline completed for all targets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
