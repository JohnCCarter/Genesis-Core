# Phase 3 Fine Tuning Log

**Run ID:** `optuna_phase3_fine_12m_v4`
**Start Date:** 2025-12-03
**Configuration:** `config/optimizer/tBTCUSD_1h_optuna_phase3_fine_v2.yaml`
**Target:** PF > 1.20

## Timeline

### 2025-12-03 10:45 - Launch

- Started optimization with `max_concurrent: 1` and `n_startup_trials: 50`.
- Engine: Vectorized Fibonacci.

### 2025-12-03 11:00 - Interruption & Restart

- **Event:** Trial 69 failed with `KeyboardInterrupt` (likely due to resource contention or manual interference during monitoring).
- **Action:** Restarted with `resume: true`.
- **Observation:** Trial 4 (from previous session) remains the best with Score 0.1507 (PF 1.02). Many trials are hitting constraints (Score -250.2) or zero-trade penalties (Score -650.0).

### 2025-12-03 11:05 - Config Refinement

- **Action:** Updated `config/optimizer/tBTCUSD_1h_optuna_phase3_fine_v2.yaml` to explicitly include `htf_exit_config` with fixed values derived from the Champion.
- **Reason:** To suppress preflight warnings and ensure parity with the Champion strategy logic.

### 2025-12-03 11:06 - Second Restart

- **Event:** Trial 75 failed with `KeyboardInterrupt` during monitoring attempt.
- **Action:** Restarted again.
- **Status:** Running stable. Monitoring via `analyze_optuna_db.py` is paused to prevent interference.

## Observations

- **Performance:** Throughput is consistent at ~240 bars/sec.
- **Search Space:** The optimizer is exploring the space, but many configurations are failing constraints. This is expected in the early Random Sampling phase.
- **Best Result (so far):** Trial 4 (PF 1.02).

## Next Steps

1. Allow the optimization to complete at least 50-100 trials.
2. Analyze the distribution of scores to see if the search space needs adjustment.
3. If PF > 1.20 is achieved, validate the best trial with a full backtest.
- **Crash 3 (Trial 144)**: Occurred at 2025-12-03 11:07. Cause: KeyboardInterrupt during SQLite commit while running nalyze_optuna_db.py. Confirmed resource contention/locking issue when monitoring active DB.
- **Action**: Restarted optimization (Run ID: optuna_phase3_fine_12m_v4).
- **Recommendation**: Do NOT run nalyze_optuna_db.py while the optimizer is active. Wait for completion or use a copy of the DB.
- **Observation (2025-12-03)**: Detected that the optimization is running on the full dataset (2023-11-30 to 2025-11-19) instead of the configured 2024 slice. Cause: unner.py bug in _run_backtest_direct ignoring start_date/end_date.
- **Fix**: Patched src/core/optimizer/runner.py to pass dates to BacktestEngine and include them in the cache key. Requires restart to take effect.
- **Action (2025-12-03)**: Killing and restarting optimization process to apply date range fix. Run ID optuna_phase3_fine_12m_v4 will resume with correct 2024 data slice.
- **Config Update (2025-12-03 11:25)**: Widened search space to address zero-trade issue. entry_conf_overall low lowered to 0.20. htf_fib and ltf_fib tolerance_atr widened to 1.0-5.0 ATR. Restarting optimization.
- **Study Reset (2025-12-03 11:35)**: Created new study optuna_phase3_fine_12m_v5 to resolve RandomSampler fallback warnings caused by dynamic search space changes. Resuming optimization with clean state.
