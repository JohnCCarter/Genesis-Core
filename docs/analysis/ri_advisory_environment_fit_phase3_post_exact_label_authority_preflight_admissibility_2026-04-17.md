# RI advisory environment-fit — Phase 3 post-exact-label-authority-preflight admissibility

This memo is docs-only and fail-closed.
It decides whether the roadmap may continue on the current capture-v2 surface after the reliability exact-label-authority preflight ended with `NOT_RECOVERED`, or whether the lane should stop before Phase 4 on this surface.

Governance packet: `docs/decisions/ri_advisory_environment_fit_phase3_post_exact_label_authority_preflight_admissibility_packet_2026-04-17.md`

## Source surface used

- `plan/ri_advisory_environment_fit_roadmap_2026-04-16.md`
- `docs/analysis/ri_advisory_environment_fit_phase2_label_taxonomy_2026-04-16.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_post_dirty_research_exact_label_admissibility_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_reliability_exact_label_authority_preflight_2026-04-17.md`
- `results/research/ri_advisory_environment_fit/phase3_reliability_exact_label_authority_preflight_2026-04-17/join_audit.json`
- `results/research/ri_advisory_environment_fit/phase3_reliability_exact_label_authority_preflight_2026-04-17/label_authority_audit.json`
- `results/research/ri_advisory_environment_fit/phase3_reliability_exact_label_authority_preflight_2026-04-17/boundary_manifest.json`
- `results/research/ri_advisory_environment_fit/phase3_reliability_exact_label_authority_preflight_2026-04-17/manifest.json`
- `results/research/ri_advisory_environment_fit/phase3_reliability_exact_label_authority_preflight_2026-04-17/closeout.md`

## Decision question

After the exact-label-authority preflight failed closed, is any further same-surface Phase 3 continuation still admissible on the current capture-v2 row surface, or should the lane stop before Phase 4 on this surface?

## Short answer

**No further same-surface exact-label-authority continuation is admissible on the current capture-v2 surface.**

The preflight answered the narrow follow-up that dirty-research and rerun work had sharpened.
It answered it cleanly and deterministically.
And the answer was `NOT_RECOVERED`.

That means the current capture-v2 surface does not support row-level Phase 2-faithful authority for the reliability axis.
So the roadmap may not continue on this same surface as if exact authority were merely delayed or “almost there.”

## Why the path closes here on the current surface

### 1. The preflight was the governed authority test

The earlier post-dirty-research decision admitted only one more narrow question:

- can exact Phase 2-faithful reliability-side authority be recovered cleanly from the locked baseline-vs-candidate chain?

That question has now been asked under the strictest admissible form:

- locked single-source authority chain
- locked join contract `normalize(entry_time)|side`
- no heuristic substitution
- no synthetic cohort invention
- deterministic replay

So the current slice was not a loose probe.
It was the actual fail-closed authority test.

### 2. The failure is structural, not incidental

The preflight did not fail because of script instability or missing provenance.
It succeeded on both of those fronts:

- deterministic replay hashes matched
- containment passed
- the single-source authority rule held

The failure is instead structural:

- capture-v2 rows: `146`
- shared comparison rows from the locked chain: `90`
- shared comparison rows matched back to capture-v2: `7`
- unmatched shared comparison rows: `83`

That means the authority surface does not materially live on the capture-v2 surface.
It only touches a tiny minority of the relevant shared comparison population when the join is held to the locked exact contract.

### 3. Local overlap is real but insufficient

The materialized row file proves that a few exact-authority rows do exist locally.
For example, `2024-07-05T06:00:00|LONG` is a real supportive exact-authority case with non-null `pnl_delta` and active-uplift membership.

That matters because it proves the locked method itself is not fictional.
But it does **not** rescue the capture-v2 surface as a whole.

Only three rows on the capture-v2 surface became exact authoritative outcome rows:

- supportive: `1`
- hostile: `2`

Meanwhile:

- non-evaluable: `143`

That is too sparse to support any honest claim that row-level exact Phase 2 authority has been restored on the capture-v2 evidence table.

## Consequence for Phase 3 on this surface

### 4. Exact-label-authority recovery is now closed on capture-v2

The important governance consequence is simple:

- `NOT_RECOVERED` is not a temporary status label to be rhetorically worked around
- it is the governing result for the current capture-v2 authority question

So the lane may not now open another same-surface exact-label recovery attempt unless the governing question or evidence surface changes materially.

### 5. Transition remains closed

Nothing in the preflight repaired the transition axis.
The slice was explicitly reliability-only, and the artifacts keep:

- `transition_promotion = false`
- `phase4_opening = false`
- `runtime_readiness = false`

So the transition decision does not improve here.
It stays closed.

### 6. Phase 4 stays blocked

The roadmap’s later shadow-evaluation stage depends on enough label authority to support honest year-by-year bucket interpretation.
The current capture-v2 surface still does not have that.

So the roadmap may not treat this preflight as partial entry into Phase 4.
The lane remains below that threshold.

## What is still true after the failure

The earlier exploratory work is not invalidated.
It still showed that:

- the selector surface is real
- provisional proxy coverage can be restored observationally
- dirty-research shaping can sharpen a question
- a weak reliability-side tilt exists on exploratory surfaces

But after this preflight, those facts must now be read under a harder boundary:

- they do not add up to row-level exact authority on capture-v2

That means any continuing discussion of reliability on this surface must remain explicitly exploratory and non-authoritative.
It cannot pretend that the exact-label gap is merely cosmetic.

## Admissibility decision

On the **current capture-v2 surface**, the honest decision is:

- **stop before Phase 4**
- **do not open further same-surface exact-label-authority work**

If the broader research lane is ever to continue, it must do so only under a new, separately governed question that accepts all of the following up front:

- `NOT_RECOVERED` stands
- `exact_label_authority = false` stands
- dirty-research labels remain non-authoritative
- transition remains closed
- runtime remains untouched

That would be a new lane question, not a continuation pretending this surface already supports the old one.

## What should not happen next

- no new same-surface authority-recovery attempt framed as “one last join fix”
- no claim that `7 / 90` overlap is enough to treat authority as mostly recovered
- no use of the three authoritative rows as rhetorical cover for the other `143` non-evaluable rows
- no reopening of transition carry-forward
- no Phase 4 opening
- no runtime score implementation

## Bottom line

The narrow reliability-side authority question was asked cleanly.
The answer is now locked:

- `NOT_RECOVERED`

That means the current capture-v2 surface does **not** support the next roadmap step toward shadow-style or authority-bearing evaluation.

So the honest state after this slice is:

- **same-surface exact-label-authority continuation: not admissible**
- **transition carry-forward: not admissible**
- **Phase 4 on the current surface: blocked**

If the advisory program continues later, it must do so under a different governed question and without pretending that the current capture-v2 surface ever regained exact row-level Phase 2 authority.
