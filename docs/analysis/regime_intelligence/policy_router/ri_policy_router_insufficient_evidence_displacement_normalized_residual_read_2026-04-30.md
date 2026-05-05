# RI policy router insufficient-evidence displacement-normalized residual read

Date: 2026-04-30
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `completed / docs-only bounded residual reread / no behavior change`

## Question

The completed four-cohort displacement crosscheck already showed that the earlier March 2021 vs
March 2025 candidate bundle mostly recurs as the same target-vs-displacement contrast in both
years.

The next honest question is smaller still:

> after that generic target-vs-displacement pattern is accounted for, does any clean
> displacement-normalized discriminator remain on the current repo-visible surface?

This slice is a bounded reread of the already-emitted crosscheck artifact only. It does not reopen
source-row discovery, recompute normalization, introduce thresholds, or create a new artifact.

## Allowed input surface

This residual read is closed to the following existing evidence only:

- `results/evaluation/ri_policy_router_insufficient_evidence_discriminator_bundle_displacement_crosscheck_2026-04-30.json`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_discriminator_bundle_displacement_crosscheck_2026-04-30.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_selective_feature_gate_contrast_2026-04-30.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_local_window_2026-04-29.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_positive_year_insufficient_evidence_control_2026-04-29.md`

No fresh reads from the annual enabled-vs-absent JSON files, curated candles, or new local windows
were used here.

## Candidate-bundle residuals

The residual read is restricted to the previously surfaced candidate bundle fields:

- `bars_since_regime_change`
- `dwell_duration`
- `action_edge`
- `confidence_gate`
- `clarity_raw`
- `clarity_score`

### Same-sign recurrence survives on every candidate field

On the existing crosscheck artifact, every candidate bundle field keeps the **same sign direction in
both years** after target-minus-displacement normalization:

- `action_edge`
  - 2021 target minus displacement: `-0.057958`
  - 2025 target minus displacement: `-0.090271`
  - recurrence label: `same_negative`
  - gap-of-gaps (`2021 - 2025`): `+0.032313`
- `confidence_gate`
  - 2021: `-0.028980`
  - 2025: `-0.045136`
  - recurrence label: `same_negative`
  - gap-of-gaps: `+0.016156`
- `clarity_raw`
  - 2021: `-0.035098`
  - 2025: `-0.054664`
  - recurrence label: `same_negative`
  - gap-of-gaps: `+0.019566`
- `clarity_score`
  - 2021: `-3.75`
  - 2025: `-5.6`
  - recurrence label: `same_negative`
  - gap-of-gaps: `+1.85`
- `bars_since_regime_change`
  - 2021: `+0.25`
  - 2025: `+1.5`
  - recurrence label: `same_positive`
  - gap-of-gaps: `-1.25`
- `dwell_duration`
  - 2021: `+4.5`
  - 2025: `+7.5`
  - recurrence label: `same_positive`
  - gap-of-gaps: `-3.0`

So the residual surface does **not** contain a sign-changing discriminator inside the current
candidate bundle. Every field still points in the same direction in both years; only the magnitude
changes.

## What remains after normalization

What survives is a **magnitude skew**, not a clean directional selector.

Among the candidate bundle fields, the largest residual magnitude differences are:

- `dwell_duration`: `-3.0`
- `clarity_score`: `+1.85`
- `bars_since_regime_change`: `-1.25`

The smaller residuals are:

- `action_edge`: `+0.032313`
- `clarity_raw`: `+0.019566`
- `confidence_gate`: `+0.016156`

These are still real descriptive differences, but they no longer look like a clean
2021-vs-2025-selective discriminator bundle. On the current surface they read as:

- the same blocked-target-vs-displacement shape in both years,
- with 2025 usually showing a more severe negative target-minus-displacement skew,
- rather than a field that changes role or direction between the harmful and acceptable cases.

## Secondary observational context

The observational proxy fields behave the same way: they also remain same-direction residuals rather
than turning into a selective sign-changing discriminator.

Examples from the existing artifact:

- `fwd_16_close_return_pct`
  - recurrence label: `same_negative`
  - gap-of-gaps: `+3.395952`
- `fwd_8_close_return_pct`
  - recurrence label: `same_negative`
  - gap-of-gaps: `+2.306995`
- `mfe_16_pct`
  - recurrence label: `same_negative`
  - gap-of-gaps: `+2.787757`

That supports the same bounded reading: after normalization, what remains is mostly a **severity
skew**, not a new clean discriminator.

## Bounded null result

The most honest bounded conclusion on the current repo-visible four-cohort surface is:

> no clean displacement-normalized sign-changing discriminator survives once the generic
> target-vs-displacement pattern is accounted for.

This is a **bounded null read** of the allowed inputs only.

It does **not** mean:

- that no discriminator exists anywhere else,
- that the larger research question is globally closed forever,
- that the candidate metric family is disproven in every future bounded context.

It means only this:

- on the exact current four-cohort crosscheck surface,
- after accounting for the generic target-vs-displacement pattern,
- the remaining residuals are same-sign magnitude skews only,
- and that is not enough on this surface alone to justify a policy-router or runtime change.

## What this does not justify

This slice does **not** authorize:

- a runtime threshold change
- a router-policy change
- a family/champion/promotion claim
- a readiness conclusion
- reuse of this null result as a global statement of absence
- widening into year-wide mining from this note alone

## Consequence for the next step

If this line is reopened again, the next honest move should no longer be another reread of the same
artifact surface.

The cheapest admissible next step would need to be one of these:

- a genuinely new bounded evidence surface, or
- an explicit decision to park the line because the current repo-visible surface has already yielded
  a bounded null on the displacement-normalized question.

On the present surface, the cleanest answer is simply: **no rule candidate survives cleanly enough
yet**.
