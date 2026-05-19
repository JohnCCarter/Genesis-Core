# Optimizer validation missing-data partial reclassification packet

Date: 2026-05-19
Branch: `feature/risk-hardening-wave2`
Status: `decision-recorded / docs-only / non-authorizing`

This packet records one bounded partial reclassification only for baseline finding `#10`. It does not claim that all optimizer validation/promotion risk is solved. It records that the current promotion path is narrower and safer on this branch than the baseline row alone suggests: when validation returns a missing-data `error` or `skipped` payload, champion promotion is already blocked in the tracked runner flow. The honest residual is therefore broader process/readability drift or future bypass risk, not an unchanged `silent promotion despite validation data missing` reading for the current promotion path.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/risk-hardening-wave2`
- **Category:** `docs`
- **Risk:** `LOW` — why: docs-only partial reclassification backed by tracked code and focused test evidence
- **Required Path:** `Quick path / docs-only truthfulness correction`
- **Lane:** `Research-evidence` — why: this slice narrows interpretation of current optimizer promotion behavior without changing runtime/code/config surfaces
- **Objective:** record that the exact `#10` carry-forward reading should be narrowed because the current optimizer promotion path already refuses error/skipped validation results caused by missing data
- **Related artifacts:** `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`, `src/core/optimizer/runner_validation.py`, `src/core/optimizer/runner.py`, `src/core/optimizer/runner_trial_results.py`, `tests/utils/test_optimizer_runner.py`

### Scope

- **Scope IN:** this packet; one later-branch partial-reclassification note in the optimizer section of `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`
- **Scope OUT:** any optimizer code/test/config change; any claim that optimizer validation is fully hardened; any claim that all `Data not available` skip patterns across the repository are harmless; any promotion-policy redesign
- **Expected changed files:** `docs/decisions/governance/optimizer_validation_missing_data_partial_reclassification_packet_2026-05-19.md`, `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`

## Purpose

This slice answers one narrow question only:

- what is the honest current-branch reading of `#10` for the tracked optimizer promotion path after reading current runner code and the focused missing-data promotion-block test?

## Governing basis

### Observed

1. `src/core/optimizer/runner_validation.py` appends validation payloads, including `error` or `skipped` results, to `validation_results` rather than silently discarding them.
2. `src/core/optimizer/runner.py` prefers `validation_results` over explore results for champion promotion when validation ran.
3. `src/core/optimizer/runner_trial_results.py::_candidate_from_result()` rejects any result carrying `error` or `skipped`, so such validation payloads do not become promotion candidates.
4. `tests/utils/test_optimizer_runner.py::test_run_optimizer_validation_missing_data_blocks_promotion` passes on current branch-visible code and asserts that missing-data validation payloads prevent `write_champion()` from being called.
5. The baseline `#10` row still reads as if the current promotion path could silently skip validation-on-missing-data without blocking promotion.

### Inferred

- the exact current promotion-path reading is narrower than `missing validation data can silently pass through unchanged`
- the honest residual risk is about broader process drift, future bypass paths, or other skip contexts — not the specific tracked promotion path proved by the focused test
- a partial reclassification note is smaller and truer than either declaring `#10` closed or opening new optimizer code work without a fresh bug

### Unverified

- whether every future optimizer promotion entry point would preserve the same guardrails
- whether non-promotion reporting surfaces could still under-signal missing validation data
- whether a later broader optimizer audit should tighten missing-data semantics further

## Bottom line

The tracked optimizer promotion path already blocks promotion when validation returns missing-data `error` or `skipped` payloads. The honest current residual for `#10` is therefore narrower than the baseline row suggests: keep concern on future bypass/process drift, not on an unchanged silent-promotion reading for the current code path.
