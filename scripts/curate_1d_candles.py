"""Curate 1D candles from existing lower-timeframe candles.

This repository currently uses HTF (1D) candles for HTF Fibonacci context and HTF exits.
If 1D data is missing, HTF-related parameters become effectively inert and Optuna trials
can look "identical" even when HTF configs change.

This script generates `tBTCUSD_1D.parquet` from an existing LTF parquet (default: 1h).

Input priority (matches engine/indicator conventions):
  1) data/raw/{symbol}_{tf}_frozen.parquet
  2) data/curated/v1/candles/{symbol}_{tf}.parquet
  3) data/candles/{symbol}_{tf}.parquet

Output:
  - data/curated/v1/candles/{symbol}_1D.parquet (always)
  - data/raw/{symbol}_1D_frozen.parquet (optional via --write-frozen)

Timestamp semantics:
- Assumes input `timestamp` represents the candle OPEN time in UTC.
- Resamples to daily candles anchored at 00:00 UTC.

Usage (PowerShell):
  python scripts/curate_1d_candles.py --symbol tBTCUSD --source-tf 1h --write-frozen

Note:
- This is a local data operation. Be careful committing large parquet files.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _find_source_parquet(symbol: str, timeframe: str) -> Path:
    base = PROJECT_ROOT / "data"
    candidates = [
        base / "raw" / f"{symbol}_{timeframe}_frozen.parquet",
        base / "curated" / "v1" / "candles" / f"{symbol}_{timeframe}.parquet",
        base / "candles" / f"{symbol}_{timeframe}.parquet",
    ]
    for p in candidates:
        if p.exists():
            return p
    tried = ", ".join(str(p) for p in candidates)
    raise FileNotFoundError(
        f"No source candles parquet found for {symbol} {timeframe}. Tried: {tried}"
    )


def _resample_to_1d(df: pd.DataFrame) -> pd.DataFrame:
    required = {"timestamp", "open", "high", "low", "close"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Input candles missing required columns: {sorted(missing)}")

    out = df.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True, errors="coerce")
    out = out.dropna(subset=["timestamp"]).sort_values("timestamp")

    # Defensive: drop duplicate timestamps (keep first occurrence)
    out = out.drop_duplicates(subset=["timestamp"], keep="first")

    out = out.set_index("timestamp")

    agg = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
    }
    if "volume" in out.columns:
        agg["volume"] = "sum"

    # Resample to 1D (00:00 UTC boundaries). Label/closed left means timestamp is period start.
    daily = out.resample("1D", label="left", closed="left").agg(agg)

    # Drop incomplete days with no data
    daily = daily.dropna(subset=["open", "high", "low", "close"]).reset_index()

    # Keep a stable column order
    cols = ["timestamp", "open", "high", "low", "close"]
    if "volume" in daily.columns:
        cols.append("volume")
    daily = daily[cols]

    return daily


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default="tBTCUSD")
    ap.add_argument(
        "--source-tf", default="1h", help="input timeframe parquet to resample (default: 1h)"
    )
    ap.add_argument(
        "--write-frozen", action="store_true", help="also write data/raw/{symbol}_1D_frozen.parquet"
    )
    ap.add_argument("--force", action="store_true", help="overwrite outputs if they already exist")
    args = ap.parse_args()

    symbol = str(args.symbol)
    source_tf = str(args.source_tf)

    src = _find_source_parquet(symbol, source_tf)
    df = pd.read_parquet(src)
    daily = _resample_to_1d(df)

    curated_out = PROJECT_ROOT / "data" / "curated" / "v1" / "candles" / f"{symbol}_1D.parquet"
    curated_out.parent.mkdir(parents=True, exist_ok=True)

    if curated_out.exists() and not args.force:
        raise SystemExit(f"Refusing to overwrite existing file (use --force): {curated_out}")

    daily.to_parquet(curated_out, index=False)
    print(f"[OK] Wrote curated 1D candles: {curated_out} (rows={len(daily)})")

    if args.write_frozen:
        frozen_out = PROJECT_ROOT / "data" / "raw" / f"{symbol}_1D_frozen.parquet"
        frozen_out.parent.mkdir(parents=True, exist_ok=True)
        if frozen_out.exists() and not args.force:
            raise SystemExit(f"Refusing to overwrite existing file (use --force): {frozen_out}")
        daily.to_parquet(frozen_out, index=False)
        print(f"[OK] Wrote frozen 1D candles: {frozen_out} (rows={len(daily)})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
