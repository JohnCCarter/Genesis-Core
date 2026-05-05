# RI policy router insufficient-evidence discriminator-bundle displacement crosscheck

Date: 2026-04-30
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `read-only observational follow-up / deterministic local evidence`

## Question

The previous fixed March 2021 vs March 2025 target-only contrast suggested one candidate
separator bundle for the `insufficient_evidence` target rows:

- later `bars_since_regime_change` in 2021
- modestly stronger `action_edge`, `confidence_gate`, `clarity_raw`, and `clarity_score` in 2021
- opposite movement in `dwell_duration`

The next honest question was smaller and stricter: does that bundle remain special when checked
against the already-fixed nearby displacement rows inside the same March 2021 and March 2025
windows, or does it collapse into a generic target-vs-displacement distinction?

## Fixed surface

This slice is fail-closed to four pre-fixed cohorts only:

- 2021 target rows (`4`):
  - `2021-03-26T12:00:00+00:00`
  - `2021-03-27T06:00:00+00:00`
  - `2021-03-27T15:00:00+00:00`
  - `2021-03-28T00:00:00+00:00`
- 2021 nearby displacement rows (`2`):
  - `2021-03-26T15:00:00+00:00`
  - `2021-03-29T00:00:00+00:00`
- 2025 target rows (`5`):
  - `2025-03-14T15:00:00+00:00`
  - `2025-03-15T00:00:00+00:00`
  - `2025-03-15T09:00:00+00:00`
  - `2025-03-15T18:00:00+00:00`
  - `2025-03-16T03:00:00+00:00`
- 2025 nearby displacement rows (`2`):
  - `2025-03-13T15:00:00+00:00`
  - `2025-03-14T00:00:00+00:00`

Inputs were limited to:

- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2021_enabled_vs_absent_action_diffs.json`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2025_enabled_vs_absent_action_diffs.json`
- `data/curated/v1/candles/tBTCUSD_3h.parquet`

Artifact:

- `results/evaluation/ri_policy_router_insufficient_evidence_discriminator_bundle_displacement_crosscheck_2026-04-30.json`

## Cohort shape

The fixed target rows in both years keep the same blocked shape already documented in the prior
contrast note:

- `LONG -> NONE`
- `switch_reason = insufficient_evidence`
- `selected_policy = RI_no_trade_policy`
- `zone = low`
- `regime = balanced`
- `confidence_level = 0`
- `mandate_level = 0`
- `switch_proposed = false`
- `switch_blocked = false`

The nearby displacement rows in both years instead resolve as continuation-like rows:

- `NONE -> LONG`
- `switch_reason = stable_continuation_state`
- `selected_policy = RI_continuation_policy`
- `zone = low`
- `regime = balanced`
- `confidence_level = 3`
- `mandate_level = 3`

So this slice is not discovering a new class of rows; it is testing whether the earlier 2021-vs-2025
candidate bundle survives when the already-fixed targets are compared against their nearby local
continuation rows.

## What recurs in both years

The main result is that the candidate bundle mostly **recurs in the same direction inside both
years** when each year’s targets are compared against its already-fixed displacement rows.

### Recurrent target-minus-displacement pattern

In both 2021 and 2025, the target rows are weaker than the nearby displacement rows on:

- `action_edge`
  - 2021 target minus displacement: `-0.057958`
  - 2025 target minus displacement: `-0.090271`
- `confidence_gate`
  - 2021: `-0.028980`
  - 2025: `-0.045136`
- `clarity_raw`
  - 2021: `-0.035098`
  - 2025: `-0.054664`
- `clarity_score`
  - 2021: `-3.75`
  - 2025: `-5.6`
- forward-return and excursion proxies
  - `fwd_16`: `-1.448900` in 2021 and `-4.844852` in 2025
  - `mfe_16`: `-1.543733` in 2021 and `-4.331490` in 2025

In both years, the target rows are higher than nearby displacement rows on:

- `dwell_duration`
  - 2021: `+4.5`
  - 2025: `+7.5`
- `bars_since_regime_change`
  - 2021: `+0.25`
  - 2025: `+1.5`

That means the earlier target-only 2021-vs-2025 contrast does **not** stay unique when pushed
through this falsifier. The same directional bundle mostly separates blocked targets from nearby
continuation rows in both years.

## What this weakens

This materially weakens the idea that the earlier 2021-vs-2025 bundle is a clean harmful-year-only
selector.

Most of the previously surfaced fields now look more like a **generic target-vs-displacement
contrast** than a selective signature unique to the bad 2021 target cluster:

- later regime age is not 2021-specific here; targets sit later than nearby displacement rows in
  both years
- stronger `action_edge`, `confidence_gate`, and clarity values belong to displacement rows in both
  years, not just to one year’s target cluster
- `dwell_duration` also moves in the same direction in both years rather than acting like a clean
  harmful-year discriminator

So the falsifier does what it was supposed to do: it shrinks the interpretation surface.

## What still matters

This does **not** mean the 2021 and 2025 target rows are locally equivalent.

If anything, the 2025 target rows look even weaker relative to their nearby displacement rows on
most of the negative target-minus-displacement metrics:

- `action_edge`: `-0.090271` vs `-0.057958`
- `clarity_score`: `-5.6` vs `-3.75`
- `fwd_16`: `-4.844852` vs `-1.448900`
- `mfe_16`: `-4.331490` vs `-1.543733`

So the local selectivity problem remains real, but this specific bundle no longer looks like a clean
2021-vs-2025 runtime discriminator on its own.

## Bottom line

The fixed displacement crosscheck is a **falsifier success**:

- it reproduces the exact four-cohort row lock cleanly (`4 / 2 / 5 / 2`)
- it shows that the earlier candidate bundle mostly recurs as the same target-vs-displacement
  contrast in both years
- it therefore narrows the honest claim surface

The safest reading now is:

> the current discriminator bundle is better understood as a descriptive local contrast between
> blocked `insufficient_evidence` targets and nearby continuation-like displacement rows than as a
> standalone selective runtime rule for separating harmful and acceptable `insufficient_evidence`
> cases.

This bounded four-cohort crosscheck is observational only. Within the exact locked 2021/2025
cohorts, the candidate bundle mostly reappears as the same target-vs-displacement contrast in both
years; it does not establish a broader year-level rule and does not authorize runtime, policy,
default-behavior, promotion, or readiness changes.

## What this does not justify

This slice is descriptive/observational only.

It does **not** authorize:

- a runtime threshold change
- a router-policy change
- a family/champion/promotion claim
- a readiness conclusion
- widening into year-wide mining from this note alone
