#!/usr/bin/env python3
"""
Test 1D Optimizations
====================

Testa alla 1D optimeringskonfigurationer.
"""

import json
from datetime import datetime


def test_1d_optimization(config_name, config_data):
    """Testa en 1D optimeringskonfiguration."""
    print(f"\nTestar {config_data['name']}...")
    print(f"Beskrivning: {config_data['description']}")

    try:
        from core.strategy.evaluate import evaluate_pipeline

        config = config_data["config"]

        # Test konfiguration
        test_config = {
            "symbol": "tBTCUSD",
            "timeframe": "1D",
            "start_date": "2025-07-01",
            "end_date": "2025-10-13",
            "initial_capital": 10000.0,
            "commission_rate": 0.003,
            "slippage_rate": 0.0005,
        }

        # Lägg till optimeringskonfiguration
        test_config.update(config)

        print(f"  Entry Confidence: {config['thresholds']['entry_conf_overall']}")
        print(f"  Max Hold Bars: {config['exit']['max_hold_bars']}")
        print(f"  Warmup Bars: {config['warmup_bars']}")

        # Kör backtest
        results = evaluate_pipeline(test_config)

        if results and "summary" in results:
            summary = results["summary"]

            trades = summary.get("num_trades", 0)
            return_pct = summary.get("total_return_pct", 0)
            win_rate = summary.get("win_rate", 0)
            profit_factor = summary.get("profit_factor", 0)
            sharpe = summary.get("sharpe_ratio", 0)
            drawdown = summary.get("max_drawdown_pct", 0)

            print("  RESULTAT:")
            print(f"    Trades: {trades}")
            print(f"    Return: {return_pct:.2f}%")
            print(f"    Win Rate: {win_rate:.2f}%")
            print(f"    Profit Factor: {profit_factor:.2f}")
            print(f"    Sharpe: {sharpe:.2f}")
            print(f"    Drawdown: {drawdown:.2f}%")

            return {
                "name": config_data["name"],
                "config_name": config_name,
                "trades": trades,
                "return_pct": return_pct,
                "win_rate": win_rate,
                "profit_factor": profit_factor,
                "sharpe": sharpe,
                "drawdown": drawdown,
                "success": trades > 0,
            }
        else:
            print("  ERROR: Ingen summary i results")
            return {
                "name": config_data["name"],
                "config_name": config_name,
                "success": False,
                "error": "No summary",
            }

    except Exception as e:
        print(f"  ERROR: {e}")
        return {
            "name": config_data["name"],
            "config_name": config_name,
            "success": False,
            "error": str(e),
        }


def test_all_1d_optimizations():
    """Testa alla 1D optimeringskonfigurationer."""
    print("Testar alla 1D optimeringskonfigurationer...")

    try:
        # Ladda optimerade konfigurationer
        with open("1d_optimized_configs.json") as f:
            optimized_configs = json.load(f)

        results = []

        for config_name, config_data in optimized_configs.items():
            result = test_1d_optimization(config_name, config_data)
            results.append(result)

        return results

    except Exception as e:
        print(f"ERROR: {e}")
        return []


def analyze_results(results):
    """Analysera resultaten."""
    print("\n" + "=" * 80)
    print("1D OPTIMERING RESULTAT ANALYS")
    print("=" * 80)

    successful_results = [r for r in results if r.get("success", False)]
    failed_results = [r for r in results if not r.get("success", False)]

    print(f"\nSUCCESSFUL CONFIGURATIONS ({len(successful_results)}):")
    for result in successful_results:
        print(f"  {result['name']}:")
        print(f"    Trades: {result['trades']}")
        print(f"    Return: {result['return_pct']:.2f}%")
        print(f"    Win Rate: {result['win_rate']:.2f}%")
        print(f"    Sharpe: {result['sharpe']:.2f}")
        print(f"    Drawdown: {result['drawdown']:.2f}%")

    if failed_results:
        print(f"\nFAILED CONFIGURATIONS ({len(failed_results)}):")
        for result in failed_results:
            print(f"  {result['name']}: {result.get('error', 'Unknown error')}")

    if successful_results:
        # Hitta bästa konfigurationen
        best_result = max(
            successful_results, key=lambda x: x["sharpe"] if x["sharpe"] > 0 else -999
        )

        print(f"\nBEST CONFIGURATION: {best_result['name']}")
        print(f"  Config: {best_result['config_name']}")
        print(f"  Trades: {best_result['trades']}")
        print(f"  Return: {best_result['return_pct']:.2f}%")
        print(f"  Win Rate: {best_result['win_rate']:.2f}%")
        print(f"  Sharpe: {best_result['sharpe']:.2f}")
        print(f"  Drawdown: {best_result['drawdown']:.2f}%")

        return best_result
    else:
        print("\nNO SUCCESSFUL CONFIGURATIONS!")
        return None


def save_results(results, best_result):
    """Spara resultaten."""
    print("\nSparar resultat...")

    results_data = {
        "timestamp": datetime.now().isoformat(),
        "all_results": results,
        "best_result": best_result,
        "summary": {
            "total_configs": len(results),
            "successful_configs": len([r for r in results if r.get("success", False)]),
            "failed_configs": len([r for r in results if not r.get("success", False)]),
            "best_config": best_result["name"] if best_result else None,
        },
    }

    with open("1d_optimization_results.json", "w") as f:
        json.dump(results_data, f, indent=2)

    print("Resultat sparade till: 1d_optimization_results.json")


def main():
    """Huvudfunktion."""
    print("TESTING 1D OPTIMIZATIONS")
    print("=" * 50)

    try:
        # Testa alla optimeringskonfigurationer
        results = test_all_1d_optimizations()

        # Analysera resultaten
        best_result = analyze_results(results)

        # Spara resultaten
        save_results(results, best_result)

        print("\n" + "=" * 50)
        if best_result:
            print("SUCCESS: Bästa 1D konfiguration hittad!")
            print(f"Bästa: {best_result['name']}")
            print("Vi kan uppdatera timeframe_configs.py med denna konfiguration.")
        else:
            print("WARNING: Ingen 1D konfiguration fungerade!")
            print("Vi behöver anpassa konfigurationerna ytterligare.")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
