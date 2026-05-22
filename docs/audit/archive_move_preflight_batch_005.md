# Batch 005 archive move preflight

Date: 2026-05-22
Mode: `RESEARCH`
Observed branch/worktree: `feature/genesis-topology-lifecycle-authority-map`
Status: `read-only preflight / non-authorizing / docs-only / no behavior change`

> This file is a read-only preflight audit for the next admissible archive move candidate.
> It does **not** perform an archive move, rename, delete, reference update, or governance
> reclassification by itself.
>
> Batch controller for this slice: `docs/system/GENESIS_TOPOLOGY_WORK_QUEUE.md`
> (`Batch 005 — archive candidates`).
>
> Prior reference audit anchor: `docs/audit/archive_move_reference_audit_batch_001.md`.

## Scope boundary

This preflight narrows Batch 005 to the single smallest move-class candidate already identified as
`READY_ARCHIVE_MOVE` in Batch 001:

- `plan/ri-family-admission-roadmap-2026-03-24.md`

The purpose here is not to reopen classification from scratch.
The purpose is to verify whether that move-ready candidate is **currently executable** as a small,
bounded, docs-only slice without entering unrelated local work.

## Method

Checked in this preflight:

- current branch and worktree state
- current existence of the source file and a plausible archive destination path
- exact current doc references by path and slug
- git status of the directly implicated reference files
- current control-surface references in:
  - `docs/knowledge/GENESIS_TOPOLOGY_LIFECYCLE_AUTHORITY_MAP.md`
  - `docs/knowledge/DOCUMENTATION_PROVENANCE_LINEAGE_MAP.md`
  - `docs/audit/DOCUMENTATION_DISPOSITION_MAP.md`
  - `docs/audit/archive_move_reference_audit_batch_001.md`

Machine-readable evidence artifact:

- `artifacts/diagnostics/batch005_archive_preflight_evidence.json`

## Observed

### Candidate state

- source file exists: `plan/ri-family-admission-roadmap-2026-03-24.md`
- plausible destination path is free:
  - `docs/archive/plan/ri-family-admission-roadmap-2026-03-24.md`
- the source file is not locally modified in the worktree
- the file already carries strong historical framing and an archive-only current status note

### Current reference surface

Current doc references remain tightly bounded.
The candidate is still cited by the same small set of reference surfaces identified in Batch 001:

1. `docs/knowledge/GENESIS_TOPOLOGY_LIFECYCLE_AUTHORITY_MAP.md`
2. `docs/knowledge/DOCUMENTATION_PROVENANCE_LINEAGE_MAP.md`
3. `docs/audit/DOCUMENTATION_DISPOSITION_MAP.md`
4. `docs/audit/archive_move_reference_audit_batch_001.md`

Observed reading of those references:

- the topology map is an active derivative controller and would need an updated path if the move is
  executed
- the provenance lineage map is a live historical routing surface and would need an updated path if
  the move is executed
- the disposition map is a current classification surface and would need an updated path or later
  note if the move is executed
- the older Batch 001 audit is already a historical audit artifact; it can remain historical, but a
  move slice should explicitly preserve that reading rather than silently pretending the old path
  never existed

### Current execution blocker

One directly implicated reference surface is already locally modified in the current worktree:

- `docs/knowledge/DOCUMENTATION_PROVENANCE_LINEAGE_MAP.md`

Observed implication:

- a clean move slice would have to enter that file to keep path-routing truthful after the move
- the standing user instruction for this stream is to leave unrelated local changes untouched
- therefore the candidate is structurally small but **not execution-clean in the current worktree**

## Inferred

- Batch 001 still appears directionally correct: this remains the cleanest small archive candidate
  outside `docs/archive/`
- a future move slice can likely stay bounded if it is opened when the provenance map is clean or
  explicitly brought into scope
- the likely minimum truthful move surface would be:
  - move `plan/ri-family-admission-roadmap-2026-03-24.md`
  - update `docs/knowledge/GENESIS_TOPOLOGY_LIFECYCLE_AUTHORITY_MAP.md`
  - update `docs/knowledge/DOCUMENTATION_PROVENANCE_LINEAGE_MAP.md`
  - update `docs/audit/DOCUMENTATION_DISPOSITION_MAP.md`
  - preserve historical truth in `docs/audit/archive_move_reference_audit_batch_001.md` rather than
    rewriting it as if the pre-move path never existed

## Unverified

- `UNRESOLVED:` whether the current local edits in
  `docs/knowledge/DOCUMENTATION_PROVENANCE_LINEAGE_MAP.md` already include nearby changes that
  would materially interact with this candidate path
- `UNRESOLVED:` whether a later combined move slice should also update any secondary
  index/controller artifact not surfaced by the current bounded reference search
- `UNRESOLVED:` whether `docs/archive/plan/` is the final preferred long-lived taxonomy home,
  though it is the most natural domain-preserving destination observed in the current tree

## Current batch conclusion

Classification for this preflight:

- structural readiness: `READY_ARCHIVE_MOVE`
- current execution status: `DEFER_UNTIL_REFERENCE_SURFACES_ARE_CLEAN`

Meaning in this batch:

- the candidate does **not** need more discovery work before a move-class slice
- the candidate also should **not** be moved in this exact autonomous batch while the required
  provenance reference surface already contains unrelated local edits

## What changed vs. what did not change

Changed in this preflight:

- the repo now has a current read-only execution-preflight record for the next small archive move
  candidate
- the blocker is made explicit as a worktree/reference-surface issue, not a renewed uncertainty
  about candidate quality

Did **not** change in this preflight:

- no file was moved
- no references were rewritten
- no archive taxonomy was altered
- no governance precedence changed
- no runtime/config/test/script behavior changed
- Batch 001's historical audit result remains intact

## Bottom line

Batch 005 is not blocked by archive-candidate ambiguity.
It is blocked by **current worktree hygiene on a required reference surface**.

The next admissible step is a bounded move-class slice for
`plan/ri-family-admission-roadmap-2026-03-24.md` once the provenance-map surface is clean or
explicitly included in scope.
