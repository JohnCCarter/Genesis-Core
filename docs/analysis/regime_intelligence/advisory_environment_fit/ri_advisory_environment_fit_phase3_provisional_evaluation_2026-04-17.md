# RI advisory environment-fit — Phase 3 provisional evaluation verdict

This memo is docs-only and fail-closed.
It records the outcome of the bounded provisional-evaluation slice on the Phase C capture-v2 evidence surface.

Governance packet: `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_provisional_evaluation_packet_2026-04-17.md`

## Source surface used

This memo uses only already tracked surfaces:

- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_provisional_evaluation_admissibility_2026-04-17.md`
- `tmp/ri_advisory_environment_fit_provisional_evaluation_20260417.py`
- `results/research/ri_advisory_environment_fit/phase3_provisional_evaluation_2026-04-17/selector_consumption.json`
- `results/research/ri_advisory_environment_fit/phase3_provisional_evaluation_2026-04-17/proxy_surface.json`
- `results/research/ri_advisory_environment_fit/phase3_provisional_evaluation_2026-04-17/bucket_summary.json`
- `results/research/ri_advisory_environment_fit/phase3_provisional_evaluation_2026-04-17/closeout.md`
- `results/research/ri_advisory_environment_fit/phase3_provisional_evaluation_2026-04-17/manifest.json`

## Decision question

Did the bounded provisional-evaluation slice expose any non-empty exploratory realized-outcome proxy surface worth carrying forward?

## Short answer

**No — the slice stopped on a proxy-coverage gap.**

Overall verdict: `BLOCKED_PROXY_COVERAGE_GAP`.

The RI selector surface remained present and bounded.
But every allowed provisional realized-outcome proxy was null across the capture-v2 rows.

## What the slice proved

### 1. Selector discipline held

The slice consumed only the already-audited selector subset:

- `ri_clarity_score`
- `ri_clarity_raw`
- `bars_since_regime_change`
- `proba_edge`
- `conf_overall`
- `decision_size`
- `htf_regime`
- `zone`
- `action`
- `side`

The allowlist check passed.
No runtime-facing score implementation or forbidden label shortcut was introduced.

### 2. The provisional proxy surface is empty on realized rows

The three allowed realized-outcome proxies all had zero non-null coverage:

- `mfe_16_atr`: `0`
- `continuation_score`: `0`
- `fwd_16_atr`: `0`

That means the provisional slice had no non-empty proxy surface to bucket against the selector ranks.
So the resulting bucket table count was:

- `0`

This is a real blocker, not a reporting artifact.

## Why this matters

The lane has now tested two increasingly weaker evaluation openings against the same RI capture-v2 surface:

1. **Exact Phase 2 supportive / hostile evaluation surface**
   - blocked because `pnl_delta` and `active_uplift_cohort_membership` were missing
2. **Narrower provisional realized-outcome proxy surface**
   - blocked because even the allowed exploratory proxies were null on realized rows

So the current Phase C capture-v2 table is stronger than the old carrier on selector-side observability, but still too weak on realized evaluation-side coverage.

## What this slice did not do

This slice did **not**:

- substitute raw `total_pnl` sign
- reconstruct `pnl_delta`
- synthesize `active_uplift_cohort_membership`
- claim contradiction-year success
- claim Phase 2 supportive/hostile fidelity

That restraint is the main positive outcome here.
The slice stopped honestly instead of inflating weak evidence.

## Consequence for Phase 3

Phase 3 should now be read even more narrowly:

- RI-native selector readiness exists
- exact label authority is absent
- provisional proxy authority is also absent on realized rows

So the lane is **not** ready for any meaningful evaluation-oriented scoring slice on the current capture-v2 evidence table.

## Exact next admissible step

The next honest move is **not** more scoring.
It is one of these:

### Option A — docs-only proxy-coverage / realized-metrics admissibility review

Decide whether a bounded follow-up slice may reopen the RI capture surface specifically to materialize non-null realized path metrics or other strictly observational evaluation proxies without changing runtime behavior.

### Option B — lane pause / closeout for Phase 3 evaluation work

If no such observational follow-up can be justified cleanly, the lane should stop rather than keep weakening the evaluation contract.

## Bottom line

The provisional slice did useful governance work by proving another boundary clearly:

- **selector surface: still real**
- **exact label surface: absent**
- **provisional proxy surface: also absent on realized rows**

So the honest state now is:

- **evaluation-oriented Phase 3 work remains blocked on coverage, not just on label semantics**
- **the next admissible step is a docs-only proxy-coverage decision, or a bounded lane stop**
