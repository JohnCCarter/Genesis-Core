# RI P1 OFF parity governed rerun definition

Date: 2026-03-17
Slice: `feature/regime-intelligence-cutover-analysis-v1`
Status: `prep-only / execution not yet approved`

## Purpose

This document defines the next slice: `RI P1 OFF parity governed rerun`.

The purpose of that future slice is to restore a reproducible, repo-verifiable sign-off evidence chain for P1 OFF-mode parity under the frozen spec `ri_p1_off_parity_v1`.

This document does **not** execute the rerun.

## Governing principles

- no runtime changes
- no default-cutover
- no champion changes
- frozen spec remains `ri_p1_off_parity_v1`
- canonical parity artifact remains `results/evaluation/ri_p1_off_parity_v1_<run_id>.json`
- supplemental audit evidence may be retained under `docs/audit/refactor/regime_intelligence/evidence/...`
- supplemental evidence must never redefine or replace the canonical artifact

## Explicit artifact definitions for the future execution slice

### 1. Canonical parity artifact

- Path: `results/evaluation/ri_p1_off_parity_v1_<run_id>.json`
- Role: normative machine-readable PASS/FAIL artifact
- Required metadata:
  - `window_spec_id=ri_p1_off_parity_v1`
  - `run_id`
  - `git_sha`
  - `mode=OFF`
  - `symbols`
  - `timeframes`
  - `start_utc`
  - `end_utc`
  - `baseline_artifact_ref`
  - `parity_verdict`
  - mismatch counts
  - `size_tolerance`

### 2. Explicit baseline artifact

- Canonical reference path: `results/evaluation/ri_p1_off_parity_v1_baseline.json`
- Required meaning: the approved baseline artifact referenced by the canonical parity artifact
- Baseline must be classified as one of:
  - recovered approved baseline, or
  - newly approved baseline under explicit governance approval
- Required supplemental retained copy for reviewability:
  - `docs/audit/refactor/regime_intelligence/evidence/ri_p1_off_parity_v1_baseline_rows_<run_id>.json`

### 3. Explicit candidate artifact

- Required supplemental retained copy:
  - `docs/audit/refactor/regime_intelligence/evidence/ri_p1_off_parity_v1_candidate_rows_<run_id>.json`
- Role: machine-readable candidate decision-row input used for the parity comparison
- Candidate must be generated from a reviewable command/path under the frozen rerun contract

### 4. Supplemental rerun manifest

- Path: `docs/audit/refactor/regime_intelligence/evidence/ri_p1_off_parity_v1_manifest_<run_id>.json`
- Role: governance-support manifest linking canonical and supplemental evidence
- Required fields:
  - `run_id`
  - `git_sha`
  - `branch`
  - `executed_at_utc`
  - `window_spec_id`
  - `symbol`
  - `timeframe`
  - `start_utc`
  - `end_utc`
  - `runtime_config_source`
  - `compare_tool_path`
  - `baseline_artifact_ref`
  - `baseline_sha256`
  - `candidate_sha256`
  - `canonical_artifact_path`
  - `canonical_artifact_sha256`
  - `supplemental_role_note`

## Reviewable input and window requirements

The future execution slice must define all of the following explicitly before running:

- exact symbol/timeframe/window
- exact baseline approval anchor
- exact candidate generation path/command
- exact runtime config source
- exact compare-tool path
- exact branch + `git_sha`
- explicit environment freeze note including `GENESIS_FAST_HASH=0`
- exact provenance for baseline and candidate inputs

## Required verification bundle for the future execution slice

The future governed rerun must include, at minimum:

- determinism replay
- feature cache invariance
- pipeline invariant
- relevant evaluate/source invariant selectors
- `ri_off_parity_artifact_check`
- any comparator/decision-row selectors required to prove the retained inputs match the frozen rerun contract

## Stop conditions for the future execution slice

Stop immediately and re-review if any of the following occur:

1. approved baseline provenance cannot be identified or verified
2. execution requires changes in `src/**`, `src/core/config/**`, `config/runtime.json`, or `config/strategy/champions/**`
3. evidence is retained only under ignored paths such as `logs/**`, `tmp/**`, or `artifacts/**`
4. canonical artifact and supplemental retained evidence do not SHA-match where the manifest says they should
5. symbol/timeframe/window/config/env drift from frozen `ri_p1_off_parity_v1` is detected
6. comparator contract or tool path drifts from the defined rerun contract
7. any mismatch count is non-zero or any required gate fails

## Readiness rule for execution approval

Execution may be proposed only when all of the following are true:

- baseline provenance is explicit and reviewable
- candidate generation path is explicit and reviewable
- canonical and supplemental artifact roles are explicit
- repo-verifiable retention plan exists for all required evidence
- gate bundle is fully named
- no runtime/default/champion scope expansion is required

## Current conclusion

The lineage analysis slice established that **sign-off evidence cannot be reproduced from tracked repository state**.

Therefore the next correct step is a **governed parity rerun**, not runtime remediation.

This document prepares that rerun contract so execution can be approved or rejected on a clean governance basis.
