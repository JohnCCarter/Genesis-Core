# RI P1 OFF parity governed baseline reset — execution runbook

Date: 2026-03-17
Slice: `feature/regime-intelligence-cutover-analysis-v1`
Status: `docs-only / prep-only / execution not approved by this slice`

## Purpose

This document defines the operational runbook for the future rerun selected by governance posture:

- `governed baseline reset via parity rerun`
- under frozen spec `ri_p1_off_parity_v1`

This document is intentionally operationally concrete.

It still does **not** start the rerun.
It does **not** grant baseline approval.
It does **not** grant execution approval.

## Reviewed execution provenance

The future rerun is pinned to the currently reviewed execution provenance:

- branch: `feature/regime-intelligence-cutover-analysis-v1`
- short SHA: `1c2f38ad`
- full SHA: `1c2f38ad88723034b819b7844c69d138a7702086`
- working tree requirement: clean

Future rerun execution may be proposed only from that exact reviewed SHA on a clean working tree.

If execution is later proposed from any successor SHA, the rerun must stop and wait for a separate execution-approval packet that re-pins and re-reviews that successor SHA.

## How the frozen spec materializes at execution time

`window_spec_id=ri_p1_off_parity_v1` is a governance-defined frozen execution identity.

It does not come from a CLI flag on `scripts/run/run_backtest.py`.

Instead, the future rerun materializes the frozen spec in two stages:

1. the backtest step materializes the frozen execution tuple:
   - `symbol=tTESTBTC:TESTUSD`
   - `timeframe=1h`
   - `start=2025-01-01`
   - `end=2025-01-31`
   - optional reviewed `--config-file`
2. the compare step materializes `window_spec_id=ri_p1_off_parity_v1` into the canonical parity artifact together with `run_id`, `git_sha`, `baseline_artifact_ref`, mismatch counts, and verdict

## Frozen execution tuple

The future rerun must preserve all of the following exactly:

- `window_spec_id=ri_p1_off_parity_v1`
- `mode=OFF`
- `symbol=tTESTBTC:TESTUSD`
- `timeframe=1h`
- `start_utc=2025-01-01T00:00:00Z`
- `end_utc=2025-01-31T23:59:59Z`
- `GENESIS_FAST_HASH=0`
- `size_tolerance=1e-12`
- canonical artifact path: `results/evaluation/ri_p1_off_parity_v1_<run_id>.json`
- canonical baseline reference path: `results/evaluation/ri_p1_off_parity_v1_baseline.json`

`results/evaluation/ri_p1_off_parity_v1_baseline.json` remains a reserved canonical reference path only.

This runbook does not treat it as a currently verified tracked baseline artifact.

## Baseline artifact: create or classify

The future execution packet must handle baseline semantics explicitly, not implicitly.

### What must be classified

The future baseline must be recorded as:

- `newly approved baseline under explicit governance approval`

That is a future governance classification path.

It is **not** granted by this runbook.

### What the rerun may produce

The future rerun may produce:

- retained baseline rows evidence
- candidate rows evidence
- canonical parity artifact
- supplemental manifest

A future parity `PASS` does **not** by itself create, promote, or approve the canonical baseline path `results/evaluation/ri_p1_off_parity_v1_baseline.json`.

Any promotion or approval of that canonical baseline path remains a separate later governance act.

## Candidate rows generation

The future rerun must generate candidate rows via `scripts/run/run_backtest.py` using the reviewed CLI surface.

Required reviewed command shape:

- `--symbol tTESTBTC:TESTUSD`
- `--timeframe 1h`
- `--start 2025-01-01`
- `--end 2025-01-31`
- `--decision-rows-out docs/audit/refactor/regime_intelligence/evidence/ri_p1_off_parity_v1_candidate_rows_<run_id>.json`
- `--decision-rows-format json`
- optional reviewed `--config-file <path>`

Required provenance captured from this step:

- `candidate_rows_path`
- `candidate_sha256`
- `candidate_generation_command`
- `runtime_config_source`

`runtime_config_source` must always be written.

If `--config-file` is omitted, `runtime_config_source` must explicitly record reviewed default runtime authority usage; it may not be omitted or left blank.

## Canonical artifact output path

The exact canonical artifact output path for the future rerun is:

- `results/evaluation/ri_p1_off_parity_v1_<run_id>.json`

The compare tool may be called with explicit `--artifact-out` for that exact path, or may rely on its built-in default, which resolves to the same canonical path shape.

## Comparator step and required command surface

The future rerun must generate the canonical artifact with `tools/compare_backtest_results.py` using the reviewed comparator surface:

- positional baseline rows input path
- positional candidate rows input path
- `--ri-off-parity`
- `--run-id <run_id>`
- `--git-sha 1c2f38ad88723034b819b7844c69d138a7702086`
- `--symbols tTESTBTC:TESTUSD`
- `--timeframes 1h`
- `--start-utc 2025-01-01T00:00:00Z`
- `--end-utc 2025-01-31T23:59:59Z`
- `--baseline-artifact-ref results/evaluation/ri_p1_off_parity_v1_baseline.json`
- optional `--artifact-out results/evaluation/ri_p1_off_parity_v1_<run_id>.json`
- optional `--size-tolerance 1e-12`

## Metadata fields that must be written to the canonical artifact

The future canonical artifact must contain at least the following fields:

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
- `action_mismatch_count`
- `reason_mismatch_count`
- `size_mismatch_count`
- `added_row_count`
- `missing_row_count`
- `size_tolerance`

## Evidence outputs the future rerun must retain

The future execution packet must retain all of the following:

- baseline rows evidence:
  - `docs/audit/refactor/regime_intelligence/evidence/ri_p1_off_parity_v1_baseline_rows_<run_id>.json`
- candidate rows evidence:
  - `docs/audit/refactor/regime_intelligence/evidence/ri_p1_off_parity_v1_candidate_rows_<run_id>.json`
- canonical parity artifact:
  - `results/evaluation/ri_p1_off_parity_v1_<run_id>.json`
- supplemental manifest:
  - `docs/audit/refactor/regime_intelligence/evidence/ri_p1_off_parity_v1_manifest_<run_id>.json`

## Gates that must pass before PASS counts as governance sign-off

A future `parity_verdict=PASS` may count as governance sign-off only if all of the following are also true:

- repo hygiene / smoke passes:
  - file-scoped or tranche-appropriate `pre-commit` / lint
  - `python -m pytest -q tests/governance/test_import_smoke_backtest_optuna.py`
- determinism / invariance passes:
  - `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
  - `python -m pytest -q tests/utils/test_features_asof_cache.py tests/utils/test_features_asof_cache_key_deterministic.py`
  - `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- evaluate/source contract checks pass:
  - `python -m pytest -q tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_shadow_error_rate_contract`
  - `python -m pytest -q tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_source_invariant_contract`
- comparator / decision-row contract checks pass:
  - `python -m pytest -q tests/backtest/test_compare_backtest_results.py::test_compare_ri_p1_off_parity_rows_pass_order_insensitive`
  - `python -m pytest -q tests/backtest/test_compare_backtest_results.py::test_build_ri_p1_off_parity_artifact_required_fields`
  - `python -m pytest -q tests/backtest/test_run_backtest_decision_rows.py::test_write_decision_rows_json_and_ndjson`
- skill checks pass:
  - `python scripts/run_skill.py --skill ri_off_parity_artifact_check --manifest dev`
  - `python scripts/run_skill.py --skill feature_parity_check --manifest dev --dry-run`
  - `python scripts/run_skill.py --skill config_authority_lifecycle_check --manifest dev --dry-run`
- provenance remains reviewable:
  - clean working tree
  - pinned reviewed SHA
  - explicit baseline classification
  - explicit `runtime_config_source`
  - SHA256-linked baseline, candidate, canonical artifact, and manifest
- parity artifact outcome remains clean:
  - `parity_verdict=PASS`
  - all mismatch counts are `0`
  - no runtime-default drift is introduced

## Stop conditions for the future execution packet

Stop and return for fresh governance review if any of the following occur:

- working tree is not clean
- proposed execution SHA differs from `1c2f38ad88723034b819b7844c69d138a7702086`
- frozen spec drifts
- compare-command surface drifts
- `runtime_config_source` cannot be stated explicitly
- baseline approval or promotion would occur implicitly as a side effect of rerun PASS
- evidence relied on for provenance exists only in ignored or untracked local state
- March sign-off text or ignored logs are proposed as recovered baseline provenance
- synthetic `ri_p1_off_parity_v1_ri-20260303-003.json` is proposed as baseline, candidate, or sign-off evidence
- runtime/config/champion/default-authority changes are required

## Current conclusion

The repository now has a docs-only execution runbook for the selected fallback path.

That means the next future step can be narrower and cleaner:

- prepare a separate execution-approval packet
- keep execution blocked until that packet explicitly approves the pinned rerun

No rerun has been started by this slice.
