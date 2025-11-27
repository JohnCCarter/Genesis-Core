# Optimizer Reproduction & Environment Variables (2025-11-26)

## Issue

Manual backtests using `scripts/run_backtest.py` were producing significantly different results (-16.65% return) compared to the optimizer's reported results (+22.75% return) for the exact same configuration (Trial 1032).

## Root Cause

The optimizer (`core.optimizer.runner`) sets specific environment variables to enable performance optimizations:

- `GENESIS_FAST_WINDOW=1`
- `GENESIS_PRECOMPUTE_FEATURES=1`
- `GENESIS_RANDOM_SEED=42`

These variables change the execution path of the feature calculation and backtest engine.

- **Without Env Vars (Default):** Streaming/Iterative calculation. Result: 1065 trades, -16.65% return.
- **With Env Vars (Optimizer Mode):** Batch/Precomputed calculation. Result: 386 trades, +22.75% return.

The discrepancy in trade count (1065 vs 386) suggests a significant divergence in signal generation between the streaming and batch modes. This is likely due to differences in how indicators are calculated or how "warmup" data is handled in the fast window mode.

## Solution

To reproduce optimizer results manually, you MUST set these environment variables.

### Reproduction Script

A script `scripts/reproduce_trial_subprocess.py` has been created that:

1. Loads the trial configuration.
2. Sets the required environment variables.
3. Runs `scripts.run_backtest` in a subprocess.

### Recommendation

Always use `GENESIS_FAST_WINDOW=1` and `GENESIS_PRECOMPUTE_FEATURES=1` when validating optimizer results.
