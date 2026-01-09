#!/usr/bin/env python3
"""Quick inspection of candle data."""

import pandas as pd

df = pd.read_parquet("data/candles/tBTCUSD_1h.parquet")

print("=" * 80)
print("CANDLE DATA INSPECTION")
print("=" * 80)

print("\nFirst 10 candles:")
print(df[["timestamp", "open", "high", "low", "close", "volume"]].head(10))

print("\nLast 10 candles:")
print(df[["timestamp", "open", "high", "low", "close", "volume"]].tail(10))

print("\nPrice Statistics:")
print(f"  Min close: {df['close'].min()}")
print(f"  Max close: {df['close'].max()}")
print(f"  Mean close: {df['close'].mean():.2f}")
print(f"  Median close: {df['close'].median():.2f}")

print("\nData Types:")
print(df.dtypes)

print("\nSample close values (check decimals):")
for i in [0, 100, 1000, 5000, 10000, -1]:
    val = df["close"].iloc[i]
    print(f"  Index {i}: {val} (type: {type(val).__name__})")

print("\nVolume check:")
print(f"  Non-zero volume: {(df['volume'] > 0).sum()} / {len(df)}")
print(f"  Mean volume: {df['volume'].mean():.2f}")

print("=" * 80)
