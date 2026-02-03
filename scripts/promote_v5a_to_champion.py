#!/usr/bin/env python3
"""
Promote v5a_sizing_exp1 to Champion Config

Converts v5a YAML baseline to proper champion JSON format with full metadata.

This script:
1. Loads v5a YAML config
2. Loads v5a backtest results (Full 2024)
3. Calculates robustness metrics from trades
4. Assembles complete champion JSON
5. Saves to config/strategy/champions/tBTCUSD_1h_composable_v5a.json
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import json
import yaml
from datetime import datetime, UTC
import subprocess


def get_git_commit():
    """Get current git commit hash."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


def calculate_pf(trades):
    """Calculate profit factor from trades list."""
    if not trades:
        return 0.0

    total_wins = sum(t["pnl"] for t in trades if t["pnl"] > 0)
    total_losses = abs(sum(t["pnl"] for t in trades if t["pnl"] < 0))

    if total_losses == 0:
        return float("inf") if total_wins > 0 else 0.0

    return total_wins / total_losses


def calculate_robustness_metrics(trades, total_pnl):
    """Calculate robustness metrics (PF utan top-N, concentration)."""
    if not trades:
        return {}

    sorted_trades = sorted(trades, key=lambda t: t["pnl"], reverse=True)

    # PF utan top-1
    if len(sorted_trades) > 1:
        trades_without_top1 = sorted_trades[1:]
        pf_without_top1 = calculate_pf(trades_without_top1)
    else:
        pf_without_top1 = 0.0

    # PF utan top-3
    if len(sorted_trades) > 3:
        trades_without_top3 = sorted_trades[3:]
        pf_without_top3 = calculate_pf(trades_without_top3)
    else:
        pf_without_top3 = 0.0

    # Concentration
    top1_pnl = sorted_trades[0]["pnl"] if len(sorted_trades) >= 1 else 0
    top1_pct = 100.0 * top1_pnl / total_pnl if total_pnl != 0 else 0.0

    if len(sorted_trades) >= 5:
        top5_pnl = sum(t["pnl"] for t in sorted_trades[:5])
        top5_pct = 100.0 * top5_pnl / total_pnl if total_pnl != 0 else 0.0
    else:
        top5_pct = 0.0

    return {
        "pf_without_top1": round(pf_without_top1, 2),
        "pf_without_top3": round(pf_without_top3, 2),
        "top1_concentration_pct": round(top1_pct, 1),
        "top5_concentration_pct": round(top5_pct, 1),
    }


def main():
    # Paths
    config_path = Path("config/strategy/composable/phase2/v5a_sizing_exp1.yaml")
    results_path = Path("results/milestone3/v5a_sizing_exp1_full2024_20260203_110625.json")
    output_path = Path("config/strategy/champions/tBTCUSD_1h_composable_v5a.json")

    # Load v5a config
    print(f"Loading v5a config: {config_path}")
    with open(config_path) as f:
        v5a_config = yaml.safe_load(f)

    # Load v5a results
    print(f"Loading v5a results: {results_path}")
    with open(results_path) as f:
        v5a_results = json.load(f)

    # Extract Full 2024 data
    full_2024 = v5a_results["Full 2024"]
    summary = full_2024["summary"]
    trades = full_2024["trades"]

    # Calculate robustness metrics
    print("Calculating robustness metrics...")
    total_pnl = summary["total_return_usd"]
    robustness = calculate_robustness_metrics(trades, total_pnl)

    # Extract quarterly metrics
    print("Extracting quarterly metrics...")
    quarterly = {}
    for quarter in ["Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024"]:
        q_summary = v5a_results[quarter]["summary"]
        quarterly[quarter.replace(" ", "_")] = {
            "pf": round(q_summary["profit_factor"], 2),
            "trades": q_summary["num_trades"],
        }

    # Get git commit
    git_commit = get_git_commit()
    print(f"Git commit: {git_commit}")

    # Assemble champion JSON
    print("Assembling champion JSON...")
    champion = {
        "created_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "run_id": "milestone3_v5a",
        "trial_id": "sizing_exp1",
        "git_commit": git_commit,
        "snapshot_id": "snap_tBTCUSD_2024-01-01_2024-12-31_phase3",
        "symbol": "tBTCUSD",
        "timeframe": "1h",
        "score": 0.0,  # No score optimization, this is a baseline
        "metrics": {
            "total_return": summary["total_return"] / 100.0,  # Convert % to decimal
            "profit_factor": summary["profit_factor"],
            "max_drawdown": summary["max_drawdown"] / 100.0,  # Convert % to decimal
            "win_rate": summary["win_rate"] / 100.0,  # Convert % to decimal
            "num_trades": summary["num_trades"],
            "sharpe_ratio": None,  # Not calculated in backtest
            "return_to_dd": None,  # Not calculated in backtest
            "total_commission": summary["total_commission"],
            "total_commission_pct": summary["total_commission"]
            / 10000.0,  # Commission as % of capital
        },
        "constraints": {
            "hard_failures": [],
            "raw": {
                "source": "phase3_milestone3",
                "run_dir": "results/milestone3",
                "results_path": str(results_path),
            },
        },
        "metadata": {
            "note": "Phase 3 Milestone 3 baseline. Composable strategy with risk_map threshold 0.53. Paper trading champion from 2026-02-03.",
            "phase": "phase3_milestone3",
            "baseline": "v5a_sizing_exp1",
            "robustness": robustness,
            "quarterly": quarterly,
        },
        "cfg": v5a_config,  # Complete YAML config as-is
    }

    # Save champion JSON
    output_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Saving champion to: {output_path}")
    with open(output_path, "w") as f:
        json.dump(champion, f, indent=2)

    print("\n" + "=" * 80)
    print("v5a PROMOTED TO CHAMPION")
    print("=" * 80)
    print(f"Champion file: {output_path}")
    print("Symbol: tBTCUSD")
    print("Timeframe: 1h")
    print(f"PF: {champion['metrics']['profit_factor']:.2f}")
    print(f"PF utan top-3: {robustness['pf_without_top3']:.2f}")
    print(f"Trades: {champion['metrics']['num_trades']}")
    print(f"MaxDD: {champion['metrics']['max_drawdown']*100:.2f}%")
    print(f"Top-1 concentration: {robustness['top1_concentration_pct']:.1f}%")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Commit this champion file")
    print("2. Verify champion freeze workflow is active")
    print("3. Start paper trading on 2026-02-03")
    print("4. Create feature/composable-research branch for continued development")


if __name__ == "__main__":
    main()
