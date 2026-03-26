# Regime Intelligence challenger family slice9 — execution outcome sign-off summary

Date: 2026-03-26
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `execution-complete / management-surface evidence achieved / no canonical-anchor sign-off`

## Purpose

This note closes the governed execution for RI challenger family slice9 on `tBTCUSD 3h`.

It records:

- the pinned execution provenance
- the validation outcome used by the slice9 execution packet
- the comparison versus slice8, slice7, slice6, and the incumbent same-head control
- the management-tuple difference that made slice9 a real falsification test rather than a pure repeat
- the residual risks that still block any canonical anchor, promotion, or freeze interpretation

## Canonical tracked summary

Tracked summary artifact for this execution:

- `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice9_20260326.json`

Primary local run artifacts referenced by this summary:

- `results/hparam_search/run_20260326_090908/run_meta.json`
- `results/hparam_search/run_20260326_090908/best_trial.json`
- `results/hparam_search/run_20260326_090908/validation/trial_001.json`
- `results/hparam_search/storage/ri_challenger_family_slice9_3h_2024_v1.db`

## Execution provenance

This run was executed against the clean reviewed launch tree:

- full SHA: `22a3900504ec87e8e3834b1be3bf900403687ec3`
- config: `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice9_2024_v1.yaml`
- `run_id=run_20260326_090908`
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

The execution preconditions required by the slice9 execution packet were satisfied on the pinned launch tree.

This included:

- clean working tree at launch time
- storage DB absence check before launch
- validator replay on exact launch YAML
- preflight replay on exact launch YAML under canonical flags
- determinism / feature-cache / pipeline-hash / authority-mode pytest anchors
- mandatory runtime-governance anchors

Outcome:

- execution gate bundle: `PASS`

## Outcome summary

### Best train trial

Best train trial recorded by Optuna:

- `trial_002`
- score: `0.4414426432506574`
- params: `entry_conf_overall=0.27`, `regime_proba.balanced=0.36`, `hysteresis_steps=4`, `cooldown_bars=1`, `max_hold_bars=8`, `exit_conf_threshold=0.40`, `ltf_override_threshold=0.38`

### Validation winner

Validation winner used for governed comparison:

- `trial_001`
- validation score: `0.26974911658712664`
- trades: `63`
- profit factor: `1.8845797002042906`
- max drawdown: `0.027808774550017137`
- sharpe: `0.20047738907046656`
- params: `entry_conf_overall=0.27`, `regime_proba.balanced=0.36`, `hysteresis_steps=4`, `cooldown_bars=1`, `max_hold_bars=8`, `exit_conf_threshold=0.40`, `ltf_override_threshold=0.38`

## Comparison versus governed references

Validation winner score `0.26974911658712664` versus:

- slice8 validation winner `0.26974911658712664` → **same score**
- slice7 validation winner `0.26974911658712664` → **same score**
- slice6 plateau `0.23646934335498004` → **higher**
- incumbent same-head control `0.2616884080730424` → **higher on score**

## Management-tuple comparison versus slice8

Slice8 provisional management tuple:

- `max_hold_bars=8`
- `exit_conf_threshold=0.42`
- `ltf_override_threshold=0.40`

Slice9 validation winner tuple:

- `max_hold_bars=8`
- `exit_conf_threshold=0.40`
- `ltf_override_threshold=0.38`

Interpretation:

- slice9 matched the slice8/slice7 governed validation score
- slice9 did so with a **non-slice8 management tuple**
- this means the slice8 entry/gating backbone survives at least one nearby management perturbation without dropping below the incumbent same-head control

## Duplicate-ratio comparison

Optuna diagnostics for this run:

- attempted trials: `75`
- duplicates: `26`
- duplicate ratio: `0.3466666666666667`

Compared with earlier governed references:

- slice8 duplicate ratio: `0.2604166666666667`
- slice7 duplicate ratio: `0.90625`

Interpretation:

- slice9 duplicate behavior was worse than slice8
- slice9 duplicate behavior remained materially better than slice7
- this weakens any claim that slice9 improved search efficiency, but does not negate the management-surface robustness signal

## Sign-off conclusion

Slice9 satisfied the success rule of its execution packet for bounded management-surface evidence.

Why:

- the governed validation winner remained at the slice7/slice8 level
- the governed validation winner stayed above the incumbent same-head control on score
- the governed validation winner used a management tuple that differs from the provisional slice8 tuple (`0.40 / 0.38` instead of `0.42 / 0.40` on the reopened axes)
- the execution was run under the pinned canonical flags on a clean reviewed tree

This summary therefore supports the following narrow sign-off statement:

- **slice9 execution is complete and counts as a successful RI bounded management-surface evidence run**

This summary does **not** support the following claims:

- canonical anchor approval
- automatic promotion approval
- champion cutover approval
- default/runtime behavior change approval

Any canonical-anchor, promotion, or freeze discussion must still be packeted separately.

## Residual risks

### 1. No higher validation score than slice7 or slice8

Interpretation:

- slice9 strengthened robustness evidence, but it did not establish a strictly better validation score than the current RI high-water line
- any anchor decision must therefore remain explicit and governed, not inferred automatically from repeated equal-score runs

### 2. Duplicate ratio degraded versus slice8

Interpretation:

- slice9 broadened robustness evidence on the management surface, but it did not improve search cleanliness versus slice8
- this means slice9 is better read as falsification evidence than as a cleaner next anchor packet by itself

### 3. Strategy-family metadata quirk in run artifacts

The run artifacts still show `merged_config.strategy_family = legacy` even though the slice was packeted and admitted as RI research.

Current assessment:

- this appears consistent with earlier RI slice artifacts and was not introduced by the slice9 work
- it did not block this execution packet
- it should still be audited separately before any promotion-grade or freeze-grade interpretation of RI run artifacts

## Next governed step

Recommended next step:

- refresh the RI anchor-decision assessment with slice9 included, since the slice8 backbone now has governed evidence of surviving a nearby management-surface perturbation while staying at the current RI validation high-water line
