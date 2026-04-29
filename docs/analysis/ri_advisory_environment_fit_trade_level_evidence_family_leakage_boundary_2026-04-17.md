# RI advisory environment-fit — trade-level evidence family and leakage boundary

This memo is docs-only and definitional.
It defines which evidence families are admissible for future trade-level authority labels and which leakage boundaries must remain fail-closed before any deterministic baseline is considered in the new RI trade-level-authority lane.

Governance packet: `docs/governance/ri_advisory_environment_fit_trade_level_evidence_family_leakage_boundary_packet_2026-04-17.md`

## Source surface used

- `plan/ri_advisory_environment_fit_roadmap_2026-04-16.md`
- `docs/analysis/ri_advisory_environment_fit_phase2_label_taxonomy_2026-04-16.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_partial_baseline_label_gap_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_provisional_evaluation_admissibility_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_reliability_exact_label_authority_preflight_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_post_exact_label_authority_preflight_admissibility_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_materially_different_surface_inventory_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_trade_level_authority_admissibility_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_trade_level_label_mapping_contract_2026-04-17.md`
- `docs/governance/ri_advisory_environment_fit_trade_level_authority_admissibility_packet_2026-04-17.md`
- `docs/governance/ri_advisory_environment_fit_trade_level_label_mapping_contract_packet_2026-04-17.md`
- `docs/governance/ri_advisory_environment_fit_phase2_label_taxonomy_packet_2026-04-16.md`

## Why this slice is needed

The previous two trade-level slices already fixed two important things:

- authority may now live primarily on the trade-outcome surface
- entry rows remain the scoring-time surface
- row outputs must stay explicit about coverage and uncertainty

But those slices did not yet define the evidence boundary.
Without that boundary, the lane could still drift in two dangerous directions:

- a trade-level label contract that quietly collapses into raw P&L sign memory
- a row-mapping lane that smuggles post-entry information back into entry-time scoring

This slice exists to stop exactly that drift.

## Core boundary rule

The lane must keep **trade-label construction evidence** separate from **row-mapping / scoring-time evidence**.

### Trade-label construction evidence

This is the evidence family used later to judge a completed trade as:

- `supportive_trade_outcome`
- `hostile_trade_outcome`
- `transition_trade_outcome`
- `non_evaluable_trade_context`

It may use realized trade evidence because it lives on the ex-post authority surface.

### Row-mapping / scoring-time evidence

This is the evidence family later used to map trade-level authority back toward entry rows.
It must be available at or before entry time.
It may describe resemblance, risk, likelihood, authority strength, and coverage.
It may not quietly import post-entry outcomes.

These two surfaces may be related.
They may not be merged.

## Admissible realized-trade evidence families

The new lane does **not** yet operationalize formulas.
But it may define bounded evidence families that a later slice can use when implementing trade-level authority labels.

### 1. Net realized outcome family

This family covers whether the completed trade ended with economically favorable or unfavorable realized outcome on the governed evaluation surface.

Examples of evidence kinds in this family include:

- realized net outcome after costs
- realized outcome normalized by trade scale or bounded risk anchor
- realized direction after fees/size are accounted for

Why this family is admissible:

- trade labels are ex-post authority labels
- some bounded notion of realized favorable vs unfavorable outcome is necessary if supportive and hostile labels are to mean anything at all

Boundary rule:

- raw `total_pnl` sign alone is not sufficient by itself
- this family must later be combined with other bounded evidence so the lane does not degrade into naive winner/loser relabeling

### 2. Path-quality / continuation family

This family covers how the trade behaved after entry rather than only where it finished.

Examples of evidence kinds in this family include:

- bounded forward path development
- continuation versus failure-to-follow-through behavior
- realized favorable excursion versus adverse excursion balance

Why this family is admissible:

- a transition-heavy or ambiguity-heavy trade can look different from a clean supportive or hostile trade even when final realized outcome alone looks similar
- path shape can help distinguish steady follow-through from noisy or unstable behavior

Boundary rule:

- path metrics may support trade-level authority labels only
- they may not later be reused as entry-time row-mapping inputs, because they are post-entry by construction

### 3. Instability / mixed-behavior family

This family covers whether the trade is better explained as instability-dominated than as clean supportive or hostile context.

Examples of evidence kinds in this family include:

- mixed or whipsaw-like realized path behavior
- weak net outcome paired with unstable path shape
- evidence that the trade resists clean directional interpretation even after bounded realized-trade review

Why this family is admissible:

- `transition_trade_outcome` must be a real label, not a cosmetic synonym for “uncertain”
- the lane needs a principled way to say that a trade was instability-sensitive rather than simply good or bad

Boundary rule:

- transition must remain narrow and evidence-based
- it may not become a junk drawer for every inconvenient trade

### 4. Coverage / evaluability family

This family covers whether the trade can be labeled at all under the governed authority surface.

Examples of evidence kinds in this family include:

- missing or insufficient admissible evidence
- conflicting evidence with no bounded resolution
- too-weak authority signal to justify supportive / hostile / transition classification

Why this family is admissible:

- the lane explicitly allows partial coverage now
- `non_evaluable_trade_context` must remain a first-class state rather than a hidden cleanup bucket

Boundary rule:

- non-evaluable is a coverage state, not a disguised hostile or ambiguous label

## Entry-time field families admissible for later row mapping

Later row mapping must stay on the scoring-time surface.
That means it may use only field families that are observable at or before entry.

### 5. Clarity family

This family includes already observable RI clarity information that can describe how clean or noisy the entry-time context looked.

Examples:

- `ri_clarity_score`
- `ri_clarity_raw`

Why it is admissible:

- clarity already lives on the entry-time surface
- it can support likelihood-style mapping without importing post-entry outcome knowledge

### 6. Regime-change recency / transition-proximity family

This family includes already observable entry-time descriptors of regime-change proximity or transition pressure.

Examples:

- `bars_since_regime_change`
- other entry-time transition-proximity descriptors already observable before or at entry

Why it is admissible:

- the lane needs a bounded way to map transition-sensitive trade authority back toward entry-time context
- recency is admissible because it remains entry-time information

### 7. Probability / confidence family

This family includes already available pre-entry predictive context.

Examples:

- `proba_*`
- `conf_*`
- bounded confidence or edge descriptors already present at scoring time

Why it is admissible:

- these fields are already available when the advisory question is asked
- they may help later mapping estimate resemblance to supportive or hostile trade contexts

### 8. Sizing / context descriptor family

This family includes already available entry-time context helpers that are not themselves authority labels.

Examples:

- `decision_size`
- `zone`
- `htf_regime`
- other bounded context descriptors already present at entry

Why it is admissible:

- these help describe what kind of context the entry row lived in
- they remain observational rather than authority-bearing by themselves

## What must remain separated

### Trade labels may use realized-trade evidence

That includes bounded use of:

- net realized outcome
- path-quality evidence
- instability / mixed-behavior evidence
- evaluability evidence

### Row mapping may use entry-time evidence only

That includes bounded use of:

- clarity
- transition proximity
- confidence / probability context
- sizing / context descriptors

### They may not cross over by default

This means:

- post-entry path metrics may not become row-mapping features
- realized trade outcome may not become a scoring-time field
- a future trade label may not be copied onto an entry row as if the row itself had direct exact authority

That is the boundary that keeps the new lane honest.

## Explicit leakage prohibitions

### Forbidden in row mapping and later deterministic scoring

The following remain forbidden as row-mapping or scoring-time inputs:

- raw `total_pnl`
- raw `total_pnl` sign
- `pnl_delta`
- `mfe_16_atr`
- `mae_16_atr`
- `fwd_4_atr`
- `fwd_8_atr`
- `fwd_16_atr`
- `continuation_score`
- any future-discovered cohort membership
- any post-entry trade-label assignment used as if it were scoring-time truth

Why:

- every one of those surfaces is post-entry or ex-post by nature
- using them in row mapping would recreate the exact leakage problem the lane is trying to escape

### Forbidden in trade-label construction shortcuts

The following also remain forbidden as sole trade-label rules:

- raw positive realized P&L sign alone
- raw negative realized P&L sign alone
- discovery-year success memory alone
- contradiction-year blindness

Why:

- the lane must avoid becoming a relabeled 2024 memory exercise
- trade-level authority must still remain bounded, multi-factor, and contradiction-aware

## Discovery-year and contradiction-year discipline

The lane still needs explicit year discipline.
That does not disappear just because authority moved from rows to trades.

### `2024`

`2024` may still help discovery, definition, or shaping in a later bounded slice.
But it may not become universal label truth by itself.

### `2025`

`2025` remains the mandatory contradiction-year check.
Any later deterministic baseline in this lane must say plainly whether its trade-label logic and row-mapping logic stay coherent or invert there.

If the lane looks persuasive only on discovery-friendly evidence and collapses on `2025`, that collapse must stay visible.

## Mandatory reporting before a deterministic baseline is admissible

Before any future deterministic baseline can even be reviewed honestly, the lane must report at minimum:

1. trade-level label coverage by year
2. row-level mapping coverage by year
3. unsupported / non-evaluable trade counts
4. unsupported / non-evaluable row counts
5. authority-strength distribution or equivalent weak/strong anchoring report
6. uncertainty reporting for weakly anchored mappings
7. explicit `2025` contradiction-year behavior
8. any material label imbalance that would make supportive / hostile / transition interpretation misleading

Those reporting requirements are not polish.
They are the minimum honesty layer for the new lane.

## What this boundary does not authorize

This slice does **not** authorize:

- implementation of trade-level labels
- implementation of row mapping
- deterministic baseline scoring
- ML comparison
- runtime integration
- Phase 4

It only says what evidence families may exist later and what leakage boundaries must remain fail-closed.

## Exact next admissible step

The next admissible move after this boundary is:

- **one docs-only trade-level deterministic baseline admissibility slice**

That next slice should decide only:

1. whether the lane now has enough contract structure to define one bounded deterministic trade-label + row-mapping baseline
2. what that baseline must keep explicitly out of scope
3. what failure classes it must report immediately if opened

That is still smaller than implementation and still cleaner than jumping straight into formulas.

## Bottom line

The new lane now has a stronger fail-closed boundary:

- **trade-label construction evidence:** bounded realized-trade evidence families only
- **row-mapping evidence:** entry-time field families only
- **leakage rule:** no post-entry path or outcome evidence may enter row mapping by default
- **coverage rule:** unsupported trades and rows must remain visible
- **year rule:** `2025` remains mandatory as contradiction-year check

That is enough structure to keep the pivot honest for one more governed step without sliding back into row-level authority theater.
