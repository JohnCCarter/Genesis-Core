#!/usr/bin/env python3
"""
Sanity Check #2: size==0 reason sniff.

Extracts reasons/flags from meta["decision"] to classify why 1032 component-allowed
actions had size=0 (never reached execute_action).

No code changes - pure read-only inspection of existing decision metadata.
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


def sanity_check_size_zero_reasons(config_path: Path):
    """Sniff size==0 reasons from meta["decision"] without code changes."""

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

    # Track size==0 reasons
    size_data = {
        "total_entry_actions": 0,
        "component_allowed": 0,
        "component_vetoed": 0,
        "size_nonzero": 0,
        "size_zero": 0,
        "size_zero_reasons": Counter(),
        "size_zero_samples": [],
        "meta_keys_seen": set(),
        "decision_keys_seen": set(),
    }

    def evaluation_tracker(result, meta, candles):
        """Track size and reasons from meta["decision"]."""
        from core.strategy.components.context_builder import ComponentContextBuilder

        context = ComponentContextBuilder.build(result, meta, candles=candles)

        action = result.get("action", "NONE")
        bar_index = context.get("bar_index", -1)

        # Track meta structure
        for key in meta.keys():
            size_data["meta_keys_seen"].add(key)

        decision_meta = meta.get("decision", {})
        if decision_meta:
            for key in decision_meta.keys():
                size_data["decision_keys_seen"].add(key)

        if action in ("LONG", "SHORT"):
            size_data["total_entry_actions"] += 1

            # Evaluate components
            decision = strategy.evaluate(context)

            if decision.allowed:
                size_data["component_allowed"] += 1

                # Extract size from meta (EXACT field BacktestEngine reads)
                size = meta.get("decision", {}).get("size", 0.0)

                if size > 0:
                    size_data["size_nonzero"] += 1
                else:
                    size_data["size_zero"] += 1

                    # Extract reasons from meta["decision"]
                    reasons = decision_meta.get("reasons", [])

                    # Classify reason for size=0
                    if not reasons:
                        reason = "no_reasons_in_meta"
                    else:
                        # Check for known blocking reasons
                        reason_str = "|".join(reasons)
                        if "POSITION_OPEN" in reason_str or "NO_STACK" in reason_str:
                            reason = "position_already_open"
                        elif "RISK_CAP" in reason_str:
                            reason = "risk_cap"
                        elif "SIZE_ZERO" in reason_str or "MIN_NOTIONAL" in reason_str:
                            reason = "size_too_small_or_notional"
                        elif "HTF_BLOCK" in reason_str or "HTF_FIB" in reason_str:
                            reason = "htf_fibonacci_block"
                        elif "LTF_BLOCK" in reason_str or "LTF_FIB" in reason_str:
                            reason = "ltf_fibonacci_block"
                        elif "HYSTERESIS" in reason_str:
                            reason = "hysteresis"
                        elif "COOLDOWN" in reason_str:
                            reason = "cooldown_internal"
                        else:
                            reason = f"other_{reasons[0]}" if reasons else "unknown"

                    size_data["size_zero_reasons"][reason] += 1

                    # Store sample
                    if len(size_data["size_zero_samples"]) < 100:
                        size_data["size_zero_samples"].append(
                            {
                                "bar_index": bar_index,
                                "action": action,
                                "size": size,
                                "reason": reason,
                                "reasons_list": reasons,
                                "decision_keys": list(decision_meta.keys()),
                            }
                        )
            else:
                size_data["component_vetoed"] += 1

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
    print("Running backtest with size==0 reason sniffing...")
    override_configs = {
        "htf_fibonacci": {"enabled": False, "missing_policy": "allow"},
        "ltf_fibonacci": {"enabled": False, "missing_policy": "allow"},
    }
    results = engine.run(configs=override_configs, verbose=False)

    # Analysis
    print(f"\n{'='*90}")
    print("SIZE==0 REASON SNIFF (Sanity Check #2)")
    print(f"{'='*90}")
    print()

    print("Entry Actions Breakdown:")
    print(f"  Total entry actions (LONG/SHORT): {size_data['total_entry_actions']}")
    print(
        f"  Component allowed: {size_data['component_allowed']} ({100.0 * size_data['component_allowed'] / size_data['total_entry_actions']:.1f}%)"
    )
    print(
        f"  Component vetoed: {size_data['component_vetoed']} ({100.0 * size_data['component_vetoed'] / size_data['total_entry_actions']:.1f}%)"
    )
    print()

    print("Component-Allowed Breakdown:")
    print(
        f"  size > 0: {size_data['size_nonzero']} ({100.0 * size_data['size_nonzero'] / size_data['component_allowed']:.1f}%)"
    )
    print(
        f"  size == 0: {size_data['size_zero']} ({100.0 * size_data['size_zero'] / size_data['component_allowed']:.1f}%)"
    )
    print()

    if size_data["size_zero_reasons"]:
        print("size==0 Reasons (from meta['decision']['reasons']):")
        for reason, count in size_data["size_zero_reasons"].most_common():
            print(f"  {reason}: {count} ({100.0 * count / size_data['size_zero']:.1f}%)")
    else:
        print("size==0 Reasons: No reasons found in meta")

    print()
    print("Meta Structure Observed:")
    print(f"  meta keys: {sorted(size_data['meta_keys_seen'])}")
    print(f"  meta['decision'] keys: {sorted(size_data['decision_keys_seen'])}")
    print()

    print("size==0 Samples (first 20):")
    print(f"{'bar_index':<12} {'action':<8} {'size':<8} {'reason':<30} {'reasons_list':<50}")
    print("-" * 110)
    for sample in size_data["size_zero_samples"][:20]:
        reasons_str = ",".join(sample["reasons_list"][:3]) if sample["reasons_list"] else "none"
        print(
            f"{sample['bar_index']:<12} {sample['action']:<8} {sample['size']:<8.4f} {sample['reason']:<30} {reasons_str:<50}"
        )

    print()
    print("Decision Metadata Keys (from samples):")
    all_decision_keys = set()
    for sample in size_data["size_zero_samples"]:
        all_decision_keys.update(sample["decision_keys"])
    print(f"  Keys found: {sorted(all_decision_keys)}")

    print(f"\n{'='*90}")
    print(f"Backtest Trades: {results['summary']['num_trades']}")
    print(f"{'='*90}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Size==0 reason sniff")
    parser.add_argument(
        "--config",
        default="config/strategy/composable/phase2/v4a_ml_regime_relaxed.yaml",
        help="Path to config",
    )

    args = parser.parse_args()

    sanity_check_size_zero_reasons(Path(args.config))


if __name__ == "__main__":
    main()
