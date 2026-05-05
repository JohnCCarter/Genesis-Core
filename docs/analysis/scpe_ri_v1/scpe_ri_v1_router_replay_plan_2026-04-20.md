# SCPE RI V1 Router Replay Plan

Date: 2026-04-20
Mode: RESEARCH
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `active / docs-only / bounded research-only replay plan`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `LOW` — docs-only replay planning for an RI family-local research lane; no runtime/config/test/results mutation.
- **Required Path:** `Quick`
- **Objective:** define the bounded research-only replay lane for SCPE RI V1, including fixed inputs, eligible decision points, canonical outputs, observational metrics, validation rules, and fail-closed stop conditions.
- **Candidate:** `SCPE RI V1 router replay plan`
- **Base SHA:** `ef16cf53`

### Scope

- **Scope IN:**
  - `docs/scpe_ri_v1_architecture.md`
  - `docs/analysis/scpe_ri_v1/scpe_ri_v1_router_replay_plan_2026-04-20.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `artifacts/**`
  - `results/**`
  - any runtime integration
  - any backtest execution integration
  - any cross-family routing
  - any model fitting or optimization
- **Expected changed files:**
  - `docs/scpe_ri_v1_architecture.md`
  - `docs/analysis/scpe_ri_v1/scpe_ri_v1_router_replay_plan_2026-04-20.md`
- **Max files touched:** `2`

### Gates required

- `pre-commit run --files docs/scpe_ri_v1_architecture.md docs/analysis/scpe_ri_v1/scpe_ri_v1_router_replay_plan_2026-04-20.md`

### Stop Conditions

- input ambiguity or missing provenance
- inability to define a deterministic RI-only decision population
- inability to prove decision-time validity of a state field
- any need to touch runtime or execution surfaces
- any attempt to widen the replay into causal execution-performance claims

## 1. Replay objective

The replay lane exists to materialize a deterministic, audit-friendly RI family-local routing trace without changing any execution path.

It must answer only this bounded question:

> If Genesis replays RI-local decision points using a minimal deterministic router and decision-time-only RI state, what routing behavior, stability profile, veto profile, and trade-level observational outcome structure appear?

This replay lane is:

- docs-first
- research-only
- shadow-only
- default OFF
- RI-only
- strictly below runtime integration

## 2. Input freeze requirements

Replay implementation must not discover inputs implicitly.
It must begin from a fixed `input_manifest.json` stored under the replay result root.

The manifest must include at minimum:

- every source file used by the replay
- canonical absolute or repo-relative path for each source
- content hash for each source
- declared field allowlist version
- declared eligible-decision-point definition version
- replay code version / script hash

If the replay cannot declare and freeze its inputs cleanly, it must stop.

## 3. Eligible historical RI decision points

Replay population must be explicit and deterministic.
A row may enter the replay only if all of the following are true:

- `family_tag = RI`
- the row is a valid historical RI decision timestamp
- decision-time state is fully materializable from allowlisted inputs
- no required core decision field is missing
- no forbidden post-entry or future-derived field is required to route it
- ordering is deterministic

Rows that fail these conditions must remain excluded or be marked unsupported according to the replay contract.
They must not be repaired through heuristic backfill.

## 4. Replay flow

For every eligible RI decision point, the replay must perform exactly these steps:

1. materialize `CoreDecisionState`
2. derive `RIDecisionState`
3. apply deterministic RI router
4. produce `RIRouterDecision`
5. apply selected RI policy
6. apply Risk/Veto
7. emit one complete canonical trace row

This replay does **not** alter execution.
It only materializes the routing and downstream safety trace.

## 5. V1 router constraints

The replayed router must remain minimal and explicit.

It may choose among exactly:

- `RI_continuation_policy`
- `RI_defensive_transition_policy`
- `RI_no_trade_policy`

Required constraints:

- deterministic rule-based router only
- no probabilistic blending
- no ML
- no optimization
- no hidden internal score composition unless fully documented
- no cross-family logic

Required controls:

- switch threshold
- hysteresis
- minimum dwell time
- confidence-aware no-trade capability

## 6. Risk / Veto constraints in replay

Risk/Veto may:

- pass
- reduce
- cap
- veto
- force no-trade

Risk/Veto may **NOT**:

- choose another policy
- switch family
- invent a new route
- act as a hidden router

Every intervention must be traced explicitly.

## 7. Canonical output root

Replay implementation must write to:

- `results/research/scpe_v1_ri/`

Required files:

- `input_manifest.json`
- `routing_trace.ndjson` ← canonical trace SSOT
- `state_trace.json` ← derived summary
- `policy_trace.json` ← derived summary
- `veto_trace.json` ← derived summary
- `replay_metrics.json`
- `summary.md`

Every replay row must include:

- `family_tag = "RI"`

Optional implementation-local files are allowed only if they stay inside the replay root and are documented in the output manifest.

## 8. Trace requirements

Every row in `routing_trace.ndjson` must include at minimum:

- decision key / timestamp
- family tag
- compact `CoreDecisionState` summary
- compact `RIDecisionState` summary
- selected policy
- previous policy
- switch reason
- confidence
- mandate level
- whether a switch was proposed, delayed, or blocked
- dwell duration
- veto action
- final routed action

The trace must be stable under repeated identical replay.
No nondeterministic ordering, timestamp injection, or environment-dependent metadata is allowed.

## 9. Metrics policy

V1 metrics must be interpreted as **observational conditional metrics**, not as integrated strategy-performance proof.

The replay may report trade-level outcome structure conditional on routed policy/state.
It may **not** claim that the replayed router has already improved the live or backtest baseline in causal execution terms.

### Mandatory routing metrics

- policy selection frequency
- switch count
- oscillation rate
- average dwell time per policy
- veto rate
- no-trade rate
- confidence distribution
- time share per policy

### Mandatory conditional observational metrics

Per routed policy:

- trade count
- winrate
- average win
- average loss
- profit factor on the observed routed subset

Per RI state bucket:

- trade count
- winrate
- average win
- average loss
- profit factor on the observed state-conditioned subset

### Year split

Replay findings must be reported separately for:

- `2024`
- `2025`

The summary must compare both years explicitly.

### Interpretation questions

At minimum the summary must answer:

- Did routing stabilize or oscillate excessively?
- Did no-trade become too dominant?
- Did continuation and defensive policies behave materially differently?
- Did `2025` improve loss containment without destroying `2024`?
- Is router quality visible at trade-level observational outcomes?
- Is the veto layer dominating the system?

## 10. Validation requirements

Replay implementation must verify all of the following:

- identical outputs across repeated runs
- no baseline behavior change
- no leakage
- no future-derived fields in state
- no policy/family substitution by risk layer
- stable trace generation
- stable input manifest and source hashes

If any validation fails:

- stop
- document failure
- do not proceed further

## 11. Additional stop conditions

The lane must stop and report a bounded failure if any of the following occurs:

- `GOVERNANCE_BLOCKED`
  - governance ambiguity or instruction conflict
- `STATE_ALLOWLIST_NOT_PROVEN`
  - a routing field cannot be proven decision-time valid
- `POLICY_SEPARATION_NOT_ESTABLISHED`
  - continuation and defensive policies are not materially distinct in routed posture or observed outcome structure
- `VETO_DOMINANCE`
  - veto/no-trade dominates so strongly that router-selected policies are rarely decisive
- `OSCILLATION_UNCONTROLLED`
  - stability controls fail to prevent excessive switching
- `INPUT_SURFACE_NOT_FROZEN`
  - replay inputs cannot be frozen and hashed cleanly
- `OUT_OF_SCOPE_GOVERNANCE_REQUIRED`
  - implementation would require runtime integration, cross-family routing, or execution-path change

## 12. Final replay summary requirements

`summary.md` under the replay root must include at minimum:

- what was built
- exact scope boundaries
- what was intentionally excluded
- state definition summary
- policy set summary
- router behavior summary
- stability findings
- `2024` vs `2025` comparison
- key risks
- whether the lane is ready for governance review
- explicit recommendation:
  - `APPROACH_PROMISING`
  - `NEEDS_REVISION`
  - `NOT_READY`

## 13. Non-claims explicitly forbidden

The replay summary may **not** claim any of the following:

- runtime readiness
- live execution improvement
- backtest-integrated edge improvement
- cross-family superiority
- causal performance improvement from replay alone
- approval for runtime or backtest integration

This lane stops after docs + research-only replay artifacts.
Anything beyond that requires new governance approval.
