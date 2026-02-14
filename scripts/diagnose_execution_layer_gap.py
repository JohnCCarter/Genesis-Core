#!/usr/bin/env python3
"""
Diagnose Gap #3: Execution layer rejection reasons.

Captures why allowed signals (action LONG/SHORT) don't become trades.
Classification: action≠NONE → size>0 → execute_action(executed)

Also extracts EV distribution for three populations:
- (a) All decisions
- (b) ML+Regime allowed (pre EVGate/Cooldown)
- (c) Executed trades
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


def diagnose_execution_gap(config_path: Path):
    """Diagnose execution layer rejection reasons and EV distribution."""

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

    # Track execution decisions
    execution_data = {
        "total_decisions": 0,
        "action_none": 0,
        "action_entry": 0,  # LONG or SHORT
        "size_zero": 0,
        "size_nonzero": 0,
        "executed": 0,
        "rejected": 0,
        "rejection_samples": [],  # Store samples for each rejection reason
        "execution_samples": [],  # Store executed trade samples
        "ev_all": [],  # EV for all decisions
        "ev_ml_regime_allowed": [],  # EV for decisions passing ML+Regime (pre EVGate)
        "ev_executed": [],  # EV for executed trades
    }

    # Track position state for rejection analysis
    position_state = {"current": "flat"}  # flat, long, short

    def diagnostic_hook(result, meta, candles):
        """Hook to capture execution layer decisions."""
        from core.strategy.components.context_builder import ComponentContextBuilder

        context = ComponentContextBuilder.build(result, meta, candles=candles)

        execution_data["total_decisions"] += 1

        # Extract EV for all decisions
        ev = context.get("expected_value", None)
        if ev is not None:
            execution_data["ev_all"].append(ev)

        # Check if ML+Regime allowed (before EVGate/Cooldown)
        ml_comp = [c for c in strategy.components if isinstance(c, MLConfidenceComponent)][0]
        regime_comp = [c for c in strategy.components if isinstance(c, RegimeFilterComponent)][0]

        ml_result = ml_comp.evaluate(context)
        regime_result = regime_comp.evaluate(context)

        if ml_result.allowed and regime_result.allowed:
            # This would have been allowed by ML+Regime (before EVGate/Cooldown)
            if ev is not None:
                execution_data["ev_ml_regime_allowed"].append(ev)

        # Now evaluate full component chain
        decision = strategy.evaluate(context)

        action = result.get("action", "NONE")
        bar_index = context.get("bar_index", -1)

        if action == "NONE":
            execution_data["action_none"] += 1
        elif action in ("LONG", "SHORT"):
            execution_data["action_entry"] += 1

            # Check if components allowed
            if not decision.allowed:
                # Components vetoed (this shouldn't happen if action≠NONE, but check anyway)
                execution_data["rejected"] += 1
                if len(execution_data["rejection_samples"]) < 100:
                    execution_data["rejection_samples"].append(
                        {
                            "bar_index": bar_index,
                            "action": action,
                            "position_state": position_state["current"],
                            "size": 0.0,
                            "executed": False,
                            "reason": f"component_veto_{decision.veto_component}",
                            "ev": ev,
                        }
                    )
                return result, meta

            # Components allowed - check size (will be computed by engine)
            # We can't easily capture size here (computed in engine), so we'll infer from execution
            # For now, just track that we got here

        return result, meta

    def post_execution_hook_tracker(symbol, bar_index, action, executed):
        """Track post-execution results."""
        if action in ("LONG", "SHORT"):
            if executed:
                execution_data["executed"] += 1
                execution_data["size_nonzero"] += 1
                position_state["current"] = action.lower()  # Update position state

                # Store execution sample
                if len(execution_data["execution_samples"]) < 100:
                    execution_data["execution_samples"].append(
                        {
                            "bar_index": bar_index,
                            "action": action,
                            "position_state": "flat",  # Was flat before entry
                            "size": "nonzero",
                            "executed": True,
                            "reason": "executed",
                        }
                    )
            else:
                execution_data["rejected"] += 1

                # Infer rejection reason based on position state
                if position_state["current"] == action.lower():
                    reason = "position_already_open_same_direction"
                elif position_state["current"] != "flat":
                    reason = "position_already_open_opposite_direction"
                else:
                    reason = "size_zero_or_risk_limit"

                # Store rejection sample
                if len(execution_data["rejection_samples"]) < 100:
                    execution_data["rejection_samples"].append(
                        {
                            "bar_index": bar_index,
                            "action": action,
                            "position_state": position_state["current"],
                            "size": 0.0,
                            "executed": False,
                            "reason": reason,
                        }
                    )

    # Create engine with diagnostic hooks
    engine = ComposableBacktestEngine(
        symbol="tBTCUSD",
        timeframe="1h",
        strategy=strategy,
        start_date="2024-01-01",
        end_date="2024-03-31",
        fast_window=True,
    )

    # Override evaluation_hook to inject diagnostic
    engine.engine.evaluation_hook = diagnostic_hook

    # Override post_execution_hook to track execution results
    original_post_hook = engine.engine.post_execution_hook

    def combined_post_hook(symbol, bar_index, action, executed):
        # Call original hook (for CooldownComponent)
        if original_post_hook is not None:
            original_post_hook(symbol, bar_index, action, executed)
        # Call tracker
        post_execution_hook_tracker(symbol, bar_index, action, executed)

    engine.engine.post_execution_hook = combined_post_hook

    # Load data
    print("Loading data...")
    if not engine.load_data():
        print("ERROR: Failed to load data")
        return

    # Run backtest (disabling fib gates for consistency)
    print("Running backtest with execution layer diagnostic...")
    override_configs = {
        "htf_fibonacci": {"enabled": False, "missing_policy": "allow"},
        "ltf_fibonacci": {"enabled": False, "missing_policy": "allow"},
    }
    results = engine.run(configs=override_configs, verbose=False)

    # Analyze results
    print(f"\n{'='*80}")
    print("EXECUTION LAYER GAP ANALYSIS (Gap #3)")
    print(f"{'='*80}")
    print(f"Total decisions: {execution_data['total_decisions']}")
    print(
        f"Action NONE: {execution_data['action_none']} ({100.0 * execution_data['action_none'] / execution_data['total_decisions']:.1f}%)"
    )
    print(
        f"Action LONG/SHORT: {execution_data['action_entry']} ({100.0 * execution_data['action_entry'] / execution_data['total_decisions']:.1f}%)"
    )
    print()
    print(
        f"Executed: {execution_data['executed']} ({100.0 * execution_data['executed'] / execution_data['action_entry']:.1f}% of entry actions)"
    )
    print(
        f"Rejected: {execution_data['rejected']} ({100.0 * execution_data['rejected'] / execution_data['action_entry']:.1f}% of entry actions)"
    )
    print()

    # Classify rejection reasons
    rejection_reasons = Counter([s["reason"] for s in execution_data["rejection_samples"]])
    print("Rejection Reasons (from samples):")
    for reason, count in rejection_reasons.most_common():
        print(f"  {reason}: {count}")

    # Show rejection samples
    print("\nRejection Samples (first 20):")
    print(
        f"{'bar_index':<12} {'action':<8} {'pos_state':<12} {'size':<8} {'executed':<10} {'reason':<40}"
    )
    print("-" * 90)
    for sample in execution_data["rejection_samples"][:20]:
        print(
            f"{sample['bar_index']:<12} {sample['action']:<8} {sample['position_state']:<12} {sample['size']:<8.4f} {sample['executed']!s:<10} {sample['reason']:<40}"
        )

    # Show execution samples
    print("\nExecution Samples (first 20):")
    print(
        f"{'bar_index':<12} {'action':<8} {'pos_state':<12} {'size':<8} {'executed':<10} {'reason':<40}"
    )
    print("-" * 90)
    for sample in execution_data["execution_samples"][:20]:
        print(
            f"{sample['bar_index']:<12} {sample['action']:<8} {sample['position_state']:<12} {sample['size']:<8} {sample['executed']!s:<10} {sample['reason']:<40}"
        )

    # EV distribution analysis
    print(f"\n{'='*80}")
    print("EV DISTRIBUTION ANALYSIS")
    print(f"{'='*80}")

    def print_ev_stats(ev_list, label):
        if not ev_list:
            print(f"{label}: No data")
            return

        import numpy as np

        ev_array = np.array(ev_list)
        print(f"\n{label}:")
        print(f"  Samples: {len(ev_array)}")
        print(f"  Mean: {ev_array.mean():.4f}")
        print(f"  Std: {ev_array.std():.4f}")
        print(f"  Min: {ev_array.min():.4f}")
        print(f"  Max: {ev_array.max():.4f}")
        print("  Percentiles:")
        for p in [25, 50, 75, 80, 85, 90, 95]:
            print(f"    p{p}: {np.percentile(ev_array, p):.4f}")

    print_ev_stats(execution_data["ev_all"], "(a) All Decisions")
    print_ev_stats(
        execution_data["ev_ml_regime_allowed"], "(b) ML+Regime Allowed (pre EVGate/Cooldown)"
    )
    print_ev_stats(execution_data["ev_executed"], "(c) Executed Trades")

    print(f"\n{'='*80}")
    print(f"Backtest Trades: {results['summary']['num_trades']}")
    print(f"{'='*80}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Diagnose execution layer gap (Gap #3)")
    parser.add_argument(
        "--config",
        default="config/strategy/composable/phase2/v4a_ml_regime_relaxed.yaml",
        help="Path to config",
    )

    args = parser.parse_args()

    diagnose_execution_gap(Path(args.config))


if __name__ == "__main__":
    main()
