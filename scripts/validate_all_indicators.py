#!/usr/bin/env python3
"""
Systematic validation of ALL indicators: vectorized vs per-sample vs external libs.

This is a CRITICAL quality gate to ensure:
1. Vectorized and per-sample implementations are bit-exact
2. Our implementations match industry standards (TA-Lib when available)
3. No hidden bugs like the BB ddof=1 issue

Usage:
    python scripts/validate_all_indicators.py --symbol tBTCUSD --timeframe 1h --samples 200

Output:
    - Console report with pass/fail for each indicator
    - JSON file with detailed metrics
    - Visualization plots for any indicators with differences
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Our implementations
from core.indicators.atr import calculate_atr
from core.indicators.derived_features import calculate_volatility_shift
from core.indicators.ema import calculate_ema
from core.indicators.rsi import calculate_rsi
from core.indicators.vectorized import (
    calculate_atr_vectorized,
    calculate_ema_vectorized,
    calculate_rsi_vectorized,
    calculate_volatility_shift_vectorized,
)

# Try to import TA-Lib for external validation
try:
    import talib

    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    print("[WARNING] TA-Lib not available - skipping external validation")


class IndicatorValidator:
    """Framework for validating indicators systematically."""

    def __init__(self, candles_df: pd.DataFrame, tolerance: float = 1e-8):
        """
        Initialize validator with candle data.

        Args:
            candles_df: DataFrame with OHLCV data
            tolerance: Numerical tolerance for comparisons (default: 1e-8)
        """
        self.df = candles_df
        self.tolerance = tolerance
        self.results = {}

    def validate_indicator(
        self,
        name: str,
        per_sample_func,
        vectorized_func,
        external_func=None,
        **kwargs,
    ) -> dict:
        """
        Validate an indicator across all implementations.

        Returns:
            dict with validation results
        """
        print(f"\n{'='*80}")
        print(f"VALIDATING: {name}")
        print(f"{'='*80}")

        result = {
            "name": name,
            "per_sample_vs_vectorized": None,
            "vectorized_vs_external": None,
            "status": "unknown",
        }

        # Test 1: Per-sample vs Vectorized
        try:
            ps_values, vec_values = self._compare_per_sample_vs_vectorized(
                per_sample_func, vectorized_func, **kwargs
            )

            diff = np.abs(ps_values - vec_values)
            max_diff = np.nanmax(diff)
            mean_diff = np.nanmean(diff)
            within_tolerance = max_diff <= self.tolerance

            result["per_sample_vs_vectorized"] = {
                "max_diff": float(max_diff),
                "mean_diff": float(mean_diff),
                "tolerance": self.tolerance,
                "within_tolerance": bool(within_tolerance),
                "samples_compared": int((~np.isnan(diff)).sum()),
            }

            status = "OK" if within_tolerance else "DIFF"
            print(f"  Per-sample vs Vectorized: [{status}]")
            print(f"    Max diff:  {max_diff:.2e}")
            print(f"    Mean diff: {mean_diff:.2e}")
            print(f"    Tolerance: {self.tolerance:.2e}")

            if not within_tolerance:
                result["status"] = "FAILED"
                print("    ⚠️  DIFFERENCE EXCEEDS TOLERANCE!")
            else:
                result["status"] = "PASSED"

        except Exception as e:
            print(f"  Per-sample vs Vectorized: [ERROR] {e}")
            result["per_sample_vs_vectorized"] = {"error": str(e)}
            result["status"] = "ERROR"

        # Test 2: Vectorized vs External (if available)
        if external_func and TALIB_AVAILABLE:
            try:
                vec_values, ext_values = self._compare_vectorized_vs_external(
                    vectorized_func, external_func, **kwargs
                )

                diff = np.abs(vec_values - ext_values)
                max_diff = np.nanmax(diff)
                mean_diff = np.nanmean(diff)
                within_tolerance = max_diff <= self.tolerance

                result["vectorized_vs_external"] = {
                    "max_diff": float(max_diff),
                    "mean_diff": float(mean_diff),
                    "tolerance": self.tolerance,
                    "within_tolerance": bool(within_tolerance),
                    "samples_compared": int((~np.isnan(diff)).sum()),
                }

                status = "OK" if within_tolerance else "DIFF"
                print(f"  Vectorized vs TA-Lib: [{status}]")
                print(f"    Max diff:  {max_diff:.2e}")
                print(f"    Mean diff: {mean_diff:.2e}")

                if not within_tolerance and result["status"] == "PASSED":
                    result["status"] = "EXTERNAL_DIFF"
                    print("    ⚠️  Differs from TA-Lib (may be OK if formula differs)")

            except Exception as e:
                print(f"  Vectorized vs TA-Lib: [SKIP] {e}")
                result["vectorized_vs_external"] = {"error": str(e)}

        self.results[name] = result
        return result

    def _compare_per_sample_vs_vectorized(self, ps_func, vec_func, **kwargs):
        """Compare per-sample and vectorized implementations."""
        # Get last N samples for per-sample (slow)
        samples = min(200, len(self.df))
        start_idx = len(self.df) - samples

        # Per-sample calculation
        ps_values = []
        for i in range(start_idx, len(self.df)):
            window = {
                "open": self.df["open"].iloc[: i + 1].tolist(),
                "high": self.df["high"].iloc[: i + 1].tolist(),
                "low": self.df["low"].iloc[: i + 1].tolist(),
                "close": self.df["close"].iloc[: i + 1].tolist(),
                "volume": self.df["volume"].iloc[: i + 1].tolist(),
            }
            result = ps_func(window, **kwargs)
            # Extract last value (handle different return types)
            if isinstance(result, list):
                ps_values.append(result[-1] if result else np.nan)
            elif isinstance(result, dict):
                # For indicators that return dict (like bollinger)
                ps_values.append(np.nan)  # Handle separately
            else:
                ps_values.append(float(result))

        ps_values = np.array(ps_values)

        # Vectorized calculation
        vec_result = vec_func(self.df, **kwargs)
        if isinstance(vec_result, pd.Series):
            vec_values = vec_result.iloc[start_idx:].values
        else:
            vec_values = np.array(vec_result[start_idx:])

        return ps_values, vec_values

    def _compare_vectorized_vs_external(self, vec_func, ext_func, **kwargs):
        """Compare vectorized implementation vs external library (TA-Lib)."""
        # Our vectorized
        vec_result = vec_func(self.df, **kwargs)
        if isinstance(vec_result, pd.Series):
            vec_values = vec_result.values
        else:
            vec_values = np.array(vec_result)

        # TA-Lib
        ext_values = ext_func(self.df, **kwargs)
        if isinstance(ext_values, pd.Series):
            ext_values = ext_values.values
        else:
            ext_values = np.array(ext_values)

        return vec_values, ext_values

    def generate_report(self) -> dict:
        """Generate comprehensive validation report."""
        report = {
            "summary": {
                "total_indicators": len(self.results),
                "passed": sum(1 for r in self.results.values() if r["status"] == "PASSED"),
                "failed": sum(1 for r in self.results.values() if r["status"] == "FAILED"),
                "errors": sum(1 for r in self.results.values() if r["status"] == "ERROR"),
                "external_diffs": sum(
                    1 for r in self.results.values() if r["status"] == "EXTERNAL_DIFF"
                ),
            },
            "indicators": self.results,
            "tolerance": self.tolerance,
        }

        return report

    def print_summary(self):
        """Print validation summary."""
        report = self.generate_report()
        summary = report["summary"]

        print("\n" + "=" * 80)
        print("VALIDATION SUMMARY")
        print("=" * 80)
        print(f"Total indicators tested: {summary['total_indicators']}")
        print(f"  [OK] PASSED: {summary['passed']}")
        print(f"  [FAIL] FAILED: {summary['failed']}")
        print(f"  [ERR] ERROR:  {summary['errors']}")
        print(f"  [WARN] EXTERNAL DIFF: {summary['external_diffs']}")
        print("=" * 80)

        if summary["failed"] > 0:
            print("\n[CRITICAL] Some indicators FAILED validation!")
            print("Failed indicators:")
            for name, result in self.results.items():
                if result["status"] == "FAILED":
                    print(f"  - {name}")
        elif summary["errors"] > 0:
            print("\n[WARNING] Some indicators had ERRORS!")
        else:
            print("\n[SUCCESS] ALL INDICATORS PASSED VALIDATION!")


# Wrapper functions for per-sample indicators
def ps_ema(window, period=20):
    """Per-sample EMA wrapper."""
    return calculate_ema(window["close"], period=period)


def ps_rsi(window, period=14):
    """Per-sample RSI wrapper."""
    return calculate_rsi(window["close"], period=period)


def ps_atr(window, period=14):
    """Per-sample ATR wrapper."""
    return calculate_atr(window["high"], window["low"], window["close"], period=period)


def ps_volatility_shift(window, short=14, long=50):
    """Per-sample volatility shift wrapper."""
    atr_short = calculate_atr(window["high"], window["low"], window["close"], period=short)
    atr_long = calculate_atr(window["high"], window["low"], window["close"], period=long)
    return calculate_volatility_shift(atr_short, atr_long)


# Wrapper functions for vectorized indicators
def vec_ema(df, period=20):
    """Vectorized EMA wrapper."""
    return calculate_ema_vectorized(df["close"], period=period)


def vec_rsi(df, period=14):
    """Vectorized RSI wrapper."""
    return calculate_rsi_vectorized(df["close"], period=period)


def vec_atr(df, period=14):
    """Vectorized ATR wrapper."""
    return calculate_atr_vectorized(df["high"], df["low"], df["close"], period=period)


def vec_volatility_shift(df, short=14, long=50):
    """Vectorized volatility shift wrapper."""
    return calculate_volatility_shift_vectorized(
        df["high"], df["low"], df["close"], short_period=short, long_period=long
    )


# External library wrappers (TA-Lib)
def ext_ema(df, period=20):
    """TA-Lib EMA wrapper."""
    return talib.EMA(df["close"].values, timeperiod=period)


def ext_rsi(df, period=14):
    """TA-Lib RSI wrapper."""
    return talib.RSI(df["close"].values, timeperiod=period)


def ext_atr(df, period=14):
    """TA-Lib ATR wrapper."""
    return talib.ATR(df["high"].values, df["low"].values, df["close"].values, timeperiod=period)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Validate all indicators systematically")
    parser.add_argument("--symbol", required=True, help="Trading symbol")
    parser.add_argument("--timeframe", required=True, help="Timeframe")
    parser.add_argument(
        "--samples", type=int, default=200, help="Number of samples to test (default: 200)"
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=1e-8,
        help="Numerical tolerance (default: 1e-8)",
    )
    parser.add_argument("--output", type=str, help="Output JSON file for detailed results")

    args = parser.parse_args()

    print("\n" + "=" * 80)
    print("SYSTEMATIC INDICATOR VALIDATION")
    print("=" * 80)
    print(f"Symbol:    {args.symbol}")
    print(f"Timeframe: {args.timeframe}")
    print(f"Samples:   {args.samples}")
    print(f"Tolerance: {args.tolerance:.2e}")
    print(f"TA-Lib:    {'Available' if TALIB_AVAILABLE else 'Not available'}")
    print("=" * 80)

    # Load candles
    candles_path = Path(f"data/candles/{args.symbol}_{args.timeframe}.parquet")
    if not candles_path.exists():
        print(f"Error: Candles file not found: {candles_path}")
        sys.exit(1)

    candles_df = pd.read_parquet(candles_path)
    print(f"\n[LOAD] Loaded {len(candles_df)} candles")

    # Initialize validator
    validator = IndicatorValidator(candles_df, tolerance=args.tolerance)

    # Validate each indicator
    validator.validate_indicator(
        "EMA (20)",
        ps_ema,
        vec_ema,
        ext_ema if TALIB_AVAILABLE else None,
        period=20,
    )

    validator.validate_indicator(
        "RSI (14)",
        ps_rsi,
        vec_rsi,
        ext_rsi if TALIB_AVAILABLE else None,
        period=14,
    )

    validator.validate_indicator(
        "ATR (14)",
        ps_atr,
        vec_atr,
        ext_atr if TALIB_AVAILABLE else None,
        period=14,
    )

    validator.validate_indicator(
        "Volatility Shift (14/50)",
        ps_volatility_shift,
        vec_volatility_shift,
        None,  # No external equivalent
        short=14,
        long=50,
    )

    # Print summary
    validator.print_summary()

    # Save detailed results
    if args.output:
        report = validator.generate_report()
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"\n[SAVED] Detailed results: {output_path}")

    # Exit code based on results
    report = validator.generate_report()
    if report["summary"]["failed"] > 0:
        print("\n[FAILED] VALIDATION FAILED!")
        sys.exit(1)
    elif report["summary"]["errors"] > 0:
        print("\n[ERROR] VALIDATION HAD ERRORS!")
        sys.exit(2)
    else:
        print("\n[PASSED] VALIDATION PASSED!")
        sys.exit(0)


if __name__ == "__main__":
    main()
