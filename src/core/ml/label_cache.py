"""
Label caching utilities to avoid recomputing expensive triple-barrier labels.

Performance impact: ~5 minutes saved per configuration (27 configs = 135 min saved!)
"""

from pathlib import Path
from typing import Any

import pandas as pd


def get_label_cache_key(
    symbol: str,
    timeframe: str,
    k_profit: float,
    k_stop: float,
    max_holding: int,
    atr_period: int = 14,
    version: str = "v2",  # Bump when labeling logic changes
) -> str:
    """
    Generate unique cache key for label configuration.

    Args:
        symbol: Trading symbol
        timeframe: Timeframe
        k_profit: Profit multiplier
        k_stop: Stop multiplier
        max_holding: Max holding bars
        atr_period: ATR calculation period
        version: Cache version (bump when code changes)

    Returns:
        Cache key string (e.g., "tBTCUSD_1h_p1.0_s0.6_H36_atr14_v2")
    """
    return f"{symbol}_{timeframe}_p{k_profit}_s{k_stop}_H{max_holding}_atr{atr_period}_{version}"


def get_label_cache_path(cache_key: str) -> Path:
    """Get full path to label cache file."""
    cache_dir = Path("cache/labels")
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"{cache_key}.parquet"


def load_cached_labels(
    symbol: str,
    timeframe: str,
    k_profit: float,
    k_stop: float,
    max_holding: int,
    atr_period: int = 14,
    version: str = "v2",
) -> list[int | None] | None:
    """
    Load labels from cache if they exist.

    Returns:
        List of labels if cache hit, None if cache miss
    """
    cache_key = get_label_cache_key(
        symbol, timeframe, k_profit, k_stop, max_holding, atr_period, version
    )
    cache_path = get_label_cache_path(cache_key)

    if not cache_path.exists():
        return None

    try:
        df = pd.read_parquet(cache_path, engine="pyarrow")
        labels = df["label"].tolist()

        # Convert NaN to None (Parquet stores None as NaN)
        labels = [None if pd.isna(label) else int(label) for label in labels]

        return labels
    except Exception as e:
        print(f"[CACHE] Warning: Failed to load cache {cache_key}: {e}")
        return None


def save_labels_to_cache(
    labels: list[int | None],
    symbol: str,
    timeframe: str,
    k_profit: float,
    k_stop: float,
    max_holding: int,
    atr_period: int = 14,
    version: str = "v2",
) -> None:
    """
    Save labels to cache for future reuse.

    Args:
        labels: List of labels to cache
        symbol: Trading symbol
        timeframe: Timeframe
        k_profit: Profit multiplier
        k_stop: Stop multiplier
        max_holding: Max holding bars
        atr_period: ATR calculation period
        version: Cache version
    """
    cache_key = get_label_cache_key(
        symbol, timeframe, k_profit, k_stop, max_holding, atr_period, version
    )
    cache_path = get_label_cache_path(cache_key)

    try:
        # Convert to DataFrame (None → NaN for Parquet compatibility)
        df = pd.DataFrame({"label": labels})
        df.to_parquet(cache_path, index=False, compression="snappy", engine="pyarrow")

        print(f"[CACHE] Saved labels to {cache_key}")
    except Exception as e:
        print(f"[CACHE] Warning: Failed to save cache {cache_key}: {e}")


def clear_label_cache(
    symbol: str | None = None,
    timeframe: str | None = None,
) -> int:
    """
    Clear label cache files.

    Args:
        symbol: If provided, only clear this symbol (e.g., "tBTCUSD")
        timeframe: If provided, only clear this timeframe (e.g., "1h")

    Returns:
        Number of files deleted
    """
    cache_dir = Path("cache/labels")

    if not cache_dir.exists():
        return 0

    # Build pattern
    pattern = "*"
    if symbol:
        pattern = f"{symbol}_*"
    if timeframe:
        if symbol:
            pattern = f"{symbol}_{timeframe}_*"
        else:
            pattern = f"*_{timeframe}_*"

    pattern += ".parquet"

    # Delete matching files
    deleted = 0
    for file in cache_dir.glob(pattern):
        file.unlink()
        deleted += 1

    if deleted > 0:
        print(f"[CACHE] Cleared {deleted} label cache file(s)")

    return deleted


def get_cache_info() -> dict[str, Any]:
    """Get information about label cache."""
    cache_dir = Path("cache/labels")

    if not cache_dir.exists():
        return {
            "exists": False,
            "total_files": 0,
            "total_size_mb": 0.0,
        }

    files = list(cache_dir.glob("*.parquet"))
    total_size = sum(f.stat().st_size for f in files)

    return {
        "exists": True,
        "total_files": len(files),
        "total_size_mb": total_size / (1024 * 1024),
        "cache_dir": str(cache_dir.absolute()),
    }
