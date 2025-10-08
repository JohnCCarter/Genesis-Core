"""
Benchmark Numba-compiled triple-barrier labeling vs pure Python.
"""

import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.ml.labeling import generate_adaptive_triple_barrier_labels
from core.ml.labeling_fast import generate_adaptive_triple_barrier_labels_fast


def main():
    print("\n" + "=" * 80)
    print("BENCHMARK: Numba Triple-Barrier vs Pure Python")
    print("=" * 80)

    # Load data
    symbol = "tBTCUSD"
    timeframe = "1h"
    candles_path = Path(f"data/candles/{symbol}_{timeframe}.parquet")

    if not candles_path.exists():
        print(f"[ERROR] Candles not found: {candles_path}")
        return

    df = pd.read_parquet(candles_path)
    closes = df["close"].tolist()
    highs = df["high"].tolist()
    lows = df["low"].tolist()

    print(f"[LOAD] {len(closes)} bars from {candles_path}")

    # Params
    k_profit = 1.0
    k_stop = 0.6
    max_holding = 36
    atr_period = 14

    print(f"[CONFIG] k_profit={k_profit}, k_stop={k_stop}, H={max_holding}, ATR={atr_period}")

    # Benchmark Pure Python
    print("\n[TEST 1/2] Pure Python implementation...")
    start = time.time()
    labels_python = generate_adaptive_triple_barrier_labels(
        closes, highs, lows, k_profit, k_stop, max_holding, atr_period
    )
    python_time = time.time() - start
    print(f"  Time: {python_time:.2f}s")
    print(
        f"  Labels: {len(labels_python)} (Profit: {labels_python.count(1)}, Loss: {labels_python.count(0)}, None: {labels_python.count(None)})"
    )

    # Benchmark Numba (first call includes JIT compilation)
    print("\n[TEST 2/2] Numba implementation (includes JIT compile on first call)...")
    start = time.time()
    labels_numba = generate_adaptive_triple_barrier_labels_fast(
        closes, highs, lows, k_profit, k_stop, max_holding, atr_period
    )
    numba_time_with_compile = time.time() - start
    print(f"  Time (with JIT compile): {numba_time_with_compile:.2f}s")

    # Benchmark Numba again (JIT already compiled)
    print("\n[TEST 3/3] Numba implementation (cached JIT)...")
    start = time.time()
    labels_numba2 = generate_adaptive_triple_barrier_labels_fast(
        closes, highs, lows, k_profit, k_stop, max_holding, atr_period
    )
    numba_time = time.time() - start
    print(f"  Time (cached): {numba_time:.2f}s")
    print(
        f"  Labels: {len(labels_numba2)} (Profit: {labels_numba2.count(1)}, Loss: {labels_numba2.count(0)}, None: {labels_numba2.count(None)})"
    )

    # Verify correctness
    if labels_python == labels_numba:
        print("\n[OK] Numba results MATCH pure Python (correctness verified)")
    else:
        print("\n[WARN] Results differ - checking details...")
        diff_count = sum(
            1 for i in range(len(labels_python)) if labels_python[i] != labels_numba[i]
        )
        print(f"  Differences: {diff_count}/{len(labels_python)} labels")

    # Speedup
    if python_time > 0:
        speedup = python_time / numba_time
        print("\n" + "=" * 80)
        print("RESULTS")
        print("=" * 80)
        print(f"Pure Python: {python_time:.2f}s")
        print(f"Numba (cached): {numba_time:.2f}s")
        print(f"Speedup: {speedup:.1f}x faster!")
        print(
            f"\nFor 27-config sweep: {python_time * 27:.0f}s -> {numba_time * 27:.0f}s (saves {(python_time - numba_time) * 27:.0f}s)"
        )
        print("=" * 80)


if __name__ == "__main__":
    main()
