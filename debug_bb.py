"""Debug BB position calculation."""
import pandas as pd
import sys
sys.path.insert(0, 'src')

from core.indicators.bollinger import bollinger_bands
from core.indicators.vectorized import calculate_bb_position_vectorized

df = pd.read_parquet('data/candles/tBTCUSD_1h.parquet').iloc[:100]
closes = df['close'].tolist()

# Per-sample
bb_ps = bollinger_bands(closes, period=20, std_dev=2.0)

# Vectorized
bb_vec = calculate_bb_position_vectorized(df['close'], period=20, std_dev=2.0)

print("BB POSITION COMPARISON:")
print(f"\nLast 5 values:")
for i in range(-5, 0):
    ps_val = bb_ps['position'][i]
    vec_val = bb_vec.iloc[i]
    diff = abs(ps_val - vec_val)
    print(f"  Bar {100+i}: ps={ps_val:.6f}, vec={vec_val:.6f}, diff={diff:.6f}")

# Check inversion and MA3
print(f"\nINVERSION & MA3 (bar 99):")
ps_last_3 = bb_ps['position'][-3:]
ps_inv_last_3 = [1.0 - pos for pos in ps_last_3]
ps_inv_ma3 = sum(ps_inv_last_3) / 3.0

print(f"  Per-sample last 3 positions: {ps_last_3}")
print(f"  Per-sample inverted: {ps_inv_last_3}")
print(f"  Per-sample inv_ma3: {ps_inv_ma3:.6f}")

vec_inv = 1.0 - bb_vec
vec_inv_ma3 = vec_inv.rolling(3).mean().iloc[-1]
print(f"  Vectorized inv_ma3: {vec_inv_ma3:.6f}")
print(f"  Diff: {abs(ps_inv_ma3 - vec_inv_ma3):.6f}")

