# tBTCUSD 3h candidate recommendation

Date: 2026-03-18
Branch: `feature/ri-optuna-train-validate-blind-v1`
Scope: analytical recommendation only; no champion/default/runtime changes.

## Executive summary

We do **not** yet have evidence to replace the current `tBTCUSD_3h` champion.

What we do have is:

- an incumbent champion that still wins the direct validation replay on score
- a coherent RI candidate family that trades and passes validation constraints
- strong evidence that the RI family should be developed as a separate strategy family, not as a thin overlay on the current champion

## Current leaderboard

### 1. Incumbent champion remains the active best validation candidate

Source: `tmp/champion_validation_20260318.log`

- Score: `0.2617`
- Return: `0.45%`
- Trades: `37`
- Win rate: `67.6%`
- Profit factor: `1.72`
- Max drawdown: `1.47%`

Recommendation:

- keep as incumbent champion until a challenger beats it on a governed comparison path

### 2. RI candidate family is real, but not yet promotable

Primary sources:

- `results/hparam_search/run_20260318_112046/best_trial.json`
- `results/hparam_search/run_20260318_112046/validation/trial_001.json`
- `results/hparam_search/run_20260318_112046/validation/trial_002.json`
- `results/hparam_search/run_20260318_112046/validation/trial_005.json`

Observed RI validation winner cluster:

- `trial_001`, `trial_002`, `trial_005`
- score: `0.22729723723866666`
- return: `1.2696%`
- trades: `62`
- win rate: `53.23%`
- profit factor: `1.6343`
- max drawdown: `2.8781%`

These three are effectively the same candidate family with minor `risk_state` variation.

### 3. Lower-ranked RI validation cluster

Sources:

- `results/hparam_search/run_20260318_112046/validation/trial_003.json`
- `results/hparam_search/run_20260318_112046/validation/trial_004.json`

Observed metrics:

- score: `0.21610457315937975`
- return: `1.0902%`
- trades: `62`
- win rate: `53.23%`
- profit factor: `1.5986`
- max drawdown: `2.8270%`

This cluster is weaker than the `001/002/005` family and should not be the lead challenger.

## Practical interpretation

### What is the best candidate right now?

If the question is **"what is the best current champion candidate?"**, the answer is:

- **the current incumbent champion remains the best validated candidate right now**

If the question is **"what is the best next challenger family?"**, the answer is:

- **the RI family represented by `trial_001/002/005` (same family as `trial_025`)**

## Promotion stance

### Do we have a new champion today?

No.

Reason:

- The incumbent champion still beats the RI challenger family on the direct validation score used in this slice.
- The RI family is promising, but not yet strong enough to justify promotion.

### Do we have a worthy challenger to continue developing?

Yes.

Recommended challenger baseline:

- freeze the `trial_001/002/005` family as the RI challenger baseline for the next governed search slice

## Recommended next step

Continue on **two clearly separated tracks**:

### Track A — incumbent control

- keep `config/strategy/champions/tBTCUSD_3h.json` as the incumbent control baseline
- do not overlay RI directly onto it as a migration path

### Track B — RI challenger family

Use the `trial_001/002/005` family as the baseline for the next RI-focused search.

Suggested baseline traits for that family:

- `authority_mode = regime_module`
- RI `version = v2`
- `signal_adaptation.atr_period = 14`
- gates `3/2`
- threshold family matching the validated RI cluster
- `clarity_score.enabled = false`
- `risk_state.enabled = true`

## What the next governed slice should try to achieve

The next RI slice should try to produce a challenger that can beat the incumbent champion on at least one of these stronger standards:

1. higher validation score with acceptable drawdown
2. equal/slightly lower score but materially better robustness across additional windows
3. positive blind-2025 result strong enough to justify a promotion discussion

## Recommended decision rule going forward

- **Incumbent champion:** current `tBTCUSD_3h` champion
- **Lead challenger family:** RI `trial_001/002/005`
- **Promotion status:** not ready
- **Research status:** continue

## Bottom line

We should absolutely continue looking for a new champion candidate — but the evidence says the right place to search is **inside the RI challenger family**, not by trying to patch RI onto the incumbent champion.
