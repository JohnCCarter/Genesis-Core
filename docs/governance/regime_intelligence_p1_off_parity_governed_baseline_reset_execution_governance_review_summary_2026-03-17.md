# RI P1 OFF parity governed baseline reset — governance review summary

Date: 2026-03-17
Slice: `feature/regime-intelligence-cutover-analysis-v1`
Status: `review-summary / ready_for_governance_review / execution not approved by this summary`

## Purpose of the governed baseline reset

This review summary supports formal governance review of the prepared execution-approval candidate packet for:

- `governed baseline reset via parity rerun`
- under frozen spec `ri_p1_off_parity_v1`

The goal of this path is to allow governance to evaluate a clean, explicitly reviewed parity rerun path when historical sign-off evidence cannot be relied on from tracked repository state.

This summary does **not** approve execution and does **not** start the rerun.

## Pinned provenance

The candidate rerun remains pinned to the reviewed execution provenance:

- branch: `feature/regime-intelligence-cutover-analysis-v1`
- short SHA: `1c2f38ad`
- full SHA: `1c2f38ad88723034b819b7844c69d138a7702086`
- working tree requirement: clean

If a future rerun is proposed from any successor SHA, fresh governance review must re-pin and re-approve that SHA before execution may be considered.

## Canonical artifact path

The canonical parity artifact path remains locked to:

- `results/evaluation/ri_p1_off_parity_v1_<run_id>.json`

The canonical baseline reference path remains reserved as:

- `results/evaluation/ri_p1_off_parity_v1_baseline.json`

That reserved baseline reference path is **not** approved, promoted, or materialized by this summary.

## Required artifact metadata

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

## Gate bundle required for sign-off

A future `parity_verdict=PASS` may count as governance sign-off only if all of the following are also green:

- repo hygiene / smoke:
  - file-scoped or tranche-appropriate `pre-commit` / lint
  - `python -m pytest -q tests/governance/test_import_smoke_backtest_optuna.py`
- determinism / invariance:
  - `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
  - `python -m pytest -q tests/utils/test_features_asof_cache.py tests/utils/test_features_asof_cache_key_deterministic.py`
  - `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- evaluate/source contract checks:
  - `python -m pytest -q tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_shadow_error_rate_contract`
  - `python -m pytest -q tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_source_invariant_contract`
- comparator / decision-row contract checks:
  - `python -m pytest -q tests/backtest/test_compare_backtest_results.py::test_compare_ri_p1_off_parity_rows_pass_order_insensitive`
  - `python -m pytest -q tests/backtest/test_compare_backtest_results.py::test_build_ri_p1_off_parity_artifact_required_fields`
  - `python -m pytest -q tests/backtest/test_run_backtest_decision_rows.py::test_write_decision_rows_json_and_ndjson`
- skill checks:
  - `python scripts/run_skill.py --skill ri_off_parity_artifact_check --manifest dev`
  - `python scripts/run_skill.py --skill feature_parity_check --manifest dev --dry-run`
  - `python scripts/run_skill.py --skill config_authority_lifecycle_check --manifest dev --dry-run`
- provenance and execution discipline:
  - clean working tree
  - exact pinned SHA
  - explicit future baseline classification
  - explicit `runtime_config_source`
  - reviewable candidate/baseline provenance bundle
  - no runtime-default drift
- parity outcome discipline:
  - `parity_verdict=PASS`
  - all mismatch counts equal `0`

## Explicit reminder

Execution is **not** approved by this summary.

No rerun has been started by this summary.
The next step is formal governance review of the prepared execution-approval candidate packet.
