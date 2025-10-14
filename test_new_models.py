#!/usr/bin/env python3
"""
Test New Models
==============

Testa att alla nya modeller fungerar korrekt.
"""

import json
import os
from pathlib import Path

def test_model_loading():
    """Testa att alla modeller kan laddas."""
    print("Testar model loading...")
    
    registry_path = "config/models/registry.json"
    with open(registry_path, 'r') as f:
        registry = json.load(f)
    
    success_count = 0
    error_count = 0
    
    for key, value in registry.items():
        if isinstance(value, dict) and 'champion' in value:
            champion_path = value['champion']
            
            if os.path.exists(champion_path):
                try:
                    with open(champion_path, 'r') as f:
                        model_data = json.load(f)
                    
                    # Kontrollera schema (kan vara 5 eller 14 features)
                    if 'schema' in model_data and len(model_data['schema']) >= 5:
                        success_count += 1
                    else:
                        print(f"ERROR: {key} - Fel schema: {len(model_data.get('schema', []))} features")
                        error_count += 1
                        
                except Exception as e:
                    print(f"ERROR: {key} - {e}")
                    error_count += 1
            else:
                print(f"ERROR: {key} - Model saknas: {champion_path}")
                error_count += 1
    
    print(f"SUCCESS: {success_count}")
    print(f"ERRORS: {error_count}")
    return error_count == 0

def test_model_registry_lookup():
    """Testa ModelRegistry lookup."""
    print("\nTestar ModelRegistry lookup...")
    
    try:
        from core.strategy.model_registry import ModelRegistry
        
        registry = ModelRegistry()
        
        # Testa några lookups
        test_cases = [
            ("tBTCUSD", "1h"),
            ("tETHUSD", "6h"),
            ("tADAUSD", "1D"),
            ("tSOLUSD", "1W")
        ]
        
        success_count = 0
        for symbol, timeframe in test_cases:
            try:
                meta = registry.get_meta(symbol, timeframe)
                if meta and 'schema' in meta:
                    print(f"OK: {symbol}:{timeframe} - {len(meta['schema'])} features")
                    success_count += 1
                else:
                    print(f"ERROR: {symbol}:{timeframe} - Ingen meta")
            except Exception as e:
                print(f"ERROR: {symbol}:{timeframe} - {e}")
        
        print(f"SUCCESS: {success_count}/{len(test_cases)}")
        return success_count == len(test_cases)
        
    except Exception as e:
        print(f"ERROR: ModelRegistry import failed: {e}")
        return False

def test_probability_prediction():
    """Testa probability prediction."""
    print("\nTestar probability prediction...")
    
    try:
        from core.strategy.prob_model import predict_proba_for
        
        # Testa prediction
        test_features = {
            "rsi_inv_lag1": 0.5,
            "volatility_shift_ma3": 0.3,
            "bb_position_inv_ma3": 0.7,
            "rsi_vol_interaction": 0.4,
            "vol_regime": 0.6
        }
        
        probas, meta = predict_proba_for("tBTCUSD", "1h", test_features)
        
        if 'buy' in probas and 'sell' in probas and 'hold' in probas:
            print(f"OK: Prediction fungerar - Buy: {probas['buy']:.3f}, Sell: {probas['sell']:.3f}, Hold: {probas['hold']:.3f}")
            return True
        else:
            print(f"ERROR: Fel prediction format: {probas}")
            return False
            
    except Exception as e:
        print(f"ERROR: Prediction failed: {e}")
        return False

def main():
    """Huvudfunktion."""
    print("TESTING NEW MODELS")
    print("="*50)
    
    try:
        # Test 1: Model loading
        test1 = test_model_loading()
        
        # Test 2: ModelRegistry lookup
        test2 = test_model_registry_lookup()
        
        # Test 3: Probability prediction
        test3 = test_probability_prediction()
        
        print("\n" + "="*50)
        print("TEST RESULTS:")
        print(f"Model Loading: {'PASS' if test1 else 'FAIL'}")
        print(f"Registry Lookup: {'PASS' if test2 else 'FAIL'}")
        print(f"Prediction: {'PASS' if test3 else 'FAIL'}")
        
        if test1 and test2 and test3:
            print("\nSUCCESS: Alla tester passerade!")
        else:
            print("\nWARNING: Några tester misslyckades!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
