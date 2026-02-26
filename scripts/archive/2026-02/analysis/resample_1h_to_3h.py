from __future__ import annotations

from pathlib import Path

import pandas as pd


def resample_1h_to_3h(*, symbol: str = "tBTCUSD") -> Path:
    """Resample frozen 1h candles to frozen 3h candles.

    This is intended for deterministic local experiments where we want 3h to be a pure
    aggregation of the canonical 1h frozen dataset.

    Input:
      data/raw/{symbol}_1h_frozen.parquet

    Output:
      data/raw/{symbol}_3h_frozen.parquet
    """

    input_path = Path("data/raw") / f"{symbol}_1h_frozen.parquet"
    output_path = Path("data/raw") / f"{symbol}_3h_frozen.parquet"

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    df = pd.read_parquet(input_path)

    required = {"timestamp", "open", "high", "low", "close"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in input: {sorted(missing)}")

    out = df.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True, errors="coerce")
    out = out.dropna(subset=["timestamp"]).sort_values("timestamp")
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

    # 3-hour bins anchored on the natural timestamp boundaries.
    df_3h = out.resample("3h", label="left", closed="left").agg(agg)
    df_3h = df_3h.dropna(subset=["open", "high", "low", "close"]).reset_index()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_3h.to_parquet(output_path, index=False)
    return output_path


def main() -> int:
    path = resample_1h_to_3h(symbol="tBTCUSD")
    print(f"[OK] Wrote: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
