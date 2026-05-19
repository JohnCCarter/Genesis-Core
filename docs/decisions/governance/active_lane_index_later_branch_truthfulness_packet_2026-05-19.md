# Active-lane-index later-branch truthfulness packet

Date: 2026-05-19
Branch: `feature/risk-hardening-wave2`
Status: `decision-recorded / docs-only / non-authorizing`

This document records the smallest honest truthfulness fix for `docs/governance/active_lane_index.md` on later branch contexts. It grants no replacement live lane, no control-plane refresh, and no runtime, config-authority, test, paper/live, promotion, or execution authority by itself.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via `feature/* -> RESEARCH`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice sharpens one retained historical pointer so it cannot be skim-read as branch-current guidance on later branches, without changing any runtime or control-plane authority
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why: this slice narrows interpretation of one control-plane pointer only; it does not refresh the live lane or appoint a new branch-current anchor set
- **Skill usage:** `none required` — bounded docs-only truthfulness slice; no repo-local skill matched this change
- **Objective:** make `docs/governance/active_lane_index.md` read truthfully on later branches, including `feature/risk-hardening-wave2`, without turning this slice into a live-lane refresh
- **Base SHA:** `9fd14872c958eebc2eecdd18076d1cb2a8984d50`
- **Related artifacts:** `docs/governance/active_lane_index.md`, `docs/decisions/governance/working_contract_branch_anchor_demotion_packet_2026-05-15.md`, `docs/decisions/governance/queue_status_freshness_guard_packet_2026-05-15.md`, `docs/governance/README.md`

### Scope

- **Scope IN:** this packet; one in-place wording sharpen in `docs/governance/active_lane_index.md` that makes its non-current status explicit for later branch contexts and says the captured branch anchors below are not branch-current guidance outside `feature/editor-worker-orchestrator`
- **Scope OUT:** `GENESIS_WORKING_CONTRACT.md`; `docs/governance/README.md`; queue redesign; replacement live-anchor selection; repo-wide branch-string cleanup; repo-wide historical-note normalization; any edits under `src/**`, `tests/**`, `config/**`, `scripts/**`, `results/**`, and `artifacts/**`; the currently dirty local governance docs `docs/decisions/governance/backtest_error_policy_reopen_shape_packet_2026-05-19.md` and `docs/decisions/governance/cache_schema_bump_selector_policy_carrier_decision_packet_2026-05-19.md`
- **Expected changed files:** `docs/decisions/governance/active_lane_index_later_branch_truthfulness_packet_2026-05-19.md`, `docs/governance/active_lane_index.md`
- **Max files touched:** `2`

### Gates required

For this packet itself:

- targeted docs validation for this packet and `docs/governance/active_lane_index.md`
- manual wording audit that the slice sharpens historical/non-current framing without refreshing the live lane
- manual wording audit that no replacement branch-current anchor set is implied
- manual wording audit that the two already-dirty governance docs remain out of scope

## Purpose

This packet answers one narrow question only:

- what is the smallest honest later-branch truthfulness fix for `docs/governance/active_lane_index.md` on `feature/risk-hardening-wave2`?

## What changed in this slice

- `docs/governance/active_lane_index.md` now states its non-current reading in branch-neutral terms for later branch contexts, including `feature/risk-hardening-wave2`
- the file now says explicitly that if the current branch is not the captured `feature/editor-worker-orchestrator` context, the captured mode/lane anchors below must not be read as branch-current guidance

## What did not change

- no replacement live lane or queue truth was established
- no refresh of `GENESIS_WORKING_CONTRACT.md`
- no update to `docs/governance/README.md`
- no runtime, config-authority, source, test, or execution behavior

## Governing basis

### Observed

1. `docs/governance/active_lane_index.md` is still headed by the captured branch `feature/editor-worker-orchestrator` and remains intentionally a retained historical pointer.
2. Its later-status note already says it should not be read as the branch-current selector on `feature/evidence-closeout-pilot`, but that wording is still tied to a specific later branch context rather than later branches generally.
3. `docs/decisions/governance/working_contract_branch_anchor_demotion_packet_2026-05-15.md` explicitly says `docs/governance/active_lane_index.md` was not refreshed or demoted in that earlier slice.
4. `docs/decisions/governance/queue_status_freshness_guard_packet_2026-05-15.md` says edits changing active-lane anchors in `docs/governance/active_lane_index.md` must reopen as a separate bounded packet.
5. `docs/governance/README.md` already describes `active_lane_index.md` as a retained historical pointer rather than a branch-current lane selector or new SSOT.

### Inferred

- The smallest honest fix is not a lane refresh, because a truthful refresh would require naming a replacement current anchor set.
- The smallest honest fix is a wording sharpen inside `docs/governance/active_lane_index.md` that generalizes its non-current reading from one successor branch to later branch contexts, including the current branch.
- `docs/governance/README.md` already carries the broader retained-historical framing, so it does not need to be edited in the same slice.

### Unverified in this packet

- what the eventual branch-current control-plane pointer set should be on `feature/risk-hardening-wave2`
- whether a later redesign should merge, demote further, or retire `docs/governance/active_lane_index.md`
- whether any broader control-plane simplification is worth doing after the remaining non-parked slices land

## Boundary decision

### Current standing conclusion

For `feature/risk-hardening-wave2`, the honest next move is:

- keep `docs/governance/active_lane_index.md` as a retained historical pointer to the captured `feature/editor-worker-orchestrator` context
- sharpen its later-branch wording so it cannot be skim-read as branch-current guidance on later branches
- stop short of appointing any replacement current lane or queue anchor in this slice

This packet therefore authorizes only an in-place truthfulness sharpen in `docs/governance/active_lane_index.md`.

### Non-goals

This slice does **not**:

- define the current live lane for `feature/risk-hardening-wave2`
- refresh `GENESIS_WORKING_CONTRACT.md`
- rewrite the queue or create a new control-plane index
- normalize all historical notes across the repo

## Hard stop and reopen rule

If a later slice needs any of the following, it must stop and reopen as a separate bounded packet:

- a replacement branch-current anchor set
- edits to `GENESIS_WORKING_CONTRACT.md` or other control-plane companions as part of a truthful refresh
- queue redesign or repo-wide historical-note normalization
- any runtime/default/config-authority/paper-live/readiness/promotion authority change

## Bottom line

The smallest honest fix for `#4` on `feature/risk-hardening-wave2` is not a new live-lane selector. It is a **later-branch truthfulness sharpen** in `docs/governance/active_lane_index.md` so the file remains useful as a retained historical pointer without reading as branch-current guidance on this branch.
