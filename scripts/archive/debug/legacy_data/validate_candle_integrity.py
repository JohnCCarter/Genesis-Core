#!/usr/bin/env python3
"""
Validate candle data integrity - detect synthetic/paper data.

Checks for signs of synthetic data:
1. Flat bars (high == low)
2. Zero volume bars
3. Identical open/close
4. Unrealistic ATR (too low)
5. Time gaps
6. Suspicious patterns

Usage:
    python scripts/validate_candle_integrity.py --symbol tBTCUSD --timeframe 1h
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def validate_candles(df: pd.DataFrame) -> dict:
    """
    Comprehensive candle integrity validation.

    Returns dict with issues found and integrity score.
    """
    issues = {}
    total_bars = len(df)

    # 1. Flat bars (high == low) - suspicious for real market data
    flat_bars = (df["high"] == df["low"]).sum()
    issues["flat_bars"] = {
        "count": int(flat_bars),
        "pct": float(flat_bars / total_bars * 100),
        "threshold": 2.0,  # >2% is suspicious
        "status": "FAIL" if (flat_bars / total_bars) > 0.02 else "OK",
    }

    # 2. Zero values
    zero_open = (df["open"] == 0).sum()
    zero_high = (df["high"] == 0).sum()
    zero_low = (df["low"] == 0).sum()
    zero_close = (df["close"] == 0).sum()
    zero_volume = (df["volume"] == 0).sum()

    total_zeros = zero_open + zero_high + zero_low + zero_close
    issues["zero_values"] = {
        "open": int(zero_open),
        "high": int(zero_high),
        "low": int(zero_low),
        "close": int(zero_close),
        "volume": int(zero_volume),
        "total_ohlc": int(total_zeros),
        "status": "FAIL" if total_zeros > 0 else "OK",
    }

    # 3. Identical open/close (doji pattern - OK in moderation)
    identical_oc = (df["open"] == df["close"]).sum()
    issues["identical_open_close"] = {
        "count": int(identical_oc),
        "pct": float(identical_oc / total_bars * 100),
        "threshold": 5.0,  # >5% is suspicious
        "status": "FAIL" if (identical_oc / total_bars) > 0.05 else "OK",
    }

    # 4. Static bars (open==high==low==close)
    static_bars = (
        (df["open"] == df["high"]) & (df["high"] == df["low"]) & (df["low"] == df["close"])
    ).sum()
    issues["static_bars"] = {
        "count": int(static_bars),
        "pct": float(static_bars / total_bars * 100),
        "threshold": 1.0,  # >1% is very suspicious
        "status": "FAIL" if (static_bars / total_bars) > 0.01 else "OK",
    }

    # 5. Time gaps (missing candles)
    if "timestamp" in df.columns:
        time_diffs = pd.to_datetime(df["timestamp"]).diff()
        expected_diff = time_diffs.mode()[0] if len(time_diffs.mode()) > 0 else pd.Timedelta("1h")
        gaps = (time_diffs > expected_diff * 1.5).sum()
        issues["time_gaps"] = {
            "count": int(gaps),
            "pct": float(gaps / total_bars * 100),
            "expected_interval": str(expected_diff),
            "status": "WARN" if gaps > total_bars * 0.01 else "OK",
        }

    # 6. ATR analysis (unrealistic if too low)
    from core.indicators.atr import calculate_atr

    atr = calculate_atr(df["high"].tolist(), df["low"].tolist(), df["close"].tolist(), period=14)
    atr_arr = np.array(atr)
    atr_pct = atr_arr / df["close"].values

    # Real BTC usually has ATR > 0.5% even in calm periods
    very_low_atr = (atr_pct < 0.001).sum()  # <0.1% is unrealistic
    median_atr_pct = np.nanmedian(atr_pct) * 100

    issues["atr_realism"] = {
        "median_atr_pct": float(median_atr_pct),
        "very_low_count": int(very_low_atr),
        "very_low_pct": float(very_low_atr / len(atr_pct) * 100),
        "expected_min": 0.5,  # BTC should have >0.5% ATR typically
        "status": "FAIL" if median_atr_pct < 0.3 else "WARN" if median_atr_pct < 0.5 else "OK",
    }

    # 7. Price precision (check for rounding artifacts)
    # Real exchanges have fine precision, paper might round
    close_decimals = df["close"].apply(lambda x: len(str(x).split(".")[-1]) if "." in str(x) else 0)
    low_precision_count = (close_decimals <= 2).sum()

    issues["price_precision"] = {
        "median_decimals": int(close_decimals.median()),
        "low_precision_count": int(low_precision_count),
        "low_precision_pct": float(low_precision_count / total_bars * 100),
        "status": "WARN" if low_precision_count > total_bars * 0.1 else "OK",
    }

    # 8. High/Low range validation
    # high should always >= close, low should always <= close
    invalid_high = (df["high"] < df["close"]).sum()
    invalid_low = (df["low"] > df["close"]).sum()
    invalid_high_open = (df["high"] < df["open"]).sum()
    invalid_low_open = (df["low"] > df["open"]).sum()

    issues["ohlc_validity"] = {
        "high_below_close": int(invalid_high),
        "low_above_close": int(invalid_low),
        "high_below_open": int(invalid_high_open),
        "low_above_open": int(invalid_low_open),
        "status": "FAIL" if (invalid_high + invalid_low) > 0 else "OK",
    }

    # Calculate overall integrity score
    failed = sum(1 for v in issues.values() if isinstance(v, dict) and v.get("status") == "FAIL")
    warned = sum(1 for v in issues.values() if isinstance(v, dict) and v.get("status") == "WARN")
    passed = sum(1 for v in issues.values() if isinstance(v, dict) and v.get("status") == "OK")

    total_checks = failed + warned + passed
    integrity_score = (passed + warned * 0.5) / total_checks if total_checks > 0 else 0.0

    return {
        "total_bars": total_bars,
        "issues": issues,
        "summary": {
            "passed": passed,
            "warned": warned,
            "failed": failed,
            "integrity_score": float(integrity_score),
        },
    }


def print_report(validation_result: dict):
    """Print validation report."""
    print("\n" + "=" * 80)
    print("CANDLE INTEGRITY REPORT")
    print("=" * 80)

    summary = validation_result["summary"]
    score = summary["integrity_score"]

    print(f"\nTotal bars: {validation_result['total_bars']}")
    print(f"Integrity Score: {score:.2%}")
    print(f"  Passed: {summary['passed']}")
    print(f"  Warnings: {summary['warned']}")
    print(f"  Failed: {summary['failed']}")

    # Status
    if score >= 0.95:
        print("\n[EXCELLENT] Data appears to be HIGH QUALITY real market data!")
    elif score >= 0.80:
        print("\n[GOOD] Data quality is acceptable with minor issues")
    elif score >= 0.60:
        print("\n[WARNING] Data quality is QUESTIONABLE - review issues")
    else:
        print("\n[CRITICAL] Data appears to be SYNTHETIC/LOW QUALITY!")
        print("DO NOT use for ML training!")

    # Detailed issues
    print("\n" + "=" * 80)
    print("DETAILED CHECKS")
    print("=" * 80)

    for check_name, check_data in validation_result["issues"].items():
        if not isinstance(check_data, dict):
            continue

        status = check_data.get("status", "UNKNOWN")
        symbol = {"OK": "[OK]", "WARN": "[WARN]", "FAIL": "[FAIL]"}.get(status, "[?]")

        print(f"\n{symbol} {check_name.replace('_', ' ').title()}:")

        for key, value in check_data.items():
            if key != "status":
                print(f"  {key}: {value}")

    print("\n" + "=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Validate candle data integrity")
    parser.add_argument("--symbol", required=True, help="Symbol")
    parser.add_argument("--timeframe", required=True, help="Timeframe")
    parser.add_argument("--output", help="Output JSON path")

    args = parser.parse_args()

    print("=" * 80)
    print("CANDLE DATA INTEGRITY VALIDATION")
    print("=" * 80)
    print(f"Symbol: {args.symbol}")
    print(f"Timeframe: {args.timeframe}")

    # Load candles
    candles_path = Path(f"data/candles/{args.symbol}_{args.timeframe}.parquet")
    if not candles_path.exists():
        print(f"\nError: File not found: {candles_path}")
        sys.exit(1)

    df = pd.read_parquet(candles_path)
    print(f"File: {candles_path}")
    print(f"Size: {candles_path.stat().st_size / 1024:.1f} KB")

    # Validate
    print("\n[VALIDATE] Running integrity checks...")
    validation_result = validate_candles(df)

    # Print report
    print_report(validation_result)

    # Save results
    if args.output:
        import json

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(validation_result, f, indent=2)
        print(f"\n[SAVED] Results: {output_path}")

    # Exit code based on score
    score = validation_result["summary"]["integrity_score"]
    if score < 0.80:
        print("\n[ACTION REQUIRED] Data quality is below threshold!")
        print("Recommendation: Fetch fresh data from Bitfinex REST API")
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
