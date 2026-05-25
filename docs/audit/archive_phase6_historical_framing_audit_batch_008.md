# Batch 008 archive Phase-6 historical framing audit

Date: 2026-05-22
Mode: `RESEARCH`
Observed branch/worktree: `feature/genesis-topology-lifecycle-authority-map`
Status: `read-only archive framing audit / non-authorizing / docs-only / no behavior change`

> This file is a bounded audit for a retained archive document in `docs/archive/phase6/`.
> It does **not** move, delete, or rewrite archive history by itself.

## Scope boundary

Primary candidate in scope:

- `docs/archive/phase6/PHASE-6_LEARNINGS.md`

Supporting evidence surfaces in scope:

- `docs/archive/phase6/README.md`
- `docs/audit/refactor/evidence/docs_archive_triage_phase6_legacy_core_decision_2026-03-09.md`
- `docs/audit/refactor/evidence/docs_archive_triage_matrix_2026-03-09.tsv`
- `docs/audit/refactor/evidence/candidate19_phase6_legacy_core_path_refcheck_2026-03-09.txt`

Out of scope in this batch:

- moving any archive file
- deleting any archive file
- rewriting historical findings, metrics, or recommendations inside the body
- editing `docs/CURRENT_AUTHORITY_INDEX.md`
- editing `docs/knowledge/DOCUMENTATION_PROVENANCE_LINEAGE_MAP.md`
- changing runtime, config, test, or script behavior

## Method

Checked in this slice:

- full read of `docs/archive/phase6/PHASE-6_LEARNINGS.md`
- full read of the hardened companion `docs/archive/phase6/README.md`
- read of the prior archive triage decision that kept this file for long-term context
- check for missing top-of-file status/current-use framing
- check for skim-risk phrases that still read like current system status or current decision pressure
- check of prior path-ref evidence for external reference pressure

Machine-readable evidence artifact:

- `artifacts/diagnostics/batch008_archive_phase6_framing_evidence.json`

## Observed

### Prior retention decision

Observed prior support:

- `docs/audit/refactor/evidence/docs_archive_triage_phase6_legacy_core_decision_2026-03-09.md`
  classifies `docs/archive/phase6/PHASE-6_LEARNINGS.md` as `KEEP`
- `docs/audit/refactor/evidence/docs_archive_triage_matrix_2026-03-09.tsv` repeats the same `KEEP`
  classification with long-term context value
- `docs/audit/refactor/evidence/candidate19_phase6_legacy_core_path_refcheck_2026-03-09.txt`
  records `NO_HIT`, which supports a low external-reference burden for a framing-only patch

### Drift in the current file top and skim path

Observed top-of-file gap:

- no `Status:` line near the file top
- no current-status note near the file top
- the file opens directly into executive-summary and discovery language

Observed skim-risk phrases:

- `Ensure system is production-ready`
- `## 📈 PERFORMANCE METRICS (Current System)`
- `- All tests passing`
- `- Production-ready`
- `## 📋 DECISION NEEDED`

Observed control anchor in the same subtree:

- `docs/archive/phase6/README.md` is already hardened as historical archive-era context and routes
  readers to current entry points instead of reading as current project status

## Inferred

- `docs/archive/phase6/PHASE-6_LEARNINGS.md` should remain a retained historical context file rather
  than a move/delete candidate in this batch
- the file still needs a top framing block so archive-era findings are not skim-read as current
  repository readiness, current system state, or current strategic decision pressure
- the safe change in this batch is **top framing only**:
  - add a `Status:` line
  - add one narrow current-status routing note near the top
  - preserve every historical finding, metric, recommendation, and archive-era conclusion below it

## UNRESOLVED

- `UNRESOLVED:` whether `docs/archive/original_genesis/GENESIS_FEATURES.md` should be the next
  archive-local framing hardening candidate in a separate bounded slice
- `UNRESOLVED:` whether any additional `docs/archive/phase6/**` files still need current-use
  framing beyond the already-hardened `README.md` and the candidate in this batch
- `UNRESOLVED:` whether a later archive-index/controller sync should record this batch explicitly in
  a separate queue/controller update

## Batch result summary

- Candidates reviewed: `1`
- `READY_STATUS_HEADER`: `1`
- `KEEP_AS_IS`: `0`
- `UNKNOWN_KEEP`: `0`

## Candidate table

| Candidate                                  | Observed role                             | Drift signal                                                           | Classification          | Safe batch action                            |
| ------------------------------------------ | ----------------------------------------- | ---------------------------------------------------------------------- | ----------------------- | -------------------------------------------- |
| `docs/archive/phase6/PHASE-6_LEARNINGS.md` | retained historical Phase-6 findings note | no top framing; several lines still read like current readiness/status | `READY_STATUS_HEADER`   | add top historical/current-use framing only  |

## What changed vs. what did not change

This audit supports changing:

- only the top framing of `docs/archive/phase6/PHASE-6_LEARNINGS.md`

This audit does **not** support changing:

- the executive summary or any findings below it
- any metrics, test counts, model names, or recommendations in the body
- archive placement of the file
- deletion of the file
- current authority maps or provenance maps
- runtime, config, test, or script behavior

## Bottom line

Batch 008 is a real GREEN patch slice.

The file is already justified as retained archive context, but it still opens too much like current
system status when skimmed quickly.

The truthful next move is to add a narrow historical/current-use frame at the top and leave the
archived Phase-6 snapshot body unchanged.
