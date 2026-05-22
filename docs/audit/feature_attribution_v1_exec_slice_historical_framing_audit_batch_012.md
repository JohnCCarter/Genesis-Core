# Batch 012 Feature Attribution v1 exec-slice historical framing audit

Date: 2026-05-22
Mode: `RESEARCH`
Observed branch/worktree: `feature/genesis-topology-lifecycle-authority-map`
Status: `read-only status/framing audit / non-authorizing / docs-only / no behavior change`

> This file is a bounded audit for the `Feature Attribution v1` `exec_slice*` packet family.
> It does **not** reopen execution, prove that any referenced run artifact was produced, or touch the
> adjacent implementation packets by itself.

## Scope boundary

Primary candidates in scope:

- `docs/decisions/feature_attribution/v1/feature_attribution_v1_exec_slice1_min_edge_identification_packet_2026-03-31.md`
- `docs/decisions/feature_attribution/v1/feature_attribution_v1_exec_slice2_hysteresis_identification_packet_2026-03-31.md`
- `docs/decisions/feature_attribution/v1/feature_attribution_v1_exec_slice3_cooldown_identification_packet_2026-03-31.md`
- `docs/decisions/feature_attribution/v1/feature_attribution_v1_exec_slice4_base_entry_confidence_identification_packet_2026-03-31.md`
- `docs/decisions/feature_attribution/v1/feature_attribution_v1_exec_slice5_htf_block_identification_packet_2026-03-31.md`

Supporting evidence surfaces in scope:

- `docs/audit/feature_attribution_v1_phase_packet_historical_framing_audit_batch_011.md`
- `docs/decisions/feature_attribution/v1/feature_attribution_v1_phase0_scope_freeze_packet_2026-03-31.md`
- `plan/feature_attribution_post_phase14_reactivation_roadmap_2026-04-02.md`
- `plan/genesis_driver_identification_master_roadmap_2026-04-14.md`

Out of scope in this batch:

- editing any `results/research/feature_attribution_v1/**` artifact
- editing any `feature_attribution_v1_impl_slice*.md`
- editing `phase0` or the already-synced `phase1–phase9` packet chain
- editing either later plan anchor
- rewriting packet bodies, gates, expected changed files, or output contracts
- changing runtime, config, test, or script behavior
- editing `docs/CURRENT_AUTHORITY_INDEX.md`
- editing `docs/knowledge/DOCUMENTATION_PROVENANCE_LINEAGE_MAP.md`

## Method

Checked in this slice:

- full read of the five `exec_slice*` packet files
- read-only comparison against the already historicalized docs-only `phase1–phase9` packet chain
- read-only comparison against the locked `phase0` anchor and the later historical/closed plan
  anchors
- top-of-file status/current-use framing check for all five candidates
- skim-path wording check for `proposed / execution-slice / single-row only` drift

Machine-readable evidence artifact:

- `artifacts/diagnostics/batch012_feature_attribution_v1_exec_slice_framing_evidence.json`

## Observed

### Adjacent documentation already reads more historical than the execution packets

Observed supporting context:

- Batch 011 already historicalized the docs-only `phase1–phase9` packet chain
- `feature_attribution_v1_phase0_scope_freeze_packet_2026-03-31.md` already reads as a locked
  internal anchor rather than a proposed next step
- the later post-Phase-14 and Genesis-driver plan anchors are already historical/closed on the
  current branch

### The exec-slice packet tops still read like current run-ready next steps

Observed top status drift across the execution packet family:

- all five packets still begin with `Status: proposed / execution-slice / single-row only`

Observed skim-risk pattern:

- each packet opens as a future execution slice with `Category: obs`, `Required Path: Full`, and
  expected changed files under both docs and `results/research/feature_attribution_v1/**`
- without a top current-status note, later readers can over-read the packet as active execution
  guidance rather than historical packet provenance
- the stale effect is concentrated at the file tops; the bodies already contain the high-sensitivity
  historical contract details that should be preserved rather than rewritten in this slice

## Inferred

- the `exec_slice*` family should remain retained historical packet provenance rather than current
  branch run-ready guidance
- the safe correction is a **top-framing sync only** that makes the execution packets read as
  historical/current-use material without rewriting any execution contract detail below the framing
- the safe patch shape in this batch is:
  - replace stale `proposed / execution-slice / single-row only` status labels with
    historical/current-use framing
  - add one narrow current-status note near the top of each packet
  - explicitly say that packet wording alone does not prove the referenced report/manifest was
    produced and does not reopen a current execution lane
  - preserve all packet bodies, gates, expected changed files, and output contracts below the
    framing block

## UNRESOLVED

- `UNRESOLVED:` whether a later bounded slice should historicalize the adjacent
  `feature_attribution_v1_impl_slice*.md` family separately
- `UNRESOLVED:` whether any later controller/queue sync should record this execution-packet cleanup
  explicitly
- `UNRESOLVED:` whether any specific referenced report/manifest surface needs its own provenance pass
  later; this batch does not classify those artifacts

## Batch result summary

- Candidates reviewed: `5`
- `READY_STATUS_HEADER`: `5`
- `KEEP_AS_IS`: `0`
- `UNKNOWN_KEEP`: `0`

## Candidate table

| Candidate                                                                                                                            | Observed role               | Drift signal                                                                                      | Classification        | Safe batch action                       |
| ------------------------------------------------------------------------------------------------------------------------------------ | --------------------------- | ------------------------------------------------------------------------------------------------- | --------------------- | --------------------------------------- |
| `docs/decisions/feature_attribution/v1/feature_attribution_v1_exec_slice1_min_edge_identification_packet_2026-03-31.md`              | historical execution packet | stale `proposed / execution-slice / single-row only` status still reads like current run guidance | `READY_STATUS_HEADER` | replace status/current-use framing only |
| `docs/decisions/feature_attribution/v1/feature_attribution_v1_exec_slice2_hysteresis_identification_packet_2026-03-31.md`            | historical execution packet | stale `proposed / execution-slice / single-row only` status still reads like current run guidance | `READY_STATUS_HEADER` | replace status/current-use framing only |
| `docs/decisions/feature_attribution/v1/feature_attribution_v1_exec_slice3_cooldown_identification_packet_2026-03-31.md`              | historical execution packet | stale `proposed / execution-slice / single-row only` status still reads like current run guidance | `READY_STATUS_HEADER` | replace status/current-use framing only |
| `docs/decisions/feature_attribution/v1/feature_attribution_v1_exec_slice4_base_entry_confidence_identification_packet_2026-03-31.md` | historical execution packet | stale `proposed / execution-slice / single-row only` status still reads like current run guidance | `READY_STATUS_HEADER` | replace status/current-use framing only |
| `docs/decisions/feature_attribution/v1/feature_attribution_v1_exec_slice5_htf_block_identification_packet_2026-03-31.md`             | historical execution packet | stale `proposed / execution-slice / single-row only` status still reads like current run guidance | `READY_STATUS_HEADER` | replace status/current-use framing only |

## What changed vs. what did not change

This audit supports changing:

- only the top framing blocks of the five `exec_slice*` packet files

This audit does **not** support changing:

- any referenced report or manifest artifact
- any `impl_slice*` packet
- the already-synced docs-only `phase1–phase9` packet chain
- any plan anchor
- any packet scope, expected changed-file list, gate bundle, or execution contract below the top
  framing
- any runtime, config, test, or script behavior

## Bottom line

Batch 012 is a real docs-only execution-packet cleanup.

The stale effect is not in the high-sensitivity body contracts themselves; it is at the packet tops,
where `proposed / execution-slice / single-row only` still reads like live execution guidance.

The truthful next move is to historicalize those five tops, explicitly avoid implying that any
referenced run artifact was produced merely because the packet exists, and leave the packet bodies
unchanged.
