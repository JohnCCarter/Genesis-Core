#!/usr/bin/env python3
"""
Milestone 3 - Experiment 3.1: Sizing Policy Tuning (risk_map adjustment)

Single config change: risk.risk_map first threshold 0.6 → 0.53

Deliverables:
1. HQT audit (PF-first): full year + per quarter, PF without top-1/top-3, PnL concentration
2. Trade stats: trades/year, size>0 rate, execution funnel
3. Risk sanity: MaxDD, fees/trade

Stop after report + artifacts for decision.
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
    """Run backtest with execution funnel tracking."""

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

    # Track execution funnel
    funnel_data = {
        "total_bars": 0,
        "action_entry": 0,
        "component_allowed": 0,
        "size_nonzero": 0,
        "size_zero": 0,
        "executed": 0,
    }

    def evaluation_tracker(result, meta, candles):
        """Track execution funnel."""
        from core.strategy.components.context_builder import ComponentContextBuilder

        context = ComponentContextBuilder.build(result, meta, candles=candles)

        action = result.get("action", "NONE")
        funnel_data["total_bars"] += 1

        if action in ("LONG", "SHORT"):
            funnel_data["action_entry"] += 1

            # Evaluate components
            decision = strategy.evaluate(context)

            if decision.allowed:
                funnel_data["component_allowed"] += 1

                # Check size
                size = meta.get("decision", {}).get("size", 0.0)
                if size > 0:
                    funnel_data["size_nonzero"] += 1
                else:
                    funnel_data["size_zero"] += 1

        return result, meta

    def post_execution_tracker(symbol, bar_index, action, executed):
        """Track post-execution."""
        if action in ("LONG", "SHORT") and executed:
            funnel_data["executed"] += 1

    # Create engine
    engine = ComposableBacktestEngine(
        symbol="tBTCUSD",
        timeframe="1h",
        strategy=strategy,
        start_date=start_date,
        end_date=end_date,
        fast_window=True,
    )

    # Override hooks
    engine.engine.evaluation_hook = evaluation_tracker

    original_post_hook = engine.engine.post_execution_hook

    def combined_post_hook(symbol, bar_index, action, executed):
        if original_post_hook is not None:
            original_post_hook(symbol, bar_index, action, executed)
        post_execution_tracker(symbol, bar_index, action, executed)

    engine.engine.post_execution_hook = combined_post_hook

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

    # Combine results with funnel data
    results["funnel"] = funnel_data
    results["period_name"] = period_name
    results["start_date"] = start_date
    results["end_date"] = end_date

    return results


def hqt_audit(results: dict):
    """Run HQT audit on results."""

    print(f"\n{'='*90}")
    print("HQT AUDIT (PF-FIRST) - Milestone 3 Experiment 3.1")
    print(f"{'='*90}\n")

    # (1) PF Overview
    print("(1) Profit Factor Overview")
    print("-" * 90)

    full_pf = results["Full 2024"]["summary"]["profit_factor"]
    full_trades = results["Full 2024"]["summary"]["num_trades"]
    print(f"  Full 2024: PF = {full_pf:.2f} ({full_trades} trades)")

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

    if len(sorted_trades) >= 1:
        top1_pnl = sorted_trades[0]["pnl"]
        top1_pct = 100.0 * top1_pnl / total_pnl if total_pnl != 0 else 0.0
        print(f"  Top-1 trade: ${top1_pnl:.2f} ({top1_pct:.1f}% of total PnL)")

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

    print()

    # (4) Trade Stats
    print("(4) Trade Stats & Execution Funnel")
    print("-" * 90)

    funnel = results["Full 2024"]["funnel"]

    total_bars = funnel["total_bars"]
    action_entry = funnel["action_entry"]
    component_allowed = funnel["component_allowed"]
    size_nonzero = funnel["size_nonzero"]
    size_zero = funnel["size_zero"]
    executed = funnel["executed"]

    print(f"  Total bars: {total_bars}")
    print(f"  Entry actions: {action_entry}")
    print(
        f"    -> Component allowed: {component_allowed} ({100.0 * component_allowed / action_entry:.1f}%)"
    )
    print(
        f"       -> size > 0 (attempted): {size_nonzero} ({100.0 * size_nonzero / component_allowed:.1f}%)"
    )
    print(f"       -> size == 0: {size_zero} ({100.0 * size_zero / component_allowed:.1f}%)")
    print(f"          -> Executed: {executed} ({100.0 * executed / size_nonzero:.1f}% of attempts)")

    size_nonzero_rate = 100.0 * size_nonzero / component_allowed if component_allowed > 0 else 0.0
    print(f"\n  size>0 rate: {size_nonzero_rate:.1f}% (was 1.4% in v4a)")
    print(f"  Trades/year: {full_trades}")

    print()

    # (5) Risk Sanity
    print("(5) Risk Sanity")
    print("-" * 90)

    summary = results["Full 2024"]["summary"]
    max_dd = summary["max_drawdown"]
    total_fees = summary["total_commission"] + summary.get("total_slippage", 0.0)
    fees_per_trade = total_fees / full_trades if full_trades > 0 else 0.0

    print(f"  Max Drawdown: {max_dd:.2f}%")
    print(f"  Total fees: ${total_fees:.2f}")
    print(f"  Fees per trade: ${fees_per_trade:.2f}")

    print()

    # HQT-pass criteria
    print(f"{'='*90}")
    print("HQT-PASS CRITERIA")
    print(f"{'='*90}\n")

    checks = []

    # [1] Helar PF >= 1.5
    check1 = full_pf >= 1.5
    checks.append(check1)
    status1 = "PASS" if check1 else "FAIL"
    print(f"  [1] Helar PF >= 1.5: {full_pf:.2f} - {status1}")

    # [2] Minst 3/4 kvartal PF >= 1.3
    quarters_above_1_3 = sum(1 for pf in pf_quarters if pf >= 1.3)
    check2 = quarters_above_1_3 >= 3
    checks.append(check2)
    status2 = "PASS" if check2 else "FAIL"
    print(f"  [2] Minst 3/4 kvartal PF >= 1.3: {quarters_above_1_3}/4 - {status2}")

    # [3] Inget kvartal < 1.0
    min_quarter_pf = min(pf_quarters) if pf_quarters else 0.0
    check3 = min_quarter_pf >= 1.0
    checks.append(check3)
    status3 = "PASS" if check3 else "FAIL"
    print(f"  [3] Inget kvartal < 1.0: min = {min_quarter_pf:.2f} - {status3}")

    # [4] PF utan top-3 >= 1.2
    if len(sorted_trades) > 3:
        check4 = pf_without_top3 >= 1.2
        checks.append(check4)
        status4 = "PASS" if check4 else "FAIL"
        print(f"  [4] PF utan top-3 >= 1.2: {pf_without_top3:.2f} - {status4}")
    else:
        print("  [4] PF utan top-3 >= 1.2: N/A (not enough trades)")
        checks.append(False)

    # [5] Top-1 PnL < 30%
    check5 = top1_pct < 30.0
    checks.append(check5)
    status5 = "PASS" if check5 else "FAIL"
    print(f"  [5] Top-1 PnL < 30%: {top1_pct:.1f}% - {status5}")

    # [6] MaxDD <= 3.5%
    check6 = max_dd <= 3.5
    checks.append(check6)
    status6 = "PASS" if check6 else "FAIL"
    print(f"  [6] MaxDD <= 3.5%: {max_dd:.2f}% - {status6}")

    print()

    # Overall verdict
    all_pass = all(checks)
    verdict = "HQT-PASS" if all_pass else "HQT-FAIL"
    print(f"  Overall: {verdict}")

    print(f"\n{'='*90}\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Milestone 3 Experiment 3.1")
    parser.add_argument(
        "--config",
        default="config/strategy/composable/phase2/v5a_sizing_exp1.yaml",
        help="Path to config",
    )

    args = parser.parse_args()

    config_path = Path(args.config)
    config_name = config_path.stem

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

    # Run HQT audit
    hqt_audit(all_results)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path("results") / "milestone3" / f"{config_name}_full2024_{timestamp}.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2, default=str)

    print(f"Results saved to: {output_file}")


if __name__ == "__main__":
    main()
