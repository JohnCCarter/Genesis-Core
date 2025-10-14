#!/usr/bin/env python3
"""
Test 6h Backtest
================

Testa 6h med korrekt BacktestEngine approach.
"""

import json
from datetime import datetime


def test_6h_backtest():
    """Testa 6h med BacktestEngine."""
    print("Testar 6h med BacktestEngine...")

    try:
        from config.timeframe_configs import get_6h_config
        from core.backtest.engine import BacktestEngine

        # Hämta 6h konfiguration
        config = get_6h_config()
        print("6h Konfiguration:")
        print(f"  entry_conf_overall: {config['thresholds']['entry_conf_overall']}")
        print(f"  regime_proba: {config['thresholds']['regime_proba']}")
        print(f"  max_hold_bars: {config['exit']['max_hold_bars']}")
        print(f"  warmup_bars: {config['warmup_bars']}")

        # Skapa BacktestEngine
        engine = BacktestEngine(
            symbol="tBTCUSD",
            timeframe="6h",
            start_date="2025-07-01",
            end_date="2025-10-13",
            initial_capital=10000.0,
            commission_rate=0.003,
            slippage_rate=0.0005,
            warmup_bars=config["warmup_bars"],
            htf_exit_config=config.get("htf_exit_config", {}),
        )

        # Ladda data
        print("\nLaddar data...")
        if not engine.load_data():
            print("ERROR: Kunde inte ladda data")
            return {"success": False, "error": "Data loading failed"}

        # Skapa policy och configs
        policy = {"symbol": "tBTCUSD", "timeframe": "6h"}

        configs = config

        print(f"\nKör backtest med {len(engine.candles_df)} candles...")

        # Kör backtest
        results = engine.run(configs=configs, policy=policy)

        if results and "summary" in results:
            summary = results["summary"]
            print("\nRESULTAT:")
            print(f"  Trades: {summary.get('num_trades', 0)}")
            print(f"  Return: {summary.get('total_return', 0):.2f}%")
            print(f"  Win Rate: {summary.get('win_rate', 0):.2f}%")
            print(f"  Profit Factor: {summary.get('profit_factor', 0):.2f}")
            print(f"  Sharpe: {summary.get('sharpe_ratio', 0):.2f}")
            print(f"  Sortino: {summary.get('sortino_ratio', 0):.2f}")
            print(f"  Calmar: {summary.get('calmar_ratio', 0):.2f}")
            print(f"  Max Drawdown: {summary.get('max_drawdown_pct', 0):.2f}%")
            print(f"  Max Winning Streak: {summary.get('max_winning_streak', 0)}")
            print(f"  Max Losing Streak: {summary.get('max_losing_streak', 0)}")
            print(f"  Avg Trade Duration: {summary.get('avg_trade_duration_hours', 0):.1f} hours")

            if summary.get("num_trades", 0) > 0:
                print("\nSUCCESS: 6h genererar trades!")

                # Analysera prestanda
                trades = summary.get("num_trades", 0)
                return_pct = summary.get("total_return", 0)
                win_rate = summary.get("win_rate", 0)
                sharpe = summary.get("sharpe_ratio", 0)
                drawdown = summary.get("max_drawdown_pct", 0)

                # Bedöm prestanda
                performance_score = 0
                if trades >= 10:
                    performance_score += 1
                    print("  OK Bra antal trades (>=10)")
                else:
                    print("  WARNING Få trades (<10)")

                if return_pct > 0:
                    performance_score += 1
                    print("  OK Positiv return")
                else:
                    print("  ERROR Negativ return")

                if win_rate >= 50:
                    performance_score += 1
                    print("  OK Bra win rate (>=50%)")
                else:
                    print("  WARNING Låg win rate (<50%)")

                if sharpe > 1.0:
                    performance_score += 1
                    print("  OK Bra Sharpe ratio (>1.0)")
                elif sharpe > 0.5:
                    print("  WARNING Acceptabel Sharpe ratio (0.5-1.0)")
                else:
                    print("  ERROR Låg Sharpe ratio (<0.5)")

                if drawdown < 20:
                    performance_score += 1
                    print("  OK Låg drawdown (<20%)")
                elif drawdown < 30:
                    print("  WARNING Acceptabel drawdown (20-30%)")
                else:
                    print("  ERROR Hög drawdown (>30%)")

                print(f"\nPERFORMANCE SCORE: {performance_score}/5")

                if performance_score >= 4:
                    print("EXCELLENT: 6h presterar utmärkt!")
                elif performance_score >= 3:
                    print("GOOD: 6h presterar bra!")
                else:
                    print("NEEDS IMPROVEMENT: 6h behöver optimering")

                return {"success": True, "performance_score": performance_score, "summary": summary}
            else:
                print("\nPROBLEM: 6h genererar inga trades")
                return {"success": False, "error": "No trades generated"}
        else:
            print("ERROR: Ingen summary i results")
            return {"success": False, "error": "No summary"}

    except Exception as e:
        print(f"ERROR: Backtest failed: {e}")
        import traceback

        traceback.print_exc()
        return {"success": False, "error": str(e)}


def save_6h_backtest_results(result):
    """Spara 6h backtest resultat."""
    print("\nSparar 6h backtest resultat...")

    results_data = {
        "timestamp": datetime.now().isoformat(),
        "test_type": "6h_backtest_engine",
        "result": result,
        "summary": {
            "success": result.get("success", False),
            "performance_score": result.get("performance_score", 0),
            "trades": (
                result.get("summary", {}).get("num_trades", 0) if result.get("summary") else 0
            ),
            "return_pct": (
                result.get("summary", {}).get("total_return", 0) if result.get("summary") else 0
            ),
            "sharpe": (
                result.get("summary", {}).get("sharpe_ratio", 0) if result.get("summary") else 0
            ),
        },
    }

    with open("6h_backtest_results.json", "w") as f:
        json.dump(results_data, f, indent=2)

    print("Resultat sparade till: 6h_backtest_results.json")


def main():
    """Huvudfunktion."""
    print("TESTING 6H BACKTEST ENGINE")
    print("=" * 50)

    try:
        # Test 6h med BacktestEngine
        result = test_6h_backtest()

        # Spara resultat
        save_6h_backtest_results(result)

        print("\n" + "=" * 50)
        print("6H BACKTEST RESULTS:")
        print(f"Success: {'PASS' if result.get('success', False) else 'FAIL'}")
        if result.get("success", False):
            print(f"Performance Score: {result.get('performance_score', 0)}/5")
            summary = result.get("summary", {})
            print(f"Trades: {summary.get('num_trades', 0)}")
            print(f"Return: {summary.get('total_return', 0):.2f}%")
            print(f"Sharpe: {summary.get('sharpe_ratio', 0):.2f}")

        if result.get("success", False) and result.get("performance_score", 0) >= 4:
            print("\nSUCCESS: 6h presterar utmärkt!")
            print("Konfigurationen är optimal och redo för produktion.")
        elif result.get("success", False):
            print("\nSUCCESS: 6h presterar bra!")
            print("Konfigurationen fungerar men kan eventuellt optimeras.")
        else:
            print("\nWARNING: 6h har problem!")
            print("Vi behöver undersöka och fixa konfigurationen.")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
