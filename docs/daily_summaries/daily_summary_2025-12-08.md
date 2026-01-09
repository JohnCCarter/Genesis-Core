# Daily Summary - 2025-12-08

## 🚨 The Reproducibility Crisis

Today's session focused on a critical discrepancy between the Optimizer's reported results and manual backtest verification.

### The Discrepancy

- **Optimizer (Trial 005)**: Score **0.4264**, Return **+5.44%**, Trades **2382**.
- **Manual Verification**: Score **0.1949**, Return **+0.98%**, Trades **386**.

### Investigation Steps

1.  **Located High Score**: Found Trial 005 in `results/hparam_search/run_20251208_111723/best_trial.json`.
2.  **Extracted Config**: Created `config/strategy/candidates/tBTCUSD_1h_score_042_20251208.json`.
3.  **Schema Fixes**: The extracted config had `regime_proba` as floats (e.g., `0.5`), but the schema expects `dict[str, float]`. Manually expanded these to `{ "trend": 0.5, "range": 0.5, ... }` to pass validation.
4.  **Verification Script**: Created `scripts/verify_candidate_exact.py` to bypass the CLI argument parser and inject the config directly into `BacktestEngine`, mimicking `runner.py`.
5.  **Result**: The verification script ran successfully but produced the lower score (0.19), confirming the discrepancy is reproducible outside the optimizer but indicating a fundamental difference in execution environment or state.

### Root Cause Hypotheses

1.  **Hidden State**: The optimizer might be leaking state between trials (e.g., global variables in `core.indicators` or `core.strategy`).
2.  **Data Mutation**: The dataset might be modified in-place during the optimization run.
3.  **Config Merging**: `runner.py` might be merging the trial config differently than `BacktestEngine`'s internal merge logic.
4.  **Seed/Randomness**: Despite setting seeds, some component might be using a non-seeded random generator.

## 🛑 Strategic Pivot: The 9-Step Stabilization Plan

Instead of patching individual bugs, we are moving to a "Lock Down" strategy to ensure absolute reproducibility.

### The 9-Step Plan (To Be Implemented)

1.  **Frozen Data Sources**: Snapshot data (parquet), no API calls in pipeline.
2.  **Fix Seeds Globally**: `numpy`, `random`, `torch`, `optuna`.
3.  **Eliminate Hidden State**: No global state, clear caches, no side effects.
4.  **Isolation**: Separate process for each run.
5.  **Pure Functions**: No inplace mutation.
6.  **Freeze Requirements**: `pip freeze`.
7.  **Static Config**: No environment/CLI overrides mixed in randomly.
8.  **Logging**: Timestamp, commit hash, config hash, seed, results.
9.  **Single Pipeline**: One code path (`pipeline.py`) for backtest/optuna/live.

## Next Steps

- Implement the 9-Step Plan starting with **Step 1: Frozen Data Sources**.
- Create `docs/roadmap/STABILIZATION_PLAN_9_STEPS.md` to track progress.
