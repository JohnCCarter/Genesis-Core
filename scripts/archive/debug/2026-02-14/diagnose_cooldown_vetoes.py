#!/usr/bin/env python3
"""
Diagnose CooldownComponent veto behavior.

Captures veto reasons to understand why CooldownComponent vetoes 1871/2041
decisions with 0 trades.
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


def diagnose_cooldown(config_path: Path):
    """Diagnose CooldownComponent veto behavior."""

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

    # Track cooldown decisions
    cooldown_decisions = {
        "total": 0,
        "allowed": 0,
        "vetoed": 0,
        "veto_reasons": Counter(),
        "context_samples": [],
    }

    def diagnostic_hook(result, meta, candles):
        """Hook to capture cooldown decisions."""
        # Build context (same as ComponentContextBuilder)
        from core.strategy.components.context_builder import ComponentContextBuilder

        context = ComponentContextBuilder.build(result, meta, candles=candles)

        # Evaluate cooldown component only (skip others for diagnosis)
        cooldown_comp = [c for c in strategy.components if isinstance(c, CooldownComponent)]
        if cooldown_comp:
            cooldown = cooldown_comp[0]
            decision = cooldown.evaluate(context)

            cooldown_decisions["total"] += 1

            if decision.allowed:
                cooldown_decisions["allowed"] += 1
            else:
                cooldown_decisions["vetoed"] += 1
                cooldown_decisions["veto_reasons"][decision.reason] += 1

            # Capture first 10 samples for inspection
            if len(cooldown_decisions["context_samples"]) < 10:
                cooldown_decisions["context_samples"].append(
                    {
                        "bar_index": context.get("bar_index"),
                        "symbol": context.get("symbol"),
                        "allowed": decision.allowed,
                        "reason": decision.reason,
                        "metadata": decision.metadata,
                    }
                )

        return result, meta

    # Create engine with diagnostic hook
    engine = ComposableBacktestEngine(
        symbol="tBTCUSD",
        timeframe="1h",
        strategy=strategy,
        start_date="2024-01-01",
        end_date="2024-03-31",
        fast_window=True,
    )

    # Override evaluation_hook to use diagnostic hook instead
    engine.engine.evaluation_hook = diagnostic_hook

    # Load data
    print("Loading data...")
    if not engine.load_data():
        print("ERROR: Failed to load data")
        return

    # Run backtest (disabling fib gates for consistency with v4a)
    print("Running backtest with cooldown diagnostic...")
    override_configs = {
        "htf_fibonacci": {"enabled": False, "missing_policy": "allow"},
        "ltf_fibonacci": {"enabled": False, "missing_policy": "allow"},
    }
    results = engine.run(configs=override_configs, verbose=False)

    # Analyze results
    print(f"\n{'='*70}")
    print("COOLDOWN COMPONENT DIAGNOSIS")
    print(f"{'='*70}")
    print(f"Total decisions: {cooldown_decisions['total']}")
    print(f"Allowed: {cooldown_decisions['allowed']}")
    print(f"Vetoed: {cooldown_decisions['vetoed']}")
    print()
    print("Veto Reasons:")
    for reason, count in cooldown_decisions["veto_reasons"].most_common():
        pct = 100.0 * count / cooldown_decisions["total"] if cooldown_decisions["total"] > 0 else 0
        print(f"  {reason}: {count} ({pct:.1f}%)")
    print()
    print("First 10 Decision Samples:")
    for i, sample in enumerate(cooldown_decisions["context_samples"]):
        print(f"\n  [{i}] bar_index={sample['bar_index']}, symbol={sample['symbol']}")
        print(f"      allowed={sample['allowed']}, reason={sample['reason']}")
        print(f"      metadata={sample['metadata']}")

    print(f"\n{'='*70}")
    print(f"Backtest Trades: {results['summary']['num_trades']}")
    print(f"{'='*70}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Diagnose CooldownComponent vetoes")
    parser.add_argument(
        "--config",
        default="config/strategy/composable/phase2/v4a_ml_regime_relaxed.yaml",
        help="Path to config",
    )

    args = parser.parse_args()

    diagnose_cooldown(Path(args.config))


if __name__ == "__main__":
    main()
