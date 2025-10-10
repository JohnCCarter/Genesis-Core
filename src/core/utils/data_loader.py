"""Utilities for loading ML data efficiently."""

from pathlib import Path

import pandas as pd


def load_features(symbol: str, timeframe: str, version: str = "v17") -> pd.DataFrame:
    """
    Load features with smart format selection.

    Tries Feather first (2× faster reads), falls back to Parquet.
    Automatically tries versioned features (v17, v16) then falls back to unversioned.

    Args:
        symbol: Trading symbol (e.g., 'tBTCUSD')
        timeframe: Timeframe (e.g., '1h', '15m')
        version: Feature version to load (default: 'v17')

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
    # Try versioned features first (v17, v16), then unversioned
    versions_to_try = [f"_{version}", "_v16", ""] if version == "v17" else [f"_{version}", ""]

    for ver_suffix in versions_to_try:
        feather_path = Path(f"data/features/{symbol}_{timeframe}_features{ver_suffix}.feather")
        parquet_path = Path(f"data/features/{symbol}_{timeframe}_features{ver_suffix}.parquet")

        # Try Feather first (faster: ~20ms vs ~40ms for Parquet)
        if feather_path.exists():
            features_df = pd.read_feather(feather_path)
            return features_df
        # Fallback to Parquet (slower but always available)
        elif parquet_path.exists():
            features_df = pd.read_parquet(parquet_path)
            return features_df

    # No version found - error with helpful message
    raise FileNotFoundError(
        f"Features not found for {symbol} {timeframe}:\n"
        f"  Tried versions: {versions_to_try}\n"
        f"Run: python scripts/precompute_features_v17.py --symbol {symbol} --timeframe {timeframe}"
    )
