# RI policy router defensive-probe concept pre-code packet

Date: 2026-04-29
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `pre-code-defined / concept-only / no implementation or execution authority`

This packet defines one bounded future candidate question for the RI policy router:
whether the existing raw `defensive_transition_state` substrate should ever be treated as a
distinct conceptual `defensive_probe` personality rather than remaining collapsed inside
`RI_defensive_transition_policy`.

It does **not** authorize runtime changes, execution, config/schema widening, new evidence runs,
family-rule changes, readiness claims, or promotion claims.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/next-slice-2026-04-29`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice is docs-only and freezes one candidate-definition question
  without opening runtime, config, tests, or authority surfaces.
- **Required Path:** `Quick`
- **Lane:** `Concept` — why this is the cheapest admissible lane now: the findings-bank
  hardening slice is closed green, the RI-router runtime chain remains parked, and the next
  honest move is to decide whether `defensive_probe` is even a coherent future candidate before
  any new evidence or runtime packet is proposed.
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** define one bounded concept-only candidate question for a future
  `defensive_probe` personality while keeping the current three-policy runtime base and all
  authority boundaries unchanged.
- **Candidate:** `defensive_probe personality concept`
- **Base SHA:** `e9500e1d`

### Constraints

- `docs-only`
- `concept-only / non-authorizing`
- `No runtime-default / config / family / promotion widening`
- `No new evidence execution`
- `Future evidence or code slice requires separate approval`

### Skill Usage

- **Applied repo-local skill:** none in this packet
- **Reason:** this artifact is docs-only and does not execute an implementation or replay
  workflow.
- **Reserved for any later code slice:** `python_engineering`, `decision_gate_debug`
- **Deferred to any later runnable evidence step:** `backtest_run`, `genesis_backtest_verify`
- **Not claimed:** no skill coverage is claimed as completed by this packet.

## Why this packet exists now

The current evidence posture already establishes the limits of the active RI-router lane:

1. the runtime chain is parked and there is no active admissible RI-router runtime packet today
2. the active router already has a three-policy runtime base and the personality mapping note says
   `defensive_probe` would be the only genuinely new personality rather than a simple relabeling
3. curated annual evidence remains mixed, and the clearly negative full years are dominated by a
   broader late suppression + later continuation-displacement structure rather than by a clean
   early defensive pocket
4. therefore the next honest move is not more years, more windows, or fresh runtime tuning, but a
   bounded concept check on whether `defensive_probe` is even a coherent future candidate

## Evidence anchors

- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_personality_mapping_2026-04-28.md`
- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_aged_weak_active_carrier_truth_parked_handoff_2026-04-27.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_enabled_vs_absent_curated_annual_evidence_2026-04-28.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_negative_year_pocket_isolation_2026-04-28.md`
- `docs/scpe_ri_v1_architecture.md`
- `src/core/strategy/ri_policy_router.py`
- `scripts/analyze/scpe_ri_v1_router_replay.py`
- `GENESIS_WORKING_CONTRACT.md`

## Exact candidate boundary

### Current explicit runtime fact

Current repo-visible logic already contains a weak defensive substrate:

- `raw_target_policy = RI_defensive_transition_policy`
- `raw_switch_reason = defensive_transition_state`
- `mandate_level = 1`
- `confidence_level = 1`

This substrate is already present in both the runtime router and the historical replay logic.
It is **not** a separate runtime identity today.

### Proposed conceptual candidate only

In this packet, `defensive_probe` means only a **future candidate interpretation** of that weak
defensive substrate.

If it ever becomes worth pursuing later, it would mean:

- a distinct conceptual personality below the current explicit `defensive_transition` identity
- still inside the RI-local router family
- still below continuation, readiness, and promotion authority
- still requiring separate evidence before any runtime leaf or behavior change is even discussed

### What this packet explicitly forbids

This packet must not be read as authority for any of the following:

- claiming `defensive_probe` is already implemented
- treating `defensive_transition_state 1/1 -> 2/2` as already justified
- assuming the negative annual years are mainly a `defensive_probe` story
- reopening aged-weak, bars-8, or generic RI-router runtime tuning from implication alone
- letting the router choose timeframe or broader family semantics

## Exact question to preserve

This packet freezes the following question only:

> Does current repo-visible evidence justify treating `defensive_transition_state` as a separate
> future `defensive_probe` candidate, or is it still better understood as a weak subcase of the
> existing `RI_defensive_transition_policy`?

This packet does **not** assume the answer is yes.
It only records that this is now the next bounded concept question worth preserving.

## What would count as a useful next answer

A useful later answer must distinguish among at least these possibilities:

1. no distinct candidate exists and `defensive_transition_state` should remain only a weak
   subcase of `RI_defensive_transition_policy`
2. a distinct concept exists, but only on one exact bounded carrier or row-set and therefore still
   does not justify runtime work
3. a distinct concept looks plausible enough to deserve one later read-only evidence slice, but
   still not a runtime/default/config packet

If a later slice cannot distinguish among those possibilities, it should stop rather than widen
into implementation language.

## Preferred next bounded follow-up if this line is reopened

If the user explicitly wants to continue this line after this packet, the cleanest next step is:

- one read-only evidence slice that isolates **one exact `defensive_transition_state` carrier or
  row-set** and compares that substrate against the current `transition_pressure_detected` and
  `RI_no_trade_policy` interpretations

What is **not** admissible from this packet alone:

- a new runtime packet
- a new config leaf
- a new evidence sweep across more years or windows
- broad annual reinterpretation

## Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_defensive_probe_concept_precode_packet_2026-04-29.md`
  - `GENESIS_WORKING_CONTRACT.md`
  - explicit anchoring to current parked-state and annual-evidence notes
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `results/**`
  - `artifacts/**`
  - new evidence execution
  - new runtime packets
  - family-rule, readiness, promotion, or champion surfaces
- **Expected changed files:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_defensive_probe_concept_precode_packet_2026-04-29.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Max files touched:** `2`

## Mode proof

- **Why this mode applies:** branch mapping from `feature/*` resolves to `RESEARCH` per
  `docs/governance_mode.md`.
- **What RESEARCH allows here:** one small docs-only concept packet that preserves a future
  candidate question without opening runtime/default authority.
- **What remains forbidden here:** runtime integration, runnable evidence, family-rule changes,
  readiness/promotion framing, champion/default changes, and broad annual/window widening.
- **What would force STRICT escalation:** touching `config/strategy/champions/`,
  `.github/workflows/champion-freeze-guard.yml`, runtime-default authority surfaces,
  family-rule surfaces, or promotion/readiness surfaces.

## Gates required for this packet

Choose the minimum docs-only gates appropriate to the current scope:

1. `pre-commit run --files GENESIS_WORKING_CONTRACT.md docs/decisions/regime_intelligence/policy_router/ri_policy_router_defensive_probe_concept_precode_packet_2026-04-29.md`
2. basic file diagnostics for both markdown files

No runtime-classified gates are required for this packet itself because it is docs-only and opens
no executable surface by itself.

## Stop Conditions

- the packet starts implying `defensive_probe` already exists as a runtime policy
- the packet starts treating mixed annual evidence as if it were already a `defensive_probe`
  mechanism proof
- the packet widens into new carrier, config, or implementation language
- the next follow-up can no longer stay local to one exact `defensive_transition_state` surface
- any need to modify files outside the two scoped docs files

## Output required

- one concept-only pre-code packet for the `defensive_probe` candidate question
- one updated working anchor

## Bottom line

The RI-router chain is currently parked, and the annual evidence remains mixed. The clean next
move is therefore not more tuning or more broad evidence, but one bounded concept packet that
decides whether `defensive_probe` is even a coherent future candidate. This packet preserves that
question only; it does not authorize any runtime or evidence follow-up by itself.
