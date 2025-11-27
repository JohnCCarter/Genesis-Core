#!/usr/bin/env python3
"""
Validate that vectorized ATR computation matches per-sample ATR.

Usage (from project root):
    python -m scripts.validate_atr_vectorized --symbol tBTCUSD --timeframe 1h
    python -m scripts.validate_atr_vectorized --symbol tBTCUSD --timeframe 1h --samples 500 --tolerance 1e-8
"""

# ruff: noqa: E402

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Lägg till src/ på sys.path så att `core.*` blir importbart
ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from core.indicators.vectorized import calculate_all_features_vectorized
from core.strategy.features_asof import extract_features_backtest
from core.utils import get_candles_path


def compute_per_sample_atr(df: pd.DataFrame, max_samples: int = 100) -> pd.DataFrame:
    """
    Beräkna ATR via ORIGINAL per-bar-logiken (extract_features_backtest).

    Detta är "ground truth" som vi jämför vectorized mot.
    """
    features_list: list[dict] = []

    start_idx = max(0, len(df) - max_samples)
    total = len(df) - start_idx
    print(f"[PER-SAMPLE] Beräknar ATR för {total} barer (långsam men korrekt)...")

    seen_keys_printed = False

    for i in range(start_idx, len(df)):
        candles_window = {
            "open": df["open"].iloc[: i + 1].tolist(),
            "high": df["high"].iloc[: i + 1].tolist(),
            "low": df["low"].iloc[: i + 1].tolist(),
            "close": df["close"].iloc[: i + 1].tolist(),
            "volume": df["volume"].iloc[: i + 1].tolist(),
        }

        feats, meta = extract_features_backtest(candles_window, asof_bar=i)
        assert meta["asof_bar"] == i, f"Expected asof_bar={i}, got {meta['asof_bar']}"

        if not seen_keys_printed:
            print("\n[DEBUG] Första per-sample feature keys:")
            for k in sorted(feats.keys()):
                print(f"  - {k}")
            print("[DEBUG] (Filtrerar på namn som innehåller 'atr')\n")
            seen_keys_printed = True

        atr_feats = {k: v for k, v in feats.items() if k.lower().startswith("atr_")}

        if not atr_feats and i == start_idx:
            print("[WARN] Hittade inga 'atr'-nycklar i per-sample-features på första baren.")

        row = {"timestamp": df["timestamp"].iloc[i]}
        row.update(atr_feats)
        features_list.append(row)

    return pd.DataFrame(features_list)


def compute_vectorized_atr(df: pd.DataFrame, max_samples: int = 100) -> pd.DataFrame:
    """
    Beräkna ATR via vectorized engine och plocka ut ATR-kolumner.
    """
    print("\n[VECTORIZED] Beräknar features (snabb väg)...")
    vect_df = calculate_all_features_vectorized(df)

    if "timestamp" not in vect_df.columns:
        vect_df.insert(0, "timestamp", df["timestamp"])

    print("\n[DEBUG] Vectorized feature columns (första körningen):")
    for col in sorted(vect_df.columns):
        print(f"  - {col}")
    print("[DEBUG] (Filtrerar på kolumner som innehåller 'atr')\n")

    atr_cols = [c for c in vect_df.columns if c.lower().startswith("atr_")]
    if not atr_cols:
        print("[WARN] Hittade inga 'atr'-kolumner i vectorized-features.")

    cols = ["timestamp"] + atr_cols
    vect_atr = vect_df[cols].tail(max_samples)
    print(f"[VECTORIZED] Har {len(vect_atr)} rader för ATR (sista N barer).")
    return vect_atr


def compare_atr(
    per_sample_df: pd.DataFrame,
    vectorized_df: pd.DataFrame,
    tolerance: float = 1e-6,
) -> dict:
    """
    Jämför per-sample-ATR med vectorized-ATR.
    """
    merged = per_sample_df.merge(
        vectorized_df,
        on="timestamp",
        suffixes=("_per", "_vec"),
    )

    if len(merged) == 0:
        print("[ERROR] Inga matchande timestamps mellan per-sample och vectorized!")
        return {
            "status": "error",
            "message": "No matching timestamps",
        }

    print(f"\n[COMPARE] Jämför {len(merged)} barer...")

    # Hitta ATR-fälten (baserat på per-sample)
    per_cols = [c for c in per_sample_df.columns if c != "timestamp"]
    results = {
        "total_samples": len(merged),
        "features_tested": 0,
        "features": {},
        "summary": {},
    }

    max_diff_overall = 0.0
    worst_feature = None

    for feat in per_cols:
        col_per = f"{feat}_per"
        col_vec = f"{feat}_vec"

        if col_per not in merged.columns or col_vec not in merged.columns:
            print(f"[WARN] ATR-fält '{feat}' saknas i någon av metoderna.")
            continue

        diff = np.abs(merged[col_per] - merged[col_vec])
        max_diff = float(diff.max())
        mean_diff = float(diff.mean())
        median_diff = float(diff.median())
        within = bool((diff <= tolerance).all())

        results["features_tested"] += 1
        results["features"][feat] = {
            "max_diff": max_diff,
            "mean_diff": mean_diff,
            "median_diff": median_diff,
            "within_tolerance": within,
            "tolerance": tolerance,
        }

        if max_diff > max_diff_overall:
            max_diff_overall = max_diff
            worst_feature = feat

        status = "[OK]" if within else "[DIFF]"
        print(
            f"  {feat:<25} {status}  "
            f"max_diff={max_diff:.3e}, mean={mean_diff:.3e}, median={median_diff:.3e}"
        )

    all_within = all(feat_stats["within_tolerance"] for feat_stats in results["features"].values())

    results["summary"] = {
        "all_within_tolerance": bool(all_within),
        "max_diff_overall": float(max_diff_overall),
        "worst_feature": worst_feature,
        "tolerance": tolerance,
    }

    return results


def print_summary(results: dict) -> None:
    """Skriv ut sammanfattning."""
    print("\n" + "=" * 80)
    print("ATR VALIDATION SUMMARY")
    print("=" * 80)

    summary = results.get("summary", {})
    if not summary:
        print("[ERROR] Tomma resultat.")
        return

    print(f"\nSamples tested:  {results.get('total_samples')}")
    print(f"ATR fields:      {results.get('features_tested')}")
    print(f"Tolerance:       {summary['tolerance']:.2e}")

    print(f"\nMax difference:  {summary['max_diff_overall']:.3e}")
    print(f"Worst feature:   {summary['worst_feature']}")

    if summary["all_within_tolerance"]:
        print("\n[SUCCESS] All ATR-fält inom tolerans.")
    else:
        print("\n[WARNING] Minst ett ATR-fält skiljer mer än toleransen!")
        print("\nFält med problem:")
        for feat, stats in results["features"].items():
            if not stats["within_tolerance"]:
                print(
                    f"  - {feat}: max_diff={stats['max_diff']:.3e}, "
                    f"mean={stats['mean_diff']:.3e}"
                )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate vectorized ATR vs per-sample ATR")
    parser.add_argument("--symbol", required=True, help="Trading symbol, t.ex. tBTCUSD")
    parser.add_argument("--timeframe", required=True, help="Timeframe, t.ex. 1h")
    parser.add_argument(
        "--samples",
        type=int,
        default=200,
        help="Antal sista barer att testa (default: 200)",
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=1e-6,
        help="Max tillåten diff (default: 1e-6)",
    )
    args = parser.parse_args()

    print("\n" + "=" * 80)
    print("ATR VECTORIZED VALIDATION")
    print("=" * 80)
    print(f"Symbol:    {args.symbol}")
    print(f"Timeframe: {args.timeframe}")
    print(f"Samples:   {args.samples}")
    print(f"Tolerance: {args.tolerance:.2e}")

    # Ladda candles
    print("\n[LOAD] Läser candles...")
    try:
        candles_path = get_candles_path(args.symbol, args.timeframe)
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        return 1

    candles_df = pd.read_parquet(candles_path)

    # Per-sample ATR
    per_sample_atr = compute_per_sample_atr(candles_df, args.samples)

    # Vectorized ATR
    vect_atr = compute_vectorized_atr(candles_df, args.samples)

    # Justera per-sample till samma antal rader (ifall off-by-one)
    if len(per_sample_atr) > len(vect_atr):
        per_sample_atr = per_sample_atr.tail(len(vect_atr))
    elif len(vect_atr) > len(per_sample_atr):
        vect_atr = vect_atr.tail(len(per_sample_atr))

    print("\n[VALIDATE] Jämför per-sample vs vectorized ATR...")
    results = compare_atr(per_sample_atr, vect_atr, args.tolerance)
    if results.get("status") == "error":
        print(f"[ERROR] {results.get('message')}")
        return 1

    print_summary(results)

    if results["summary"]["all_within_tolerance"]:
        print("\n" + "=" * 80)
        print("[SUCCESS] ATR vectorized implementation VALIDATED")
        print("=" * 80 + "\n")
        return 0
    else:
        print("\n" + "=" * 80)
        print("[FAILED] ATR vectorized implementation DIFFERS from per-sample")
        print("=" * 80 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
