# Feature Attribution — post-Phase-14 RI trade / exit join fixed three-cohort pass

Date: 2026-05-26
Branch: `feature/research-attribution-layer-foundation-2026-05-26`
Mode: `RESEARCH`
Base SHA anchor: `a437c0da62ee46537c29381fbe10e89a4778f4c8`
Status: `completed / bounded decision-to-trade join / stop-exit taxonomy pass`

## Purpose

This slice implements the first bounded join from the canonical Slice 2 `decision_row` artifact into actual opened positions and serialized trade legs.

It does **not** claim that the runtime now emits a canonical `execution_row`.
It only proves how far the current same-stack observed surfaces can go without runtime changes.

## Scope

### Scope IN

- one read-only join helper over the fixed three-cohort RI decision surface
- one retained artifact proving which joins are observed versus derived
- one bounded stop / exit taxonomy pass over current `trade.exit_reason` values
- one current-branch note advancing the attribution-layer foundation lane

### Scope OUT

- runtime/config/strategy/backtest behavior changes
- canonical runtime `execution_row` implementation
- canonical `ledger_impact_row` implementation
- same-stack `OFF vs ON` comparator work
- broader all-history attribution or family-wide expansion

## Evidence inputs

Primary:

- `scripts/analyze/feature_attribution_post_phase14_ri_trade_exit_join_fixed_three_cohort_20260526.py`
- `results/evaluation/feature_attribution_post_phase14_ri_trade_exit_join_fixed_three_cohort_2026-05-26.json`
- `results/evaluation/feature_attribution_post_phase14_ri_decision_surface_fixed_three_cohort_2026-05-26.json`

Current-code anchors:

- `src/core/backtest/engine.py`
- `src/core/backtest/position_tracker.py`
- `src/core/backtest/engine_results.py`
- `src/core/strategy/htf_exit_engine.py`
- `tools/compare_backtest_results.py`

## Exact command run

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m black scripts/analyze/feature_attribution_post_phase14_ri_trade_exit_join_fixed_three_cohort_20260526.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m ruff check scripts/analyze/feature_attribution_post_phase14_ri_trade_exit_join_fixed_three_cohort_20260526.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/feature_attribution_post_phase14_ri_trade_exit_join_fixed_three_cohort_20260526.py --base-sha a437c0da62ee46537c29381fbe10e89a4778f4c8`

## Main result

The join helper emitted a bounded trade / exit artifact with status:

- `feature_attribution_ri_trade_exit_join_fixed_three_cohort_generated`

Across the fixed three-cohort surface, the artifact proves:

- `22` exact `decision_row` inputs from Slice 2
- `13` non-`NONE` decision rows on the two continuation-positive cohorts
- `3` observed open-entry events captured via helper-side `post_execution_hook`
- `3` actual bounded positions linked to those opens
- `4` serialized trade events across those positions
- `10` non-`NONE` decision rows that still do **not** have a direct observed execution status in current outputs

So Slice 3 now exists as a real join/taxonomy artifact instead of only a schema intention.

## Observed

### 1. The harmful `2024` target remains blocked end-to-end on the bounded surface

For `blocked_dominant_mixed_pocket` (`2024 harmful target`):

- exact decision rows: `9`
- non-`NONE` decision rows: `0`
- observed open-entry events: `0`
- positions: `0`
- trade events: `0`

This slice therefore does **not** overturn the earlier warning surface.

> Tänk på att policyn även har försämrat bra år, tex 2024.

More narrowly here, the harmful target remains a true no-trade / blocked path even after the first honest decision-to-trade join pass.

### 2. Only a minority of positive-cohort `LONG` decisions became observed opens

Per cohort:

| Cohort                | Exact decision rows | Non-`NONE` rows | Observed opens | Positions | Trade events | Unresolved non-opening `LONG` decisions |
| --------------------- | ------------------: | --------------: | -------------: | --------: | -----------: | --------------------------------------: |
| `2023-12 wave 1`      |                 `6` |             `6` |            `2` |       `2` |          `3` |                                     `4` |
| `2023-12 wave 2`      |                 `7` |             `7` |            `1` |       `1` |          `1` |                                     `6` |
| harmful `2024` target |                 `9` |             `0` |            `0` |       `0` |          `0` |                                     `0` |
| **Total**             |                `22` |            `13` |            `3` |       `3` |          `4` |                                    `10` |

This is the main Slice 3 finding.
The decision surface alone is **not** enough to say that a non-`NONE` decision became a trade.

The current bounded truth is instead:

- some `LONG` decisions become observed opens
- many `LONG` decisions remain non-opening signals without a canonical emitted execution status
- therefore a direct `decision_row -> trade_row` join is still not an observed native runtime surface

### 3. The current repo surfaces support an honest bounded join contract

The artifact proves the following bounded chain:

1. `decision_row.timestamp` + `decision_row.reasons`
2. helper-side open-entry capture via `post_execution_hook`
3. `trade.position_id` / `trade.entry_time`
4. serialized trade legs and `trade.exit_reason`

That means the following are now supported on the fixed cohort surface without runtime changes:

- observed matching for actual opens
- observed grouping of trade legs by opened position
- observed exit-reason recovery for those positions

But the artifact also freezes the limits honestly:

- `decision_row.position_id` is still not directly observed
- non-opening signals still lack a canonical emitted `execution_status`
- helper-side open capture is useful evidence, but it is **not** yet a canonical runtime `execution_row`

### 4. Exit taxonomy is recoverable from current `trade.exit_reason` plus bounded config context

Observed exit-reason counts across the bounded joined positions:

- `EMERGENCY_SL = 2`
- `TRAIL_STOP = 1`
- `TP1 Hit (42448.50) = 1`

Derived `exit_family` counts:

- `stop_loss = 2`
- `trailing_stop = 1`
- `take_profit = 1`

No joined positions on this fixed surface emitted:

- `REGIME_CHANGE`
- `CONF_DROP`
- `FALLBACK_TRAIL`
- `EMERGENCY_TP`
- `OPPOSITE_SIGNAL`

An important small but real taxonomy follow-up came directly from the run:

- the first implementation only matched `TP*` styles like `TP1_0382`
- the actual joined surface also uses human-readable reasons like `TP1 Hit (42448.50)`
- Slice 3 therefore had to freeze both forms into the same `take_profit` family

### 5. The joined positions show that continuation-positive cohorts are still mixed downstream

The bounded joined positions were:

- `2023-12-15T21:00:00` open -> partial `TP1 Hit (42448.50)` -> final `TRAIL_STOP` -> gross trade PnL `+5.781198`
- `2023-12-17T00:00:00` open -> final `EMERGENCY_SL` -> gross trade PnL `-20.90836`
- `2023-12-22T15:00:00` open -> final `EMERGENCY_SL` -> gross trade PnL `-8.944728`

So even the continuation-positive cohorts do **not** resolve into a clean monotonic profit story after the decision layer.
The bounded join already shows downstream mixture:

- one opened position produced a partial take-profit then trailed out
- two opened positions ended in emergency stop-loss exits

## Inferred

### 1. Helper-side open capture is enough for bounded execution support, but not for a canonical runtime execution row

This is stronger than the Slice 1 schema draft but still narrower than a real execution-row implementation.

The branch now has evidence that:

- actual opens can be observed without runtime edits
- non-opens still cannot be classified completely without a canonical execution-status surface

### 2. The biggest current collapse gap is between `decision_row` and non-opening execution semantics

The missing information is **not** whether the system can emit `LONG` decisions.
It can.

The missing information is why `10` of the `13` non-`NONE` decisions on this bounded surface did **not** become observed opens in retained current outputs.

That collapse reason should stay explicitly unresolved for now rather than being guessed.

### 3. Slice 4 can now build metrics on a more honest funnel

The first regime-/policy-separated attribution cube can now distinguish at least four stages on the fixed surface:

1. decision rows
2. observed opens
3. trade legs
4. exit-family outcomes

That is enough to start measuring where activity survives or collapses before a later ledger projection slice.

## Unverified

This slice still does **not** prove:

- the exact emitted collapse reason for the `10` non-opening `LONG` decisions
- a canonical runtime `execution_row`
- a canonical `ledger_impact_row`
- same-stack `OFF vs ON` comparator semantics on the trade / ledger layers
- whether broader surfaces will introduce additional exit-reason families that require taxonomy expansion

## Consequence

The next admissible step is now **Slice 4 — regime- and policy-separated attribution metrics**.

That slice should reuse this joined artifact rather than rebuilding either the decision surface or the bounded trade join again.

## Verification

- `python -m black scripts/analyze/feature_attribution_post_phase14_ri_trade_exit_join_fixed_three_cohort_20260526.py` -> pass
- `python -m ruff check scripts/analyze/feature_attribution_post_phase14_ri_trade_exit_join_fixed_three_cohort_20260526.py` -> pass
- `python scripts/analyze/feature_attribution_post_phase14_ri_trade_exit_join_fixed_three_cohort_20260526.py --base-sha a437c0da62ee46537c29381fbe10e89a4778f4c8` -> emitted artifact with status `feature_attribution_ri_trade_exit_join_fixed_three_cohort_generated`

## What changed and what did not

What changed:

- one new read-only join helper now links a bounded subset of Slice 2 decision rows to actual opened positions and serialized trade legs
- one new retained artifact now freezes observed-vs-derived join semantics for the fixed three-cohort RI surface
- stop / exit taxonomy is now materially exercised against current emitted `exit_reason` values rather than only schema labels
- the branch now has direct evidence that many non-`NONE` decisions still collapse before any observed opened position exists in retained outputs

What did **not** change:

- no runtime/config/strategy/backtest behavior changed
- no canonical runtime `execution_row` was introduced
- no canonical `ledger_impact_row` was introduced
- no promotion or runtime-authority claim was made
