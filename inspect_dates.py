import pandas as pd

p = "data/curated/v1/candles/tBTCUSD_30m.parquet"
try:
    df = pd.read_parquet(p)
    print(f"Start: {df['timestamp'].min()}")
    print(f"End:   {df['timestamp'].max()}")
except Exception as e:
    print(e)
