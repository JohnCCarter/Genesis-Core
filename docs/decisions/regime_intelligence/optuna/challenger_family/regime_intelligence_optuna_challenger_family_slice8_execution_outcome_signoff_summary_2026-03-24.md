# Regime Intelligence challenger family slice8 — execution outcome sign-off summary

Date: 2026-03-24
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `execution-complete / widen-search evidence achieved / no anchor sign-off`

## Purpose

This note closes the governed execution for RI challenger family slice8 on `tBTCUSD 3h`.

It records:

- the pinned execution provenance
- the validation outcome used by the slice8 execution packet
- the comparison versus slice7, slice6, slice4, slice3, and the incumbent same-head control
- the duplicate-ratio improvement that made the widen-search useful even without a higher validation score
- the residual risks that still block any anchor, promotion, or freeze interpretation

## Canonical tracked summary

Tracked summary artifact for this execution:

- `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice8_20260324.json`

Primary local run artifacts referenced by this summary:

- `results/hparam_search/run_20260324_174006/run_meta.json`
- `results/hparam_search/run_20260324_174006/best_trial.json`
- `results/hparam_search/run_20260324_174006/validation/trial_001.json`
- `results/hparam_search/storage/ri_challenger_family_slice8_3h_2024_v1.db`

## Execution provenance

This run was executed against the clean reviewed launch tree:

- full SHA: `9c1f9d3b76f19194217bdab629a30f3f62bf107a`
- config: `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`
- `run_id=run_20260324_174006`
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

The execution preconditions required by the slice8 execution packet were satisfied on the pinned launch tree.

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

- `trial_005`
- score: `0.4414426432506574`
- params: `entry_conf_overall=0.27`, `regime_proba.balanced=0.36`, `hysteresis_steps=4`, `cooldown_bars=1`

### Validation winner

Validation winner used for governed comparison:

- `trial_001`
- validation score: `0.26974911658712664`
- trades: `63`
- profit factor: `1.8845797002042906`
- max drawdown: `0.027808774550017137`
- sharpe: `0.20047738907046656`
- params: `entry_conf_overall=0.27`, `regime_proba.balanced=0.36`, `hysteresis_steps=4`, `cooldown_bars=1`

## Comparison versus governed references

Validation winner score `0.26974911658712664` versus:

- slice7 validation winner `0.26974911658712664` → **same score**
- slice6 plateau `0.23646934335498004` → **higher**
- slice4 plateau `0.22516209452403432` → **higher**
- slice3 plateau `0.22289051935876203` → **higher**
- incumbent same-head control `0.2616884080730424` → **higher on score**

## Duplicate-ratio comparison

Optuna diagnostics for this run:

- attempted trials: `96`
- duplicates: `25`
- duplicate ratio: `0.2604166666666667`

Compared with slice7:

- slice7 duplicate ratio: `0.90625`
- slice8 duplicate ratio: `0.2604166666666667`
- improvement: `0.6458333333333333`

Interpretation:

- slice8 did not produce a higher validation winner than slice7
- slice8 did produce dramatically stronger search-quality evidence by reproducing the same winning local geometry with far less duplicate collapse
- this makes the slice8 widen-search useful governed evidence even without a new score high-water mark

## Sign-off conclusion

Slice8 satisfied the success rule of its execution packet for widen-search evidence.

Why:

- the governed validation winner remained at the slice7 level while still beating slice6, slice4, slice3, and the incumbent same-head control on score
- the duplicate ratio improved materially from `0.90625` to `0.2604166666666667`
- the execution was run under the pinned canonical flags on a clean reviewed tree

This summary therefore supports the following narrow sign-off statement:

- **slice8 execution is complete and counts as a successful RI widen-search evidence run**

This summary does **not** support the following claims:

- automatic anchor approval
- automatic promotion approval
- champion cutover approval
- default/runtime behavior change approval

Any anchor, promotion, or freeze discussion must still be packeted separately.

## Residual risks

### 1. No higher validation score than slice7

Interpretation:

- slice8 strengthened robustness evidence, but it did not establish a strictly better validation score than slice7
- any anchor decision must therefore be explicit and governed, not inferred automatically from the widen-search

### 2. Strategy-family metadata quirk in run artifacts

The run artifacts still show `merged_config.strategy_family = legacy` even though the slice was packeted and admitted as RI research.

Current assessment:

- this appears consistent with earlier RI slice artifacts and was not introduced by the slice8 work
- it did not block this execution packet
- it should still be audited separately before any promotion-grade or freeze-grade interpretation of RI run artifacts

## Next governed step

Recommended next step:

- packet a focused RI anchor-decision assessment deciding whether the slice8-backed local geometry (`entry_conf_overall=0.27`, `regime_proba.balanced=0.36`, `hysteresis_steps=4`, `cooldown_bars=1`) should become the next RI research anchor, or whether one more falsification slice is required before any anchor choice is made
