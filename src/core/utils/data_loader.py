"""Utilities for loading ML data efficiently."""

from pathlib import Path

import pandas as pd


def load_features(symbol: str, timeframe: str) -> pd.DataFrame:
    """
    Load features with smart format selection.

    Tries Feather first (2× faster reads), falls back to Parquet.

    Args:
        symbol: Trading symbol (e.g., 'tBTCUSD')
        timeframe: Timeframe (e.g., '1h', '15m')

    Returns:
        DataFrame with features (timestamp + feature columns)

    Raises:
        FileNotFoundError: If neither Feather nor Parquet exists
        ValueError: If loaded DataFrame is empty

    Example:
        >>> features = load_features('tBTCUSD', '1h')
        >>> print(features.columns)
        Index(['timestamp', 'bb_position', 'trend_confluence', 'rsi'], dtype='object')
    """
    feather_path = Path(f"data/features/{symbol}_{timeframe}_features.feather")
    parquet_path = Path(f"data/features/{symbol}_{timeframe}_features.parquet")

    # Try Feather first (faster: ~20ms vs ~40ms for Parquet)
    if feather_path.exists():
        features_df = pd.read_feather(feather_path)
    # Fallback to Parquet (slower but always available from precompute_features.py)
    elif parquet_path.exists():
        features_df = pd.read_parquet(parquet_path)
    # Neither exists - error with helpful message
    else:
        raise FileNotFoundError(
            f"Features not found for {symbol} {timeframe}:\n"
            f"  Feather: {feather_path}\n"
            f"  Parquet: {parquet_path}\n"
            f"Run: python scripts/precompute_features.py --symbol {symbol} --timeframe {timeframe}"
        )

    if features_df.empty:
        raise ValueError(f"Features DataFrame is empty for {symbol} {timeframe}")

    return features_df
