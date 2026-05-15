# Working-contract branch-anchor demotion packet

Date: 2026-05-15
Branch: `feature/evidence-closeout-pilot`
Status: `decision-recorded / docs-only / non-authorizing`

This document records the bounded demotion of `GENESIS_WORKING_CONTRACT.md` as a branch-current anchor on `feature/evidence-closeout-pilot`. It grants no replacement live lane pointer set and no runtime, config-authority, paper/live, promotion, or execution authority by itself.
This change demotes a retained historical branch anchor; it does not refresh the active lane, rewrite the queue, or establish a replacement branch-current control-plane anchor.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via `feature/* -> RESEARCH`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice neutralizes false branch-current wording in an existing docs control-plane surface only and does not modify source, tests, results, runtime behavior, or governance precedence
- **Required Path:** `Quick path / docs-only boundary record`
- **Lane:** `Research-evidence` — why: this packet reduces control-plane interpretation drift without refreshing the live lane or widening into a new status framework
- **Skill usage:** `none required` — bounded docs-only demotion packet; no repo-local skill matched this slice
- **Objective:** further demote `GENESIS_WORKING_CONTRACT.md` from branch-current control-plane truth to retained historical anchor content on the current branch, without appointing a substitute live anchor set
- **Base SHA:** `1251acca3c97df1df7dfce7627868fc25949f1ec`
- **Related artifacts:** `GENESIS_WORKING_CONTRACT.md`, `docs/analysis/diagnostics/genesis_core_deep_premortem_feature_evidence_closeout_pilot_2026-05-15.md`, `docs/analysis/diagnostics/deep_premortem_followup_phase_plan_feature_evidence_closeout_pilot_2026-05-15.md`, `docs/decisions/governance/queue_status_freshness_guard_packet_2026-05-15.md`, `docs/governance/active_lane_index.md`

### Scope

- **Scope IN:** this demotion packet; in-place historical qualification of `GENESIS_WORKING_CONTRACT.md`
- **Scope OUT:** `docs/governance/active_lane_index.md`; `docs/analysis/diagnostics/deep_premortem_followup_phase_plan_feature_evidence_closeout_pilot_2026-05-15.md`; `docs/analysis/diagnostics/next_phase_verkstad_queue_2026-05-15.md`; repo-wide branch-string cleanup; repo-wide historical-note normalization; any source/test/config/results/artifacts/runtime changes
- **Max files touched:** `2`

### Gates required

For this packet itself:

- targeted docs validation for this packet and `GENESIS_WORKING_CONTRACT.md`
- manual wording audit that the slice removes implied present authority without assigning new present authority
- manual wording audit that stale branch/lane/next-step headings become explicitly historical rather than being replaced with a partial live refresh

## Purpose

This packet answers one narrow question only:

- what is the smallest honest control-plane fix for the stale branch-current reading of `GENESIS_WORKING_CONTRACT.md` on `feature/evidence-closeout-pilot`?

## What changed in this slice

- `GENESIS_WORKING_CONTRACT.md` now states that the detailed branch/lane content it retains is historical for `feature/editor-worker-orchestrator`
- the stale branch, validated-lane, and next-step headings in `GENESIS_WORKING_CONTRACT.md` are now qualified as retained historical anchor content

## What did not change

- no replacement branch-current anchor set was established
- `docs/governance/active_lane_index.md` was not refreshed or demoted in this slice
- no queue, phase-plan, source, test, runtime, config-authority, readiness, promotion, paper/live, or champion semantics changed

## Governing basis

### Observed

1. The deep premortem lists stale branch-anchor truth in `GENESIS_WORKING_CONTRACT.md` as a concrete branch risk.
2. The follow-up phase plan explicitly keeps one bounded Phase 1 slice open that either refreshes or further demotes `GENESIS_WORKING_CONTRACT.md`.
3. Before this slice, `GENESIS_WORKING_CONTRACT.md` still named `feature/editor-worker-orchestrator` under `Current branch and mode anchor` and still presented `Current validated lane` plus `Next admissible steps` as if they were current branch truth.
4. `docs/governance/active_lane_index.md` still mirrors that older branch context and still points readers back to `GENESIS_WORKING_CONTRACT.md` as the current drift anchor.
5. The queue/status freshness guard already says that edits changing active-lane anchors in `GENESIS_WORKING_CONTRACT.md` or `docs/governance/active_lane_index.md` must reopen as a separate bounded packet.

### Inferred

- The smallest honest fix is **not** a refresh, because a truthful refresh would require a broader control-plane update that also touches `docs/governance/active_lane_index.md` and explicitly replaces the live pointer set.
- The smallest honest fix is a **demotion**: keep `GENESIS_WORKING_CONTRACT.md` tracked, but narrow it to retained historical anchor content and remove its implied present authority on `feature/evidence-closeout-pilot`.
- This packet may explain why the demotion is necessary, but it may not become a substitute live anchor or quiet queue rewrite.

### Unverified in this packet

- what the eventual replacement branch-current anchor set should be on `feature/evidence-closeout-pilot`
- whether `docs/governance/active_lane_index.md` should later be refreshed, further demoted, or otherwise redesigned
- whether any broader control-plane simplification is worth doing after the remaining deep-premortem slices land

## Boundary decision

### Current standing conclusion

For `feature/evidence-closeout-pilot`, `GENESIS_WORKING_CONTRACT.md` may remain tracked as retained historical drift-reference content, but it must not continue reading as the current branch anchor.

This slice therefore does only the following:

- adds explicit branch-mismatch demotion wording
- qualifies stale branch, lane, and next-step headings as retained historical content
- does **not** refresh `docs/governance/active_lane_index.md`
- does **not** define a new live lane, live queue, or replacement control-plane anchor set

### Non-goals

This slice does **not**:

- define the current live lane for `feature/evidence-closeout-pilot`
- appoint a substitute current anchor document
- retrofit historical branch references across the repo
- rewrite the phase plan or reopen the closed successor queue

## Hard stop and reopen rule

If a future slice needs any of the following, it must stop and reopen as a separate bounded packet:

- refresh `docs/governance/active_lane_index.md` or any other third control-plane file as part of a truthful replacement anchor set
- queue or phase-plan synchronization beyond this retained-historical clarification
- runtime/default/comparison/readiness/promotion/paper-live authority changes

## Bottom line

The honest fix here is demotion, not refresh. This slice removes false present authority from `GENESIS_WORKING_CONTRACT.md` on the current branch while leaving any broader anchor-pair refresh for a later bounded reopen.
