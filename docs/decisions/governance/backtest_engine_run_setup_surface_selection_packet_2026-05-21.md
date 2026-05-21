# Backtest engine run-setup surface selection packet

Date: 2026-05-21
Branch: `feature/risk-hardening-wave3`
Status: `decision-recorded / docs-only / non-authorizing`

This packet records the next fresh current-branch `#15` surface after the already-landed
`_build_results()` extraction. It does not authorize source changes, approve broader
`engine.py` modularization, or reopen the old worktree-split story as if it were still the live
carrier for `#15` on this branch.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via `feature/* -> RESEARCH`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice selects one future `#15` surface only and changes no runtime,
  tests, cache semantics, exit behavior, or governance precedence
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why: this slice selects one exact next hot-file surface without
  beginning backtest runtime work
- **Skill usage:** `none required` — bounded docs-only current-surface selection
- **Objective:** replace vague family-level `#15` carry-forward language with one exact next
  current-branch surface after the already-landed `_build_results()` seam
- **Related artifacts:**
  `docs/decisions/governance/backtest_engine_build_results_seam_packet_2026-05-19.md`,
  `handoff.md`, `src/core/backtest/engine.py`, `tests/backtest/test_backtest_engine.py`,
  `tests/integration/test_golden_trace_runtime_semantics.py`,
  `tests/integration/test_scrub_volatile_and_config_fingerprint.py`

### Scope

- **Scope IN:** this packet; one later-branch note in
  `docs/decisions/governance/backtest_engine_build_results_seam_packet_2026-05-19.md`; one live
  note refresh in `handoff.md`
- **Scope OUT:** all edits under `src/**`, `tests/**`, `scripts/**`, `config/**`, `results/**`,
  and `artifacts/**`; any new `#15` implementation; any claim that the broader `#15` family is
  closed; any reopening of the old worktree-engine-split story as branch-current evidence
- **Expected changed files:**
  `docs/decisions/governance/backtest_engine_run_setup_surface_selection_packet_2026-05-21.md`,
  `docs/decisions/governance/backtest_engine_build_results_seam_packet_2026-05-19.md`,
  `handoff.md`
- **Max files touched:** `3`

### Gates required

For this docs-only slice:

- targeted docs validation for the changed markdown files
- manual wording audit that the slice remains surface-selection only and non-authorizing
- manual wording audit that `_build_results()` is not re-opened as the current candidate
- manual wording audit that no direct trade-behavior or exit-behavior surface is implicitly
  approved

## Purpose

This packet answers one narrow question only:

- after `_build_results()` was extracted, what is the next honest fresh `#15` surface on the
  current branch?

## What changed in this slice

- one new packet selects the next fresh `#15` surface after the already-landed `_build_results()`
  seam
- the historical `_build_results()` packet now points future readers away from retelling that seam
  as still open
- `handoff.md` is refreshed so wave3 no longer leaves `#15` hanging as a vague hot-file family

## What did not change

- no backtest runtime code changed
- no tests changed
- no `engine.py` behavior changed
- no new helper module was introduced
- no engine split was approved

## Governing basis

### Observed

1. `docs/decisions/governance/backtest_engine_build_results_seam_packet_2026-05-19.md` now carries
   a later-branch note saying the exact `_build_results()` candidate has already been implemented on
   `feature/risk-hardening-wave3` via `src/core/backtest/engine_results.py`.
2. Current `src/core/backtest/engine.py` no longer keeps result assembly or persisted precompute-spec
   ownership in the same place they historically occupied; those two bounded internal separations
   already reduced some `engine.py` blast radius.
3. The current `BacktestEngine.run(...)` body still contains one concentrated pre-loop
   setup/config-preparation block before the replay loop starts, including:
   - engine-state reset
   - defensive config copy
   - champion merge resolution
   - explicit non-default `data_source_policy` propagation
   - HTF exit-engine reinitialization from merged config
   - `precomputed_features` injection
   - effective-config fingerprint recording
4. Existing tests already pin key contract surfaces inside that block, including
   `tests/backtest/test_backtest_engine.py` for config isolation / data-source policy behavior and
   integration tests for effective-config fingerprint stability.
5. Higher-sensitivity exit/evaluation surfaces remain deeper in `run()` or in
   `_check_htf_exit_conditions(...)`; those paths still sit closer to direct trade behavior than the
   pre-loop setup block does.

### Inferred

- the next honest `#15` surface is no longer `_build_results()` and no longer the old worktree split
  story; it is the pre-loop administrative setup/config-preparation block inside `run()`
- this is a truer next hot-file surface than the exit paths because it remains internal and can be
  described without reopening direct per-bar trade logic as the default next move
- selecting this surface keeps `#15` anchored to current branch reality rather than to historical
  split aspirations

### Unverified

- whether a later code slice is needed at all
- whether a later implementation should use an internal helper, sidecar module, or stay inside
  `engine.py`
- the exact minimal future test subset beyond the already-known config-fingerprint and
  data-source-policy proofs

## Surface selection conclusion

The next fresh current-branch `#15` surface is:

- the **pre-loop run-setup/config-preparation block inside `BacktestEngine.run(...)`**, not the
  already-landed `_build_results()` seam and not a revived whole-file split story

This selection does **not** approve code work. It records the next honest surface only.

## Bottom line

On wave3, `#15` should no longer be retold as “maybe the old engine split” or “still `_build_results()`.”
The next fresh surface, if the family reopens later, is the internal run-setup/config-preparation
block at the top of `BacktestEngine.run(...)`.
