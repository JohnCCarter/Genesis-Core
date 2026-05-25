# Archive / Move Reference Audit — Batch 001

Date: 2026-05-22
Mode: `RESEARCH`
Observed branch/worktree: `feature/genesis-topology-lifecycle-authority-map`
Status: `reference audit surface / non-authorizing / docs-only / no behavior change`

> This file is a read-only batch reference audit. It does **not** authorize archive moves,
> renames, deletions, reclassification, or any runtime/config/test changes by itself.
>
> Batch controller for this slice: `docs/knowledge/GENESIS_TOPOLOGY_LIFECYCLE_AUTHORITY_MAP.md`
> (`plan/` zone = `YELLOW`, reference checks before moves).
>
> Disposition input for this batch: `docs/audit/DOCUMENTATION_DISPOSITION_MAP.md`.
>
> No archive/move actions are performed in this audit slice. Every classification below is a
> recommendation only.

## Scope boundary

This batch starts with the `plan/**` historical roadmap candidates currently surfaced in
`docs/audit/DOCUMENTATION_DISPOSITION_MAP.md` as:

- `MOVE_TO_ARCHIVE_LATER`
- `SUPERSEDE_WITH_POINTER`

Candidates available in this bounded start-scope at audit time: **4**.
No additional `plan/**` roadmap candidates were present in the folder tree.

Because only four direct candidates existed in this batch-start zone, the `at least 10 candidates`
threshold was **not reachable in this bounded scope**.
The broader queue for batches 002–007 is tracked separately in
`docs/system/GENESIS_TOPOLOGY_WORK_QUEUE.md`.

## Method

For each candidate, this batch checked:

- inbound references by exact path
- inbound references by filename
- inbound references by filename slug
- exact title-match references when practical
- whether the file is cited by current map/support surfaces
- whether the file already has historical / non-authorizing framing
- whether an explicit canonical successor is already named

Observed note:

- exact title matches were `0` for all four candidates in repo text search
- path / filename / slug references were the reliable inbound-reference signals for this batch
- the numeric inbound-reference counts below were captured **before this audit artifact existed** and therefore exclude self-reference from `docs/audit/archive_move_reference_audit_batch_001.md`

## Classification legend

| Classification             | Meaning in this batch                                                                                    |
| -------------------------- | -------------------------------------------------------------------------------------------------------- |
| `READY_STATUS_HEADER`      | Safe status/header hardening appears ready now                                                           |
| `READY_SUPERSEDED_POINTER` | Safe explicit successor pointer appears ready now                                                        |
| `READY_ARCHIVE_MOVE`       | Archive/move looks structurally ready after this audit, but is **not** performed here                    |
| `KEEP_PROVENANCE`          | File currently serves as evidence/provenance/current-map support and should be retained as-is for now    |
| `BLOCKED_REFERENCE_FOUND`  | Inbound references are broad enough that archive/move is blocked pending a larger reference update slice |
| `NEEDS_OPUS`               | Risk/authority ambiguity is high enough to require heavier review                                        |
| `UNKNOWN_KEEP`             | Evidence is ambiguous or incomplete; fail-closed hold                                                    |

## Batch result summary

| Classification             | Count | Candidates                                                                                                                                    |
| -------------------------- | ----: | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `READY_STATUS_HEADER`      |     0 | none                                                                                                                                          |
| `READY_SUPERSEDED_POINTER` |     0 | none                                                                                                                                          |
| `READY_ARCHIVE_MOVE`       |     1 | `plan/ri-family-admission-roadmap-2026-03-24.md`                                                                                              |
| `KEEP_PROVENANCE`          |     2 | `plan/feature_attribution_post_phase14_reactivation_roadmap_2026-04-02.md`, `plan/genesis_driver_identification_master_roadmap_2026-04-14.md` |
| `BLOCKED_REFERENCE_FOUND`  |     1 | `plan/ri_advisory_environment_fit_roadmap_2026-04-16.md`                                                                                      |
| `NEEDS_OPUS`               |     0 | none                                                                                                                                          |
| `UNKNOWN_KEEP`             |     0 | none                                                                                                                                          |

## Candidate table

| Candidate                                                                  | Disposition-map hint     | Inbound refs (path / filename / slug) | Current map support                 | Historical / non-authorizing status already present | Explicit successor                                                      | Classification            |
| -------------------------------------------------------------------------- | ------------------------ | ------------------------------------- | ----------------------------------- | --------------------------------------------------- | ----------------------------------------------------------------------- | ------------------------- |
| `plan/feature_attribution_post_phase14_reactivation_roadmap_2026-04-02.md` | `SUPERSEDE_WITH_POINTER` | `9 / 9 / 9`                           | Yes — topology map + provenance map | Yes                                                 | Yes — `plan/genesis_driver_identification_master_roadmap_2026-04-14.md` | `KEEP_PROVENANCE`         |
| `plan/genesis_driver_identification_master_roadmap_2026-04-14.md`          | `MOVE_TO_ARCHIVE_LATER`  | `8 / 8 / 8`                           | Yes — topology map + provenance map | Yes                                                 | No explicit later successor found                                       | `KEEP_PROVENANCE`         |
| `plan/ri-family-admission-roadmap-2026-03-24.md`                           | `MOVE_TO_ARCHIVE_LATER`  | `3 / 3 / 3`                           | Yes — topology map + provenance map | Yes                                                 | No explicit later successor found                                       | `READY_ARCHIVE_MOVE`      |
| `plan/ri_advisory_environment_fit_roadmap_2026-04-16.md`                   | `MOVE_TO_ARCHIVE_LATER`  | `31 / 31 / 31`                        | Yes — topology map + provenance map | Yes                                                 | No explicit later successor found                                       | `BLOCKED_REFERENCE_FOUND` |

## Evidence notes by candidate

### 1) `plan/feature_attribution_post_phase14_reactivation_roadmap_2026-04-02.md`

- Current file already carries strong historical framing:
  - `Status: closed / historical / archive-only / evidence-carried / no-default-behavior-change`
  - archived current-status note
- An explicit historical successor pointer is already present in the current status note:
  - `plan/genesis_driver_identification_master_roadmap_2026-04-14.md`
- Inbound path/filename/slug refs are moderate (`9 / 9 / 9`) and include:
  - later diagnostic-campaign packet chain
  - the later Genesis-driver roadmap
  - topology/provenance maps
  - the disposition map
- Canonical-support reading:
  - yes, it still supports current topology/provenance interpretation of `plan/` as historical context
- Honest read:
  - the safe superseded-pointer follow-up is already satisfied
  - remaining role is historical evidence/provenance, not a fresh patch target

**Classification:** `KEEP_PROVENANCE`

### 2) `plan/genesis_driver_identification_master_roadmap_2026-04-14.md`

- Current file already carries strong historical framing:
  - `Status: closed / historical / archive-only / bounded closeout complete / docs-only authority`
  - archived current-status note
- It also contains a lineage note naming the older Feature Attribution roadmap as predecessor.
- Inbound path/filename/slug refs are moderate (`8 / 8 / 8`) and include:
  - diagnostic-campaign closeout packets
  - topology/provenance maps
  - the disposition map
  - the earlier Feature Attribution roadmap
- Canonical-support reading:
  - yes, this file currently acts as a closeout anchor for multiple historical packet chains
- Honest read:
  - move pressure exists, but the file is still carrying provenance/evidence load across multiple packet references
  - no explicit later canonical successor was found that would safely replace it in this batch

**Classification:** `KEEP_PROVENANCE`

### 3) `plan/ri-family-admission-roadmap-2026-03-24.md`

- Current file already carries strong historical framing:
  - `Status: historical / parked / archive-only / not active on current branch / no-behavior-change roadmap`
  - archived current-status note
- Inbound path/filename/slug refs are low (`3 / 3 / 3`) and are currently limited to:
  - topology map
  - provenance map
  - disposition map
- No packet-chain or analysis-chain fan-out was found in this batch's inbound-reference search.
- Canonical-support reading:
  - yes, but only as a lightly cited historical planning surface in current derivative maps
- Honest read:
  - this is the cleanest next archive candidate in batch 001
  - archive/move is still a **later** slice because map/reference updates would be required, but the reference surface is small and bounded

**Classification:** `READY_ARCHIVE_MOVE`

### 4) `plan/ri_advisory_environment_fit_roadmap_2026-04-16.md`

- Current file already carries strong historical framing:
  - `Status: historical / parked / archive-only / not active on current branch / planning-only / advisory-only / no-runtime-authority`
  - archived current-status note
- Inbound path/filename/slug refs are high (`31 / 31 / 31`) and fan out across:
  - `docs/analysis/regime_intelligence/advisory_environment_fit/**`
  - `docs/decisions/regime_intelligence/advisory_environment_fit/**`
  - topology/provenance maps
- Canonical-support reading:
  - yes, but with a large evidence/provenance fan-out across the advisory-environment-fit packet chain
- Honest read:
  - archive/move is not a small follow-up anymore
  - the current reference surface is broad enough that a later move would need a larger coordinated update slice first

**Classification:** `BLOCKED_REFERENCE_FOUND`

## Patch eligibility for the follow-up patch phase

Under the stated patch rules, only these classes are patch-eligible:

- `READY_STATUS_HEADER`
- `READY_SUPERSEDED_POINTER`

Current batch result:

- `READY_STATUS_HEADER`: **none**
- `READY_SUPERSEDED_POINTER`: **none**

Therefore:

- **no patchable candidate is produced by Batch 001 itself**
- the next admissible follow-up from this batch is **not** a patch, but a separate move-class slice for `plan/ri-family-admission-roadmap-2026-03-24.md` if and when the required reference-update scope is authorized

## Bottom line

Batch 001 confirms that the `plan/` zone can now be handled in batches rather than as isolated one-file decisions, but the batch truth is mixed:

- one candidate is structurally light enough to recommend for a later archive/move slice
- two candidates still function as historical provenance/evidence anchors and should not be moved casually
- one candidate is blocked by a broad packet/analysis reference surface

That means the topology map is working best here as a **batch controller**:

- route the zone to `YELLOW`
- run one bounded reference audit
- bucket candidates by risk
- patch only if a patch-safe bucket actually exists
- defer move-class work to its own governed slice
