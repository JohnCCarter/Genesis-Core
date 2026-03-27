# Regime Intelligence challenger family — DECISION EV/edge slice1 execution outcome signoff summary

Date: 2026-03-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `completed / research-only / PLATEAU`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `obs`
- **Risk:** `MED` — why: this summary records the executed research-only Decision EV/edge slice outcome and closes the lane without opening runtime validity, comparison, readiness, promotion, or writeback.
- **Required Path:** `Full gated docs-only`
- **Objective:** Record the exact outcome of the first admissible Decision EV/edge slice and apply the strict decision gate.
- **Candidate:** `tBTCUSD 3h RI Decision EV/edge slice1 full grid result`
- **Base SHA:** `d227be7e6d07c4b389529ee6a0ece228ca9a9b10`

### Scope

- **Scope IN:** one docs-only outcome summary covering smoke proof, canonical full execution, exact metrics, strict classification, and the resulting decision gate.
- **Scope OUT:** no source-code changes, no config changes, no changes under `src/core/**`, no changes to `family_registry.py`, no changes to `family_admission.py`, no automatic slice2, no comparison opening, no readiness opening, no promotion opening, no writeback.
- **Expected changed files:** `docs/governance/regime_intelligence_optuna_decision_ev_edge_slice1_execution_outcome_signoff_summary_2026-03-27.md`
- **Max files touched:** `1`

### Stop Conditions

- any ambiguity about the exact validated outcome
- any evidence of runtime error, failed trial, or artifact incompleteness
- any attempt to reinterpret the result as runtime-valid RI conformity or promotion authority

## Executed subjects

### Canonical launch subject

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_decision_ev_edge_slice1_2024_v1.yaml`
- `run_id: ri_decision_ev_edge_slice1_launch_20260327`
- artifact root: `results/hparam_search/ri_decision_ev_edge_slice1_launch_20260327/`

### Smoke subject

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_decision_ev_edge_slice1_smoke_20260327.yaml`
- `run_id: ri_decision_ev_edge_slice1_smoke_20260327`
- artifact root: `results/hparam_search/ri_decision_ev_edge_slice1_smoke_20260327/`

## Phase status

### Phase 1 — Smoke validation

Result: `PASS`

Verified facts:

- smoke artifact set exists and is bound by `run_meta.json`
- exactly `9` smoke trial JSON artifacts were produced
- repository search found no `Traceback`, `ERROR`, `FAILED`, or `SKIPPED` markers
- file-based evidence confirmed non-zero trades across the grid (`12`, `13`, and `14` trades)
- emitted smoke artifacts preserved `thresholds.min_edge = 0.0` as an explicit serialized literal

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

Observed non-blocking artifact note:

- emitted trial artifacts still carry the known `merged_config.strategy_family = legacy` metadata quirk
- `run_meta.json` and the executed config path remain bound to the intended RI Decision YAML
- this quirk did not block research-only interpretation of the executed slice

## Exact outcome extraction

### Train-side score geometry

The full 9-trial train grid did **not** collapse into one single score tuple.

Observed train-side geometry by `thresholds.min_edge`:

#### Geometry A — `thresholds.min_edge = 0.00`

- tuples:
  - `(ev.R_default=1.6, thresholds.min_edge=0.00)` → `trial_001`
  - `(ev.R_default=1.8, thresholds.min_edge=0.00)` → `trial_004`
  - `(ev.R_default=2.0, thresholds.min_edge=0.00)` → `trial_007`
- score: `0.3483831252109516`
- profit factor: `2.2673747395738073`
- max drawdown: `0.020826371420198206`
- trades: `70`
- sharpe: `0.25869044908406247`
- total return: `0.019048553157600328`

#### Geometry B — `thresholds.min_edge = 0.01`

- tuples:
  - `(ev.R_default=1.6, thresholds.min_edge=0.01)` → `trial_002`
  - `(ev.R_default=1.8, thresholds.min_edge=0.01)` → `trial_005`
  - `(ev.R_default=2.0, thresholds.min_edge=0.01)` → `trial_008`
- score: `0.4414426432506574`
- profit factor: `3.0167738958170376`
- max drawdown: `0.016793944212705077`
- trades: `66`
- sharpe: `0.3199106071648006`
- total return: `0.04159677671379941`

#### Geometry C — `thresholds.min_edge = 0.02`

- tuples:
  - `(ev.R_default=1.6, thresholds.min_edge=0.02)` → `trial_003`
  - `(ev.R_default=1.8, thresholds.min_edge=0.02)` → `trial_006`
  - `(ev.R_default=2.0, thresholds.min_edge=0.02)` → `trial_009`
- score: `0.3615944944371261`
- profit factor: `2.450811260848`
- max drawdown: `0.020594425085928066`
- trades: `63`
- sharpe: `0.2628038152032381`
- total return: `0.028044510050974535`

Top recorded train-side trial:

- `trial_id: trial_002`
- parameter combination:
  - `ev.R_default = 1.6`
  - `thresholds.min_edge = 0.01`
- score: `0.4414426432506574`
- profit factor: `3.0167738958170376`
- max drawdown: `0.016793944212705077`
- trades: `66`
- sharpe: `0.3199106071648006`
- total return: `0.04159677671379941`

Interpretation:

- train-side differentiation was real
- within this slice, train-side geometry tracked `thresholds.min_edge`, not `ev.R_default`

### Validation-side outcome geometry

The validation stage evaluated exactly `5` tuples because `top_n = 5`.

Observed validated tuple set:

#### Plateau geometry — all validated `thresholds.min_edge = 0.01` tuples

- tuples:
  - `(ev.R_default=1.6, thresholds.min_edge=0.01)` → `validation/trial_001`
  - `(ev.R_default=1.8, thresholds.min_edge=0.01)` → `validation/trial_002`
  - `(ev.R_default=2.0, thresholds.min_edge=0.01)` → `validation/trial_003`
- score: `0.26974911658712664`
- profit factor: `1.8845797002042906`
- max drawdown: `0.027808774550017137`
- trades: `63`
- sharpe: `0.20047738907046656`
- total return: `0.0319034694105756`

#### Weaker geometry — validated subset of `thresholds.min_edge = 0.02`

- tuples:
  - `(ev.R_default=1.6, thresholds.min_edge=0.02)` → `validation/trial_004`
  - `(ev.R_default=1.8, thresholds.min_edge=0.02)` → `validation/trial_005`
- score: `0.14794606273673022`
- profit factor: `1.3852493175913543`
- max drawdown: `0.04363754151783238`
- trades: `60`
- sharpe: `0.11611655219838882`
- total return: `0.0004989928398264965`

Unvalidated full-grid tuples under `top_n = 5`:

- `(ev.R_default=1.6, thresholds.min_edge=0.00)`
- `(ev.R_default=1.8, thresholds.min_edge=0.00)`
- `(ev.R_default=2.0, thresholds.min_edge=0.00)`
- `(ev.R_default=2.0, thresholds.min_edge=0.02)`

Top validated artifact recorded in the validation artifact set:

- `trial_id: trial_001`
- parameter combination:
  - `ev.R_default = 1.6`
  - `thresholds.min_edge = 0.01`
- score: `0.26974911658712664`
- profit factor: `1.8845797002042906`
- max drawdown: `0.027808774550017137`
- trades: `63`
- sharpe: `0.20047738907046656`
- total return: `0.0319034694105756`

Observed validation-side duplication evidence:

- all three validated `thresholds.min_edge = 0.01` tuples reproduced the same plateau signature exactly
- both validated `thresholds.min_edge = 0.02` tuples reproduced the same weaker signature exactly
- no validated tuple exceeded the plateau signature

## Golden plateau comparison

Golden plateau reference carried forward into this slice:

- validation score: `0.26974911658712664`
- profit factor: `1.8845797002042906`
- max drawdown: `0.027808774550017137`
- trades: `63`
- sharpe: `0.20047738907046656`

Best validated Decision EV/edge slice outcome:

- validation score: `0.26974911658712664`
- profit factor: `1.8845797002042906`
- max drawdown: `0.027808774550017137`
- trades: `63`
- sharpe: `0.20047738907046656`

Comparison result:

- the best validated outcome reproduces the plateau signature **exactly**
- three distinct validated tuples reached the exact plateau signature
- no validated artifact exceeds the golden plateau reference
- no verified improvement geometry exists

## Strict classification

Classification: `PLATEAU`

Why:

1. no validated artifact exceeded the golden plateau score `0.26974911658712664`
2. the best validated artifact reproduced the exact plateau signature tuple
3. equality to the incumbent score was pre-defined as `PLATEAU`
4. the result therefore satisfies the pre-defined falsification condition for non-improving Decision EV/edge slice1 behavior

## Decision gate

Decision: `CLOSE Decision EV/edge slice1 as non-improving`

Consequences:

- do **not** create slice2 automatically
- do **not** open comparison
- do **not** open readiness
- do **not** open promotion
- do **not** perform champion/default writeback
- retain this result as research-only plateau evidence
- require a separate later governance packet before any new Decision lane is opened

## Bottom line

The first admissible RI Decision EV/edge slice executed successfully under the approved research envelope and produced real train-side differentiation across the `thresholds.min_edge` seam.

However, on validation, the best outcome reproduced the incumbent plateau signature exactly for all three `thresholds.min_edge = 0.01` tuples, while the validated `thresholds.min_edge = 0.02` subset underperformed.

Because no validated tuple produced strict uplift over `0.26974911658712664`, the correct classification is `PLATEAU`, and the lane closes without opening slice2, comparison, readiness, promotion, or writeback.
