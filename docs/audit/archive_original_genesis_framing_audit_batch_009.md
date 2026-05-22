# Batch 009 original Genesis archive framing audit

Date: 2026-05-22
Mode: `RESEARCH`
Observed branch/worktree: `feature/genesis-topology-lifecycle-authority-map`
Status: `read-only archive framing audit / non-authorizing / docs-only / no behavior change`

> This file is a bounded audit for a retained archive document in `docs/archive/original_genesis/`.
> It does **not** move, delete, or rewrite legacy archive content by itself.

## Scope boundary

Primary candidate in scope:

- `docs/archive/original_genesis/GENESIS_FEATURES.md`

Supporting evidence surfaces in scope:

- `docs/audit/refactor/evidence/docs_archive_triage_phase6_legacy_core_decision_2026-03-09.md`
- `docs/audit/refactor/evidence/docs_archive_triage_matrix_2026-03-09.tsv`
- `docs/audit/refactor/evidence/candidate19_phase6_legacy_core_path_refcheck_2026-03-09.txt`
- `docs/archive/phase6/README.md`

Out of scope in this batch:

- moving any archive file
- deleting any archive file
- rewriting historical feature descriptions, API notes, or porting suggestions in the body
- editing `docs/CURRENT_AUTHORITY_INDEX.md`
- editing `docs/knowledge/DOCUMENTATION_PROVENANCE_LINEAGE_MAP.md`
- changing runtime, config, test, or script behavior

## Method

Checked in this slice:

- full read of `docs/archive/original_genesis/GENESIS_FEATURES.md`
- read of the prior archive triage decision that kept this file for long-term context
- check for missing top-of-file status/current-use framing
- check for skim-risk phrases that still read like current Genesis-Core architecture or porting instruction
- check of prior path-ref evidence for external reference pressure

Machine-readable evidence artifact:

- `artifacts/diagnostics/batch009_original_genesis_framing_evidence.json`

## Observed

### Prior retention decision

Observed prior support:

- `docs/audit/refactor/evidence/docs_archive_triage_phase6_legacy_core_decision_2026-03-09.md`
  classifies `docs/archive/original_genesis/GENESIS_FEATURES.md` as `KEEP`
- `docs/audit/refactor/evidence/docs_archive_triage_matrix_2026-03-09.tsv` repeats the same
  `KEEP` classification with long-term context value
- `docs/audit/refactor/evidence/candidate19_phase6_legacy_core_path_refcheck_2026-03-09.txt`
  records `NO_HIT`, which supports a low external-reference burden for a framing-only patch

### Drift in the current file top and skim path

Observed top-of-file gap:

- no `Status:` line near the file top
- no current-status note near the file top
- the file opens directly into present-tense feature summaries and porting context

Observed skim-risk phrases:

- `Unified Config API (`rest/unified_config_api.py`)`
- `Pydantic settings med .env, fallback till v1/v2`
- `### Portnings‑karta till Genesis‑Core (förslag)`
- `REST endpoints: börja med minsta nödvändiga ...`
- `Rekommenderad portning till Genesis‑Core`
- `Lägg till NonceManager och uppdatera REST/WS-klienterna ...`

Observed comparison anchor:

- `docs/archive/phase6/README.md` already uses explicit historical/current-entry-point framing for
  archive-era documentation, which is a good positive anchor for the same archive-doc hardening
  style here

## Inferred

- `docs/archive/original_genesis/GENESIS_FEATURES.md` should remain a retained historical reference
  file rather than a move/delete candidate in this batch
- the file still needs a top framing block so present-tense API/config/risk descriptions and
  porting suggestions are not skim-read as current Genesis-Core architecture guidance or active
  implementation instruction
- the safe change in this batch is **top framing only**:
  - add a `Status:` line
  - add one narrow current-status routing note near the top
  - add one historical reading note clarifying that legacy module names and porting suggestions are
    retained for provenance/context only
  - preserve every historical summary and suggested porting note below it

## UNRESOLVED

- `UNRESOLVED:` whether additional retained legacy core archive files outside this exact path need
  similar framing in later bounded slices
- `UNRESOLVED:` whether a later archive-index/controller sync should record this batch explicitly in
  a separate queue/controller update
- `UNRESOLVED:` whether any later compare-and-port packet should cite this document only as legacy
  context rather than operational instruction

## Batch result summary

- Candidates reviewed: `1`
- `READY_STATUS_HEADER`: `1`
- `KEEP_AS_IS`: `0`
- `UNKNOWN_KEEP`: `0`

## Candidate table

| Candidate                                           | Observed role                            | Drift signal                                                           | Classification        | Safe batch action                           |
| --------------------------------------------------- | ---------------------------------------- | ---------------------------------------------------------------------- | --------------------- | ------------------------------------------- |
| `docs/archive/original_genesis/GENESIS_FEATURES.md` | retained original-Genesis reference note | no top framing; present-tense feature/porting text can read as current | `READY_STATUS_HEADER` | add top historical/current-use framing only |

## What changed vs. what did not change

This audit supports changing:

- only the top framing of `docs/archive/original_genesis/GENESIS_FEATURES.md`

This audit does **not** support changing:

- the feature overview body
- the porting map body
- any API/config/risk/nonce descriptions below the top framing
- archive placement of the file
- deletion of the file
- current authority maps or provenance maps
- runtime, config, test, or script behavior

## Bottom line

Batch 009 is another real GREEN patch slice.

The file is already justified as retained legacy context, but it still opens like a live technical
feature/porting guide when skimmed quickly.

The truthful next move is to add a narrow historical/current-use frame at the top and leave the
legacy/original-Genesis summary body unchanged.
