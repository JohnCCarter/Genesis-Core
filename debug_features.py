import pandas as pd
import sys
sys.path.insert(0, 'src')

from core.strategy.features_asof import extract_features_backtest
from core.indicators.vectorized import calculate_all_features_vectorized

df = pd.read_parquet('data/candles/tBTCUSD_1h.parquet')

candles = {
    'open': df['open'].iloc[:100].tolist(),
    'high': df['high'].iloc[:100].tolist(),
    'low': df['low'].iloc[:100].tolist(),
    'close': df['close'].iloc[:100].tolist(),
    'volume': df['volume'].iloc[:100].tolist()
}

# Use AS-OF semantik: features AS OF bar 99 (uses bars 0-99 inclusive)
feats_ps, meta = extract_features_backtest(candles, asof_bar=99)
print(f"[META] asof_bar={meta['asof_bar']}, uses_bars={meta['uses_bars']}")

feats_vec = calculate_all_features_vectorized(df.iloc[:100])

print('PER-SAMPLE (bar 99):')
for k, v in sorted(feats_ps.items()):
    print(f'  {k:30s} {v:+.6f}')

print('\nVECTORIZED (bar 99):')
for k, v in sorted(feats_vec.iloc[-1].to_dict().items()):
    print(f'  {k:30s} {v:+.6f}')

print('\nDIFFERENCES:')
for k in sorted(feats_ps.keys()):
    diff = abs(feats_ps[k] - feats_vec.iloc[-1][k])
    status = 'OK' if diff < 0.001 else 'DIFF'
    print(f'  {k:30s} {status:5s} diff={diff:.6f}')

