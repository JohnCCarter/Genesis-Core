#!/usr/bin/env python3
"""Debug script to inspect HTF levels structure."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd

from core.indicators.htf_fibonacci import get_htf_fibonacci_context

# Load 6h candles
candles_path = Path("data/curated/v1/candles/tBTCUSD_6h.parquet")
df = pd.read_parquet(candles_path)

# Convert to dict format
candles_dict = {
    "open": df["open"].tolist(),
    "high": df["high"].tolist(),
    "low": df["low"].tolist(),
    "close": df["close"].tolist(),
    "volume": df["volume"].tolist(),
}

# Get HTF context
htf_ctx = get_htf_fibonacci_context(
    candles_dict, timeframe="6h", symbol="tBTCUSD", htf_timeframe="1D"
)

print("HTF Context Keys:", htf_ctx.keys())
print("\nHTF Context:")
for key, value in htf_ctx.items():
    print(f"  {key}: {type(value).__name__} = {value}")

if "levels" in htf_ctx:
    print("\nLevels Detail:")
    levels = htf_ctx["levels"]
    print(f"  Type: {type(levels)}")
    for key, value in levels.items():
        print(f"    {key}: {type(value).__name__} = {value}")
