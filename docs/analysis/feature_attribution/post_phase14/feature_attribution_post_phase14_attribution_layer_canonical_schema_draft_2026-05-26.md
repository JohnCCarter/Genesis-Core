# Feature Attribution — post-Phase-14 attribution layer canonical schema draft

Date: 2026-05-26
Branch: `feature/research-attribution-layer-foundation-2026-05-26`
Mode: `RESEARCH`
Base SHA anchor: `0b31bb0f306f0616368f3f69a3d32226beb2c2bf`
Status: `completed / docs-first canonical schema draft / current branch guidance for bounded RI attribution work`

## Purpose

This slice freezes the canonical row families, join keys, and field semantics for the first bounded RI-first attribution layer.

The goal is not to claim that every row family is fully implemented already.
The goal is to stop later extractors from inventing ad hoc schemas.

## Scope

### Scope IN

- current-branch canonical schema for one bounded RI-first attribution lane
- decision, execution, trade / position, and ledger-impact row families
- stable join keys and support-state classification
- explicit separation between observed fields and derived labels
- explicit compatibility rules for same-stack `OFF vs ON` evidence

### Scope OUT

- runtime behavior changes
- threshold / policy retuning
- full multi-family all-history schema expansion
- promotion, readiness, or runtime-authority claims

## Evidence inputs

- `scripts/run/run_backtest.py`
- `tools/compare_backtest_results.py`
- `src/core/strategy/decision.py`
- `src/core/strategy/ri_policy_router.py`
- `src/core/backtest/engine_results.py`
- `src/core/backtest/position_tracker.py`
- `src/core/backtest/intelligence_shadow.py`
- `scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_packet_20260526.py`
- `scripts/analyze/feature_attribution_post_phase14_ri_decision_surface_fixed_three_cohort_20260526.py`
- `results/evaluation/feature_attribution_post_phase14_ri_decision_surface_fixed_three_cohort_2026-05-26.json`
- `docs/analysis/feature_attribution/post_phase14/feature_attribution_post_phase14_attribution_layer_foundation_plan_2026-05-26.md`
- `docs/analysis/feature_attribution/post_phase14/feature_attribution_post_phase14_attribution_layer_observed_surface_inventory_2026-05-26.md`

## Main result

The bounded RI attribution layer should use **four canonical row families**:

1. `decision_row`
2. `execution_row`
3. `trade_row`
4. `ledger_impact_row`

Only two of those are fully observed on current code surfaces today:

- `decision_row`
- `trade_row`

The other two are still required by schema, but their first current implementation status differs:

- `execution_row` is a **schema-required gap** with only partial current observability
- `ledger_impact_row` is a **schema-required projection** that can be derived from trade rows in the first bounded tranche

That is the key freeze:

> the canonical schema is wider than the currently materialized surfaces, but narrower than a full-system universal ledger.

## Observed

### 1. Canonical row families and support state

| Row family          | Canonical purpose                                                                             | Current support state               | Primary observed anchor                                                                                                                                                                              |
| ------------------- | --------------------------------------------------------------------------------------------- | ----------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `decision_row`      | freeze what the system decided on one bar before downstream trade outcome interpretation      | `observed_now`                      | `scripts/run/run_backtest.py`, `src/core/strategy/decision.py`, `src/core/strategy/ri_policy_router.py`, `scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_packet_20260526.py` |
| `execution_row`     | record whether a decision became an executable / filled action or collapsed before that point | `required_gap_partial_support_only` | partial hints only from decision result surfaces; no current canonical serialized execution row                                                                                                      |
| `trade_row`         | record completed or partial realized trade legs                                               | `observed_now`                      | `src/core/backtest/position_tracker.py`, `src/core/backtest/engine_results.py`                                                                                                                       |
| `ledger_impact_row` | express realized capital impact in an attribution-safe form                                   | `derived_from_trade_row_in_v1`      | trade rows plus summary / equity context                                                                                                                                                             |

### 2. Stable join spine

The canonical join spine for the bounded RI lane should be frozen as follows.

#### 2.1 Decision spine

Observed stable identity anchors already exist:

- `row_id = {symbol}|{timeframe}|{bar_index}`
- `bar_index`
- `timestamp`
- `symbol`
- `timeframe`

These are already emitted in `scripts/run/run_backtest.py` and reused in `src/core/backtest/intelligence_shadow.py` as `backtest_row` references.

Observed follow-up from the Slice 2 fixed-three-cohort extractor:

- `row_id` remains stable inside one run envelope
- `row_id` alone is **not** globally unique across separate bounded reruns because `bar_index` resets per run window

**Freeze:**

- `local_decision_row_id = row_id`
- `decision_identity_key = row_id|bar_index|timestamp|symbol|timeframe` for multi-window artifacts and same-stack comparator-ready extracts

Supporting identity fields must still be carried explicitly:

- `bar_index`
- `timestamp`
- `symbol`
- `timeframe`

#### 2.2 `OFF vs ON` comparator spine

Current comparator logic in `tools/compare_backtest_results.py` already treats the following as stable row-key fields:

- `row_id`
- `bar_index`
- `timestamp`
- `entry_time`
- `position_id`
- `symbol`
- `timeframe`

**Freeze:** these become the allowed canonical identity fields for later same-stack comparator work.

#### 2.3 Trade spine

Observed trade-level stable identity anchors already exist:

- `position_id`
- `entry_time`
- `exit_time`
- `is_partial`
- `symbol`
- `side`

**Freeze:**

- `trade_position_key = position_id`
- `trade_leg_key = position_id|exit_time|is_partial`

#### 2.4 Decision -> trade join status

A direct observed join from decision rows to trade rows is **not** fully materialized today.

Current branch truth:

- `decision_row` has a stable `row_id`
- `trade_row` has a stable `position_id`
- current decision rows do **not** carry `position_id`

So the schema must freeze this honestly:

- `decision_row -> trade_row` is **not currently an observed direct join**
- the first bounded trade join must therefore pass through:
  - a future `execution_row`, or
  - a bounded derived join contract that stays explicitly marked as derived

#### 2.5 Trade -> ledger join status

`ledger_impact_row` v1 should be a deterministic projection over trade rows.

**Freeze:**

- `ledger_impact_key = trade_leg_key`

That keeps the first bounded ledger layer simple and avoids pretending that a separate runtime-native ledger row already exists.

### 3. Canonical required fields by row family

#### 3.1 `decision_row`

Required identity fields:

- `row_id`
- `bar_index`
- `timestamp`
- `symbol`
- `timeframe`

Required derived identity field for multi-window artifacts:

- `decision_identity_key`

Required observed decision outcome fields:

- `action`
- `reasons`
- `size`

Required observed RI context fields for the bounded RI lane:

- `router_state`
- `router_debug.selected_policy`
- `router_debug.previous_policy`
- `router_debug.raw_target_policy`
- `router_debug.switch_reason`
- `router_debug.switch_proposed`
- `router_debug.switch_blocked`
- `router_debug.switch_control_mode`
- `router_debug.candidate`
- `router_debug.regime`
- `router_debug.zone`
- `router_debug.mandate_level`
- `router_debug.confidence_level`
- `router_debug.dwell_duration`
- `router_debug.bars_since_regime_change`
- `router_debug.action_edge`
- `router_debug.confidence_gate`
- `router_debug.clarity_score`
- `router_debug.size_multiplier`
- `router_debug.size_before_policy_router`
- `router_debug.size_after_policy_router`

Required run-context fields for later reproducibility and `OFF vs ON` comparison:

- `base_sha`
- `effective_config_fingerprint`
- `start_date`
- `end_date`
- `warmup_bars`
- `mode_label`
- `component_toggle_label`

#### 3.2 `execution_row`

This row family is schema-required but not yet fully observed.

Required future identity fields:

- `decision_row_key`
- `timestamp`
- `symbol`
- `timeframe`

Required future outcome fields:

- `execution_status`
- `collapse_stage`
- `collapse_reason`
- `filled_action`
- `filled_size`
- `position_id` if a position is opened
- `entry_time` if a position is opened

Current support note:

- `decision.action` is observed
- a canonical fill / no-fill / collapse serialization is **not** yet frozen in current outputs

So these fields are frozen as schema targets, not as already-materialized branch outputs.

#### 3.3 `trade_row`

Required observed identity fields:

- `position_id`
- `entry_time`
- `exit_time`
- `is_partial`
- `symbol`
- `side`

Required observed trade fields:

- `size`
- `entry_price`
- `exit_price`
- `pnl`
- `pnl_pct`
- `commission`
- `remaining_size`
- `exit_reason`
- `entry_regime`
- `entry_reasons`
- `entry_fib_debug`
- `exit_fib_debug`

#### 3.4 `ledger_impact_row`

`ledger_impact_row` v1 should be a deterministic projection over `trade_row`.

Required identity fields:

- `ledger_impact_key`
- `trade_leg_key`
- `position_id`

Required realized-impact fields:

- `realized_pnl`
- `realized_pnl_pct`
- `commission`
- `remaining_size`
- `exit_reason`
- `is_partial`

Required derived attribution fields:

- `exit_family`
- `take_profit_flag`
- `stop_loss_flag`
- `regime_exit_flag`
- `confidence_exit_flag`
- `manual_or_other_exit_flag`

Optional later extension fields:

- `equity_before`
- `equity_after`
- `drawdown_contribution`
- `expectancy_bucket`

These later fields are not required for the first bounded extractor if they cannot be emitted deterministically without widening scope.

### 4. Observed vs derived boundary

The attribution layer must freeze the following boundary.

#### Observed fields

Fields are `observed` only if they are emitted directly by current code surfaces.
Examples in current repo:

- `row_id`
- `bar_index`
- `timestamp`
- `action`
- `reasons`
- `size`
- `selected_policy`
- `switch_reason`
- `switch_blocked`
- `bars_since_regime_change`
- `exit_reason`
- `position_id`
- `entry_time`
- `exit_time`
- `pnl`
- `pnl_pct`

#### Derived fields

Fields are `derived` if they classify or aggregate current observed values.
Examples for the bounded attribution layer:

- `decision_identity_key`
- `exit_family`
- `take_profit_flag`
- `stop_loss_flag`
- `collapse_stage`
- `collapse_reason` when not directly emitted
- `driver_vs_noise_label`
- `regime_bucket`
- `policy_effect_bucket`
- `drawdown_contribution`
- `expectancy_bucket`

**Freeze:** every derived field must remain visibly labeled as derived in emitted artifacts and notes.

### 5. Stop / exit taxonomy freeze for v1

Because current code preserves `exit_reason` but not a canonical attribution taxonomy, the schema should freeze the first derived stop / exit family labels now.

Canonical `exit_family` values for v1:

- `take_profit`
- `stop_loss`
- `trailing_stop`
- `regime_exit`
- `confidence_exit`
- `manual_or_other`
- `unknown_unclassified`

Required rule:

- `exit_reason` remains the observed source field
- `exit_family` is always derived from `exit_reason` plus bounded current config context
- if the mapping is ambiguous, emit `unknown_unclassified` rather than inventing certainty

### 6. Same-stack `OFF vs ON` compatibility rules

The canonical schema must support same-stack comparator work without changing interpretation semantics.

Required comparator envelope fields for every row family:

- `base_sha`
- `symbol`
- `timeframe`
- `start_date`
- `end_date`
- `warmup_bars`
- `effective_config_fingerprint`
- `mode_label`
- `component_toggle_label`

Required comparator rules:

1. `OFF vs ON` comparisons must keep the same stack except for the explicitly toggled component.
2. Decision rows must compare on stable row identity before comparing action / reasons / size.
3. Trade and ledger rows must compare on `position_id` / leg identity before interpreting outcome deltas.
4. Added or missing rows count as structural differences, not as formatting noise.
5. Derived labels may be compared only after observed row alignment is complete.

## Inferred

### 1. `row_id` is the correct local decision spine, but multi-window extracts need a composite identity key

This is the strongest current repo-wide anchor because it already appears in:

- decision-row capture
- intelligence-shadow references
- parity comparison logic

But the Slice 2 fixed-three-cohort extractor also showed that separate rerun windows can reuse the same `row_id` values when `bar_index` resets.

So the stable cross-window identity must be the composite `decision_identity_key`, not `row_id` alone.

### 2. The first execution gap should be solved by a dedicated row family, not by smuggling execution guesses into decision rows

That keeps the schema honest and prevents “decision == execution” leakage.

### 3. `ledger_impact_row` should start as a deterministic trade projection, not as a fake independent authority surface

That matches current repo truth while still satisfying the need to separate realized trade events from attribution metrics.

## Unverified

The following remain open after this schema freeze:

1. whether a future extractor can observe canonical `execution_row` fields without touching runtime behavior
2. whether `decision.timestamp == trade.entry_time` is sufficiently stable to support any bounded derived join before `position_id` is available upstream
3. whether full drawdown-contribution attribution can be emitted deterministically in the first ledger projection slice without widening scope
4. whether additional feature snapshots beyond current RI router debug are already available at the required point-in-time granularity

## Consequence

The next admissible step is now **Slice 2 — deterministic decision-surface extractor**.

That extractor should target only the now-frozen `decision_row` schema and should not try to solve the trade join or ledger projection in the same slice.

## What changed and what did not

What changed:

- the branch now has a frozen canonical schema draft for the bounded RI attribution lane
- row families, join keys, observed fields, derived labels, and `OFF vs ON` support rules are explicit
- multi-window decision identity now distinguishes local `row_id` from cross-window `decision_identity_key`
- the execution gap is now named as a schema gap instead of being silently ignored

What did **not** change:

- no runtime/config/strategy/backtest behavior changed
- no extractor was introduced in this slice
- no stop taxonomy was implemented in code yet
- no readiness or runtime-authority claim was made
