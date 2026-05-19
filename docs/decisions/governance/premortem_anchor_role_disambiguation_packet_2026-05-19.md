# Premortem-anchor role disambiguation packet

Date: 2026-05-19
Branch: `feature/risk-hardening-wave2`
Status: `decision-recorded / docs-only / non-authorizing`

This document records the smallest honest disambiguation fix for the three tracked premortem notes that can otherwise compete for canonical-anchor status. It grants no queue refresh, no new authority, and no runtime, config-authority, test, paper/live, promotion, or execution authority by itself.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via `feature/* -> RESEARCH`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice adds reader-routing and role labels to existing historical diagnostics notes only, without changing their underlying claims or turning any one note into a live selector
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why: this slice clarifies how three retained diagnostics notes should be read relative to each other; it does not reopen any premortem lane or create a new control-plane anchor
- **Skill usage:** `none required` — bounded docs-only anchor-disambiguation slice; no repo-local skill matched this change
- **Objective:** reduce `#19` anchor competition by adding explicit role routing across the three tracked premortem notes: branch-specific implementation-time risk frame, later branch-state re-anchor, and broader project-baseline sweep
- **Base SHA:** `a891d94ecd0c66087ffc33542f1a4f6ad20792e5`
- **Related artifacts:** `docs/analysis/diagnostics/genesis_core_premortem_feature_evidence_closeout_pilot_2026-05-15.md`, `docs/analysis/diagnostics/premortem_delta_reanchor_feature_evidence_closeout_pilot_2026-05-18.md`, `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`

### Scope

- **Scope IN:** this packet; status-note reader-routing in the three tracked premortem docs only; explicit role labels that say which note is the branch-specific implementation-time frame, which note is the later re-anchor, and which note is the broader project-baseline sweep
- **Scope OUT:** queue redesign; authority changes; any edits under `src/**`, `tests/**`, `config/**`, `scripts/**`, `results/**`, and `artifacts/**`; any rewrite of the historical body content of the three notes; any edits to the already-dirty local governance docs `docs/decisions/governance/backtest_error_policy_reopen_shape_packet_2026-05-19.md` and `docs/decisions/governance/cache_schema_bump_selector_policy_carrier_decision_packet_2026-05-19.md`
- **Expected changed files:** `docs/decisions/governance/premortem_anchor_role_disambiguation_packet_2026-05-19.md`, `docs/analysis/diagnostics/genesis_core_premortem_feature_evidence_closeout_pilot_2026-05-15.md`, `docs/analysis/diagnostics/premortem_delta_reanchor_feature_evidence_closeout_pilot_2026-05-18.md`, `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`
- **Max files touched:** `4`

### Gates required

For this packet itself:

- targeted docs validation for the packet and the three touched diagnostics notes
- manual wording audit that the slice adds routing/disambiguation only and does not rewrite historical findings as current instructions
- manual wording audit that no note becomes a branch-current selector or queue authority by convenience
- manual wording audit that the two already-dirty governance docs remain out of scope

## Purpose

This packet answers one narrow question only:

- what is the smallest honest fix for `#19` so the three tracked premortem notes no longer compete silently for canonical-anchor status?

## What changed in this slice

- each tracked premortem note now says more explicitly what role it plays relative to the other two
- readers now get direct routing from one note to the other two when they need branch-specific frame, later re-anchor, or broader project-baseline synthesis

## What did not change

- no queue reopened
- no historical body content was rewritten as current instruction
- no authority, runtime, config, test, or execution behavior changed
- no note was promoted into a new SSOT or live selector

## Governing basis

### Observed

1. `docs/analysis/diagnostics/genesis_core_premortem_feature_evidence_closeout_pilot_2026-05-15.md` already says it is a historical branch-specific risk frame, but it does not route readers directly to the later re-anchor or the broader project-baseline note.
2. `docs/analysis/diagnostics/premortem_delta_reanchor_feature_evidence_closeout_pilot_2026-05-18.md` already says it is a historical re-anchor snapshot, but it does not route readers directly to the original implementation-time frame or the broader project-baseline note.
3. `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md` already says it is not a delta and already references the earlier notes, but the reciprocal routing is incomplete.
4. The current baseline explicitly names `#19` as competition between three tracked premortem chains and recommends explicit cross-links with role labels.

### Inferred

- The smallest honest fix is not to collapse the three notes into one.
- The smallest honest fix is not a queue or authority rewrite.
- The smallest honest fix is a role-disambiguation layer in their status notes so each note keeps its historical content but stops forcing readers to infer which note is the “real” anchor.

### Unverified in this packet

- whether a later repo-wide diagnostics taxonomy simplification is worth doing
- whether any future branch should replace this three-note structure with a different anchored chain
- whether any broader governance index should later summarize these diagnostics notes centrally

## Boundary decision

### Current standing conclusion

The honest `#19` fix on `feature/risk-hardening-wave2` is:

- keep all three tracked premortem notes
- preserve their historical bodies
- add explicit role routing so each note names the other two as the branch-specific frame, later re-anchor, or broader project-baseline sweep as appropriate

This packet therefore authorizes only status-note-level role disambiguation in those three docs.

### Non-goals

This slice does **not**:

- create a single canonical premortem file
- reopen any premortem queue or follow-up plan
- rewrite historical findings into current branch guidance
- change governance precedence or current active-lane truth

## Hard stop and reopen rule

If a later slice needs any of the following, it must stop and reopen as a separate bounded packet:

- repo-wide diagnostics taxonomy cleanup
- a new canonical governance index for diagnostics chains
- queue, active-lane, or authority changes
- any runtime/default/config-authority/paper-live/readiness/promotion change

## Bottom line

The smallest honest `#19` fix is a **role-disambiguation slice**, not a rewrite. The three tracked premortem notes stay intact, but their status notes now route readers explicitly to the branch-specific implementation-time frame, the later branch-state re-anchor, and the broader project-baseline sweep so they no longer compete silently for canonical-anchor status.
