# Feature Attribution — post-Phase-14 attribution layer foundation plan

Date: 2026-05-26
Branch: `feature/research-attribution-layer-foundation-2026-05-26`
Mode: `RESEARCH`
Base SHA anchor: `0b31bb0f306f0616368f3f69a3d32226beb2c2bf`
Status: `current working plan / bounded current-branch guidance / observational plus implementation planning`

## Purpose

This plan defines the smallest current-branch route for building a deterministic attribution layer that can answer, on bounded evidence surfaces:

- what actually drives edge
- what is merely active noise
- what is regime-dependent
- what collapses before execution or before ledger impact
- what changes when a bounded component is toggled `OFF` vs `ON` on the same stack

The plan is intentionally narrower than a full “analyze everything” program.
It starts with one bounded RI-first foundation lane and expands only after the observability and join surfaces are frozen.

## Scope

### Scope IN

- current-branch attribution-layer foundation work only
- deterministic RI-first bounded slices
- decision-level, policy-level, regime-level, execution-level, and trade/ledger-level observability
- docs and research helpers needed to freeze schema, joins, and first bounded extraction lane
- `OFF vs ON` compatibility on same-stack evidence surfaces

### Scope OUT

- runtime behavior changes
- threshold retuning or policy changes
- full-history all-family attribution in one pass
- treating historical `plan/**` materials as current execution authority
- promotion, readiness, or runtime-authority claims

## Success criteria

A first foundation tranche is complete only when all are true:

1. a current canonical attribution schema exists for the bounded RI lane
2. the schema separates:
   - decision
   - execution
   - trade / position
   - ledger impact
3. regime and policy fields are explicit rather than inferred ad hoc later
4. stop / exit semantics are classifiable at analysis time
5. the first bounded extractor can be rerun deterministically
6. the emitted evidence is usable for same-stack `OFF vs ON` comparison without changing runtime behavior

## Observed anchors already present in the repo

The current branch does **not** start from zero.
Observed current-code anchors already exist:

- `src/core/strategy/decision.py` already supports a narrow feature-attribution request seam and emits `research_policy_router_state` / `research_policy_router_debug`
- `src/core/strategy/ri_policy_router.py` already materializes policy, switch reason, dwell, mandate, size multiplier, and router debug context
- `scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_packet_20260526.py` already demonstrates deterministic per-bar capture of `router_state` and `router_debug`
- `src/core/backtest/position_tracker.py` and `src/core/backtest/engine_results.py` already preserve trade-level `exit_reason` and entry/exit debug payloads
- `src/core/backtest/intelligence_shadow.py` already shows an advisory-only event/ledger side channel, but not a canonical joined attribution ledger

These surfaces are enough to start a bounded attribution foundation lane without reopening runtime logic.

## Execution slices

### Slice 0 — foundation scope freeze and observed surface inventory

**Goal**

Lock the current branch route, inventory the real observed surfaces, and separate current guidance from historical feature-attribution roadmaps.

**Deliverables**

- this plan document
- `docs/analysis/feature_attribution/post_phase14/feature_attribution_post_phase14_attribution_layer_observed_surface_inventory_2026-05-26.md`

**Status**

- `completed in this turn`

### Slice 1 — canonical attribution schema draft

**Goal**

Define the canonical row families and joins for a bounded RI-first attribution ledger.

**Required outputs**

- one docs-first schema note describing:
  - decision row
  - execution row
  - trade / position row
  - ledger-impact row
  - join keys
  - required regime / policy / stop / outcome fields
- explicit field-level support for `OFF vs ON` same-stack evidence

**Done means**

- every later extractor can target one frozen schema instead of inventing ad hoc fields
- the schema distinguishes observed fields from derived labels

**Status**

- `next active slice`

### Slice 2 — deterministic decision-surface extractor

**Goal**

Materialize the canonical decision-side surface on one bounded RI carrier.

**Required outputs**

- one read-only helper under `scripts/analyze/`
- one emitted artifact under `results/evaluation/`
- one bounded analysis note under `docs/analysis/feature_attribution/post_phase14/`

**Done means**

- rerunning with the same stack reproduces the same schema-compatible decision rows
- regime / policy / switch / blocker fields are explicit in the artifact

### Slice 3 — trade / exit join and stop taxonomy pass

**Goal**

Join the decision surface to actual trade outcomes and classify stop / exit semantics.

**Required outputs**

- one deterministic join helper
- one stop / exit taxonomy note
- one artifact proving which joins are observed versus derived

**Done means**

- the bounded surface can answer which decisions became trades, which trades exited by what mechanism, and what reached ledger impact

### Slice 4 — regime- and policy-separated attribution metrics

**Goal**

Build the first regime-separated / policy-separated attribution cube on the bounded surface.

**Required outputs**

- metrics for:
  - expectancy
  - profit factor
  - drawdown contribution
  - take-profit share
  - stop-loss share
  - performance by regime and policy
- funnel metrics from decision to ledger impact

**Done means**

- the bounded artifact can distinguish high activity from actual edge
- the artifact identifies collapse points before execution or before ledger impact

### Slice 5 — `OFF vs ON` comparator contract

**Goal**

Freeze how bounded component toggles will be compared without changing the interpretation surface.

**Required outputs**

- one same-stack comparator contract note
- explicit semantics for diffing:
  - decision rows
  - executions
  - trades
  - ledger outcomes

**Done means**

- later attribution claims can say whether a component merely correlates with outcomes or actually changes them on the same stack

### Slice 6 — first bounded execution tranche

**Goal**

Run the first full attribution pass on one bounded RI-first surface.

**Required outputs**

- one deterministic execution helper chain
- one bounded analysis note
- one retained artifact pack usable for follow-on `OFF vs ON` probes

**Done means**

- the branch has its first real attribution-layer evidence surface instead of only a plan and schema

## Active next step

The next admissible step is **Slice 1 — canonical attribution schema draft**.

That slice should stay docs-first and answer only these questions:

1. what is the minimal canonical row family set?
2. what are the stable join keys?
3. which fields are truly observed today?
4. which labels are derived and therefore must stay explicitly marked as derived?

## What changed and what did not

What changed:

- the current branch now has a concrete current-branch plan surface for the attribution-layer foundation lane
- the plan is tied to current observed repo surfaces, not to archived `plan/**` guidance
- the next bounded slice is explicit instead of implied

What did **not** change:

- no runtime/config/strategy/backtest behavior changed
- no authority precedence changed
- no promotion/readiness/runtime claim was made
- no full-history attribution sweep was authorized
