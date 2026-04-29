# Regime Intelligence challenger family — DECISION risk-state transition-guard slice1 authoring admissibility packet

Date: 2026-03-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `authoring-admissibility-defined / docs-only / no YAML authoring opened`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet decides only whether a later docs-only YAML authoring review may even be opened for the two already reserved subject paths, while remaining narrower than YAML authoring, narrower than launch authorization, and free of any final field decisions.
- **Required Path:** `Full gated docs-only`
- **Objective:** Define the admissible evidence surface, the authoring-admissibility criteria, and the explicit blockers for any later separate docs-only authoring review concerning the already reserved transition-guard slice1 subject paths.
- **Candidate:** `future tBTCUSD 3h RI DECISION transition-guard slice1 authoring-admissibility gate`
- **Base SHA:** `d227be7e6d07c4b389529ee6a0ece228ca9a9b10`

### Scope

- **Scope IN:** one docs-only authoring-admissibility packet; the same two already reserved subject paths; permitted evidence inputs; explicit authoring-admissibility criteria; known unknowns / blockers; explicit non-authorizations; exact next admissible step.
- **Scope OUT:** no source-code changes, no test changes, no changes under `src/core/**`, no changes under `tests/**`, no changes under `config/optimizer/**`, no changes under `tmp/**`, no changes under `results/**`, no YAML authoring, no save-ready pseudo-YAML, no parameter values, no defaults, no thresholds, no final field decisions, no launch, no validator/preflight/smoke execution, no gate claims, no runtime-valid RI conformity, no comparison/readiness/promotion/writeback.
- **Expected changed files:** `docs/decisions/regime_intelligence/optuna/decision/regime_intelligence_optuna_decision_risk_state_transition_guard_slice1_authoring_admissibility_packet_2026-03-27.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/path sanity only
- manual wording audit that the packet remains authoring-admissibility only and does not draft YAML
- manual wording audit that the packet contains no parameter-value or final-field decisions

For interpretation discipline inside this packet:

- the packet must remain limited to the same two already reserved subject paths
- the packet must cite the prior governance chain as backdrop rather than restating new config truth
- the packet must define criteria for a later authoring review without becoming that review
- the packet must not reinterpret config-authority, runtime semantics, or launch semantics
- the packet must not imply that authoring, execution, or gate passage is already approved

### Stop Conditions

- any wording that drafts or implies copy-ready YAML
- any wording that introduces parameter values, thresholds, defaults, or final field decisions
- any wording that expands beyond the same two reserved paths
- any wording that upgrades this packet into authoring, execution approval, or launch preparation
- any wording that claims or implies passed gates or runtime-valid RI conformity

### Output required

- one reviewable docs-only authoring-admissibility packet
- exact two reserved subject paths under review
- explicit permitted evidence inputs
- explicit authoring-admissibility criteria
- explicit blockers / known unknowns
- explicit non-authorizations
- exact next admissible step only

## Decision question / narrow purpose

This packet answers one narrow question only:

- under what conditions may a later separate docs-only authoring review even be considered governance-admissible for the two already reserved `transition_guard` slice1 subject paths?

This packet does **not** answer:

- what the final YAML text should be
- what the final field values should be
- whether any YAML should now be created
- whether validator, preflight, smoke, or launch is approved

## Exact two reserved subject paths under review

The only subject paths under review in this packet are:

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_decision_risk_state_transition_guard_slice1_2024_v1.yaml`
- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_decision_risk_state_transition_guard_slice1_smoke_20260327.yaml`

No other path is opened, implied, or admitted by this packet.

## Permitted evidence inputs

The only permitted evidence inputs for deciding authoring-admissibility in this packet are the already tracked governance references below:

- `docs/decisions/regime_intelligence/optuna/decision/regime_intelligence_optuna_decision_clarity_risk_state_direction_packet_2026-03-27.md`
- `docs/decisions/regime_intelligence/optuna/decision/regime_intelligence_optuna_decision_risk_state_transition_guard_slice1_precode_command_packet_2026-03-27.md`
- `docs/decisions/regime_intelligence/optuna/decision/regime_intelligence_optuna_decision_risk_state_transition_guard_slice1_launch_admissibility_packet_2026-03-27.md`
- `docs/decisions/regime_intelligence/optuna/decision/regime_intelligence_optuna_decision_risk_state_transition_guard_slice1_setup_packet_2026-03-27.md`
- `docs/decisions/regime_intelligence/optuna/decision/regime_intelligence_optuna_decision_risk_state_transition_guard_slice1_yaml_shape_review_packet_2026-03-27.md`
- `docs/decisions/regime_intelligence/optuna/decision/regime_intelligence_optuna_decision_ev_edge_slice1_execution_outcome_signoff_summary_2026-03-27.md`

Permitted use of those references in this packet is limited to:

- confirming that the same two subject paths were already reserved
- confirming that the current lane remains docs-only and no-launch
- confirming that the single-seam attribution and bounded research surface were already defined upstream
- confirming that the prior YAML-shape review remains proposal-only rather than authoring authority

This packet does not admit any new evidence class, runtime artifact, or config-authority source.

## Authoring-admissibility criteria

A later separate docs-only authoring review may be considered admissible only if all of the following remain true:

1. it stays limited to the same two already reserved subject paths and no others
2. it derives its field-level drafting surface only from the already cited upstream governance chain
3. it preserves the same single-seam attribution and the same bounded research surface already defined upstream
4. it does not introduce any new parameter family, any new runtime/config-authority interpretation, or any new search dimension
5. it remains distinct from YAML creation, execution approval, and launch authorization
6. it states explicitly that any later authoring artifact is still subject to separate evidence and later gate review
7. it does not claim that the prior proposal-only shape review has already become a final config decision
8. it keeps comparison, readiness, promotion, and writeback closed

If any one of those conditions fails, later authoring review is inadmissible and work must stop for fresh governance review.

## Known unknowns / blockers

The following blockers remain open after this packet and prevent any implicit jump to YAML authoring or execution:

- no later authoring review has yet been accepted
- no YAML file exists at either reserved subject path by authority of this packet
- no final field-decision packet exists
- no validator evidence exists in this packet
- no preflight evidence exists in this packet
- no smoke evidence exists in this packet
- no launch-admissibility or launch-authorization decision exists downstream of this packet
- no runtime-valid RI conformity claim is available from this packet

These blockers are intentional and remain in force.

## Explicit non-authorizations

This packet does **not** authorize any of the following:

- YAML authoring
- YAML creation under `config/optimizer/**`
- pseudo-YAML intended for copy/paste
- parameter selection
- threshold selection
- default selection
- final field decisions
- validator, preflight, or smoke execution
- launch preparation
- launch authorization
- runtime-valid RI conformity
- comparison, readiness, promotion, or writeback

## What may appear in a later authoring review, if separately admitted

If and only if a later separate authoring review is admitted, that later step may discuss:

- how the already cited upstream governance chain constrains drafting
- how the two already reserved subject paths differ in role
- what later evidence would still be required before any execution step could be considered

That later step would still remain separate from YAML creation, execution approval, and launch authority unless independently approved.

## Next admissible step after this packet

If this packet is accepted, the next admissible step is limited to:

- a later separate docs-only authoring review for the same two already reserved subject paths, still bounded by the upstream chain and still distinct from YAML creation and launch authorization

Anything broader must stop and return to fresh governance review.

## Bottom line

This packet does one narrow thing only:

- it decides whether later docs-only authoring review may even be opened for the already reserved `transition_guard` slice1 subject paths, and it says that such review is admissible only under the exact bounded criteria and blocker set recorded above.
