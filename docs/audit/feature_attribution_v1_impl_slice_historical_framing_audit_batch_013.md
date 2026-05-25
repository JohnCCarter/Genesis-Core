# Batch 013 Feature Attribution v1 impl-slice historical framing audit

Date: 2026-05-22
Mode: `RESEARCH`
Observed branch/worktree: `feature/genesis-topology-lifecycle-authority-map`
Status: `read-only status/framing audit / non-authorizing / docs-only / no behavior change`

> This file is a bounded audit for the `Feature Attribution v1` `impl_slice*` packet family.
> It does **not** reopen implementation, authorize code/test changes, or touch adjacent execution,
> phase, or plan surfaces by itself.

## Scope boundary

Primary candidates in scope:

- `docs/decisions/feature_attribution/v1/feature_attribution_v1_impl_slice1_min_edge_neutralization_packet_2026-03-31.md`
- `docs/decisions/feature_attribution/v1/feature_attribution_v1_impl_slice2_hysteresis_neutralization_packet_2026-03-31.md`
- `docs/decisions/feature_attribution/v1/feature_attribution_v1_impl_slice3_cooldown_neutralization_packet_2026-03-31.md`
- `docs/decisions/feature_attribution/v1/feature_attribution_v1_impl_slice5_htf_block_neutralization_packet_2026-03-31.md`

Supporting evidence surfaces in scope:

- `docs/audit/feature_attribution_v1_phase_packet_historical_framing_audit_batch_011.md`
- `docs/audit/feature_attribution_v1_exec_slice_historical_framing_audit_batch_012.md`
- `docs/decisions/feature_attribution/v1/feature_attribution_v1_phase0_scope_freeze_packet_2026-03-31.md`
- `plan/feature_attribution_post_phase14_reactivation_roadmap_2026-04-02.md`
- `plan/genesis_driver_identification_master_roadmap_2026-04-14.md`

Out of scope in this batch:

- editing any `results/research/feature_attribution_v1/**` artifact
- editing any `feature_attribution_v1_exec_slice*.md`
- editing `phase0` or the already-synced `phase1–phase9` packet chain
- editing either later plan anchor
- rewriting packet bodies, scopes, expected changed files, gates, default-behavior locks, or
  output contracts
- changing runtime, config, test, or script behavior
- editing `docs/CURRENT_AUTHORITY_INDEX.md`
- editing `docs/knowledge/DOCUMENTATION_PROVENANCE_LINEAGE_MAP.md`

## Method

Checked in this slice:

- full read of the four existing `impl_slice*` packet files in the retained v1 family
- read-only comparison against the already historicalized docs-only `phase1–phase9` and
  `exec_slice*` packet chains
- read-only comparison against the locked `phase0` anchor and later historical/closed plan anchors
- top-of-file status/current-use framing check for all four candidates
- skim-path wording check for `proposed / behavior-touching / explicit-opt-in only` drift

Machine-readable evidence artifact:

- `artifacts/diagnostics/batch013_feature_attribution_v1_impl_slice_framing_evidence.json`

## Observed

### Adjacent v1 packet families already read as retained historical provenance

Observed supporting context:

- Batch 011 already historicalized the docs-only `phase1–phase9` packet chain
- Batch 012 already historicalized the `exec_slice*` packet chain
- `feature_attribution_v1_phase0_scope_freeze_packet_2026-03-31.md` already reads as a locked
  internal anchor rather than a proposed next step
- the later post-Phase-14 and Genesis-driver plan anchors are already historical/closed on the
  current branch

### The impl-slice packet tops still read like current implementation-ready next steps

Observed top status drift across the implementation packet family:

- all four existing packets still begin with `Status: proposed / behavior-touching / explicit-opt-in only`

Observed skim-risk pattern:

- each packet opens as a future implementation slice with `Category: api`, `Risk: HIGH`,
  `Required Path: Full`, and expected changed files under docs plus high-sensitivity code/test
  paths
- without a top current-status note, later readers can over-read the packet as current
  implementation guidance rather than retained historical packet provenance
- the stale effect is concentrated at the file tops; the bodies already contain the historical
  implementation-contract details that should be preserved rather than rewritten in this slice

## Inferred

- the `impl_slice*` family should remain retained historical implementation-packet provenance
  rather than current branch implementation authority
- the safe correction is a **top-framing sync only** that makes the implementation packets read as
  historical/current-use material without rewriting any code/test contract detail below the framing
- the safe patch shape in this batch is:
  - replace stale `proposed / behavior-touching / explicit-opt-in only` status labels with
    historical/current-use framing
  - add one narrow current-status note near the top of each packet
  - explicitly say that implementation-packet wording alone does not authorize code/test changes or
    reopen a current branch implementation lane
  - preserve all packet bodies, scopes, expected changed files, gates, and output contracts below
    the framing block

## UNRESOLVED

- `UNRESOLVED:` whether any later controller/queue sync should record this implementation-packet
  cleanup explicitly
- `UNRESOLVED:` whether any specific runtime/report artifact linked from the broader v1 chain needs
  its own provenance pass later; this batch does not classify those surfaces
- `UNRESOLVED:` there is no `impl_slice4` file in the retained family; this batch does not invent,
  renumber, or reconcile that absence

## Batch result summary

- Candidates reviewed: `4`
- `READY_STATUS_HEADER`: `4`
- `KEEP_AS_IS`: `0`
- `UNKNOWN_KEEP`: `0`

## Candidate table

| Candidate                                                                                                                 | Observed role                    | Drift signal                                                                                         | Classification        | Safe batch action                       |
| ------------------------------------------------------------------------------------------------------------------------- | -------------------------------- | ---------------------------------------------------------------------------------------------------- | --------------------- | --------------------------------------- |
| `docs/decisions/feature_attribution/v1/feature_attribution_v1_impl_slice1_min_edge_neutralization_packet_2026-03-31.md`   | historical implementation packet | stale `proposed / behavior-touching / explicit-opt-in only` status still reads like current guidance | `READY_STATUS_HEADER` | replace status/current-use framing only |
| `docs/decisions/feature_attribution/v1/feature_attribution_v1_impl_slice2_hysteresis_neutralization_packet_2026-03-31.md` | historical implementation packet | stale `proposed / behavior-touching / explicit-opt-in only` status still reads like current guidance | `READY_STATUS_HEADER` | replace status/current-use framing only |
| `docs/decisions/feature_attribution/v1/feature_attribution_v1_impl_slice3_cooldown_neutralization_packet_2026-03-31.md`   | historical implementation packet | stale `proposed / behavior-touching / explicit-opt-in only` status still reads like current guidance | `READY_STATUS_HEADER` | replace status/current-use framing only |
| `docs/decisions/feature_attribution/v1/feature_attribution_v1_impl_slice5_htf_block_neutralization_packet_2026-03-31.md`  | historical implementation packet | stale `proposed / behavior-touching / explicit-opt-in only` status still reads like current guidance | `READY_STATUS_HEADER` | replace status/current-use framing only |

## What changed vs. what did not change

This audit supports changing:

- only the top framing blocks of the four existing `impl_slice*` packet files

This audit does **not** support changing:

- any runtime, config, test, or script surface
- any referenced code/test path named in the packets
- any `exec_slice*` packet
- the already-synced docs-only `phase1–phase9` packet chain
- any plan anchor
- any packet scope, expected changed-file list, gate bundle, default-behavior lock, or
  implementation contract below the top framing
- the missing `impl_slice4` numbering gap

## Bottom line

Batch 013 is a real docs-only implementation-packet cleanup.

The stale effect is not in the high-sensitivity body contracts themselves; it is at the packet tops,
where `proposed / behavior-touching / explicit-opt-in only` still reads like live implementation
guidance.

The truthful next move is to historicalize those four tops, explicitly avoid implying that the
packet text authorizes any current code/test changes, and leave the packet bodies unchanged.
