# Feature Attribution — post-Phase-14 RI `OFF vs ON` comparator contract fixed three-cohort surface

Date: 2026-05-26
Branch: `feature/research-attribution-layer-foundation-2026-05-26`
Mode: `RESEARCH`
Base SHA anchor: `8587cf8e39826dce8527c97b8f826ac1486a02e7`
Status: `completed / docs-first comparator contract / fixed three-cohort RI surface`

## Purpose

This slice freezes how a bounded same-stack `OFF` vs `ON` comparison must be represented on the current RI attribution surface.

It does **not** run an `ON` experiment yet.
It only defines the row-alignment and diff contract that later bounded runs must obey if they want to claim real comparator evidence.

## Scope

### Scope IN

- one docs-first comparator contract for the fixed three-cohort RI surface
- explicit alignment rules for:
  - `decision_row`
  - execution-stage proxy rows
  - `trade_row`
  - `ledger_impact_row` proxy semantics
- explicit semantics for added / missing rows and for non-opening actionable decisions
- explicit same-stack preconditions for valid `OFF` vs `ON` attribution claims

### Scope OUT

- runtime/config/strategy/backtest behavior changes
- running the first bounded `ON` comparison itself
- canonical runtime `execution_row` implementation
- canonical runtime `ledger_impact_row` implementation
- broader all-history comparator policy

## Evidence inputs

Comparator implementation anchors:

- `tools/compare_backtest_results.py`
- `tests/backtest/test_compare_backtest_results.py`

Current bounded attribution surfaces:

- `results/evaluation/feature_attribution_post_phase14_ri_decision_surface_fixed_three_cohort_2026-05-26.json`
- `results/evaluation/feature_attribution_post_phase14_ri_trade_exit_join_fixed_three_cohort_2026-05-26.json`
- `results/evaluation/feature_attribution_post_phase14_ri_regime_policy_attribution_cube_fixed_three_cohort_2026-05-26.json`

Current schema / plan anchors:

- `docs/analysis/feature_attribution/post_phase14/feature_attribution_post_phase14_attribution_layer_canonical_schema_draft_2026-05-26.md`
- `docs/analysis/feature_attribution/post_phase14/feature_attribution_post_phase14_attribution_layer_foundation_plan_2026-05-26.md`
- `docs/analysis/feature_attribution/post_phase14/feature_attribution_post_phase14_ri_trade_exit_join_fixed_three_cohort_2026-05-26.md`
- `docs/analysis/feature_attribution/post_phase14/feature_attribution_post_phase14_ri_regime_policy_attribution_cube_fixed_three_cohort_2026-05-26.md`

## Main result

The fixed three-cohort RI surface now has a bounded `OFF` vs `ON` comparator contract with four explicit comparison layers:

1. `decision_row`
2. execution-stage proxy row
3. `trade_row`
4. `ledger_impact_row` proxy

The contract freezes three important truths:

- **identity alignment comes first**
- **observed fields must be compared before derived labels**
- **missing realized downstream rows must not be faked when an actionable decision never opens**

That means later `OFF` vs `ON` claims can be interpreted honestly instead of collapsing into a vague “results changed somehow” bucket.

## Observed

### 1. The repo already contains one real comparator primitive for decision-row parity

`tools/compare_backtest_results.py` already defines a deterministic row-alignment strategy for RI P1 OFF parity:

- stable key fields currently used:
  - `row_id`
  - `bar_index`
  - `timestamp`
  - `entry_time`
  - `position_id`
  - `symbol`
  - `timeframe`
- rows are grouped by deterministic key
- rows inside each key group are sorted canonically to eliminate order-only noise
- added / missing rows are counted as structural differences
- PASS is allowed only when:
  - no action mismatches
  - no reason mismatches
  - no size mismatches
  - no added rows
  - no missing rows

That primitive is narrower than the attribution layer needs, but it is the right starting point.

### 2. `decision_row` comparison must prefer `decision_identity_key`, not `row_id` alone

The Slice 2 decision artifact already proved that:

- `row_id` is locally stable within one run envelope
- `row_id` is **not** globally unique across separate bounded reruns

So the bounded attribution comparator must freeze:

- primary `decision_row` key: `decision_identity_key`
- allowed fallback key fields only when `decision_identity_key` is unavailable:
  - `row_id`
  - `bar_index`
  - `timestamp`
  - `symbol`
  - `timeframe`

Once rows are aligned, the comparison order is:

1. observed decision outcome fields:
   - `action`
   - `reasons`
   - `size`
2. observed router context fields:
   - `router_state`
   - `router_debug.selected_policy`
   - `router_debug.previous_policy`
   - `router_debug.switch_reason`
   - `router_debug.switch_blocked`
   - `router_debug.bars_since_regime_change`
   - `router_debug.action_edge`
   - `router_debug.confidence_gate`
   - `router_debug.clarity_score`
3. derived labels only after observed alignment:
   - regime bucket labels
   - policy-effect labels
   - any later attribution classification layers

### 3. Execution comparison remains a proxy surface, not an independent row family yet

Current branch truth is still:

- there is no canonical runtime `execution_row`
- Slice 3 only proved a bounded helper-side open-event seam
- non-opening actionable decisions still do not carry a canonical emitted `execution_status`

So the Slice 5 contract must freeze execution comparison as a **decision-aligned proxy layer**.

Comparator identity for execution proxy rows:

- `decision_identity_key`

Required proxy comparison fields:

- `join_status`
- `matched_open_event_count`
- `matched_position_keys`
- `entry_reasons_exact_match`

Allowed current proxy status values:

- `no_action_decision`
- `observed_open_event_matched`
- `non_opening_signal_without_execution_row`

This is intentionally narrow.
It prevents the comparator from pretending that the repo already emits a first-class execution ledger when it does not.

### 4. `trade_row` comparison must align on realized trade-leg identity, not on decision identity

Current schema and current runtime outputs already support a stable trade spine.

The Slice 5 contract freezes:

- `trade_position_key = position_id`
- `trade_leg_key = position_id|exit_time|is_partial`

Trade comparison must therefore proceed in two steps:

1. optional position-level grouping on `position_id`
2. trade-leg alignment on `trade_leg_key`

Once aligned, the comparator must compare observed trade fields before derived labels:

Observed identity and outcome fields:

- `position_id`
- `entry_time`
- `exit_time`
- `is_partial`
- `symbol`
- `side`
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

Derived trade labels only after observed alignment:

- `exit_family`
- `take_profit_flag`
- `stop_loss_flag`
- any later bucketization labels

Added / missing trade legs are structural differences, not formatting noise.

### 5. `ledger_impact_row` comparison is currently a trade-realized proxy only

The branch still does **not** have a canonical runtime `ledger_impact_row`.

So the Slice 5 comparator contract freezes a bounded proxy instead:

- ledger proxy identity = `trade_leg_key`
- ledger proxy exists only when a realized trade leg exists

Observed proxy fields:

- `realized_pnl`
- `realized_pnl_pct`
- `commission`
- `remaining_size`
- `exit_reason`
- `is_partial`

Derived proxy fields after alignment:

- `exit_family`
- `take_profit_flag`
- `stop_loss_flag`
- `regime_exit_flag`
- `confidence_exit_flag`
- `manual_or_other_exit_flag`
- `realized_drawdown_contribution_share`

That last field is especially important.
On the current Slice 4 cube it is still only:

- trade-realized loss share within the bounded surface

It is **not** yet:

- equity-path drawdown attribution
- canonical runtime ledger impact
- portfolio-level ledger truth

### 6. Non-opening actionable decisions must remain explicit execution-stage divergence, not synthetic missing trades

This is the most important honesty rule in the whole comparator contract.

If an aligned decision row is actionable but does not produce an observed open on one side, then the comparator must record:

- a decision-row alignment exists
- the execution proxy diverges
- no synthetic trade row should be created for the non-opening side
- no synthetic ledger proxy row should be created for the non-opening side

So when `OFF` and `ON` diverge, the contract must allow a path like this:

- same `decision_identity_key`
- baseline execution proxy = `non_opening_signal_without_execution_row`
- candidate execution proxy = `observed_open_event_matched`
- candidate side then legitimately contains added realized trade / ledger proxy rows downstream

This avoids two bad mistakes:

1. pretending a non-open is the same thing as a missing trade artifact
2. pretending a trade row exists when nothing opened

### 7. Same-stack comparator validity requires a fixed run envelope with only the sanctioned toggle changed

A valid `OFF` vs `ON` attribution claim must preserve the same run envelope.

Fields that must remain fixed across both sides:

- `base_sha`
- `symbol`
- `timeframe`
- `start_date`
- `end_date`
- `warmup_bars`
- `data_source_policy`
- deterministic env envelope
  - `GENESIS_RANDOM_SEED`
  - `GENESIS_FAST_WINDOW`
  - `GENESIS_PRECOMPUTE_FEATURES`
  - `GENESIS_PRECOMPUTE_CACHE_WRITE`
  - `GENESIS_MODE_EXPLICIT`
  - `GENESIS_FAST_HASH`
  - `GENESIS_SCORE_VERSION`

Fields that must be carried explicitly and reviewed, but may differ because of the sanctioned toggle:

- `component_toggle_label`
- `effective_config_fingerprint`

Required comparator validity rule:

> if anything besides the explicitly sanctioned toggle changes the run envelope, the resulting comparison is not a valid same-stack `OFF vs ON` attribution claim.

### 8. Comparator-ready fields are now frozen for the first bounded tranche

The current branch should preserve the following fields in any later `OFF` vs `ON` evidence pack:

- `decision_identity_key`
- `row_id`
- `timestamp`
- `position_id`
- `entry_time`
- `exit_time`
- `symbol`
- `timeframe`
- `regime`
- `selected_policy`
- `exit_family`

These are not all identity keys, but they are the minimum interpretation spine needed to align rows and then explain why aligned rows changed.

## Inferred

### 1. Slice 5 can stay docs-first because the repo already has a real alignment primitive

The branch did not need a speculative new comparator engine just to complete this slice.
The existing decision-row parity logic in `tools/compare_backtest_results.py` is enough to ground the contract.

### 2. Execution and ledger comparison remain deliberately weaker than decision and trade comparison

That is the correct outcome for this slice.
The branch should not pretend those surfaces are more mature than they really are.

### 3. Slice 6 can now run a bounded `OFF` vs `ON` experiment without redefining semantics midstream

That is the practical value of Slice 5.
The next slice no longer needs to invent:

- row keys
- added/missing semantics
- non-opening representation
- drawdown-proxy comparison meaning

Those are now frozen.

## Unverified

This slice still does **not** prove:

- that a bounded `ON` run on the same fixed surface will be valid under this contract
- that broader RI surfaces will preserve the same identity simplicity
- that a future canonical `execution_row` will match the current execution proxy categories exactly
- that a future canonical `ledger_impact_row` will preserve the same drawdown-proxy interpretation semantics

## Consequence

The next admissible step is now **Slice 6 — first bounded execution tranche**.

That slice should produce the first real same-stack `OFF` vs `ON` evidence pack under this frozen comparator contract.

## What changed and what did not

What changed:

- the branch now has a frozen docs-first `OFF vs ON` comparator contract for the fixed three-cohort RI surface
- row-alignment semantics are explicit for decision, execution-proxy, trade, and ledger-proxy layers
- non-opening actionable decisions now have an explicit comparison rule instead of being left to ad hoc interpretation
- the validity envelope for a same-stack `OFF` vs `ON` claim is now explicit

What did **not** change:

- no runtime/config/strategy/backtest behavior changed
- no `ON` run was executed in this slice
- no canonical runtime `execution_row` was introduced
- no canonical runtime `ledger_impact_row` was introduced
- no promotion or runtime-authority claim was made
