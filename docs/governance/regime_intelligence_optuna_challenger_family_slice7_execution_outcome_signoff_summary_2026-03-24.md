# Regime Intelligence challenger family slice7 — execution outcome sign-off summary

Date: 2026-03-24
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `execution-complete / challenger evidence achieved / no promotion sign-off`

## Purpose

This note closes the governed execution for RI challenger family slice7 on `tBTCUSD 3h`.

It records:

- the pinned execution provenance
- the validation outcome used by the execution packet
- the comparison versus slice6, slice4, slice3, and the incumbent same-head control
- the residual risks that still block any promotion interpretation

## Canonical tracked summary

Tracked summary artifact for this execution:

- `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice7_20260324.json`

Primary local run artifacts referenced by this summary:

- `results/hparam_search/run_20260324_171511/run_meta.json`
- `results/hparam_search/run_20260324_171511/best_trial.json`
- `results/hparam_search/run_20260324_171511/validation/trial_001.json`
- `results/hparam_search/storage/ri_challenger_family_slice7_3h_2024_v1.db`

## Execution provenance

This run was executed against the clean reviewed launch tree:

- full SHA: `1d1470745927050cf9a0cfd4ccb6d3603b1d813d`
- config: `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice7_2024_v1.yaml`
- `run_id=run_20260324_171511`
- `run_intent=research_slice`
- symbol: `tBTCUSD`
- timeframe: `3h`
- train window: `2023-12-21..2024-06-30`
- validation window: `2024-07-01..2024-12-31`
- score version: `v2`

Canonical execution flags:

- `GENESIS_FAST_WINDOW=1`
- `GENESIS_PRECOMPUTE_FEATURES=1`
- `GENESIS_FAST_HASH=0`
- `GENESIS_PREFLIGHT_FAST_HASH_STRICT=1`
- `GENESIS_RANDOM_SEED=42`
- `PYTHONPATH=src`

## Gate bundle outcome

The execution preconditions required by the slice7 execution packet were satisfied on the pinned launch tree.

This included:

- clean working tree at launch time
- storage DB absence check before launch
- validator replay on exact launch YAML
- preflight replay on exact launch YAML
- mandatory runtime-governance anchors

Outcome:

- execution gate bundle: `PASS`

## Outcome summary

### Best train trial

Best train trial recorded by Optuna:

- `trial_007`
- score: `0.4414426432506574`
- gates: `hysteresis_steps=4`, `cooldown_bars=1`

### Validation winner

Validation winner used for governed comparison:

- `trial_001`
- validation score: `0.26974911658712664`
- trades: `63`
- profit factor: `1.8845797002042906`
- max drawdown: `0.027808774550017137`
- sharpe: `0.20047738907046656`
- gates: `hysteresis_steps=4`, `cooldown_bars=1`

## Comparison versus governed references

Validation winner score `0.26974911658712664` versus:

- slice6 plateau `0.23646934335498004` → **higher**
- slice4 plateau `0.22516209452403432` → **higher**
- slice3 plateau `0.22289051935876203` → **higher**
- incumbent same-head control `0.2616884080730424` → **higher on score**

## Sign-off conclusion

Slice7 satisfied the success rule of its execution packet for challenger evidence.

Why:

- the governed validation winner strictly exceeded the slice6 plateau
- the same winner also exceeded the current incumbent same-head control on score
- the execution was run under the pinned canonical flags on a clean reviewed tree

This summary therefore supports the following narrow sign-off statement:

- **slice7 execution is complete and counts as a successful RI challenger-evidence run**

This summary does **not** support the following claims:

- automatic promotion approval
- champion cutover approval
- default/runtime behavior change approval

Any promotion or freeze discussion must still be packeted separately.

## Residual risks

### 1. Duplicate-heavy search surface

Optuna diagnostics for this run:

- attempted trials: `96`
- duplicates: `87`
- duplicate ratio: `0.90625`

Interpretation:

- the slice produced useful evidence, but the search surface is very narrow and sampler efficiency was poor
- future RI slices should treat this as a search-design warning, not as invisible free robustness

### 2. Strategy-family metadata quirk in run artifacts

The run artifacts still show `merged_config.strategy_family = legacy` even though the slice was packeted and admitted as RI research.

Current assessment:

- this appears consistent with earlier RI slice artifacts and was not introduced by the slice7 family-admission work
- it did not block this execution packet
- it should still be audited separately before any promotion-grade interpretation of RI run artifacts

## Next governed step

Recommended next step:

- packet a focused RI post-slice7 assessment deciding whether to
  - keep `4/1` as the new RI family anchor for a follow-up slice, or
  - widen or reshape the search surface to reduce duplicate collapse before any candidate/freeze path is discussed
