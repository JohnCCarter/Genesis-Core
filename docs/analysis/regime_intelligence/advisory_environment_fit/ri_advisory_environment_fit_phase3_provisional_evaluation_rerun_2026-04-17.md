# RI advisory environment-fit — Phase 3 provisional evaluation rerun verdict

This memo is fail-closed and research-only.
It records the outcome of the bounded provisional-evaluation rerun on the restored Phase C proxy surface.

Governance packet: `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_provisional_evaluation_rerun_packet_2026-04-17.md`

## Source surface used

This memo uses only already tracked surfaces:

- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_proxy_coverage_audit_2026-04-17.md`
- `tmp/ri_advisory_environment_fit_provisional_evaluation_rerun_20260417.py`
- `results/research/ri_advisory_environment_fit/phase3_provisional_evaluation_rerun_2026-04-17/selector_consumption.json`
- `results/research/ri_advisory_environment_fit/phase3_provisional_evaluation_rerun_2026-04-17/allowlist_manifest.json`
- `results/research/ri_advisory_environment_fit/phase3_provisional_evaluation_rerun_2026-04-17/join_audit.json`
- `results/research/ri_advisory_environment_fit/phase3_provisional_evaluation_rerun_2026-04-17/proxy_surface.json`
- `results/research/ri_advisory_environment_fit/phase3_provisional_evaluation_rerun_2026-04-17/bucket_summary.json`
- `results/research/ri_advisory_environment_fit/phase3_provisional_evaluation_rerun_2026-04-17/manifest.json`
- `results/research/ri_advisory_environment_fit/phase3_provisional_evaluation_rerun_2026-04-17/closeout.md`

## Decision question

After provisional proxy coverage was restored, did the bounded rerun expose enough non-empty exploratory structure to justify carrying Phase 3 evaluation work forward?

## Short answer

**Yes — but only partially, and still below exact label authority.**

Overall execution verdict: `EXPLORATORY_RERUN_COMPLETE`.

That is intentionally narrower than a baseline-success claim.
It means the rerun produced a clean joined exploratory surface and non-empty year-by-year bucket summaries.
It does **not** mean that the Phase 2 supportive/hostile contract is repaired, and it does **not** mean that Phase 4 shadow evaluation is automatically open.

## What the rerun proved

### 1. The joined exploratory surface is now real

The rerun passed the exact join discipline required by the packet:

- `selector_row_count = 146`
- `restored_proxy_row_count = 146`
- `matched_joined_rows = 146`
- `unmatched_left_count = 0`
- `unmatched_right_count = 0`
- duplicate selector keys: `0`
- duplicate proxy keys: `0`

Proxy null counts after the exact join also matched the restored proxy source exactly:

- `mfe_16_atr = 0` null
- `continuation_score = 0` null
- `fwd_16_atr = 1` null

So the rerun no longer fails on the earlier proxy-coverage blocker.
The exploratory evaluation surface is now materially present.

### 2. Deterministic replay held

The rerun executed identical-input replay and recorded:

- `summary_hash_match = true`
- `bucket_hash_match = true`

So the bounded rerun stayed deterministic on the fixed joined inputs.

### 3. `decision_reliability_rank` shows some bounded structure

The strongest exploratory signal appeared on the `decision_reliability_rank` axis, especially against forward/continuation-style proxies rather than pure `mfe_16_atr`.

Examples:

- against `fwd_16_atr`
  - `2024`: high bucket mean `1.247`, mid `-0.535`, low `0.664`
  - `2025`: high bucket mean `0.100`, mid `-0.135`, low `-0.390`
- against `continuation_score`
  - `2024`: high bucket mean `0.696`, mid `-0.174`, low `0.555`
  - `2025`: high bucket mean `0.101`, mid `-0.085`, low `-0.211`

This is still weak and not monotone on every proxy.
But it is no longer empty noise.
The rerun now shows that a clarity/confidence-weighted reliability rank can separate some exploratory forward/continuation behavior more than the failed pre-restoration slice could.

### 4. `transition_proxy_rank` is still mixed and unstable

The transition-oriented exploratory rank did **not** become cleanly useful across years.

Examples:

- against `fwd_16_atr`
  - `2024`: low bucket mean `1.294`, high `0.325`
  - `2025`: high bucket mean `-0.325`, low `-0.153`
- against `continuation_score`
  - `2024`: low bucket mean `0.665`, high `0.420`
  - `2025`: high bucket mean `-0.225`, low `0.070`

That is not stable enough to treat the current transition proxy as an honest multi-year advisory surface.
It still looks mixed at best and inverted at worst.

## What the rerun did not prove

This slice did **not** prove any of the following:

- exact Phase 2 supportive/hostile fidelity
- `pnl_delta` availability
- active-uplift cohort membership
- contradiction-year pass/fail behavior under the Phase 2 contract
- a full Phase 3 deterministic baseline
- readiness for Phase 4 shadow-runtime-style evaluation

The separate `BLOCKED_LABEL_GAP` remains intact.

## Consequence for Phase 3

The rerun moves the lane one step forward, but only one:

- **selector surface:** open
- **provisional proxy coverage:** restored and joined cleanly
- **bounded exploratory reliability structure:** present but weak
- **transition proxy structure:** still mixed / unstable
- **exact Phase 2 label authority:** still blocked

That means Phase 3 is no longer blocked by empty provisional proxy coverage.
But it is also **not** ready to declare a stable deterministic advisory baseline.

## Exact next admissible step

The next honest move is **not** Phase 4 shadow evaluation yet.

The next admissible step should be one docs-only decision that answers this narrower question:

> Does the bounded exploratory reliability signal now justify opening a separate exact-label-authority / Phase-2-faithful materialization decision, or should Phase 3 stop at exploratory-only evidence?

That follow-up should stay explicit that:

- `decision_reliability_rank` is the only axis showing any bounded carry-forward signal here
- `transition_proxy_rank` is still too mixed to advance honestly
- restored proxy evidence still does not repair the exact supportive/hostile contract

## Bottom line

The rerun succeeded at the one thing it needed to test after proxy restoration:

- the bounded exploratory evaluation surface is now real, deterministic, and non-empty

But the outcome is still only partial:

- some exploratory reliability structure exists
- transition-oriented structure remains mixed
- exact Phase 2 label authority is still blocked

So the honest new state is:

- **empty proxy coverage is no longer the blocker**
- **full deterministic Phase 3 success is still not proven**
- **next admissible step: docs-only decision on whether the narrow reliability signal is worth an exact-label-authority follow-up, or whether the lane should stop before Phase 4**
