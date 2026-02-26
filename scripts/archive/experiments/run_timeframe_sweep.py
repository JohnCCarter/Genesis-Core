# ruff: noqa: T201,E402
"""Batcha träning och holdoutvalidering över flera timeframes.

Kör fastställda tidsupplösningar för en symbol och samlar IC/Q-spread i en tabell.

Exempel:
    python scripts/run_timeframe_sweep.py --symbol tBTCUSD \
        --timeframes 15m 1h 3h 6h \
        --feature-version v18 \
        --lookahead 5 --threshold 0.0 \
        --use-ensemble
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
MODELS_DIR = ROOT / "results" / "models"
SWEEP_RESULTS_DIR = ROOT / "results" / "timeframe_sweep"


class SweepError(RuntimeError):
    """Signalera fel i timeframe-svepet."""


def run_command(cmd: list[str], *, cwd: Path) -> None:
    """Kör kommando och höj fel vid non-zero exit."""

    process = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if process.returncode != 0:
        raise SweepError(
            "Command failed"
            f"\ncmd: {' '.join(cmd)}"
            f"\nstdout:\n{process.stdout}"
            f"\nstderr:\n{process.stderr}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Kör multi-timeframe sweep")
    parser.add_argument("--symbol", required=True, help="Symbol att träna på (t.ex. tBTCUSD)")
    parser.add_argument(
        "--timeframes",
        nargs="*",
        default=["15m", "1h", "3h", "6h"],
        help="Lista av timeframes att köra",
    )
    parser.add_argument(
        "--feature-version",
        default="v18",
        help="Feature-version att använda vid träning",
    )
    parser.add_argument(
        "--lookahead",
        type=int,
        default=5,
        help="Lookahead (antal bar) för labeling",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.0,
        help="Tröskel för labeling (procent)",
    )
    parser.add_argument(
        "--use-ensemble",
        action="store_true",
        help="Aktivera ensemble-träning (annars single-modell)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Mindre utskrift från underliggande script",
    )
    parser.add_argument(
        "--results-tag",
        default=datetime.utcnow().strftime("%Y%m%d_%H%M%S"),
        help="Tagg för resultatfil (default: current UTC)",
    )
    parser.add_argument(
        "--extra-train-args",
        nargs=argparse.REMAINDER,
        help="Extra argument att skicka vidare till train_model.py",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    SWEEP_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    summary: list[dict[str, Any]] = []

    for timeframe in args.timeframes:
        print(f"\n==== {args.symbol} {timeframe} ====")
        version_suffix = "ensemble" if args.use_ensemble else "single"
        version = f"sweep_{timeframe}_{version_suffix}_la{args.lookahead}_th{args.threshold}"

        train_cmd = [
            sys.executable,
            "scripts/train_model.py",
            "--symbol",
            args.symbol,
            "--timeframe",
            timeframe,
            "--feature-version",
            args.feature_version,
            "--use-holdout",
            "--lookahead",
            str(args.lookahead),
            "--threshold",
            str(args.threshold),
            "--version",
            version,
        ]

        if args.quiet:
            train_cmd.append("--quiet")
        if args.use_ensemble:
            train_cmd.append("--use-ensemble")

        if args.extra_train_args:
            train_cmd.extend(args.extra_train_args)

        print("[RUN]", " ".join(train_cmd))
        run_command(train_cmd, cwd=ROOT)

        model_path = MODELS_DIR / f"{args.symbol}_{timeframe}_{version}.json"
        if not model_path.exists():
            raise SweepError(f"Expected model not found: {model_path}")

        validate_cmd = [
            sys.executable,
            "scripts/validate_holdout.py",
            "--model",
            str(model_path),
            "--symbol",
            args.symbol,
            "--timeframe",
            timeframe,
            "--quiet",
            "--output",
            str(SWEEP_RESULTS_DIR / f"{args.symbol}_{timeframe}_{args.results_tag}.json"),
        ]

        print("[RUN]", " ".join(validate_cmd))
        run_command(validate_cmd, cwd=ROOT)

        metrics_path = MODELS_DIR / f"{args.symbol}_{timeframe}_{version}_metrics.json"
        if not metrics_path.exists():
            raise SweepError(f"Expected metrics file not found: {metrics_path}")

        metas = json.loads(metrics_path.read_text(encoding="utf-8"))
        holdout_path = SWEEP_RESULTS_DIR / f"{args.symbol}_{timeframe}_{args.results_tag}.json"
        holdout_results = json.loads(holdout_path.read_text(encoding="utf-8"))

        results = {
            "symbol": args.symbol,
            "timeframe": timeframe,
            "model_path": str(model_path),
            "metrics_path": str(metrics_path),
            "holdout_path": str(holdout_path),
            "n_train": metas.get("n_train"),
            "n_val": metas.get("n_val"),
            "val_auc": metas.get("buy_model", {}).get("val_auc"),
            "holdout_ic": holdout_results.get("ic"),
            "holdout_ic_p": holdout_results.get("ic_p_value"),
            "holdout_q5_q1": holdout_results.get("q5_q1_spread"),
            "holdout_size": holdout_results.get("holdout_size"),
        }

        summary.append(results)

    summary_path = SWEEP_RESULTS_DIR / f"{args.symbol}_{args.results_tag}_summary.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSweep summary saved to {summary_path}")


if __name__ == "__main__":
    main()
