# SCPE RI V1 runtime/integration roadmap

Date: 2026-04-20
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `historical / future-only / non-executable / no authorization`

> Current status note:
>
> - This roadmap is not an active lane on `feature/next-slice-2026-04-29` and should not be treated as the next live path.
> - Preserve it as a historical future-only governance path for SCPE RI follow-up after the 2026-04-20 closeout.
> - `GENESIS_WORKING_CONTRACT.md` already treats the SCPE replay surfaces as historical reference context only.

This document is a planning artifact in `RESEARCH` and grants no implementation, runtime, readiness, cutover, launch, deployment, or promotion authority. It must not be used as approval to begin code, config, test, runtime, paper-trading, or operational changes. Every future phase below requires a separate commit contract, separate command packet, Opus pre-code review, and its own verification.

## COMMAND PACKET (planning-only, non-executable)

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `LOW` — why: single-file docs-only sequencing artifact; main risk is governance wording drift that could be misread as runtime or promotion authority
- **Required Path:** `Quick`
- **Objective:** define a fail-closed sequencing roadmap for any future SCPE RI runtime/integration work after the bounded 2026-04-20 research closeout, while preserving the current non-authorization boundary and separating future shadow, runtime-observability, paper-shadow, and behavior-change questions into distinct governance lanes
- **Candidate:** `future SCPE RI runtime/integration governance path`
- **Base SHA:** `b0805d47`

### Scope

- **Scope IN:** this roadmap only; explicit starting point from the 2026-04-20 research closeout; phased future-lane sequencing; explicit prerequisites; explicit out-of-scope and non-authorization boundaries
- **Scope OUT:** all code/config/test/result/artifact changes; all edits under `src/**`, `tests/**`, `config/**`, `scripts/**`, `results/**`, or `artifacts/**`; all edits to existing closeout docs; all runtime/readiness/cutover/promotion approvals; all runnable commands, selectors, or execution instructions; all claims that any future lane is already chosen or approved
- **Expected changed files:** `docs/analysis/scpe_ri_v1/scpe_ri_v1_runtime_integration_roadmap_2026-04-20.md`
- **Max files touched:** `1`

### Stop Conditions

- any wording that treats this roadmap as implementation authority
- any wording that implies inherited runtime approval from the research closeout
- any wording that presents a future lane as already selected, greenlit, or executable
- any wording that introduces runnable commands, selectors, gates, or implementation scope for future phases
- any wording that treats historical shadow artifacts as adopted design authority rather than historical precedent
- any wording that claims readiness, promotion, cutover, or deployment status

## Purpose

This roadmap answers one narrow governance question only:

- what fail-closed sequencing path should apply if SCPE RI work later moves from the now-closed bounded research lane toward runtime-adjacent or integration-adjacent questions?

This roadmap is **planning-only governance**.

It does **not**:

- reopen the closed research lane
- authorize code changes
- authorize config changes
- authorize test creation or execution
- authorize runtime observability changes
- authorize backtest integration
- authorize paper-trading integration
- authorize cutover, readiness, launch, deployment, or promotion

## Starting point

The starting point is fixed by the already tracked closeout boundary:

- `docs/decisions/scpe_ri_v1/scpe_ri_v1_research_closeout_report_2026-04-20.md`

That closeout already established that:

1. the current bounded SCPE RI V1 research roadmap is complete as a research lane
2. the canonical replay root remains `NEEDS_REVISION`
3. no runtime/integration approval is inherited from the closeout
4. any follow-up must start as a brand-new governance lane
5. the objective of any future lane must be explicit
6. default behavior must remain unchanged unless separately authorized
7. family boundaries, parity requirements, determinism requirements, and trade-off decisions must be restated for the new lane

Additional historical precedent surfaces may inform future packet design, but only as documentary precedent rather than adopted authority:

- `docs/analysis/regime_intelligence/core/regime_intelligence_default_cutover_gap_analysis_2026-03-17.md`
- `docs/features/feature-champion-shadow-intelligence-1.md`
- `docs/audit/research_system/command_packet_backtest_champion_shadow_intelligence_v1_2026-03-18.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_direct_baseline_admissibility_2026-04-16.md`

Those documents are referenced here only to preserve already learned constraints:

- governance blockers remain governance/control-surface oriented
- shadow-only integration must remain explicitly opt-in and parity-safe
- direct shortcuts into runtime-like surfaces are not admissible without prerequisite slices

This roadmap does **not** choose, reuse, or approve any specific historical integration design.

## Out of scope

The following remain explicitly out of scope for this roadmap:

- any runnable implementation slice
- any edits to runtime authority or default authority
- any edits to `config/runtime.json` or candidate/champion configs
- any edits to strategy, backtest, API, scheduler, or paper-runner code
- any new tests or selectors
- any execution guidance
- any readiness, cutover, launch, deployment, or promotion packet
- any claim that SCPE RI is ready for runtime or integrated behavior change
- any cross-family routing or family-boundary relaxation

## Planning stance

This roadmap proceeds under a fail-closed stance:

- preserve the closeout boundary
- assume no inherited authority
- open only the smallest future governance question at a time
- keep behavior-changing possibilities explicitly later than observational or shadow-only possibilities
- require each future lane to justify its own objective, scope, gates, and stop conditions from scratch

## Phases

### Phase 0 — Preserve the closeout boundary

Goal:

- keep the just-completed research closeout authoritative as a boundary, not as a runtime green light

Required outcome:

- every downstream note must continue to say that the research lane ended with bounded explanatory success, not runtime readiness

Stop if:

- any text starts treating the closeout as implicit approval for implementation or promotion

### Phase 1 — Inventory the current-state integration seams

Goal:

- identify which future integration questions are even admissible to ask first without yet selecting an implementation lane

Scope of the future question:

- which backtest seams, runtime-adjacent observability seams, paper-shadow seams, and control-surface boundaries would matter for an RI-specific integration path?

Required outcome:

- one future compatibility/seam-inventory note that maps candidate surfaces, authority boundaries, artifact homes, and likely stop conditions

Important boundary:

- this roadmap records only that such an inventory note should come first
- this roadmap does not perform that inventory
- this roadmap does not authorize code inspection changes or seam activation

Stop if:

- the roadmap starts selecting a concrete integration seam or implementation design

### Phase 2 — Consider a separate shadow-only backtest lane

Goal:

- if the seam inventory is admissible, evaluate whether the smallest implementation-adjacent step should be a deterministic, explicitly opt-in, shadow-only backtest lane

Why this phase exists:

- historical precedent suggests that shadow-only backtest integration is the narrowest honest way to test artifact plumbing and parity discipline before any runtime-facing change

Required future lane properties:

- explicit opt-in only
- no decision drift
- deterministic artifact output
- no mutation of runtime/default/champion authority
- explicit failure policy

Important boundary:

- this roadmap does not choose a design
- this roadmap does not authorize reuse of any historical shadow packet as-is
- this roadmap only states that a shadow-only backtest lane is the earliest plausible implementation candidate

Stop if:

- the roadmap starts describing code changes, tests, commands, or artifact schemas as if they are already approved

### Phase 3 — Consider a separate runtime-observability lane

Goal:

- only after a backtest-shadow lane is separately justified and closed, assess whether a runtime-adjacent observational lane is admissible

Nature of the future lane:

- observational only
- default-OFF or otherwise non-authoritative unless separately approved
- no decision-input authority by implication
- no readiness or promotion claim

Required future questions:

- what observability could be emitted without changing authority?
- what runtime-adjacent trace or summary surfaces would remain clearly non-authoritative?
- how would determinism/parity be restated for an observational runtime path?

Important boundary:

- this roadmap does not authorize runtime instrumentation now
- this roadmap does not claim that runtime observability is already open
- this roadmap keeps runtime-adjacent work below readiness, cutover, and promotion semantics

Stop if:

- the roadmap begins to speak as if runtime instrumentation is already greenlit or harmless by default

### Phase 4 — Consider a separate paper-shadow lane

Goal:

- only after prior observational lanes are separately justified, assess whether a paper-trading-adjacent shadow lane is admissible

Nature of the future lane:

- observational/shadow only
- no order-decision authority change
- no live promotion
- no inherited approval from backtest or runtime-observability lanes

Required future questions:

- what paper-shadow artifact or audit outputs would be needed?
- what failure policy would preserve normal paper execution semantics?
- what operational controls, rollback boundaries, and review discipline would be required?

Important boundary:

- this roadmap does not authorize paper deployment
- this roadmap does not authorize paper execution changes
- this roadmap only preserves paper-shadow as a later candidate governance lane

Stop if:

- the roadmap starts treating paper-shadow as equivalent to paper approval, or paper approval as equivalent to live readiness

### Phase 5 — Only then assess whether a behavior-change candidate lane is admissible

Goal:

- keep any actual decision-path or policy-behavior change explicitly later than shadow and observational work

Status:

- **candidate only**, not selected by this roadmap

Required future preconditions:

- prior lanes must have their own closed evidence chains
- explicit exception to `NO BEHAVIOR CHANGE`
- fresh governance packet
- restated parity and determinism contract for the intended behavior change
- explicit trade-off decision on what evidence is sufficient and what degradation is acceptable
- explicit statement of whether the lane is still RI-only and how family boundaries remain protected

Important boundary:

- this roadmap does not authorize a behavior-changing lane now
- this roadmap does not define the future acceptance threshold now
- this roadmap does not convert research findings into runtime authority

Stop if:

- the roadmap starts presenting a behavior change as the expected or approved destination

### Phase 6 — Readiness, cutover, and promotion remain future-only

Goal:

- keep readiness, default cutover, champion/config writeback, deployment, and promotion outside the present roadmap

Status:

- **future-only**, not opened here

Boundary:

- no readiness claim
- no cutover framing
- no promotion framing
- no deployment framing

Stop if:

- the roadmap starts sounding like a launch checklist

## Bottom line

The bounded SCPE RI research lane is closed, but it does not hand over implementation authority.

The correct next governance shape is therefore not “start integrating RI now.”

It is a fail-closed sequencing path:

1. preserve the closeout boundary
2. inventory seams before selecting any implementation-adjacent lane
3. treat shadow-only backtest work as the earliest plausible implementation candidate
4. keep any runtime-observability lane separate and explicitly non-authoritative
5. keep any paper-shadow lane later and separately justified
6. keep any behavior-changing lane explicitly later still
7. leave readiness, cutover, and promotion strictly outside the current roadmap

So this document starts the runtime/integration roadmap only in the one admissible sense available now:

- as a planning-only governance map for future lanes,
- not as approval to enter them.
