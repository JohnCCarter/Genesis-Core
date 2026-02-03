#!/usr/bin/env python3
"""
Diagnose Gap #3: Execution layer rejection reasons (V2 - Complete).

Captures COMPLETE flow: action≠NONE → size>0 → execute_action(executed)
Includes EV distribution for executed trades.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import os

os.environ["GENESIS_FAST_WINDOW"] = "1"
os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"

import yaml
from collections import Counter

from core.backtest.composable_engine import ComposableBacktestEngine
from core.strategy.components.ml_confidence import MLConfidenceComponent
from core.strategy.components.regime_filter import RegimeFilterComponent
from core.strategy.components.ev_gate import EVGateComponent
from core.strategy.components.cooldown import CooldownComponent
from core.strategy.components.strategy import ComposableStrategy


def diagnose_execution_gap_v2(config_path: Path):
    """Diagnose execution layer rejection reasons with complete tracking."""

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

    # Global tracking dict (bar_index → data)
    bar_data = {}

    # Summary counters
    summary = {
        "total_bars": 0,
        "action_none": 0,
        "action_entry_total": 0,  # All LONG/SHORT actions
        "component_allowed": 0,  # Passed all components
        "component_vetoed": 0,  # Blocked by components
        "component_veto_reasons": Counter(),
        "executed": 0,  # Actually opened trade
        "execution_rejected": 0,  # Allowed by components but rejected by engine
        "ev_all": [],
        "ev_ml_regime_allowed": [],
        "ev_executed": [],
        "rejection_samples": [],
        "execution_samples": [],
    }

    def evaluation_hook_tracker(result, meta, candles):
        """Track evaluation decisions."""
        from core.strategy.components.context_builder import ComponentContextBuilder

        context = ComponentContextBuilder.build(result, meta, candles=candles)

        bar_index = context.get("bar_index", -1)
        action = result.get("action", "NONE")
        ev = context.get("expected_value")

        summary["total_bars"] += 1

        # Store bar data
        bar_data[bar_index] = {
            "action": action,
            "ev": ev,
            "context": context,
        }

        # Track EV for all decisions
        if ev is not None:
            summary["ev_all"].append(ev)

        # Check ML+Regime allowance (pre EVGate/Cooldown)
        ml_comp = [c for c in strategy.components if isinstance(c, MLConfidenceComponent)][0]
        regime_comp = [c for c in strategy.components if isinstance(c, RegimeFilterComponent)][0]

        ml_result = ml_comp.evaluate(context)
        regime_result = regime_comp.evaluate(context)

        if ml_result.allowed and regime_result.allowed and ev is not None:
            summary["ev_ml_regime_allowed"].append(ev)

        # Track action distribution
        if action == "NONE":
            summary["action_none"] += 1
        elif action in ("LONG", "SHORT"):
            summary["action_entry_total"] += 1

            # Evaluate full component chain
            decision = strategy.evaluate(context)

            if decision.allowed:
                summary["component_allowed"] += 1
                bar_data[bar_index]["component_allowed"] = True
            else:
                summary["component_vetoed"] += 1
                summary["component_veto_reasons"][decision.veto_component] += 1
                bar_data[bar_index]["component_allowed"] = False
                bar_data[bar_index]["veto_component"] = decision.veto_component

                # Sample component vetoes
                if len(summary["rejection_samples"]) < 100:
                    summary["rejection_samples"].append(
                        {
                            "bar_index": bar_index,
                            "action": action,
                            "reason": f"component_veto_{decision.veto_component}",
                            "ev": ev,
                        }
                    )

        return result, meta

    def post_execution_tracker(symbol, bar_index, action, executed):
        """Track post-execution results."""
        if action in ("LONG", "SHORT"):
            bar_info = bar_data.get(bar_index, {})

            if executed:
                summary["executed"] += 1

                # Extract EV for executed trade
                ev = bar_info.get("ev")
                if ev is not None:
                    summary["ev_executed"].append(ev)

                # Sample executions
                if len(summary["execution_samples"]) < 50:
                    summary["execution_samples"].append(
                        {
                            "bar_index": bar_index,
                            "action": action,
                            "reason": "executed",
                            "ev": ev,
                        }
                    )
            else:
                # Execution rejected (components allowed but engine rejected)
                if bar_info.get("component_allowed", False):
                    summary["execution_rejected"] += 1

                    # Sample execution rejections
                    if len(summary["rejection_samples"]) < 200:
                        summary["rejection_samples"].append(
                            {
                                "bar_index": bar_index,
                                "action": action,
                                "reason": "execution_rejected_position_open",
                                "ev": bar_info.get("ev"),
                            }
                        )

    # Create engine with hooks
    engine = ComposableBacktestEngine(
        symbol="tBTCUSD",
        timeframe="1h",
        strategy=strategy,
        start_date="2024-01-01",
        end_date="2024-03-31",
        fast_window=True,
    )

    # Override hooks
    engine.engine.evaluation_hook = evaluation_hook_tracker

    original_post_hook = engine.engine.post_execution_hook

    def combined_post_hook(symbol, bar_index, action, executed):
        if original_post_hook is not None:
            original_post_hook(symbol, bar_index, action, executed)
        post_execution_tracker(symbol, bar_index, action, executed)

    engine.engine.post_execution_hook = combined_post_hook

    # Load data
    print("Loading data...")
    if not engine.load_data():
        print("ERROR: Failed to load data")
        return

    # Run backtest
    print("Running backtest with complete execution tracking...")
    override_configs = {
        "htf_fibonacci": {"enabled": False, "missing_policy": "allow"},
        "ltf_fibonacci": {"enabled": False, "missing_policy": "allow"},
    }
    results = engine.run(configs=override_configs, verbose=False)

    # Print analysis
    print(f"\n{'='*90}")
    print("EXECUTION LAYER GAP ANALYSIS (Gap #3) - COMPLETE")
    print(f"{'='*90}")
    print(f"\nTotal bars processed: {summary['total_bars']}")
    print()

    # Action distribution
    print("Action Distribution:")
    print(f"  Action NONE: {summary['action_none']} ({100.0 * summary['action_none'] / summary['total_bars']:.1f}%)")
    print(
        f"  Action LONG/SHORT: {summary['action_entry_total']} ({100.0 * summary['action_entry_total'] / summary['total_bars']:.1f}%)"
    )
    print()

    # Component filtering
    print("Component Filtering (of entry actions):")
    print(
        f"  Allowed by components: {summary['component_allowed']} ({100.0 * summary['component_allowed'] / summary['action_entry_total']:.1f}%)"
    )
    print(
        f"  Vetoed by components: {summary['component_vetoed']} ({100.0 * summary['component_vetoed'] / summary['action_entry_total']:.1f}%)"
    )
    if summary['component_veto_reasons']:
        print("    Veto reasons:")
        for comp, count in summary['component_veto_reasons'].most_common():
            print(
                f"      {comp}: {count} ({100.0 * count / summary['component_vetoed']:.1f}% of vetoes)"
            )
    print()

    # Execution layer
    print("Execution Layer (of component-allowed):")
    print(
        f"  Executed: {summary['executed']} ({100.0 * summary['executed'] / summary['component_allowed']:.1f}% of allowed)"
    )
    print(
        f"  Rejected: {summary['execution_rejected']} ({100.0 * summary['execution_rejected'] / summary['component_allowed']:.1f}% of allowed)"
    )
    print()

    # Overall funnel
    print("Overall Funnel:")
    print(f"  Entry actions (LONG/SHORT): {summary['action_entry_total']} (100.0%)")
    print(
        f"  → Component allowed: {summary['component_allowed']} ({100.0 * summary['component_allowed'] / summary['action_entry_total']:.1f}%)"
    )
    print(
        f"  → Executed trades: {summary['executed']} ({100.0 * summary['executed'] / summary['action_entry_total']:.1f}%)"
    )
    print(
        f"  → Component veto drop: {summary['component_vetoed']} ({100.0 * summary['component_vetoed'] / summary['action_entry_total']:.1f}%)"
    )
    print(
        f"  → Execution reject drop: {summary['execution_rejected']} ({100.0 * summary['execution_rejected'] / summary['action_entry_total']:.1f}%)"
    )

    # Samples
    print(f"\n{'='*90}")
    print("Rejection Samples (first 20):")
    print(f"{'bar_index':<12} {'action':<8} {'reason':<50} {'EV':<10}")
    print("-" * 90)
    for sample in summary["rejection_samples"][:20]:
        ev_str = f"{sample['ev']:.4f}" if sample['ev'] is not None else "N/A"
        print(f"{sample['bar_index']:<12} {sample['action']:<8} {sample['reason']:<50} {ev_str:<10}")

    print(f"\nExecution Samples (first 20):")
    print(f"{'bar_index':<12} {'action':<8} {'reason':<50} {'EV':<10}")
    print("-" * 90)
    for sample in summary["execution_samples"][:20]:
        ev_str = f"{sample['ev']:.4f}" if sample['ev'] is not None else "N/A"
        print(f"{sample['bar_index']:<12} {sample['action']:<8} {sample['reason']:<50} {ev_str:<10}")

    # EV distribution
    print(f"\n{'='*90}")
    print("EV DISTRIBUTION ANALYSIS")
    print(f"{'='*90}")

    def print_ev_stats(ev_list, label):
        if not ev_list:
            print(f"\n{label}: No data")
            return

        import numpy as np

        ev_array = np.array(ev_list)
        print(f"\n{label}:")
        print(f"  Samples: {len(ev_array)}")
        print(f"  Mean: {ev_array.mean():.4f}")
        print(f"  Std: {ev_array.std():.4f}")
        print(f"  Min: {ev_array.min():.4f}")
        print(f"  Max: {ev_array.max():.4f}")
        print(f"  Percentiles:")
        for p in [25, 50, 75, 80, 85, 90, 95]:
            print(f"    p{p}: {np.percentile(ev_array, p):.4f}")

    print_ev_stats(summary["ev_all"], "(a) All Decisions")
    print_ev_stats(summary["ev_ml_regime_allowed"], "(b) ML+Regime Allowed (pre EVGate/Cooldown)")
    print_ev_stats(summary["ev_executed"], "(c) Executed Trades")

    print(f"\n{'='*90}")
    print(f"Backtest Trades: {results['summary']['num_trades']}")
    print(f"{'='*90}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Diagnose execution gap v2")
    parser.add_argument(
        "--config",
        default="config/strategy/composable/phase2/v4a_ml_regime_relaxed.yaml",
        help="Path to config",
    )

    args = parser.parse_args()

    diagnose_execution_gap_v2(Path(args.config))


if __name__ == "__main__":
    main()
