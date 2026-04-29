# RI advisory environment-fit — Phase 3 provisional evaluation admissibility

This memo is docs-only and fail-closed.
It decides what the smallest honest next Phase 3 step is after the bounded partial-baseline preflight stopped on an exact Phase 2 label-gap.

Governance packet: `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_provisional_evaluation_admissibility_packet_2026-04-17.md`

## Source surface used

This memo uses only already tracked surfaces:

- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase2_label_taxonomy_2026-04-16.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_direct_baseline_admissibility_2026-04-16.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_post_capture_v2_baseline_admissibility_2026-04-17.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_partial_baseline_label_gap_2026-04-17.md`
- `tmp/current_atr_900_env_profile_20260416.py`
- `tmp/current_atr_900_multi_year_env_robustness_20260416.py`
- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_env_profile_2026-04-16/env_summary.json`
- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_multi_year_env_robustness_2026-04-16/robustness_summary.json`

## Decision question

After the partial-baseline preflight stopped on a missing exact Phase 2 label surface, what is the next admissible Phase 3 move?

## Short answer

**A separate provisional-evaluation admissibility review is the smallest honest next step.**

Opening exact Phase 2 label-surface materialization directly from the currently fixed surfaces would overreach.
The lane should first decide, in docs only, whether any narrower provisional outcome-proxy evaluation is admissible — and exactly what claims would remain forbidden if it is.

## Why exact label materialization is not the smallest next step

### 1. The exact Phase 2 contract is stronger than the capture-v2 evidence rows

The partial-baseline preflight already proved that the capture-v2 RI rows do not contain the exact supportive / hostile contract fields:

- `pnl_delta`
- `active_uplift_cohort_membership`

That gap is real, not clerical.
It means the RI capture surface does not currently carry the exact Phase 2 label contract in-place.

### 2. The current row-level label logic lives on a different evidence chain

The current-atr scripts show that exact supportive / hostile row labels were built through a bounded comparison flow that depends on:

- baseline-vs-candidate shared positions
- positive `size_delta` as active-uplift gating
- computed `pnl_delta`
- row-level analysis rows assembled from that comparison surface

That is a legitimate evidence chain.
But it is not the same thing as the Phase C RI capture-v2 surface.

### 3. Jumping straight to exact materialization now risks hidden drift

Opening exact label materialization immediately would likely require at least one of these moves:

- reconstructing a second comparison surface not fixed by the current Phase 3 packet
- importing legacy-family active-uplift evidence into RI evaluation without a fresh boundary review
- treating temporary current-atr scripts as if they already define a fixed Phase 3 label-join artifact

That would be a larger and riskier step than the lane needs right now.
It would also come too close to reopening the earlier blocker that direct baseline work must not blur legacy outcome evidence and RI-native observability by stealth.

## Why a provisional-evaluation review is admissible

### 4. The selector side is now real enough to justify a narrower question

The preflight already established that a bounded RI selector surface exists on the capture-v2 rows:

- clarity variation exists
- recency variation exists
- probability/confidence variation exists
- the slice can state exactly which pre-entry columns are admissible

That means the lane now has a legitimate docs-only question to answer:

> Is there a narrowly defined provisional outcome-proxy evaluation surface that can be used for exploratory Phase 3 research without being misrepresented as the exact Phase 2 supportive/hostile contract?

That is smaller than label materialization.
It is also safer.

### 5. A docs-only provisional review can keep the lane honest

Such a review can define, before any new code is written:

- whether a provisional outcome proxy is admissible at all
- which proxy ingredients are allowed or forbidden
- what exact claims are prohibited
- what outputs must be labeled exploratory only
- what later work would still be required before any Phase 2-faithful supportive/hostile claim is allowed

That lets the lane move one notch forward without pretending the label problem is already solved.

## What a provisional review must not authorize

If the lane opens a provisional-evaluation review, that review must still forbid all of the following by default:

- treating raw `total_pnl` sign as equivalent to the Phase 2 supportive / hostile contract
- claiming contradiction-year success on a weakened label surface
- renaming exploratory outcome proxies as supportive/hostile labels
- implying that a provisional score has already passed the Phase 2 failure taxonomy
- reopening full role-map or `market_fit_score` claims

## Exact next admissible step

The next admissible move is therefore:

- **one docs-only provisional outcome-proxy evaluation admissibility review**

That review should decide whether there is any bounded exploratory score-check surface worth opening while staying explicit that:

- it is not the exact Phase 2 label contract
- it is not supportive/hostile proof
- it is not contradiction-year validation authority

## What still remains required later

Even if a provisional review is accepted, the lane would still need a later separate slice for at least one of these:

1. exact Phase 2 label-surface materialization on a governed RI-compatible comparison surface, or
2. an explicit lane conclusion that provisional research adds little and the bounded lane should stop

So a provisional review is a boundary-setting step, not a shortcut around the label contract.

## Bottom line

The partial-baseline preflight did enough to justify one more careful decision.
It did **not** justify exact label materialization or score implementation from the current surfaces alone.

So the smallest honest next step is:

- **open a docs-only provisional-evaluation admissibility review**

That keeps the lane moving while preserving the distinction between:

- RI-native selector readiness, and
- Phase 2-faithful supportive/hostile evaluation authority.
