#!/usr/bin/env python3
"""
Sanity Check #1: EVGate percentile reconciliation.

Verifies that EV percentiles match veto rates using EXACT same field that EVGate reads.
Tests on same sample/fixture to ensure determinism.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import os

os.environ["GENESIS_FAST_WINDOW"] = "1"
os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"

import yaml
import numpy as np

from core.backtest.composable_engine import ComposableBacktestEngine
from core.strategy.components.ml_confidence import MLConfidenceComponent
from core.strategy.components.regime_filter import RegimeFilterComponent
from core.strategy.components.ev_gate import EVGateComponent
from core.strategy.components.cooldown import CooldownComponent
from core.strategy.components.strategy import ComposableStrategy


def sanity_check_evgate_percentiles(config_path: Path):
    """Verify EVGate percentiles match veto rates on same sample."""

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

    # Track EV values and EVGate decisions
    ev_data = {
        "all_ev": [],  # All decisions with EV
        "component_allowed_ev": [],  # Decisions passing ML+Regime (pre EVGate)
        "evgate_decisions": [],  # EVGate evaluation results
    }

    def evaluation_tracker(result, meta, candles):
        """Track EV values and EVGate decisions."""
        from core.strategy.components.context_builder import ComponentContextBuilder

        context = ComponentContextBuilder.build(result, meta, candles=candles)

        # Extract EV from context (EXACT field EVGate reads)
        ev = context.get("expected_value")

        if ev is not None:
            ev_data["all_ev"].append(ev)

        # Check if ML+Regime allowed (pre EVGate)
        ml_comp = [c for c in strategy.components if isinstance(c, MLConfidenceComponent)][0]
        regime_comp = [c for c in strategy.components if isinstance(c, RegimeFilterComponent)][0]

        ml_result = ml_comp.evaluate(context)
        regime_result = regime_comp.evaluate(context)

        if ml_result.allowed and regime_result.allowed:
            if ev is not None:
                ev_data["component_allowed_ev"].append(ev)

            # Now evaluate EVGate on this decision
            evgate_comp = [c for c in strategy.components if isinstance(c, EVGateComponent)]
            if evgate_comp:
                evgate = evgate_comp[0]
                evgate_result = evgate.evaluate(context)
                ev_data["evgate_decisions"].append(
                    {
                        "ev": ev,
                        "allowed": evgate_result.allowed,
                        "reason": evgate_result.reason,
                    }
                )

        return result, meta

    # Create engine with tracker
    engine = ComposableBacktestEngine(
        symbol="tBTCUSD",
        timeframe="1h",
        strategy=strategy,
        start_date="2024-01-01",
        end_date="2024-03-31",
        fast_window=True,
    )

    engine.engine.evaluation_hook = evaluation_tracker

    # Load data
    print("Loading data...")
    if not engine.load_data():
        print("ERROR: Failed to load data")
        return

    # Run backtest
    print("Running backtest with EVGate reconciliation...")
    override_configs = {
        "htf_fibonacci": {"enabled": False, "missing_policy": "allow"},
        "ltf_fibonacci": {"enabled": False, "missing_policy": "allow"},
    }
    results = engine.run(configs=override_configs, verbose=False)

    # Analysis
    print(f"\n{'='*90}")
    print("EVGATE PERCENTILE RECONCILIATION (Sanity Check #1)")
    print(f"{'='*90}")
    print()

    # (a) All decisions with EV
    if ev_data["all_ev"]:
        all_ev = np.array(ev_data["all_ev"])
        print("(a) All Decisions with EV:")
        print(f"  Samples: {len(all_ev)}")
        print(f"  Mean: {all_ev.mean():.4f}")
        print(f"  Std: {all_ev.std():.4f}")
        print(f"  Min: {all_ev.min():.4f}")
        print(f"  Max: {all_ev.max():.4f}")
        print("  Percentiles:")
        for p in [25, 50, 75, 80, 85, 90, 95]:
            print(f"    p{p}: {np.percentile(all_ev, p):.4f}")
    else:
        print("(a) All Decisions: No EV data")

    print()

    # (b) ML+Regime allowed (pre EVGate)
    if ev_data["component_allowed_ev"]:
        allowed_ev = np.array(ev_data["component_allowed_ev"])
        print("(b) ML+Regime Allowed (pre EVGate):")
        print(f"  Samples: {len(allowed_ev)}")
        print(f"  Mean: {allowed_ev.mean():.4f}")
        print(f"  Std: {allowed_ev.std():.4f}")
        print(f"  Min: {allowed_ev.min():.4f}")
        print(f"  Max: {allowed_ev.max():.4f}")
        print("  Percentiles:")
        for p in [25, 50, 75, 80, 85, 90, 95]:
            percentile_val = np.percentile(allowed_ev, p)
            print(f"    p{p}: {percentile_val:.4f}")
    else:
        print("(b) ML+Regime Allowed: No EV data")

    print()

    # (c) EVGate decisions
    if ev_data["evgate_decisions"]:
        total_evgate = len(ev_data["evgate_decisions"])
        allowed_count = sum(1 for d in ev_data["evgate_decisions"] if d["allowed"])
        vetoed_count = total_evgate - allowed_count
        veto_rate = vetoed_count / total_evgate if total_evgate > 0 else 0.0

        print("(c) EVGate Decisions (on ML+Regime allowed):")
        print(f"  Total: {total_evgate}")
        print(f"  Allowed: {allowed_count} ({100.0 * allowed_count / total_evgate:.1f}%)")
        print(f"  Vetoed: {vetoed_count} ({100.0 * veto_rate:.1f}%)")
        print()

        # Get EVGate min_ev threshold from config
        evgate_cfg = next((c for c in config.get("components", []) if c["type"] == "ev_gate"), None)
        min_ev = evgate_cfg["params"]["min_ev"] if evgate_cfg else 0.0

        print(f"EVGate Threshold: min_ev={min_ev:.4f}")
        print()

        # Compute ACTUAL percentile that matches veto rate
        evgate_ev_values = [d["ev"] for d in ev_data["evgate_decisions"] if d["ev"] is not None]
        if evgate_ev_values:
            evgate_ev_array = np.array(evgate_ev_values)
            actual_percentile = 100.0 * veto_rate

            # Find what EV value corresponds to actual veto rate
            actual_threshold = np.percentile(evgate_ev_array, actual_percentile)

            print("Reconciliation:")
            print(f"  Configured min_ev: {min_ev:.4f}")
            print(f"  Actual veto rate: {100.0 * veto_rate:.1f}%")
            print(f"  Corresponding percentile: p{actual_percentile:.1f} = {actual_threshold:.4f}")
            print()

            # Check if threshold matches percentile
            expected_percentile = 100.0 - actual_percentile  # e.g., 73% veto = p27
            expected_threshold = np.percentile(evgate_ev_array, expected_percentile)
            print(
                f"  Expected threshold for {100.0 * veto_rate:.1f}% veto: p{expected_percentile:.1f} = {expected_threshold:.4f}"
            )
            print()

            # Sanity check: Does min_ev match expected_threshold?
            threshold_diff = abs(min_ev - expected_threshold)
            if threshold_diff < 0.01:
                print(
                    f"  ✅ MATCH: min_ev ({min_ev:.4f}) ≈ p{expected_percentile:.1f} ({expected_threshold:.4f})"
                )
            else:
                print(
                    f"  ❌ MISMATCH: min_ev ({min_ev:.4f}) != p{expected_percentile:.1f} ({expected_threshold:.4f})"
                )
                print(f"  Difference: {threshold_diff:.4f}")

        # Show sample of vetoed vs allowed
        print()
        print("Sample EVGate Decisions (first 20):")
        print(f"{'EV':<12} {'Allowed':<10} {'Reason':<30}")
        print("-" * 52)
        for decision in ev_data["evgate_decisions"][:20]:
            ev_str = f"{decision['ev']:.4f}" if decision["ev"] is not None else "N/A"
            print(f"{ev_str:<12} {str(decision['allowed']):<10} {decision['reason']:<30}")

    else:
        print("(c) EVGate Decisions: No data")

    print(f"\n{'='*90}")
    print(f"Backtest Trades: {results['summary']['num_trades']}")
    print(f"{'='*90}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="EVGate percentile reconciliation")
    parser.add_argument(
        "--config",
        default="config/strategy/composable/phase2/v4b_ev_09.yaml",
        help="Path to config (default: v4b_ev_09 for testing)",
    )

    args = parser.parse_args()

    sanity_check_evgate_percentiles(Path(args.config))


if __name__ == "__main__":
    main()
