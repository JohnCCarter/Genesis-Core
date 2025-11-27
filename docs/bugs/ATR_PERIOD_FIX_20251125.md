# ATR Period Mismatch Fix (2025-11-25)

## Problem

The strategy `tBTCUSD_1h` was configured with `"atr_period": 28`, but the backtest produced only 1 trade (or very few) and lost money.
Diagnosis revealed that `LTF_FIB_BLOCK` was rejecting trades.
Further investigation showed that the codebase (`features_asof.py` and `engine.py`) was hardcoded to use `atr_14` (period 14), ignoring the configuration.
This caused the volatility tolerance (calculated as `tolerance_atr * atr`) to be based on the wrong ATR value, leading to incorrect gating decisions.

## Solution

1.  **Refactored `src/core/strategy/features_asof.py`**:

    - Added logic to extract `atr_period` from the configuration.
    - Updated `_extract_asof` to use the configured period for ATR calculation and caching.
    - Fixed a potential bug where `atr_vals` could be undefined in the fast path.

2.  **Refactored `src/core/backtest/engine.py`**:
    - Updated `_prepare_numpy_arrays` to check the configuration for `atr_period`.
    - Added logic to precompute the custom ATR period if it differs from the standard (14/50).
    - Updated the cache loading logic to calculate the custom ATR if it's missing from the cache.

## Verification

- Ran backtest with `tBTCUSD_1h.json` (ATR 28).
- **Before**: 1 trade, negative return.
- **After**: 978 trades, +0.75% return, PF 1.01.
- The strategy is now correctly executing trades based on the configured volatility parameters.

## Next Steps

- The current performance (PF 1.01) indicates the strategy is break-even.
- Now that the technical bug is fixed, parameter optimization (Optuna) can be resumed to improve the Profit Factor.
- The `long_max_level` in the champion config is `0.2`, which is very tight. It might need to be relaxed or optimized.
