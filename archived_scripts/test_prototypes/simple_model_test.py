#!/usr/bin/env python3
"""
Simple Model Test
================

Enkel test för att verifiera att modellerna fungerar.
"""


def test_model_registry():
    """Testa ModelRegistry funktionalitet."""
    print("Testar ModelRegistry...")

    try:
        from core.strategy.model_registry import ModelRegistry

        registry = ModelRegistry()

        # Testa några lookups
        test_cases = [
            ("tBTCUSD", "1h"),
            ("tETHUSD", "6h"),
            ("tADAUSD", "1D"),
            ("tSOLUSD", "1W"),
            ("tDOTUSD", "3h"),
            ("tDOGEUSD", "12h"),
        ]

        success_count = 0
        for symbol, timeframe in test_cases:
            try:
                meta = registry.get_meta(symbol, timeframe)
                if meta and "schema" in meta:
                    schema_len = len(meta["schema"])
                    print(f"OK: {symbol}:{timeframe} - {schema_len} features")
                    success_count += 1
                else:
                    print(f"ERROR: {symbol}:{timeframe} - Ingen meta")
            except Exception as e:
                print(f"ERROR: {symbol}:{timeframe} - {e}")

        print(f"SUCCESS: {success_count}/{len(test_cases)}")
        return success_count == len(test_cases)

    except Exception as e:
        print(f"ERROR: ModelRegistry test failed: {e}")
        return False


def test_probability_prediction():
    """Testa probability prediction med olika modeller."""
    print("\nTestar probability prediction...")

    try:
        from core.strategy.prob_model import predict_proba_for

        # Testa olika symboler och timeframes
        test_cases = [("tBTCUSD", "1h"), ("tETHUSD", "6h"), ("tADAUSD", "1D")]

        # Test features
        test_features = {
            "rsi_inv_lag1": 0.5,
            "volatility_shift_ma3": 0.3,
            "bb_position_inv_ma3": 0.7,
            "rsi_vol_interaction": 0.4,
            "vol_regime": 0.6,
        }

        success_count = 0
        for symbol, timeframe in test_cases:
            try:
                probas, meta = predict_proba_for(symbol, timeframe, test_features)

                if "buy" in probas and "sell" in probas and "hold" in probas:
                    print(
                        f"OK: {symbol}:{timeframe} - Buy: {probas['buy']:.3f}, Sell: {probas['sell']:.3f}, Hold: {probas['hold']:.3f}"
                    )
                    success_count += 1
                else:
                    print(f"ERROR: {symbol}:{timeframe} - Fel prediction format")

            except Exception as e:
                print(f"ERROR: {symbol}:{timeframe} - {e}")

        print(f"SUCCESS: {success_count}/{len(test_cases)}")
        return success_count == len(test_cases)

    except Exception as e:
        print(f"ERROR: Prediction test failed: {e}")
        return False


def test_all_timeframes():
    """Testa alla timeframes för en symbol."""
    print("\nTestar alla timeframes...")

    try:
        from core.strategy.prob_model import predict_proba_for

        symbol = "tBTCUSD"
        timeframes = ["1m", "5m", "15m", "30m", "1h", "3h", "6h", "12h", "1D", "1W", "14D", "1M"]

        # Test features
        test_features = {
            "rsi_inv_lag1": 0.5,
            "volatility_shift_ma3": 0.3,
            "bb_position_inv_ma3": 0.7,
            "rsi_vol_interaction": 0.4,
            "vol_regime": 0.6,
        }

        success_count = 0
        for timeframe in timeframes:
            try:
                probas, meta = predict_proba_for(symbol, timeframe, test_features)

                if "buy" in probas and "sell" in probas:
                    print(
                        f"OK: {symbol}:{timeframe} - Buy: {probas['buy']:.3f}, Sell: {probas['sell']:.3f}"
                    )
                    success_count += 1
                else:
                    print(f"ERROR: {symbol}:{timeframe} - Fel prediction format")

            except Exception as e:
                print(f"ERROR: {symbol}:{timeframe} - {e}")

        print(f"SUCCESS: {success_count}/{len(timeframes)} timeframes")
        return success_count == len(timeframes)

    except Exception as e:
        print(f"ERROR: All timeframes test failed: {e}")
        return False


def main():
    """Huvudfunktion."""
    print("SIMPLE MODEL TEST")
    print("=" * 50)

    try:
        # Test 1: ModelRegistry
        test1 = test_model_registry()

        # Test 2: Probability prediction
        test2 = test_probability_prediction()

        # Test 3: All timeframes
        test3 = test_all_timeframes()

        print("\n" + "=" * 50)
        print("TEST RESULTS:")
        print(f"ModelRegistry: {'PASS' if test1 else 'FAIL'}")
        print(f"Prediction: {'PASS' if test2 else 'FAIL'}")
        print(f"All Timeframes: {'PASS' if test3 else 'FAIL'}")

        if test1 and test2 and test3:
            print("\nSUCCESS: Alla modeller fungerar perfekt!")
            print("Model Registry uppdatering är komplett och fungerar!")
        else:
            print("\nWARNING: Några tester misslyckades!")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
