# RI advisory environment-fit — Phase 3 post-dirty-research exact-label admissibility

This memo is docs-only and fail-closed.
It decides whether the controlled dirty-research shaping pass made the narrow reliability-side exact-label-authority question more concrete, or whether the lane should stop before any further authority-oriented follow-up.

Governance packet: `docs/governance/ri_advisory_environment_fit_phase3_post_dirty_research_exact_label_admissibility_packet_2026-04-17.md`

## Source surface used

- `docs/analysis/ri_advisory_environment_fit_phase2_label_taxonomy_2026-04-16.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_provisional_evaluation_rerun_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_post_rerun_label_authority_admissibility_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_dirty_reliability_evidence_2026-04-17.md`
- `results/research/ri_advisory_environment_fit/phase3_dirty_reliability_evidence_2026-04-17/join_audit.json`
- `results/research/ri_advisory_environment_fit/phase3_dirty_reliability_evidence_2026-04-17/heuristic_definition.json`
- `results/research/ri_advisory_environment_fit/phase3_dirty_reliability_evidence_2026-04-17/approx_label_surface.json`
- `results/research/ri_advisory_environment_fit/phase3_dirty_reliability_evidence_2026-04-17/reliability_crosstab.json`
- `results/research/ri_advisory_environment_fit/phase3_dirty_reliability_evidence_2026-04-17/boundary_manifest.json`
- `results/research/ri_advisory_environment_fit/phase3_dirty_reliability_evidence_2026-04-17/manifest.json`

## Decision question

Did the dirty-research shaping pass make the next narrow reliability-side exact-label-authority question sufficiently concrete to justify one more separately governed follow-up, while still keeping Phase 4 closed?

## Short answer

**Yes — but only as a narrow, reliability-only admissibility question.**

The dirty-research pass did not create authority.
It did create a clearer inspection surface.

That means the lane has progressed from:

- “there might be something on the reliability axis”

to:

- “there is a weak but readable reliability-side tilt that is concrete enough to justify one later exact-label-authority decision”

That is a meaningful improvement.
It is still far short of a Phase 4 opening.

## Why the question is now more concrete

### 1. The shaped surface stayed inside the approved rerun boundary

The dirty-research join audit kept the exact same 146-row exploratory surface:

- `matched_joined_rows = 146`
- `coverage_shortfall = 0`
- duplicate-key counts = `0`
- proxy null counts matched the restored proxy source exactly

So the shaping pass did not fabricate a new dataset.
It only made the existing exploratory surface easier to inspect.

### 2. The heuristic labels are crude, but they made the reliability signal easier to reason about

The heuristic surface is explicitly rough:

- supportive proxy bucket when `continuation_score > 0` and `fwd_16_atr > 0`
- hostile proxy bucket when `continuation_score < 0` and `fwd_16_atr < 0`
- ambiguous otherwise
- non-evaluable when heuristic inputs are null

That is not exact label authority.
But it is good enough to test whether the reliability-side rank continues to point in a direction that looks worth the cost of a cleaner follow-up.

### 3. The shaped surface adds a weak but non-trivial reliability-side tilt

The signal remains weak, but it is no longer abstract.

#### 2024

- overall supportive share: `54.17%`
- overall hostile share: `37.50%`
- high reliability bucket:
  - supportive: `65.22%`
  - hostile: `26.09%`
- low reliability bucket:
  - supportive: `52.17%`
  - hostile: `39.13%`

That is a readable directional tilt.
Not a strong one, but readable.

#### 2025

- overall supportive share: `44.59%`
- overall hostile share: `36.49%`
- high reliability bucket:
  - supportive: `46.15%`
  - hostile: `26.92%`
- low reliability bucket:
  - supportive: `46.15%`
  - hostile: `50.00%`

This is still mixed and weak.
But the low bucket being materially more hostile-heavy than the high bucket means the reliability-side question is not empty.

That is enough to make a later exact-label-authority admissibility follow-up feel concrete rather than speculative.

## What did not change

### 4. The dirty-research pass did not recover the exact Phase 2 contract

The dirty-research surface remains heuristic and exploratory.
It did not recover:

- `pnl_delta`
- `active_uplift_cohort_membership`
- Phase 2-faithful supportive/hostile semantics

So the following remain authoritative:

- `exact_label_authority = false`
- `phase4_opening = false`
- heuristic proxy labels are not exact labels

### 5. The transition axis is still not admissible

Nothing in the dirty-research shaping pass repaired the earlier transition-side weakness.
The pass was reliability-oriented by design, and nothing honest in its outputs justifies reopening transition carry-forward.

So the transition decision stays unchanged:

- **not admissible**

## Admissibility decision

The next admissible move is still limited to:

- **one later separately governed exact-label-authority / Phase-2-faithful admissibility follow-up, scoped narrowly to the reliability axis**

That follow-up must remain scoped OUT from:

- transition carry-forward
- direct Phase 4 opening
- runtime-facing implementation
- any claim that heuristic dirty-research buckets already answer the exact label question

## When the lane should stop instead

If the later exact-label-authority question cannot be answered cleanly without:

- synthetic cohort invention
- weakened Phase 2 semantics
- cross-surface drift
- relabeling heuristic buckets as if they were authoritative

then the honest outcome remains:

- **stop before Phase 4**

That would not invalidate the dirty-research slice.
It would simply mean the slice succeeded as evidence shaping but could not be promoted into an authority-bearing follow-up.

## Bottom line

The dirty-research pass did one valuable thing:

- it made the narrow reliability-side exact-label-authority question more concrete

It did **not** do any of the things that would be required to open Phase 4.

So the honest state after this slice is:

- **next narrow reliability-side exact-label-authority admissibility follow-up: still admissible, now more concrete**
- **transition carry-forward: still not admissible**
- **Phase 4: still blocked**

That is the furthest clean interpretation the current evidence supports.
