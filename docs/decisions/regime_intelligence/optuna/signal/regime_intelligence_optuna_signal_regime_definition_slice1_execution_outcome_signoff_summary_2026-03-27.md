# Regime Intelligence challenger family — SIGNAL regime-definition slice1 execution outcome signoff summary

Date: 2026-03-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `completed / research-only / PLATEAU`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `HIGH` — why: this summary records the executed research-only regime-definition slice outcome and closes the decision gate without opening runtime validity, comparison, readiness, promotion, or writeback.
- **Required Path:** `Full gated docs-only`
- **Objective:** Record the exact outcome of the first admissible regime-definition slice and apply the strict decision gate.
- **Candidate:** `tBTCUSD 3h RI SIGNAL regime-definition slice1 full grid result`
- **Base SHA:** `d227be7e6d07c4b389529ee6a0ece228ca9a9b10`

### Scope

- **Scope IN:** one docs-only outcome summary covering smoke proof, canonical full execution, exact metrics, strict classification, and the resulting decision gate.
- **Scope OUT:** no source-code changes, no config changes, no changes under `src/core/**`, no changes to `family_registry.py`, no changes to `family_admission.py`, no automatic slice2, no comparison opening, no readiness opening, no promotion opening, no writeback.
- **Expected changed files:** `docs/decisions/regime_intelligence/optuna/signal/regime_intelligence_optuna_signal_regime_definition_slice1_execution_outcome_signoff_summary_2026-03-27.md`
- **Max files touched:** `1`

### Stop Conditions

- any ambiguity about the exact validated outcome
- any evidence of runtime error, failed trial, or artifact incompleteness
- any attempt to reinterpret the result as runtime-valid RI conformity or promotion authority

## Executed subjects

### Canonical launch subject

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_signal_regime_definition_slice1_2024_v1.yaml`
- `run_id: ri_signal_regime_definition_slice1_launch_20260327`
- artifact root: `results/hparam_search/ri_signal_regime_definition_slice1_launch_20260327/`

### Smoke subject

- `tmp/tBTCUSD_3h_ri_signal_regime_definition_slice1_smoke_20260327.yaml`
- `run_id: ri_signal_regime_definition_slice1_smoke`
- artifact root: `results/hparam_search/ri_signal_regime_definition_slice1_smoke/`

## Phase status

### Phase 1 — Smoke validation

Result: `PASS`

Verified facts:

- smoke artifact set exists and is bound by `run_meta.json`
- exactly `9` smoke trial JSON artifacts were produced
- repository search found no `Traceback`, `ERROR`, `FAILED`, or `SKIPPED` markers
- file-based evidence confirmed non-zero trades (`num_trades: 13`)

### Phase 2 — Canonical preflight confirmation

Result: `PASS`

Verified facts:

- validator returned warnings only, no hard failure
- preflight returned overall `[OK]`
- family admission passed for `run_intent=research_slice`
- exactly `2` searchable parameters were present

### Phase 3 — Launch authorization

Result: `AUTHORIZED NOW`

Authority boundary remained research-only and excluded runtime validity, comparison, readiness, promotion, and writeback.

### Phase 4 — Full execution

Result: `PASS`

Verified facts:

- process exited with code `0`
- main run metadata recorded `validated: 5`
- full artifact set contains `9` train trial JSON files and `5` validation trial JSON files
- repository search found no `Traceback`, `ERROR`, `FAILED`, or `SKIPPED` markers in the full artifact tree

## Exact outcome extraction

### Best train-side artifact

Top recorded train-side trial:

- `trial_id: trial_001`
- parameter combination:
  - `adx_trend_threshold = 23.0`
  - `adx_range_threshold = 18.0`
  - `slope_threshold = 0.001`
  - `volatility_threshold = 0.05`
- score: `0.4414426432506574`
- profit factor: `3.0167738958170376`
- max drawdown: `0.016793944212705077`
- trades: `66`
- sharpe: `0.3199106071648006`
- total return: `0.04159677671379941`

Observed train-side duplication evidence:

- stdout from the completed run showed `trial_001` through `trial_009` all returning the same train-side metric tuple
- the train artifact set contains `9` unique grid tuples but only one observed train-side score geometry

### Best validated artifact

Top validated trial recorded in the validation artifact set:

- `trial_id: trial_001`
- parameter combination:
  - `adx_trend_threshold = 23.0`
  - `adx_range_threshold = 18.0`
  - `slope_threshold = 0.001`
  - `volatility_threshold = 0.05`
- score: `0.26974911658712664`
- profit factor: `1.8845797002042906`
- max drawdown: `0.027808774550017137`
- trades: `63`
- sharpe: `0.20047738907046656`
- total return: `0.0319034694105756`

Observed validation-side duplication evidence:

- total validated trials: `5`
- stdout from the completed run showed validation `trial_001` through `trial_005` all returning the same validated metric tuple
- sampled validation artifacts (`trial_001.json`, `trial_005.json`) confirmed the same score tuple under distinct parameter combinations

## Golden plateau comparison

Golden plateau reference carried forward into this slice:

- validation score: `0.26974911658712664`
- profit factor: `1.8845797002042906`
- max drawdown: `0.027808774550017137`
- trades: `63`
- sharpe: `0.20047738907046656`

Best validated regime-definition slice outcome:

- validation score: `0.26974911658712664`
- profit factor: `1.8845797002042906`
- max drawdown: `0.027808774550017137`
- trades: `63`
- sharpe: `0.20047738907046656`

Comparison result:

- the best validated outcome reproduces the plateau signature **exactly**
- no validated artifact exceeds the golden plateau reference
- no verified improvement geometry exists

## Strict classification

Classification: `PLATEAU`

Why:

1. no validated artifact exceeded the golden plateau score `0.26974911658712664`
2. the best validated artifact reproduced the exact plateau signature tuple
3. the result therefore satisfies the pre-defined falsification condition for non-improving regime-definition slice1 behavior

## Decision gate

Decision: `CLOSE regime-definition slice1 as non-improving`

Consequences:

- do **not** create slice2 automatically
- do **not** open comparison
- do **not** open readiness
- do **not** open promotion
- do **not** perform champion/default writeback
- retain this result as research-only plateau evidence

## Bottom line

The first admissible RI regime-definition slice executed successfully under the approved research envelope, but its best validated result reproduced the previously tracked plateau signature exactly.

Because the slice did not produce verified uplift, the strict classification is `PLATEAU`, and the decision gate closes the lane without opening slice2, comparison, readiness, promotion, or writeback.
