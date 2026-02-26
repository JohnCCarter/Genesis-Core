import sys
from pathlib import Path

import pandas as pd

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from core.indicators.htf_fibonacci import get_htf_fibonacci_context, load_candles_data


def debug_loading():
    symbol = "tBTCUSD"
    timeframe = "1h"
    htf_timeframe = "1D"

    print(f"Testing HTF Loading for {symbol} {htf_timeframe}...")

    # 1. Test direct loading
    try:
        df = load_candles_data(symbol, htf_timeframe)
        print(
            f"[OK] Loaded {len(df)} 1D candles. Range: {df['timestamp'].min()} to {df['timestamp'].max()}"
        )
        print("Sample 1D rows:")
        print(df.tail(3))
    except Exception as e:
        print(f"[FAIL] load_candles_data: {e}")
        return

    # 2. Test get_htf_fibonacci_context with a dummy LTF bar
    # Use a timestamp that should exist in the data
    test_ts = pd.Timestamp("2024-12-20 11:00:00")
    dummy_ltf = {"timestamp": [test_ts], "close": [90000.0]}

    print(f"\nTesting context for {test_ts}...")
    ctx = get_htf_fibonacci_context(
        dummy_ltf, timeframe=timeframe, symbol=symbol, htf_timeframe=htf_timeframe
    )
    print("Context result:", ctx)


if __name__ == "__main__":
    debug_loading()
