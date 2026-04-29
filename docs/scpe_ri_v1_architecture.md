# SCPE RI V1 Architecture

Date: 2026-04-20
Mode: RESEARCH
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `active / docs-only / governance-and-architecture packet`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `LOW` — docs-only architecture and governance packet for an RI family-local research lane; no runtime/config/test/results mutation.
- **Required Path:** `Quick`
- **Objective:** define a governance-compatible, RI-only V1 architecture for a Deterministic State-Conditioned Policy Engine (SCPE) that remains docs-first, research-only, default-OFF, and strictly below runtime integration.
- **Candidate:** `SCPE RI V1 governance-and-architecture packet`
- **Base SHA:** `ef16cf53`

### Scope

- **Scope IN:**
  - `docs/scpe_ri_v1_architecture.md`
  - `docs/analysis/scpe_ri_v1_router_replay_plan_2026-04-20.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `artifacts/**`
  - `results/**`
  - any runtime integration
  - any backtest execution integration
  - any cross-family routing between `ri` and `legacy`
  - any default-ON functionality
  - any adaptive runtime behavior, online learning, or ML model work
- **Expected changed files:**
  - `docs/scpe_ri_v1_architecture.md`
  - `docs/analysis/scpe_ri_v1_router_replay_plan_2026-04-20.md`
- **Max files touched:** `2`

### Gates required

- `pre-commit run --files docs/scpe_ri_v1_architecture.md docs/analysis/scpe_ri_v1_router_replay_plan_2026-04-20.md`

### Stop Conditions

- governance ambiguity or conflicting instructions
- any attempt to widen the lane beyond RI-only routing research
- any attempt to touch runtime or execution surfaces
- any need to weaken decision-time-only state rules
- any need to let risk/veto act as a hidden router

### Output required

- one docs-only governance-and-architecture packet
- one bounded research-only replay plan

## Concise scope confirmation

This lane is intentionally narrow.
It is **RI family-local only**, **default OFF**, **research-only**, and **non-integrated**.
No cross-family selection, runtime wiring, execution change, or behavioral promotion is allowed in V1.
If any later step needs those surfaces, the lane must stop and request new governance approval.

## 1. Problem Statement

Static single-policy behavior is brittle when observable market state changes materially over time.
A single RI posture can look coherent during one condition cluster and degrade badly when the state becomes transition-heavy, confidence-degraded, or structurally unstable.

This lane therefore asks a bounded question only:

> Can Genesis support an **RI family-local deterministic routing layer** that selects among a minimal set of RI policy profiles using only decision-time observable RI state?

This lane does **not** ask whether Genesis should route between strategy families.
Cross-family selection between `ri` and `legacy` is explicitly deferred because it is a separate meta-routing problem with separate semantics, boundaries, and governance risk.

## 2. Scope Statement

### In scope

- RI-only family-local architecture
- docs-first governance and architecture definition
- decision-time-only RI state definition
- deterministic RI router replay
- RI-local policy routing research artifacts
- trade-level evaluation of replay outcomes
- shadow/research outputs only

### Out of scope

- cross-family routing between `ri` and `legacy`
- `legacy` routing implementation
- runtime integration
- live execution changes
- backtest execution integration
- adaptive runtime behavior
- online learning
- model training/tuning
- parameter optimization
- any default-ON functionality

### V1 family boundary

- V1 is `RI-only`
- `Legacy` is explicitly **out of routing scope**
- `Legacy` may be referenced only as documentation baseline/comparator context, not inside router logic

### Default mode

- OFF by default
- zero behavior change to the existing baseline system

## 3. System Definition

SCPE RI V1 is defined as:

> **A deterministic RI family-local multi-policy routing system selecting among approved RI policy profiles based only on decision-time observable RI state.**

Conceptual flow:

`CoreDecisionState -> RIDecisionState -> RIRouterDecision -> RIPolicyDecision -> RIVetoDecision`

V1 must **not** introduce any `FamilyRouterDecision`.
No logic in this lane may choose between `RI` and `Legacy`.

## 4. Layer Definitions

### `CoreDecisionState`

Shared, decision-time-only state that is family-agnostic enough to describe the current decision context without embedding policy choice or outcome knowledge.
It describes market state only.

### `RIDecisionState`

An RI-local projection derived only from `CoreDecisionState` and RI-valid decision-time surfaces.
It may enrich RI-relevant interpretation but may not introduce future or post-entry information.

### `RIRouterDecision`

A deterministic family-local mandate decision selecting one RI policy profile, or explicit no-trade, using only allowlisted RI decision-time state.
It chooses mandate only.

### `RIPolicyDecision`

A policy-local proposed action/posture computed under the selected RI policy profile.
It proposes action only.

### `RIVetoDecision`

A downstream safety decision that may reduce, cap, veto, or force no-trade.
It may constrain exposure only.
It may **not** select a different policy or family.

## 5. Allowed / Forbidden Data Contract

## `CoreDecisionState` allowlist

Only the following families are admissible in V1, and only if they are provably available at decision time:

- decision key / timestamp / symbol / timeframe metadata
- volatility context already known at decision time, such as:
  - `current_atr_used`
  - `atr_period_used`
- higher-timeframe context descriptors already known at decision time, such as:
  - `htf_regime`
- bounded zone/context descriptors already known at decision time, such as:
  - `zone`

If a candidate field cannot be proven decision-time valid, it is excluded.

## `RIDecisionState` allowlist

Only the following RI-local field families are admissible in V1, and only if they are provably decision-time valid and stable:

- RI clarity:
  - `ri_clarity_score`
  - `ri_clarity_raw`
- regime-change recency:
  - `bars_since_regime_change`
- RI confidence / probability structure:
  - `proba_edge`
  - `conf_overall`
- transition-sensitive context that is either:
  - already present at decision time, or
  - deterministically derived from allowlisted decision-time fields only
- disagreement / mismatch signals only if they are:
  - decision-time valid
  - stable
  - non-leaking

Fields are admissible only when provenance is explicit and decision-time validity is demonstrable.
Unproven fields remain excluded by default.

## Explicit forbidden list

The following are forbidden as routing or state inputs in V1:

- post-entry information
- future-derived signals
- trade outcome fields
- outcome-linked features or proxies
- `total_pnl`
- `pnl_delta`
- `mfe_*`
- `mae_*`
- `fwd_*`
- `continuation_score`
- future cohort membership
- hidden cache-dependent behavior
- replay shortcuts that bypass as-of correctness
- runtime side-effect dependencies
- any field whose decision-time validity cannot be proven

## 6. RI Policy Set (minimal V1)

### `RI_continuation_policy`

**Role**

- continuation-oriented posture under sufficiently stable RI state

**Assumptions**

- clarity is adequate
- transition pressure is not dominant
- confidence structure is strong enough to justify continuation posture

**Allowed outputs**

- policy-local proposed action
- policy-local posture metadata
- rationale fields tied to RI-local decision-time state

**Must NOT do**

- perform routing internally
- reference `Legacy`
- consume post-entry or future-derived information
- invent fallback behavior when mandate is weak

### `RI_defensive_transition_policy`

**Role**

- cautious / degraded posture under transition-heavy or unstable RI state

**Assumptions**

- transition pressure, instability, or degraded clarity is present
- continuation posture is not well-supported by current RI state

**Allowed outputs**

- reduced or defensive proposed action/posture
- policy-local rationale fields tied to RI-local decision-time state

**Must NOT do**

- perform routing internally
- select another policy
- reference `Legacy`
- consume post-entry or future-derived information

### `RI_no_trade_policy`

**Role**

- first-class no-exposure policy when evidence is insufficient or mandate is not justified

**Assumptions**

- state evidence is too weak, too conflicting, or too transition-dominated for directional action

**Allowed outputs**

- explicit no-trade proposal
- rationale fields explaining insufficiency / degradation

**Must NOT do**

- masquerade as a routing failure bucket
- embed cross-family fallback
- consume post-entry or future-derived information

## 7. Router Contract

### Inputs

- `RIDecisionState` only
- optional bounded memory of previous selected RI policy and dwell duration
- no post-entry outcomes
- no `Legacy` state or policy surfaces

### Outputs

`RIRouterDecision` must include at minimum:

- `selected_policy`
- `previous_policy`
- `switch_reason`
- `mandate_level`
- `confidence`
- `no_trade_flag`
- `family_tag = RI`

### Mandate semantics

- mandate is discrete and explicit
- recommended V1 domain:
  - `mandate_level ∈ {0,1,2,3}`
- `0` corresponds to no meaningful mandate
- higher values correspond to stronger policy mandate, not performance guarantee

### Confidence semantics

- confidence is discrete and explicit
- recommended V1 domain:
  - `confidence ∈ {0,1,2,3}`
- confidence is a bounded routing confidence indicator, not a calibrated probability

### No-trade semantics

- no-trade is a first-class routing outcome
- no-trade is allowed when state evidence is insufficient, conflicting, or stability controls block a switch
- no-trade is not a hidden substitution for another policy or family

### Routing reason codes

V1 must use explicit, inspectable reason codes, for example:

- `stable_continuation_state`
- `transition_pressure_detected`
- `insufficient_evidence`
- `switch_blocked_by_hysteresis`
- `switch_blocked_by_min_dwell`
- `confidence_below_threshold`

The router must remain discrete and explicit:

- no fuzzy blends
- no weighted mixtures
- no hidden optimization
- no undocumented score composition

## 8. Routing Stability Controls

V1 must include explicit routing stability controls to prevent oscillatory regime theater.

Required controls:

- hysteresis
- minimum dwell time
- switch threshold
- optional cooldown only if explicitly documented and justified

Required logging:

- whether a switch was proposed
- why the current policy retained mandate
- why the previous policy lost mandate
- whether stability controls delayed or blocked the switch

## 9. Risk / Veto Contract

Risk/Veto may:

- reduce
- cap
- veto
- force no-trade

Risk/Veto may **NOT**:

- choose another policy
- switch to `Legacy`
- act as a hidden router
- invent a new route

Risk/Veto is downstream safety only.
If Risk/Veto becomes the true selector, the lane must treat that as a failure mode rather than as clever behavior.

## 10. Trace / Audit Requirements

Every replay decision row must log at minimum:

- timestamp / decision key
- family tag = `RI`
- `CoreDecisionState` summary
- `RIDecisionState` summary
- selected policy
- previous policy
- switch reason
- confidence
- mandate level
- veto outcome
- final routed action
- dwell duration

### Canonical trace rule

`routing_trace.ndjson` must be the canonical replay trace SSOT.
Other trace artifacts such as `state_trace.json`, `policy_trace.json`, and `veto_trace.json` may exist only as derived summaries.

## 11. Risks

At minimum, this lane must recognize the following risks:

- state instability
- routing oscillation
- policy overlap / regime theater
- hidden meta-strategy risk
- veto dominance risk
- false confidence from discovery-year behavior
- policy distinctness not being materially established
- observational replay being misread as integrated execution proof

## 12. Success Criteria

The lane is successful only if all of the following hold:

- RI state classification is stable enough to replay deterministically
- routing behavior is interpretable and audit-friendly
- the three RI-local policies are materially distinct in routed posture
- replay artifacts are reproducible and versionable
- trade-level observational outcomes differ meaningfully by routed policy or RI state
- no baseline behavior changes occur
- all outputs remain below runtime integration and promotion semantics

## 13. Stop Condition

This lane must stop after docs + research-only replay artifacts.
No runtime integration, no backtest execution wiring, no cross-family routing, and no promotion work are allowed without explicit governance approval.

Additional fail-closed stop conditions include:

- inability to prove decision-time validity for a routing field
- inability to keep `Legacy` out of router logic
- inability to keep risk/veto downstream-only
- policy overlap so strong that V1 policy identities are not materially distinct
- veto dominance so strong that router choice is rarely decisive
- any attempt to convert observational replay into causal execution-performance claims

## Non-goals explicitly deferred

The following are intentionally deferred:

- `FamilyRouterDecision`
- cross-family routing between `RI` and `Legacy`
- runtime integration
- backtest execution integration
- adaptive routing or online learning
- model training, tuning, or optimization
- any default-ON release surface
