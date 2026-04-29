# RI advisory environment-fit — Phase 3 proxy-coverage admissibility

This memo is docs-only and fail-closed.
It decides whether the next admissible step after `BLOCKED_PROXY_COVERAGE_GAP` is a bounded observational proxy-coverage audit, or whether evaluation-side Phase 3 work should stop.

Governance packet: `docs/decisions/ri_advisory_environment_fit_phase3_proxy_coverage_admissibility_packet_2026-04-17.md`

## Source surface used

This memo uses only already tracked surfaces:

- `docs/analysis/ri_advisory_environment_fit_phase2_label_taxonomy_2026-04-16.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_post_capture_admissibility_2026-04-16.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_post_capture_v2_baseline_admissibility_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_partial_baseline_label_gap_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_provisional_evaluation_2026-04-17.md`
- `tmp/ri_advisory_environment_fit_capture_v2_20260417.py`
- `tmp/ri_advisory_environment_fit_capture_20260416.py`
- `tmp/ri_advisory_environment_fit_provisional_evaluation_20260417.py`
- `tmp/current_atr_900_env_profile_20260416.py`
- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/entry_rows.ndjson`
- `results/research/ri_advisory_environment_fit/phase3_provisional_evaluation_2026-04-17/proxy_surface.json`
- `results/research/ri_advisory_environment_fit/phase3_provisional_evaluation_2026-04-17/manifest.json`
- `results/research/ri_advisory_environment_fit/phase3_partial_baseline_preflight_2026-04-17/label_surface_audit.json`
- `results/research/ri_advisory_environment_fit/phase3_ri_evidence_capture_2026-04-16/entry_rows.ndjson`

## Decision question

After the provisional slice stopped on `BLOCKED_PROXY_COVERAGE_GAP`, is there one smaller honest follow-up that can audit the missing realized-proxy coverage directly, or is evaluation-side Phase 3 work now fully blocked?

## Short answer

**Yes — one bounded observational proxy-coverage audit is admissible.**

But it is admissible only because the blocker is now narrow and local:

- the selector surface is real
- the exact Phase 2 label surface is still blocked for separate reasons
- the provisional proxy surface is empty because the capture-v2 rows are missing the ATR-normalization anchor that the raw realized-path proxy formulas currently require

So the next admissible move is **not** more scoring.
It is one bounded audit of proxy coverage / normalization availability.

## What the provisional slice actually proved

The provisional slice ended with:

- `overall_verdict = BLOCKED_PROXY_COVERAGE_GAP`
- `bucket_row_count = 0`
- `mfe_16_atr.non_null_count = 0`
- `continuation_score.non_null_count = 0`
- `fwd_16_atr.non_null_count = 0`

That proved the bounded exploratory score slice had no realized proxy surface to work with.

It did **not** prove that RI selector observability failed.
It proved that the realized-path proxy columns never materialized.

## Root cause is now specific, not general

### 1. Capture-v2 computes the proxy family only when `entry_atr` exists

In `tmp/ri_advisory_environment_fit_capture_v2_20260417.py`:

- `_aggregate_positions()` stores `entry_atr` from `trade.entry_fib_debug.ltf.atr`
- `_compute_path_metrics()` sets `atr = pos.entry_atr`
- if `atr` is missing or non-positive, all ATR-normalized realized-path metrics become `None`

That means the provisional proxy family is structurally dependent on the captured `entry_atr` field.
### 2. On the v2 evidence table, `entry_atr` is missing everywhere

The label-gap constraint for this slice comes from
`docs/analysis/ri_advisory_environment_fit_phase3_partial_baseline_label_gap_2026-04-17.md`
as a governance boundary source only.
No standalone `label_surface_audit.json` artifact is asserted for the current workspace state.

The capture-v2 rows show `entry_atr: null` on the realized rows.

Direct verification on the tracked artifact returned:

- `v2_null = 146`
- `v2_numeric = 0`

The same tracked rows also show `current_atr_used` populated rather than null on the v2 surface.

So the blocker is not “no possible normalization field exists anywhere.”
The blocker is that the current proxy formulas are wired to `entry_atr`, and that specific anchor is absent on the v2 realized rows.

### 3. This is not how the earlier capture behaved

The earlier fixed-carrier capture surface did materialize this same proxy family.

Direct verification on the older tracked capture returned:

- `v1_numeric = 167` for `entry_atr`

And the tracked older `entry_rows.ndjson` examples show the same path-metric family with non-null values for:

- `entry_atr`
- `mfe_16_atr`
- `fwd_16_atr`
- `continuation_score`

So the problem is not a generic candle-join bug or a broken bucket routine.
It is a narrower capture-surface / normalization-anchor gap specific to the Phase C v2 evidence rows.

## Why that makes a bounded follow-up admissible

This lane has already separated three different blockers cleanly:

1. **selector readiness**
   - open
2. **exact Phase 2 label authority**
   - still blocked on `pnl_delta` + `active_uplift_cohort_membership`
3. **provisional proxy coverage**
   - blocked because ATR-normalized realized proxies cannot materialize without a usable anchor

The third blocker is narrower than the second.
It can be studied without pretending to solve the exact supportive/hostile contract.

That makes one bounded observational follow-up admissible, provided it stays inside a very small box.

## Exact admissible next step

The next admissible step is one bounded **proxy-coverage / normalization-anchor audit**.

That slice may do only the following:

1. audit the relationship between `entry_atr` and already captured pre-entry ATR fields on tracked surfaces where both are present
2. determine whether `current_atr_used` is an observationally admissible normalization anchor for the provisional proxy family on the v2 rows
3. if and only if that audit stays clean, materialize a strictly provisional realized-path proxy surface in a separate research-only artifact set
4. report coverage only

That slice must remain explicitly below the level of any renewed scoring or evaluation claim.

## What remains forbidden even if that follow-up opens

Even a successful proxy-coverage audit would **not** authorize:

- exact Phase 2 supportive/hostile evaluation
- `pnl_delta` reconstruction
- synthetic `active_uplift_cohort_membership`
- contradiction-year pass/fail claims
- `market_fit_score` claims
- runtime integration
- role-map implementation

Most importantly:

- a usable provisional proxy surface would still be **proxy** evidence only
- it would not repair the separate `BLOCKED_LABEL_GAP`

## Required stop condition for the next slice

The next slice must stop immediately if either of these becomes true:

1. equivalence between `entry_atr` and the candidate fallback anchor cannot be supported cleanly from tracked evidence
2. restoring proxy coverage would require semantic relabeling, runtime-path changes, or hidden rewriting of the Phase 2 contract

If that happens, the honest verdict should be:

- `BLOCKED_NORMALIZATION_AUTHORITY_GAP`

## Consequence for Phase 3

Phase 3 evaluation-side work is not fully dead, but it must get smaller.

The new order is:

1. do **not** reopen scoring
2. do **not** reopen label semantics
3. audit the proxy-coverage gap as a normalization-surface issue only
4. stop again if that narrower audit cannot be justified cleanly

## Bottom line

The provisional slice did not show that the RI lane lacks selector structure.
It showed something narrower and more actionable:

- the current v2 realized rows do not carry the `entry_atr` anchor that the provisional realized-path proxy formulas depend on

That makes one more bounded research step admissible:

- **a proxy-coverage / normalization-anchor audit**

It does **not** make renewed scoring admissible, and it does **not** unblock the separate exact-label gap.
