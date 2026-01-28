"""Curate 3h candles from existing lower-timeframe candles.

Why:
- Switching the strategy from 1h to 3h requires a candles parquet for 3h.
- The backtest engine and some indicators look for these paths (priority order):
  1) data/raw/{symbol}_{tf}_frozen.parquet
  2) data/curated/v1/candles/{symbol}_{tf}.parquet
  3) data/candles/{symbol}_{tf}.parquet

This script generates `*_3h.parquet` from an existing LTF parquet (default: 1h).

Output:
- data/curated/v1/candles/{symbol}_3h.parquet (always)
- data/raw/{symbol}_3h_frozen.parquet (optional via --write-frozen)

Timestamp semantics:
- Assumes input `timestamp` represents the candle OPEN time in UTC.
- Resamples to 3-hour candles anchored at 00:00 UTC (00:00, 03:00, 06:00, ...).

Usage (PowerShell):
  python scripts/curate_3h_candles.py --symbol tBTCUSD --source-tf 1h --write-frozen

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


def _resample_to_3h(df: pd.DataFrame) -> pd.DataFrame:
    required = {"timestamp", "open", "high", "low", "close"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Input candles missing required columns: {sorted(missing)}")

    out = df.copy()
    # The repo commonly stores timestamps as tz-naive datetimes (UTC assumed), but some
    # datasets may still have int64 unix milliseconds. Support both.
    ts = out["timestamp"]
    if pd.api.types.is_integer_dtype(ts) or pd.api.types.is_float_dtype(ts):
        out["timestamp"] = pd.to_datetime(ts, unit="ms", errors="coerce")
    else:
        out["timestamp"] = pd.to_datetime(ts, errors="coerce")
        # If the source is tz-aware, drop tz to keep a tz-naive UTC-as-assumed convention.
        if pd.api.types.is_datetime64tz_dtype(out["timestamp"]):
            out["timestamp"] = out["timestamp"].dt.tz_convert(None)
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

    # Resample to 3H. Label/closed left means timestamp is period start.
    resampled = out.resample("3H", label="left", closed="left").agg(agg)

    # Drop incomplete periods with no data
    resampled = resampled.dropna(subset=["open", "high", "low", "close"]).reset_index()

    cols = ["timestamp", "open", "high", "low", "close"]
    if "volume" in resampled.columns:
        cols.append("volume")
    resampled = resampled[cols]

    return resampled


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default="tBTCUSD")
    ap.add_argument(
        "--source-tf", default="1h", help="input timeframe parquet to resample (default: 1h)"
    )
    ap.add_argument(
        "--write-frozen", action="store_true", help="also write data/raw/{symbol}_3h_frozen.parquet"
    )
    ap.add_argument("--force", action="store_true", help="overwrite outputs if they already exist")
    args = ap.parse_args()

    symbol = str(args.symbol)
    source_tf = str(args.source_tf)

    src = _find_source_parquet(symbol, source_tf)
    df = pd.read_parquet(src)
    out_3h = _resample_to_3h(df)

    curated_out = PROJECT_ROOT / "data" / "curated" / "v1" / "candles" / f"{symbol}_3h.parquet"
    curated_out.parent.mkdir(parents=True, exist_ok=True)

    if curated_out.exists() and not args.force:
        raise SystemExit(f"Refusing to overwrite existing file (use --force): {curated_out}")

    out_3h.to_parquet(curated_out, index=False)
    print(f"[OK] Wrote curated 3h candles: {curated_out} (rows={len(out_3h)})")

    if args.write_frozen:
        frozen_out = PROJECT_ROOT / "data" / "raw" / f"{symbol}_3h_frozen.parquet"
        frozen_out.parent.mkdir(parents=True, exist_ok=True)
        if frozen_out.exists() and not args.force:
            raise SystemExit(f"Refusing to overwrite existing file (use --force): {frozen_out}")
        out_3h.to_parquet(frozen_out, index=False)
        print(f"[OK] Wrote frozen 3h candles: {frozen_out} (rows={len(out_3h)})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
