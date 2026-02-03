#!/usr/bin/env python3
"""
Milestone 4 - Experiment 4.2: ml_confidence Quality Tuning

Single config change: ml_confidence threshold 0.24 -> 0.26

Goal: Improve PF (1.45 -> 1.50+) without sacrificing robustness (PF utan top-3 >= 1.25)

CRITICAL: Auto-reject if PF utan top-3 < 1.25 (stop criterion)

Deliverables:
1. HQT audit: PF, robustness, concentration
2. Comparison with v5a baseline
3. Component veto rates
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import os

os.environ["GENESIS_FAST_WINDOW"] = "1"
os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"

import json
import yaml
from datetime import datetime

from core.backtest.composable_engine import ComposableBacktestEngine
from core.strategy.components.ml_confidence import MLConfidenceComponent
from core.strategy.components.regime_filter import RegimeFilterComponent
from core.strategy.components.ev_gate import EVGateComponent
from core.strategy.components.cooldown import CooldownComponent
from core.strategy.components.strategy import ComposableStrategy


def calculate_pf(trades):
    """Calculate profit factor from trades list."""
    if not trades:
        return 0.0

    total_wins = sum(t["pnl"] for t in trades if t["pnl"] > 0)
    total_losses = abs(sum(t["pnl"] for t in trades if t["pnl"] < 0))

    if total_losses == 0:
        return float("inf") if total_wins > 0 else 0.0

    return total_wins / total_losses


def run_backtest_with_tracking(config_path: Path, start_date: str, end_date: str, period_name: str):
    """Run backtest with execution funnel and component tracking."""

    # Load config
    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Build components
    components = []
    for comp_cfg in config.get("components", []):
        comp_type = comp_cfg["type"]
        params = comp_cfg.get("params", {})

        if comp_type == "ml_confidence":
            components.append(MLConfidenceComponent(**params))
        elif comp_type == "regime_filter":
            components.append(RegimeFilterComponent(**params))
        elif comp_type == "ev_gate":
            components.append(EVGateComponent(**params))
        elif comp_type == "cooldown":
            components.append(CooldownComponent(params))

    strategy = ComposableStrategy(components=components)

    # Create engine
    engine = ComposableBacktestEngine(
        symbol="tBTCUSD",
        timeframe="1h",
        strategy=strategy,
        start_date=start_date,
        end_date=end_date,
        fast_window=True,
    )

    # Load data
    print(f"Loading data for {period_name}...")
    if not engine.load_data():
        print(f"ERROR: Failed to load data for {period_name}")
        return None

    # Run backtest
    print(f"Running backtest for {period_name}...")

    # Pass risk config from YAML to backtest engine
    override_configs = {
        "htf_fibonacci": {"enabled": False, "missing_policy": "allow"},
        "ltf_fibonacci": {"enabled": False, "missing_policy": "allow"},
    }

    # Add risk config if present in YAML
    if "risk" in config:
        override_configs["risk"] = config["risk"]

    results = engine.run(configs=override_configs, verbose=False)

    # Add attribution data
    results["period_name"] = period_name
    results["start_date"] = start_date
    results["end_date"] = end_date

    return results


def hqt_audit_with_comparison(results: dict, baseline_results: dict = None):
    """Run HQT audit with optional baseline comparison."""

    print(f"\n{'='*90}")
    print("HQT AUDIT - Milestone 4 Experiment 4.2")
    print(f"{'='*90}\n")

    # (1) PF Overview
    print("(1) Profit Factor Overview")
    print("-" * 90)

    full_pf = results["Full 2024"]["summary"]["profit_factor"]
    full_trades = results["Full 2024"]["summary"]["num_trades"]
    print(f"  Full 2024: PF = {full_pf:.2f} ({full_trades} trades)")

    if baseline_results:
        baseline_pf = baseline_results["Full 2024"]["summary"]["profit_factor"]
        baseline_trades = baseline_results["Full 2024"]["summary"]["num_trades"]
        pf_change = full_pf - baseline_pf
        trades_change = full_trades - baseline_trades
        print(f"    vs v5a: PF {baseline_pf:.2f} -> {full_pf:.2f} ({pf_change:+.2f}), trades {baseline_trades} -> {full_trades} ({trades_change:+d})")

    quarters = ["Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024"]
    pf_quarters = []
    for quarter in quarters:
        pf = results[quarter]["summary"]["profit_factor"]
        num_trades = results[quarter]["summary"]["num_trades"]
        pf_quarters.append(pf)
        print(f"  {quarter}: PF = {pf:.2f} ({num_trades} trades)")

    print()

    # (2) PnL Concentration
    print("(2) PnL Concentration")
    print("-" * 90)

    trades = results["Full 2024"]["trades"]
    sorted_trades = sorted(trades, key=lambda t: t["pnl"], reverse=True)
    total_pnl = sum(t["pnl"] for t in trades)

    top1_pnl = sorted_trades[0]["pnl"] if len(sorted_trades) >= 1 else 0
    top1_pct = 100.0 * top1_pnl / total_pnl if total_pnl != 0 else 0.0
    print(f"  Top-1 trade: ${top1_pnl:.2f} ({top1_pct:.1f}% of total PnL)")

    if baseline_results:
        baseline_trades = baseline_results["Full 2024"]["trades"]
        baseline_sorted = sorted(baseline_trades, key=lambda t: t["pnl"], reverse=True)
        baseline_total_pnl = sum(t["pnl"] for t in baseline_trades)
        baseline_top1_pct = 100.0 * baseline_sorted[0]["pnl"] / baseline_total_pnl if baseline_total_pnl != 0 else 0.0
        print(f"    vs v5a: {baseline_top1_pct:.1f}% -> {top1_pct:.1f}% ({top1_pct - baseline_top1_pct:+.1f}pp)")

    if len(sorted_trades) >= 5:
        top5_pnl = sum(t["pnl"] for t in sorted_trades[:5])
        top5_pct = 100.0 * top5_pnl / total_pnl if total_pnl != 0 else 0.0
        print(f"  Top-5 trades: ${top5_pnl:.2f} ({top5_pct:.1f}% of total PnL)")

    print()

    # (3) PF Robustness
    print("(3) PF Robustness")
    print("-" * 90)

    if len(sorted_trades) > 1:
        trades_without_top1 = sorted_trades[1:]
        pf_without_top1 = calculate_pf(trades_without_top1)
        print(f"  PF without top-1: {pf_without_top1:.2f} (was {full_pf:.2f})")

    if len(sorted_trades) > 3:
        trades_without_top3 = sorted_trades[3:]
        pf_without_top3 = calculate_pf(trades_without_top3)
        print(f"  PF without top-3: {pf_without_top3:.2f} (was {full_pf:.2f})")

        if baseline_results:
            baseline_sorted_trades = sorted(baseline_trades, key=lambda t: t["pnl"], reverse=True)
            if len(baseline_sorted_trades) > 3:
                baseline_without_top3 = baseline_sorted_trades[3:]
                baseline_pf_without_top3 = calculate_pf(baseline_without_top3)
                print(f"    vs v5a: {baseline_pf_without_top3:.2f} -> {pf_without_top3:.2f} ({pf_without_top3 - baseline_pf_without_top3:+.2f})")

    print()

    # (4) Component Attribution
    print("(4) Component Attribution")
    print("-" * 90)

    attribution = results["Full 2024"]["attribution"]
    total_decisions = attribution.get("total_decisions", 0)
    allowed = attribution.get("allowed", 0)
    vetoed = attribution.get("vetoed", 0)
    veto_counts = attribution.get("veto_counts", {})

    print(f"  Total decisions: {total_decisions}")
    print(f"  Allowed: {allowed} ({100.0 * allowed / total_decisions:.1f}%)")
    print(f"  Vetoed: {vetoed} ({100.0 * vetoed / total_decisions:.1f}%)")

    if veto_counts:
        print(f"  Veto breakdown:")
        for comp, count in veto_counts.items():
            veto_rate = 100.0 * count / total_decisions if total_decisions > 0 else 0.0
            print(f"    {comp}: {count} ({veto_rate:.1f}%)")

    print()

    # (5) Risk Sanity
    print("(5) Risk Sanity")
    print("-" * 90)

    summary = results["Full 2024"]["summary"]
    max_dd = summary["max_drawdown"]
    total_fees = summary["total_commission"] + summary.get("total_slippage", 0.0)
    fees_per_trade = total_fees / full_trades if full_trades > 0 else 0.0

    print(f"  Max Drawdown: {max_dd:.2f}%")
    print(f"  Fees per trade: ${fees_per_trade:.2f}")

    if baseline_results:
        baseline_max_dd = baseline_results["Full 2024"]["summary"]["max_drawdown"]
        baseline_fees_per_trade = (baseline_results["Full 2024"]["summary"]["total_commission"] + baseline_results["Full 2024"]["summary"].get("total_slippage", 0.0)) / baseline_results["Full 2024"]["summary"]["num_trades"]
        print(f"    vs v5a: MaxDD {baseline_max_dd:.2f}% -> {max_dd:.2f}% ({max_dd - baseline_max_dd:+.2f}pp)")
        print(f"    vs v5a: Fees/trade ${baseline_fees_per_trade:.2f} -> ${fees_per_trade:.2f} ({fees_per_trade - baseline_fees_per_trade:+.2f})")

    print()

    # HQT-pass criteria
    print(f"{'='*90}")
    print("HQT-PASS CRITERIA (Milestone 4 Goals)")
    print(f"{'='*90}\n")

    checks = []

    # [1] Helar PF >= 1.50
    check1 = full_pf >= 1.50
    checks.append(check1)
    status1 = "PASS" if check1 else "FAIL"
    print(f"  [1] Helar PF >= 1.50: {full_pf:.2f} - {status1}")

    # [2] PF utan top-3 >= 1.25
    if len(sorted_trades) > 3:
        check2 = pf_without_top3 >= 1.25
        checks.append(check2)
        status2 = "PASS" if check2 else "FAIL"
        print(f"  [2] PF utan top-3 >= 1.25: {pf_without_top3:.2f} - {status2}")
    else:
        print(f"  [2] PF utan top-3 >= 1.25: N/A")
        checks.append(False)

    # [3] Top-1 PnL < 30%
    check3 = top1_pct < 30.0
    checks.append(check3)
    status3 = "PASS" if check3 else "FAIL"
    print(f"  [3] Top-1 PnL < 30%: {top1_pct:.1f}% - {status3}")

    # [4] MaxDD <= 3.5%
    check4 = max_dd <= 3.5
    checks.append(check4)
    status4 = "PASS" if check4 else "FAIL"
    print(f"  [4] MaxDD <= 3.5%: {max_dd:.2f}% - {status4}")

    print()

    # Overall verdict
    all_pass = all(checks)
    verdict = "MILESTONE-4-PASS" if all_pass else "MILESTONE-4-FAIL"
    print(f"  Overall: {verdict}")

    print(f"\n{'='*90}\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Milestone 4 Experiment 4.2")
    parser.add_argument(
        "--config",
        default="config/strategy/composable/phase2/v6b_mlconf_exp2.yaml",
        help="Path to config",
    )
    parser.add_argument(
        "--baseline",
        default="results/milestone3/v5a_sizing_exp1_full2024_20260203_110625.json",
        help="Path to v5a baseline results for comparison",
    )

    args = parser.parse_args()

    config_path = Path(args.config)
    config_name = config_path.stem

    # Load baseline results if available
    baseline_results = None
    baseline_path = Path(args.baseline)
    if baseline_path.exists():
        with open(baseline_path) as f:
            baseline_results = json.load(f)
        print(f"Loaded baseline: {baseline_path}")

    # Define periods
    periods = [
        ("Q1 2024", "2024-01-01", "2024-03-31"),
        ("Q2 2024", "2024-04-01", "2024-06-30"),
        ("Q3 2024", "2024-07-01", "2024-09-30"),
        ("Q4 2024", "2024-10-01", "2024-12-31"),
        ("Full 2024", "2024-01-01", "2024-12-31"),
    ]

    # Run all periods
    all_results = {}
    for period_name, start_date, end_date in periods:
        results = run_backtest_with_tracking(config_path, start_date, end_date, period_name)
        if results:
            all_results[period_name] = results

    # Run HQT audit with baseline comparison
    hqt_audit_with_comparison(all_results, baseline_results)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path("results") / "milestone4" / f"{config_name}_full2024_{timestamp}.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2, default=str)

    print(f"Results saved to: {output_file}")


if __name__ == "__main__":
    main()
