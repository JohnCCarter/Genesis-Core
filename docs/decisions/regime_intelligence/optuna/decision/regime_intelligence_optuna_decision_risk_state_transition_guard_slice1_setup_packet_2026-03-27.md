# Regime Intelligence challenger family — DECISION risk-state transition-guard slice1 setup packet

Date: 2026-03-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `setup-defined / docs-only / no YAML creation or launch authority`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet reserves the exact future YAML subject paths and later evidence obligations for the already chosen `transition_guard` seam, but must remain docs-only, narrower than YAML authoring, and narrower than launch authorization.
- **Required Path:** `Full gated docs-only`
- **Objective:** Define the exact future canonical subject path, exact future bounded smoke subject path, exact frozen backdrop carry-forward, and exact later validator/preflight/smoke evidence obligations for `multi_timeframe.regime_intelligence.risk_state.transition_guard.{guard_bars,mult}`.
- **Candidate:** `future tBTCUSD 3h RI DECISION transition-guard slice1 setup boundary`
- **Base SHA:** `d227be7e6d07c4b389529ee6a0ece228ca9a9b10`

### Scope

- **Scope IN:** one docs-only setup packet; exact chain placement; exact seam carry-forward; exact tuple-grid carry-forward; exact freeze carry-forward; exactly one reserved future canonical YAML subject path; exactly one reserved future bounded smoke YAML subject path; exact later evidence requirements for validator/preflight/smoke.
- **Scope OUT:** no source-code changes, no test changes, no changes under `src/core/**`, no changes under `tests/**`, no changes under `config/optimizer/**`, no changes under `tmp/**`, no changes under `results/**`, no YAML creation, no YAML snippets, no validator/preflight/smoke execution, no gate-pass claims, no launch authorization, no runtime-valid RI conformity, no comparison/readiness/promotion/writeback.
- **Expected changed files:** `docs/decisions/regime_intelligence/optuna/decision/regime_intelligence_optuna_decision_risk_state_transition_guard_slice1_setup_packet_2026-03-27.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/path sanity only
- manual wording audit that the packet remains docs-only setup definition and does not imply YAML authoring or launch authority

For interpretation discipline inside this packet:

- the seam must remain strictly limited to `multi_timeframe.regime_intelligence.risk_state.transition_guard.{guard_bars,mult}`
- the tuple grid must remain exactly `{1,2,3} × {0.55,0.65,0.75}`
- the freeze carry-forward must remain unchanged from the predecessor admissibility packet
- exactly one future canonical subject path and exactly one future bounded smoke subject path may be named
- no sentence may imply that YAML files already exist or are authorized to be created now
- no sentence may imply that validator, preflight, or smoke has already passed
- no sentence may imply research launch, runtime-validity, comparison, readiness, promotion, or writeback authority

### Stop Conditions

- any wording that does more than reserve future subject paths and define later evidence obligations
- any wording that opens more than one seam
- any wording that changes the exact tuple grid
- any wording that changes, shortens, or reinterprets the freeze carry-forward
- any wording that reopens `risk_state.drawdown_guard.*`, `clarity_score.*`, `size_multiplier.{min,max}`, `OBJECTIVE`, or `SIGNAL / feature-surface`
- any wording that contains YAML content or YAML field payloads rather than future path reservation only
- any wording that claims or implies a passed gate, created YAML, or launch readiness

### Output required

- one reviewable docs-only setup packet
- exact future canonical subject path
- exact future bounded smoke subject path
- exact freeze carry-forward statement
- exact later evidence requirements for validator/preflight/smoke
- exact non-authorizations for this step

## Why this step exists

This packet sits after:

1. the class-level direction packet
2. the pre-code seam-definition packet
3. the launch-admissibility gate packet

Its role is narrower than YAML authoring and much narrower than launch authorization.

It exists only to freeze the future YAML surface for this seam before any later authoring or evidence-collection step is even reviewed.

## Governing basis

This packet is downstream of the following tracked artifacts:

- `docs/decisions/regime_intelligence/optuna/decision/regime_intelligence_optuna_decision_clarity_risk_state_direction_packet_2026-03-27.md`
- `docs/decisions/regime_intelligence/optuna/decision/regime_intelligence_optuna_decision_risk_state_transition_guard_slice1_precode_command_packet_2026-03-27.md`
- `docs/decisions/regime_intelligence/optuna/decision/regime_intelligence_optuna_decision_risk_state_transition_guard_slice1_launch_admissibility_packet_2026-03-27.md`

Carried-forward meaning:

1. the active class-level path remains `DECISION / clarity-risk-state sizing surface`
2. the first proposed minimal seam remains exactly `multi_timeframe.regime_intelligence.risk_state.transition_guard.{guard_bars,mult}`
3. the only admissible grid remains exactly nine tuples
4. the freeze carry-forward remains in force unchanged
5. this packet may reserve future subject paths and later evidence requirements only; it may not create, authorize, or claim any YAML, gate pass, or launch

## Exact seam and exact tuple grid carried forward

The only seam covered by this packet is:

- `multi_timeframe.regime_intelligence.risk_state.transition_guard.guard_bars`
- `multi_timeframe.regime_intelligence.risk_state.transition_guard.mult`

The only admissible future tuple grid remains exactly:

- `(guard_bars=1, mult=0.55)`
- `(guard_bars=1, mult=0.65)`
- `(guard_bars=1, mult=0.75)`
- `(guard_bars=2, mult=0.55)`
- `(guard_bars=2, mult=0.65)`
- `(guard_bars=2, mult=0.75)`
- `(guard_bars=3, mult=0.55)`
- `(guard_bars=3, mult=0.65)`
- `(guard_bars=3, mult=0.75)`

This remains an exact $3 \times 3 = 9$ tuple surface.

No other tuple and no other seam is admissible under this packet.

## Freeze carry-forward — unchanged

All freeze boundaries from the predecessor admissibility packet remain in force unchanged.

That unchanged freeze carry-forward includes at minimum:

- family / authority / identity markers remain frozen
- signal / regime-definition backdrop remains frozen
- the prior `EV / edge` seam remains frozen
- execution-management backdrop remains frozen
- `multi_timeframe.regime_intelligence.risk_state.drawdown_guard.*` remains frozen / unopened
- `multi_timeframe.regime_intelligence.clarity_score.*` remains frozen / unopened
- `multi_timeframe.regime_intelligence.size_multiplier.{min,max}` remains frozen / unopened
- `OBJECTIVE` remains deferred
- `SIGNAL / feature-surface` remains deferred

This packet introduces no reinterpretation, no new opening, and no relaxation of that freeze state.

## Reserved future subject paths only

This packet reserves only the following future subject paths for a later separate authoring review:

### Future canonical subject path — reserved only

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_decision_risk_state_transition_guard_slice1_2024_v1.yaml`

### Future bounded smoke subject path — reserved only

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_decision_risk_state_transition_guard_slice1_smoke_20260327.yaml`

These are reserved future subject paths only.

No YAML files are created in this step.
No YAML contents are approved in this step.
No authoring authority is granted in this step.

## Reserved bounded smoke boundary

This packet reserves the bounded smoke subject path only.

Any smoke-specific semantics or field-level differences versus the future canonical subject must be defined and reviewed in a later separate authoring/evidence packet.

None of those semantics are approved in this step.

## Later evidence bundle — what must be proven later

This packet does not claim any gate has passed.
It defines only what a later evidence bundle would need to prove.

### Later validator evidence must prove

A later validator evidence bundle must prove that the future canonical subject:

1. remains inside the exact seam `multi_timeframe.regime_intelligence.risk_state.transition_guard.{guard_bars,mult}`
2. exposes only the exact nine-tuple surface `{1,2,3} × {0.55,0.65,0.75}`
3. leaves the full frozen backdrop intact outside that seam
4. introduces no new searchable parameters and no hidden widening
5. keeps the slice research-only with promotion disabled

### Later preflight evidence must prove

A later preflight evidence bundle must prove that the future canonical subject:

1. still resolves as a research-only RI subject under the later exact authoring step
2. still presents exactly one seam and exactly nine tuples
3. still preserves the unchanged freeze carry-forward
4. does not drift into launch authorization, runtime-validity, or broader config-authority claims
5. remains bounded to one canonical subject path and one bounded smoke subject path only

### Later bounded smoke evidence must prove

A later bounded smoke evidence bundle must prove only that the later reserved smoke subject:

1. is correctly bounded as a smoke subject for this exact seam only
2. preserves the same single-seam attribution as the later canonical subject
3. remains consistent with the unchanged frozen backdrop outside `transition_guard.{guard_bars,mult}`
4. serves as a bounded seam-check only, not as proof of uplift, readiness, or launch approval

## What this packet does not claim

This packet does **not** claim any of the following:

- that either reserved YAML subject path already exists
- that either reserved YAML subject path is approved for authoring now
- that validator has passed
- that preflight has passed
- that bounded smoke has passed
- that the slice is launch-ready
- that the slice is runtime-valid RI conformity
- that comparison, readiness, promotion, or writeback is open

## Exact non-authorizations

This is a docs-only setup packet.

It is **not**:

- a YAML authoring packet
- a gate-pass packet
- a launch-admissibility packet
- a launch-authorization packet
- an execution packet
- an outcome-signoff packet

It authorizes none of those things.

## Next admissible step after this packet

If this packet is accepted, the next admissible step is only:

- a later separate docs-only YAML-authoring / evidence-collection review for the two reserved future subject paths above

That later step remains distinct from launch authorization and must still respect the unchanged freeze carry-forward and exact nine-tuple seam definition.

## Bottom line

This packet does one thing only:

- it reserves exactly one future canonical subject path and exactly one future bounded smoke subject path for the already chosen `transition_guard` seam, while carrying the entire freeze state forward unchanged and defining what later validator/preflight/smoke evidence would still need to prove.

Anything broader must stop and return to new governance review.
