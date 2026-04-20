# RI advisory environment-fit — Phase 3 bundle-surface reliability opening

This memo is docs-only and fail-closed.
It decides whether the newly materialized non-runtime evidence-bundle surface created a real next roadmap opening after the earlier capture-v2 surface was exhausted for same-surface authority-bearing continuation.

Governance packet: `docs/governance/ri_advisory_environment_fit_phase3_bundle_surface_reliability_opening_packet_2026-04-17.md`

## Source surface used

- `plan/ri_advisory_environment_fit_roadmap_2026-04-16.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_alternative_evidence_surface_admissibility_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_non_runtime_evidence_namespace_2026-04-17.md`
- `docs/governance/ri_advisory_environment_fit_phase3_phaseC_evidence_freeze_packet_2026-04-17.md`
- `docs/governance/ri_advisory_environment_fit_phase3_phaseC_evidence_capture_v2_packet_2026-04-17.md`
- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/capture_summary.json`
- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/manifest.json`
- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/closeout.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_partial_baseline_label_gap_2026-04-17.md`

## Decision question

Did the bundle-driven non-runtime evidence surface create a real next Phase 3 opening, and if so, what exactly is now open versus still closed?

## Short answer

**Yes — but only narrowly.**

The bundle-driven capture succeeded in a way the exhausted same-surface path never did:

- the evidence source is now a materially different non-runtime surface
- row-level realized-position joining succeeded with `146` matched positions and `0` unmatched positions
- containment stayed `PASS`
- the bundle hash stayed unchanged
- clarity coverage is complete on the realized rows (`146 / 146`, with `0` missing `ri_clarity_score`)

That is enough to say the roadmap now has a **real next opening**.
But it is not a full baseline opening.
It is only a narrow opening for **decision-reliability-side provisional work** on the RI selector surface.

## Why this counts as a real opening

### 1. The roadmap asked for a materially different evidence surface, and that now exists

The earlier admissibility decision already concluded that the roadmap could continue only if a materially different evidence surface was introduced.
The ledger-primary / bundle-secondary non-runtime surface is exactly that kind of change in footing.

This is not the old capture-v2 surface with another rhetorical retry.
It is a new evidence chain rooted in:

- frozen non-runtime bundle
- ledger classification
- bounded capture over that bundle

So the lane is no longer blocked on the question of whether a different surface can be materialized honestly.
That question is now answered `yes`.

### 2. The RI selector surface is now materially present on realized rows

The capture summary and closeout show the key improvement clearly:

- `matched_positions = 146`
- `unmatched_positions = 0`
- `bundle_enabled_rows = 146`
- `runtime_enabled_rows = 146`
- `missing_score_rows = 0`

This means the bundle-driven surface now carries a real, row-level RI selector table with:

- clarity present
- recency present
- probability/confidence context present
- bounded sizing/context descriptors present
- realized P&L/size/commission fields present as raw evidence

That is enough to reopen the narrow question of whether **decision reliability** can be explored honestly on this RI-native selector surface.

## Why the opening is narrow, not full

### 3. Exact Phase 2 supportive / hostile authority is still not restored on-row

The earlier label-gap memo remains relevant because the exact Phase 2 supportive / hostile contract is still not carried directly on the evidence rows.
The current capture summary still lists only raw outcome columns such as:

- `total_pnl`
- `total_size`
- `total_commission`
- ATR-normalized forward fields as allowed outputs

But the surface still does not claim on-row materialization of the exact Phase 2 authority fields such as:

- `pnl_delta`
- `active_uplift_cohort_membership`

So this capture does **not** reopen full supportive/hostile authority-bearing evaluation.
It reopens selector-side reliability work only.

### 4. Transition/disagreement evidence is still effectively closed on this surface

The capture summary reports:

- `shadow_mismatch_rows = 0` in both `2024` and `2025`
- `transition_guard_rows = 0` in both `2024` and `2025`

That means this surface does not currently show live disagreement/transition variation strong enough to justify opening an honest `transition_risk_score` lane.

So although the roadmap names `transition_risk_score` as a candidate output, this specific bundle-driven surface does not yet support opening it as a real next step.

### 5. `market_fit_score` remains even further away

`market_fit_score` was always the broadest Phase 3 role-map ambition.
If transition/disagreement evidence is still flat and exact supportive/hostile authority is still unresolved, then `market_fit_score` remains closed by even stronger logic.

Opening that now would overstate what this surface can support.

## What is now open

The only honest next opening is:

- **bounded, provisional `decision_reliability_score`-side work on the bundle-driven RI selector surface**

That opening is still constrained:

- non-runtime only
- advisory-only
- no Phase 2-faithful supportive/hostile claim by implication
- no `transition_risk_score` opening from this memo alone
- no `market_fit_score` opening from this memo alone
- no Phase 4 opening from this memo alone

This is a real opening because the lane is no longer blocked on selector-surface materiality.
But it is also honest because it keeps the still-missing authority surfaces closed.

## What remains closed

The following remain closed on the present surface:

- exact Phase 2 supportive / hostile authority restoration
- `transition_risk_score` as a real opened output lane
- `market_fit_score`
- Phase 4 shadow multi-year evaluation
- runtime-readiness or any promotion framing

## Outcome relative to the user-approved stop condition

The user-defined completion condition allowed the work to stop at either:

- a **next real roadmap opening**, or
- a clean lane-close recommendation

This memo reaches the first condition.

The next real roadmap opening is now explicit:

- **decision-reliability-side provisional work is admissibly open on the bundle-driven RI surface**

That is the cleanest honest stopping point for the current autonomous block.

## Bottom line

The bundle-driven non-runtime surface did enough to move the roadmap forward.
It did **not** open the whole Phase 3 role-map ambition.
But it did open one real and useful next step:

- **a narrow provisional reliability lane on real RI selector evidence**

Everything broader than that remains closed until later evidence or later review reopens it explicitly.
