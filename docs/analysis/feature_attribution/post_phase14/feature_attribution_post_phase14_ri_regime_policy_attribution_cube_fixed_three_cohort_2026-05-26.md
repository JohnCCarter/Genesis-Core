# Feature Attribution — post-Phase-14 RI regime / policy attribution cube fixed three-cohort pass

Date: 2026-05-26
Branch: `feature/research-attribution-layer-foundation-2026-05-26`
Mode: `RESEARCH`
Base SHA anchor: `8b5cbe779a99bd2311df3cb1a69c04d035acc439`
Status: `completed / bounded regime-policy attribution cube / fixed three-cohort RI surface`

## Purpose

This slice builds the first regime-separated / policy-separated attribution cube over the bounded RI surface already frozen by Slice 2 and Slice 3.

It does **not** introduce a canonical `execution_row` or `ledger_impact_row`.
It only aggregates the currently observed `decision_row` and bounded realized trade surface into a deterministic metrics cube.

## Scope

### Scope IN

- one read-only helper that combines the Slice 2 decision artifact with the Slice 3 trade / exit join artifact
- one retained attribution-cube artifact under `results/evaluation/`
- regime-, policy-, and cohort-separated funnel and outcome metrics on the fixed three-cohort RI surface
- explicit trade-realized drawdown proxy semantics so later slices do not pretend a full ledger row already exists

### Scope OUT

- runtime/config/strategy/backtest behavior changes
- canonical runtime `execution_row` implementation
- canonical `ledger_impact_row` implementation
- same-stack `OFF vs ON` comparator execution
- widening beyond the fixed three-cohort RI surface

## Evidence inputs

Primary:

- `scripts/analyze/feature_attribution_post_phase14_ri_regime_policy_attribution_cube_fixed_three_cohort_20260526.py`
- `results/evaluation/feature_attribution_post_phase14_ri_regime_policy_attribution_cube_fixed_three_cohort_2026-05-26.json`
- `results/evaluation/feature_attribution_post_phase14_ri_decision_surface_fixed_three_cohort_2026-05-26.json`
- `results/evaluation/feature_attribution_post_phase14_ri_trade_exit_join_fixed_three_cohort_2026-05-26.json`

Current-code / schema anchors:

- `docs/analysis/feature_attribution/post_phase14/feature_attribution_post_phase14_attribution_layer_foundation_plan_2026-05-26.md`
- `docs/analysis/feature_attribution/post_phase14/feature_attribution_post_phase14_attribution_layer_canonical_schema_draft_2026-05-26.md`
- `docs/analysis/feature_attribution/post_phase14/feature_attribution_post_phase14_ri_trade_exit_join_fixed_three_cohort_2026-05-26.md`

## Exact command run

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m black scripts/analyze/feature_attribution_post_phase14_ri_regime_policy_attribution_cube_fixed_three_cohort_20260526.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m ruff check scripts/analyze/feature_attribution_post_phase14_ri_regime_policy_attribution_cube_fixed_three_cohort_20260526.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/feature_attribution_post_phase14_ri_regime_policy_attribution_cube_fixed_three_cohort_20260526.py --base-sha 8b5cbe779a99bd2311df3cb1a69c04d035acc439`

## Main result

The helper emitted a bounded attribution cube with status:

- `feature_attribution_ri_regime_policy_attribution_cube_fixed_three_cohort_generated`

On this fixed surface, the cube proves three things at once:

1. the **regime** dimension is flat:
   - unique regimes observed = `balanced`
2. the **policy** dimension is not flat:
   - unique selected policies observed = `RI_continuation_policy`, `RI_no_trade_policy`
3. high policy activity still does **not** imply edge:
   - `RI_continuation_policy` is the only policy that opens positions, but it is still net negative on the bounded surface

Global bounded outcome:

- decision rows: `22`
- actionable decision rows: `13`
- observed open decisions: `3`
- unresolved non-opening actionable decisions: `10`
- realized positions: `3`
- trade events: `4`
- gross realized PnL: `-24.07189`
- expectancy per position: `-8.023963333333`
- profit factor: `0.193654941157`

So Slice 4 now exists as a real current-branch attribution cube rather than only a promised next metric layer.

## Observed

### 1. Regime does **not** separate this fixed surface; policy does

The emitted cube shows:

- unique regimes observed = `balanced`
- unique selected policies observed = `RI_continuation_policy`, `RI_no_trade_policy`

That matters because it answers the first Slice 4 question directly:

- on this fixed surface, **regime separation is currently flat**
- the meaningful first separation comes from **selected policy**, not from regime label

This is not a bug in the cube.
It is a truthful property of the bounded evidence surface.

### 2. `RI_continuation_policy` carries all realized activity — and still loses overall

Policy rollup for `RI_continuation_policy`:

- decision rows: `13`
- actionable decision rows: `13`
- observed open decisions: `3`
- realized positions: `3`
- trade events: `4`
- actionable -> observed open rate: `0.230769230769`
- actionable -> non-opening rate: `0.769230769231`
- gross realized PnL: `-24.07189`
- expectancy per position: `-8.023963333333`
- profit factor: `0.193654941157`
- realized drawdown contribution share: `1.0`

Trade-event exit-family shares for `RI_continuation_policy`:

- `take_profit = 0.25`
- `stop_loss = 0.5`
- `trailing_stop = 0.25`

Final-position exit-family shares for `RI_continuation_policy`:

- `stop_loss = 0.666666666667`
- `trailing_stop = 0.333333333333`
- `take_profit = 0.0`

So the first policy-separated attribution answer is already uncomfortable but useful:

> the policy that creates all realized opportunities on this bounded surface is also the policy carrying all realized losses.

### 3. `RI_no_trade_policy` preserves the harmful `2024` target as a real no-trade surface

Policy rollup for `RI_no_trade_policy`:

- decision rows: `9`
- actionable decision rows: `0`
- observed opens: `0`
- realized positions: `0`
- trade events: `0`
- gross realized PnL: `0.0`

This preserves the explicit warning rather than weakening it:

> Tänk på att policyn även har försämrat bra år, tex 2024.

More narrowly here, the harmful `2024` target remains a true bounded no-trade policy surface even after the first attribution cube is built.

### 4. Activity still collapses mostly before execution / realized trade impact

The global funnel metrics are:

- decision -> observed open rate: `0.136363636364`
- actionable -> observed open rate: `0.230769230769`
- actionable -> non-opening rate: `0.769230769231`
- realized position -> trade event rate: `1.333333333333`

That means the main current collapse is still upstream:

- not between open position and realized trade event
- but between actionable decision and observed open

This preserves the Slice 3 conclusion and strengthens it with quantified funnel metrics.

### 5. Cohort splits show that the same regime/policy bucket is still mixed downstream

All three cohort-policy-regime buckets are still `balanced`, but their realized outcomes differ.

#### `2023-12 wave 1` + `balanced` + `RI_continuation_policy`

- decision rows: `6`
- observed opens: `2`
- realized positions: `2`
- gross realized PnL: `-15.127162`
- expectancy per position: `-7.563581`
- profit factor: `0.2765017438`
- realized drawdown contribution share: `0.700375116973`
- trade-event exit-family split: `take_profit = 1`, `stop_loss = 1`, `trailing_stop = 1`

#### `2023-12 wave 2` + `balanced` + `RI_continuation_policy`

- decision rows: `7`
- observed opens: `1`
- realized positions: `1`
- gross realized PnL: `-8.944728`
- expectancy per position: `-8.944728`
- profit factor: `0.0`
- realized drawdown contribution share: `0.299624883027`
- trade-event exit-family split: `stop_loss = 1`

#### harmful `2024` target + `balanced` + `RI_no_trade_policy`

- decision rows: `9`
- observed opens: `0`
- realized positions: `0`
- gross realized PnL: `0.0`

This matters because it prevents an overly easy story.
Even inside the only live regime/policy bucket on the continuation-positive side:

- one cohort still mixed partial-take-profit / trailing-stop / stop-loss outcomes
- another cohort is pure realized stop-loss

So policy state alone is **not** the full explanation for edge quality on this bounded surface.

### 6. Drawdown contribution is now explicitly frozen as a trade-realized proxy, not a fake ledger row

The emitted cube uses:

- `realized_drawdown_contribution_share = bucket gross_loss_abs / global gross_loss_abs`

That is useful because it quantifies which bucket carries realized downside on the current observed surface.
But it is still only a bounded trade-realized loss proxy.

It is **not** yet:

- equity-path drawdown attribution
- a canonical `ledger_impact_row`
- a full portfolio drawdown decomposition

That honesty is important for later slices.

## Inferred

### 1. Slice 4 successfully distinguishes activity from realized edge

This was the main requirement for the slice.
The cube now shows that:

- `RI_continuation_policy` has all the activity
- `RI_continuation_policy` also has all realized downside on this bounded surface
- therefore policy activity cannot be treated as positive evidence by itself

### 2. The next useful comparator seam is policy-preserving same-stack alignment, not more current-surface aggregation

At this point the branch already has:

- decision rows
- bounded join truth
- stop taxonomy
- policy/regime attribution cube

The next question is no longer “can we aggregate this current surface one more time?”
It is:

- how should `OFF` vs `ON` runs align on the same schema without inventing execution/ledger surfaces?

That points directly to Slice 5.

### 3. The fixed surface is regime-flat but still useful

A flat regime dimension might look disappointing at first, but it is actually informative.
It tells us that:

- this bounded surface is not yet the place where regime labels explain outcome variation
- policy state and downstream trade realization do more explanatory work here than regime alone

That is a real finding, not a failed slice.

## Unverified

This slice still does **not** prove:

- that broader RI surfaces will remain regime-flat
- that the `10` unresolved non-opening actionable decisions can already be classified without a canonical execution-status surface
- that the trade-realized drawdown proxy will match a later true ledger / equity drawdown decomposition
- how same-stack `OFF vs ON` row alignment should treat added/missing non-opening decisions and realized trade rows

## Consequence

The next admissible step is now **Slice 5 — `OFF vs ON` comparator contract**.

That slice should freeze:

- row alignment semantics for decision, observed-open, realized-position, and trade-event surfaces
- mandatory comparator keys
- how to represent added/missing rows
- how to compare exit-family and realized-drawdown-proxy metrics without pretending a canonical ledger row already exists

## Verification

- `python -m black scripts/analyze/feature_attribution_post_phase14_ri_regime_policy_attribution_cube_fixed_three_cohort_20260526.py` -> pass
- `python -m ruff check scripts/analyze/feature_attribution_post_phase14_ri_regime_policy_attribution_cube_fixed_three_cohort_20260526.py` -> pass
- `python scripts/analyze/feature_attribution_post_phase14_ri_regime_policy_attribution_cube_fixed_three_cohort_20260526.py --base-sha 8b5cbe779a99bd2311df3cb1a69c04d035acc439` -> emitted artifact with status `feature_attribution_ri_regime_policy_attribution_cube_fixed_three_cohort_generated`

## What changed and what did not

What changed:

- one new read-only helper now emits a bounded regime-/policy-separated attribution cube on top of Slice 2 + Slice 3
- one new retained artifact now freezes funnel, performance, exit-share, and drawdown-proxy metrics for the fixed three-cohort RI surface
- the branch now has direct evidence that policy separation matters here while regime separation is currently flat
- the branch now has explicit comparator-ready fields preserved for the upcoming Slice 5 contract

What did **not** change:

- no runtime/config/strategy/backtest behavior changed
- no canonical runtime `execution_row` was introduced
- no canonical `ledger_impact_row` was introduced
- no same-stack `OFF vs ON` execution was run in this slice
- no promotion or runtime-authority claim was made
