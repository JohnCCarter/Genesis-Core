# Performance Optimization Report - 2025-11-26

## Summary

This update focuses on improving the backtest engine performance to enable faster hyperparameter optimization.

## Key Changes

### 1. Vectorization of Indicators

- **ADX, RSI, ATR**: Rewrote these indicators to use NumPy vectorization instead of Python loops.
- **Impact**: Significant speedup for indicator calculation (O(1) vs O(N) overhead).
- **Verification**: `src/core/indicators/adx.py` is now fully vectorized.

### 2. Optuna Pruning Integration

- **Feature**: `BacktestEngine` now accepts a `pruning_callback`.
- **Mechanism**: Every 100 bars, the engine reports the current ROI to Optuna. If Optuna decides the trial is unpromising (e.g., worse than median), it raises `TrialPruned`.
- **Benefit**: Bad trials are stopped early, saving compute time.
- **Implementation**:
  - `src/core/backtest/engine.py`: Added callback logic.
  - `scripts/run_backtest.py`: Added Optuna integration.
  - `src/core/optimizer/runner.py`: Added pruning support for both Subprocess and In-Process modes.

### 3. In-Process Execution (Experimental)

- **Concept**: Run backtests in the same process (using threads) to share memory and avoid data reloading overhead.
- **Implementation**: `GENESIS_IN_PROCESS=1` environment variable triggers this mode.
- **Findings (Windows)**:
  - **Status**: **NOT RECOMMENDED** on Windows.
  - **Reason**: The Python Global Interpreter Lock (GIL) causes severe contention when running CPU-bound backtests in threads.
  - **Benchmark**: In-Process mode was ~12x slower than Subprocess mode (939s vs 96s for 5 trials).
  - **Recommendation**: Use Subprocess mode (`GENESIS_IN_PROCESS=0`) which uses `ProcessPoolExecutor` to utilize multiple CPU cores effectively.

### 4. Bug Fixes

- **PositionTracker**: Fixed `AttributeError: 'PositionTracker' object has no attribute 'current_capital'` by adding `current_equity` property and updating `engine.py`.
- **Runner**: Fixed scope issues in `runner.py` for In-Process execution.

## Usage

To run optimization with maximum performance:

```powershell
$Env:GENESIS_FAST_WINDOW='1'
$Env:GENESIS_PRECOMPUTE_FEATURES='1'
$Env:GENESIS_IN_PROCESS='0'  # Keep 0 on Windows
$Env:GENESIS_MAX_CONCURRENT='4' # Adjust to CPU cores
python -m core.optimizer.runner config/optimizer/your_config.yaml
```
