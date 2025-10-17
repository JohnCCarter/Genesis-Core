#!/usr/bin/env python3
"""
Quick IC ranking per feature for v18 feature sets.

Usage:
  python scripts/feature_ic_v18.py --symbol tBTCUSD --timeframes 1h 3h 6h 1D --horizon 10
"""

import argparse
import csv
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

# Make src importable
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.utils import get_candles_path
from core.utils.data_loader import load_features


def compute_forward_returns(close: pd.Series, horizon: int) -> np.ndarray:
    returns = close.pct_change(horizon).shift(-horizon)
    return returns.values


def ic_rank_for_timeframe(
    symbol: str, timeframe: str, horizon: int
) -> list[tuple[str, float, float, int]]:
    features_df = load_features(symbol, timeframe, version="v18")

    candles_path = get_candles_path(symbol, timeframe)
    candles_df = pd.read_parquet(candles_path)

    forward_returns = compute_forward_returns(candles_df["close"], horizon)

    results: list[tuple[str, float, float, int]] = []
    for name in [c for c in features_df.columns if c != "timestamp"]:
        x = features_df[name].values
        mask = (~np.isnan(x)) & (~np.isnan(forward_returns))
        x = x[mask]
        r = forward_returns[mask]
        n = int(len(x))
        if n < 50:
            continue
        ic, _p = spearmanr(x, r)
        ic = float(ic) if not np.isnan(ic) else 0.0
        t_stat = float(ic) * np.sqrt(max(n - 2, 1)) / np.sqrt(max(1 - ic * ic, 1e-10))
        results.append((name, ic, t_stat, n))

    results.sort(key=lambda z: abs(z[1]), reverse=True)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="IC ranking on v18 features")
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--timeframes", nargs="+", required=True)
    parser.add_argument("--horizon", type=int, default=10)
    parser.add_argument("--output-dir", default="results/feature_ic")

    args = parser.parse_args()

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    for tf in args.timeframes:
        res = ic_rank_for_timeframe(args.symbol, tf, args.horizon)

        print(f"\n=== {args.symbol} {tf} (h={args.horizon}) ===")
        print("Top (|IC|):")
        for i, (name, ic, t, n) in enumerate(res[:10], 1):
            print(f"{i:2d}. {name:25s} IC={ic:+0.4f} t={t:+0.2f} n={n}")
        fib_only = [row for row in res if "fib" in row[0]]
        if fib_only:
            print("Top fib:")
            for name, ic, t, n in fib_only[:10]:
                print(f" - {name:25s} IC={ic:+0.4f} t={t:+0.2f} n={n}")

        csv_path = outdir / f"{args.symbol}_{tf}_v18_feature_ic.csv"
        with open(csv_path, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["feature", "ic", "t", "n"])
            w.writerows(res)
        print(f"[CSV] Saved {csv_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
