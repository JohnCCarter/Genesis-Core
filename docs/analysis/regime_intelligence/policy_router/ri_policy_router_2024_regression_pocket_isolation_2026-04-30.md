# RI policy router 2024 regression pocket isolation

Date: 2026-04-30
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `completed / read-only fixed-pocket evidence / observational only`

This slice opens one genuinely new bounded evidence surface after the March 2021 / March 2025 four-cohort insufficient-evidence loop was closed by a bounded null on the displacement-normalized question.

It does **not** reopen runtime tuning.
It does **not** widen into additional 2024 pocket discovery.
It does **not** authorize router, strategy, config, backtest, optimizer, or promotion changes.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-04-29`
- **Risk:** `LOW`
- **Required Path:** `Lite`
- **Lane:** `Research-evidence`
- **Objective:** materialize one exact 2024 late low-zone regression pocket inside the already documented blocked-baseline / later-`stable_continuation_state` family.
- **Candidate:** `2024-11-28 regression pocket isolation`
- **Base SHA:** `1cf34904ac2922f3aa7b062fd3e55200c9069038`
- **Skill Usage:** `decision_gate_debug`, `python_engineering`
- **Opus pre-code verdict:** `APPROVED_WITH_NOTES`

## Evidence inputs

- `scripts/analyze/ri_policy_router_2024_regression_pocket_isolation_20260430.py`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2024_enabled_vs_absent_action_diffs.json`
- `data/curated/v1/candles/tBTCUSD_3h.parquet`
- `results/evaluation/ri_policy_router_2024_regression_pocket_isolation_2026-04-30.json`
- motivating anchors only:
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_enabled_vs_absent_curated_annual_evidence_2026-04-28.md`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_negative_year_pocket_isolation_2026-04-28.md`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_positive_vs_negative_pocket_comparison_2026-04-28.md`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_shared_pocket_outcome_quality_2026-04-28.md`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_blocked_reason_split_2026-04-29.md`

## Exact command run

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/ri_policy_router_2024_regression_pocket_isolation_20260430.py --base-sha 1cf34904ac2922f3aa7b062fd3e55200c9069038`

Artifact packaging note:

- the emitted JSON artifact `results/evaluation/ri_policy_router_2024_regression_pocket_isolation_2026-04-30.json` is reproducible local evidence for this slice, but it remains ignored under current repo policy unless explicitly staged

## Fixed subject lock

### Mixed blocked target cluster (`9` rows)

- `2024-11-28T15:00:00+00:00`
- `2024-11-29T00:00:00+00:00`
- `2024-11-29T09:00:00+00:00`
- `2024-11-29T18:00:00+00:00`
- `2024-11-30T03:00:00+00:00`
- `2024-11-30T12:00:00+00:00`
- `2024-11-30T21:00:00+00:00`
- `2024-12-01T15:00:00+00:00`
- `2024-12-02T00:00:00+00:00`

Locked target shape:

- absent action = `LONG`
- enabled action = `NONE`
- `zone = low`
- `candidate = LONG`
- `bars_since_regime_change >= 8`
- reason split:
  - `AGED_WEAK_CONTINUATION_GUARD = 4`
  - `insufficient_evidence = 5`

### Nearby true displacement row (`1`)

- `2024-12-01T00:00:00+00:00`
- shape: absent `NONE` -> enabled `LONG`
- `switch_reason = stable_continuation_state`

### Nearby stable blocked context row (`1`)

- `2024-12-01T06:00:00+00:00`
- shape: absent `LONG` -> enabled `NONE`
- `switch_reason = stable_continuation_state`

### Local envelope

- `2024-11-27T15:00:00+00:00` -> `2024-12-03T00:00:00+00:00`
- additional unlabeled context rows inside the envelope: `0`

## Main result

This exact 2024 pocket reads as a **tight local suppression/displacement blend**, not as a pure single-reason seam.

Three facts stand out on the bounded observational proxy surface:

1. the mixed blocked target cluster is locally weak overall
2. the nearby true `stable_continuation_state` displacement row looks materially better than the blocked target cluster
3. the nearby `stable_continuation_state` blocked row is even weaker than the mixed target cluster

So this pocket is not well-described by either of the too-simple stories:

- "only `insufficient_evidence` is the problem here"
- "all `stable_continuation_state` rows in the pocket are the healthy release path"

The exact local pocket contains both:

- a materially weak mixed blocked cluster, and
- split stable-continuation behavior, where the true displacement row is better but the nearby stable blocked row is worse.

## Evidence summary

### 1. The mixed blocked target cluster is locally negative

For the fixed target cluster (`9` rows):

- `fwd_16` mean: `-0.441517%`
- `fwd_16` median: `-0.614476%`
- `fwd_16 > 0` share: `11.11%`
- `mfe_16` mean: `+1.443341%`
- `mae_16` mean: `-1.918417%`

That is a meaningfully weak local profile.

The cluster is not uniformly catastrophic — the first row (`2024-11-28T15:00:00+00:00`) is strongly positive on `fwd_16` — but the pocket as a whole slopes negative and only `1 / 9` rows is positive at `+16` bars.

### 2. The nearby true displacement row looks better than the blocked target cluster

For the exact comparison row (`2024-12-01T00:00:00+00:00`):

- `fwd_16`: `+0.307740%`
- `fwd_8`: `+1.953891%`
- `mfe_16`: `+2.482787%`
- `mae_16`: `-1.232005%`

Descriptive gap versus the blocked target cluster:

- `fwd_16` mean gap (`target - displacement`): `-0.749257%`
- `mfe_16` mean gap: `-1.039446%`
- `mae_16` mean gap: `-0.686412%`

On this exact pocket, the true displacement row is locally healthier than the mixed blocked target cluster.

### 3. The nearby stable blocked row is weaker still

For the exact stable blocked context row (`2024-12-01T06:00:00+00:00`):

- `fwd_16`: `-1.616388%`
- `fwd_8`: `-2.094823%`
- `mfe_16`: `+1.078278%`
- `mae_16`: `-2.585604%`

Descriptive gap versus the blocked target cluster:

- `fwd_16` mean gap (`target - stable_context`): `+1.174871%`
- `mfe_16` mean gap: `+0.365063%`
- `mae_16` mean gap: `+0.667187%`

That means the mixed blocked target cluster is weak, but it is **not** the worst thing in the exact pocket.
The nearby `stable_continuation_state` blocked row is even weaker on the same local proxy surface.

## Interpretation

This fixed 2024 pocket adds one exact local example consistent with one specific reading from the broader annual chain:

- the negative-year late low-zone family really can contain locally harmful blocked target mass
- a nearby true `stable_continuation_state` release can look better on the same pocket
- but the same pocket can also contain `stable_continuation_state` rows that remain blocked and locally weak

So the cleanest bounded interpretation in this envelope only is:

> this exact 2024 regression pocket behaves like a compact suppression/displacement blend in which the mixed blocked cluster looks locally harmful relative to the nearby true displacement row, but not every `stable_continuation_state` row in the pocket is benign.

That is more specific than the earlier annual notes, but still strictly local and observational.

## What this slice supports

- one exact 2024 late low-zone regression pocket exists where a mixed `AGED_WEAK_CONTINUATION_GUARD` / `insufficient_evidence` blocked cluster looks locally weak
- the nearby true `stable_continuation_state` displacement row in that same pocket looks better on the bounded proxy surface
- the nearby stable blocked row remains weak, so the pocket is not reducible to a single simple suppressor-versus-release polarity

These observations are local to this exact envelope only and do not justify year-level generalization by themselves.

## What this slice does **not** support

- weakening `insufficient_evidence` or `AGED_WEAK_CONTINUATION_GUARD` from this pocket alone
- treating `stable_continuation_state` as uniformly healthy or uniformly harmful
- runtime router tuning
- promotion/readiness claims
- widening to additional 2024 pockets without a new explicit packet

## Consequence

The 2024 line is now anchored by one exact fixed pocket rather than only by year-level summaries.

If this lane is reopened again, the next honest read-only move should remain bounded and comparative, for example:

1. compare this exact 2024 pocket against one similarly fixed negative-year control pocket (for example a 2021 pocket) without reopening the exhausted March 2021 / March 2025 four-cohort artifact loop as the primary subject, or
2. perform a tiny row-local split inside this exact 2024 pocket to compare the `insufficient_evidence` subset against the `AGED_WEAK_CONTINUATION_GUARD` subset descriptively only.

## Validation notes

- helper artifact row lock held exactly: `9 / 1 / 1 / 0`
- exact target reason signature held exactly: `4 / 5`
- focused tests for fixed target locking and cohort labeling passed
- all claims in this note are observational and pocket-local only
