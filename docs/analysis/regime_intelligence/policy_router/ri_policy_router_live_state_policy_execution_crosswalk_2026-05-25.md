# RI policy router live state-policy-execution crosswalk

Date: 2026-05-25
Branch: `feature/research-next-bounded-case-2026-05-25`
Mode: `RESEARCH`
Status: `completed / docs-only live crosswalk / no runtime behavior change`

This note does **not** propose a new runtime policy.
It anchors the current live `ri_policy_router` implementation to the cleaner Genesis-Core separation:

- **state / regime** = what the world is doing
- **policy** = how the RI family chooses to behave under that state
- **execution** = how the selected behavior is constrained or expressed

The purpose is to reduce semantic drift before any new bounded policy slice is proposed.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: live branch `feature/research-next-bounded-case-2026-05-25`
- **Risk:** `LOW` — docs-only semantic crosswalk on an existing live implementation
- **Required Path:** `Quick`
- **Lane:** `Concept`
- **Objective:** map the current live RI router and adjacent decision surfaces to a state -> policy -> execution reading without implying new runtime authority
- **Candidate:** `live state policy execution crosswalk`
- **Base SHA:** `270b65346ebe9208c953abfc7181bf83df34d8f5`

## Scope

### Scope IN

- one docs-only live implementation crosswalk
- current code surfaces only
- current research findings only
- clarification of state vs policy vs execution semantics

### Scope OUT

- `src/**`
- `tests/**`
- runtime routing changes
- new policy identities
- threshold retuning
- promotion/readiness claims

## Evidence inputs

- `docs/scpe_ri_v1_architecture.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_personality_mapping_2026-04-28.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_12_vs_2024_fixed_window_phase_contrast_2026-05-25.md`
- `src/core/strategy/decision_gates.py`
- `src/core/strategy/ri_policy_router.py`
- `src/core/strategy/decision_sizing.py`
- `src/core/intelligence/regime/clarity.py`
- `tests/utils/test_ri_policy_router.py`

## Main result

The repository already contains the intended architectural separation in conceptual form:

`CoreDecisionState -> RIDecisionState -> RIRouterDecision -> RIPolicyDecision -> RIVetoDecision`

The live code is directionally consistent with that model, but it compresses parts of **state interpretation** and **policy selection** together inside the RI router and nearby gate code.

So the clean reading of the current implementation is:

1. **state/context classification** is already present,
2. **policy selection** is already explicit at the RI-family level,
3. **execution constraints** are already present downstream,
4. but the state layer is still only partly explicit.

## Current live layer map

| Layer                   | Current live role                                                   | Main live surfaces                                         | Notes                                                                                                                  |
| ----------------------- | ------------------------------------------------------------------- | ---------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `state / regime`        | describe the observed decision-time world                           | `decision_gates.py`, `clarity.py`, `decision_sizing.py`    | includes `regime`, `zone`, `bars_since_regime_change`, `confidence_gate`, `action_edge`, volatility/risk-state context |
| `policy selection`      | choose RI-family behavior                                           | `ri_policy_router.py`                                      | explicit output is one of `RI_continuation_policy`, `RI_defensive_transition_policy`, `RI_no_trade_policy`             |
| `execution constraints` | constrain exposure or block switching after/around policy selection | `ri_policy_router.py`, `decision.py`, `decision_sizing.py` | includes hysteresis, min dwell, switch threshold, no-trade, size multiplier, risk-state sizing                         |

## Observed

### 1. The live router already uses policy as behavior, not as a market label

The current router output is already policy-shaped:

- `RI_continuation_policy`
- `RI_defensive_transition_policy`
- `RI_no_trade_policy`

These are **behavioral responses**, not descriptions of the market.

So labels like `bull`, `bear`, `high volatility`, or `transition pressure` should not be read as policies in the current Genesis-Core framing.

### 2. State/context inputs already exist, but are spread across multiple surfaces

The live code already consumes several decision-time state descriptors, for example:

- `regime`
- `htf_regime`
- `zone`
- `bars_since_regime_change`
- `confidence_gate`
- `action_edge`
- `clarity_score`
- drawdown / risk-state context
- event/risk blocks

This means the raw material for a cleaner `RIDecisionState` interpretation already exists.
It is simply not gathered into one explicit live object yet.

### 3. The router currently mixes state interpretation with policy choice

Inside `_raw_router_decision(...)`, the live router computes:

- `continuation_points`
- `transition_points`

and then immediately converts those into policy outcomes such as:

- `stable_continuation_state` -> `RI_continuation_policy`
- `continuation_state_supported` -> `RI_continuation_policy`
- `transition_pressure_detected` -> `RI_defensive_transition_policy`
- `defensive_transition_state` -> `RI_defensive_transition_policy`
- `insufficient_evidence` -> `RI_no_trade_policy`

That is already deterministic and valid, but it means the code still compresses:

- **what state are we in?**
- and
- **what behavior should we choose under that state?**

into one live step.

### 4. The current live code is already transition-aware

The router is not driven only by static labels.
It already reacts to transition-like conditions, especially through:

- `bars_since_regime_change`
- `zone`
- `transition_points`
- aged/weak continuation guards
- release blocking and dwell controls

So the repo is already closer to a **transition-aware policy system** than to a naive one-label regime filter.

### 5. Execution is already downstream and partially separated

After candidate selection and router selection, the live code applies additional constraints such as:

- hysteresis
- minimum dwell
- switch threshold
- no-trade blocking
- defensive size multiplier
- volatility sizing
- regime/HTF regime multipliers
- RI risk-state sizing

This is already recognizably an execution/risk layer rather than a policy-definition layer.

## Current live translation of proposed state labels

The following labels are best read as **observed state classes**, not as policies.

| Proposed state label | Best current live meaning                                               | Current live policy response                                  |
| -------------------- | ----------------------------------------------------------------------- | ------------------------------------------------------------- |
| `clean_continuation` | strong / phase-clean continuation support                               | usually `RI_continuation_policy`                              |
| `aging_continuation` | aged continuation that has not strengthened enough                      | often `RI_no_trade_policy` via `AGED_WEAK_CONTINUATION_GUARD` |
| `blocked_mixed`      | blocked-dominant pocket with mixed reasons and interrupted continuation | typically `RI_no_trade_policy` or blocked release behavior    |
| `transition_chop`    | unstable transition-heavy state with degraded clarity/support           | usually `RI_defensive_transition_policy`                      |

This is the key separation:

- the left-hand column describes the world,
- the right-hand column describes the agent response.

## Relationship to the current `2023-12` vs `2024` finding

The current bounded research line already supports this reading.

`2023-12` was useful because it behaved more like a **phase-pure continuation state**.
Late `2024` was useful because it behaved more like a **blocked-dominant mixed state**.

That finding is better read as:

- two different **observed local states**
- provoking different or differently justified **policy responses**

rather than as proof that one state label is itself a policy.

## Inferred

The next honest move is not to invent many new policies from market labels.
It is to make the **state interpretation layer** more explicit while keeping the current policy trio stable:

- `RI_continuation_policy`
- `RI_defensive_transition_policy`
- `RI_no_trade_policy`

A cleaner future shape would therefore be:

1. explicit RI-local observed state,
2. deterministic policy selection over the existing trio,
3. downstream execution constraints.

That is cheaper and cleaner than widening the policy set before the state taxonomy is explicit.

## Unverified

This note does **not** prove:

- that the current live router should gain new first-class policy identities now
- that a future explicit `RIDecisionState` object improves outcomes by itself
- that `transition_chop` deserves its own policy rather than a better-defined state-to-defensive mapping
- that runtime refactoring is yet justified

## Consequence

The next bounded research slice should likely be:

1. keep the current explicit policy trio unchanged,
2. treat labels like `clean_continuation`, `aging_continuation`, `blocked_mixed`, and `transition_chop` as **state taxonomy candidates**, and
3. test whether those state classes can be described deterministically on the already-fixed `2023-12` and late-`2024` subjects before any runtime routing change is proposed.

That would move the work forward without confusing:

- state classification,
- policy selection,
- and execution controls.

## What changed and what did not

What changed:

- the repo now has one live implementation crosswalk tying current code to the cleaner Genesis-Core state -> policy -> execution reading
- the current policy discussion is now anchored to the existing architecture contract instead of informal label drift

What did **not** change:

- no runtime behavior changed
- no new policy was introduced
- no thresholds, guards, sizing, or routing semantics changed
- no readiness or promotion claim was made
