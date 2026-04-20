# RI advisory environment-fit — Phase 3 dirty reliability evidence verdict

This memo is fail-closed and research-only.
It records the outcome of the bounded dirty-research reliability evidence-shaping slice.

Governance packet: `docs/governance/ri_advisory_environment_fit_phase3_dirty_reliability_evidence_packet_2026-04-17.md`

## Source surface used

- `tmp/ri_advisory_environment_fit_dirty_reliability_evidence_20260417.py`
- `results/research/ri_advisory_environment_fit/phase3_dirty_reliability_evidence_2026-04-17/join_audit.json`
- `results/research/ri_advisory_environment_fit/phase3_dirty_reliability_evidence_2026-04-17/heuristic_definition.json`
- `results/research/ri_advisory_environment_fit/phase3_dirty_reliability_evidence_2026-04-17/approx_label_surface.json`
- `results/research/ri_advisory_environment_fit/phase3_dirty_reliability_evidence_2026-04-17/reliability_crosstab.json`
- `results/research/ri_advisory_environment_fit/phase3_dirty_reliability_evidence_2026-04-17/boundary_manifest.json`
- `results/research/ri_advisory_environment_fit/phase3_dirty_reliability_evidence_2026-04-17/manifest.json`
- `docs/analysis/ri_advisory_environment_fit_phase3_post_rerun_label_authority_admissibility_2026-04-17.md`

## Decision question

Does a controlled dirty-research evidence-shaping pass make the narrow reliability-side follow-up more concrete, without pretending to create exact label authority?

## Short answer

**Yes — it sharpens the reliability-side question, but it still does not create exact label authority.**

This slice stayed inside the new controlled dirty-research allowance:

- approximate labels
- incomplete classification
- simple heuristics

All of that remained explicitly:

- exploratory
- approximate
- non-authoritative

So the slice is useful as evidence shaping only.

## What the slice proved

### 1. The joined surface stayed identical to the approved rerun boundary

The join-audit remained clean:

- `matched_joined_rows = 146`
- `unmatched_left_count = 0`
- `unmatched_right_count = 0`
- duplicate-key counts = `0`
- proxy null counts matched the restored source exactly

So the dirty-research pass did not create a new surface.
It only reshaped the already approved exploratory surface.

### 2. The heuristic labels are explicit and bounded

The shaping rules were intentionally simple:

- `approx_supportive_proxy_label`: `continuation_score > 0 and fwd_16_atr > 0`
- `approx_hostile_proxy_label`: `continuation_score < 0 and fwd_16_atr < 0`
- `approx_ambiguous_proxy_label`: all other rows with non-null heuristic inputs
- `approx_non_evaluable_proxy_label`: any joined row where heuristic inputs are null

This is a deliberately rough evidence shape.
It is useful because it is easy to inspect and hard to mistake for exact label authority when clearly marked.

### 3. Reliability buckets now show a more readable tilt

The shaped surface makes the narrow reliability-side question more concrete than the raw rerun buckets alone.

#### 2024

- overall approximate label mix:
  - supportive: `39 / 72` (`54.17%`)
  - hostile: `27 / 72` (`37.50%`)
  - ambiguous: `6 / 72` (`8.33%`)
- reliability high bucket:
  - supportive: `65.22%`
  - hostile: `26.09%`
- reliability low bucket:
  - supportive: `52.17%`
  - hostile: `39.13%`

That is not a dramatic separator, but it is directionally cleaner than the earlier empty-surface state.

#### 2025

- overall approximate label mix:
  - supportive: `33 / 74` (`44.59%`)
  - hostile: `27 / 74` (`36.49%`)
  - ambiguous: `13 / 74` (`17.57%`)
  - non-evaluable: `1 / 74` (`1.35%`)
- reliability high bucket:
  - supportive: `46.15%`
  - hostile: `26.92%`
  - ambiguous: `26.92%`
- reliability low bucket:
  - supportive: `46.15%`
  - hostile: `50.00%`
  - ambiguous: `3.85%`

This is weak, but informative.
The high bucket is not “good” in any strong sense, yet the low bucket is more hostile-heavy than the high bucket.
That means the reliability-side axis still looks directionally relevant enough to inspect further.

## What the slice did not prove

This slice did **not** prove any of the following:

- exact supportive/hostile authority
- Phase 2 fidelity
- contradiction-year success/failure under the Phase 2 taxonomy
- readiness for Phase 4
- a valid transition-axis carry-forward

The boundary manifest stayed explicit:

- `exact_label_authority = false`
- `phase4_opening = false`
- `runtime_readiness = false`
- `transition_promotion = false`

That boundary is the most important output of the slice.

## Consequence for Phase 3

The dirty-research pass does not replace the earlier admissibility memo.
It makes that memo more actionable.

The lane now has:

- a clean joined exploratory surface
- a weak but inspectable reliability-side pattern
- a simple approximate evidence shape that makes the next narrow question easier to reason about

The lane still does **not** have:

- exact label authority
- a transition-side signal strong enough to carry forward honestly
- Phase 4 readiness

## Exact next admissible step

The next honest move remains:

- **one narrow reliability-side exact-label-authority / Phase-2-faithful admissibility follow-up**

Dirty research helped here because it turned the abstract question:

> is there anything on the reliability axis worth pursuing?

into a slightly sharper one:

> is the weak but visible reliability tilt strong enough to justify the cost of a clean exact-label-authority follow-up?

That is now a much more concrete decision than before.

## Bottom line

The controlled dirty-research slice succeeded at the thing it was supposed to do:

- shape the exploratory surface into something more inspectable without breaching authority boundaries

It did **not** create production-clean evidence.
It did **not** repair Phase 2 labels.
It did **not** open Phase 4.

But it did improve the lane in one useful way:

- the narrow reliability-side follow-up now looks more concrete and less speculative than before

So the honest new state is:

- **dirty research added evidence-shaping value**
- **authority is still blocked**
- **next admissible step is still the narrow reliability-side exact-label-authority question, not Phase 4**
