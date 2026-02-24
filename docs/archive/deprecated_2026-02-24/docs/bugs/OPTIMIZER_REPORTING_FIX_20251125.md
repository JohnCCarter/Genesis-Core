# Optimization Reporting Bug Fix (2025-11-25)

## Issue

Optimization trials (e.g., Trial 13 in `run_20251125_092436`) were reported as having exactly **5 trades**, despite the logs showing successful execution with hundreds of trades (e.g., 548 trades).

## Root Cause Analysis

1. **Regex Failure**: The `runner.py` script used a regex `^\s*results:\s*(.*\.json)\s*$` to parse the result file path from the backtest log.
2. **Log Format Mismatch**: The actual log output from `trade_logger.py` is `[SAVED] Results: path/to/file.json`. The regex failed because:
   - It expected the line to start with `results:` (ignoring the `[SAVED]` prefix).
   - It was case-sensitive (`results` vs `Results`).
3. **Fallback Trap**: When the regex failed, the runner fell back to selecting the last file in the `results/backtests` directory using `sorted(glob(...))[-1]`.
4. **The Trap File**: A dummy file named `tBTCUSD_1h_diffcache_2.json` existed in the directory. This file contained exactly 5 trades.
5. **Sorting Order**: Alphabetically, `tBTCUSD_1h_diffcache_2.json` sorts _after_ the timestamped files (e.g., `tBTCUSD_1h_20251125_...`) because `d` > `2`.
6. **Result**: The runner consistently picked up the dummy file for every trial where the regex failed, reporting 5 trades for all of them.

## Fix Implemented

1. **Deleted Trap File**: Removed `results/backtests/tBTCUSD_1h_diffcache_2.json`.
2. **Updated Regex**: Modified `src/core/optimizer/runner.py` to use a robust regex:
   ```python
   match = re.search(r"(?:\[SAVED\]\s*)?Results:\s*(.*\.json)\s*$", log_content, re.MULTILINE | re.IGNORECASE)
   ```

## Verification

- The log file `trial_013.log` confirms 548 trades.
- The corresponding JSON file `tBTCUSD_1h_20251125_102811.json` confirms 548 trades.
- Future runs will correctly parse the path from the log and avoid the fallback logic.
