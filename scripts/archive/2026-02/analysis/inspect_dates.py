"""Quickly inspect min/max timestamp for a curated candles parquet file.

This is a manual helper script.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


def _find_repo_root() -> Path:
    """Find repository root from current file location."""

    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").exists() and (parent / "src").exists():
            return parent
    return Path(__file__).resolve().parents[1]


def _bootstrap_repo_root_on_path() -> None:
    """Allow running the script from arbitrary working directories."""

    repo_root = _find_repo_root()
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))


_bootstrap_repo_root_on_path()


def main() -> None:
    path = "data/curated/v1/candles/tBTCUSD_30m.parquet"
    try:
        df = pd.read_parquet(path)
        print(f"Start: {df['timestamp'].min()}")
        print(f"End:   {df['timestamp'].max()}")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
