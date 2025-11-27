# Performance Improvements (2025-11-25)

## Overview

Optimized feature extraction in `features_asof.py` and `engine.py` to reduce overhead during backtesting.

## Changes

### 1. Precomputed Derived Features

Added precomputation for `volatility_shift` and `ema_slope` in `BacktestEngine`.

- **Before**: Calculated on-the-fly for every bar using full history (O(N^2) cumulative).
- **After**: Calculated once at start using vectorized NumPy operations (O(N)).

### 2. Fast Path Feature Extraction

Modified `features_asof.py` to use direct indexing or minimal slicing when precomputed features are available.

- **RSI**: Direct access `pre_rsi[asof_bar]` instead of slicing `pre_rsi[:asof_bar+1]`.
- **Bollinger Bands**: Slice only last 3 values instead of full history.
- **Volatility Shift**: Slice only last 3 values instead of full history.
- **ADX**: Direct access.
- **EMA Slope**: Direct access.
- **ATR**: Slice only last 56 values (for percentiles) instead of full history.

### 3. Optimized Swing Filtering

Used `bisect` module to filter precomputed swings.

- **Before**: List comprehension iterating over all swings for every bar (O(M) per bar).
- **After**: `bisect_right` to find cut-off index (O(log M) per bar).

## Impact

- Reduces memory allocation (fewer list copies).
- Reduces CPU usage (fewer redundant calculations).
- Should significantly improve backtest speed for large datasets.
