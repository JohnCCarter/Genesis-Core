# RI policy router personality mapping

Date: 2026-04-28
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `docs-only / taxonomy crosswalk / no runtime behavior change`

This note maps the current `ri_policy_router` runtime surface to a possible future five-personality taxonomy.
It is a naming and interpretation crosswalk only.
It does **not** introduce new runtime policies, new timeframe authority, or new promotion claims.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Risk:** `MED` — why: docs-only semantic mapping in a high-sensitivity decision surface; no code behavior changes are allowed.
- **Required Path:** `Quick`
- **Lane:** `Concept` — why this is the cheapest admissible lane now: the repository already contains the active router behavior and current annual evidence, and the next cheap step is to make the existing behavioral taxonomy explicit before any new runtime leaf is proposed.
- **Objective:** map current router identities, switch reasons, and guards to a future five-personality naming model without changing runtime behavior.
- **Candidate:** `ri policy router personality taxonomy`
- **Base SHA:** `989308bf8a5ecabdfe684d2a16d92bfb0b77375a`

### Concept lane

- **Hypotes / idé:** the current router already contains enough structure to support a future five-personality taxonomy, but only part of that taxonomy is explicit today.
- **Varför det kan vara bättre:** a clearer taxonomy can reduce semantic drift, make evidence slices more readable, and separate label-only refactoring from genuinely new runtime behavior.
- **Vad skulle falsifiera idén:** if the current code paths cannot be cleanly mapped to the proposed labels without inventing behavior that does not exist today.
- **Billigaste tillåtna ytor:** `docs/analysis/**`, existing code/test surfaces, existing governance notes.
- **Nästa bounded evidence-steg:** if needed later, isolate whether a future `defensive_probe` personality is behaviorally distinct enough from current defensive routing to justify a new runtime leaf.

### Scope

- **Scope IN:** one docs-only mapping note grounded in current router code and tests.
- **Scope OUT:** `src/**`, `tests/**`, `config/**`, `results/**`, runtime tuning, timeframe selection authority, challenger promotion claims.
- **Expected changed files:** `1`
- **Max files touched:** `1`

### Gates required

- editor/file validation only for this docs-only slice

### Stop Conditions

- any need to reinterpret current runtime behavior beyond what code/tests already show
- any pressure to smuggle in a new policy as if it already exists
- any attempt to let the router choose timeframe inside this taxonomy slice

### Output required

- one repo-visible mapping note
- explicit distinction between already-explicit, already-implicit, and genuinely-new personalities

## Bottom-line map

The current router has **three runtime identities today**:

1. `RI_continuation_policy`
2. `RI_defensive_transition_policy`
3. `RI_no_trade_policy`

A future five-personality taxonomy can be layered on top of that, but it must distinguish between:

- what is already explicit today
- what is already present only as an implicit submode
- what would be a genuinely new runtime policy

## Current runtime identities vs future taxonomy

| Future taxonomy label    | Current runtime identity                                    | Current switch reason / substrate            | Runtime status today   | Evidence status                                                                |
| ------------------------ | ----------------------------------------------------------- | -------------------------------------------- | ---------------------- | ------------------------------------------------------------------------------ |
| `continuation_strong`    | `RI_continuation_policy`                                    | `stable_continuation_state`                  | implicit only          | explicit in code, directly asserted in tests                                   |
| `continuation_qualified` | `RI_continuation_policy`                                    | `continuation_state_supported`               | implicit only          | explicit in code, directly asserted in tests                                   |
| `defensive_transition`   | `RI_defensive_transition_policy`                            | `transition_pressure_detected`               | explicit today         | explicit in code, directly asserted in tests                                   |
| `defensive_probe`        | nearest current substrate: `RI_defensive_transition_policy` | `defensive_transition_state`                 | **not** explicit today | code branch exists, but no separate runtime identity or dedicated evidence yet |
| `no_trade`               | `RI_no_trade_policy`                                        | `insufficient_evidence` plus no-trade guards | explicit today         | explicit in code, directly asserted in tests                                   |

## What the router already chooses today

### 1. Continuation

Current runtime constant:

- `POLICY_CONTINUATION = "RI_continuation_policy"`

This is already split internally into two meaningful strengths.

#### A. Strong continuation

Current code signature:

- `raw_target_policy = RI_continuation_policy`
- `raw_switch_reason = stable_continuation_state`
- `mandate_level = 3`
- `confidence_level = 3`

Current interpretation:

- continuation is clearly supported
- the router stays constructive
- size multiplier remains `1.0`

Future label fit:

- `continuation_strong`

Current evidence anchors:

- `src/core/strategy/ri_policy_router.py` — `_raw_router_decision(...)`
- `tests/utils/test_ri_policy_router.py::test_policy_router_preserves_aged_strong_continuation`
- `tests/utils/test_decision_scenario_behavior.py` assertions on `stable_continuation_state`

#### B. Qualified continuation

Current code signature:

- `raw_target_policy = RI_continuation_policy`
- `raw_switch_reason = continuation_state_supported`
- `mandate_level = 2`
- `confidence_level = 2`

Current interpretation:

- continuation is acceptable, but not maximally strong
- this is weaker than `stable_continuation_state`
- it still remains inside the continuation family, not defensive

Future label fit:

- `continuation_qualified`

Current evidence anchors:

- `src/core/strategy/ri_policy_router.py` — `_raw_router_decision(...)`
- `tests/utils/test_ri_policy_router.py::test_policy_router_keeps_fresh_weak_continuation_allowed`
- `tests/utils/test_decision_scenario_behavior.py` assertions on `continuation_state_supported`

### 2. Defensive

Current runtime constant:

- `POLICY_DEFENSIVE = "RI_defensive_transition_policy"`

The current router has one explicit defensive runtime identity, but two different defensive strengths in raw routing logic.

#### A. Explicit current defensive transition

Current code signature:

- `raw_target_policy = RI_defensive_transition_policy`
- `raw_switch_reason = transition_pressure_detected`
- `mandate_level = 2`
- `confidence_level = 2`
- size multiplier defaults to `defensive_size_multiplier = 0.5`

Current interpretation:

- the router still allows participation
- but it cuts size and treats the state as fragile / transitional

Future label fit:

- `defensive_transition`

Current evidence anchors:

- `src/core/strategy/ri_policy_router.py`
- `tests/utils/test_ri_policy_router.py::test_policy_router_selects_defensive_policy_in_fresh_transition_pocket`
- `tests/utils/test_decision_scenario_behavior.py::test_decide_enabled_policy_router_selects_defensive_and_reduces_size`

#### B. Weak defensive substrate (nearest candidate for future probe)

Current code signature:

- `raw_target_policy = RI_defensive_transition_policy`
- `raw_switch_reason = defensive_transition_state`
- `mandate_level = 1`
- `confidence_level = 1`

Current interpretation:

- the code already has a weaker defensive branch below `transition_pressure_detected`
- however, it is **not** exposed as a distinct runtime policy today
- it still collapses into the same explicit defensive identity

Future label fit:

- nearest candidate for `defensive_probe`

Important boundary:

- `defensive_probe` does **not** exist yet as a first-class runtime identity
- this branch only shows that there is already a natural substrate for such a future split

Current evidence status:

- explicit code branch exists in `src/core/strategy/ri_policy_router.py`
- no dedicated test currently asserts `defensive_transition_state` as its own behavioral class
- no annual or bounded evidence note currently isolates this branch as a validated separate policy

So:

- `defensive_probe` should be treated as **proposed only**, not already present

### 3. No-trade

Current runtime constant:

- `POLICY_NO_TRADE = "RI_no_trade_policy"`

This is already explicit today.

Current code signatures include:

- `insufficient_evidence`
- aged-weak continuation guard paths
- blocked release paths that keep the router in no-trade

Future label fit:

- `no_trade`

Current evidence anchors:

- `tests/utils/test_ri_policy_router.py::test_policy_router_forces_no_trade_when_evidence_floor_fails`
- `tests/utils/test_ri_policy_router.py::test_policy_router_blocks_aged_weak_continuation`
- `tests/utils/test_decision_scenario_behavior.py::test_decide_enabled_policy_router_can_force_no_trade_before_sizing`

## Guards and exceptions are not separate personalities

Several important router mechanisms exist today, but they should **not** be mistaken for standalone personalities.

### `AGED_WEAK_CONTINUATION_GUARD`

Meaning today:

- blocks late weak continuation
- routes to no-trade when continuation has aged without becoming strong enough

Taxonomy role:

- guard inside the continuation/no-trade boundary
- **not** its own personality

### `WEAK_PRE_AGED_CONTINUATION_RELEASE_GUARD`

Meaning today:

- blocks an early release from prior no-trade into weak continuation
- acts as a one-step hold/release constraint

Taxonomy role:

- release blocker within the transition from no-trade back into continuation
- **not** its own personality

### `bars7_continuation_persistence_reconsideration_applied`

Meaning today:

- exact bounded continuation-preservation exception on the approved bars-7 seam
- keeps an exact continuation row alive under tightly bounded conditions

Taxonomy role:

- continuation exception / persistence helper
- **not** its own top-level personality

## Recommended future naming split

If the taxonomy is later made explicit without broadening runtime behavior, the cleanest first split would be:

### Already-real semantics that could become explicit labels later

- `continuation_strong`
- `continuation_qualified`
- `defensive_transition`
- `no_trade`

This would mostly be a **labeling clarification** of existing behavior.

### Genuinely new candidate that would require separate evidence

- `defensive_probe`

This one should not be smuggled in as if it were already present.

It would need its own bounded case for:

- when it is selected instead of `defensive_transition`
- whether its size / persistence / release behavior is distinct
- why it is better than simply staying with current defensive routing or no-trade

## What this mapping does **not** justify

This mapping note does **not** justify:

- letting the policy choose timeframe
- treating the current router as already having five first-class runtime policies
- claiming `defensive_probe` is already implemented
- claiming broader annual readiness from the current mixed enabled-vs-absent annual evidence

## Recommended next admissible move

If we continue this line without changing runtime behavior yet, the next clean step would be:

1. keep the current explicit runtime trio:
   - `RI_continuation_policy`
   - `RI_defensive_transition_policy`
   - `RI_no_trade_policy`
2. use this note as the semantic crosswalk for future discussion
3. if a later docs-only slice is desired, split continuation into:
   - `continuation_strong`
   - `continuation_qualified`
     at the taxonomy level first
4. treat `defensive_probe` as a separate future candidate that needs its own bounded evidence slice before any runtime promotion

## Bottom line

Today the router already supports a clean **three-policy runtime base** with internal substructure:

- explicit continuation
- explicit defensive transition
- explicit no-trade

The proposed five-personality model is a good future taxonomy, but only part of it is already real today:

- `continuation_strong` and `continuation_qualified` are already there **implicitly**
- `defensive_transition` and `no_trade` are already there **explicitly**
- `defensive_probe` would be the only **genuinely new** personality
