# Regime Intelligence Phase B/C Re-run Plan (2026-03-13)

Mode: `RESEARCH`
Branch: `feature/Regime-Intelligence`

## Why this plan exists

The runtime and test evidence indicate that Regime Intelligence (RI) is already
implemented and behaving correctly behind explicit ON/OFF gating. The remaining
uncertainty is not primarily code completeness, but evidence completeness:

- old `Phase B v2` narrative is partially invalid because two config-key bugs
  caused `clarity_score.weights` and `size_multiplier` to be ignored
- corrected post-fix artifacts already exist:
  - `config/optimizer/phased_v3_best_trials/phaseB_v3_best_trial.json`
  - `config/optimizer/phased_v3_best_trials/phaseC_oos_trial.json`
- the corresponding `Phase B v3` study DB is not currently present in
  `results/hparam_search/storage/`

This plan defines when a re-run is necessary and how to execute it cleanly.

## Current evidence status

### Execution update (completed 2026-03-13)

The recommended rerun has now been executed from `feature/Regime-Intelligence`.

- Focused RI baseline tests passed before rerun
- Fresh Phase B run completed in `results/hparam_search/ri_phaseB_rerun_20260313/`
- Fresh Phase B study DB now exists at
  `results/hparam_search/storage/phased_v3_phaseB_v2_3h.db`
- Phase B again selected **`trial_082`** with score **`0.3336954196`**
- Fresh Phase C OOS rerun completed in
  `results/hparam_search/ri_phaseC_rerun_20260313/`
- Fresh Phase C rerun DB now exists at
  `results/hparam_search/storage/phased_v3_phaseC_rerun_20260313.db`
- Phase C rerun produced score **`0.1612487234`**

Result: the earlier evidence gap is now closed for branch-local reproducibility.

### Baseline without RI

- `Phase A` = baseline without RI
- Artifact: `config/optimizer/phased_v3_best_trials/phaseA_best_trial.json`

### RI enabled, corrected path

- `Phase B v3` = corrected RI best-trial artifact
- `Phase C` = corrected OOS artifact for Phase B v3 best params

### Runtime / test proof already available

Targeted proof points currently available in the repository:

- `tests/utils/test_decision.py::test_clarity_score_v2_off_preserves_legacy_path`
- `tests/utils/test_decision.py::test_clarity_score_v2_on_round_policy_tie_half_even_deterministic`
- `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_legacy_parity_cases`
- `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic`
- `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_ri_v2_clarity_on_changes_sizing_only_and_logs`
- `tests/utils/test_risk_state_engine.py`
- `tests/utils/test_risk_state_multiplier.py`

## Decision rule

### No re-run needed yet if the goal is

- summarize current RI status
- compare Phase A vs corrected RI artifacts
- continue with docs / merge-readiness analysis

### Re-run needed if the goal is

- full study-level reproducibility
- regenerate the missing Phase B v3 study DB
- produce fresh branch-local evidence from the current tip
- verify that no later refactor changed the optimization outcome materially

## Recommended execution order

### Step 1 — Baseline verification

Run the focused RI baseline tests:

- decision OFF/ON parity
- authority-mode deterministic path
- risk_state tests

### Step 2 — Re-run Phase B from current branch

Use:

- `config/optimizer/tBTCUSD_3h_phased_v3_phaseB.yaml`

Expected outcome:

- fresh study DB under `results/hparam_search/storage/`
- fresh best trial result and config payload
- ability to compare new best trial against stored `phaseB_v3_best_trial.json`

### Step 3 — Freeze the best post-fix Phase B artifact

If the re-run reproduces or improves the existing artifact:

- update `config/optimizer/phased_v3_best_trials/phaseB_v3_best_trial.json`
  only if new result is intentionally accepted as canonical
- otherwise keep existing artifact and document parity

### Step 4 — Re-run Phase C OOS from current branch

Use:

- `config/optimizer/tBTCUSD_3h_phased_v3_phaseC.yaml`

Expected outcome:

- fresh OOS result using the corrected RI best parameters
- direct comparison with `phaseC_oos_trial.json`

### Step 5 — Write explicit comparison summary

Produce one short summary containing:

- Phase A baseline (no RI)
- Phase B v3 corrected IS
- Phase C corrected OOS
- optional note about Phase D/E being RI + risk_state, not RI alone

## Suggested acceptance questions

Before calling RI "done", answer these explicitly:

1. Does corrected Phase B still materially beat Phase A in-sample?
2. Does corrected Phase C still materially beat Phase A out-of-sample?
3. Are OFF-path parity tests still green on current branch?
4. Do we have enough artifact continuity to merge without a fresh re-run?
5. If not, do we want canonical fresh artifacts on `feature/Regime-Intelligence`?

## Recommended next action

Default next step: use the fresh rerun evidence for merge-readiness analysis.

Suggested follow-through:

1. decide whether to promote any rerun outputs into canonical tracked artifacts,
2. summarize Phase A vs fresh Phase B/C evidence in the PR or handoff, and
3. keep Phase D/E clearly labeled as RI + risk_state, not RI alone.
