#!/usr/bin/env python3
"""
Extended Validation: Full 2024 (config-only) with v4a baseline.

Runs helår + per kvartal (Q1-Q4) with comprehensive metrics:
- Trades, PF, Win%, Return%, MaxDD, fees
- Component veto-rate per komponent
- Execution funnel (action→allowed→size==0 with ZONE breakdown→attempted→executed/rejected)
- EVGate veto-rate

Guardrails: Flags "insufficient sample size" if helår <40 trades OR any kvartal 0 trades.
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
from collections import Counter

from core.backtest.composable_engine import ComposableBacktestEngine
from core.strategy.components.ml_confidence import MLConfidenceComponent
from core.strategy.components.regime_filter import RegimeFilterComponent
from core.strategy.components.ev_gate import EVGateComponent
from core.strategy.components.cooldown import CooldownComponent
from core.strategy.components.strategy import ComposableStrategy


def run_backtest_with_funnel_analysis(
    config_path: Path, start_date: str, end_date: str, period_name: str
):
    """Run backtest with execution funnel analysis."""

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
        "action_none": 0,
        "action_entry": 0,
        "component_allowed": 0,
        "component_vetoed": 0,
        "component_veto_counts": Counter(),
        "evgate_vetoed": 0,
        "size_nonzero": 0,
        "size_zero": 0,
        "zone_low": 0,
        "zone_mid": 0,
        "zone_high": 0,
        "zone_other": 0,
        "executed": 0,
        "execution_rejected": 0,
    }

    # Track per-component decisions
    executed_bar_indices = set()

    def evaluation_tracker(result, meta, candles):
        """Track execution funnel."""
        from core.strategy.components.context_builder import ComponentContextBuilder

        context = ComponentContextBuilder.build(result, meta, candles=candles)

        action = result.get("action", "NONE")

        funnel_data["total_bars"] += 1

        if action == "NONE":
            funnel_data["action_none"] += 1
        elif action in ("LONG", "SHORT"):
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

                    # Extract ZONE reason
                    reasons = meta.get("decision", {}).get("reasons", [])
                    zone_reason = next((r for r in reasons if r.startswith("ZONE:")), None)
                    if zone_reason:
                        if "low" in zone_reason:
                            funnel_data["zone_low"] += 1
                        elif "mid" in zone_reason:
                            funnel_data["zone_mid"] += 1
                        elif "high" in zone_reason:
                            funnel_data["zone_high"] += 1
                        else:
                            funnel_data["zone_other"] += 1
                    else:
                        funnel_data["zone_other"] += 1
            else:
                funnel_data["component_vetoed"] += 1
                funnel_data["component_veto_counts"][decision.veto_component] += 1

                # Check if EVGate vetoed
                if decision.veto_component == "EVGate":
                    funnel_data["evgate_vetoed"] += 1

        return result, meta

    def post_execution_tracker(symbol, bar_index, action, executed):
        """Track post-execution."""
        if action in ("LONG", "SHORT"):
            if executed:
                funnel_data["executed"] += 1
                executed_bar_indices.add(bar_index)
            else:
                # Only count as rejection if size was nonzero (reached execute_action)
                # We'll infer this from whether bar_index is in executed set
                pass

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
    override_configs = {
        "htf_fibonacci": {"enabled": False, "missing_policy": "allow"},
        "ltf_fibonacci": {"enabled": False, "missing_policy": "allow"},
    }
    results = engine.run(configs=override_configs, verbose=False)

    # Infer execution rejections
    funnel_data["execution_rejected"] = funnel_data["size_nonzero"] - funnel_data["executed"]

    # Combine results with funnel data
    results["funnel"] = funnel_data
    results["period_name"] = period_name
    results["start_date"] = start_date
    results["end_date"] = end_date

    return results


def print_period_report(results: dict, period_name: str):
    """Print comprehensive report for a period."""
    summary = results.get("summary", {})
    attribution = results.get("attribution", {})
    funnel = results.get("funnel", {})

    print(f"\n{'='*90}")
    print(f"{period_name} RESULTS")
    print(f"{'='*90}")

    # Performance metrics
    print("\nPerformance Metrics:")
    print(f"  Trades: {summary.get('num_trades', 0)}")
    print(f"  Profit Factor: {summary.get('profit_factor', 0.0):.2f}")
    print(f"  Win Rate: {summary.get('win_rate', 0.0):.1f}%")
    print(f"  Total Return: {summary.get('total_return', 0.0):.2f}%")
    print(f"  Max Drawdown: {summary.get('max_drawdown', 0.0):.2f}%")
    total_fees = summary.get("total_commission", 0.0) + summary.get("total_slippage", 0.0)
    print(f"  Total Fees: ${total_fees:.2f}")

    # Component attribution
    print("\nComponent Attribution:")
    print(f"  Total Decisions: {attribution.get('total_decisions', 0)}")
    print(
        f"  Allowed: {attribution.get('allowed', 0)} ({100.0 * attribution.get('allow_rate', 0.0):.1f}%)"
    )
    print(f"  Vetoed: {attribution.get('vetoed', 0)}")

    veto_counts = attribution.get("veto_counts", {})
    if veto_counts:
        print("  Veto Counts:")
        for comp, count in veto_counts.items():
            veto_rate = (
                100.0 * count / attribution.get("total_decisions", 1)
                if attribution.get("total_decisions", 0) > 0
                else 0.0
            )
            print(f"    {comp}: {count} ({veto_rate:.1f}% of total)")

    # EVGate veto rate
    evgate_veto_rate = (
        100.0 * funnel.get("evgate_vetoed", 0) / funnel.get("action_entry", 1)
        if funnel.get("action_entry", 0) > 0
        else 0.0
    )
    print(f"  EVGate Veto Rate: {evgate_veto_rate:.1f}% of entry actions")

    # Execution funnel
    print("\nExecution Funnel:")
    print(f"  Total bars: {funnel.get('total_bars', 0)}")
    print(f"  Action NONE: {funnel.get('action_none', 0)}")
    print(f"  Action LONG/SHORT: {funnel.get('action_entry', 0)}")
    print(f"    -> Component allowed: {funnel.get('component_allowed', 0)}")
    print(f"    -> Component vetoed: {funnel.get('component_vetoed', 0)}")
    print(f"       -> size > 0 (attempted): {funnel.get('size_nonzero', 0)}")
    print(f"       -> size == 0: {funnel.get('size_zero', 0)}")

    # ZONE breakdown
    total_size_zero = funnel.get("size_zero", 0)
    if total_size_zero > 0:
        print("          ZONE breakdown:")
        print(
            f"            low@0.250: {funnel.get('zone_low', 0)} ({100.0 * funnel.get('zone_low', 0) / total_size_zero:.1f}%)"
        )
        print(
            f"            mid@0.320: {funnel.get('zone_mid', 0)} ({100.0 * funnel.get('zone_mid', 0) / total_size_zero:.1f}%)"
        )
        print(
            f"            high@0.380: {funnel.get('zone_high', 0)} ({100.0 * funnel.get('zone_high', 0) / total_size_zero:.1f}%)"
        )
        if funnel.get("zone_other", 0) > 0:
            print(
                f"            other: {funnel.get('zone_other', 0)} ({100.0 * funnel.get('zone_other', 0) / total_size_zero:.1f}%)"
            )

    print(f"          -> Executed: {funnel.get('executed', 0)}")
    print(f"          -> Rejected: {funnel.get('execution_rejected', 0)}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Extended validation full 2024")
    parser.add_argument(
        "--config",
        default="config/strategy/composable/phase2/v4a_ml_regime_relaxed.yaml",
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
        results = run_backtest_with_funnel_analysis(config_path, start_date, end_date, period_name)
        if results:
            all_results[period_name] = results
            print_period_report(results, period_name)

    # Guardrails check
    print(f"\n{'='*90}")
    print("GUARDRAILS CHECK")
    print(f"{'='*90}")

    full_year_trades = all_results.get("Full 2024", {}).get("summary", {}).get("num_trades", 0)
    insufficient_sample = False

    print(f"\nFull 2024 trades: {full_year_trades}")
    if full_year_trades < 40:
        print("  WARNING: Insufficient sample size (helaar <40 trades)")
        insufficient_sample = True
    else:
        print("  OK: Sufficient sample size")

    print("\nQuarterly trades:")
    for quarter in ["Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024"]:
        trades = all_results.get(quarter, {}).get("summary", {}).get("num_trades", 0)
        print(f"  {quarter}: {trades} trades", end="")
        if trades == 0:
            print(" - WARNING: Zero trades")
            insufficient_sample = True
        else:
            print()

    if insufficient_sample:
        print("\nFLAG: INSUFFICIENT SAMPLE SIZE")
        print("Action required: Review sizing-policy (ATR zone multipliers) before further tuning")
    else:
        print("\nPASSED: Sufficient sample size for extended validation")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = (
        Path("results") / "extended_validation" / f"{config_name}_full2024_{timestamp}.json"
    )
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2, default=str)

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
