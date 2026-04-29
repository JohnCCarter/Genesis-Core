# Regime Intelligence challenger family — DECISION clarity/risk-state direction packet

Date: 2026-03-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `direction-selected / planning-only / no authorization`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet selects exactly one next RI research direction after closing the first Decision EV/edge slice as plateau, but must remain planning-only and must not create admissibility, launch, runtime-validity, comparison, readiness, promotion, or writeback semantics.
- **Required Path:** `Quick`
- **Objective:** Select exactly one next admissible RI research direction after closing `Decision EV/edge slice1` as non-improving.
- **Candidate:** `future RI DECISION clarity/risk-state sizing research lane`
- **Base SHA:** `d227be7e6d07c4b389529ee6a0ece228ca9a9b10`

### Scope

- **Scope IN:** one docs-only direction decision selecting exactly one next direction and clearly parking the alternatives.
- **Scope OUT:** no source-code changes, no config YAML creation, no validator/preflight/smoke/launch work, no changes under `src/core/**`, no changes to `family_registry.py`, no changes to `family_admission.py`, no slice2, no comparison/readiness/promotion/writeback.
- **Expected changed files:** `docs/governance/regime_intelligence_optuna_decision_clarity_risk_state_direction_packet_2026-03-27.md`
- **Max files touched:** `1`

### Stop Conditions

- any wording that implies the next lane is launch-authorized or launch-admissible now
- any wording that implies runtime-valid RI conformity
- any wording that selects more than one next direction
- any wording that reopens `OBJECTIVE` inside this packet
- any wording that treats parked alternatives as permanently rejected

## Purpose

This packet answers one narrow question only:

- what is the next chosen RI research direction after closing `DECISION EV/edge slice1` as plateau?

This packet is **planning-only governance**.

It does **not**:

- authorize a runnable next lane
- authorize config creation
- authorize validator/preflight/smoke/launch
- grant runtime-valid RI conformity
- reopen comparison, readiness, promotion, or writeback

## Governing basis

This packet is downstream of the following tracked artifacts:

- `docs/governance/regime_intelligence_optuna_decision_roadmap_2026-03-27.md`
- `docs/governance/regime_intelligence_optuna_decision_ev_edge_slice1_precode_command_packet_2026-03-27.md`
- `docs/governance/regime_intelligence_optuna_decision_ev_edge_slice1_execution_outcome_signoff_summary_2026-03-27.md`
- `docs/governance/regime_intelligence_optuna_signal_regime_definition_direction_packet_2026-03-27.md`
- `src/core/strategy/decision_sizing.py`

Carried-forward meaning:

1. the broader `DECISION` class was previously chosen over reopening `OBJECTIVE`
2. the first tested `DECISION` surface — `EV / edge` — is now closed as `PLATEAU`
3. that closure applies to the tested surface, not to the entire `DECISION` class
4. the next step is therefore to choose the next **specific** direction within the still-open `DECISION` class
5. any future runnable lane still requires separate pre-code governance, exact fixed backdrop, exact search surface, and explicit research-only boundaries

## Candidate directions under decision

### Option 1 — DECISION / clarity-risk-state sizing surface

Meaning:

- keep the next lane inside the `DECISION` class
- move from pure EV/edge gating to already implemented sizing and guard surfaces that modulate decision expression
- keep signal/regime-definition, objective/scoring, and exit/management surfaces fixed

Current suitability:

- **CHOSEN NOW**

Rationale:

- the EV/edge lane produced real train-side differentiation but validated back to the incumbent plateau signature
- the next smallest remaining `DECISION` hypothesis should therefore stay inside already implemented decision-layer config rather than reopening broader classes
- the relevant surface is already consumed in `src/core/strategy/decision_sizing.py`, which makes this direction narrower and cleaner than reopening `OBJECTIVE`

Relevant rationale surfaces in the current codebase:

- `multi_timeframe.regime_intelligence.clarity_score.*`
- `multi_timeframe.regime_intelligence.risk_state.*`
- other already implemented sizing/guard controls consumed in `src/core/strategy/decision_sizing.py`

Important boundary:

- these surfaces are cited here as **research rationale only**
- this packet does **not** declare them already authorized as a runnable tuple set
- any later runnable lane must still define exact fixed versus tunable fields in a separate packet

### Option 2 — OBJECTIVE

Meaning:

- move the next lane to scoring or optimization-target semantics

Current suitability:

- **NOT CHOSEN NOW**

Reason:

- it remains a valid future hypothesis class, but it is broader than the remaining already implemented decision-sizing surface
- it should remain deferred while a narrower `DECISION` path still exists

### Option 3 — SIGNAL / feature-surface

Meaning:

- leave the `DECISION` class and reopen the broader `SIGNAL` class through feature/input availability rather than decision-layer sizing

Current suitability:

- **NOT CHOSEN NOW**

Reason:

- it remains a valid future alternative, but it is not the next chosen lane while an already implemented `DECISION` sizing surface remains available
- it is parked, not rejected

## Decision

### Chosen next direction

- `CHOSEN — DECISION / clarity-risk-state sizing surface`

### Parked alternatives

- `NOT CHOSEN NOW — OBJECTIVE`
- `NOT CHOSEN NOW — SIGNAL / feature-surface`

## Why this direction is chosen

The direction is chosen because the first `DECISION` attempt showed that changing `ev.R_default × thresholds.min_edge` was not enough to beat the carried-forward plateau on validation.

Observed meaning carried forward from the closed slice:

- `thresholds.min_edge` created real train-side geometry
- validated `thresholds.min_edge = 0.01` tuples reproduced the exact plateau signature
- no validated tuple exceeded `0.26974911658712664`

This suggests that the next admissible `DECISION` attempt should not be a wider EV/edge retry and should not jump immediately to `OBJECTIVE`.

Instead, the next best `DECISION` hypothesis is to move to the already implemented clarity/risk-state sizing surface that shapes how decisions are expressed, while still holding signal, objective, and exit classes fixed.

## Fixed surfaces in this direction choice

The following surfaces remain fixed in this direction choice:

- objective/scoring class
- signal/regime-definition class
- EV/edge slice1 closeout remains closed
- exit/management surface
- family-registry rules
- family-admission rules
- comparison closed
- readiness closed
- promotion closed
- champion/default writeback closed

## Expected improvement signature

A future clarity/risk-state sizing lane would count as an improvement only if at least one validated artifact:

1. has validation score strictly greater than `0.26974911658712664`, and
2. does **not** reproduce the closed plateau tuple below:
   - validation score: `0.26974911658712664`
   - profit factor: `1.8845797002042906`
   - max drawdown: `0.027808774550017137`
   - trades: `63`
   - sharpe: `0.20047738907046656`

## Falsification condition

A future clarity/risk-state sizing lane would be falsified if either:

1. no validated artifact exceeds validation score `0.26974911658712664`, or
2. the best validated artifact reproduces the exact plateau tuple above

## Explicit blocker

This direction packet does **not** make the next lane admissible or launchable.

A separate later packet is still required to resolve:

- what exact clarity/risk-state sizing fields are fixed versus tunable
- what exact frozen backdrop is inherited from the closed EV/edge lane
- what exact future tuple set remains inside `DECISION` rather than drifting into `OBJECTIVE` or `SIGNAL`
- what exact research-only artifacts and later gates would be required before any runnable lane exists

Until that later packet exists, the following remain closed:

- runnable YAML creation
- validator/preflight/smoke/launch for the new lane
- slice2
- comparison/readiness/promotion/writeback

## Bottom line

The next chosen RI direction is now:

- **DECISION on clarity/risk-state sizing surface**

This keeps the work inside the already-open `DECISION` class, parks `OBJECTIVE` and `SIGNAL / feature-surface` for later review, and preserves all launch/admissibility/runtime boundaries for future separate governance.
