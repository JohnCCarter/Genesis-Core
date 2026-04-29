# RI advisory environment-fit — Phase 3 alternative evidence surface admissibility

This memo is docs-only and fail-closed.
It decides whether the roadmap may continue after the current capture-v2 surface was exhausted for same-surface exact-label-authority work, or whether the lane should close unless a materially different evidence surface is introduced.

Governance packet: `docs/decisions/ri_advisory_environment_fit_phase3_alternative_evidence_surface_admissibility_packet_2026-04-17.md`

## Source surface used

- `plan/ri_advisory_environment_fit_roadmap_2026-04-16.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_post_capture_v2_baseline_admissibility_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_post_dirty_research_exact_label_admissibility_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_reliability_exact_label_authority_preflight_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_post_exact_label_authority_preflight_admissibility_2026-04-17.md`
- `results/research/ri_advisory_environment_fit/phase3_reliability_exact_label_authority_preflight_2026-04-17/join_audit.json`
- `results/research/ri_advisory_environment_fit/phase3_reliability_exact_label_authority_preflight_2026-04-17/label_authority_audit.json`
- `results/research/ri_advisory_environment_fit/phase3_reliability_exact_label_authority_preflight_2026-04-17/boundary_manifest.json`

## Decision question

After the current capture-v2 surface failed closed on the exact-label-authority test, may the roadmap continue only through a materially different evidence surface, or should the lane stop here?

## Short answer

**Yes — a materially different evidence surface is now the only admissible route if the roadmap is to continue.**

The current surface has been exhausted for the question it was supposed to answer.
It may still exist as exploratory evidence.
But it may no longer serve as the carrier for same-surface authority-bearing continuation.

So the roadmap now forks cleanly:

- either define a materially different evidence surface, or
- close the lane rather than continue by rhetorical drift

## Why the current surface is exhausted

### 1. The same-surface authority question has already been asked under full discipline

The lane has already done all of the honest intermediate work on the present capture-v2 surface:

- selector-side admissibility
- provisional proxy restoration
- dirty-research reliability shaping
- post-dirty-research admissibility narrowing
- exact-label-authority preflight

That final preflight was the decisive governed test, and it ended in `NOT_RECOVERED`.

So the current surface is not merely underexplored.
It is now explored enough to close the same-surface authority path.

### 2. The failure was structural, not procedural

The preflight replayed the locked authority chain deterministically and still landed at:

- shared comparison rows: `90`
- rows matched back to capture-v2: `7`
- rows unmatched: `83`
- supportive rows on capture-v2: `1`
- hostile rows on capture-v2: `2`
- non-evaluable rows: `143`

That means the current surface does not carry enough co-resident authority to support Phase 2-faithful row-level interpretation.

This was not a formatting bug, a nondeterminism issue, or a missing hash.
It was a surface-design failure for this specific purpose.

### 3. Dirty research no longer moves the boundary

Dirty research helped earlier because it sharpened the question.
It did not and cannot convert sparse same-surface overlap into exact authority.

So any attempt to continue on the same surface by using more exploratory shaping would no longer be question-sharpening.
It would be boundary drift.

## What a new surface would have to provide

A new evidence surface is admissible **only if** it is materially different in the ways that matter, not merely renamed or rejoined.

At minimum, such a surface must satisfy all of the following:

1. **co-resident observability and authority**
   - the surface must carry RI-relevant pre-entry observability and the authority-bearing outcome surface in a way that does not depend on a sparse post hoc join-back like `7 / 90`

2. **deterministic exact join discipline**
   - if a join is still required, it must be exact, unique, and materially complete enough that row-level authority is not mostly absent by construction

3. **no dirty-research authority substitution**
   - heuristic labels may shape exploration, but they may not stand in for Phase 2-faithful authority

4. **RI-only and advisory-only boundaries preserved**
   - no runtime authority, no default changes, no cross-family leakage, no transition promotion by implication

5. **clear contradiction-year usefulness path**
   - the surface must support honest multi-year evaluation, especially against `2025`, rather than merely restoring a `2024`-friendly local story

If a candidate surface cannot satisfy those conditions, it is not a real continuation surface.
It is just a new way to keep the old ambiguity alive.

## What this does and does not open

### What it does open

The next admissible move is now one new governed question only:

> Is there a materially different evidence surface that can carry both RI observability and outcome authority honestly enough to reopen deterministic advisory-baseline work?

That is the only honest continuation question left.

### What it does not open

This decision does **not** open:

- another same-surface authority-recovery attempt
- Phase 4
- runtime-readiness
- transition-axis carry-forward
- score implementation
- new artifact generation by default

It only says that if the roadmap continues, it must do so on different footing.

## Lane-close condition

If no materially different surface can be identified cleanly under the existing lane constraints, then the honest result is:

- **close the lane**

That would not mean the work failed to produce insight.
It would mean the work succeeded in proving that the current route does not support robust continuation.

That is still a useful research result.
And it is far better than Phase-4 theater on a surface that never regained authority.

## Admissibility decision

The honest state is now:

- **current capture-v2 surface: closed for same-surface authority-bearing continuation**
- **materially different evidence surface: admissible in principle as the only continuation route**
- **lane close: required fallback if no such surface can be justified cleanly**

## Bottom line

We are no longer deciding whether the current surface can be salvaged.
That decision has already been made.

The next decision is narrower and cleaner:

- either define a materially different evidence surface that co-locates observability and authority well enough to support renewed deterministic advisory work,
- or stop.

That is what it means to be ready to continue the roadmap honestly from here.
