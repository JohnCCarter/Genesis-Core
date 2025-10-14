#!/usr/bin/env python3
"""
Test 1D Model Only
=================

Testa bara 1D modellen utan backtest.
"""

def test_1d_model():
    """Testa 1D modellen."""
    print("Testar 1D modellen...")
    
    try:
        from core.strategy.model_registry import ModelRegistry
        from core.strategy.prob_model import predict_proba_for
        
        # Testa ModelRegistry lookup
        registry = ModelRegistry()
        meta = registry.get_meta("tBTCUSD", "1D")
        
        if meta and 'schema' in meta:
            schema_len = len(meta['schema'])
            print(f"SUCCESS: tBTCUSD:1D model laddad - {schema_len} features")
            print(f"Schema: {meta['schema']}")
        else:
            print("ERROR: Ingen meta för tBTCUSD:1D")
            return False
        
        # Testa prediction
        test_features = {
            "rsi_inv_lag1": 0.5,
            "volatility_shift_ma3": 0.3,
            "bb_position_inv_ma3": 0.7,
            "rsi_vol_interaction": 0.4,
            "vol_regime": 0.6
        }
        
        probas, meta = predict_proba_for("tBTCUSD", "1D", test_features)
        
        if 'buy' in probas and 'sell' in probas and 'hold' in probas:
            print(f"SUCCESS: Prediction fungerar - Buy: {probas['buy']:.3f}, Sell: {probas['sell']:.3f}, Hold: {probas['hold']:.3f}")
            return True
        else:
            print(f"ERROR: Fel prediction format: {probas}")
            return False
            
    except Exception as e:
        print(f"ERROR: Model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_1d_config():
    """Testa 1D konfiguration."""
    print("\nTestar 1D konfiguration...")
    
    try:
        from config.timeframe_configs import get_1d_config
        
        config = get_1d_config()
        
        print("1D Konfiguration:")
        print(f"  entry_conf_overall: {config['thresholds']['entry_conf_overall']}")
        print(f"  regime_proba: {config['thresholds']['regime_proba']}")
        print(f"  max_hold_bars: {config['exit']['max_hold_bars']}")
        print(f"  warmup_bars: {config['warmup_bars']}")
        print(f"  risk_map: {config['risk']['risk_map']}")
        
        # Kontrollera att konfigurationen är extremt permisiv
        if config['thresholds']['entry_conf_overall'] <= 0.05:
            print("SUCCESS: Extremt låg entry confidence - borde generera trades")
        else:
            print("WARNING: Entry confidence kanske för hög")
        
        if all(prob <= 0.1 for prob in config['thresholds']['regime_proba'].values()):
            print("SUCCESS: Extremt låga regime probabilities - borde generera trades")
        else:
            print("WARNING: Regime probabilities kanske för höga")
        
        if config['exit']['max_hold_bars'] >= 30:
            print("SUCCESS: Långa hold times - bra för 1D")
        else:
            print("WARNING: Hold times kanske för korta")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_1d_data_availability():
    """Testa 1D data tillgänglighet."""
    print("\nTestar 1D data tillgänglighet...")
    
    try:
        from core.io.bitfinex.data_loader import BitfinexDataLoader
        
        loader = BitfinexDataLoader()
        
        # Testa att ladda 1D data
        candles = loader.load_candles("tBTCUSD", "1D", "2025-09-01", "2025-10-13")
        
        if candles and len(candles) > 0:
            print(f"SUCCESS: 1D data laddad - {len(candles)} candles")
            print(f"Första candle: {candles[0]}")
            print(f"Sista candle: {candles[-1]}")
            return True
        else:
            print("ERROR: Ingen 1D data laddad")
            return False
            
    except Exception as e:
        print(f"ERROR: Data test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Huvudfunktion."""
    print("TESTING 1D MODEL AND CONFIG")
    print("="*50)
    
    try:
        # Test 1: Model
        test1 = test_1d_model()
        
        # Test 2: Config
        test2 = test_1d_config()
        
        # Test 3: Data
        test3 = test_1d_data_availability()
        
        print("\n" + "="*50)
        print("1D TEST RESULTS:")
        print(f"Model: {'PASS' if test1 else 'FAIL'}")
        print(f"Config: {'PASS' if test2 else 'FAIL'}")
        print(f"Data: {'PASS' if test3 else 'FAIL'}")
        
        if test1 and test2 and test3:
            print("\nSUCCESS: 1D model, config och data fungerar!")
            print("Problemet är troligen i backtest pipeline.")
            print("Vi kan fortsätta med optimering.")
        else:
            print("\nWARNING: Några komponenter har problem.")
            print("Vi behöver fixa dessa först.")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
