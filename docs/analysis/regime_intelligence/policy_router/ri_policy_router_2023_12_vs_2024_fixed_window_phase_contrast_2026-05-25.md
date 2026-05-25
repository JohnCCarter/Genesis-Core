# RI policy router 2023-12 vs 2024 fixed-window phase contrast

Date: 2026-05-25
Branch: `feature/research-next-bounded-case-2026-05-25`
Mode: `RESEARCH`
Status: `completed / read-only fixed-window contrast / observational only`

This slice compares two already-locked local subjects instead of reopening annual screening or runtime tuning:

- the exact `2023-12` dual-wave continuation-local surface, and
- the exact late-`2024` harmful pocket.

The goal is not to prove a portable rule.
It is to test whether the strongest current positive-looking local candidate differs from the known harmful surface by **phase structure** rather than by a new threshold or a new annual pocket hunt.

This slice does **not**:

- reopen runtime tuning
- reopen counterfactual transport claims
- widen to more years
- authorize strategy/config/promotion/readiness changes

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: live branch `feature/research-next-bounded-case-2026-05-25`
- **Risk:** `LOW`
- **Required Path:** `Quick`
- **Lane:** `Research-evidence`
- **Objective:** compare the fixed `2023-12` continuation-local subject against the fixed `2024` harmful subject using exact row locks, phase ordering, and already-available evidence surfaces
- **Candidate:** `2023-12 vs 2024 fixed-window phase contrast`
- **Base SHA:** `270b65346ebe9208c953abfc7181bf83df34d8f5`

## Evidence inputs

- `scripts/analyze/ri_policy_router_2023_12_vs_2024_fixed_window_phase_contrast_20260525.py`
- `results/evaluation/ri_policy_router_2023_12_vs_2024_fixed_window_phase_contrast_2026-05-25.json`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2023_enabled_vs_absent_action_diffs.json`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2024_enabled_vs_absent_action_diffs.json`
- `results/evaluation/ri_policy_router_2024_regression_pocket_isolation_2026-04-30.json`
- `artifacts/research_ledger/indexes/findings_index.json`

Motivating anchors only:

- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_enabled_vs_absent_curated_annual_evidence_2026-04-28.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_negative_year_pocket_isolation_2026-04-28.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_positive_vs_negative_pocket_comparison_2026-04-28.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_12_vs_2017_03_continuation_local_window_concentration_2026-05-06.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_12_vs_2017_03_dominant_window_chronology_2026-05-06.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2024_regression_pocket_isolation_2026-04-30.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2024_regression_pocket_reason_split_2026-04-30.md`

## Exact command run

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/ri_policy_router_2023_12_vs_2024_fixed_window_phase_contrast_20260525.py --base-sha 270b65346ebe9208c953abfc7181bf83df34d8f5`

## Fixed subject lock

### `2023-12` continuation side

Two exact continuation-release waves:

- wave 1: `2023-12-15T21:00:00+00:00` -> `2023-12-17T18:00:00+00:00` (`6` rows)
- wave 2: `2023-12-22T15:00:00+00:00` -> `2023-12-26T00:00:00+00:00` (`7` rows)

Locked shape:

- action pair: `NONE -> LONG`
- `switch_reason = stable_continuation_state`
- `selected_policy = RI_continuation_policy`
- blocked-like rows inside the fixed subject: `0`

### `2024` harmful side

Exact fixed harmful pocket:

- blocked target cluster: `9` rows
- nearby true displacement row: `1`
- nearby stable blocked context row: `1`

Locked shape:

- target cluster action pair: `LONG -> NONE`
- target reason split:
  - `AGED_WEAK_CONTINUATION_GUARD = 4`
  - `insufficient_evidence = 5`
- displacement row action pair: `NONE -> LONG`
- stable blocked context action pair: `LONG -> NONE`

## Main result

The fixed-window contrast supports a tighter reading than the earlier broad annual language.

The strongest current positive-looking local subject (`2023-12`) is not merely “a month with continuation rows.”
It is a **phase-pure dual-wave continuation-release surface**.

The known harmful `2024` subject is not merely “a month with both blocking and continuation.”
It is a **blocked-dominant mixed pocket** with only one brief continuation-release interruption inside a six-segment harmful sequence.

So the useful contrast is:

- not `continuation exists` vs `continuation absent`
- but rather
- **phase-pure continuation clustering** vs **blocked-dominant mixed churn**

## Observed

### 1. `2023-12` is continuation-pure on the fixed subject

The exact `2023-12` subject contains:

- `13 / 13` continuation-like rows
- `0 / 13` blocked-like rows
- `2` segments total
- phase sequence:
  - `continuation_release`
  - `continuation_release`

Segment structure:

- segment 1: `6` rows over `45h`
- segment 2: `7` rows over `81h`

There is no blocked-like interruption inside the locked `2023-12` subject.

### 2. `2024` is blocked-dominant and phase-mixed on the fixed harmful subject

The exact `2024` subject contains:

- `10 / 11` blocked-like rows
- `1 / 11` continuation-like row
- `6` segments total
- phase sequence:
  - `blocked_aged_weak_continuation_guard`
  - `blocked_insufficient_evidence`
  - `blocked_aged_weak_continuation_guard`
  - `continuation_release`
  - `blocked_stable_context`
  - `blocked_insufficient_evidence`

This means the continuation row is a tiny interruption inside a much larger blocked sequence rather than the dominant local shape.

### 3. Router-local quality scores are stronger on `2023-12`, but that does not carry the full outcome story

With curated candles restored, the helper now materializes local forward-return proxies directly.
The router-local descriptive fields still look cleaner on `2023-12`, but the refreshed proxy surface is more mixed than the first structure-only read.

`2023-12` combined continuation cohort:

- `action_edge` mean: `0.101335`
- `confidence_gate` mean: `0.550668`
- `clarity_score` mean: `40.615385`

`2024` harmful target cohort:

- `action_edge` mean: `0.040542`
- `confidence_gate` mean: `0.520271`
- `clarity_score` mean: `36.888889`

So the positive-looking local subject is not only phase-cleaner; it also scores cleaner on the router-local descriptive fields.

### 4. Freshly recomputed local proxies complicate the edge reading

The recomputed `2023-12` continuation cohort is not locally strong on the first proxy surface even though its phase structure is cleaner.

`2023-12` combined continuation cohort:

- `fwd_16` mean: `-0.624829%`
- `fwd_16` median: `-0.931138%`
- `fwd_16 > 0` share: `23.08%`

Wave split:

- wave 1 `fwd_16` mean: `-0.154828%` (`50%` positive)
- wave 2 `fwd_16` mean: `-1.027688%` (`0%` positive)

The fixed `2024` harmful target still reads:

- harmful target `fwd_16` mean: `-0.441517%`
- harmful target `fwd_16` median: `-0.614476%`
- harmful target `fwd_16 > 0` share: `11.11%`
- nearby displacement `fwd_16`: `+0.307740%`
- nearby stable blocked context `fwd_16`: `-1.616388%`

Descriptive gaps from the refreshed contrast artifact:

- `2023-12` combined minus `2024` target `fwd_16` mean gap: `-0.183312%`
- `2023-12` wave 2 minus `2024` target `fwd_16` mean gap: `-0.586171%`
- `2023-12` combined minus `2024` displacement `fwd_16` mean gap: `-0.932569%`

So the updated evidence says two things at once:

- `2023-12` is structurally cleaner than the harmful `2024` pocket, and
- that structural cleanliness does **not** automatically translate into a stronger local `fwd_16` outcome on the refreshed proxy surface.

## Inferred

The currently best bounded edge framing is now narrower and more constrained:

> phase purity is a real structural discriminator, but it is **not** yet an outcome discriminator. The fixed `2023-12` dual-wave continuation subject is cleaner than the fixed `2024` harmful pocket, but it does not beat that harmful target on mean `fwd_16`, and its second wave is materially weaker than its first.

That is a better working hypothesis than either of these weaker stories:

- “policy continuation broadly helps”
- “`insufficient_evidence` alone explains 2024 harm”
- “phase-pure continuation windows are automatically the local edge”

The contrast instead points toward a more specific discriminator class:

- phase structure first: continuation-dominant local clustering with no blocked re-entry, versus mixed blocked pockets where continuation appears only briefly and is surrounded by renewed blocking
- then outcome split inside the positive-looking side itself: less-hostile continuation waves versus structurally clean but still weak continuation waves

## Unverified

This slice does **not** prove:

- that phase-pure continuation windows are locally favorable just because they are phase-pure
- that the weaker `2023-12` second wave and the harmful `2024` pocket are separated by one portable rule
- that one portable phase-purity rule cleanly separates positive from negative years
- that `insufficient_evidence` or `AGED_WEAK_CONTINUATION_GUARD` should be weakened
- that runtime tuning is justified

The slice is descriptive and fixed-subject only.

## Consequence

The best honest next bounded slice is no longer “find more continuation months,” and it is no longer just “separate pure continuation from blocked pockets.”
It is:

1. keep late `2024` as the harmful fixed local subject,
2. split `2023-12` explicitly into wave 1 and wave 2 as separate local outcome subjects, and
3. test whether the next tiny descriptive discriminator can separate
   - **less-hostile phase-pure continuation waves**
     from
   - **phase-pure but still weak continuation waves**
     and
   - **blocked-dominant mixed pockets**
     without assuming a portable `insufficient_evidence` rule.

That is a better next slice because it preserves the user’s `2024` warning as an explicit constraint and also prevents us from over-reading `2023-12` as one uniformly favorable block.

## What changed and what did not

What changed:

- the repo now contains a new read-only helper for fixed-window `2023-12` vs `2024` phase contrast
- the current local evidence posture is sharper: `2023-12` reads as phase-pure continuation, `2024` reads as blocked-dominant mixed churn

What did **not** change:

- no runtime/config/strategy/backtest behavior changed
- no annual verdict was reopened
- no threshold or policy retune was introduced
- no readiness/promotion claim was made
