# Regime Intelligence challenger family — experiment-map post-binding roadmap

Date: 2026-03-30
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `historical / documentary chain / archive-only / future-only / no authorization`

> Current status note:
>
> - [ARCHIVED 2026-05-05] This roadmap is not an active lane on `feature/next-slice-2026-05-05`.
> - Preserve it as an archived historical documentary governance chain for the earlier March 30 post-binding path.
> - Any future reuse still requires a fresh compatibility decision or packet.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this roadmap sequences the next governance questions after the current reselection chain was bound to an already existing historical pre-code reference, but must remain narrower than pre-code, narrower than admissibility, narrower than launch preparation, and narrower than execution or signoff authority.
- **Required Path:** `Quick`
- **Objective:** Define the next fail-closed governance roadmap after the current experiment-map reselection chain was completed through packet-boundary and Phase 5 binding.
- **Candidate:** `future post-binding governance path`
- **Base SHA:** `c27add49`

### Scope

- **Scope IN:** one docs-only roadmap that sequences the next governance questions after the Phase 5 binding note; explicit historical-status handling for the adopted pre-code reference; explicit first compatibility-inventory note; explicit future-only packet-class sequencing; explicit out-of-scope and non-authorization boundaries.
- **Scope OUT:** no source-code changes; no config YAML creation; no validator/preflight/smoke/optimizer execution; no launch authorization; no execution; no signoff; no new slice content; no changes under `src/**`, `config/**`, `scripts/**`, or `tests/**`; no fib reopening; no reopening of the closed slice8 upstream diagnostic path; no comparison/readiness/promotion/writeback.
- **Expected changed files:** `docs/analysis/regime_intelligence/core/regime_intelligence_experiment_map_post_binding_roadmap_2026-03-30.md`
- **Max files touched:** `1`

### Stop Conditions

- any wording that reactivates the adopted historical pre-code reference
- any wording that treats historical launch authorization as current launch authority
- any wording that resolves compatibility instead of merely inventorying the question
- any wording that selects or prepares a launch packet as the next active step
- any wording that creates commands, gates, YAML shape, ranges, grids, selectors, or execution guidance

## Purpose

This roadmap answers one narrow question only:

- what governance-sequencing path should apply after the current reselection chain has already been completed through candidate-surface selection, packet-boundary definition, and Phase 5 pre-code reference binding?

This roadmap is **planning-only governance**.

It does **not**:

- reactivate the adopted historical pre-code reference
- authorize launch
- authorize execution
- authorize validation activity
- authorize YAML creation
- authorize signoff

## Starting point

The starting point for this roadmap is fixed by the already tracked chain artifacts:

- `docs/analysis/regime_intelligence/core/regime_intelligence_experiment_map_reselection_roadmap_2026-03-30.md`
- `docs/decisions/regime_intelligence/experiment_map/regime_intelligence_experiment_map_reselection_signal_segmentation_direction_packet_2026-03-30.md`
- `docs/decisions/regime_intelligence/experiment_map/regime_intelligence_experiment_map_reselection_regime_definition_candidate_surface_packet_2026-03-30.md`
- `docs/decisions/regime_intelligence/experiment_map/regime_intelligence_experiment_map_reselection_regime_definition_packet_boundary_2026-03-30.md`
- `docs/decisions/regime_intelligence/experiment_map/regime_intelligence_experiment_map_reselection_phase5_precode_binding_note_2026-03-30.md`

Carried-forward meaning:

1. the fixed slice8 upstream diagnostic path remains closed in current tracked state
2. the chosen class remains `SIGNAL / segmentation`
3. the chosen candidate surface remains `multi_timeframe.regime_intelligence.regime_definition.*`
4. the chain has already been bound to one historical bounded pre-code reference
5. no execution, launch, validation activity, or YAML authoring has been authorized by that chain

## Historical reference status

The adopted reference:

- `docs/decisions/regime_intelligence/optuna/signal/regime_intelligence_optuna_signal_regime_definition_slice1_precode_command_packet_2026-03-27.md`

must be treated here only as a **historical bounded pre-code reference**.

This roadmap does **not**:

- reactivate it
- update it
- refresh it
- treat it as currently green for use
- derive immediate launch or execution authority from it

The same caution applies to the historical launch packet:

- `docs/decisions/regime_intelligence/optuna/signal/regime_intelligence_optuna_signal_regime_definition_slice1_launch_authorization_packet_2026-03-27.md`

That document remains historically true for its original state, but this roadmap does **not** treat it as current launch authority for the present chain.

## Out of scope

The following remain explicitly out of scope for this roadmap:

- any runnable slice
- any YAML creation or editing
- any validator/preflight/smoke run
- any launch authorization
- any execution
- any signoff or outcome interpretation
- any reopening of fib
- any reopening of the closed slice8 upstream diagnostic path
- any comparison/readiness/promotion/writeback framing

## Planning stance

This roadmap proceeds under the following fail-closed stance:

- preserve the current non-authorization boundary
- treat adopted historical references as documentary anchors only
- inventory compatibility questions before considering any later packet-class choice
- keep any future launch/execution/signoff strictly future-only

## Phases

### Phase 0 — Preserve the non-authorization boundary

Goal:

- keep the completed reselection chain documentary only

Required outcome:

- every downstream note must continue to state that no launch, execution, validator/preflight activity, or signoff authority has been created by the March 30 reselection chain

Stop if:

- any text begins speaking as if the chain has produced runnable-slice readiness

### Phase 1 — Anchor the adopted historical reference

Goal:

- preserve the adopted pre-code reference and the historical launch packet as historical artifacts rather than active approvals

Required outcome:

- downstream planning must continue to distinguish between historical reference status and present-chain authority

Stop if:

- the adopted pre-code packet is described as reactivated
- the historical launch packet is described as current authorization

### Phase 2 — Inventory the current-state compatibility question

Goal:

- identify whether a separate current-state compatibility delta note is required before any future use of the adopted historical pre-code reference could even be considered

Boundary:

- this roadmap starts directly only by recording this compatibility question as an inventory concern
- this roadmap does **not** answer the question
- this roadmap does **not** establish compatibility

Phase status:

- **started now** in this document, only in the sense that the inventory note below is recorded here

Initial compatibility inventory note:

- the current chain is anchored to a historical pre-code reference dated `2026-03-27`
- that same historical line also contains a separate launch-authorization packet dated `2026-03-27`
- before any future use of the adopted pre-code reference could be considered, a separate governance note may be required to determine whether present-chain framing and current repository state still allow that historical pre-code reference to be used as an admissible starting point
- this inventory note does **not** decide that question and does **not** imply that compatibility is already satisfied

Stop if:

- the compatibility question starts being answered inside this roadmap

### Phase 3 — Future packet-class assessment only if separately governed

Goal:

- if and only if a later separate compatibility note resolves cleanly, determine what future packet class would be admissible next

Status:

- **föreslagen**, not selected by this roadmap itself

Important boundary:

- this roadmap does **not** choose that future packet class now
- this roadmap does **not** prepare launch authorization now
- this roadmap does **not** prepare execution now

Stop if:

- any future packet class is described here as already chosen

### Phase 4 — Execution and signoff remain future-only

Goal:

- keep execution, output interpretation, and signoff outside the present roadmap

Status:

- **föreslagen**, not opened by this roadmap

Boundary:

- no execution
- no launch
- no signoff
- no artifact interpretation

Stop if:

- the roadmap begins to describe commands, gates, or execution envelopes

## Bottom line

The current experiment-map reselection chain is complete as a **documentary governance chain**.

The next roadmap therefore does **not** move directly into launch preparation.

Instead, it sequences one fail-closed post-binding path:

- preserve non-authorization,
- preserve historical-reference status,
- start only by inventorying whether a separate current-state compatibility note is required,
- and leave any future packet-class choice, launch, execution, or signoff strictly outside the present roadmap.
