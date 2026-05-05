# Regime Intelligence challenger family — experiment-map reselection Phase 5 binding note

Date: 2026-03-30
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `phase5-resolved / planning-only / no authorization`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this note resolves Phase 5 by binding the current experiment-map reselection chain to one already existing bounded pre-code packet, but must remain narrower than pre-code creation, narrower than admissibility, and narrower than launch or execution authority.
- **Required Path:** `Quick`
- **Objective:** Resolve Phase 5 by selecting the exact already existing bounded pre-code packet that would govern any future pre-code step for the current reselection chain.
- **Candidate:** `Phase 5 pre-code reference binding`
- **Base SHA:** `c27add49`

### Scope

- **Scope IN:** one docs-only binding note; explicit designation of one already existing bounded pre-code packet as the future pre-code reference for the current reselection chain; explicit compatibility statement with the already chosen class, surface, and 3h anchor; explicit non-authorization boundary.
- **Scope OUT:** no source-code changes; no config YAML creation; no validator/preflight/smoke/optimizer execution; no new pre-code content; no launch subject; no admissibility refresh; no launch authorization; no implementation path; no changes under `src/**`, `config/**`, `scripts/**`, or `tests/**`; no fib reopening; no reopening of the closed slice8 upstream diagnostic path; no comparison/readiness/promotion/writeback.
- **Expected changed files:** `docs/decisions/regime_intelligence/experiment_map/regime_intelligence_experiment_map_reselection_phase5_precode_binding_note_2026-03-30.md`
- **Max files touched:** `1`

### Stop Conditions

- any wording that makes the referenced 2026-03-27 pre-code packet newly authorized for execution
- any wording that presents this note as a new pre-code packet rather than a binding note
- any wording that republishes, supersedes, or refreshes the referenced 2026-03-27 packet
- any wording that creates new YAML, new ranges, new grids, new selectors, or new execution guidance
- any wording that reopens fib or the closed slice8 upstream diagnostic path

## Purpose

This note answers one narrow question only:

- which exact already existing bounded pre-code packet should serve as the future pre-code reference for the current experiment-map reselection chain?

This note is **planning-only governance**.

It does **not**:

- create a new pre-code packet
- create new pre-code scope
- authorize launch
- authorize execution
- authorize validation activity
- authorize YAML creation

## Governing basis

This note is downstream of the following tracked artifacts:

- `docs/analysis/regime_intelligence/core/regime_intelligence_experiment_map_reselection_roadmap_2026-03-30.md`
- `docs/decisions/regime_intelligence/experiment_map/regime_intelligence_experiment_map_reselection_signal_segmentation_direction_packet_2026-03-30.md`
- `docs/decisions/regime_intelligence/experiment_map/regime_intelligence_experiment_map_reselection_regime_definition_candidate_surface_packet_2026-03-30.md`
- `docs/decisions/regime_intelligence/experiment_map/regime_intelligence_experiment_map_reselection_regime_definition_packet_boundary_2026-03-30.md`
- `docs/decisions/regime_intelligence/optuna/signal/regime_intelligence_optuna_signal_regime_definition_slice1_precode_command_packet_2026-03-27.md`

Carried-forward meaning:

1. the current reselection chain has already chosen `SIGNAL / segmentation` as class orientation
2. the current reselection chain has already chosen `multi_timeframe.regime_intelligence.regime_definition.*` as the single candidate surface
3. the packet boundary has already established that the next admissible step, if work continues, may only be a separate bounded pre-code packet
4. this note therefore resolves only which exact already existing pre-code packet fills that role

## Non-reopen boundary

The closed slice8 upstream diagnostic path remains closed.

This note does **not**:

- reopen that path
- extend that path
- derive a new diagnostic slice from that path
- convert that path into launch or implementation authority

## Selected future pre-code reference

The exact designated future pre-code reference for the current reselection chain is:

- `docs/decisions/regime_intelligence/optuna/signal/regime_intelligence_optuna_signal_regime_definition_slice1_precode_command_packet_2026-03-27.md`

This note selects that packet as the already existing bounded pre-code reference for the current chain.

It introduces no new pre-code scope, trials, YAML, or admissibility content.

## Compatibility statement only

Compatibility is recorded only as documentary alignment with the already selected:

- class: `SIGNAL / segmentation`
- candidate surface: `multi_timeframe.regime_intelligence.regime_definition.*`
- anchor: `3h`

Representative `3h` artifact anchor:

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_signal_regime_definition_slice1_2024_v1.yaml`

This is an alignment statement only.

It is **not**:

- a new validation claim
- a launch-readiness claim
- a new admissibility claim
- a new execution claim

## Historical status preserved

The referenced 2026-03-27 pre-code packet retains its:

- original date
- original scope
- original historical status

This note does **not**:

- republish it
- supersede it
- refresh it
- upgrade it into execution authority

It only binds the current experiment-map reselection chain to that already existing bounded pre-code reference.

## Explicit non-authorization boundary

This note does **not** issue:

- launch approval
- execution approval
- validator/preflight/smoke approval
- admissibility refresh
- runnable-slice readiness
- implementation approval

Any future execution decision remains subject to a separate explicit governance step under the then-current repository state and checks.

## Bottom line

Phase 5 is now resolved for the current experiment-map reselection chain as follows:

- the chain is bound to the already existing bounded pre-code packet `docs/decisions/regime_intelligence/optuna/signal/regime_intelligence_optuna_signal_regime_definition_slice1_precode_command_packet_2026-03-27.md`
- no new pre-code packet content is introduced here
- no new launch, execution, validation, YAML, or admissibility authority is created here

This note resolves the **reference**, not the **execution**.
