"""Utilities for loading ML data efficiently."""

from pathlib import Path

import pandas as pd


def load_features(symbol: str, timeframe: str, version: str | None = "v17") -> pd.DataFrame:
    """
    Load features with smart format selection.

    Tries curated (v18/v17) first, then archive, then legacy. Supports timestamped files.
    """
    if version:
        version = version.lower()

    if version in (None, "auto"):
        versions_to_try = ["_v18", "_v17", "_v16", ""]
    elif version == "v17":
        versions_to_try = ["_v17", "_v16", ""]
    else:
        versions_to_try = [f"_{version}"]

    base_paths = [
        Path("data/curated/v1/features"),
        Path("data/archive/features"),
        Path("data/features"),
    ]

    def _curated_candidates(base: Path, suffix: str, ext: str) -> list[Path]:
        curated_dir = base / symbol / timeframe
        if not curated_dir.exists():
            return []
        candidates: list[Path] = []
        if suffix:
            exact_name = curated_dir / f"{symbol}_{timeframe}_features{suffix}{ext}"
            candidates.append(exact_name)
            candidates.extend(
                sorted(
                    curated_dir.glob(f"**/{symbol}_{timeframe}_features{suffix}_*{ext}"),
                    reverse=True,
                )
            )
        else:
            exact_name = curated_dir / f"{symbol}_{timeframe}_features{ext}"
            candidates.append(exact_name)
            candidates.extend(
                sorted(curated_dir.glob(f"**/{symbol}_{timeframe}_features_*{ext}"), reverse=True)
            )
        return candidates

    def _flat_candidates(base: Path, suffix: str, ext: str) -> list[Path]:
        name = f"{symbol}_{timeframe}_features{suffix}{ext}"
        candidates = [base / name]
        if suffix:
            candidates.extend(
                sorted(base.glob(f"{symbol}_{timeframe}_features{suffix}_*{ext}"), reverse=True)
            )
        return candidates

    for base in base_paths:
        is_curated = "curated" in base.parts
        for suffix in versions_to_try:
            feather_candidates = (
                _curated_candidates(base, suffix, ".feather")
                if is_curated
                else _flat_candidates(base, suffix, ".feather")
            )
            for path in feather_candidates:
                if path.exists():
                    return pd.read_feather(path)

            parquet_candidates = (
                _curated_candidates(base, suffix, ".parquet")
                if is_curated
                else _flat_candidates(base, suffix, ".parquet")
            )
            for path in parquet_candidates:
                if path.exists():
                    return pd.read_parquet(path)

    raise FileNotFoundError(
        f"Features not found for {symbol} {timeframe}. Tried versions {versions_to_try}"
    )
