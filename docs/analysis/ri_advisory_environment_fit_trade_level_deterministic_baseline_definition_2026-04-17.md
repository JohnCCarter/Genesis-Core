# RI advisory environment-fit — trade-level deterministic baseline definition

This memo is docs-only and definitional.
It defines the first bounded deterministic baseline for the new RI trade-level-authority lane.

Governance packet: `docs/governance/ri_advisory_environment_fit_trade_level_deterministic_baseline_definition_packet_2026-04-17.md`

## Source surface used

- `plan/ri_advisory_environment_fit_roadmap_2026-04-16.md`
- `docs/analysis/ri_advisory_environment_fit_phase2_label_taxonomy_2026-04-16.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_direct_baseline_admissibility_2026-04-16.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_post_capture_v2_baseline_admissibility_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_trade_level_authority_admissibility_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_trade_level_label_mapping_contract_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_trade_level_evidence_family_leakage_boundary_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_trade_level_deterministic_baseline_admissibility_2026-04-17.md`
- `docs/governance/ri_advisory_environment_fit_trade_level_authority_admissibility_packet_2026-04-17.md`
- `docs/governance/ri_advisory_environment_fit_trade_level_label_mapping_contract_packet_2026-04-17.md`
- `docs/governance/ri_advisory_environment_fit_trade_level_evidence_family_leakage_boundary_packet_2026-04-17.md`
- `docs/governance/ri_advisory_environment_fit_trade_level_deterministic_baseline_admissibility_packet_2026-04-17.md`

## Why this slice is needed

The admissibility decision already answered **whether** a bounded deterministic baseline may exist.
What remained open was **what exact baseline gets defined**.

Without this definition slice, the lane would still be exposed to two kinds of drift:

- trade-level labels that look deterministic in prose but hide fuzzy fallback rules
- row-mapping outputs that quietly smuggle post-entry knowledge back into the scoring-time surface

This slice fixes that by defining one rule-ordered baseline and one reporting contract.

## Core baseline rule

The first baseline must remain split across two governed surfaces:

- **trade-level authority labels**
- **entry-row mapping outputs**

The trade surface may use realized-trade evidence families only.
The row surface may use entry-time field families only.
The baseline is deterministic only if that split stays explicit all the way through.

## Trade-level deterministic label surface

The first baseline must emit only the already admitted trade-level labels:

- `supportive_trade_outcome`
- `hostile_trade_outcome`
- `transition_trade_outcome`
- `non_evaluable_trade_context`

### Required predicate layer

Before any trade label is assigned, the later implementation must materialize a bounded predicate layer from the already admitted realized-trade evidence families.
That predicate layer must stay deterministic and must expose at minimum:

1. **coverage / evaluability predicate**
   - can the trade be judged at all on the admitted authority surface?
2. **net realized outcome direction predicate**
   - is the bounded realized-trade outcome favorable, unfavorable, or unresolved?
3. **path-quality predicate**
   - does the realized path support follow-through, oppose follow-through, or remain mixed?
4. **instability predicate**
   - does the realized trade look instability-dominated rather than directionally clean?

This slice does **not** choose implementation thresholds for those predicates.
It defines the deterministic rule order that must consume them.

### Deterministic trade-label rule order

Trade labels must be assigned in this exact order:

#### 1. Coverage gate

If the coverage / evaluability predicate fails, the trade must be labeled:

- `non_evaluable_trade_context`

This gate comes first and may not be bypassed by directional eagerness.

#### 2. Transition gate

If the instability predicate is true, and the trade is better explained as mixed or unstable than as cleanly directional, the trade must be labeled:

- `transition_trade_outcome`

This gate must fire before supportive or hostile assignment.
That keeps transition narrow, explicit, and evidence-based.

#### 3. Supportive gate

If all of the following are true:

- coverage / evaluability passed
- transition gate did not fire
- net realized outcome direction is favorable
- path-quality predicate is supportive rather than mixed or hostile

then the trade must be labeled:

- `supportive_trade_outcome`

#### 4. Hostile gate

If all of the following are true:

- coverage / evaluability passed
- transition gate did not fire
- net realized outcome direction is unfavorable
- path-quality predicate is hostile rather than mixed or supportive

then the trade must be labeled:

- `hostile_trade_outcome`

#### 5. Conflict fallback

If coverage passed but the directional predicates remain unresolved or contradictory after the gates above, the trade must fall back to:

- `non_evaluable_trade_context`

That fallback is required so the baseline does not pretend that every difficult trade is classifiable.

## Trade-label shortcut prohibitions

The baseline may **not** define trade labels using any of these shortcuts:

- raw `total_pnl` sign alone
- discovery-year success memory alone
- a path-quality rule reused as if it were entry-time evidence
- a transition label used as a cleanup bucket for every awkward case

A deterministic baseline is allowed to be simple.
It is not allowed to be lazy.

## Entry-row deterministic mapping surface

The first baseline must emit only the already admitted bounded row outputs:

- `supportive_context_likelihood`
- `hostile_context_likelihood`
- `transition_risk_likelihood`
- `authority_strength`
- `coverage_state`

### Required entry-time input families

Later implementation may derive mapping outputs only from the already admitted entry-time families:

- clarity family
- regime-change recency / transition-proximity family
- probability / confidence family
- sizing / context descriptor family

No post-entry field may enter this surface.
That prohibition remains absolute.

### Required mapping input bands

The first baseline must normalize those entry-time families into deterministic bands before assigning row outputs.
At minimum, the row surface must expose:

1. `clarity_band`
   - `low | medium | high`
2. `transition_proximity_band`
   - `near | mid | far`
3. `confidence_band`
   - `weak | mixed | strong`
4. `context_support_band`
   - `adverse | mixed | supportive`

This slice does **not** choose runtime thresholds for those bands.
It defines the deterministic combinations that the bands must drive.

### Deterministic output domains

The first baseline must use the following bounded output domains:

- `supportive_context_likelihood ∈ {0, 1, 2, 3}`
- `hostile_context_likelihood ∈ {0, 1, 2, 3}`
- `transition_risk_likelihood ∈ {0, 1, 2, 3}`
- `authority_strength ∈ {0, 1, 2, 3}`
- `coverage_state ∈ {direct_trade_anchor, partial_inference, unsupported, non_evaluable_trade_context}`

The scale is ordinal:

- `0 = none`
- `1 = low`
- `2 = medium`
- `3 = high`

## Deterministic row-mapping rule order

### 1. Coverage-state gate

Before any likelihood output is trusted, the baseline must assign `coverage_state` first.

#### `unsupported`

Use when one or more required core entry-time input families are missing.
That means the row may not receive directional interpretation from guessed values.

#### `non_evaluable_trade_context`

Use when the linked trade label itself is `non_evaluable_trade_context`.
That state must propagate clearly rather than being disguised as weak hostility or weak support.

#### `partial_inference`

Use when the row has enough entry-time inputs to compute bounded likelihoods, but one or more non-core mapping ingredients are incomplete or the resulting mapping remains weakly anchored.

#### `direct_trade_anchor`

Use only when:

- the linked trade label is evaluable
- all required entry-time input families are present
- the row mapping can be computed without any leakage shortcut

### 2. Transition-risk rule

`transition_risk_likelihood` must be assigned before directional likelihood dominance is interpreted.

The rule order must be:

- assign `3` when transition proximity is `near` and clarity is not `high`, or when transition proximity is `near` and confidence is not `strong`
- assign `2` when exactly one strong transition-sensitive condition is present and the row is still evaluable
- assign `1` when only weak transition-sensitive evidence is present
- assign `0` otherwise

This keeps transition tied to entry-time proximity and degraded clarity/confidence rather than to ex-post noise.

### 3. Supportive-likelihood rule

`supportive_context_likelihood` must be assigned from supportive entry-time structure only.

The rule order must be:

- assign `3` when clarity is `high`, transition proximity is `far`, confidence is `strong`, and context support is `supportive`
- assign `2` when at least three of those supportive conditions hold and transition risk is not dominant
- assign `1` when exactly two supportive conditions hold and hostile evidence is not dominant
- assign `0` otherwise

### 4. Hostile-likelihood rule

`hostile_context_likelihood` must be assigned from adverse entry-time structure only.

The rule order must be:

- assign `3` when clarity is `low`, confidence is `weak`, context support is `adverse`, and transition risk is not dominant
- assign `2` when at least three hostile conditions hold and the row is still directional rather than transition-dominant
- assign `1` when exactly two hostile conditions hold and supportive evidence is not dominant
- assign `0` otherwise

### 5. Authority-strength rule

`authority_strength` must be assigned after coverage and directional likelihoods are known.

The rule order must be:

- assign `0` when `coverage_state = unsupported` or `coverage_state = non_evaluable_trade_context`
- assign `1` when the row is evaluable but no likelihood output exceeds `1`
- assign `2` when one likelihood output is `2` and competing outputs remain materially lower
- assign `3` when one likelihood output is `3`, competing outputs remain at most `1`, and `coverage_state = direct_trade_anchor`

This keeps authority strength tied to both separability and coverage.

## Required reporting surface

Any later implementation of this baseline must emit at minimum:

1. trade-level label counts by year
2. row-level coverage-state counts by year
3. row-level likelihood-band counts by year
4. authority-strength distribution by year
5. unsupported and non-evaluable counts by year
6. `transition_trade_outcome` share by year
7. explicit `2024` versus `2025` comparison for every trade label and every row output family
8. label-imbalance warnings when one directional class materially dominates the others
9. weak-authority warnings when most evaluable rows remain at authority strength `0` or `1`
10. contradiction-year warnings when `2025` materially inverts the discovery-year story

These reports are baseline requirements, not cleanup work for later.

## Immediate fail-closed checks

The first deterministic baseline must stop or report failure plainly if any of the following occurs:

### 1. Raw-P&L-only failure

If supportive or hostile trade labels can be defined only by raw realized P&L sign memory, the baseline is not honest enough to continue.

### 2. Leakage-boundary failure

If any row-mapping output requires post-entry fields such as `total_pnl`, `pnl_delta`, `mfe_16_atr`, `mae_16_atr`, `fwd_*`, `continuation_score`, or future cohort membership, the baseline must stop.

### 3. Coverage-collapse failure

If unsupported plus non-evaluable states dominate the surface so strongly that directional interpretation becomes mostly absent, that failure must remain explicit.

### 4. Transition-junk-drawer failure

If `transition_trade_outcome` absorbs difficult cases without real instability evidence, the baseline must report that as taxonomic failure.

### 5. Weak-authority failure

If most rows remain weakly anchored even when trade labels are evaluable, that must be reported as baseline weakness rather than hidden inside averages.

### 6. Contradiction-year inversion

If `2024` and `2025` tell materially opposite stories for the same baseline surface, that inversion must remain explicit.

## What this definition does not solve

This slice still does **not** solve:

- restored exact row-level authority
- runtime readiness
- Phase 4
- ML comparison
- full market-role or promotion claims

It defines the first bounded baseline.
It does not certify that baseline as successful.

## Exact next admissible step

The next admissible move after this definition is:

- **one bounded implementation-readiness slice for the trade-level deterministic baseline**

That next slice should decide only:

1. whether the predicate layer and band layer can be materialized cleanly from already admitted surfaces
2. whether the implementation can stay fully below runtime and ML surfaces
3. what exact artifacts and fail-closed outputs the first implementation slice must emit

That is the smallest honest move after definition.

## Bottom line

The new lane now has a defined first deterministic baseline:

- trade labels use a fixed gate order
- row mapping uses fixed entry-time bands and fixed output domains
- coverage and authority remain explicit
- leakage remains fail-closed
- `2025` remains mandatory

So the honest new state is:

- **trade-level deterministic baseline: now defined in bounded form**
- **old exact row-level authority problem: still closed**
- **next step: one bounded implementation-readiness slice, not runtime implementation**
