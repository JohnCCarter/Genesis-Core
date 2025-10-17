#!/usr/bin/env python3
"""
Test 6h Model Only
=================

Testa bara 6h modellen utan backtest.
"""


def test_6h_model():
    """Testa 6h modellen."""
    print("Testar 6h modellen...")

    try:
        from core.strategy.model_registry import ModelRegistry
        from core.strategy.prob_model import predict_proba_for

        # Testa ModelRegistry lookup
        registry = ModelRegistry()
        meta = registry.get_meta("tBTCUSD", "6h")

        if meta and "schema" in meta:
            schema_len = len(meta["schema"])
            print(f"SUCCESS: tBTCUSD:6h model laddad - {schema_len} features")
            print(f"Schema: {meta['schema']}")
        else:
            print("ERROR: Ingen meta för tBTCUSD:6h")
            return False

        # Testa prediction
        test_features = {
            "rsi_inv_lag1": 0.5,
            "volatility_shift_ma3": 0.3,
            "bb_position_inv_ma3": 0.7,
            "rsi_vol_interaction": 0.4,
            "vol_regime": 0.6,
        }

        probas, meta = predict_proba_for("tBTCUSD", "6h", test_features)

        if "buy" in probas and "sell" in probas and "hold" in probas:
            print(
                f"SUCCESS: Prediction fungerar - Buy: {probas['buy']:.3f}, Sell: {probas['sell']:.3f}, Hold: {probas['hold']:.3f}"
            )
            return True
        else:
            print(f"ERROR: Fel prediction format: {probas}")
            return False

    except Exception as e:
        print(f"ERROR: Model test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_6h_config():
    """Testa 6h konfiguration."""
    print("\nTestar 6h konfiguration...")

    try:
        from config.timeframe_configs import get_6h_config

        config = get_6h_config()

        print("6h Konfiguration:")
        print(f"  entry_conf_overall: {config['thresholds']['entry_conf_overall']}")
        print(f"  regime_proba: {config['thresholds']['regime_proba']}")
        print(f"  max_hold_bars: {config['exit']['max_hold_bars']}")
        print(f"  warmup_bars: {config['warmup_bars']}")
        print(f"  risk_map: {config['risk']['risk_map']}")
        print(f"  partial_1_pct: {config['htf_exit_config']['partial_1_pct']}")
        print(f"  fib_threshold_atr: {config['htf_exit_config']['fib_threshold_atr']}")

        # Kontrollera att konfigurationen är rimlig
        if 0.3 <= config["thresholds"]["entry_conf_overall"] <= 0.4:
            print("SUCCESS: Entry confidence är rimlig")
        else:
            print("WARNING: Entry confidence kanske inte optimal")

        if 15 <= config["exit"]["max_hold_bars"] <= 25:
            print("SUCCESS: Max hold bars är rimlig")
        else:
            print("WARNING: Max hold bars kanske inte optimal")

        if 0.3 <= config["htf_exit_config"]["partial_1_pct"] <= 0.5:
            print("SUCCESS: Partial exit är rimlig")
        else:
            print("WARNING: Partial exit kanske inte optimal")

        return True

    except Exception as e:
        print(f"ERROR: Config test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Huvudfunktion."""
    print("TESTING 6H MODEL AND CONFIG")
    print("=" * 50)

    try:
        # Test 1: Model
        test1 = test_6h_model()

        # Test 2: Config
        test2 = test_6h_config()

        print("\n" + "=" * 50)
        print("6H TEST RESULTS:")
        print(f"Model: {'PASS' if test1 else 'FAIL'}")
        print(f"Config: {'PASS' if test2 else 'FAIL'}")

        if test1 and test2:
            print("\nSUCCESS: 6h model och config fungerar!")
            print("Vi kan fortsätta med backtest när data problem är löst.")
        else:
            print("\nWARNING: Några komponenter har problem.")
            print("Vi behöver fixa dessa först.")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
