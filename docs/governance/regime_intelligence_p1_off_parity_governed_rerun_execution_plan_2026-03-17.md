# RI P1 OFF parity governed rerun — execution plan

Date: 2026-03-17
Slice: `feature/regime-intelligence-cutover-analysis-v1`
Status: `prep-only / execution not yet approved`

## Purpose

This document defines the exact future execution flow for `RI P1 OFF parity governed rerun`.

It prepares a reviewable execution packet that can later be governance-reviewed before any rerun is actually run.

This document does **not** execute the rerun.

## Planned frozen execution inputs

These are the **planned frozen execution inputs derived from the current repo-visible contract/example surface**.

| Field                   | Planned value                                          |
| ----------------------- | ------------------------------------------------------ |
| `window_spec_id`        | `ri_p1_off_parity_v1`                                  |
| `mode`                  | `OFF`                                                  |
| `symbol`                | `tTESTBTC:TESTUSD`                                     |
| `timeframe`             | `1h`                                                   |
| `start_utc`             | `2025-01-01T00:00:00Z`                                 |
| `end_utc`               | `2025-01-31T23:59:59Z`                                 |
| `baseline_artifact_ref` | `results/evaluation/ri_p1_off_parity_v1_baseline.json` |
| `GENESIS_FAST_HASH`     | `0`                                                    |
| `size_tolerance`        | `1e-12`                                                |

## Hard rule on baseline semantics

The planned target window above does **not** prove that an approved baseline already exists.

Before execution may begin, the future execution slice must classify the baseline as exactly one of:

- `recovered approved baseline`
- `newly approved baseline under explicit governance approval`

If the baseline cannot be classified that way, execution must STOP.

`results/evaluation/ri_p1_off_parity_v1_baseline.json` is therefore treated here as a **reserved canonical reference path**, not as a currently verified tracked artifact.

## Exact future execution flow

### Step 1 — freeze execution packet metadata

The future execution slice must first record:

- `run_id`
- `git_sha`
- `branch`
- `executed_at_utc`
- `window_spec_id`
- `mode`
- `symbol`
- `timeframe`
- `start_utc`
- `end_utc`
- `runtime_config_source`
- `compare_tool_path`
- `decision_rows_format=json`
- `GENESIS_FAST_HASH=0`

### Step 2 — verify and classify baseline provenance

The future execution slice must verify the baseline provenance anchor before generating any parity verdict.

Required outputs from this step:

- baseline classification (`recovered approved baseline` or `newly approved baseline under explicit governance approval`)
- baseline approval anchor
- `baseline_artifact_ref`
- `baseline_rows_path`
- `baseline_sha256`

### Step 3 — materialize/recover baseline rows evidence

The future execution slice must retain machine-readable baseline rows evidence at:

- `docs/audit/refactor/regime_intelligence/evidence/ri_p1_off_parity_v1_baseline_rows_<run_id>.json`

This retained evidence is supplemental governance evidence only. It must hash-link to the approved baseline used by the canonical parity comparison.

### Step 4 — generate candidate decision rows

The future execution slice must generate candidate decision rows using the repo's decision-row capture path in `scripts/run/run_backtest.py`.

Planned command shape:

- use `--symbol tTESTBTC:TESTUSD`
- use `--timeframe 1h`
- use `--start 2025-01-01`
- use `--end 2025-01-31`
- use `--decision-rows-out docs/audit/refactor/regime_intelligence/evidence/ri_p1_off_parity_v1_candidate_rows_<run_id>.json`
- use `--decision-rows-format json`
- record any `--config-file` value as `runtime_config_source`

Required outputs from this step:

- `candidate_rows_path`
- `candidate_sha256`
- `candidate_generation_command`

### Step 5 — generate canonical parity artifact

The future execution slice must compare baseline rows and candidate rows using `tools/compare_backtest_results.py --ri-off-parity`.

Planned canonical output:

- `results/evaluation/ri_p1_off_parity_v1_<run_id>.json`

Required outputs from this step:

- `canonical_artifact_path`
- `canonical_artifact_sha256`
- `compare_command`
- canonical artifact fields required by the DoD:
  - `window_spec_id`
  - `run_id`
  - `git_sha`
  - `mode`
  - `symbols`
  - `timeframes`
  - `start_utc`
  - `end_utc`
  - `baseline_artifact_ref`
  - `parity_verdict`
  - mismatch counts
  - `size_tolerance`

### Step 6 — write supplemental rerun manifest

The future execution slice must write:

- `docs/audit/refactor/regime_intelligence/evidence/ri_p1_off_parity_v1_manifest_<run_id>.json`

Required fields in the manifest:

- `run_id`
- `git_sha`
- `branch`
- `executed_at_utc`
- `window_spec_id`
- `mode`
- `symbol`
- `timeframe`
- `start_utc`
- `end_utc`
- `runtime_config_source`
- `compare_tool_path`
- `baseline_artifact_ref`
- `baseline_rows_path`
- `candidate_rows_path`
- `baseline_sha256`
- `candidate_sha256`
- `canonical_artifact_path`
- `canonical_artifact_sha256`
- `size_tolerance`
- `decision_rows_format`
- `candidate_generation_command`
- `compare_command`
- `supplemental_role_note`

### Step 7 — run required gates

Before PASS may count as sign-off, the future execution slice must run all of the following:

#### Repo hygiene / smoke

- file-scoped or tranche-appropriate `pre-commit` / lint
- `python -m pytest -q tests/governance/test_import_smoke_backtest_optuna.py`

#### Determinism / invariance

- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/utils/test_features_asof_cache.py tests/utils/test_features_asof_cache_key_deterministic.py`
- `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

#### Evaluate/source contract checks

- `python -m pytest -q tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_shadow_error_rate_contract`
- `python -m pytest -q tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_source_invariant_contract`

#### Comparator / decision-row contract checks

- `python -m pytest -q tests/backtest/test_compare_backtest_results.py::test_compare_ri_p1_off_parity_rows_pass_order_insensitive`
- `python -m pytest -q tests/backtest/test_compare_backtest_results.py::test_build_ri_p1_off_parity_artifact_required_fields`
- `python -m pytest -q tests/backtest/test_run_backtest_decision_rows.py::test_write_decision_rows_json_and_ndjson`

#### Skill checks

- `python scripts/run_skill.py --skill ri_off_parity_artifact_check --manifest dev`
- `python scripts/run_skill.py --skill feature_parity_check --manifest dev --dry-run`
- `python scripts/run_skill.py --skill config_authority_lifecycle_check --manifest dev --dry-run`

### Step 8 — sign-off gate

PASS may count as governance sign-off only if all of the following are true:

- parity artifact verdict is `PASS`
- all mismatch counts are `0`
- all required gates are green
- baseline provenance classification is valid
- canonical and supplemental evidence hash-link correctly
- no runtime-default drift is introduced

## Stop conditions for the future execution slice

Stop immediately and return for fresh governance review if any of the following occur:

1. baseline provenance cannot be verified
2. baseline cannot be classified as `recovered approved baseline` or `newly approved baseline under explicit governance approval`
3. execution requires any change in `src/**`, `src/core/config/**`, `config/runtime.json`, or `config/strategy/champions/**`
4. any evidence chain would live only under ignored paths such as `logs/**`, `tmp/**`, or `artifacts/**`
5. canonical and supplemental evidence fail SHA256 linkage
6. symbol/timeframe/window/config/env drift from the planned frozen target is detected
7. comparator contract/tool path drift is detected
8. any mismatch count is non-zero
9. any required gate fails
10. the repo-visible synthetic fixture `ri_p1_off_parity_v1_ri-20260303-003.json` is proposed as sign-off evidence, baseline, or candidate input

## Current conclusion

This execution plan is ready for governance review.

It defines a future rerun path that is:

- frozen against `ri_p1_off_parity_v1`
- explicit about baseline/candidate handling
- explicit about canonical vs supplemental artifacts
- explicit about metadata and gates
- still preparation only

No rerun has been executed by this slice.
