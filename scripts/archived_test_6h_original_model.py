#!/usr/bin/env python3
"""
Test Original 6h Model with Correct v17 Features
===============================================

Ett enkelt test för att verifiera att original modellen med v17 features
ger +14.10% return som dokumenterat.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.backtest.engine import BacktestEngine


def test_original_6h_model():
    """Test original 6h model with correct v17 features."""

    print("=" * 80)
    print("ORIGINAL 6H MODEL TEST - V17 FEATURES")
    print("Target: +14.10% return, 75% win rate, 4 trades")
    print("=" * 80)

    # Test configuration
    config = {
        "symbol": "tBTCUSD",
        "timeframe": "6h",
        "start_date": "2025-07-01",
        "end_date": "2025-10-13",
        "initial_capital": 10000.0,
        "commission_rate": 0.003,
        "slippage_rate": 0.0005,
        "warmup_bars": 50,
    }

    # Strategy configuration from 6h documentation
    strategy_config = {
        "cfg": {
            "thresholds": {
                "entry_conf_overall": 0.35,  # From 6h documentation
                "regime_proba": {"ranging": 0.5, "bull": 0.5, "bear": 0.5, "balanced": 0.5},
            },
            "risk": {
                "risk_map": [
                    [0.35, 0.1],  # 0.35 confidence -> 0.1 size
                    [0.45, 0.15],
                    [0.55, 0.2],
                    [0.65, 0.25],
                    [0.75, 0.3],
                ]
            },
            "exit": {
                "enabled": True,
                "exit_conf_threshold": 0.3,
                "max_hold_bars": 20,  # From 6h documentation
                "regime_aware_exits": True,
            },
            "gates": {
                "cooldown_bars": 0,
                "hysteresis_steps": 2,
            },
            "htf_exit_config": {
                "enable_partials": True,
                "enable_trailing": True,
                "enable_structure_breaks": True,
                "partial_1_pct": 0.40,  # From 6h documentation
                "partial_2_pct": 0.30,
                "fib_threshold_atr": 0.3,
                "trail_atr_multiplier": 1.3,
                "swing_update_strategy": "fixed",  # Symmetric Chamoun
            },
            "warmup_bars": 50,
        }
    }

    print(f"Testing {config['symbol']} {config['timeframe']}")
    print(f"Period: {config['start_date']} to {config['end_date']}")
    print(f"Entry Conf Overall: {strategy_config['cfg']['thresholds']['entry_conf_overall']}")
    print(f"Max Hold Bars: {strategy_config['cfg']['exit']['max_hold_bars']}")
    print(f"Partial 1 Pct: {strategy_config['cfg']['htf_exit_config']['partial_1_pct']}")
    print(
        f"Swing Update Strategy: {strategy_config['cfg']['htf_exit_config']['swing_update_strategy']}"
    )

    try:
        # Initialize backtest engine
        engine = BacktestEngine(
            symbol=config["symbol"],
            timeframe=config["timeframe"],
            start_date=config["start_date"],
            end_date=config["end_date"],
            initial_capital=config["initial_capital"],
            commission_rate=config["commission_rate"],
            slippage_rate=config["slippage_rate"],
            warmup_bars=config["warmup_bars"],
            htf_exit_config=strategy_config["cfg"]["htf_exit_config"],
        )

        print("\nLoading data...")
        if not engine.load_data():
            print("ERROR: Could not load data")
            return {"success": False, "error": "Data loading failed"}

        print(f"Loaded {len(engine.candles_df):,} candles")

        # Create policy
        policy = {"symbol": config["symbol"], "timeframe": config["timeframe"]}

        print("\nRunning backtest...")

        # Debug: Test evaluate_pipeline directly
        print("\n=== DEBUG: Testing evaluate_pipeline ===")
        from core.strategy.evaluate import evaluate_pipeline

        # Test with first few bars
        test_candles = {
            "open": [100000, 101000, 102000],
            "high": [101000, 102000, 103000],
            "low": [99000, 100000, 101000],
            "close": [100500, 101500, 102500],
            "volume": [1000, 1100, 1200],
        }

        test_result, test_meta = evaluate_pipeline(
            candles=test_candles, policy=policy, configs=strategy_config, state={}
        )

        print(f"Test Action: {test_result.get('action')}")
        print(f"Test Confidence: {test_result.get('confidence')}")
        print(f"Test Probas: {test_result.get('probas')}")
        print(f"Test Decision: {test_meta.get('decision', {})}")
        print(f"Test Configs: {strategy_config}")

        # Debug risk management
        from core.strategy.decision import decide

        test_decision, test_decision_meta = decide(
            policy=policy,
            probas=test_result.get("probas"),
            confidence=test_result.get("confidence"),
            regime=test_result.get("regime"),
            state={},
            risk_ctx=strategy_config.get("risk"),
            cfg=strategy_config,
        )
        print(f"Direct Decision: {test_decision}")
        print(f"Direct Decision Meta: {test_decision_meta}")
        print("=== END DEBUG ===\n")

        # Run backtest with verbose output
        results = engine.run(configs=strategy_config, policy=policy, verbose=True)

        if not results:
            print("ERROR: Backtest returned no results")
            return {"success": False, "error": "No backtest results"}

        # Extract key metrics
        summary = results.get("summary", {})
        trades = results.get("trades", [])

        print("\n" + "=" * 60)
        print("BACKTEST RESULTS")
        print("=" * 60)

        print(f"Total Trades: {len(trades)}")
        print(f"Total Return: {summary.get('total_return_pct', 0):.2f}%")
        print(f"Win Rate: {summary.get('win_rate', 0):.1f}%")
        print(f"Profit Factor: {summary.get('profit_factor', 0):.2f}")
        print(f"Sharpe Ratio: {summary.get('sharpe_ratio', 0):.2f}")
        print(f"Max Drawdown: {summary.get('max_drawdown_pct', 0):.2f}%")

        # Check for partial exits
        partial_exits = [t for t in trades if t.get("is_partial", False)]
        print(f"Partial Exits: {len(partial_exits)}")

        if len(partial_exits) > 0:
            print(f"Exit Rate: {len(partial_exits) / len(trades) * 100:.1f}%")

        # Compare with documented results
        print("\n" + "=" * 60)
        print("COMPARISON WITH 6H DOCUMENTATION")
        print("=" * 60)

        documented_return = 14.10
        documented_win_rate = 75.0
        documented_trades = 4

        actual_return = summary.get("total_return_pct", 0)
        actual_win_rate = summary.get("win_rate", 0)
        actual_trades = len(trades)

        print(
            f"Return: {actual_return:.2f}% vs {documented_return:.2f}% (diff: {actual_return - documented_return:+.2f}%)"
        )
        print(
            f"Win Rate: {actual_win_rate:.1f}% vs {documented_win_rate:.1f}% (diff: {actual_win_rate - documented_win_rate:+.1f}%)"
        )
        print(
            f"Trades: {actual_trades} vs {documented_trades} (diff: {actual_trades - documented_trades:+d})"
        )

        # Analysis
        print("\n" + "=" * 60)
        print("ANALYSIS")
        print("=" * 60)

        if actual_return > 10:
            print("[EXCELLENT] Return matches or exceeds documentation")
        elif actual_return > 5:
            print("[GOOD] Return is positive and significant")
        elif actual_return > 0:
            print("[MARGINAL] Return is positive but low")
        else:
            print("[POOR] Return is negative")

        if actual_win_rate > 70:
            print("[EXCELLENT] Win rate matches or exceeds documentation")
        elif actual_win_rate > 50:
            print("[GOOD] Win rate is above 50%")
        else:
            print("[POOR] Win rate is below 50%")

        if len(partial_exits) > 0:
            print("[SUCCESS] HTF Exit System is working (partial exits detected)")
        else:
            print("[WARNING] No partial exits detected - HTF system may not be working")

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/6h_original_model_test_{timestamp}.json"

        results_data = {
            "test_timestamp": datetime.now().isoformat(),
            "config": config,
            "strategy_config": strategy_config,
            "results": results,
            "comparison": {
                "documented": {
                    "return": documented_return,
                    "win_rate": documented_win_rate,
                    "trades": documented_trades,
                },
                "actual": {
                    "return": actual_return,
                    "win_rate": actual_win_rate,
                    "trades": actual_trades,
                },
                "differences": {
                    "return_diff": actual_return - documented_return,
                    "win_rate_diff": actual_win_rate - documented_win_rate,
                    "trades_diff": actual_trades - documented_trades,
                },
            },
        }

        with open(filename, "w") as f:
            json.dump(results_data, f, indent=2, default=str)

        print(f"\n[SAVE] Results saved to: {filename}")

        return {
            "success": True,
            "results": results,
            "comparison": results_data["comparison"],
            "filename": filename,
        }

    except Exception as e:
        print(f"ERROR: Backtest failed: {e}")
        import traceback

        traceback.print_exc()
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    test_original_6h_model()
