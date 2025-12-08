# Genesis-Core Stabilization Plan: The 9 Steps

**Objective**: Fix the pipeline in a deterministic system. Make Genesis repeatable, stable, and predictable.

## ⭐ STEP 1 — Frozen Data Sources

**Problem**: Fetching data dynamically causes inconsistency.
**Action**: Create immutable snapshots.

- [ ] Create `data/raw/BTCUSD_1m_2020-2025.parquet` (and ETHUSD).
- [ ] Ensure ALL pipelines (Optuna, Backtest, Live) use these exact files.
- [ ] Remove all API calls from the data loading pipeline.

## ⭐ STEP 2 — Fix Seeds Globally

**Problem**: Randomness varies between runs.
**Action**: Set seeds in all libraries.

- [ ] Implement global seeding for `numpy`, `random`, `torch`.
- [ ] Enforce `optuna.samplers.TPESampler(seed=42)`.

## ⭐ STEP 3 — Eliminate "Hidden State"

**Problem**: Results depend on execution order or previous runs.
**Action**: Identify and remove state leakage.

- [ ] Audit for global variables.
- [ ] Ensure caches are cleared between runs.
- [ ] Verify no signal values depend on previous runs.

## ⭐ STEP 4 — Full Isolation

**Problem**: Shared memory/instances cause side effects.
**Action**: Isolate execution contexts.

- [ ] Instantiate new objects for every trial/backtest.
- [ ] Ideally: Run each trial in a separate process (multiprocessing).

## ⭐ STEP 5 — Pure Functions

**Problem**: In-place mutation makes data flow unpredictable.
**Action**: Refactor to pure functions.

- [ ] Replace `df['col'] = ...` with `df.assign()` or new dataframe creation where appropriate in critical paths.
- [ ] Ensure inputs are never modified.

## ⭐ STEP 6 — Freeze Requirements

**Problem**: Dependency updates break reproducibility.
**Action**: Lock environment.

- [ ] Run `pip freeze > requirements.txt`.
- [ ] Enforce usage of this exact environment.

## ⭐ STEP 7 — Static Configuration

**Problem**: Configs injected from env/CLI/random sources are hard to track.
**Action**: Centralize configuration.

- [ ] Create static config files (`config/strategy.yaml`, `config/backtest.yaml`, `config/optuna.yaml`).
- [ ] Disable runtime overrides that aren't explicitly tracked.

## ⭐ STEP 8 — Comprehensive Logging

**Problem**: Cannot trace back _why_ a result happened.
**Action**: Log metadata for every run.

- [ ] Log: Timestamp, Git Commit Hash, Config Hash, Dataset Version, Seed, Result.

## ⭐ STEP 9 — Single Pipeline

**Problem**: Divergent scripts (`runner.py` vs `run_backtest.py`) behave differently.
**Action**: Unify execution.

- [ ] Create `pipeline.py` as the single entry point.
- [ ] Modes: `--mode backtest`, `--mode optuna`, `--mode live`.
- [ ] Ensure they share the EXACT same loading and execution logic.
