# RI policy router insufficient-evidence counterfactual screen

Date: 2026-04-30
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `completed / read-only exact-subject counterfactual screen / observational only`

This slice is a bounded read-only follow-up to the structural roadmap and the new exact 2024 pocket chain.
It tests one narrow question only:

- on the fixed `2024` `insufficient_evidence` subset and one fresh exact `2020` positive-year low-zone `insufficient_evidence` control cluster, does any simple admissible decision-time split survive as a genuine counterfactual unlock screen?

This slice does **not** reopen runtime tuning.
It does **not** authorize config/default changes.
It does **not** admit payoff-state into runtime.
It does **not** reopen the closed March 2021 / March 2025 loop as the primary subject.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-04-29`
- **Risk:** `LOW`
- **Required Path:** `Lite`
- **Lane:** `Research-evidence`
- **Objective:** test one exact `2024` vs `2020` `insufficient_evidence` counterfactual screen with payoff remaining offline truth only
- **Candidate:** `fixed 2024 subset vs fixed 2020 positive-year control`
- **Base SHA:** `9ae9451d9d4d063db874ce14498a756209a2dd07`
- **Skill Usage:** `decision_gate_debug`, `python_engineering`
- **Opus pre-code verdict:** `APPROVED_WITH_NOTES`

## Evidence inputs

- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_counterfactual_screen_precode_packet_2026-04-30.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2024_regression_pocket_reason_split_2026-04-30.md`
- `results/evaluation/ri_policy_router_2024_regression_pocket_isolation_2026-04-30.json`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2020_enabled_vs_absent_action_diffs.json`
- `data/curated/v1/candles/tBTCUSD_3h.parquet`
- `results/evaluation/ri_policy_router_insufficient_evidence_counterfactual_screen_2026-04-30.json`

## Exact command run

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/ri_policy_router_insufficient_evidence_counterfactual_screen_20260430.py --base-sha 9ae9451d9d4d063db874ce14498a756209a2dd07`

## Fixed row lock

### `2024` target side — exact `insufficient_evidence` subset (`5` rows)

- `2024-11-29T09:00:00+00:00`
- `2024-11-29T18:00:00+00:00`
- `2024-11-30T03:00:00+00:00`
- `2024-12-01T15:00:00+00:00`
- `2024-12-02T00:00:00+00:00`

Nearby fixed `2024` context retained for descriptive checks only:

- true displacement row: `2024-12-01T00:00:00+00:00`
- stable blocked context row: `2024-12-01T06:00:00+00:00`

### `2020` control side — exact low-zone `insufficient_evidence` cluster (`4` rows)

- `2020-10-31T21:00:00+00:00`
- `2020-11-01T06:00:00+00:00`
- `2020-11-01T15:00:00+00:00`
- `2020-11-02T00:00:00+00:00`

Nearby fixed `2020` context retained for descriptive checks only:

- true displacement rows:
  - `2020-11-02T03:00:00+00:00`
  - `2020-11-02T21:00:00+00:00`
- stable blocked context rows:
  - `2020-11-02T09:00:00+00:00`
  - `2020-11-03T03:00:00+00:00`

## Main result

### 1. The helper emitted `no_surviving_screen`

The final artifact status is:

- `no_surviving_screen`

This did **not** happen because no descriptive separator existed.
It happened because the fixed `2024` and fixed `2020` target sides did **not** remain truth-opposed on the chosen offline `fwd_16` proxy surface.

The helper therefore refused to promote any mechanical separator into a surviving counterfactual unlock screen.

### 2. The truth surface is not opposed on `fwd_16`

The explicit truth check in the artifact reports:

- `2024` target `fwd_16` mean: `-0.855705%`
- `2020` control `fwd_16` mean: `-0.875411%`
- `truth_surface_is_opposed = false`

So on this exact bounded `fwd_16` proxy surface:

- the fixed `2024` side does **not** re-materialize as a locally favorable blocked cluster
- the fixed `2020` control side remains locally weak as expected

That means the intended harmful-vs-correct polarity is **not** present on the current exact `2024` vs `2020` pair on this chosen `fwd_16` proxy.

### 3. A mechanical separator exists, but it is only descriptive

The best descriptive candidate was:

- `bars_since_regime_change <= 282`

Its exact behavior on the bounded surface was:

- selects `5 / 5` `2024` target rows
- selects `0 / 4` `2020` control target rows
- balanced accuracy on target/control rows: `1.0`

Nearby-cohort behavior:

- selects the `2024` nearby displacement row (`1 / 1`)
- selects the `2024` nearby stable blocked context row (`1 / 1`)
- selects no `2020` nearby displacement rows (`0 / 2`)
- selects no `2020` nearby blocked context rows (`0 / 2`)

So this candidate is a **coarse local envelope / regime-age separator** across the exact `2024` and `2020` pockets.
It is **not** a clean blocked-versus-displacement discriminator inside a year, and because the chosen `fwd_16` truth surface is not opposed, it is **not** promoted here as a genuine unlock screen.

## Cohort readout

### Fixed `2024` target side stays locally weak

For the exact `2024` target subset (`5` rows):

- `bars_since_regime_change` mean: `281.4`
- `action_edge` mean: `0.027769`
- `confidence_gate` mean: `0.513884`
- `clarity_score` mean: `36.2`
- `fwd_16` mean: `-0.855705%`
- `fwd_16 > 0` share: `0%`
- `mfe_16` mean: `+0.724505%`
- `mae_16` mean: `-2.480330%`

Relative to the fixed nearby `2024` displacement row, the target side remains weaker:

- `fwd_16` mean gap (`target - displacement`): `-1.163445%`

So this exact `2024` target surface is locally weak on the same proxy family used for the screen.

### Fixed `2020` control side is also locally weak

For the exact `2020` control target (`4` rows):

- `bars_since_regime_change` mean: `302.0`
- `action_edge` mean: `0.027054`
- `confidence_gate` mean: `0.513527`
- `clarity_score` mean: `36.0`
- `fwd_16` mean: `-0.875411%`
- `fwd_16 > 0` share: `25%`
- `mfe_16` mean: `+1.103043%`
- `mae_16` mean: `-4.077616%`

Relative to the fixed nearby `2020` displacement rows, the control target is also materially weaker:

- `fwd_16` mean gap (`target - displacement`): `-3.430844%`

So the `2020` side behaves exactly like a locally justified suppression control.

## Interpretation

The bounded conclusion is narrower than the packet's initial harmful-vs-correct framing hoped for on this chosen `fwd_16` proxy surface.

What this slice actually shows is:

1. the exact `2024` `insufficient_evidence` subset does **not** re-materialize as a locally favorable blocked cohort on the same chosen offline `fwd_16` proxy family
2. the fixed `2020` control cluster is also locally weak and sits beside healthier nearby continuation rows
3. `bars_since_regime_change <= 282` cleanly separates the two exact envelopes, but only as a descriptive local-state separator

So the honest reading is:

> this exact `2024` vs `2020` slice does **not** yield a surviving harmful-vs-correct counterfactual unlock screen. It yields a no-screen verdict plus one strong descriptive separator (`bars_since_regime_change`) that distinguishes the two bounded envelopes without rescuing the missing harmful-side truth polarity.

## What this slice supports

- the fixed `2024` target/control pair chosen for this slice is **not** truth-opposed on the current chosen offline `fwd_16` proxy surface
- the helper therefore correctly fails closed to `no_surviving_screen`
- `bars_since_regime_change` remains the strongest descriptive field on this exact surface
- that field behaves as a coarse envelope separator, not as a proven unlock rule for wrongly suppressed rows

## What this slice does **not** support

- a runtime or concept-only packet for an unlock rule from this exact surface alone
- any claim that `bars_since_regime_change <= 282` is ready for runtime admission
- any claim that the exact `2024` side now proves locally harmful suppression
- any reopening of broad threshold retuning from this result

## Consequence

The strict bounded outcome of this slice is:

- **no clean counterfactual unlock screen survived on this exact `2024` vs `2020` surface**

But one descriptive fact survives and should be remembered carefully:

- the strongest separator was still later-vs-earlier regime age (`302` in `2020` vs `281..282` in `2024`)

That means the next honest move, if this line is reopened, is **not** a runtime packet.
It is a cheaper truth-surface correction step, for example:

1. replace the `2024` side with one exact non-March negative-year subset that actually materializes as locally favorable on the same proxy family, or
2. explicitly close this `2024` vs `2020` branch as a bounded no-screen result and park the discriminator line on this exact surface.

## Validation notes

- helper diagnostics were clean on creation and rerun
- the helper executed successfully and wrote the bounded JSON artifact
- the final rerun emitted `no_surviving_screen`
- all claims in this note remain observational, bounded, and non-authoritative
