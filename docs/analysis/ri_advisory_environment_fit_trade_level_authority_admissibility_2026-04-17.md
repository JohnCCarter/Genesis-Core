# RI advisory environment-fit — trade-level authority admissibility

This memo is docs-only and fail-closed.
It decides whether RI advisory work may pivot from the exhausted exact row-level authority-recovery path to a new lane where trade outcomes become the primary authority surface while entry rows remain the pre-entry scoring surface.

Governance packet: `docs/governance/ri_advisory_environment_fit_trade_level_authority_admissibility_packet_2026-04-17.md`

## Source surface used

- `plan/ri_advisory_environment_fit_roadmap_2026-04-16.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_partial_baseline_label_gap_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_provisional_evaluation_admissibility_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_bundle_surface_reliability_opening_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_reliability_exact_label_authority_preflight_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_post_exact_label_authority_preflight_admissibility_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_materially_different_surface_inventory_2026-04-17.md`
- `docs/governance/ri_advisory_environment_fit_phase3_reliability_exact_label_authority_preflight_packet_2026-04-17.md`
- `docs/governance/ri_advisory_environment_fit_phase3_phaseC_evidence_capture_v2_packet_2026-04-17.md`

## Decision question

After the current RI lane failed to recover exact row-level authority on the capture-v2 surface, is it admissible to open a new research lane that defines authority primarily at the trade-outcome level and then derives entry-time advisory signal from that authority surface under explicit uncertainty and partial coverage?

## Short answer

**Yes — in principle, but only as a new lane with new semantics.**

That means:

- the old exact row-level authority question remains closed
- the new lane may ask a different question
- the new lane must not pretend to have repaired the old contract

This is a pivot, not a recovery.

## Why a pivot is now reasonable

### 1. The old row-level authority path is exhausted

The old lane tried to answer a specific question:

- can exact Phase-2-faithful supportive/hostile authority be rematerialized back onto the RI capture-v2 entry-row surface?

That question has already been asked under explicit fail-closed conditions.
The answer was:

- `NOT_RECOVERED`

That result remains authoritative.
The current capture-v2 surface therefore may not be treated as if exact row-level authority were merely delayed.

### 2. The selector surface is more usable than the authority surface

The RI lane did manage to materialize a meaningful selector surface on the bundle-driven evidence rows:

- clarity
- recency
- confidence/probability context
- sizing/context descriptors
- deterministic join discipline for realized trades

What remained blocked was the authority side:

- exact supportive/hostile labels were not carried on-row
- rematerialized authority from the locked comparison chain was far too sparse
- same-surface continuation was therefore closed

That makes a reframing reasonable.
The lane may need a different primary authority surface than the entry-row surface itself.

### 3. The research goal is advisory signal, not perfect row completeness at any cost

The roadmap’s larger question was never “can we force every entry row into an exact label?”
It was closer to:

- when is the RI strategy in supportive context?
- when is it in hostile context?
- when is it in transition/ambiguity?

If those questions are more naturally answered at the trade-outcome level first, then it is admissible to explore that framing.
But only if the lane stays explicit that it is now solving a different problem than exact row-level authority recovery.

## What the new lane may and may not assume

### 4. Trade outcomes may be the primary authority surface

It is admissible in principle for the new lane to define ground truth primarily at the trade-outcome level.
That is the strongest part of the proposed pivot.

A later slice may therefore ask questions such as:

- what counts as a supportive trade outcome?
- what counts as a hostile trade outcome?
- what counts as a transition-sensitive or ambiguity-heavy trade outcome?

But those definitions must still be explicit, bounded, and honest about contradiction-year behavior.

### 5. Entry rows must remain the scoring-time surface

The pivot may **not** discard entry rows as the scoring surface.

Why:

- the advisory lane is still supposed to estimate context at or before entry time
- if entry rows stop mattering, the lane stops being an entry-time RI advisory question and becomes a different trade analysis program entirely

So the admissible framing is:

- **trade outcomes = primary authority surface**
- **entry rows = scoring-time surface**

That is the key structural rule of the new lane.

### 6. Partial coverage and uncertainty may be admitted explicitly

A later lane may allow:

- probabilistic mapping
- partial coverage
- confidence-weighted or uncertainty-aware labels
- explicit authority-strength flags

But only if all of the following remain true:

- missing coverage is reported plainly
- uncertainty is surfaced, not hidden
- partial coverage is not reframed as complete row-level authority
- no one claims Phase-2-faithful exact supportive/hostile row labels have been restored

So partial coverage is admissible only as an honest boundary, not as a rhetorical shortcut.

## What this pivot does not solve automatically

### 7. It does not repair the old exact contract

The pivot does **not** make any of the following suddenly true:

- exact row-level authority recovered
- old Phase 2 row-level contract restored
- same-surface continuation reopened
- Phase 4 opened

Those remain closed.

### 8. It creates a new set of blockers instead

If this new lane opens, the hard problems become:

- trade-level label definition
- mapping semantics from trade outcome back to entry-time signal
- leakage control
- honest handling of partial coverage
- contradiction-year robustness, especially on `2025`

That is acceptable.
But it must be acknowledged up front.

## ML remains out of scope for now

The roadmap already keeps ML behind deterministic framing.
That remains correct here.

If this new lane opens, the order must still be:

1. define trade-level authority semantics
2. define entry-time mapping semantics
3. build a small deterministic baseline
4. test it against `2025`
5. only then consider ML as comparator

So ML is not the next step in this pivot.

## Exact next admissible step

If this pivot is accepted, the next narrow governed step should be:

- **one docs-only trade-level label and mapping contract slice**

That next slice should define only:

1. a minimal trade-level supportive / hostile / transition taxonomy
2. what entry-time mapping outputs are allowed in principle
3. how partial coverage and uncertainty must be reported
4. what remains forbidden before any deterministic baseline implementation begins

That is the smallest honest next move.

## Bottom line

The old exact row-level authority path remains closed.
That does not mean the entire RI advisory idea is dead.

It does mean the next viable step must be a **new lane**:

- trade outcomes may become the primary authority surface
- entry rows remain the scoring-time surface
- partial coverage and uncertainty may be admitted explicitly
- exact row-level authority is not claimed to have been restored
- ML remains deferred until a deterministic baseline exists

So the honest verdict is:

- **pivot admissible in principle**
- **old exact authority path remains closed**
- **next step = docs-only trade-level label and mapping contract**
