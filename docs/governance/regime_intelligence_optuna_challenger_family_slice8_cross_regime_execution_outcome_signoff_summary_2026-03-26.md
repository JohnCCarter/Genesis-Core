# Regime Intelligence challenger family slice8 cross-regime OOS 2025 — execution outcome sign-off summary

Date: 2026-03-26
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `execution-complete / negative cross-regime generalization evidence / no anchor-or-promotion sign-off`

## Purpose

This note closes the governed cross-regime replay opened for the reproduced slice8 full tuple on `tBTCUSD 3h`.

It records:

- the exact launch provenance for the authorized 2025 OOS replay
- the observed single-trial outcome on the fixed slice8 tuple
- the narrow interpretation that is supported by this run
- the claims that remain explicitly unsupported
- the recommended next governed research step

## Canonical tracked summary

Primary run artifacts referenced by this summary:

- `results/hparam_search/ri_slice8_cross_regime_oos_launch_20260326/run_meta.json`
- `results/hparam_search/ri_slice8_cross_regime_oos_launch_20260326/best_trial.json`
- `results/hparam_search/storage/ri_challenger_family_slice8_cross_regime_oos_2025_v1.db`

Governing packet chain for this cross-regime replay:

- `docs/governance/regime_intelligence_optuna_challenger_family_slice8_cross_regime_research_question_packet_2026-03-26.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_slice8_cross_regime_setup_only_packet_2026-03-26.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_slice8_cross_regime_launch_authorization_packet_2026-03-26.md`

## Execution provenance

This run was executed against the clean reviewed launch tree:

- full SHA: `0514dbf8708097ef0e037a6451320912dcba71a9`
- config: `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_cross_regime_oos_2025_v1.yaml`
- `run_id=ri_slice8_cross_regime_oos_launch_20260326`
- `run_intent=research_slice`
- symbol: `tBTCUSD`
- timeframe: `3h`
- sample window: `2025-01-01..2025-12-31`
- validation: `disabled`
- score version: `v2`
- study name: `ri_challenger_family_slice8_cross_regime_oos_2025_v1`
- storage: `results/hparam_search/storage/ri_challenger_family_slice8_cross_regime_oos_2025_v1.db`

Canonical execution flags:

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

The execution preconditions required by the launch-authorization packet were satisfied on the pinned launch tree.

This included:

- no tracked working-tree changes at launch time
- storage DB absence check before launch
- validator replay on the exact launch YAML
- preflight replay on the exact launch YAML under canonical flags
- exact-config launch authorization for this replay only

Outcome:

- execution gate bundle: `PASS`

## Outcome summary

The authorized replay executed exactly one fixed trial.

Observed result:

- `trial_001`
- score: `0.07072678526577773`
- trades: `131`
- total return: `-0.0741219662911315`
- profit factor: `1.1975357661291959`
- max drawdown: `0.1009633059474205`
- sharpe: `0.059252108457198624`
- win rate: `0.6259541984732825`
- hard failures: none
- constraints: `ok=true`

Fixed replay tuple carried into the OOS run included, among other parameters:

- `entry_conf_overall=0.27`
- `regime_proba.balanced=0.36`
- `gates.hysteresis_steps=4`
- `gates.cooldown_bars=1`
- `max_hold_bars=8`
- `exit_conf_threshold=0.42`
- `ltf_override_threshold=0.40`
- `clarity_score.enabled=false`
- `risk_state.enabled=true`

Optuna diagnostics for this run:

- attempted trials: `1`
- duplicates: `0`
- duplicate ratio: `0.0`
- pruned count: `0`
- zero-trade count: `0`

## Interpretation discipline

This replay supports the following narrow conclusion:

- the reproduced slice8 full tuple did **not** show strong cross-regime generalization on the bounded `2025-01-01..2025-12-31` OOS replay surface

Why this conclusion is justified:

- the replay was executed on the exact fixed slice8 tuple rather than a nearby variant
- the replay used the separately packeted and authorized non-2024 sample window
- the observed outcome was weak on score and negative on total return
- no alternate best-trial selection or validation-stage re-ranking exists here because the run was a one-trial fixed replay

This summary therefore supports the following sign-off statement:

- **the slice8 cross-regime question has been answered negatively on this bounded 2025 OOS replay surface**

## Claims explicitly not supported

This summary does **not** support the following claims:

- RI family rejection in general
- permanent rejection of slice8-related research
- objective-function invalidation by itself
- canonical anchor approval
- promotion approval
- runtime/default behavior change approval

The result is best read as falsification-grade evidence for this exact tuple on this exact cross-regime surface, not as a family-wide terminal verdict.

## Residual risks

### 1. Single-surface evidence only

Interpretation:

- this run answers one bounded non-2024 replay question only
- it should not be generalized into a claim about every alternative regime window or every nearby management/search-space variant

### 2. Artifact metadata quirk still exists

The run artifact still reports:

- `merged_config.strategy_family = legacy`

Current assessment:

- this remains consistent with earlier RI research artifacts
- it did not block this governed replay
- it still should not be treated as promotion-grade family-identity evidence

### 3. Snapshot label remains 2024-scoped while sample window is 2025

Interpretation:

- the preflight warning remained non-blocking because the runner uses the explicit sample range
- the warning should still remain visible in any future replay interpretation so that the evidence chain stays precise

## Next governed step

Recommended next step:

- open the **structural search-space** lane next if further RI challenger-family research is desired

Why:

- the bounded cross-regime replay already answered the user's chosen question `C` with negative evidence for the exact slice8 tuple
- because that answer is now available, the next informative lane is not to reopen the same tuple again, but to test whether a structurally adjusted search surface can produce a more robust family candidate
- the objective-change lane should remain secondary until a structural lane either improves robustness evidence or proves equally brittle

## Bottom line

The governed slice8 cross-regime replay is now complete.

Its exact bounded result is:

- one fixed 2025 OOS replay
- on the reproduced slice8 full tuple
- under the authorized research-only config and canonical flags
- yielding score `0.07072678526577773` with return `-7.41%`

That is sufficient to close the current cross-regime question with a negative answer on this bounded surface.

Any further work should proceed through a separate packeted lane, with **structural search-space change** as the recommended next step.
