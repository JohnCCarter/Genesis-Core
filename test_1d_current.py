#!/usr/bin/env python3
"""
Test Current 1D Configuration
============================

Testa nuvarande 1D konfiguration för att se om den genererar trades.
"""

import json
from datetime import datetime

def test_1d_current():
    """Testa nuvarande 1D konfiguration."""
    print("Testar nuvarande 1D konfiguration...")
    
    try:
        from core.strategy.evaluate import evaluate_pipeline
        from config.timeframe_configs import get_1d_config
        
        # Hämta 1D konfiguration
        config = get_1d_config()
        print("1D Konfiguration:")
        print(f"  entry_conf_overall: {config['thresholds']['entry_conf_overall']}")
        print(f"  regime_proba: {config['thresholds']['regime_proba']}")
        print(f"  max_hold_bars: {config['exit']['max_hold_bars']}")
        print(f"  warmup_bars: {config['warmup_bars']}")
        
        # Test konfiguration
        test_config = {
            "symbol": "tBTCUSD",
            "timeframe": "1D",
            "start_date": "2025-07-01",
            "end_date": "2025-10-13",
            "initial_capital": 10000.0,
            "commission_rate": 0.003,
            "slippage_rate": 0.0005,
            "warmup_bars": config['warmup_bars'],
        }
        
        # Lägg till 1D specifika inställningar
        test_config.update(config)
        
        print(f"\nKör backtest med 1D konfiguration...")
        results = evaluate_pipeline(test_config)
        
        if results and 'summary' in results:
            summary = results['summary']
            print(f"\nRESULTAT:")
            print(f"  Trades: {summary.get('num_trades', 0)}")
            print(f"  Return: {summary.get('total_return_pct', 0):.2f}%")
            print(f"  Win Rate: {summary.get('win_rate', 0):.2f}%")
            print(f"  Profit Factor: {summary.get('profit_factor', 0):.2f}")
            print(f"  Sharpe: {summary.get('sharpe_ratio', 0):.2f}")
            print(f"  Max Drawdown: {summary.get('max_drawdown_pct', 0):.2f}%")
            
            if summary.get('num_trades', 0) > 0:
                print(f"\nSUCCESS: 1D genererar trades!")
                return True
            else:
                print(f"\nPROBLEM: 1D genererar inga trades")
                return False
        else:
            print("ERROR: Ingen summary i results")
            return False
            
    except Exception as e:
        print(f"ERROR: Backtest failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_1d_with_different_periods():
    """Testa 1D med olika tidsperioder."""
    print("\nTestar 1D med olika tidsperioder...")
    
    periods = [
        ("2025-01-01", "2025-10-13", "Hela året"),
        ("2025-07-01", "2025-10-13", "Senaste 3 månaderna"),
        ("2025-09-01", "2025-10-13", "Senaste månaden"),
    ]
    
    success_count = 0
    
    for start_date, end_date, description in periods:
        try:
            from core.strategy.evaluate import evaluate_pipeline
            from config.timeframe_configs import get_1d_config
            
            config = get_1d_config()
            
            test_config = {
                "symbol": "tBTCUSD",
                "timeframe": "1D",
                "start_date": start_date,
                "end_date": end_date,
                "initial_capital": 10000.0,
                "commission_rate": 0.003,
                "slippage_rate": 0.0005,
                "warmup_bars": config['warmup_bars'],
            }
            
            test_config.update(config)
            
            results = evaluate_pipeline(test_config)
            
            if results and 'summary' in results:
                summary = results['summary']
                trades = summary.get('num_trades', 0)
                return_pct = summary.get('total_return_pct', 0)
                
                print(f"  {description}: {trades} trades, {return_pct:.2f}% return")
                
                if trades > 0:
                    success_count += 1
            else:
                print(f"  {description}: ERROR - Ingen summary")
                
        except Exception as e:
            print(f"  {description}: ERROR - {e}")
    
    print(f"\nSUCCESS: {success_count}/{len(periods)} perioder genererar trades")
    return success_count > 0

def main():
    """Huvudfunktion."""
    print("TESTING 1D CURRENT CONFIGURATION")
    print("="*50)
    
    try:
        # Test 1: Nuvarande konfiguration
        test1 = test_1d_current()
        
        # Test 2: Olika tidsperioder
        test2 = test_1d_with_different_periods()
        
        print("\n" + "="*50)
        print("1D TEST RESULTS:")
        print(f"Current Config: {'PASS' if test1 else 'FAIL'}")
        print(f"Different Periods: {'PASS' if test2 else 'FAIL'}")
        
        if test1 and test2:
            print("\nSUCCESS: 1D fungerar med nuvarande konfiguration!")
            print("Vi kan fortsätta med optimering.")
        else:
            print("\nWARNING: 1D har problem med nuvarande konfiguration.")
            print("Vi behöver anpassa konfigurationen ytterligare.")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
