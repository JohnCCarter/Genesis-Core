# RI policy router insufficient-evidence selective feature-gate contrast

Date: 2026-04-30
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `completed / read-only selective contrast / fixed 2021-vs-2025 target comparison`

This slice is a read-only follow-up to the completed March 2021 negative-year local-window note and the completed March 2025 positive-year control note.
It compares only the already-fixed `insufficient_evidence` target rows from those two slices on the smallest available repo-visible feature/gate surface: existing `enabled.router_debug` fields plus the same candle observational proxies already used in the local-window artifacts.
It does not reopen runtime work, default semantics, config authority, promotion surfaces, or the parked aged-weak chain.

All returns and excursion values in this slice are timestamp-close observational proxies on existing evidence rows only.
They are descriptive only and do not establish realized trade PnL, causal gate truth, runtime-authoritative row semantics, readiness, or promotion.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-04-29`
- **Risk:** `LOW` — why: this slice reads two already-frozen action-diff JSON artifacts plus curated candles only and emits one bounded JSON artifact plus this note.
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the local windows are already frozen, so the next honest move is one exact target-vs-target contrast instead of a fresh annual scan or runtime speculation.
- **Objective:** compare the fixed March 2021 and fixed March 2025 `insufficient_evidence` target rows on the smallest available feature/gate surface so the selectivity question becomes more concrete.
- **Candidate:** `fixed March 2021 vs March 2025 insufficient_evidence feature-gate contrast`
- **Base SHA:** `1cf34904ac2922f3aa7b062fd3e55200c9069038`
- **Skill Usage:** `decision_gate_debug`, `python_engineering`
- **Opus pre-code verdict:** `APPROVED_WITH_NOTES`

## Evidence inputs

- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_selective_feature_gate_contrast_packet_2026-04-30.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_local_window_2026-04-29.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_positive_year_insufficient_evidence_control_2026-04-29.md`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2021_enabled_vs_absent_action_diffs.json`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2025_enabled_vs_absent_action_diffs.json`
- `data/curated/v1/candles/tBTCUSD_3h.parquet`
- `results/evaluation/ri_policy_router_insufficient_evidence_selective_feature_gate_contrast_2026-04-30.json`

## Exact command run

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/ri_policy_router_insufficient_evidence_selective_feature_gate_contrast_20260430.py --base-sha 1cf34904ac2922f3aa7b062fd3e55200c9069038`

Artifact packaging note:

- the emitted JSON artifact was reproduced deterministically with identical SHA256 across two runs:
  `A107B62D0CAE4E360F9DFE067BDB3637C73DB60209F812137D37E134E29144CE`
- in the current repo state, new `results/evaluation` artifacts still appear ignored, so this JSON is
  deterministic local evidence rather than committed evidence in this slice unless staged explicitly by policy

## Fixed targets that actually materialized

### March 2021 negative-year target rows

- `2021-03-26T12:00:00+00:00`
- `2021-03-27T06:00:00+00:00`
- `2021-03-27T15:00:00+00:00`
- `2021-03-28T00:00:00+00:00`

### March 2025 positive-year target rows

- `2025-03-14T15:00:00+00:00`
- `2025-03-15T00:00:00+00:00`
- `2025-03-15T09:00:00+00:00`
- `2025-03-15T18:00:00+00:00`
- `2025-03-16T03:00:00+00:00`

## Main result

### 1. The two target clusters are structurally the same router outcome shape

Across both cohorts, the shared constant fields are the same:

- `switch_reason = insufficient_evidence`
- `selected_policy = RI_no_trade_policy`
- `raw_target_policy = RI_no_trade_policy`
- `previous_policy = RI_no_trade_policy`
- `zone = low`
- `candidate = LONG`
- `absent_action = LONG`
- `enabled_action = NONE`
- `regime = balanced`
- `confidence_level = 0`
- `mandate_level = 0`
- `switch_proposed = false`
- `switch_blocked = false`
- `size_multiplier = 0.0`

So the selectivity contrast is **not** explained by different policy labels or a different top-level router branch.
The interesting difference is inside the numeric signature of the same blocked shape.

### 2. The clearest separator on the first gate surface is regime age, not a changed policy identity

The largest mean gap in the artifact is:

- `bars_since_regime_change`: `+6.75` bars for 2021 versus 2025

Cohort summaries:

- 2021 mean: `71.75`
- 2025 mean: `65.00`

So the harmful-looking 2021 cluster sits **materially later** in regime age than the weak-looking 2025 control cluster.
That is the sharpest numerical separator on the bounded target-vs-target surface.

### 3. The 2021 cluster is also modestly stronger on edge, confidence, and clarity

Relative to the 2025 target cluster, the 2021 target rows are slightly stronger on the same router-debug metrics:

- `action_edge` mean gap: `+0.006131`
- `confidence_gate` mean gap: `+0.003065`
- `clarity_raw` mean gap: `+0.003713`
- `clarity_score` mean gap: `+0.35`

This is not a huge separation, but it is directionally consistent.
On the bounded descriptive surface, the 2021 blocked cluster looks a bit more mature and a bit stronger, not merely later by accident.

### 4. The observational outcome split still points the same way as the earlier window notes

The same target-vs-target rows still separate sharply on the observational outcome proxies:

- `fwd_16` mean gap: `+4.710832%` in favor of 2021
- `mfe_16` mean gap: `+4.047040%` in favor of 2021
- `fwd_8` mean gap: `+2.109023%` in favor of 2021
- `fwd_4` mean gap: `+1.426991%` in favor of 2021

And the cohort means stay consistent with the earlier local-window notes:

- 2021 target `fwd_16` mean: `+3.692905%`
- 2025 target `fwd_16` mean: `-1.017927%`

So this slice does not overturn the earlier selectivity read; it sharpens it.

### 5. One counter-signal exists: 2025 has longer dwell duration inside the same blocked shape

The main counter-directional metric in the artifact is:

- `dwell_duration` mean gap: `-3.5` (2021 lower, 2025 higher)

Cohort means:

- 2021 mean dwell duration: `5.5`
- 2025 mean dwell duration: `9.0`

So the simple story is **not** “everything is stronger in 2021.”
A more careful bounded reading is:

- 2021 target rows are later in regime age and somewhat stronger on edge/confidence/clarity,
- while 2025 target rows remain blocked longer inside the same no-trade state.

That makes `bars_since_regime_change` plus the near-floor strength metrics more plausible candidate discriminators than dwell duration alone.

## Interpretation

This slice is the first bounded evidence pass that makes the selectivity question more concrete.

The strongest descriptive reading now is:

> The harmful-looking March 2021 `insufficient_evidence` cluster is not a different router branch than the weak-looking March 2025 control. It is the same blocked low-zone `LONG -> NONE` shape, but it appears later in regime age and slightly stronger on edge/confidence/clarity, while the 2025 control remains earlier and weaker on those same metrics.

That does **not** prove a future rule.
But it does turn the robust-policy question into a more specific candidate hypothesis:

> if a future discriminator exists, it may need to preserve earlier/weaker 2025-like blocked rows while reconsidering older/stronger 2021-like blocked rows.

That is a much tighter question than the earlier annual framing.

## What this slice does not prove

This slice does **not** prove:

- that `bars_since_regime_change` alone is sufficient
- that `action_edge`, `confidence_gate`, or `clarity` can be thresholded safely
- that one scalar rule can solve the selectivity problem
- exact realized trade PnL or fill-aware truth
- runtime-authoritative row semantics
- that runtime/default/policy tuning is justified now
- that promotion/readiness/family/champion claims are warranted

## Consequence for the robust-policy question

This slice improves the question quality.
The next honest question is no longer just:

> why are some `insufficient_evidence` years bad and others good?

It becomes:

> does the observed 2021-vs-2025 discriminator bundle — especially later regime age plus slightly stronger edge/confidence/clarity inside the same blocked shape — recur anywhere else, or is it only a two-window coincidence?

That is a much better next step for a robust policy than jumping straight into a broad positive-year-vs-negative-year aggregate.

## Next admissible step

If this line is reopened, the cheapest honest next move should remain read-only:

1. test whether the observed discriminator bundle (`bars_since_regime_change`, `action_edge`, `confidence_gate`, `clarity_raw`, `clarity_score`) recurs on one additional bounded pair or one tiny fixed recurrence check, or
2. compare those same discriminator candidates against the already-fixed nearby displacement rows inside the March 2021 and March 2025 windows without widening into year-wide mining.

That keeps the work in research-evidence while asking a much sharper question than the annual split alone.

## What is not justified from this slice

- new router tuning
- default-policy changes
- global weakening of `insufficient_evidence`
- global strengthening of `insufficient_evidence`
- any runtime threshold proposal from this target-vs-target contrast alone
