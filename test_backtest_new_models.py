#!/usr/bin/env python3
"""
Test Backtest with New Models
============================

Testa att de nya modellerna fungerar i backtest.
"""

import json
from datetime import datetime

def test_backtest_with_new_models():
    """Testa backtest med nya modeller."""
    print("Testar backtest med nya modeller...")
    
    try:
        from core.backtest.engine import BacktestEngine
        from core.strategy.evaluate import evaluate_pipeline
        
        # Test konfiguration
        test_config = {
            "symbol": "tBTCUSD",
            "timeframe": "1h",
            "start_date": "2025-07-01",
            "end_date": "2025-10-13",
            "initial_capital": 10000.0,
            "commission_rate": 0.003,
            "slippage_rate": 0.0005,
            "warmup_bars": 200,
        }
        
        # Kör backtest
        print("Kör backtest...")
        results = evaluate_pipeline(test_config)
        
        if results and 'summary' in results:
            summary = results['summary']
            print(f"SUCCESS: Backtest fungerar!")
            print(f"Trades: {summary.get('num_trades', 0)}")
            print(f"Return: {summary.get('total_return_pct', 0):.2f}%")
            print(f"Win Rate: {summary.get('win_rate', 0):.2f}%")
            return True
        else:
            print("ERROR: Ingen summary i results")
            return False
            
    except Exception as e:
        print(f"ERROR: Backtest failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_different_timeframes():
    """Testa olika timeframes."""
    print("\nTestar olika timeframes...")
    
    timeframes = ["1h", "6h", "1D"]
    success_count = 0
    
    for timeframe in timeframes:
        try:
            from core.strategy.evaluate import evaluate_pipeline
            
            test_config = {
                "symbol": "tBTCUSD",
                "timeframe": timeframe,
                "start_date": "2025-07-01",
                "end_date": "2025-10-13",
                "initial_capital": 10000.0,
                "commission_rate": 0.003,
                "slippage_rate": 0.0005,
                "warmup_bars": 50,
            }
            
            results = evaluate_pipeline(test_config)
            
            if results and 'summary' in results:
                summary = results['summary']
                print(f"OK: {timeframe} - {summary.get('num_trades', 0)} trades, {summary.get('total_return_pct', 0):.2f}% return")
                success_count += 1
            else:
                print(f"ERROR: {timeframe} - Ingen summary")
                
        except Exception as e:
            print(f"ERROR: {timeframe} - {e}")
    
    print(f"SUCCESS: {success_count}/{len(timeframes)} timeframes")
    return success_count == len(timeframes)

def main():
    """Huvudfunktion."""
    print("TESTING BACKTEST WITH NEW MODELS")
    print("="*50)
    
    try:
        # Test 1: Basic backtest
        test1 = test_backtest_with_new_models()
        
        # Test 2: Different timeframes
        test2 = test_different_timeframes()
        
        print("\n" + "="*50)
        print("BACKTEST TEST RESULTS:")
        print(f"Basic Backtest: {'PASS' if test1 else 'FAIL'}")
        print(f"Multiple Timeframes: {'PASS' if test2 else 'FAIL'}")
        
        if test1 and test2:
            print("\nSUCCESS: Alla backtest tester passerade!")
            print("Modellerna fungerar perfekt i backtest!")
        else:
            print("\nWARNING: Några backtest tester misslyckades!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
