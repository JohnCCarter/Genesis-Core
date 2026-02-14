#!/usr/bin/env python3
"""Test HTF Fibonacci Mapping for Genesis-Core.

Manual script (not a pytest test).
"""

from __future__ import annotations

import sys
from pathlib import Path


def _bootstrap_src_on_path() -> None:
    # scripts/<this file> -> repo root is parents[1]
    repo_root = Path(__file__).resolve().parents[1]
    src_dir = repo_root / "src"
    if src_dir.is_dir() and str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))


_bootstrap_src_on_path()

import pandas as pd  # noqa: E402

from core.indicators.htf_fibonacci import (  # noqa: E402
    compute_htf_fibonacci_mapping,
    get_htf_fibonacci_context,
    load_candles_data,
)
from core.strategy.features_asof import extract_features_backtest  # noqa: E402


def test_candle_loading():
    print("=== Testing Candle Loading ===")

    try:
        htf_data = load_candles_data("tBTCUSD", "1D")
        print(f"[OK] Loaded 1D data: {len(htf_data)} candles")
        print(f"   Date range: {htf_data['timestamp'].min()} to {htf_data['timestamp'].max()}")

        ltf_data = load_candles_data("tBTCUSD", "1h")
        print(f"[OK] Loaded 1h data: {len(ltf_data)} candles")
        print(f"   Date range: {ltf_data['timestamp'].min()} to {ltf_data['timestamp'].max()}")

        return htf_data, ltf_data
    except Exception as e:
        print(f"[ERROR] Candle loading failed: {e}")
        return None, None


def test_htf_fibonacci_computation():
    print("\n=== Testing HTF Fibonacci Computation ===")

    try:
        htf_data = load_candles_data("tBTCUSD", "1D")
        htf_test = htf_data.tail(100).copy().reset_index(drop=True)

        from core.indicators.htf_fibonacci import compute_htf_fibonacci_levels

        htf_fib = compute_htf_fibonacci_levels(htf_test)
        print(f"[OK] Computed HTF Fibonacci levels: {len(htf_fib)} rows")

        recent = htf_fib.tail(5)
        print("\nRecent HTF Fibonacci Levels:")
        for _, row in recent.iterrows():
            date = row["timestamp"].strftime("%Y-%m-%d")
            levels = (
                f"0.382:{row['htf_fib_0382']:.0f} | 0.5:{row['htf_fib_05']:.0f} | "
                f"0.618:{row['htf_fib_0618']:.0f}"
            )
            swing = f"H:{row['htf_swing_high']:.0f} L:{row['htf_swing_low']:.0f}"
            print(f"   {date}: {levels} | {swing}")

        return htf_fib
    except Exception as e:
        print(f"[ERROR] HTF Fibonacci computation failed: {e}")
        return None


def test_htf_to_ltf_mapping():
    print("\n=== Testing HTF-to-LTF Mapping ===")

    try:
        htf_data = load_candles_data("tBTCUSD", "1D").tail(30)
        ltf_data = load_candles_data("tBTCUSD", "1h").tail(200)

        mapping = compute_htf_fibonacci_mapping(htf_data, ltf_data)
        print(f"[OK] Created HTF-to-LTF mapping: {len(mapping)} LTF bars")

        print("\nVerifying AS-OF Semantics:")
        for i in [0, len(mapping) // 2, -1]:
            ltf_row = mapping.iloc[i]
            ltf_time = ltf_row["timestamp"]

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
                    f"   LTF {ltf_time.strftime('%Y-%m-%d %H:%M')}: "
                    "No HTF data available (expected)"
                )

        print("\nChecking for Lookahead Bias:")
        lookahead_violations = 0

        for _i, ltf_row in mapping.iterrows():
            ltf_time = ltf_row["timestamp"]

            if not pd.isna(ltf_row["htf_fib_0618"]):
                available_htf = htf_data[htf_data["timestamp"] < ltf_time]
                if len(available_htf) == 0:
                    continue

                latest_htf_time = available_htf["timestamp"].iloc[-1]
                newer_htf = htf_data[
                    (htf_data["timestamp"] > latest_htf_time) & (htf_data["timestamp"] <= ltf_time)
                ]

                if len(newer_htf) > 0:
                    lookahead_violations += 1
                    if lookahead_violations <= 3:
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
    print("\n=== Testing extract_features() Integration ===")

    try:
        ltf_data = load_candles_data("tBTCUSD", "1h").tail(200)
        candles_dict = {
            "open": ltf_data["open"].tolist(),
            "high": ltf_data["high"].tolist(),
            "low": ltf_data["low"].tolist(),
            "close": ltf_data["close"].tolist(),
            "volume": ltf_data["volume"].tolist(),
        }

        features, meta = extract_features_backtest(
            candles_dict,
            asof_bar=len(candles_dict["close"]) - 1,
            timeframe="1h",
            symbol="tBTCUSD",
        )
        print(f"[OK] Features extracted: {len(features)} features")
        print(f"   Feature count: {meta.get('feature_count', 'N/A')}")

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
    print("\n=== Testing HTF Context Direct ===")

    try:
        ltf_data = load_candles_data("tBTCUSD", "1h").tail(100)
        latest = ltf_data.iloc[-1]
        candles_dict = {
            "open": [latest["open"]],
            "high": [latest["high"]],
            "low": [latest["low"]],
            "close": [latest["close"]],
            "volume": [latest["volume"]],
        }

        context = get_htf_fibonacci_context(candles_dict, timeframe="1h")

        print("[OK] HTF Context retrieved")
        print(f"   Available: {context.get('available', False)}")

        if context.get("available"):
            levels = context.get("levels", {})
            print(f"   Current price: {latest['close']:.0f}")
            print(f"   Fib 0.382: {levels.get(0.382, 'N/A'):.0f}")
            print(f"   Fib 0.5: {levels.get(0.5, 'N/A'):.0f}")
            print(f"   Fib 0.618: {levels.get(0.618, 'N/A'):.0f}")
        else:
            print(f"   Reason: {context.get('reason', 'UNKNOWN')}")
            if "error" in context:
                print(f"   Error: {context['error']}")

        return context

    except Exception as e:
        print(f"[ERROR] HTF context direct test failed: {e}")
        return None


def main():
    print("Testing HTF Fibonacci Mapping Implementation\n")

    htf_data, ltf_data = test_candle_loading()
    if htf_data is None or ltf_data is None:
        print("[ERROR] Cannot continue - data loading failed")
        return

    htf_fib = test_htf_fibonacci_computation()
    if htf_fib is None:
        print("[WARN] HTF computation failed, continuing with other tests...")

    mapping = test_htf_to_ltf_mapping()
    if mapping is None:
        print("[WARN] HTF mapping failed, continuing with other tests...")

    context = test_htf_context_direct()
    if context is None:
        print("[WARN] HTF context failed, continuing with integration test...")

    features, meta = test_extract_features_integration()
    if features is None:
        print("[ERROR] extract_features integration failed")
        return

    print("\nHTF Fibonacci Mapping Tests Complete!")


if __name__ == "__main__":
    main()
