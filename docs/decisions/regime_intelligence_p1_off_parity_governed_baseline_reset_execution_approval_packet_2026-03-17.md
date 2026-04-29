# RI P1 OFF parity governed baseline reset — execution approval candidate packet

Date: 2026-03-17
Slice: `feature/regime-intelligence-cutover-analysis-v1`
Status: `approval-candidate / ready_for_governance_review / execution not approved by this slice`

## Purpose

This document prepares the reviewable execution-approval candidate packet for:

- `governed baseline reset via parity rerun`
- under frozen spec `ri_p1_off_parity_v1`

This packet is meant to be reviewed by governance before any rerun starts.

Readiness state for this slice: `ready_for_governance_review`.

It does **not** itself approve execution.
It does **not** itself enact baseline approval.
It does **not** start the rerun.

## Pinned provenance inherited from the runbook

The future rerun requested by this packet is pinned to:

- branch: `feature/regime-intelligence-cutover-analysis-v1`
- short SHA: `1c2f38ad`
- full SHA: `1c2f38ad88723034b819b7844c69d138a7702086`
- working tree requirement: clean

If future execution is proposed from any successor SHA, this packet is no longer sufficient and a fresh governance packet must re-pin and re-review that SHA before rerun start is considered.

## Requested future baseline classification

Allowed / requested future baseline classification for this approval path:

- `newly approved baseline under explicit governance approval`

This wording is future-scoped deliberately.

It means this is the baseline classification being requested for governance review.

It does **not** mean that the baseline is already approved in this slice.
It does **not** promote `results/evaluation/ri_p1_off_parity_v1_baseline.json` in this slice.
It does **not** make a future `PASS` auto-promote or auto-approve that canonical baseline path.

## Candidate / baseline provenance required for approval review

Before a later rerun may be treated as eligible under this packet, the future execution packet must present a reviewable provenance bundle that includes at least:

- `baseline_artifact_ref`
- `baseline_rows_path`
- `baseline_sha256`
- `baseline_approval_anchor`
- `candidate_rows_path`
- `candidate_sha256`
- `candidate_generation_command`
- `runtime_config_source`
- `compare_tool_path`
- `compare_command`
- `canonical_artifact_path`
- `decision_rows_format=json`
- pinned `git_sha`
- `window_spec_id=ri_p1_off_parity_v1`
- `symbol=tTESTBTC:TESTUSD`
- `timeframe=1h`
- `start_utc=2025-01-01T00:00:00Z`
- `end_utc=2025-01-31T23:59:59Z`

This slice defines those items as approval requirements only.

It does not create the provenance evidence, write the evidence files, or mark the provenance as already verified.

## Canonical artifact path and metadata contract

The canonical artifact path remains locked to:

- `results/evaluation/ri_p1_off_parity_v1_<run_id>.json`

The canonical baseline reference path remains:

- `results/evaluation/ri_p1_off_parity_v1_baseline.json`

`results/evaluation/ri_p1_off_parity_v1_baseline.json` remains a reserved canonical reference path only.

This packet does not treat that path as an already verified tracked artifact.

The future canonical artifact must contain at least the following metadata fields:

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

Those requirements are defined in this slice, not fulfilled by this slice.

## Full gate bundle that must pass before PASS counts as governance sign-off

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

## What this packet does not do

This packet does **not**:

- approve execution merely by existing
- approve or promote the canonical baseline path merely by existing
- write evidence outputs under `results/**` or `docs/audit/refactor/regime_intelligence/evidence/**`
- certify that candidate/baseline provenance already exists
- certify that gates have already passed
- start the rerun

## Stop conditions for governance review of this packet

Stop and return for fresh governance review if any of the following occur:

- wording drifts into implying execution approval by packet existence
- wording drifts into implying that baseline approval has already been enacted
- the requested future baseline classification is written as an already-approved present-tense fact
- branch or SHA drift from the pinned runbook provenance is introduced
- canonical artifact path or metadata contract drifts
- gate bundle or named skill checks drift
- a future `PASS` is described as auto-promoting `results/evaluation/ri_p1_off_parity_v1_baseline.json`
- provenance is described as verified while depending only on ignored or untracked local state
- runtime/config/champion/default-authority changes are required

## Current conclusion

The repository now has a separate execution-approval candidate packet prepared and marked `ready_for_governance_review`.

That means the next step can be the intended one:

- governance reviews this approval candidate
- only after that review may rerun start be considered

Execution remains blocked by this slice.
No rerun has been started by this slice.
