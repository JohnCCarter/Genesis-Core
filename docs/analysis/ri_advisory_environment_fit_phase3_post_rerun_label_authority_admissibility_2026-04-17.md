# RI advisory environment-fit — Phase 3 post-rerun label-authority admissibility

This memo is docs-only and fail-closed.
It decides whether the bounded exploratory signal from the provisional rerun is strong enough to justify one more separate Phase 3 follow-up centered on exact label authority, or whether the lane should stop before Phase 4.

Governance packet: `docs/decisions/ri_advisory_environment_fit_phase3_post_rerun_label_authority_admissibility_packet_2026-04-17.md`

## Source surface used

- `plan/ri_advisory_environment_fit_roadmap_2026-04-16.md`
- `docs/analysis/ri_advisory_environment_fit_phase2_label_taxonomy_2026-04-16.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_partial_baseline_label_gap_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_provisional_evaluation_rerun_2026-04-17.md`
- `results/research/ri_advisory_environment_fit/phase3_provisional_evaluation_rerun_2026-04-17/join_audit.json`
- `results/research/ri_advisory_environment_fit/phase3_provisional_evaluation_rerun_2026-04-17/bucket_summary.json`
- `results/research/ri_advisory_environment_fit/phase3_provisional_evaluation_rerun_2026-04-17/manifest.json`

## Decision question

Does the post-rerun exploratory surface justify opening a later separate exact-label-authority / Phase-2-faithful materialization decision, or should Phase 3 stop before Phase 4?

## Short answer

**Yes — but only for a narrow reliability-side follow-up, not for the transition axis and not for Phase 4.**

The rerun did enough to show that the lane is no longer blocked by empty provisional proxy coverage.
It also did enough to show that one bounded exploratory signal — the reliability-oriented rank — is not pure noise.

But that is still weaker than a validated deterministic baseline.
So the only admissible carry-forward is one later, separate decision or slice about whether exact Phase 2 label authority can be materialized cleanly for the narrow reliability question.

## Why a narrow follow-up is admissible

### 1. The rerun is now operationally clean

The post-rerun join discipline passed exactly:

- `matched_joined_rows = 146`
- `unmatched_left_count = 0`
- `unmatched_right_count = 0`
- duplicate-key counts = `0`
- replay hashes matched

So the lane is no longer blocked on the mechanics of joining RI selector rows to exploratory proxy evidence.

### 2. Reliability-side exploratory structure is present, even if weak

The rerun memo showed that `decision_reliability_rank` now has some bounded directional structure, especially against:

- `fwd_16_atr`
- `continuation_score`

That structure is weak and not cleanly monotone everywhere.
But it is materially different from the earlier empty-surface failure.

The lane therefore has a new narrow question worth asking:

> if the reliability-side signal is not empty, is it strong enough to justify testing against the exact Phase 2 supportive/hostile contract under a separate governed follow-up?

That question is smaller — and more honest — than jumping to Phase 4.

## Why this does not open Phase 4

### 3. Exact label authority is still blocked

The earlier partial-baseline preflight already proved that the exact Phase 2 surface is still missing:

- `pnl_delta`
- `active_uplift_cohort_membership`

The rerun did not repair that.
It only restored provisional proxy evidence and showed that some exploratory ranking structure exists on that provisional surface.

So the following remains true:

- restored proxies are **exploratory evidence only**
- `label_gap_still_blocked = true` remains authoritative
- supportive/hostile evaluation under the Phase 2 contract is still not materially open

### 4. Transition-side carry-forward is not justified

The rerun memo also showed that `transition_proxy_rank` remains mixed or inverted across years.

That means the rerun does **not** justify a transition-oriented next slice.
If any later follow-up opens, it should be explicitly limited to the narrow reliability-side question.

### 5. Roadmap Phase 4 still requires more than exploratory proxies

Phase 4 expects year-by-year shadow score behavior and bucketed outcome tables for:

- supportive
- hostile
- ambiguous
- transition

The current surface still lacks the exact supportive/hostile authority needed for those tables.
And the transition-oriented exploratory signal is not strong enough to carry forward honestly.

So Phase 4 remains closed.

## Admissibility decision

The next admissible move is:

- **one later separate exact-label-authority / Phase-2-faithful materialization admissibility decision or follow-up, limited to the narrow reliability-side question**

That next follow-up must remain explicitly scoped OUT from:

- transition-axis carry-forward
- direct Phase 4 opening
- runtime-facing baseline implementation
- contradiction-year proof claims

## What should not happen next

- no claim that restored proxy buckets are equivalent to supportive/hostile labels
- no claim that Phase 3 is complete already
- no Phase 4 opening from exploratory proxy evidence alone
- no attempt to carry the mixed transition axis forward as if it were stable

## Fallback if the narrow follow-up is not clean

If a later exact-label-authority follow-up cannot be made cleanly without cross-surface drift, synthetic cohort invention, or weakened Phase 2 semantics, the honest outcome should be:

- **stop before Phase 4**

That would still be a valid result.
It would mean the lane found some bounded exploratory structure, but not enough governed authority to promote it into a real deterministic baseline.

## Bottom line

The rerun changed one thing materially:

- the lane is no longer blocked by an empty exploratory proxy surface

But it did **not** change the deeper authority boundary:

- exact Phase 2 label authority is still blocked
- transition-side structure is still too mixed
- Phase 4 is still not open

So the honest next state is:

- **narrow reliability-side follow-up: admissible in principle**
- **transition carry-forward: not admissible**
- **Phase 4: still blocked**

That is the furthest clean step the current evidence supports.
