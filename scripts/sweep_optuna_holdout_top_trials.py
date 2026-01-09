"""Batch holdout backtests for top Optuna trials.

This is a practical bridge between Optuna *train* performance and real out-of-sample validation.
It:
  1) Loads trial result JSONs from a run directory (results/hparam_search/<run_id>/trial_*.json)
  2) Selects the top-N by train score (score.score)
  3) Runs canonical holdout backtests via scripts/run_backtest.py for each trial's config
  4) Parses the saved results JSON and writes a compact CSV summary.

Why run via run_backtest.py?
  - It enforces the canonical mode policy and uses the same config-file semantics we use manually.
  - It produces the same artifacts (results JSON, trades CSV) that we can inspect later.

Example:
    python scripts/sweep_optuna_holdout_top_trials.py --run-id 20251222_164040 --top-n 20 \
        --start 2025-10-01 --end 2025-12-11 --warmup 150 --capital 10000

Notes:
  - Output is written under results/diagnostics/holdout_sweep_<run_id>_topN/.
  - This script intentionally keeps console output small; per-trial logs are captured to files.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


def _get(d: dict, path: str, default=None):
    cur = d
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


@dataclass(frozen=True)
class TrialRef:
    trial_id: int
    train_score: float
    config_path: str


_SAVED_RESULTS_RE = re.compile(r"^\[SAVED\] Results: (.+)$", re.MULTILINE)


def _get_saved_results_from_log(*, project_root: Path, log_path: Path) -> Path | None:
    """Return the saved results JSON path referenced in a run_backtest log, if available."""
    if not log_path.exists():
        return None
    log_text = log_path.read_text(encoding="utf-8", errors="replace")
    m = _SAVED_RESULTS_RE.search(log_text)
    if not m:
        return None

    rel = m.group(1).strip().replace("/", "\\")
    results_path = (project_root / rel).resolve()
    return results_path if results_path.exists() else None


def _select_top_trials(run_dir: Path, top_n: int) -> list[TrialRef]:
    trial_files = [
        p for p in run_dir.glob("trial_*.json") if "_config" not in p.name and p.is_file()
    ]
    if not trial_files:
        raise FileNotFoundError(f"No trial_*.json files found in: {run_dir}")

    refs: list[TrialRef] = []
    for p in trial_files:
        data = json.loads(p.read_text(encoding="utf-8"))
        train_score = _get(data, "score.score")
        trial_id = data.get("trial_id")
        config_path = data.get("config_path")
        if train_score is None or trial_id is None or not config_path:
            continue
        refs.append(
            TrialRef(
                trial_id=int(trial_id), train_score=float(train_score), config_path=str(config_path)
            )
        )

    refs.sort(key=lambda r: r.train_score, reverse=True)
    return refs[:top_n]


def _run_one_backtest(
    *,
    python_exe: str,
    project_root: Path,
    config_file: Path,
    log_path: Path,
    start: str,
    end: str,
    warmup: int,
    capital: float,
    symbol: str,
    timeframe: str,
) -> Path:
    env = os.environ.copy()
    env["GENESIS_FAST_WINDOW"] = "1"
    env["GENESIS_PRECOMPUTE_FEATURES"] = "1"
    env["GENESIS_RANDOM_SEED"] = env.get("GENESIS_RANDOM_SEED", "42")

    cmd = [
        python_exe,
        "-u",
        str(project_root / "scripts" / "run_backtest.py"),
        "--symbol",
        symbol,
        "--timeframe",
        timeframe,
        "--start",
        start,
        "--end",
        end,
        "--warmup",
        str(warmup),
        "--capital",
        str(capital),
        "--config-file",
        str(config_file),
    ]

    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as f:
        proc = subprocess.run(
            cmd,
            cwd=str(project_root),
            env=env,
            stdout=f,
            stderr=subprocess.STDOUT,
            check=False,
            text=True,
        )

    if proc.returncode != 0:
        raise RuntimeError(f"Backtest failed (rc={proc.returncode}) for config: {config_file}")

    results_path = _get_saved_results_from_log(project_root=project_root, log_path=log_path)
    if results_path is None:
        raise RuntimeError(f"Could not find saved results path in log: {log_path}")
    return results_path


def _extract_holdout_metrics(payload: dict) -> dict:
    """Extract holdout metrics from a saved backtest JSON.

    The canonical backtest artifacts written by scripts/run_backtest.py include:
      - payload['summary'] where total_return and max_drawdown are already in percent units.
    Some other artifacts may include payload['metrics'] where values are commonly in fractional units.
    We normalize to *_pct columns.
    """

    summary = payload.get("summary")
    if isinstance(summary, dict) and "total_return" in summary:
        return {
            "holdout_return_pct": float(summary.get("total_return", 0.0)),
            "holdout_pf": float(summary.get("profit_factor", 0.0)),
            "holdout_dd_pct": float(summary.get("max_drawdown", 0.0)),
            "holdout_trades": int(summary.get("num_trades", 0) or 0),
            "metrics_source": "summary",
        }

    metrics = payload.get("metrics")
    if isinstance(metrics, dict) and "total_return" in metrics:
        return {
            "holdout_return_pct": float(metrics.get("total_return", 0.0)) * 100.0,
            "holdout_pf": float(metrics.get("profit_factor", 0.0)),
            "holdout_dd_pct": float(metrics.get("max_drawdown", 0.0)) * 100.0,
            "holdout_trades": int(metrics.get("num_trades", metrics.get("total_trades", 0)) or 0),
            "metrics_source": "metrics",
        }

    return {
        "holdout_return_pct": 0.0,
        "holdout_pf": 0.0,
        "holdout_dd_pct": 0.0,
        "holdout_trades": 0,
        "metrics_source": "missing",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Holdout sweep for top Optuna trials")
    parser.add_argument(
        "--run-id", required=True, help="Run id folder under results/hparam_search/"
    )
    parser.add_argument(
        "--top-n", type=int, default=20, help="How many top trials (by train score) to run"
    )
    parser.add_argument("--start", required=True, help="Holdout start date (YYYY-MM-DD)")
    parser.add_argument("--end", required=True, help="Holdout end date (YYYY-MM-DD)")
    parser.add_argument("--warmup", type=int, default=150, help="Warmup bars")
    parser.add_argument("--capital", type=float, default=10000.0, help="Initial capital")
    parser.add_argument("--symbol", default="tBTCUSD", help="Symbol")
    parser.add_argument("--timeframe", default="1h", help="Timeframe")
    parser.add_argument(
        "--python",
        dest="python_exe",
        default=None,
        help="Python executable to use (defaults to current interpreter)",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    run_dir = project_root / "results" / "hparam_search" / args.run_id
    if not run_dir.exists():
        raise FileNotFoundError(f"Run dir not found: {run_dir}")

    python_exe = args.python_exe or os.fspath(Path(os.sys.executable).resolve())

    out_dir = (
        project_root / "results" / "diagnostics" / f"holdout_sweep_{args.run_id}_top{args.top_n}"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    refs = _select_top_trials(run_dir, args.top_n)
    if not refs:
        raise RuntimeError("No valid trials found to sweep.")

    rows: list[dict] = []
    print(f"[INFO] Sweeping holdout for top {len(refs)} trials (by train score) from {args.run_id}")
    print(f"[INFO] Holdout: {args.start} -> {args.end} (warmup={args.warmup})")

    for idx, ref in enumerate(refs, start=1):
        cfg_file = (run_dir / ref.config_path).resolve()
        trial_tag = f"trial_{ref.trial_id:03d}"
        log_path = out_dir / f"{trial_tag}.log"

        print(f"[{idx:02d}/{len(refs):02d}] {trial_tag} train_score={ref.train_score:.6f}")

        results_json = _get_saved_results_from_log(project_root=project_root, log_path=log_path)
        if results_json is None:
            results_json = _run_one_backtest(
                python_exe=python_exe,
                project_root=project_root,
                config_file=cfg_file,
                log_path=log_path,
                start=args.start,
                end=args.end,
                warmup=args.warmup,
                capital=args.capital,
                symbol=args.symbol,
                timeframe=args.timeframe,
            )

        payload = json.loads(results_json.read_text(encoding="utf-8"))
        holdout = _extract_holdout_metrics(payload)

        rows.append(
            {
                "trial_id": ref.trial_id,
                "train_score": ref.train_score,
                **holdout,
                "results_json": str(results_json),
                "log": str(log_path),
            }
        )

    df = pd.DataFrame(rows)

    out_csv = out_dir / "holdout_sweep_summary.csv"
    df.sort_values(["holdout_return_pct", "holdout_pf"], ascending=False).to_csv(
        out_csv, index=False
    )

    survivors = df[(df["holdout_return_pct"] > 0) & (df["holdout_pf"] > 1.0)]

    print(f"\n[OK] Wrote: {out_csv}")
    print(f"[OK] Completed {len(df)} holdout backtests")
    print(f"[INFO] Survivors (return>0 and PF>1): {len(survivors)}")

    if not survivors.empty:
        print("\n=== SURVIVORS (sorted by return desc) ===")
        cols = [
            "trial_id",
            "train_score",
            "holdout_return_pct",
            "holdout_pf",
            "holdout_dd_pct",
            "holdout_trades",
        ]
        print(
            survivors.sort_values(["holdout_return_pct"], ascending=False)[cols].to_string(
                index=False
            )
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
