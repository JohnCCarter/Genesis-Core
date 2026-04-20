# SCPE RI V1 shadow-backtest packet boundary

Date: 2026-04-20
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `packet-boundary-defined / planning-only / no authorization`

This document is a planning artifact in `RESEARCH` and grants no implementation, runtime, readiness, cutover, launch, execution, deployment, paper-trading, or promotion authority. It must not be used as approval to begin code, config, test, backtest, runtime, or operational changes. Any future RI shadow-backtest step requires its own separate commit contract, separate command packet, fresh scope approval, and separate verification.

## Future packet scaffold (planning-only, non-executable placeholder)

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `LOW` — why: this note only defines the next packet boundary for a future SCPE RI shadow-backtest slice and must remain narrower than pre-code, narrower than admissibility, narrower than execution planning, and narrower than launch or implementation authority
- **Required Path:** `Quick`
- **Objective:** define what packet type must come next, if work continues, before any future runnable or implementation-adjacent SCPE RI shadow-backtest slice could be considered on the already visible repository seam
- **Candidate:** `future packet boundary for bounded RI-only shadow-backtest slice`
- **Base SHA:** `afe32b20`

The scaffold below is a non-executable planning placeholder only. It contains no approved selectors, commands, gates, implementation scope, readiness claim, or authorization for future work.

### Scope

- **Scope IN:** one docs-only packet-boundary decision; explicit relation to the 2026-04-20 research closeout, runtime/integration roadmap, and seam inventory; explicit statement of what remains fixed; explicit statement of what remains out of scope; explicit determination of the next admissible packet type only; explicit fail-closed non-authorization boundary
- **Scope OUT:** all edits under `src/**`, `tests/**`, `config/**`, `scripts/**`, `results/**`, and `artifacts/**`; all runnable commands or selectors; all implementation approval; all backtest execution approval; all runtime/paper behavior claims; all readiness/cutover/promotion framing
- **Expected changed files:** `docs/governance/scpe_ri_v1_shadow_backtest_packet_boundary_2026-04-20.md`
- **Max files touched:** `1`

### Stop Conditions

- any wording that treats this note as approval to run or implement a shadow-backtest slice
- any wording that reactivates or adopts historical shadow packets as current authority
- any wording that turns the visible seam into execution readiness, launch readiness, or implementation readiness
- any wording that creates commands, selectors, artifact schemas, subject windows, or test sets for a future slice
- any wording that opens runtime instrumentation, paper-shadow, behavior change, readiness, cutover, or promotion work

## Purpose

This note answers one narrow question only:

- what packet type must come next, if work continues, before any future SCPE RI shadow-backtest slice could be considered on the already visible repository seam?

This note is **planning-only governance**.

It does **not**:

- authorize a runnable shadow-backtest slice
- authorize a code change
- authorize a config change
- authorize a test change
- authorize execution
- authorize launch
- authorize signoff or readiness

## Governing basis

This note is downstream of the following tracked artifacts:

- `docs/governance/scpe_ri_v1_research_closeout_report_2026-04-20.md`
- `docs/governance/scpe_ri_v1_runtime_integration_roadmap_2026-04-20.md`
- `docs/governance/scpe_ri_v1_runtime_integration_seam_inventory_2026-04-20.md`
- `docs/audit/research_system/command_packet_backtest_champion_shadow_intelligence_v1_2026-03-18.md`
- `docs/features/feature-champion-shadow-intelligence-1.md`

Carried-forward meaning:

1. the bounded SCPE RI research lane is closed and grants no inherited runtime/integration approval
2. the runtime/integration roadmap already placed shadow-only backtest work earlier than runtime-observability, paper-shadow, and behavior-change work
3. the seam inventory already identified the backtest shadow seam as the smallest currently visible implementation-adjacent seam in the repository snapshot
4. this note must therefore decide only the **next packet boundary**, not whether a shadow-backtest slice is open

## Existing seam status

The repository already contains visible generic shadow-backtest plumbing:

- `scripts/run/run_backtest.py`
  - imports `BacktestIntelligenceShadowRecorder`
  - exposes opt-in flag `--intelligence-shadow-out`
  - wires the recorder into `engine.evaluation_hook`
- `src/core/backtest/intelligence_shadow.py`
  - builds deterministic shadow events
  - derives advisory-only parameter sets
  - runs deterministic research orchestration
  - persists summary output and ledger-linked artifacts
- `src/core/backtest/engine.py`
  - exposes the passive `evaluation_hook(result, meta, candles)` seam

Meaning:

- the generic seam is already visible in tracked repository state
- this note is therefore **not** deciding whether generic shadow plumbing should be implemented
- this note is deciding only what packet type is required before any future **RI-specific** shadow-backtest slice could be considered

## Historical-precedent boundary

The historical documents:

- `docs/audit/research_system/command_packet_backtest_champion_shadow_intelligence_v1_2026-03-18.md`
- `docs/features/feature-champion-shadow-intelligence-1.md`

are treated here only as **historical seam precedent**.

This note does **not**:

- reactivate them
- extend them
- treat them as current implementation authority
- treat them as approval for SCPE RI-specific use
- convert their scope, artifact homes, or tests into active authority for the current lane

## Boundary decision

### What is not required next

Because the generic shadow-backtest seam is already present in tracked repository state, the next step does **not** need to be:

- a new generic shadow-plumbing implementation packet
- a seam-invention packet
- a runtime-observability packet
- a paper-shadow packet
- a behavior-change packet
- a launch-authorization packet

Why:

- the repository already exposes a passive backtest shadow hook and opt-in CLI surface
- the repository already exposes deterministic shadow artifact production machinery
- the current question is no longer whether a shadow-backtest seam can exist in general
- the current question is only how an **RI-specific bounded slice** would need to be packeted, if work continues

This is a narrow boundary conclusion only.

It does **not** imply that an RI shadow-backtest slice is now greenlit.

### What the next admissible packet may be

If work continues, the next admissible step may only be:

- a **separate pre-code packet** for one exact bounded **RI-only shadow-backtest slice**

That future pre-code packet, if opened later, must still remain bounded and fail-closed.

It would need to define only things such as:

- the exact RI-only objective for the slice
- the exact subject boundary for the slice
- whether the slice is purely observational or produces any new retained evidence artifacts
- how the slice preserves opt-in and non-authoritative status
- what remains out of scope relative to runtime, paper, and behavior-change surfaces

It must **not** itself authorize runtime instrumentation, paper execution, or promotion.

## What remains fixed

Before any future pre-code packet could exist, the following remain fixed:

- research closeout boundary remains intact
- replay-root closeout remains non-authoritative
- runtime-observability remains unopened
- paper-shadow remains unopened
- behavior change remains unopened
- runtime-config/champion/default-authority surfaces remain closed
- family boundaries remain explicit and unchanged unless separately re-approved
- readiness, cutover, and promotion remain closed

## What remains out of scope

Still out of scope beyond this note:

- any runnable backtest shadow slice
- any runtime instrumentation slice
- any paper-shadow slice
- any behavior-changing slice
- any config writeback or champion mutation
- any commands, selectors, trial windows, or artifact schemas
- any test definition
- any readiness/cutover/promotion/writeback framing

## Explicit non-authorization boundary

This note does **not** constitute:

- implementation approval
- execution approval
- launch approval
- admissibility approval for a runnable slice
- readiness approval
- cutover or promotion approval

Its sole purpose is to determine the required packet type before any future SCPE RI shadow-backtest slice could be considered.

## Bottom line

The packet boundary is now defined as follows:

- no new generic shadow-plumbing implementation packet is required for the already visible repository seam
- no runtime-observability, paper-shadow, or behavior-change packet is the next admissible step
- the next admissible step, if work continues, may only be a **separate pre-code packet for one exact bounded RI-only shadow-backtest slice**

Nothing in this note authorizes implementation, execution, runtime instrumentation, paper activity, readiness, cutover, or promotion.
