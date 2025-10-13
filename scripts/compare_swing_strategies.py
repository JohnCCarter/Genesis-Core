#!/usr/bin/env python3
"""
Swing Update Strategy Comparison - Ablation Study

Jämför FIXED vs DYNAMIC vs HYBRID swing update strategies
för symmetrisk Fibonacci exit-logik.

Testar:
- FIXED: Swing fastställs vid entry, uppdateras aldrig
- DYNAMIC: Uppdatera vid varje ny validerad swing
- HYBRID: Uppdatera endast om "bättre" swing (2% improvement)

Mätvärden:
- Total return, Sharpe ratio, win rate
- Partial exit rate, swing update frequency
- Max drawdown, average trade duration
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.backtest.engine import BacktestEngine
from core.backtest.metrics import calculate_metrics


def run_strategy_comparison(
    symbol: str = "tBTCUSD",
    timeframe: str = "1h",
    start_date: str = "2025-04-16",
    end_date: str = "2025-10-13",
    initial_capital: float = 10000.0,
) -> dict:
    """
    Run comparison between different swing update strategies.

    Args:
        symbol: Trading symbol
        timeframe: Timeframe for backtest
        start_date: Start date for backtest
        end_date: End date for backtest
        initial_capital: Initial capital

    Returns:
        Dictionary with results for each strategy
    """
    print(f"\n{'='*80}")
    print("SWING UPDATE STRATEGY COMPARISON")
    print(f"{'='*80}")
    print(f"Symbol: {symbol} | Timeframe: {timeframe}")
    print(f"Period: {start_date} to {end_date}")
    print(f"Initial Capital: ${initial_capital:,.0f}")
    print(f"{'='*80}")

    strategies = {
        "FIXED": {
            "swing_update_strategy": "fixed",
            "description": "Swing fixed at entry, never updated",
        },
        "DYNAMIC": {
            "swing_update_strategy": "dynamic",
            "swing_update_params": {
                "min_improvement_pct": 0.0,  # Update on any new swing
                "max_age_bars": 100,
                "allow_worse_swing": True,
                "log_updates": True,
            },
            "description": "Update on every new validated swing",
        },
        "HYBRID": {
            "swing_update_strategy": "hybrid",
            "swing_update_params": {
                "min_improvement_pct": 0.02,  # 2% improvement required
                "max_age_bars": 30,
                "allow_worse_swing": False,
                "log_updates": True,
            },
            "description": "Update only if 2%+ improvement",
        },
    }

    results = {}

    for strategy_name, config in strategies.items():
        print(f"\n[{strategy_name}] Running backtest...")
        print(f"Description: {config['description']}")

        # Configure HTF exit engine
        htf_exit_config = {
            "partial_1_pct": 0.40,  # 40% @ TP1
            "partial_2_pct": 0.30,  # 30% @ TP2
            "fib_threshold_atr": 0.3,  # 30% ATR
            "trail_atr_multiplier": 1.3,  # 1.3x ATR
            "enable_partials": True,
            "enable_trailing": True,
            "enable_structure_breaks": True,
            **config,  # Merge strategy-specific config
        }

        # Create and run backtest
        engine = BacktestEngine(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            htf_exit_config=htf_exit_config,
        )

        # Load data first
        engine.load_data()

        try:
            backtest_results = engine.run(
                policy={"symbol": symbol, "timeframe": timeframe},
                configs={
                    "thresholds": {
                        "entry_conf_overall": 0.5,  # Lower threshold to get signals
                        "regime_proba": {"ranging": 0.5, "bull": 0.5, "bear": 0.5, "balanced": 0.5},
                    },
                    "risk": {
                        "risk_map": [
                            [0.5, 0.1],  # 50% confidence = 10% position size
                            [0.6, 0.2],  # 60% confidence = 20% position size
                            [0.7, 0.3],  # 70% confidence = 30% position size
                            [0.8, 0.4],  # 80% confidence = 40% position size
                        ]
                    },
                },
                verbose=False,
            )

            # Calculate metrics
            metrics = calculate_metrics(backtest_results["trades"])

            # Extract swing update stats from exit engine
            swing_updates = engine.htf_exit_engine.swing_update_log
            update_count = len(swing_updates)

            # Count partial exits
            partial_exits = sum(
                1 for trade in backtest_results["trades"] if trade.get("is_partial", False)
            )
            total_exits = len(backtest_results["trades"])
            partial_rate = (partial_exits / total_exits * 100) if total_exits > 0 else 0.0

            results[strategy_name] = {
                "config": config,
                "metrics": metrics,
                "swing_updates": update_count,
                "partial_exits": partial_exits,
                "total_exits": total_exits,
                "partial_rate": partial_rate,
                "trades": backtest_results["trades"],
                "equity_curve": backtest_results["equity_curve"],
            }

            print(
                f"[{strategy_name}] [OK] Complete - {len(backtest_results['trades'])} trades, {update_count} swing updates"
            )

        except Exception as e:
            print(f"[{strategy_name}] [FAIL] Failed: {e}")
            results[strategy_name] = {"error": str(e)}

    return results


def print_comparison_report(results: dict) -> None:
    """Print detailed comparison report."""
    print(f"\n{'='*80}")
    print("COMPARISON REPORT")
    print(f"{'='*80}")

    # Header
    print(
        f"{'Strategy':<12} {'Return%':<10} {'Sharpe':<8} {'Win%':<8} {'Partial%':<10} {'Updates':<8} {'Trades':<8}"
    )
    print(f"{'-'*80}")

    for strategy_name, result in results.items():
        if "error" in result:
            print(
                f"{strategy_name:<12} {'ERROR':<10} {'ERROR':<8} {'ERROR':<8} {'ERROR':<10} {'ERROR':<8} {'ERROR':<8}"
            )
            continue

        metrics = result["metrics"]

        # Handle case when no trades were generated
        if result.get("total_exits", 0) == 0:
            print(
                f"{strategy_name:<12} "
                f"{'N/A':>8} "
                f"{'N/A':>7} "
                f"{'N/A':>7} "
                f"{'N/A':>9} "
                f"{result.get('swing_updates', 0):>7} "
                f"{result.get('total_exits', 0):>7}"
            )
        else:
            print(
                f"{strategy_name:<12} "
                f"{metrics.get('total_return_pct', 0):>8.1f}% "
                f"{metrics.get('sharpe_ratio', 0):>7.2f} "
                f"{metrics.get('win_rate', 0):>7.1f}% "
                f"{result.get('partial_rate', 0):>9.1f}% "
                f"{result.get('swing_updates', 0):>7} "
                f"{result.get('total_exits', 0):>7}"
            )

    # Detailed analysis
    print(f"\n{'='*80}")
    print("DETAILED ANALYSIS")
    print(f"{'='*80}")

    for strategy_name, result in results.items():
        if "error" in result:
            continue

        print(f"\n[{strategy_name}] {result['config']['description']}")
        if result.get("total_exits", 0) > 0:
            print(f"  Total Return: {result['metrics'].get('total_return_pct', 0):.1f}%")
            print(f"  Sharpe Ratio: {result['metrics'].get('sharpe_ratio', 0):.2f}")
            print(f"  Win Rate: {result['metrics'].get('win_rate', 0):.1f}%")
            print(f"  Max Drawdown: {result['metrics'].get('max_drawdown_pct', 0):.1f}%")
            print(
                f"  Avg Trade Duration: {result['metrics'].get('avg_trade_duration_hours', 0):.1f} hours"
            )
            print(
                f"  Partial Exit Rate: {result['partial_rate']:.1f}% ({result['partial_exits']}/{result['total_exits']})"
            )
            print(f"  Swing Updates: {result['swing_updates']}")

            if result["swing_updates"] > 0:
                print(f"  Updates per Trade: {result['swing_updates'] / result['total_exits']:.2f}")
        else:
            print("  Total Return: N/A (0 trades)")
            print("  Sharpe Ratio: N/A (0 trades)")
            print("  Win Rate: N/A (0 trades)")
            print("  Max Drawdown: N/A (0 trades)")
            print("  Avg Trade Duration: N/A (0 trades)")
            print("  Partial Exit Rate: N/A (0 trades)")
            print(f"  Swing Updates: {result.get('swing_updates', 0)}")


def analyze_swing_update_patterns(results: dict) -> None:
    """Analyze swing update patterns for strategies that logged updates."""
    print(f"\n{'='*80}")
    print("SWING UPDATE PATTERN ANALYSIS")
    print(f"{'='*80}")

    for strategy_name, result in results.items():
        if "error" in result or "swing_updates" not in result:
            continue

        if result["swing_updates"] == 0:
            print(f"\n[{strategy_name}] No swing updates recorded")
            continue

        print(f"\n[{strategy_name}] Swing Update Patterns:")

        # This would require access to the actual update log
        # For now, just show summary stats
        engine = None  # Would need to access the engine instance
        if hasattr(engine, "htf_exit_engine") and hasattr(
            engine.htf_exit_engine, "swing_update_log"
        ):
            updates = engine.htf_exit_engine.swing_update_log

            if updates:
                improvements = [u.get("improvement_pct", 0) for u in updates]
                reasons = [u.get("reason", "") for u in updates]

                print(f"  Average Improvement: {sum(improvements)/len(improvements)*100:.1f}%")
                print(f"  Most Common Reason: {max(set(reasons), key=reasons.count)}")

                # Show first few updates
                print("  Recent Updates:")
                for i, update in enumerate(updates[-3:]):  # Last 3 updates
                    print(
                        f"    {i+1}. {update.get('reason', 'Unknown')} "
                        f"({update.get('improvement_pct', 0)*100:.1f}% improvement)"
                    )


def save_results_to_file(results: dict, filename: str = None) -> str:
    """Save comparison results to JSON file."""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/swing_strategy_comparison_{timestamp}.json"

    # Convert to serializable format
    serializable_results = {}
    for strategy_name, result in results.items():
        if "error" in result:
            serializable_results[strategy_name] = {"error": result["error"]}
            continue

        serializable_results[strategy_name] = {
            "config": result["config"],
            "metrics": result["metrics"],
            "swing_updates": result["swing_updates"],
            "partial_exits": result["partial_exits"],
            "total_exits": result["total_exits"],
            "partial_rate": result["partial_rate"],
            "trades": result["trades"],
            # Note: equity_curve excluded due to size
        }

    # Ensure results directory exists
    Path(filename).parent.mkdir(parents=True, exist_ok=True)

    with open(filename, "w") as f:
        json.dump(serializable_results, f, indent=2, default=str)

    print(f"\n[SAVE] Results saved to: {filename}")
    return filename


def main():
    """Main execution function."""
    print("Swing Update Strategy Comparison - Genesis-Core")
    print("Comparing FIXED vs DYNAMIC vs HYBRID strategies")

    # Run comparison
    results = run_strategy_comparison()

    # Print report
    print_comparison_report(results)

    # Analyze patterns
    analyze_swing_update_patterns(results)

    # Save results
    filename = save_results_to_file(results)

    print(f"\n{'='*80}")
    print("COMPARISON COMPLETE")
    print(f"{'='*80}")
    print(f"Results saved to: {filename}")
    print("Use this data to determine optimal swing update strategy.")


if __name__ == "__main__":
    main()
