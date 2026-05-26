# Feature Attribution — post-Phase-14 attribution layer observed surface inventory

Date: 2026-05-26
Branch: `feature/research-attribution-layer-foundation-2026-05-26`
Mode: `RESEARCH`
Base SHA anchor: `0b31bb0f306f0616368f3f69a3d32226beb2c2bf`
Status: `completed / read-only observed surface inventory / current branch support note`

## Purpose

This slice records the current observed repo surfaces that can support a bounded attribution layer without reopening runtime behavior.

It is the first completed step in the current attribution-layer foundation plan.

## Scope

### Scope IN

- current code surfaces only
- decision-level, policy-level, regime-level, execution-level, and trade-level observability relevant to attribution
- current branch guidance only

### Scope OUT

- runtime changes
- threshold or policy retuning
- historical roadmap reinterpretation as current authority
- implementation claims beyond what is observed in current code

## Evidence inputs

- `src/core/strategy/decision.py`
- `src/core/strategy/ri_policy_router.py`
- `src/core/backtest/engine.py`
- `src/core/backtest/engine_results.py`
- `src/core/backtest/position_tracker.py`
- `src/core/backtest/intelligence_shadow.py`
- `scripts/analyze/scpe_ri_v1_router_replay.py`
- `scripts/analyze/scpe_ri_v1_router_diagnostics.py`
- `scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_packet_20260526.py`
- `docs/analysis/diagnostics/feature_attribution_post_phase14_rebaseline_reconciliation_2026-04-02.md`

## Observed

### 1. Decision-level policy-router attribution data already exists on the runtime-adjacent decision surface

Observed in current code:

- `src/core/strategy/decision.py` writes:
  - `research_policy_router_state`
  - `research_policy_router_debug`
- `src/core/strategy/ri_policy_router.py` materializes debug fields including:
  - `selected_policy`
  - `switch_reason`
  - `switch_blocked`
  - `candidate`
  - `bars_since_regime_change`
  - `action_edge`
  - `confidence_gate`
  - `clarity_score`
  - `size_multiplier`

So a meaningful policy / regime / blocker attribution surface already exists at decision time.

### 2. A narrow historical feature-attribution seam already exists, but it is not yet a full attribution layer

Observed in `src/core/strategy/decision.py`:

- a `feature_attribution` request key exists
- it supports only a small bounded row set and a neutralize mode

That means the codebase already contains attribution-oriented logic, but it is a narrow seam-neutralization helper rather than a general decision-to-ledger attribution system.

### 3. Deterministic per-bar decision capture is already demonstrably possible

Observed in `scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_packet_20260526.py`:

- the backtest engine hook can capture, per bar:
  - `action`
  - `reasons`
  - `size`
  - `router_state`
  - `router_debug`
- the helper is already treated as a deterministic read-only evidence surface

So the branch does not need to invent per-bar capture from scratch.
A current pattern for deterministic decision-row extraction already exists.

### 4. Trade-level and exit-level surfaces already exist, but are not yet joined back to decision rows canonically

Observed in current backtest surfaces:

- `src/core/backtest/engine.py` closes positions with explicit `exit_reason`
- `src/core/backtest/engine_results.py` serializes `exit_reason`
- `src/core/backtest/position_tracker.py` stores:
  - `exit_reason`
  - `position_id`
  - `entry_reasons`
  - entry / exit fib debug payloads
  - partial vs final exit state

So trade / exit observability exists.
What is missing is the canonical attribution join from decision rows to final trade / ledger outcomes.

### 5. Stop-loss configuration exists, but stop taxonomy is not yet normalized into an attribution-friendly category layer

Observed in current config and engine surfaces:

- `src/core/config/schema.py` exposes:
  - `stop_loss_pct`
  - `take_profit_pct`
  - `exit_conf_threshold`
  - `regime_aware_exits`
  - `trailing_stop_enabled`
- `src/core/backtest/engine.py` contains explicit emergency stop-loss logic
- trade rows preserve `exit_reason`, but not a higher-level canonical stop taxonomy

So the ingredients for stop attribution exist, but the analysis layer still needs a stable derived classification for:

- take profit
- stop loss
- trailing stop
- regime exit
- confidence exit
- manual / other

### 6. Advisory research-ledger style artifact chains already exist, but they are not a substitute for a canonical attribution ledger

Observed in `src/core/backtest/intelligence_shadow.py` and `src/core/research_ledger/**`:

- advisory-only event capture exists
- ledger artifacts and indexes exist
- the repo already warns repeatedly that these are research/evidence surfaces, not runtime or governance authority

So these surfaces can help with provenance and retained evidence packaging, but they must not be mistaken for the attribution-layer schema itself.

### 7. Existing replay / diagnostics artifacts already prove policy-separated summaries are feasible

Observed in `scripts/analyze/scpe_ri_v1_router_replay.py` and `scripts/analyze/scpe_ri_v1_router_diagnostics.py`:

- policy counts
- switch reason counts
- proposed vs blocked switch rates
- dwell by policy
- veto summaries

So Genesis already has working examples of policy-separated descriptive metrics.
The new attribution layer should reuse that lesson rather than invent a parallel vocabulary.

### 8. The key current gap is the missing canonical join from decision -> execution -> trade -> ledger impact

Observed current gap:

- decision-level router context exists
- trade-level outcome and exit context exists
- advisory ledger/event packaging exists
- but no current canonical attribution row family ties them together deterministically on one bounded surface

That is the foundation gap to close first.
Not “more years,” and not “all features at once.”

## Inferred

### 1. The best first implementation lane is RI-first and bounded

Because the policy-router lane already has rich decision-time debug and multiple deterministic local packet helpers, the RI surface is the best current foundation lane for the attribution layer.

### 2. The first schema should distinguish observed fields from derived labels explicitly

Examples:

- observed today: `selected_policy`, `switch_reason`, `bars_since_regime_change`, `exit_reason`
- derived later: high-level stop taxonomy, collapse classification, driver / noise labels

If this distinction is not explicit, later attribution claims will blur observation and interpretation.

### 3. The first pass should be docs-first before a new helper is written

The codebase already has enough current observed anchors to freeze a schema before opening a new extractor.
That is the cheapest admissible next move.

## Unverified

The following remain open:

1. whether timestamp + bar index alone are sufficient as the stable join spine for every bounded slice
2. whether all stop / exit families can be recovered from current `exit_reason` plus current config without new instrumentation
3. whether feature snapshots beyond the current router debug surface are already available at the required point-in-time granularity
4. whether one bounded extractor can cover both decision collapse and final ledger impact without an intermediate join artifact

## Consequence

The next admissible step is a docs-first canonical schema draft for the attribution layer.

That slice should freeze:

- row families
- join keys
- required observed fields
- allowed derived labels
- `OFF vs ON` comparator compatibility rules

Only after that should a new extraction helper be written.

## What changed and what did not

What changed:

- the branch now has an explicit current observed-surface inventory for attribution-layer foundation work
- the first completed step in the plan is now materialized in repo
- the current missing foundation gap is named precisely: canonical decision-to-ledger joins

What did **not** change:

- no runtime/config/strategy/backtest behavior changed
- no historical roadmap was reactivated as current authority
- no attribution claims were promoted beyond current observed repo surfaces
- no full implementation helper was introduced yet
