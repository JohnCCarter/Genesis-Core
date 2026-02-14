"""
Composable Strategy POC - Backtest Runner

Runs backtests with different component combinations to evaluate
which components add value.

Usage:
    python scripts/run_composable_backtest_poc.py config/strategy/composable/poc/v0_baseline.yaml
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import argparse
import json
from datetime import datetime

import yaml

from core.strategy.components import ComposableStrategy
from core.strategy.components.atr_filter import ATRFilterComponent
from core.strategy.components.attribution import AttributionTracker
from core.strategy.components.htf_gate import HTFGateComponent
from core.strategy.components.ml_confidence import MLConfidenceComponent


def build_component(component_config: dict):
    """
    Build a component from config.

    Args:
        component_config: Dict with 'type' and 'params' keys.

    Returns:
        StrategyComponent instance.
    """
    component_type = component_config["type"]
    params = component_config.get("params", {})

    if component_type == "ml_confidence":
        return MLConfidenceComponent(**params)
    elif component_type == "htf_gate":
        return HTFGateComponent(**params)
    elif component_type == "atr_filter":
        return ATRFilterComponent(**params)
    else:
        raise ValueError(f"Unknown component type: {component_type}")


def load_config(config_path: Path) -> dict:
    """Load YAML config file."""
    with open(config_path) as f:
        return yaml.safe_load(f)


def run_backtest_poc(config_path: Path):
    """
    Run POC backtest with composable strategy.

    This is a simplified runner that demonstrates component evaluation
    and attribution tracking. For full backtest integration, this would
    need to integrate with BacktestEngine.

    Args:
        config_path: Path to POC config YAML.
    """
    config = load_config(config_path)

    print(f"Loading config: {config_path.name}")
    print(f"Description: {config.get('description', 'N/A')}")
    print(f"Symbol: {config['symbol']}, Timeframe: {config['timeframe']}")
    print(f"Period: {config['start_date']} to {config['end_date']}")
    print()

    components = [build_component(c) for c in config["components"]]
    strategy = ComposableStrategy(components)
    tracker = AttributionTracker()

    print(f"Components loaded: {[c.name() for c in components]}")
    print()

    print("=" * 70)
    print("POC BACKTEST SIMULATION")
    print("=" * 70)
    print()
    print("NOTE: This is a POC demonstration showing component evaluation.")
    print("      Full backtest integration requires connecting to BacktestEngine.")
    print("      For now, we simulate with dummy context data.")
    print()

    dummy_contexts = [
        {"ml_confidence": 0.6, "htf_regime": "trending", "atr": 0.02, "atr_ma": 0.015},
        {"ml_confidence": 0.4, "htf_regime": "trending", "atr": 0.02, "atr_ma": 0.015},
        {"ml_confidence": 0.7, "htf_regime": "ranging", "atr": 0.02, "atr_ma": 0.015},
        {"ml_confidence": 0.6, "htf_regime": "trending", "atr": 0.01, "atr_ma": 0.015},
        {"ml_confidence": 0.8, "htf_regime": "bull", "atr": 0.025, "atr_ma": 0.015},
    ]

    for i, context in enumerate(dummy_contexts, 1):
        decision = strategy.evaluate(context)
        tracker.record(decision)

        print(f"Bar {i}: {context}")
        print(f"  Decision: {'ALLOWED' if decision.allowed else 'VETOED'}")
        print(f"  Confidence: {decision.confidence:.3f}")
        if decision.veto_component:
            print(f"  Veto by: {decision.veto_component} ({decision.veto_reason})")
        print()

    print(tracker.get_report())

    output_dir = Path("results/composable_poc")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{config_path.stem}_results.json"
    results = {
        "config": config_path.name,
        "description": config.get("description"),
        "timestamp": datetime.now().isoformat(),
        "components": [c.name() for c in components],
        "tracker_stats": {
            "total_decisions": tracker.total_decisions,
            "total_allowed": tracker.total_allowed,
            "total_vetoed": tracker.total_vetoed,
            "component_stats": {
                name: {
                    "evaluations": stats.total_evaluations,
                    "vetoes": stats.veto_count,
                    "avg_confidence": (
                        sum(stats.confidences) / len(stats.confidences)
                        if stats.confidences
                        else 0.0
                    ),
                }
                for name, stats in tracker.stats.items()
            },
        },
    }

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Run composable strategy POC backtest")
    parser.add_argument("config", type=Path, help="Path to POC config YAML")
    args = parser.parse_args()

    if not args.config.exists():
        print(f"Error: Config file not found: {args.config}")
        sys.exit(1)

    run_backtest_poc(args.config)


if __name__ == "__main__":
    main()
