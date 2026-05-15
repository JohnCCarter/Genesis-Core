# Queue/status freshness guard packet

Date: 2026-05-15
Branch: `feature/evidence-closeout-pilot`
Status: `decision-recorded / docs-only / non-authorizing`

This document records the minimal same-slice freshness rule for queue status, historical framing, and next-step prose. It grants no runtime, config-authority, paper/live, promotion, or execution authority by itself.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via `feature/* -> RESEARCH`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice records one control-plane freshness rule for existing docs surfaces only and does not modify source, tests, results, runtime behavior, or governance precedence
- **Required Path:** `Quick path / docs-only boundary record`
- **Lane:** `Research-evidence` — why: the packet reduces stale sequencing drift in the current docs/control-plane surfaces without widening into a new status framework
- **Objective:** define the smallest same-slice update rule that prevents stale queue status or stale next-step prose from silently taking control
- **Base SHA:** `ad21fa4ffe10ce1a61c16c797ecb720ae3391017`
- **Related artifacts:** `docs/analysis/diagnostics/next_phase_verkstad_queue_2026-05-15.md`, `docs/analysis/diagnostics/genesis_core_premortem_feature_evidence_closeout_pilot_2026-05-15.md` (`local-only / untracked / historical reference only / not repository-tracked authority`), `GENESIS_WORKING_CONTRACT.md`, `docs/governance/active_lane_index.md`

### Scope

- **Scope IN:** this freshness-guard packet; queue sync that closes the current successor phase truthfully
- **Scope OUT:** edits to `GENESIS_WORKING_CONTRACT.md`; edits to `docs/governance/active_lane_index.md`; repo-wide status-framework redesign; archive-wide historical-note retrofit; any source/test/config/results/artifacts/runtime changes
- **Max files touched:** `2`

### Gates required

For this packet itself:

- targeted docs validation for this packet and queue sync
- manual wording audit that the rule stays minimal and trigger-based rather than universal bureaucracy
- manual wording audit that historical notes remain historical instead of being rewritten as live instructions

## Purpose

This packet answers one narrow question only:

- when must queue status, historical packet framing, and next-step prose be updated in the same slice?

## What changed in this slice

- the repo now has one explicit same-slice freshness rule for queue truth and touched artifact framing
- the current successor queue is closed explicitly instead of being left in a half-live state

## What did not change

- no source, test, results, runtime, or config-authority behavior
- no new SSOT or repo-wide status framework
- no requirement to rewrite untouched historical notes

## Governing basis

### Observed

1. The live successor queue records stale “next step” text as a real steering hazard once multiple packets and diagnostics notes exist in parallel.
2. The branch premortem ranks queue drift and documentation topology as real control-plane risks.
3. `GENESIS_WORKING_CONTRACT.md` is explicitly a drift anchor rather than SSOT and says to stop/re-anchor before proceeding if the next step starts relying on memory instead of cited anchors.
4. `docs/governance/active_lane_index.md` explicitly says historical/observational/parked notes must remain in that bucket until a later packet changes status, and that the page itself updates only when active-lane pointers actually change.
5. On the current branch, every successor slice from 7 through 11 required queue sync to keep the actual next admissible step truthful after the slice landed.

### Inferred

- The smallest useful rule is **not** a universal status-maintenance regime across the repo.
- The smallest useful rule is a **same-slice freshness bundle** triggered only when a slice changes the actual next admissible step or changes how a touched artifact should be read.
- Untouched historical files do not need retrofit just because newer queue truth exists.
- Touched files may not keep stale next-step prose when that prose conflicts with the current queue truth.

## Boundary decision

### Same-slice freshness bundle

When a slice changes the actual next admissible step, that same slice must update all of the following before publication:

1. **Live queue truth**
   - mark the current slice truthfully (`queued`, `selected`, `completed`, `next`, or closed as applicable)
   - advance or close the next-step line in the live queue artifact
2. **Touched artifact framing**
   - keep packet/note status truthful (`historical`, `observational`, `planning-only`, `non-authorizing`, `completed in this slice`, and similar wording as applicable)
   - say what changed and what did not change when the slice is docs-only
3. **Touched next-step prose**
   - if a file touched in the slice still contains stale “next step” language that now conflicts with live queue truth, update or neutralize that prose in the same slice

### Trigger boundary

This freshness bundle is required when either of these is true:

- the slice changes the actual next admissible step
- the slice changes how a touched packet/note should be interpreted (for example from live-looking to historical, from queued to completed, or from ambiguous to explicitly local/non-authorizing)

It is **not** required for every typo fix or housekeeping edit that does not affect sequencing truth.

### Publish boundary

If a slice cannot update the live queue and the touched artifact framing in the same diff, the honest state is:

- do not publish the slice yet

## Hard stop and reopen rule

If a future slice needs any of the following, it must stop and reopen as a separate bounded packet:

- repo-wide historical-note normalization
- a new shared status framework or automation layer
- edits that change active-lane anchors in `GENESIS_WORKING_CONTRACT.md` or `docs/governance/active_lane_index.md`
- runtime/default/comparison/readiness/promotion/paper-live authority changes

## Bottom line

Queue freshness is a risk control, not cosmetics. The minimal rule is simple: when a slice changes the real next step, publish the queue truth, touched artifact framing, and any conflicting touched next-step prose together in that same slice. That is enough to keep stale docs from quietly becoming the control plane.
