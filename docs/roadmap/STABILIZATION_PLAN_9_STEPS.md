# Genesis-Core Stabilization Plan: The 9 Steps

**Objective**: Fix the pipeline in a deterministic system. Make Genesis repeatable, stable, and predictable.

## ⭐ STEP 1 — Frozen Data Sources

**Problem**: Fetching data dynamically causes inconsistency.
**Action**: Create immutable snapshots.

- [x] Create `data/raw/tBTCUSD_1h_frozen.parquet` and `data/raw/tBTCUSD_1m_frozen.parquet`.
- [x] Ensure ALL pipelines (Optuna, Backtest, Live) use these exact files.
- [x] Remove all API calls from the data loading pipeline.

## ⭐ STEP 2 — Fix Seeds Globally

**Problem**: Randomness varies between runs.
**Action**: Set seeds in all libraries.

- [x] Implement global seeding for `numpy`, `random`, `torch`.
- [x] Enforce `optuna.samplers.TPESampler(seed=42)`.

## ⭐ STEP 3 — Eliminate "Hidden State"

**Problem**: Results depend on execution order or previous runs.
**Action**: Identify and remove state leakage.

- [x] Audit for global variables.
- [x] Ensure caches are cleared between runs.
- [x] Verify no signal values depend on previous runs.

## ⭐ STEP 4 — Full Isolation

**Problem**: Shared memory/instances cause side effects.
**Action**: Isolate execution contexts.

- [x] Instantiate new objects for every trial/backtest (or reset state completely).
- [x] Ideally: Run each trial in a separate process (multiprocessing).

## ⭐ STEP 5 — Pure Functions

**Problem**: In-place mutation makes data flow unpredictable.
**Action**: Refactor to pure functions.

- [x] Replace `df['col'] = ...` with `df.assign()` or new dataframe creation where appropriate in critical paths.
- [x] Ensure inputs are never modified.

## ⭐ STEP 6 — Freeze Requirements

**Problem**: Dependency updates break reproducibility.
**Action**: Lock environment.

- [x] Run `pip freeze > requirements.lock`.
- [x] Enforce usage of this exact environment (Python 3.11.9).

## ⭐ STEP 7 — Static Configuration

**Problem**: Configs injected from env/CLI/random sources are hard to track.
**Action**: Centralize configuration.

- [x] Create static config files (`config/backtest_defaults.yaml`).
- [x] Update `run_backtest.py` to load defaults from static config.
- [x] Track/guard runtime overrides explicitly (canonical 1/1 by default; debug-only requires explicit marker).

## ⭐ STEP 8 — Comprehensive Logging

**Problem**: Cannot trace back _why_ a result happened.
**Action**: Log metadata for every run.

- [x] Log: Timestamp, Git Commit Hash, Seed, Result in `backtest_info`.
- [ ] Log: Config Hash, Dataset Version (explicitly) in backtest artifacts.

Notes (current state):

- `backtest_info.execution_mode` captures canonical vs explicit mode flags.
- Config hash/version is available via the runtime/config API, but is not yet embedded in every backtest JSON.

## ⭐ STEP 9 — Single Pipeline

**Problem**: Divergent scripts (`runner.py` vs `run_backtest.py`) behave differently.
**Action**: Unify execution.

- [x] Create `src/core/pipeline.py` as the unified entry point for shared setup.
- [ ] Modes: `--mode backtest`, `--mode optuna`, `--mode live` (nice-to-have).
- [x] Ensure backtest + optimizer share the same environment setup and engine creation defaults.
