# Regime Intelligence challenger family — DECISION risk-state transition-guard slice1 leaf-field inventory admissibility packet

Date: 2026-03-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `leaf-inventory-admissibility-defined / docs-only / no leaf inventory yet`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet decides only whether a later separate docs-only packet may enumerate leaf-field names without values for the same two already reserved subject paths, while remaining narrower than leaf inventory itself, narrower than YAML creation, and narrower than launch authorization.
- **Required Path:** `Full gated docs-only`
- **Objective:** Define the admissibility criteria, blockers, and non-authorizations for any later separate docs-only leaf-field inventory packet concerning the same two already reserved transition-guard slice1 subject paths.
- **Candidate:** `future tBTCUSD 3h RI DECISION transition-guard slice1 leaf-inventory admissibility gate`
- **Base SHA:** `d227be7e6d07c4b389529ee6a0ece228ca9a9b10`

### Scope

- **Scope IN:** one docs-only admissibility packet; exact same two reserved subject paths; why this remains docs-only; admissibility criteria for a later leaf-field inventory packet; explicit still-blocked items; exact next allowed step only.
- **Scope OUT:** no source-code changes, no test changes, no changes under `src/core/**`, no changes under `tests/**`, no changes under `config/optimizer/**`, no changes under `tmp/**`, no changes under `results/**`, no YAML authoring, no file creation outside this one docs packet, no YAML/config/result/tmp file creation, no pseudo-YAML, no leaf names in this packet, no leaf values, no defaults, no ranges, no types, no requiredness, no ordering semantics, no launch, no validator/preflight/smoke execution, no gate claims, no runtime-valid RI conformity, no comparison/readiness/promotion/writeback.
- **Expected changed files:** `docs/decisions/regime_intelligence_optuna_decision_risk_state_transition_guard_slice1_leaf_field_inventory_admissibility_packet_2026-03-27.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/path sanity only
- manual wording audit that the packet decides only admissibility and does not enumerate leaf fields
- manual wording audit that the packet contains no schema-like structure, value decision, or YAML-adjacent scaffold

For interpretation discipline inside this packet:

- discussion must remain limited to the same two already reserved subject paths
- no leaf-field names may appear as drafting content in this packet
- no sentence may imply that a later leaf inventory is already accepted
- no sentence may imply that leaf inventory approval equals YAML creation approval
- no sentence may imply launch, execution, or gate passage authority

### Stop Conditions

- any leaf-field inventory appearing in this packet
- any schema-like grouping that effectively inventories leaf content by implication
- any values, defaults, ranges, types, requiredness, or ordering rules
- any new subject path, alias path, or auxiliary path
- any wording that upgrades this packet into authoring approval, YAML creation approval, or launch preparation

### Output required

- one reviewable docs-only leaf-field inventory admissibility packet
- exact same two reserved subject paths
- explicit admissibility criteria for a later leaf-field inventory packet
- explicit still-blocked items
- exact non-authorizations
- exact next allowed step only

## Decision question

This packet answers one narrow question only:

- under what conditions may a later separate docs-only packet enumerate leaf-field names without values for the same two already reserved `transition_guard` slice1 subject paths?

This packet does **not** answer:

- what those leaf-field names are
- what any values, defaults, ranges, or types are
- whether any YAML should now be created
- whether any execution or launch step may begin

## Exact same reserved subject paths only

The only subject paths carried forward by this packet remain:

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_decision_risk_state_transition_guard_slice1_2024_v1.yaml`
- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_decision_risk_state_transition_guard_slice1_smoke_20260327.yaml`

No other path is opened or implied here.

## Why this is still docs-only

This packet remains docs-only because it decides only whether a later naming-only inventory step may be reviewed.

It does not:

- enumerate leaves
- specify values
- specify types
- specify requiredness
- specify ordering
- create or edit YAML
- authorize launch or execution

## Admissibility criteria for a later leaf-field inventory packet

A later separate docs-only leaf-field inventory packet may be considered admissible only if all of the following remain true:

1. it stays limited to the same two already reserved subject paths and no others
2. it enumerates leaf-field names only, without values, defaults, ranges, step sizes, enum decisions, or type decisions
3. it remains downstream of the already approved upstream governance chain only
4. it does not imply that naming a leaf makes that leaf approved for YAML creation or execution semantics
5. it remains distinct from YAML authoring, validator/preflight/smoke evidence, launch authorization, and execution approval
6. it preserves the already bounded single-seam research surface rather than widening it

If any one of those conditions fails, the later leaf-field inventory packet is inadmissible and work must stop for fresh governance review.

## Still blocked after this packet

The following remain blocked after this packet:

- any actual leaf-field inventory in this packet
- any value assignment
- any type decision
- any default decision
- any YAML authoring or file creation
- any validator/preflight/smoke evidence packet
- any launch-admissibility or launch-authorization packet downstream of this step
- any execution packet or outcome signoff

These blockers remain intentional.

## Non-authorizations

This packet is not:

- a leaf-field inventory packet
- a YAML authoring packet
- a YAML creation packet
- a launch packet
- an execution packet

This packet authorizes none of those things.

## Outcome / next allowed step

The bounded conclusion of this packet is:

- one later separate docs-only packet may, if separately accepted, enumerate leaf-field names without values for the same two already reserved subject paths and still remain below YAML creation and launch

The next admissible step after this packet remains only:

- a later separate docs-only leaf-field inventory packet for the same two already reserved subject paths, still without values and still distinct from YAML creation and launch authorization

Anything broader must stop and return to fresh governance review.

## Bottom line

This packet does one narrow thing only:

- it decides whether a later value-less leaf-field inventory packet may even be considered for the already reserved `transition_guard` slice1 subject paths.
