# current_atr 900 multi-year environment robustness packet

Date: 2026-04-16
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / research / observational / no-runtime-edits`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `MED` — why: this slice runs a non-trivial observational replay analysis over multiple years with controlled artifact generation, but it authorizes no runtime, config, or API changes.
- **Required Path:** `Full`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** Freeze a `2024` good-environment / bad-environment definition for the already validated `current_atr >= 900` candidate and measure whether that feature-space separation retains classification power across other full calendar years.
- **Candidate:** `current_atr 900 multi-year environment robustness`
- **Base SHA:** `e578898448711ad5b2aeca1d2ad3a3bef7342e54`

### Scope

- **Scope IN:**
  - `docs/decisions/current_atr_900_multi_year_env_robustness_packet_2026-04-16.md`
  - `tmp/current_atr_900_multi_year_env_robustness_20260416.py`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_multi_year_env_robustness_2026-04-16/manifest.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_multi_year_env_robustness_2026-04-16/robustness_summary.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_multi_year_env_robustness_2026-04-16/closeout.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - runtime defaults / authority / schema surfaces
  - API surfaces
  - all `1435` packet/artifact files
  - any output outside `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_multi_year_env_robustness_2026-04-16/`
  - any threshold mining beyond the frozen candidate `current_atr >= 900`
  - any retuning on non-`2024` years
- **Expected changed files:**
  - `docs/decisions/current_atr_900_multi_year_env_robustness_packet_2026-04-16.md`
  - `tmp/current_atr_900_multi_year_env_robustness_20260416.py`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_multi_year_env_robustness_2026-04-16/manifest.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_multi_year_env_robustness_2026-04-16/robustness_summary.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_multi_year_env_robustness_2026-04-16/closeout.md`
- **Max files touched:** `5`

### Skill Usage

- **Repo-local skill specs to apply:**
  - `.github/skills/python_engineering.json`
  - `.github/skills/genesis_backtest_verify.json`
  - `.github/skills/ri_off_parity_artifact_check.json`
- **Why these skills apply:**
  - `python_engineering` applies because this slice adds one bounded Python orchestration script under `tmp/`.
  - `genesis_backtest_verify` applies because the slice depends on deterministic replay evidence over frozen configs and frozen year sets.
  - `ri_off_parity_artifact_check` applies because the artifact outputs must keep explicit field/row discipline rather than becoming narrative-only research notes.
- **Skill coverage boundary:**
  - These skills are used as verification anchors only for this slice.
  - No broader process coverage is claimed beyond the explicit gates and outputs listed below.

## What this slice is trying to answer

This slice is not asking whether `900` is a universal strategy.
It is asking whether the feature-space where the already existing strategy seems to have positive expectancy in `2024` can be frozen and then recognized again across other years.

The target formulation is:

> We are not trying to find a universal strategy. We are trying to identify the feature-space where the existing strategy has positive expectancy, and test whether that space exists across years.

## Locked candidate and evidence basis

### Locked config artifacts

- baseline `0.90` config artifact:
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/tBTCUSD_3h_bull_high_persistence_override_min_size_001_vol_mult_090_vol_thr_75_cfg.json`
- candidate `900` config artifact:
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/candidate_900_cfg.json`

### Carried-forward evidence anchors

- prior dedicated validation:
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/replay_summary.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/closeout.md`
- prior env-profile slice:
  - `docs/decisions/current_atr_900_env_profile_packet_2026-04-16.md`
  - `tmp/current_atr_900_env_profile_20260416.py`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_env_profile_2026-04-16/env_summary.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_env_profile_2026-04-16/closeout.md`

No source-code, test, config, or authority surfaces may be changed by this slice.

## Discovery and holdout years

The year set is fixed and deterministic:

- `discovery_year = 2024`
- `holdout_years = [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2025]`
- partial `2016` is excluded
- partial `2026` is excluded

`2024` is the only year allowed to create the environment definition.
No holdout year may participate in seed selection, threshold adjustment, profile replacement, or re-ranking.

## Dirty-tree execution note

This slice may execute on a non-clean tree because a preexisting unrelated unstaged path already exists outside scope:

- `docs/decisions/current_atr_1435_default_off_trial_packet_2026-04-16.md`

That path is explicitly outside scope.
The script must record a byte/hash snapshot for that path before and after execution and fail if it changes.

This is an explicit one-slice containment exception only.
It is not a new general policy for dirty-tree execution.

## Seed construction vs frozen profile definition

This slice must keep a strict boundary between:

- `seed_only_features`
- `frozen_profile_features`

### seed_only_features

These may be used only to label the observational `2024` seed sets:

- `pnl_delta`
- `mfe_16_atr`
- `continuation_score`

Post-entry continuation proxies are used only to construct `2024` observational seed labels.
They are excluded from the frozen environment profile definition and from all holdout-year classification scoring.

### frozen_profile_features

These are the only features allowed in the frozen `good_environment` / `bad_environment` definitions and holdout-year classification:

- `current_atr_used`
- `zone_atr`
- `pre_slope_8_atr`
- `pre_range_8_atr`
- `zone`
- `regime`
- `htf_regime`
- `proba_buy`
- `proba_sell`
- `proba_edge`
- `conf_overall`
- `wick_body_ratio`

The script must assert that `seed_only_features ∩ frozen_profile_features = ∅`.

## Planned operationalization

The script must:

1. replay baseline `0.90` and candidate `900` read-only on the fixed year set above
2. restrict the analysis population inside each year to the active-treatment subset where candidate size exceeds baseline size
3. use `2024` only to build observational seed labels:
  - `good_trade_seed`: helpful rows (`pnl_delta > 0`) ranked by a composite seed-only score over `pnl_delta`, `mfe_16_atr`, and `continuation_score`, then frozen as the top discovery cohort
  - `bad_trade_seed`: harmful rows (`pnl_delta < 0`) ranked by the weakest composite seed-only score over `pnl_delta`, `mfe_16_atr`, and `continuation_score`, then frozen as the top discovery cohort
4. build frozen `2024` distribution profiles for both `good_environment` and `bad_environment` using only the `frozen_profile_features`
5. apply those same exact frozen profiles to every holdout year without retuning
6. classify each holdout-year active-treatment row as closer to `good_environment`, closer to `bad_environment`, or `ambiguous`
7. report year-by-year classification power, not just a single aggregate number
8. say plainly if the frozen separation is weak or contradictory across holdouts

## Canonical env pins

The script execution must set and record exactly:

- `GENESIS_RANDOM_SEED=42`
- `GENESIS_FAST_WINDOW=1`
- `GENESIS_PRECOMPUTE_FEATURES=1`
- `GENESIS_MODE_EXPLICIT=1`
- `GENESIS_FAST_HASH=0`
- `SYMBOL_MODE=realistic`

## Output files

Write only these files under:

- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_multi_year_env_robustness_2026-04-16/`

Artifacts:

1. `manifest.json`
2. `robustness_summary.json`
3. `closeout.md`

No other artifact, cache, config, log, or results write is admissible.

## Manifest requirements

`manifest.json` must record at minimum:

- `base_sha`
- `executed_sha`
- `rebase_from_base`
- `discovery_year`
- `holdout_years`
- `seed_only_features`
- `frozen_profile_features`
- `dirty_path_verification`
- `containment.verdict`
- exact approved output file list

## Robustness summary requirements

`robustness_summary.json` must record at minimum:

- discovery-year seed thresholds / definitions
- discovery-year good/bad environment profiles
- year-by-year classification results for every holdout year
- counts for `good`, `bad`, and `ambiguous`
- mean `pnl_delta` and helpful/harmful shares per classification bucket
- an explicit overall robustness verdict that may be negative

## Closeout wording discipline

`closeout.md` must state clearly:

- whether the frozen `2024` separation keeps useful classification power across holdouts
- whether the evidence looks robust, mixed, or weak
- that this is observational replay research only
- that any signal is associative rather than causal
- that no runtime proposal or default promotion is authorized by this slice

If classification is contradictory or weak on most holdouts, the closeout must say so plainly instead of forcing a robust-driver claim.

## Exact execution command

Run from repository root:

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe tmp/current_atr_900_multi_year_env_robustness_20260416.py --symbol tBTCUSD --timeframe 3h --discovery-year 2024 --holdout-years 2017 2018 2019 2020 2021 2022 2023 2025 --output-dir results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_multi_year_env_robustness_2026-04-16 --manifest-out results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_multi_year_env_robustness_2026-04-16/manifest.json --summary-out results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_multi_year_env_robustness_2026-04-16/robustness_summary.json --closeout-out results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_multi_year_env_robustness_2026-04-16/closeout.md`

## Gates required

- `pre-commit run --files docs/decisions/current_atr_900_multi_year_env_robustness_packet_2026-04-16.md tmp/current_atr_900_multi_year_env_robustness_20260416.py`
- exact script execution command above with canonical env pins
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/backtest/test_compare_backtest_results.py::test_compare_ri_p1_off_parity_rows_pass_order_insensitive tests/backtest/test_compare_backtest_results.py::test_build_ri_p1_off_parity_artifact_required_fields`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/backtest/test_backtest_determinism_smoke.py::test_backtest_engine_is_deterministic_across_two_runs`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- proof from `manifest.json` that the unrelated dirty path stayed byte-identical
- proof from `manifest.json` that no create/modify/delete event occurred outside the approved output files

## Stop Conditions

- any need to edit `src/**`, `tests/**`, or `config/**`
- any overlap between `seed_only_features` and `frozen_profile_features`
- any use of holdout-year data to adjust thresholds or profiles
- any change to the unrelated dirty path listed above
- any uncontrolled artifact write outside the approved output root
- any determinism / invariance gate failure
- evidence that the frozen separation is too weak to support a robust-driver claim

## Done criteria

This slice is done only if all conditions are met:

1. packet + script stay within Scope IN/OUT
2. the exact gate stack passes
3. `2024` remains the only discovery year
4. every holdout year is evaluated with the same frozen profiles
5. `manifest.json` records base SHA vs executed SHA and dirty-path verification
6. `robustness_summary.json` gives year-by-year classification evidence
7. `closeout.md` states plainly whether the evidence is robust, mixed, or weak
8. no runtime/config/default recommendation is made

## Evidence discipline

- This slice is observational replay research only.
- Any discovered environment split is evidence of association, not causal proof.
- The goal is not to find a universal strategy.
- The goal is to identify whether the feature-space where the existing strategy has positive expectancy can still be recognized across years.
- If the answer is `no` or `mixed`, that result is still valid and must be reported plainly.
