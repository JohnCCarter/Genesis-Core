"""HTF Fibonacci candle loading and cache helpers."""

from pathlib import Path
from typing import Any

import pandas as pd

from core.utils import is_case_sensitive_directory, timeframe_filename_suffix

# Cache: {"{symbol}_{htf_timeframe}_{config_hash}": {"fib_df": pd.DataFrame}}
_htf_context_cache: dict[str, dict[str, Any]] = {}

# Small in-memory candle cache to avoid repeated parquet reads in hot paths.
_candles_cache: dict[tuple[str, str], pd.DataFrame] = {}


def load_candles_data(symbol: str, timeframe: str) -> pd.DataFrame:
    """Load candles from frozen/curated/legacy parquet with deterministic priority.

    Priority:
      1) data/raw/{symbol}_{tf}_frozen.parquet
      2) data/curated/v1/candles/{symbol}_{tf}.parquet
      3) data/candles/{symbol}_{tf}.parquet
    """

    tf_in = str(timeframe)
    tf_cache = timeframe_filename_suffix(tf_in)
    cache_key = (symbol, tf_cache)
    cached = _candles_cache.get(cache_key)
    if cached is not None:
        return cached

    repo_root = Path(__file__).resolve().parents[3]
    data_dir = repo_root / "data"

    suffixes: list[str]
    if tf_in in {"1M", "1mo"}:
        suffixes = ["1mo"]
        if is_case_sensitive_directory(data_dir):
            suffixes.append("1M")
    else:
        suffixes = [tf_cache]

    path: Path | None = None
    for tf in suffixes:
        candidates = [
            data_dir / "raw" / f"{symbol}_{tf}_frozen.parquet",
            data_dir / "curated" / "v1" / "candles" / f"{symbol}_{tf}.parquet",
            data_dir / "candles" / f"{symbol}_{tf}.parquet",
        ]
        path = next((p for p in candidates if p.exists()), None)
        if path is not None:
            break
    if path is None:
        tried = []
        for tf in suffixes:
            tried.extend(
                [
                    data_dir / "raw" / f"{symbol}_{tf}_frozen.parquet",
                    data_dir / "curated" / "v1" / "candles" / f"{symbol}_{tf}.parquet",
                    data_dir / "candles" / f"{symbol}_{tf}.parquet",
                ]
            )
        raise FileNotFoundError(
            f"No candle parquet found for {symbol} {tf_cache}. Tried: {', '.join(str(p) for p in tried)}"
        )

    df = pd.read_parquet(path, engine="pyarrow")
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    _candles_cache[cache_key] = df
    return df
