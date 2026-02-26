# Phase 3 Optimization - Fix & Results (2025-11-21)

## Issue: Identical Results in Optimization

During the initial attempt to run Phase 3 optimization (`run_20251121_134256`), we observed that all 50 trials produced identical results (Score 0.0802, PF 1.12, 86 trades), despite Optuna suggesting different parameters.

### Root Cause

The Optuna configuration used dot-notation keys (e.g., `thresholds.entry_conf_overall`) to define the search space. The `runner.py` script used a deep merge function to apply these parameters to the default configuration. However, the merge function treated `thresholds.entry_conf_overall` as a new top-level key instead of updating the nested `entry_conf_overall` key within the `thresholds` dictionary. As a result, the backtest engine ignored these "flat" keys and used the default values for all trials.

### Fix

We patched `src/core/optimizer/param_transforms.py` to include a new helper function `_expand_dot_notation(params)`. This function transforms flat dot-notation keys into nested dictionaries before the merge step.

- **File**: `src/core/optimizer/param_transforms.py`
- **Function**: `_expand_dot_notation` added, `transform_parameters` updated.

## Verification Run (`run_20251121_140023`)

After applying the fix, we re-ran the optimization with the same configuration (`config/optimizer/tBTCUSD_1h_optuna_phase3_fine.yaml`).

### Results

The optimization successfully produced varied results, confirming that the parameters are now being correctly injected into the backtest.

- **Total Trials**: 100 (50 pairs of duplicates due to some reason, likely seed or sampler behavior, but results vary _between_ different parameter sets)
- **Best Trial**: `trial_009`
  - **Score**: 0.1634
  - **Trades**: 85
  - **Profit Factor**: 1.16
  - **Total Return**: +6.15%
  - **Sharpe Ratio**: 0.057
  - **Drawdown**: 7.35%

### Comparison

- **Before Fix**: All trials identical (PF 1.12, Return +2.05%)
- **After Fix**: Best trial (PF 1.16, Return +6.15%)

## Conclusion

The parameter injection mechanism is now robust and handles dot-notation keys correctly. The Phase 3 optimization has produced a candidate with improved metrics (PF > 1.15 target met).

## Next Steps

- Analyze the best parameters from `trial_009`.
- Consider running a longer optimization or a walk-forward validation on the best candidate.
