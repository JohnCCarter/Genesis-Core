# Daily Summary - 2025-11-25

## Overview

Today's focus was on executing the "Phase 3 Wide" optimization to explore a broader parameter space. The initial attempt failed due to technical and strategic issues, which were diagnosed and resolved. A second run is now active.

## Key Events

### 1. Phase 3 Wide Failure (Run `run_20251125_082700`)

- **Status**: Crashed at trial 177.
- **Technical Cause**: `sqlite3.OperationalError: disk I/O error` due to high concurrency (4 workers) on a file-based DB.
- **Strategic Cause**: Zero valid trials. All 177 trials failed the `min_trades: 30` constraint.
- **Diagnosis**: The Fibonacci gating logic (`LTF_FIB_BLOCK`) was too restrictive. Fixed levels (`long_max_level=0.786`) combined with insufficient tolerance blocked almost all trades, especially in strong trends/breakouts.

### 2. Remediation & Fixes

- **Configuration Update**: Modified `tBTCUSD_1h_optuna_phase3_wide.yaml`.
  - Added `long_max_level` and `short_min_level` to the optimization search space (allowing values > 1.0 and < 0.0 for breakouts).
  - Increased `tolerance_atr` range from [0.2, 1.1] to [0.5, 3.0].
  - Reduced `max_concurrent` to 2 to prevent SQLite crashes.
- **Documentation**: Created `docs/optimization/PHASE3_WIDE_FAIL_ANALYSIS_20251125.md`.

### 3. Phase 3 Wide v2 (Run `run_20251125_090251`)

- **Status**: In Progress.
- **Early Results**: Trial 001 log shows healthy trade activity (`ENTRY` events) and no `LTF_FIB_BLOCK` rejections, confirming the fix.
- **Parameters**: Trial 001 selected `tolerance_atr=3.0` and `short_min_level=-0.05`, validating the need for wider bounds.

### 4. Phase 3 Wide v3 (Run `run_20251125_100252` approx)

- **Status**: Started.
- **Reason**: Discovered that `max_hold_bars` was ignored in `BacktestEngine`, causing low trade counts in v2 (trades were held indefinitely).
- **Fix**: Patched `src/core/backtest/engine.py` to enforce `max_hold_bars` in `_check_traditional_exit_conditions`.
- **Expectation**: Trade counts should increase significantly (e.g. > 30 trades/year).

### 5. Commission Fee Update & Restart (Run `run_20251125_114800` approx)

- **Status**: Started (Resumed study `optuna_phase3_wide_v6`).
- **Change**: Updated default commission rate from 0.1% to 0.2% (Taker fee) in `BacktestEngine`, `PositionTracker`, and `run_backtest.py`.
- **Reason**: To ensure backtest results are realistic and robust against actual exchange fees (Bitfinex Taker = 0.2%).
- **Impact**: Total round-trip cost is now ~0.50% (0.2% entry + 0.2% exit + 0.05% slippage \* 2). This will lower scores slightly but increase confidence in profitability.
- **Action**: Restarted the optimization process with `resume: true` to continue the study with the new cost structure.

### 6. Critical Bug Fixes & Parity Verification

- **ATR Period Fix**: Discovered that `features_asof.py` and `engine.py` were ignoring the configured `atr_period` (e.g., 28) and hardcoding it to 14. This caused `LTF_FIB_BLOCK` to reject valid trades due to incorrect volatility calculations. Fixed and verified (trades increased from 1 to 978 in test case).
- **Optimizer Reporting Fix**: Fixed a regex bug in `runner.py` that caused the optimizer to report exactly 5 trades for every trial (fallback to a dummy file). It now correctly parses the backtest output.
- **Parity Test Success**: Confirmed mathematical parity between the Optuna pipeline and manual backtest. Initial discrepancy (-0.85% vs +0.46%) was resolved by aligning `warmup_bars` (150 vs 120). Both engines now produce identical trade counts (386) and returns (-0.85%) when configured identically.

### 7. Clean Slate (Phase 3 Wide v7)

- **Action**: Archived all previous runs from today (`run_20251125_*`) and their databases to `results/hparam_search/_archive/20251125_buggy_runs/` to prevent contamination from the ATR/MaxHold/Commission bugs.
- **New Config**: Created `config/optimizer/tBTCUSD_1h_optuna_phase3_wide_v7.yaml` with:
  - `warmup_bars: 150` (Parity aligned).
  - `commission: 0.2%` (Realistic).
  - `atr_period` range 6-40 (Correctly used).
  - `max_hold_bars` range 12-96 (Correctly enforced).
- **Status**: Ready to launch the definitive Phase 3 Wide exploration.

## Next Steps

1. Launch `run_phase3_wide_v7` (200 trials).
2. Monitor for valid trades and diversity in the first 50 bootstrap trials.
3. Analyze results for non-linear relationships in the widened search space.
