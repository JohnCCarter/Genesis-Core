#!/usr/bin/env python3
"""
Validate historical candle data quality.

Usage:
    python scripts/validate_data.py --symbol tBTCUSD --timeframe 1m
    python scripts/validate_data.py --symbol tETHUSD --timeframe 1h --verbose
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd


def check_gaps(df: pd.DataFrame, timeframe: str) -> dict:
    """Check for missing timestamps (gaps in data)."""
    # Calculate expected frequency
    freq_map = {
        "1m": "1min",
        "5m": "5min",
        "15m": "15min",
        "30m": "30min",
        "1h": "1h",
        "3h": "3h",
        "6h": "6h",
        "1D": "1D",
        "1W": "1W",
    }
    
    freq = freq_map.get(timeframe)
    if not freq:
        return {"error": f"Unknown timeframe: {timeframe}"}

    # Generate expected range
    start = df["timestamp"].min()
    end = df["timestamp"].max()
    expected = pd.date_range(start=start, end=end, freq=freq)

    # Find gaps
    actual_set = set(df["timestamp"])
    expected_set = set(expected)
    missing = expected_set - actual_set

    gaps = []
    if missing:
        missing_sorted = sorted(missing)
        # Group consecutive gaps
        current_gap_start = None
        current_gap_end = None
        
        for ts in missing_sorted:
            if current_gap_start is None:
                current_gap_start = ts
                current_gap_end = ts
            elif ts == current_gap_end + pd.Timedelta(freq):
                current_gap_end = ts
            else:
                gaps.append({
                    "start": current_gap_start.isoformat(),
                    "end": current_gap_end.isoformat(),
                    "count": len(pd.date_range(current_gap_start, current_gap_end, freq=freq))
                })
                current_gap_start = ts
                current_gap_end = ts
        
        # Add last gap
        if current_gap_start:
            gaps.append({
                "start": current_gap_start.isoformat(),
                "end": current_gap_end.isoformat(),
                "count": len(pd.date_range(current_gap_start, current_gap_end, freq=freq))
            })

    return {
        "total_expected": len(expected),
        "total_actual": len(df),
        "missing_count": len(missing),
        "gaps": gaps[:10],  # Limit to first 10 gaps
        "coverage": len(df) / len(expected) if len(expected) > 0 else 0,
    }


def check_duplicates(df: pd.DataFrame) -> dict:
    """Check for duplicate timestamps."""
    duplicates = df[df.duplicated(subset=["timestamp"], keep=False)]
    
    duplicate_groups = []
    if not duplicates.empty:
        for ts, group in duplicates.groupby("timestamp"):
            duplicate_groups.append({
                "timestamp": ts.isoformat(),
                "count": len(group),
                "prices": group["close"].tolist()
            })

    return {
        "duplicate_count": len(duplicates),
        "duplicate_timestamps": len(duplicate_groups),
        "examples": duplicate_groups[:5],  # First 5 examples
    }


def check_outliers(df: pd.DataFrame, threshold: float = 0.10) -> dict:
    """Check for extreme price movements (outliers)."""
    # Calculate price change percentage
    df["price_change_pct"] = df["close"].pct_change().abs()
    
    # Find outliers (> threshold, e.g., 10%)
    outliers = df[df["price_change_pct"] > threshold]
    
    outlier_list = []
    for idx, row in outliers.head(10).iterrows():
        outlier_list.append({
            "timestamp": row["timestamp"].isoformat(),
            "change_pct": round(row["price_change_pct"] * 100, 2),
            "close": row["close"],
            "prev_close": df.loc[idx - 1, "close"] if idx > 0 else None,
        })

    return {
        "outlier_count": len(outliers),
        "max_change_pct": round(df["price_change_pct"].max() * 100, 2) if len(df) > 1 else 0,
        "threshold_pct": threshold * 100,
        "examples": outlier_list,
    }


def check_zero_volume(df: pd.DataFrame) -> dict:
    """Check for candles with zero volume."""
    zero_volume = df[df["volume"] == 0]
    
    examples = []
    for idx, row in zero_volume.head(10).iterrows():
        examples.append({
            "timestamp": row["timestamp"].isoformat(),
            "close": row["close"],
        })

    return {
        "zero_volume_count": len(zero_volume),
        "zero_volume_pct": round(len(zero_volume) / len(df) * 100, 2) if len(df) > 0 else 0,
        "examples": examples,
    }


def check_ohlc_logic(df: pd.DataFrame) -> dict:
    """Check OHLC consistency (High >= Open/Close, Low <= Open/Close)."""
    # High should be >= both open and close
    high_invalid = df[(df["high"] < df["open"]) | (df["high"] < df["close"])]
    
    # Low should be <= both open and close
    low_invalid = df[(df["low"] > df["open"]) | (df["low"] > df["close"])]
    
    # High should be >= Low
    high_low_invalid = df[df["high"] < df["low"]]

    invalid_examples = []
    for idx, row in pd.concat([high_invalid, low_invalid, high_low_invalid]).head(10).iterrows():
        invalid_examples.append({
            "timestamp": row["timestamp"].isoformat(),
            "open": row["open"],
            "high": row["high"],
            "low": row["low"],
            "close": row["close"],
        })

    return {
        "high_invalid": len(high_invalid),
        "low_invalid": len(low_invalid),
        "high_low_invalid": len(high_low_invalid),
        "total_invalid": len(high_invalid) + len(low_invalid) + len(high_low_invalid),
        "examples": invalid_examples,
    }


def calculate_quality_score(validation_results: dict, total_candles: int) -> float:
    """Calculate overall quality score (0.0 - 1.0)."""
    # Start with perfect score
    score = 1.0
    
    # Deduct for gaps
    coverage = validation_results["gaps"]["coverage"]
    score *= coverage
    
    # Deduct for duplicates
    if validation_results["duplicates"]["duplicate_count"] > 0:
        dup_penalty = validation_results["duplicates"]["duplicate_count"] / total_candles
        score -= min(dup_penalty, 0.1)  # Max 10% penalty
    
    # Deduct for OHLC errors
    if validation_results["ohlc"]["total_invalid"] > 0:
        ohlc_penalty = validation_results["ohlc"]["total_invalid"] / total_candles
        score -= min(ohlc_penalty, 0.2)  # Max 20% penalty
    
    # Slight deduction for high outliers
    outlier_pct = validation_results["outliers"]["outlier_count"] / total_candles
    if outlier_pct > 0.01:  # More than 1%
        score -= min(outlier_pct * 0.5, 0.05)  # Max 5% penalty
    
    return max(score, 0.0)


def validate_data(symbol: str, timeframe: str, verbose: bool = False) -> dict:
    """Run all validation checks on data."""
    print(f"\n{'='*70}")
    print(f"Validating Data: {symbol} {timeframe}")
    print(f"{'='*70}\n")

    # Load data
    data_file = Path(__file__).parent.parent / "data" / "candles" / f"{symbol}_{timeframe}.parquet"
    
    if not data_file.exists():
        print(f"[ERROR] Data file not found: {data_file}")
        return {"error": "file_not_found"}

    df = pd.read_parquet(data_file)
    print(f"[OK] Loaded {len(df):,} candles")
    print(f"     Date range: {df['timestamp'].min()} to {df['timestamp'].max()}\n")

    # Run checks
    results = {}
    
    print("[1/5] Checking for gaps...")
    results["gaps"] = check_gaps(df, timeframe)
    if verbose:
        print(f"      Coverage: {results['gaps']['coverage']*100:.2f}%")
        print(f"      Missing: {results['gaps']['missing_count']} candles")
    
    print("[2/5] Checking for duplicates...")
    results["duplicates"] = check_duplicates(df)
    if verbose:
        print(f"      Duplicates: {results['duplicates']['duplicate_count']}")
    
    print("[3/5] Checking for outliers...")
    results["outliers"] = check_outliers(df)
    if verbose:
        print(f"      Outliers (>10%): {results['outliers']['outlier_count']}")
    
    print("[4/5] Checking for zero volume...")
    results["zero_volume"] = check_zero_volume(df)
    if verbose:
        print(f"      Zero volume: {results['zero_volume']['zero_volume_count']}")
    
    print("[5/5] Checking OHLC consistency...")
    results["ohlc"] = check_ohlc_logic(df)
    if verbose:
        print(f"      Invalid: {results['ohlc']['total_invalid']}")

    # Calculate quality score
    quality_score = calculate_quality_score(results, len(df))
    
    results["summary"] = {
        "symbol": symbol,
        "timeframe": timeframe,
        "total_candles": len(df),
        "quality_score": round(quality_score, 4),
        "validated_at": datetime.now().isoformat(),
    }

    return results


def print_report(results: dict):
    """Print validation report."""
    summary = results.get("summary", {})
    
    print(f"\n{'='*70}")
    print("VALIDATION REPORT")
    print(f"{'='*70}")
    print(f"Symbol:        {summary.get('symbol')}")
    print(f"Timeframe:     {summary.get('timeframe')}")
    print(f"Total Candles: {summary.get('total_candles'):,}")
    print(f"\nQuality Score: {summary.get('quality_score')} / 1.0")
    
    # Interpret score
    score = summary.get("quality_score", 0)
    if score >= 0.99:
        quality = "[EXCELLENT]"
    elif score >= 0.95:
        quality = "[GOOD]"
    elif score >= 0.90:
        quality = "[ACCEPTABLE]"
    else:
        quality = "[POOR]"
    
    print(f"Quality:       {quality}")
    print(f"{'='*70}")
    
    # Detailed results
    gaps = results.get("gaps", {})
    print(f"\n[GAPS]")
    print(f"  Coverage:      {gaps.get('coverage', 0)*100:.2f}%")
    print(f"  Missing:       {gaps.get('missing_count', 0)} candles")
    if gaps.get("gaps"):
        print(f"  Gap periods:   {len(gaps['gaps'])} (showing first few)")
        for gap in gaps["gaps"][:3]:
            print(f"    - {gap['start']} to {gap['end']} ({gap['count']} candles)")
    
    dups = results.get("duplicates", {})
    print(f"\n[DUPLICATES]")
    print(f"  Total:         {dups.get('duplicate_count', 0)}")
    
    outliers = results.get("outliers", {})
    print(f"\n[OUTLIERS]")
    print(f"  Count (>10%):  {outliers.get('outlier_count', 0)}")
    print(f"  Max change:    {outliers.get('max_change_pct', 0)}%")
    
    zv = results.get("zero_volume", {})
    print(f"\n[ZERO VOLUME]")
    print(f"  Count:         {zv.get('zero_volume_count', 0)}")
    print(f"  Percentage:    {zv.get('zero_volume_pct', 0)}%")
    
    ohlc = results.get("ohlc", {})
    print(f"\n[OHLC CONSISTENCY]")
    print(f"  Invalid:       {ohlc.get('total_invalid', 0)}")
    
    print(f"{'='*70}\n")


def save_report(results: dict, symbol: str, timeframe: str):
    """Save validation report to metadata."""
    metadata_dir = Path(__file__).parent.parent / "data" / "metadata"
    metadata_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"{symbol}_{timeframe}_validation.json"
    filepath = metadata_dir / filename
    
    with open(filepath, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"[SAVED] Validation report: {filepath}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Validate historical candle data quality")
    parser.add_argument("--symbol", type=str, required=True, help="Trading pair (e.g., tBTCUSD)")
    parser.add_argument("--timeframe", type=str, required=True, help="Candle timeframe")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    try:
        # Run validation
        results = validate_data(args.symbol, args.timeframe, args.verbose)
        
        if "error" in results:
            return 1
        
        # Print report
        print_report(results)
        
        # Save report
        save_report(results, args.symbol, args.timeframe)
        
        # Return non-zero if quality is poor
        quality_score = results["summary"]["quality_score"]
        if quality_score < 0.90:
            print("[WARN] Quality score below 0.90 - consider re-fetching data")
            return 2
        
        return 0
        
    except KeyboardInterrupt:
        print("\n[CANCELLED] Interrupted by user")
        return 1
    except Exception as e:
        print(f"\n[FAILED] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
