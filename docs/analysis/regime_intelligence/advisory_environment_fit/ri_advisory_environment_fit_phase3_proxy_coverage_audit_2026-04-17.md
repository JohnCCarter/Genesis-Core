# RI advisory environment-fit — Phase 3 proxy-coverage audit verdict

This memo is fail-closed and research-only.
It records the outcome of the bounded proxy-coverage / normalization-anchor audit on the Phase C capture-v2 evidence surface.

Governance packet: `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_proxy_coverage_audit_packet_2026-04-17.md`

## Source surface used

This memo uses only already tracked surfaces:

- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_proxy_coverage_admissibility_2026-04-17.md`
- `tmp/ri_advisory_environment_fit_proxy_coverage_audit_20260417.py`
- `results/research/ri_advisory_environment_fit/phase3_proxy_coverage_audit_2026-04-17/normalization_audit.json`
- `results/research/ri_advisory_environment_fit/phase3_proxy_coverage_audit_2026-04-17/proxy_surface.json`
- `results/research/ri_advisory_environment_fit/phase3_proxy_coverage_audit_2026-04-17/materialized_proxy_rows.ndjson`
- `results/research/ri_advisory_environment_fit/phase3_proxy_coverage_audit_2026-04-17/manifest.json`
- `results/research/ri_advisory_environment_fit/phase3_proxy_coverage_audit_2026-04-17/closeout.md`

## Decision question

Did the bounded audit clear the provisional proxy-coverage blocker on the Phase C capture-v2 rows without drifting into score logic or label substitution?

## Short answer

**Yes — provisionally and observationally.**

Overall verdict: `PROVISIONAL_PROXY_COVERAGE_RESTORED`.

That verdict is narrow on purpose.
It means the provisional realized-path proxy family can now be materialized on the v2 surface under an audited anchor rule.
It does **not** mean the separate Phase 2 label contract is repaired.

## What the audit proved

### 1. The anchor overlap surface passed cleanly

On the older tracked capture surface, the audit compared `entry_atr` and `current_atr_used` on exactly matched rows.

The result was:

- `overlap_count = 167`
- `coverage_rate = 1.0`
- `max_abs_diff = 0.0`
- `max_rel_diff = 0.0`
- anchor audit verdict: `PASS`

So on the bounded overlap surface that the audit was allowed to inspect, `current_atr_used` was observationally compatible with `entry_atr`.

Important wording boundary:

- this is an **audited bounded compatibility result**
- it is **not** a repo-wide claim that the two fields are always semantically identical in every future context

### 2. The v2 proxy family can now be materialized

Using that audited anchor rule, the bounded slice materialized provisional proxy rows for the Phase C capture-v2 surface.

Materialized row count:

- `146`

Restored proxy coverage:

- `mfe_16_atr.non_null_count = 146`
- `continuation_score.non_null_count = 146`
- `fwd_16_atr.non_null_count = 145`

The one-row shortfall on `fwd_16_atr` is consistent with forward-horizon clipping near the window edge, not with a renewed anchor failure.

### 3. Deterministic replay held

The audit script executed an identical-input replay check and recorded:

- `summary_hash_match = true`

So the bounded audit stayed deterministic on the fixed inputs.

### 4. Containment held

The audit wrote only the approved outputs in:

- `results/research/ri_advisory_environment_fit/phase3_proxy_coverage_audit_2026-04-17/`

No runtime or production-near surfaces were touched.

## What the audit did not prove

This slice did **not** prove any of the following:

- exact Phase 2 supportive/hostile label fidelity
- `pnl_delta` availability
- active-uplift cohort membership
- contradiction-year pass/fail behavior
- score quality
- runtime readiness

The separate `BLOCKED_LABEL_GAP` remains intact.

## Consequence for Phase 3

The lane has now moved one blocker cleanly:

- **selector surface:** open
- **provisional proxy coverage:** now restored on an audited observational basis
- **exact Phase 2 label surface:** still blocked

That means evaluation-side Phase 3 is no longer blocked by missing provisional proxy coverage.
It remains blocked only where the lane still requires exact Phase 2 supportive/hostile authority.

## Exact next admissible step

The next honest move is now a **bounded provisional-evaluation rerun** on the restored proxy surface, under a new packet that stays explicit about two things:

1. the work is still provisional / exploratory only
2. the separate exact-label gap remains unresolved

What should **not** happen next:

- no direct promotion to score implementation
- no reframing of restored proxy coverage as exact supportive/hostile evidence
- no contradiction-year claim inflation

## Bottom line

The audit cleared the narrow blocker it was supposed to test:

- the Phase C v2 surface did not fail because the RI selector surface was empty
- it failed because the provisional proxy formulas had lost their ATR anchor
- on the bounded overlap surface, `current_atr_used` matched `entry_atr` exactly
- using that audited anchor rule restored provisional proxy coverage on the v2 rows

So the honest new state is:

- **provisional proxy coverage: restored**
- **exact Phase 2 label authority: still blocked**
- **next admissible step: bounded provisional-evaluation rerun, not runtime scoring**
