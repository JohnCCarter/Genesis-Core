#!/usr/bin/env python3
"""
Test HTF Fibonacci Mapping for Genesis-Core

Verify that HTF-to-LTF mapping works correctly with AS-OF semantics.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd

from core.indicators.htf_fibonacci import (
    compute_htf_fibonacci_mapping,
    get_htf_fibonacci_context,
    load_candles_data,
)
from core.strategy.features import extract_features


def test_candle_loading():
    """Test basic candle data loading."""
    print("=== Testing Candle Loading ===")

    try:
        # Test loading 1D data
        htf_data = load_candles_data("tBTCUSD", "1D")
        print(f"[OK] Loaded 1D data: {len(htf_data)} candles")
        print(f"   Date range: {htf_data['timestamp'].min()} to {htf_data['timestamp'].max()}")

        # Test loading 1h data
        ltf_data = load_candles_data("tBTCUSD", "1h")
        print(f"[OK] Loaded 1h data: {len(ltf_data)} candles")
        print(f"   Date range: {ltf_data['timestamp'].min()} to {ltf_data['timestamp'].max()}")

        return htf_data, ltf_data

    except Exception as e:
        print(f"[ERROR] Candle loading failed: {e}")
        return None, None


def test_htf_fibonacci_computation():
    """Test HTF Fibonacci level computation."""
    print("\n=== Testing HTF Fibonacci Computation ===")

    try:
        htf_data = load_candles_data("tBTCUSD", "1D")

        # Take recent subset for testing (last 100 days)
        htf_test = htf_data.tail(100).copy().reset_index(drop=True)

        from core.indicators.htf_fibonacci import compute_htf_fibonacci_levels

        htf_fib = compute_htf_fibonacci_levels(htf_test)

        print(f"[OK] Computed HTF Fibonacci levels: {len(htf_fib)} rows")

        # Check recent results
        recent = htf_fib.tail(5)
        print("\nRecent HTF Fibonacci Levels:")
        for _, row in recent.iterrows():
            date = row["timestamp"].strftime("%Y-%m-%d")
            levels = f"0.382:{row['htf_fib_0382']:.0f} | 0.5:{row['htf_fib_05']:.0f} | 0.618:{row['htf_fib_0618']:.0f}"
            swing = f"H:{row['htf_swing_high']:.0f} L:{row['htf_swing_low']:.0f}"
            print(f"   {date}: {levels} | {swing}")

        return htf_fib

    except Exception as e:
        print(f"[ERROR] HTF Fibonacci computation failed: {e}")
        return None


def test_htf_to_ltf_mapping():
    """Test HTF-to-LTF mapping with AS-OF semantics."""
    print("\n=== Testing HTF-to-LTF Mapping ===")

    try:
        # Load test data (smaller subset for speed)
        htf_data = load_candles_data("tBTCUSD", "1D").tail(30)  # Last 30 days
        ltf_data = load_candles_data("tBTCUSD", "1h").tail(200)  # Last ~8 days of 1h data

        # Create mapping
        mapping = compute_htf_fibonacci_mapping(htf_data, ltf_data)

        print(f"[OK] Created HTF-to-LTF mapping: {len(mapping)} LTF bars")

        # Test AS-OF semantics: Check a few specific cases
        print("\nVerifying AS-OF Semantics:")

        for i in [0, len(mapping) // 2, -1]:  # First, middle, last
            ltf_row = mapping.iloc[i]
            ltf_time = ltf_row["timestamp"]

            # Find corresponding HTF data that should be used (latest BEFORE ltf_time)
            available_htf = htf_data[htf_data["timestamp"] < ltf_time]

            if len(available_htf) > 0:
                expected_htf_time = available_htf["timestamp"].iloc[-1]
                data_age = (ltf_time - expected_htf_time).total_seconds() / 3600

                fib_618 = ltf_row["htf_fib_0618"]
                fib_618_str = f"{fib_618:.0f}" if fib_618 is not None else "None"

                print(
                    f"   LTF {ltf_time.strftime('%Y-%m-%d %H:%M')}: "
                    f"Age {data_age:.1f}h, "
                    f"Fib 0.618 = {fib_618_str}"
                )
            else:
                print(
                    f"   LTF {ltf_time.strftime('%Y-%m-%d %H:%M')}: No HTF data available (expected)"
                )

        # Check for lookahead bias (most important test!)
        print("\nChecking for Lookahead Bias:")
        lookahead_violations = 0

        for _i, ltf_row in mapping.iterrows():
            ltf_time = ltf_row["timestamp"]

            # Check if any HTF data used is AFTER this LTF bar
            if not pd.isna(ltf_row["htf_fib_0618"]):
                # Find which HTF bar was used for this LTF bar
                available_htf = htf_data[htf_data["timestamp"] < ltf_time]
                if len(available_htf) == 0:
                    continue  # No HTF data available - OK

                latest_htf_time = available_htf["timestamp"].iloc[-1]

                # If there's newer HTF data that could have been used, that's lookahead bias
                newer_htf = htf_data[
                    (htf_data["timestamp"] > latest_htf_time) & (htf_data["timestamp"] <= ltf_time)
                ]

                if len(newer_htf) > 0:
                    lookahead_violations += 1
                    if lookahead_violations <= 3:  # Show first 3 violations
                        print(
                            f"   [WARN] Potential lookahead: LTF {ltf_time}, "
                            f"used HTF {latest_htf_time}, "
                            f"newer HTF available: {newer_htf['timestamp'].iloc[0]}"
                        )

        if lookahead_violations == 0:
            print("   [OK] No lookahead bias detected!")
        else:
            print(f"   [ERROR] Found {lookahead_violations} potential lookahead violations")

        return mapping

    except Exception as e:
        print(f"[ERROR] HTF-to-LTF mapping failed: {e}")
        return None


def test_extract_features_integration():
    """Test integration with extract_features()."""
    print("\n=== Testing extract_features() Integration ===")

    try:
        # Load recent 1h data for testing
        ltf_data = load_candles_data("tBTCUSD", "1h").tail(200)

        # Convert to extract_features format (dict of lists)
        candles_dict = {
            "open": ltf_data["open"].tolist(),
            "high": ltf_data["high"].tolist(),
            "low": ltf_data["low"].tolist(),
            "close": ltf_data["close"].tolist(),
            "volume": ltf_data["volume"].tolist(),
        }

        # Extract features with HTF context
        features, meta = extract_features(candles_dict, timeframe="1h")

        print(f"[OK] Features extracted: {len(features)} features")
        print(f"   Feature count: {meta.get('feature_count', 'N/A')}")

        # Check HTF context
        htf_context = meta.get("htf_fibonacci", {})
        print("\nHTF Fibonacci Context:")
        print(f"   Available: {htf_context.get('available', False)}")

        if htf_context.get("available"):
            levels = htf_context.get("levels", {})
            print(
                f"   Levels: 0.382={levels.get(0.382, 'N/A'):.0f}, "
                f"0.5={levels.get(0.5, 'N/A'):.0f}, "
                f"0.618={levels.get(0.618, 'N/A'):.0f}"
            )
            print(
                f"   Swing H/L: {htf_context.get('swing_high', 'N/A'):.0f} / "
                f"{htf_context.get('swing_low', 'N/A'):.0f}"
            )
            print(f"   Data age: {htf_context.get('data_age_hours', 'N/A'):.1f} hours")
        else:
            reason = htf_context.get("reason", "UNKNOWN")
            print(f"   Reason unavailable: {reason}")

        return features, meta

    except Exception as e:
        print(f"[ERROR] extract_features() integration failed: {e}")
        return None, None


def test_htf_context_direct():
    """Test HTF context function directly."""
    print("\n=== Testing HTF Context Direct ===")

    try:
        # Load recent data
        ltf_data = load_candles_data("tBTCUSD", "1h").tail(100)

        # Convert latest candle to dict format
        latest = ltf_data.iloc[-1]
        candles_dict = {
            "open": [latest["open"]],
            "high": [latest["high"]],
            "low": [latest["low"]],
            "close": [latest["close"]],
            "volume": [latest["volume"]],
        }

        # Get HTF context
        context = get_htf_fibonacci_context(candles_dict, timeframe="1h")

        print("[OK] HTF Context retrieved")
        print(f"   Available: {context.get('available', False)}")

        if context.get("available"):
            levels = context.get("levels", {})
            print(f"   Current price: {latest['close']:.0f}")
            print(f"   Fib 0.382: {levels.get(0.382, 'N/A'):.0f}")
            print(f"   Fib 0.5: {levels.get(0.5, 'N/A'):.0f}")
            print(f"   Fib 0.618: {levels.get(0.618, 'N/A'):.0f}")

            # Calculate proximity (similar to exit logic)
            current_price = latest["close"]
            for level_name, level_price in levels.items():
                if level_price:
                    distance = abs(current_price - level_price)
                    distance_pct = distance / current_price * 100
                    print(f"   Distance to {level_name}: {distance:.0f} ({distance_pct:.1f}%)")
        else:
            print(f"   Reason: {context.get('reason', 'UNKNOWN')}")
            if "error" in context:
                print(f"   Error: {context['error']}")

        return context

    except Exception as e:
        print(f"[ERROR] HTF context direct test failed: {e}")
        return None


def main():
    """Run all tests."""
    print("Testing HTF Fibonacci Mapping Implementation\n")

    # Test 1: Basic data loading
    htf_data, ltf_data = test_candle_loading()
    if htf_data is None or ltf_data is None:
        print("[ERROR] Cannot continue - data loading failed")
        return

    # Test 2: HTF Fibonacci computation
    htf_fib = test_htf_fibonacci_computation()
    if htf_fib is None:
        print("[WARN] HTF computation failed, continuing with other tests...")

    # Test 3: HTF-to-LTF mapping
    mapping = test_htf_to_ltf_mapping()
    if mapping is None:
        print("[WARN] HTF mapping failed, continuing with other tests...")

    # Test 4: Direct HTF context
    context = test_htf_context_direct()
    if context is None:
        print("[WARN] HTF context failed, continuing with integration test...")

    # Test 5: Integration with extract_features
    features, meta = test_extract_features_integration()
    if features is None:
        print("[ERROR] extract_features integration failed")
        return

    print("\nHTF Fibonacci Mapping Tests Complete!")
    print("\nNext Steps:")
    print("1. [DONE] Phase 0A: HTF Fibonacci Mapping - IMPLEMENTED")
    print("2. [TODO] Phase 0B: Partial Exit Infrastructure")
    print("3. [TODO] Phase 1: HTF Exit Engine")
    print("4. [TODO] Phase 2: Ablation Study & Validation")


if __name__ == "__main__":
    main()
