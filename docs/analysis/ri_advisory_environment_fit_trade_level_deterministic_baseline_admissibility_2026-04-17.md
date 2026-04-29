# RI advisory environment-fit — trade-level deterministic baseline admissibility

This memo is docs-only and fail-closed.
It decides whether the new RI trade-level-authority lane now has enough contract structure to open one bounded deterministic baseline before any implementation or ML work begins.

Governance packet: `docs/decisions/ri_advisory_environment_fit_trade_level_deterministic_baseline_admissibility_packet_2026-04-17.md`

## Source surface used

- `plan/ri_advisory_environment_fit_roadmap_2026-04-16.md`
- `docs/analysis/ri_advisory_environment_fit_phase2_label_taxonomy_2026-04-16.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_direct_baseline_admissibility_2026-04-16.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_post_capture_v2_baseline_admissibility_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_trade_level_authority_admissibility_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_trade_level_label_mapping_contract_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_trade_level_evidence_family_leakage_boundary_2026-04-17.md`
- `docs/decisions/ri_advisory_environment_fit_trade_level_authority_admissibility_packet_2026-04-17.md`
- `docs/decisions/ri_advisory_environment_fit_trade_level_label_mapping_contract_packet_2026-04-17.md`
- `docs/decisions/ri_advisory_environment_fit_trade_level_evidence_family_leakage_boundary_packet_2026-04-17.md`

## Decision question

After fixing the trade-level authority pivot, the minimal label/mapping contract, and the evidence-family / leakage boundary, may the lane now open one bounded deterministic baseline?

## Short answer

**Yes — but only as a bounded trade-level baseline with explicit mapping weakness, explicit coverage gaps, and explicit contradiction-year reporting.**

That means:

- the lane may now define one deterministic trade-label surface
- the lane may now define one deterministic row-mapping surface
- the lane may not pretend that either surface restores exact row-level Phase-2 authority

So this is an admissibility opening for a small baseline, not a declaration of solved truth.

## Why a bounded baseline is now admissible

### 1. The lane now has the minimum contract layers that were previously missing

The earlier pivot slice fixed the structural reset:

- trade outcomes may be the primary authority surface
- entry rows remain the scoring-time surface
- partial coverage and uncertainty are explicit design features

The later contract slice then fixed:

- the minimal trade-level labels
- the minimal row-mapping outputs
- the rule that mapping outputs are not restored exact row labels

The evidence-boundary slice then fixed:

- which evidence families may define trade labels
- which entry-time field families may support row mapping
- which leakage shortcuts must fail the lane closed
- which reports must exist before any baseline can be reviewed honestly

Taken together, that is now enough structure to define one deterministic baseline without immediately collapsing into authority theater.

### 2. The baseline can now be scoped to two different but governed surfaces

The main blocker earlier was not just missing formulas.
It was missing surface discipline.

That surface discipline now exists:

- **trade-level deterministic labels** may later be built only from bounded realized-trade evidence families
- **entry-row deterministic mapping outputs** may later be built only from entry-time field families

Because those two surfaces are now separated explicitly, a deterministic baseline can be opened without letting post-entry evidence leak back into scoring-time inputs.

### 3. The new lane explicitly allows partial rather than fabricated completeness

The old exact row-level lane failed in part because it could not honestly recover complete exact authority on the row surface.
The new lane does not require that fiction.

A deterministic baseline is now admissible because it may say plainly that some items are:

- unsupported
- weakly anchored
- non-evaluable
- transition-heavy rather than cleanly directional

That is what makes this opening honest.
The baseline is allowed to be incomplete.
It is not allowed to hide that incompleteness.

## What the first deterministic baseline may include

### 1. Admissible trade-level outputs

The first deterministic baseline may define only the already-governed trade-level labels:

- `supportive_trade_outcome`
- `hostile_trade_outcome`
- `transition_trade_outcome`
- `non_evaluable_trade_context`

These labels must remain deterministic, bounded, and based only on the admissible realized-trade evidence families already defined:

- net realized outcome family
- path-quality / continuation family
- instability / mixed-behavior family
- coverage / evaluability family

### 2. Admissible row-level outputs

The first deterministic baseline may define only bounded row-mapping outputs such as:

- `supportive_context_likelihood`
- `hostile_context_likelihood`
- `transition_risk_likelihood`
- `authority_strength`
- `coverage_state`

These outputs must remain entry-time only and may use only the already admitted field families:

- clarity family
- regime-change recency / transition-proximity family
- probability / confidence family
- sizing / context descriptor family

### 3. Admissible reporting surface

The first deterministic baseline must report at minimum:

1. trade-level label coverage by year
2. row-level mapping coverage by year
3. unsupported / non-evaluable trade counts
4. unsupported / non-evaluable row counts
5. authority-strength distribution or equivalent weak/strong anchoring report
6. uncertainty reporting for weakly anchored mappings
7. explicit `2025` contradiction-year behavior
8. any material label imbalance that distorts interpretation

Those reports are part of admissibility, not optional extras.

## What the first deterministic baseline must keep out of scope

### 1. No restored exact row-level authority claims

Even if the baseline is useful, it may **not** claim:

- restored exact Phase-2-faithful row labels
- solved row-level authority recovery
- equivalence to the closed exact row-level lane

`NOT_RECOVERED` remains authoritative for the old problem.
This new baseline does not overwrite that.

### 2. No post-entry leakage into row mapping

The first deterministic baseline may **not** use any of the following as row-mapping inputs:

- raw `total_pnl`
- raw `total_pnl` sign
- `pnl_delta`
- `mfe_16_atr`
- `mae_16_atr`
- `fwd_*`
- `continuation_score`
- future-discovered cohort membership
- trade labels copied onto rows as if they were entry-time truth

That remains the hard leakage wall.

### 3. No full market-role or runtime claims

The first deterministic baseline may **not** open:

- runtime integration
- production-readiness
- Phase 4
- promotion framing
- ML comparison
- any full market-fit or comprehensive role-map claim beyond the bounded trade-label + row-mapping baseline itself

This lane still has to earn those later, if ever.

## Required failure classes for the first deterministic baseline

If the first deterministic baseline opens, it must report failure plainly rather than smoothing it away.
At minimum it must expose the following failure classes:

### 1. Discovery-year / contradiction-year inversion

If the baseline looks coherent on `2024` and collapses or inverts on `2025`, that must be explicit.
This is the lane's most important honesty check.

### 2. Unsupported-coverage failure

If too much of the trade or row surface remains unsupported or non-evaluable, that must be reported as a real limitation, not buried in averages.

### 3. Weak-authority failure

If mappings exist but most of them are weakly anchored, the baseline must say so plainly rather than presenting likelihood outputs as if they were strong authority.

### 4. Transition-junk-drawer failure

If `transition_trade_outcome` starts absorbing too many difficult cases without clear instability evidence, that must be reported as a baseline failure rather than accepted as taxonomic tidiness.

### 5. Label-imbalance failure

If supportive / hostile / transition counts are so imbalanced that apparent baseline coherence is mostly majority-class inertia, that must stay visible.

### 6. Leakage-boundary failure

If the baseline cannot be defined without importing post-entry evidence into row mapping, the lane must stop rather than weaken the boundary.

## What would make a deterministic baseline inadmissible after all

The opening is narrow and still fail-closed.
A deterministic baseline would become inadmissible if any of the following turned out to be necessary:

- hiding unsupported coverage for neat reporting
- using post-entry evidence as row-mapping input
- redefining mapped row outputs as restored exact authority
- relaxing the `2025` contradiction-year requirement
- widening the baseline into runtime, ML, or promotion semantics before the bounded research surface has even survived review

If that happens, the honest outcome is not “almost admissible.”
It is:

- **stop before formulas**

## Exact next admissible step

The next admissible move after this decision is:

- **one bounded deterministic trade-level baseline definition slice**

That slice should do only the following:

1. define deterministic rules for the four trade-level labels from the admitted realized-trade evidence families
2. define deterministic rules for the bounded row-mapping outputs from admitted entry-time field families only
3. define the exact coverage / authority-strength / uncertainty reports the baseline must emit
4. define the immediate fail-closed checks for `2025`, unsupported coverage, leakage, and label imbalance

That is the smallest honest move after admissibility.
It is still smaller than implementation and still safely below ML.

## Bottom line

The new trade-level lane now has enough structure to open one bounded deterministic baseline.

But that opening is tightly constrained:

- **trade-level labels:** allowed
- **entry-row mapping outputs:** allowed
- **coverage / uncertainty reporting:** mandatory
- **post-entry leakage into row mapping:** forbidden
- **restored exact row-level authority claims:** forbidden
- **`2025`:** mandatory contradiction-year check
- **ML / runtime / Phase 4:** still out of scope

So the honest verdict is:

- **bounded trade-level deterministic baseline: admissible**
- **old exact row-level authority problem: still closed**
- **next step: one bounded deterministic baseline-definition slice, not implementation**
