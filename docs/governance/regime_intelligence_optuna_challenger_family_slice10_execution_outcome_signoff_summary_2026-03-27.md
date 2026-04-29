# Regime Intelligence challenger family slice10 — execution outcome sign-off summary

Date: 2026-03-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `execution-complete / bounded local plateau evidence achieved / no canonical-anchor sign-off`

## Purpose

This note closes the governed execution for RI challenger family slice10 on `tBTCUSD 3h`.

It records:

- the pinned execution provenance
- the gate bundle and launch-authority context used for the run
- the best-train outcome and the governed validation tie set
- the bounded interpretation of that tie set as local plateau evidence inside the authorized slice10 management surface
- the residual risks that still block any canonical anchor, runtime-valid RI, promotion, or default/runtime interpretation

## Canonical tracked summary

Primary local run artifacts referenced by this summary:

- `results/hparam_search/run_20260327_080025/run_meta.json`
- `results/hparam_search/run_20260327_080025/best_trial.json`
- `results/hparam_search/run_20260327_080025/validation/trial_001.json`
- `results/hparam_search/run_20260327_080025/validation/trial_002.json`
- `results/hparam_search/run_20260327_080025/validation/trial_003.json`
- `results/hparam_search/run_20260327_080025/validation/trial_004.json`
- `results/hparam_search/run_20260327_080025/validation/trial_005.json`
- `results/hparam_search/storage/ri_challenger_family_slice10_3h_2024_v1.db`

## Execution provenance

This run was executed against the separately authorized clean launch tree:

- full SHA: `d43e7cdcf6bac4e84a8ebc694152fc3ce7e1f3f9`
- config: `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice10_2024_v1.yaml`
- launch authorization packet:
  - `docs/governance/regime_intelligence_optuna_challenger_family_slice10_structural_launch_authorization_packet_2026-03-27.md`
- `run_id=run_20260327_080025`
- `run_intent=research_slice`
- symbol: `tBTCUSD`
- timeframe: `3h`
- train window: `2023-12-21..2024-06-30`
- validation window: `2024-07-01..2024-12-31`
- score version: `v2`

Canonical execution flags recorded by the launch process:

- `GENESIS_FAST_WINDOW=1`
- `GENESIS_PRECOMPUTE_FEATURES=1`
- `GENESIS_FAST_HASH=0`
- `GENESIS_PREFLIGHT_FAST_HASH_STRICT=1`
- `GENESIS_RANDOM_SEED=42`
- `PYTHONPATH=src`
- `PYTHONIOENCODING=utf-8`
- `TQDM_DISABLE=1`
- `OPTUNA_MAX_DUPLICATE_STREAK=2000`

## Gate bundle outcome

The execution preconditions required by the slice10 launch-authorization packet were satisfied on the pinned launch tree.

This included:

- clean working tree at launch time
- storage DB absence check before launch
- validator success on the exact launch YAML
- preflight success on the exact launch YAML under canonical flags
- bounded supporting smoke completion for the slice10 launch surface

Outcome:

- execution gate bundle at launch time: `PASS`

This summary re-reports the execution evidence recorded for that launch sequence.
It does not claim that the launch-precondition checks were re-run independently by this closeout note.

## Outcome summary

### Best train trial

Best train trial recorded by Optuna:

- `trial_002`
- score: `0.4414426432506574`
- params: `max_hold_bars=8`, `exit_conf_threshold=0.40`, `ltf_override_threshold=0.38`

### Governed validation tie set

This run did **not** establish a unique new validation leader.

Instead, the top validated slice10 artifacts formed a five-artifact tie set across `trial_001` through `trial_005` with the same governed validation outcome:

- validation score: `0.26974911658712664`
- trades: `63`
- profit factor: `1.8845797002042906`
- max drawdown: `0.027808774550017137`
- sharpe: `0.20047738907046656`

Representative tied management tuples in that validation tie set:

- `trial_001`: `max_hold_bars=8`, `exit_conf_threshold=0.40`, `ltf_override_threshold=0.38`
- `trial_002`: `max_hold_bars=9`, `exit_conf_threshold=0.40`, `ltf_override_threshold=0.42`
- `trial_003`: `max_hold_bars=9`, `exit_conf_threshold=0.41`, `ltf_override_threshold=0.38`
- `trial_004`: `max_hold_bars=7`, `exit_conf_threshold=0.41`, `ltf_override_threshold=0.40`
- `trial_005`: `max_hold_bars=8`, `exit_conf_threshold=0.41`, `ltf_override_threshold=0.41`

Interpretation boundary:

- slice10 therefore adds **bounded observed local plateau evidence** that multiple nearby management tuples inside the authorized slice10 surface formed the same governed validation tie signature
- this is an observed local plateau / tie-signature within this run only
- it is **not** evidence of broader generalization, a new canonical anchor, or distinct validated decision-path diversity beyond what the validation artifacts directly show

## Comparison versus governed references

Tracked comparison references for the currently cited comparison set:

- `docs/governance/regime_intelligence_optuna_challenger_family_slice9_execution_outcome_signoff_summary_2026-03-26.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_ranked_research_summary_2026-03-26.md`
- `results/hparam_search/ri_slice8_launch_20260326/validation/trial_001.json`
- `results/hparam_search/run_20260324_171511/validation/trial_001.json`

Slice10 governed validation outcome `0.26974911658712664` versus:

- slice8 validation winner `0.26974911658712664` → **same score**
- slice9 validation winner `0.26974911658712664` → **same score**
- slice7 validation winner `0.26974911658712664` → **same score**
- slice6 plateau `0.23646934335498004` → **higher**
- incumbent same-head control `0.2616884080730424` → **higher on score**

Interpretation boundary:

- slice10 reproduced rather than exceeded the currently tracked governed RI validation level within the cited comparison set
- any refreshed continuation ordering or anchor assessment must therefore be handled in a separate assessment, not inferred automatically from this closeout

## Duplicate-ratio comparison

Optuna diagnostics for this run:

- attempted trials: `75`
- duplicates: `26`
- duplicate ratio: `0.3466666666666667`

Compared with earlier governed references:

- slice8 duplicate ratio: `0.2604166666666667`
- slice9 duplicate ratio: `0.3466666666666667`
- slice7 duplicate ratio: `0.90625`

Interpretation:

- slice10 did **not** improve search cleanliness over slice9
- slice10 matched slice9 on duplicate ratio
- slice10 remained materially cleaner than slice7 but noisier than slice8

## Sign-off conclusion

Slice10 satisfied the success rule of its launch packet for a bounded RI structural management/override execution.

Why:

- the run completed on the pinned authorized slice10 subject under the reviewed canonical flag surface
- the governed validation outcome remained at the current RI high-water line
- the validation tie set showed that multiple nearby management tuples inside the authorized slice10 surface converged to the same governed validation outcome
- the run remained explicitly research-only, with promotion disabled and no writeback action

This summary therefore supports the following narrow sign-off statement:

- **slice10 execution is complete and counts as a successful RI bounded local plateau evidence run inside the authorized management/override surface**

This summary does **not** support the following claims:

- canonical anchor approval
- runtime-valid RI approval
- automatic promotion approval
- champion cutover approval
- default/runtime behavior change approval
- proof of broad generalization beyond the local authorized slice10 surface

## Residual risks

### 1. No new validation high-water line

Interpretation:

- slice10 preserved rather than exceeded the current governed validation ceiling
- this means any anchor or continuation decision must remain explicit and separately governed

### 2. No search-cleanliness gain over slice9

Interpretation:

- slice10 added local plateau evidence but did not improve duplicate-ratio behavior relative to slice9
- this weakens any argument that slice10 should automatically displace slice8 as the preferred clean continuation surface

### 3. Validation tie set is parameter-level evidence only

Interpretation:

- this summary records only that multiple nearby parameter tuples tied on the same governed validation outcome
- it does not claim that those tied tuples represent materially distinct decision traces or broader validated behavior classes

### 4. Strategy-family metadata quirk persists in run artifacts

The run artifacts still show `merged_config.strategy_family = legacy` even though the slice was packeted and admitted as RI research.

Current assessment:

- this remains consistent with earlier RI slice artifacts and was not introduced by the slice10 work
- it did not block this execution packet
- it should still be audited separately before any promotion-grade or freeze-grade interpretation of RI run artifacts

## Next governed step

Recommended next step:

- refresh the RI continuation / anchor assessment with slice10 included as additional local plateau evidence on the bounded management surface, without automatically changing slice8 preference, runtime validity, or promotion scope
