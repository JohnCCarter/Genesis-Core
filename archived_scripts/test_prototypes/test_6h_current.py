#!/usr/bin/env python3
"""
Test Current 6h Configuration
============================

Testa nuvarande 6h konfiguration för att verifiera excellent performance.
"""

import json
from datetime import datetime


def test_6h_current():
    """Testa nuvarande 6h konfiguration."""
    print("Testar nuvarande 6h konfiguration...")

    try:
        from config.timeframe_configs import get_6h_config
        from core.strategy.evaluate import evaluate_pipeline

        # Hämta 6h konfiguration
        config = get_6h_config()
        print("6h Konfiguration:")
        print(f"  entry_conf_overall: {config['thresholds']['entry_conf_overall']}")
        print(f"  regime_proba: {config['thresholds']['regime_proba']}")
        print(f"  max_hold_bars: {config['exit']['max_hold_bars']}")
        print(f"  warmup_bars: {config['warmup_bars']}")
        print(f"  partial_1_pct: {config['htf_exit_config']['partial_1_pct']}")
        print(f"  fib_threshold_atr: {config['htf_exit_config']['fib_threshold_atr']}")

        # Test konfiguration
        test_config = {
            "symbol": "tBTCUSD",
            "timeframe": "6h",
            "start_date": "2025-07-01",
            "end_date": "2025-10-13",
            "initial_capital": 10000.0,
            "commission_rate": 0.003,
            "slippage_rate": 0.0005,
            "warmup_bars": config["warmup_bars"],
        }

        # Lägg till 6h specifika inställningar
        test_config.update(config)

        print("\nKör backtest med 6h konfiguration...")
        results = evaluate_pipeline(test_config)

        if results and "summary" in results:
            summary = results["summary"]
            print("\nRESULTAT:")
            print(f"  Trades: {summary.get('num_trades', 0)}")
            print(f"  Return: {summary.get('total_return_pct', 0):.2f}%")
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
                return_pct = summary.get("total_return_pct", 0)
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


def test_6h_with_different_periods():
    """Testa 6h med olika tidsperioder."""
    print("\nTestar 6h med olika tidsperioder...")

    periods = [
        ("2025-01-01", "2025-10-13", "Hela året"),
        ("2025-07-01", "2025-10-13", "Senaste 3 månaderna"),
        ("2025-09-01", "2025-10-13", "Senaste månaden"),
    ]

    results = []

    for start_date, end_date, description in periods:
        try:
            from config.timeframe_configs import get_6h_config
            from core.strategy.evaluate import evaluate_pipeline

            config = get_6h_config()

            test_config = {
                "symbol": "tBTCUSD",
                "timeframe": "6h",
                "start_date": start_date,
                "end_date": end_date,
                "initial_capital": 10000.0,
                "commission_rate": 0.003,
                "slippage_rate": 0.0005,
                "warmup_bars": config["warmup_bars"],
            }

            test_config.update(config)

            results_pipeline = evaluate_pipeline(test_config)

            if results_pipeline and "summary" in results_pipeline:
                summary = results_pipeline["summary"]
                trades = summary.get("num_trades", 0)
                return_pct = summary.get("total_return_pct", 0)
                sharpe = summary.get("sharpe_ratio", 0)

                print(
                    f"  {description}: {trades} trades, {return_pct:.2f}% return, Sharpe: {sharpe:.2f}"
                )

                results.append(
                    {
                        "period": description,
                        "trades": trades,
                        "return_pct": return_pct,
                        "sharpe": sharpe,
                        "success": trades > 0,
                    }
                )
            else:
                print(f"  {description}: ERROR - Ingen summary")
                results.append({"period": description, "success": False, "error": "No summary"})

        except Exception as e:
            print(f"  {description}: ERROR - {e}")
            results.append({"period": description, "success": False, "error": str(e)})

    successful_periods = [r for r in results if r.get("success", False)]
    print(f"\nSUCCESS: {len(successful_periods)}/{len(periods)} perioder genererar trades")

    return results


def save_6h_test_results(main_result, period_results):
    """Spara 6h testresultat."""
    print("\nSparar 6h testresultat...")

    results_data = {
        "timestamp": datetime.now().isoformat(),
        "main_test": main_result,
        "period_tests": period_results,
        "summary": {
            "main_test_success": main_result.get("success", False),
            "main_performance_score": main_result.get("performance_score", 0),
            "successful_periods": len([r for r in period_results if r.get("success", False)]),
            "total_periods": len(period_results),
        },
    }

    with open("6h_test_results.json", "w") as f:
        json.dump(results_data, f, indent=2)

    print("Resultat sparade till: 6h_test_results.json")


def main():
    """Huvudfunktion."""
    print("TESTING 6H CURRENT CONFIGURATION")
    print("=" * 50)

    try:
        # Test 1: Nuvarande konfiguration
        main_result = test_6h_current()

        # Test 2: Olika tidsperioder
        period_results = test_6h_with_different_periods()

        # Spara resultat
        save_6h_test_results(main_result, period_results)

        print("\n" + "=" * 50)
        print("6H TEST RESULTS:")
        print(f"Main Test: {'PASS' if main_result.get('success', False) else 'FAIL'}")
        if main_result.get("success", False):
            print(f"Performance Score: {main_result.get('performance_score', 0)}/5")

        successful_periods = len([r for r in period_results if r.get("success", False)])
        print(f"Period Tests: {successful_periods}/{len(period_results)} successful")

        if main_result.get("success", False) and main_result.get("performance_score", 0) >= 4:
            print("\nSUCCESS: 6h presterar utmärkt!")
            print("Konfigurationen är optimal och redo för produktion.")
        elif main_result.get("success", False):
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
