# Batch 010 Feature Attribution post-Phase-14 historical framing audit

Date: 2026-05-22
Mode: `RESEARCH`
Observed branch/worktree: `feature/genesis-topology-lifecycle-authority-map`
Status: `read-only status/framing audit / non-authorizing / docs-only / no behavior change`

> This file is a bounded audit for the post-Phase-14 Feature Attribution packet cluster and its
> companion reconciliation memo.
> It does **not** reopen the lane, authorize execution, or change the surrounding historical plan
> anchors by itself.

## Scope boundary

Primary candidates in scope:

- `docs/decisions/feature_attribution/post_phase14/feature_attribution_post_phase14_phase0_reactivation_packet_2026-04-02.md`
- `docs/decisions/feature_attribution/post_phase14/feature_attribution_post_phase14_phase1_rebaseline_reconciliation_packet_2026-04-02.md`
- `docs/decisions/feature_attribution/post_phase14/feature_attribution_post_phase14_phase2_6_closeout_packet_2026-04-02.md`
- `docs/analysis/diagnostics/feature_attribution_post_phase14_rebaseline_reconciliation_2026-04-02.md`

Supporting evidence surfaces in scope:

- `plan/feature_attribution_post_phase14_reactivation_roadmap_2026-04-02.md`
- `plan/genesis_driver_identification_master_roadmap_2026-04-14.md`

Out of scope in this batch:

- editing either plan anchor
- editing any `docs/decisions/feature_attribution/v1/**` file
- editing any execution/implementation packet
- rewriting packet bodies, metrics, rankings, or conclusions
- changing runtime, config, test, or script behavior
- editing `docs/CURRENT_AUTHORITY_INDEX.md`
- editing `docs/knowledge/DOCUMENTATION_PROVENANCE_LINEAGE_MAP.md`

## Method

Checked in this slice:

- full read of the three post-Phase-14 packet files
- full read of the companion reconciliation memo
- full read of the two surrounding plan anchors already marked historical/closed
- top-of-file status/current-use framing check for all four candidates
- skim-path wording check for active/proposed/live restart language

Machine-readable evidence artifact:

- `artifacts/diagnostics/batch010_feature_attribution_post_phase14_framing_evidence.json`

## Observed

### Historical plan anchors are already closed

Observed in the supporting plan layer:

- `plan/feature_attribution_post_phase14_reactivation_roadmap_2026-04-02.md` is already framed as
  `closed / historical / archive-only / evidence-carried`
- `plan/genesis_driver_identification_master_roadmap_2026-04-14.md` is already framed as
  `closed / historical / archive-only / bounded closeout complete`

These plan anchors already route readers away from treating the earlier Feature Attribution lane as
current branch guidance.

### The packet cluster still reads more active than the plan anchors

Observed packet status lines:

- Phase 0 packet: `phase0-active / docs-only / non-authorizing`
- Phase 1 packet: `phase1-proposed / docs-plus-artifact / non-authorizing`
- Phase 2–6 packet: `closeout-active / docs-only / non-authorizing`

Observed companion memo drift:

- the memo has no top `Status:` line or current-status note
- the memo still says its job is to separate the two `live reference surfaces`
- the memo still says to `start the replay lane` with `Volatility sizing cluster`
- the memo still calls the Phase 14 frame `still-active` in a way that can read like current branch
  restart guidance when skimmed quickly

## Inferred

- the post-Phase-14 Feature Attribution cluster should remain retained historical provenance rather
  than active restart guidance on the current branch
- the safe correction is a **top-framing sync only** that makes the packet/memo layer read as
  historical companion material consistent with the already-hardened plan anchors
- the safe patch shape in this batch is:
  - replace stale packet status labels with historical/current-use framing
  - add one narrow current-status note near the top of each packet
  - add a top status/current-use frame to the companion memo
  - preserve all packet scope, rankings, evidence, and conclusions below the framing block

## UNRESOLVED

- `UNRESOLVED:` whether a later broader Feature Attribution v1 packet sweep should historicalize
  the older `phase1–phase9` docs-only packet chain in a separate bounded slice
- `UNRESOLVED:` whether any later controller/queue sync should record this packet-cluster cleanup
  explicitly
- `UNRESOLVED:` whether any later packet should reopen this lane under a fresh current branch frame;
  this batch does not authorize that step

## Batch result summary

- Candidates reviewed: `4`
- `READY_STATUS_HEADER`: `4`
- `KEEP_AS_IS`: `0`
- `UNKNOWN_KEEP`: `0`

## Candidate table

| Candidate | Observed role | Drift signal | Classification | Safe batch action |
| --------- | ------------- | ------------ | -------------- | ----------------- |
| `docs/decisions/feature_attribution/post_phase14/feature_attribution_post_phase14_phase0_reactivation_packet_2026-04-02.md` | historical restart packet | stale `phase0-active` status still reads like current lane opening | `READY_STATUS_HEADER` | replace status/current-use framing only |
| `docs/decisions/feature_attribution/post_phase14/feature_attribution_post_phase14_phase1_rebaseline_reconciliation_packet_2026-04-02.md` | historical reconciliation packet | stale `phase1-proposed` status still reads like a live next slice | `READY_STATUS_HEADER` | replace status/current-use framing only |
| `docs/decisions/feature_attribution/post_phase14/feature_attribution_post_phase14_phase2_6_closeout_packet_2026-04-02.md` | historical closeout packet | stale `closeout-active` status conflicts with later closed plan anchors | `READY_STATUS_HEADER` | replace status/current-use framing only |
| `docs/analysis/diagnostics/feature_attribution_post_phase14_rebaseline_reconciliation_2026-04-02.md` | historical reconciliation memo | no top framing; memo still uses `live` / `start the replay lane` wording | `READY_STATUS_HEADER` | add top status/current-use framing only |

## What changed vs. what did not change

This audit supports changing:

- only the top framing blocks of the four candidate files

This audit does **not** support changing:

- any plan anchor
- packet scope, questions, metrics, ranking tables, or conclusions
- the meaning of the historical provenance split between frozen and current executable-route baselines
- any runtime, config, test, or script behavior

## Bottom line

Batch 010 is a real GREEN packet-cluster cleanup.

The surrounding plan layer is already historical/closed, but the companion packet/memo layer still
contains `active`, `proposed`, `closeout-active`, and `live restart` language that can be skim-read
as current branch guidance.

The truthful next move is to sync those four file tops to their actual historical/current-use role
and leave the packet bodies unchanged.
