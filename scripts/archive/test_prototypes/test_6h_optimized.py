#!/usr/bin/env python3
"""
Test 6h timeframe with optimized configuration from documentation.
"""

import sys

sys.path.append("src")

from datetime import datetime

from config.timeframe_configs import get_timeframe_backtest_config, get_timeframe_config
from core.backtest.engine import BacktestEngine


def test_6h_optimized():
    """Test 6h timeframe with optimized configuration."""
    print("=== 6H TIMEFRAME OPTIMIZATION TEST ===")
    print(f"Test startad: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Get optimized 6h configuration
    config = get_timeframe_backtest_config("6h")
    strategy_config = get_timeframe_config("6h")

    print("\n=== KONFIGURATION ===")
    print(f"Symbol: {config['symbol']}")
    print(f"Timeframe: {config['timeframe']}")
    print(f"Period: {config['start_date']} to {config['end_date']}")
    print(f"Initial Capital: ${config['initial_capital']:,.2f}")
    print(f"Commission: {config['commission_rate']*100:.3f}%")
    print(f"Slippage: {config['slippage_rate']*100:.3f}%")
    print(f"Warmup Bars: {config['warmup_bars']}")

    print("\n=== STRATEGY CONFIG ===")
    print(f"Entry Conf Overall: {strategy_config['thresholds']['entry_conf_overall']}")
    print(f"Exit Conf Threshold: {strategy_config['exit']['exit_conf_threshold']}")
    print(f"Max Hold Bars: {strategy_config['exit']['max_hold_bars']}")
    print(f"Risk Map: {strategy_config['risk']['risk_map'][0]}")
    print(f"Partial 1 Pct: {strategy_config['htf_exit_config']['partial_1_pct']}")
    print(f"Fib Threshold ATR: {strategy_config['htf_exit_config']['fib_threshold_atr']}")
    print(f"Trail ATR Multiplier: {strategy_config['htf_exit_config']['trail_atr_multiplier']}")

    # Initialize backtest engine with all parameters
    engine = BacktestEngine(
        symbol=config["symbol"],
        timeframe=config["timeframe"],
        start_date=config["start_date"],
        end_date=config["end_date"],
        initial_capital=config["initial_capital"],
        commission_rate=config["commission_rate"],
        slippage_rate=config["slippage_rate"],
        warmup_bars=config["warmup_bars"],
        htf_exit_config=config.get("htf_exit_config", {}),
    )

    # Load data
    print("\n=== LADDAR DATA ===")
    try:
        success = engine.load_data()
        if success:
            print("Data laddad framgångsrikt")
        else:
            print("Fel vid dataladdning")
            return
    except Exception as e:
        print(f"Fel vid dataladdning: {e}")
        return

    print("\n=== KÖRER BACKTEST ===")
    try:
        results = engine.run(configs=strategy_config)

        if results and "summary" in results:
            summary = results["summary"]
            print("\n=== RESULTAT ===")
            print(f"Success: {summary.get('success', False)}")
            print(f"Performance Score: {summary.get('performance_score', 0)}/5")
            print(f"Trades: {summary.get('num_trades', 0)}")
            print(f"Return: {summary.get('total_return', 0):.2f}%")
            print(f"Win Rate: {summary.get('win_rate', 0):.2f}%")
            print(f"Profit Factor: {summary.get('profit_factor', 0):.2f}")
            print(f"Sharpe: {summary.get('sharpe_ratio', 0):.2f}")
            print(f"Max Drawdown: {summary.get('max_drawdown', 0):.2f}%")
            print(f"Avg Trade Duration: {summary.get('avg_trade_duration_hours', 0):.1f} hours")

            # Compare with documented results
            print("\n=== JÄMFÖRELSE MED DOKUMENTATION ===")
            documented_return = 14.10
            documented_win_rate = 75.0
            documented_trades = 4
            documented_profit_factor = 2.20
            documented_sharpe = 0.29
            documented_drawdown = 0.00

            actual_return = summary.get("total_return", 0)
            actual_win_rate = summary.get("win_rate", 0)
            actual_trades = summary.get("num_trades", 0)
            actual_profit_factor = summary.get("profit_factor", 0)
            actual_sharpe = summary.get("sharpe_ratio", 0)
            actual_drawdown = summary.get("max_drawdown", 0)

            print(
                f"Return: {actual_return:.2f}% (Dokumenterat: {documented_return:.2f}%) - {'OK' if abs(actual_return - documented_return) < 1.0 else 'MISS'}"
            )
            print(
                f"Win Rate: {actual_win_rate:.1f}% (Dokumenterat: {documented_win_rate:.1f}%) - {'OK' if abs(actual_win_rate - documented_win_rate) < 5.0 else 'MISS'}"
            )
            print(
                f"Trades: {actual_trades} (Dokumenterat: {documented_trades}) - {'OK' if actual_trades == documented_trades else 'MISS'}"
            )
            print(
                f"Profit Factor: {actual_profit_factor:.2f} (Dokumenterat: {documented_profit_factor:.2f}) - {'OK' if abs(actual_profit_factor - documented_profit_factor) < 0.2 else 'MISS'}"
            )
            print(
                f"Sharpe: {actual_sharpe:.2f} (Dokumenterat: {documented_sharpe:.2f}) - {'OK' if abs(actual_sharpe - documented_sharpe) < 0.1 else 'MISS'}"
            )
            print(
                f"Drawdown: {actual_drawdown:.2f}% (Dokumenterat: {documented_drawdown:.2f}%) - {'OK' if abs(actual_drawdown - documented_drawdown) < 0.1 else 'MISS'}"
            )

            # Overall assessment
            matches = 0
            if abs(actual_return - documented_return) < 1.0:
                matches += 1
            if abs(actual_win_rate - documented_win_rate) < 5.0:
                matches += 1
            if actual_trades == documented_trades:
                matches += 1
            if abs(actual_profit_factor - documented_profit_factor) < 0.2:
                matches += 1
            if abs(actual_sharpe - documented_sharpe) < 0.1:
                matches += 1
            if abs(actual_drawdown - documented_drawdown) < 0.1:
                matches += 1

            print("\n=== SAMMANFATTNING ===")
            print(f"Matchar dokumentation: {matches}/6 metrics")
            if matches >= 5:
                print("EXCELLENT - Konfigurationen matchar dokumentationen perfekt!")
            elif matches >= 4:
                print("GOOD - Konfigurationen matchar dokumentationen bra!")
            elif matches >= 3:
                print("OK - Konfigurationen matchar dokumentationen delvis")
            else:
                print("POOR - Konfigurationen matchar inte dokumentationen")

        else:
            print("Inga resultat från backtest")

    except Exception as e:
        print(f"Fel under backtest: {e}")
        import traceback

        traceback.print_exc()

    print(f"\nTest avslutat: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    test_6h_optimized()
