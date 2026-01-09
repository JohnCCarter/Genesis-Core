"""Quickly inspect min/max timestamp for a curated candles parquet file.

This is a manual helper script.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


def _bootstrap_repo_root_on_path() -> None:
    """Allow running the script from arbitrary working directories."""

    repo_root = Path(__file__).resolve().parents[1]
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
