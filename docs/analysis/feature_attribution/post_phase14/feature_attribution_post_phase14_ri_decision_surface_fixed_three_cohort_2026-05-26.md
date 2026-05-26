# Feature Attribution — post-Phase-14 RI decision surface fixed three-cohort extractor

Date: 2026-05-26
Branch: `feature/research-attribution-layer-foundation-2026-05-26`
Mode: `RESEARCH`
Base SHA anchor: `9743e54148ffa668ce97f1cd7f133085cf8027d1`
Status: `completed / read-only decision-row extractor / bounded RI-first evidence slice`

## Purpose

This slice implements the first bounded extractor promised by the attribution-layer foundation plan.

It does **not** try to solve execution joins, trade joins, or ledger projection.
It only materializes canonical `decision_row` evidence on a fixed, already-locked RI surface.

## Scope

### Scope IN

- one read-only extractor for canonical `decision_row` artifacts
- one bounded RI-first surface defined by the fixed three-cohort phase-contrast artifact
- schema-compatible identity, action, reason, size, and router context fields
- deterministic rerun validation on the existing same-stack carrier

### Scope OUT

- runtime/config/strategy/backtest behavior changes
- execution-row implementation
- trade / position joining
- ledger-impact projection
- `OFF vs ON` outcome comparison

## Evidence inputs

Primary:

- `scripts/analyze/feature_attribution_post_phase14_ri_decision_surface_fixed_three_cohort_20260526.py`
- `results/evaluation/feature_attribution_post_phase14_ri_decision_surface_fixed_three_cohort_2026-05-26.json`
- `results/evaluation/ri_policy_router_2023_12_vs_2024_fixed_window_phase_contrast_2026-05-25.json`

Current-code anchors:

- `scripts/run/run_backtest.py`
- `src/core/strategy/decision.py`
- `src/core/strategy/ri_policy_router.py`
- `tools/compare_backtest_results.py`

## Exact command run

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m black scripts/analyze/feature_attribution_post_phase14_ri_decision_surface_fixed_three_cohort_20260526.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m ruff check scripts/analyze/feature_attribution_post_phase14_ri_decision_surface_fixed_three_cohort_20260526.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/feature_attribution_post_phase14_ri_decision_surface_fixed_three_cohort_20260526.py --base-sha 9743e54148ffa668ce97f1cd7f133085cf8027d1`

## Main result

The extractor emitted a bounded canonical `decision_row` artifact with status:

- `feature_attribution_ri_decision_surface_fixed_three_cohort_generated`

It materialized `22` exact decision rows across the already-locked fixed cohorts:

- `6` rows for `2023-12 wave 1`
- `7` rows for `2023-12 wave 2`
- `9` rows for the harmful `2024` target

All three cohorts were rerun on the same carrier with the same deterministic mode envelope and the same `effective_config_fingerprint`:

- `70f082360e0a2565e68afeabd14940b58b91a754441acf0e03b9aebc70bfc0db`

So Slice 2 now exists as a real decision-surface artifact rather than only a schema intention.

## Observed

### 1. The extractor cleanly separates continuation vs harmful target decisions on the canonical `decision_row` surface

Per-cohort decision summaries from the emitted artifact:

#### `2023-12 wave 1`

- exact rows: `6`
- action counts: `LONG = 6`
- selected policy counts: `RI_continuation_policy = 6`
- switch reason counts: `stable_continuation_state = 6`
- run window: `2023-11-15` -> `2023-12-18`

#### `2023-12 wave 2`

- exact rows: `7`
- action counts: `LONG = 7`
- selected policy counts: `RI_continuation_policy = 7`
- switch reason counts: `stable_continuation_state = 7`
- run window: `2023-11-22` -> `2023-12-27`

#### harmful `2024` target

- exact rows: `9`
- action counts: `NONE = 9`
- selected policy counts: `RI_no_trade_policy = 9`
- switch reason split:
  - `AGED_WEAK_CONTINUATION_GUARD = 4`
  - `insufficient_evidence = 5`
- run window: `2024-10-29` -> `2024-12-03`

The 2024 warning remains explicit here:

> on this fixed harmful target surface, the extractor does **not** reveal a hidden continuation wave that became harmless after schema normalization.
> It preserves the blocked / no-trade shape directly on emitted decision rows.

### 2. Canonical RI router fields are now materially emitted on the bounded attribution surface

Each emitted `decision_row` carries the schema-critical RI fields instead of only topline labels, including:

- `row_id`
- `bar_index`
- `timestamp`
- `action`
- `reasons`
- `size`
- `router_state`
- `router_debug`
- `effective_config_fingerprint`
- `mode_label`
- `component_toggle_label`

That means later slices no longer need to guess whether the bounded surface can carry:

- selected policy
- previous policy
- switch reason
- switch blocked / proposed state
- bars since regime change
- clarity / confidence / edge context
- size before / after policy routing

The extractor has already proven that it can.

### 3. `row_id` is stable locally, but not sufficient as a standalone cross-window key

The first implementation attempt failed honestly because duplicate `row_id` values appeared across separate cohort reruns.

Why:

- `row_id` is built from `symbol|timeframe|bar_index`
- `bar_index` resets when the engine reruns on a different bounded window

So the extractor had to freeze a derived composite identity:

- `decision_identity_key = row_id|bar_index|timestamp|symbol|timeframe`

That result matters beyond this script.
It is direct evidence that:

- `row_id` is valid as a local run-level anchor
- multi-window attribution artifacts need the comparator-style composite identity spine

### 4. The fixed three-cohort surface can be rerun deterministically with bounded warmup context

The extractor did need bounded warmup padding around the exact target timestamps:

- `30` days of start padding
- `1` day of end padding

But that padding affects only the run envelope, not the exact target row set.
The emitted rows are still filtered back down to the fixed timestamps from the prior phase-contrast artifact.

That is the right shape for Slice 2:

- enough context to compute decisions faithfully
- exact bounded timestamps for retained evidence

## Inferred

### 1. Slice 2 validates the canonical schema direction instead of widening it

The extractor did not need new runtime instrumentation.
It reused existing evaluation-hook and router-debug surfaces and simply emitted them under a canonical decision-row contract.

That is a positive sign for the broader attribution foundation lane:

- the branch is not blocked on decision-row observability
- the current missing join is still later in the chain: execution -> trade -> ledger

### 2. The best next step is now exactly what the plan already expected

Because decision-row capture is working, the next honest move is not another decision-surface variant.
It is the join-and-taxonomy slice:

- trade / exit join
- stop / exit taxonomy
- observed vs derived join proof

## Unverified

This slice does **not** prove:

- that `execution_row` can be emitted without new instrumentation
- that `decision.timestamp == trade.entry_time` is stable enough as a bounded join shortcut
- that stop / exit taxonomy can be derived losslessly from current `exit_reason` values alone
- that `ledger_impact_row` can be emitted without an intermediate join artifact

## Consequence

The next admissible step is now **Slice 3 — trade / exit join and stop taxonomy pass**.

That slice should reuse this emitted `decision_row` artifact rather than rebuilding the decision surface yet again.

## Verification

- `python -m black scripts/analyze/feature_attribution_post_phase14_ri_decision_surface_fixed_three_cohort_20260526.py` -> pass
- `python -m ruff check scripts/analyze/feature_attribution_post_phase14_ri_decision_surface_fixed_three_cohort_20260526.py` -> pass
- `python scripts/analyze/feature_attribution_post_phase14_ri_decision_surface_fixed_three_cohort_20260526.py --base-sha 9743e54148ffa668ce97f1cd7f133085cf8027d1` -> emitted artifact with status `feature_attribution_ri_decision_surface_fixed_three_cohort_generated`

## What changed and what did not

What changed:

- one new read-only extractor now emits schema-compatible RI `decision_row` artifacts on a fixed three-cohort surface
- one new retained artifact now captures `22` exact decision rows with router context attached
- the schema now has direct implementation evidence that multi-window artifacts need a composite `decision_identity_key`

What did **not** change:

- no runtime/config/strategy/backtest behavior changed
- no execution, trade, or ledger row family was implemented in this slice
- no stop taxonomy was introduced in code yet
- no promotion or runtime-authority claim was made
