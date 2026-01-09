# Zero Trades Fix - 2025-12-03

## Issue

Optimization run `optuna_phase3_fine_12m_v5` (Config v2/v3) resulted in 97% zero-trade trials.
Diagnosis showed that while `entry_conf_overall` was lowered (0.20-0.30), the **HTF Fibonacci Gate** remained strict and blocked all trades.
Specifically:

- `htf_fib.entry.tolerance_atr` was too tight (1.0-1.5) for the market conditions.
- `ltf_override_threshold` was too high (0.55-0.75) compared to the lowered entry confidence (0.20), making overrides impossible.

## Solution (Config v4)

Created `config/optimizer/tBTCUSD_1h_optuna_phase3_fine_v4.yaml` with the following changes:

1.  **Lowered LTF Override Threshold**: Reduced to `0.30 - 0.55` (was 0.55-0.75) to allow strong model signals to override HTF blocks.
2.  **Widened HTF Tolerance**: Increased `htf_fib.entry.tolerance_atr` to `2.0 - 8.0` (was 1.0-5.0).
3.  **Optional HTF Gate**: Added `htf_fib.entry.enabled` as a grid parameter `[true, false]` to allow the optimizer to disable the gate if it's detrimental.

## Results

- **Trial 0 (v4)**: Produced **1043 trades** (vs 0 previously).
- **Performance**: Initial random trial had negative return (-17%, PF 0.75), but this confirms the blocking issue is resolved. Optuna can now optimize for profitability.

## Next Steps

- Monitor `optuna_phase3_fine_12m_v7` for convergence.
- Expect Profit Factor to improve as TPE learns which filters (HTF enabled vs disabled, tolerance levels) work best.
