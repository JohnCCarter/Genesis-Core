# SCPE RI V1 runtime-observability transition packet

Date: 2026-04-21
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `phase-2-closed / phase-3-opening-defined / docs-only / no direct code authorization`

This document is a governance transition artifact in `RESEARCH`.
It records that the separately governed phase-2 shadow-backtest prerequisite is now closed and determines the exact next admissible runtime/integration-adjacent lane.
It does **not** itself authorize code changes, config changes, test changes, runtime deployment, paper-shadow, readiness, cutover, or promotion.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet transitions from a completed shadow-only backtest lane to the next runtime-adjacent governance lane, and the main risk is over-reading completed phase-2 evidence as broader runtime authority.
- **Required Path:** `Quick`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** decide whether the completed shadow-backtest bridge slice is sufficient to open the next separately governed runtime-observability lane, and if so freeze the exact smallest admissible implementation-adjacent slice.
- **Candidate:** `SCPE RI V1 runtime-observability phase transition`
- **Base SHA:** `b475736d`
- **Skill Usage:** `.github/skills/python_engineering.json`, `.github/skills/repo_clean_refactor.json` referenced as scope/minimal-diff guardrails only; this packet makes no skill-based implementation claim.

### Scope

- **Scope IN:**
  - one docs-only transition/admissibility packet
  - explicit relation to the completed phase-2 shadow-backtest lane
  - explicit selection of the exact next admissible runtime/integration-adjacent lane
  - explicit non-authorization and carry-forward boundary
- **Scope OUT:**
  - all edits under `src/**`, `tests/**`, `config/**`, `scripts/**`, `results/**`, and `artifacts/**`
  - any implementation approval for paper-shadow or behavior-change lanes
  - any reuse of research replay packets as inherited runtime/integration authority
  - any launch, readiness, cutover, deployment, or promotion wording
- **Expected changed files:**
  - `docs/governance/scpe_ri_v1_runtime_observability_transition_packet_2026-04-21.md`
  - downstream separate pre-code packet only if this packet affirms the lane
- **Max files touched:** `2`

### Gates required

- `pre-commit run --files docs/governance/scpe_ri_v1_runtime_observability_transition_packet_2026-04-21.md docs/governance/scpe_ri_v1_runtime_observability_slice1_precode_packet_2026-04-21.md`

### Stop Conditions

- any wording that treats the completed shadow-backtest slice as inherited runtime or paper approval
- any wording that treats the router-replay research lineage as runtime/integration authorization
- any wording that skips directly to paper-shadow or behavior-change work
- any wording that opens an always-on response-shape change, runtime-config mutation, champion merge change, or decision-path change
- any wording that treats existing additive observability as already-governed SCPE RI implementation authority

## Governing basis

This packet is downstream of:

- `docs/governance/scpe_ri_v1_runtime_integration_roadmap_2026-04-20.md`
- `docs/governance/scpe_ri_v1_runtime_integration_seam_inventory_2026-04-20.md`
- `docs/governance/scpe_ri_v1_shadow_backtest_packet_boundary_2026-04-20.md`
- `docs/governance/scpe_ri_v1_shadow_backtest_bridge_slice1_final_launch_authorization_packet_2026-04-21.md`
- `docs/governance/scpe_ri_v1_shadow_backtest_bridge_slice1_execution_summary_2026-04-21.md`
- `docs/governance/scpe_ri_v1_research_closeout_report_2026-04-20.md`

Carried-forward meaning that remains fixed:

1. the bounded research lane is closed and grants no inherited runtime/integration approval
2. the completed phase-2 shadow-backtest slice is valid only for its exact RI-only observational surface
3. runtime-observability remains a later lane that must be separately justified
4. paper-shadow remains later still
5. behavior-change remains later still
6. default behavior must remain unchanged unless separately and explicitly approved

## What phase 2 resolved

The completed phase-2 shadow-backtest bridge slice now contributes the following green evidence:

- exact RI-only control/shadow parity was observed on the bounded bridge subject
- the machine-readable shadow summary remained advisory-only
- bounded write containment remained green
- the bridge lane proved that a passive RI-only observational hook can run without decision-row drift on the reviewed backtest surface

This evidence closes the phase-2 prerequisite named in the runtime/integration roadmap.
It does **not** automatically open runtime-adjacent code changes.

## Why replay lineage does not satisfy this transition by itself

The repository already contains a tracked SCPE RI replay implementation lineage on research surfaces:

- `docs/governance/scpe_ri_v1_router_replay_implementation_packet_2026-04-20.md`
- `docs/governance/scpe_ri_v1_router_replay_script_promotion_packet_2026-04-20.md`
- `scripts/analyze/scpe_ri_v1_router_replay.py`
- `results/evaluation/scpe_ri_v1_router_replay_2026-04-20.json`

That lineage remains valid as research-only replay/evidence work.
It does **not** provide inherited authorization for runtime/integration because:

- it is explicitly below runtime integration
- it is rooted in frozen research replay, not runtime request handling
- the research closeout explicitly denied inherited runtime/integration approval

## Current runtime seam snapshot

The seam inventory and current code show that `src/core/strategy/evaluate.py` already emits additive runtime observability under:

- `meta["observability"]["shadow_regime"]`

Current tracked properties include:

- `authoritative_source`
- `shadow_source`
- `authority_mode`
- `authority_mode_source`
- `authority`
- `shadow`
- `mismatch`
- `decision_input = False`

Current tests already prove that this shadow-regime payload is additive and non-authoritative.
That is useful seam evidence, but it is not the same thing as an opened SCPE RI runtime-observability lane.

## Transition decision

### Decision

- **Phase 2 is closed enough to open Phase 3 only as one bounded runtime-observability lane**

### Exact next admissible lane

The next admissible implementation-adjacent lane is **not**:

- paper-shadow
- behavior change
- runtime-config authority work
- champion/default merge policy work
- always-on API response-shape widening

The next admissible lane is only:

- **one bounded, additive, request-scoped, RI-only runtime-observability slice on `/strategy/evaluate` that remains explicitly non-authoritative and default-unchanged when opt-in is absent**

## Why this is the smallest honest next lane

This is the smallest honest lane because it:

- stays later than the now-completed shadow-backtest prerequisite, exactly as the roadmap required
- uses an already visible runtime seam instead of inventing a new authority surface
- remains additive and observational only
- can preserve default response shape when opt-in is absent
- can avoid runtime-config and champion-authority surfaces entirely
- stays meaningfully narrower than paper-shadow or behavior change

## Exact lane constraints that remain fixed

Any downstream implementation packet opened from this transition must keep all of the following fixed:

- request-scoped opt-in only
- no change to `result`
- no change to action, size, reasons, confidence, regime, or champion merge behavior
- no mutation of `meta["observability"]["shadow_regime"]`
- no runtime-config authority surface
- no paper-runner surface
- no router/policy/veto authority surface
- no default-on response-shape drift
- no readiness, cutover, or promotion framing

## What the downstream pre-code packet must define exactly

The separately governed downstream packet must define at minimum:

1. the exact opt-in request surface
2. the exact additive response namespace
3. the exact field allowlist for the additive RI payload
4. the exact files allowed in Scope IN
5. the exact parity and no-drift gates
6. the exact stop conditions if the slice tries to widen into authority or contract drift

## Explicit non-authorization boundary

This packet does **not** authorize:

- direct code edits
- direct test edits
- runtime deployment
- runtime default change
- paper-shadow
- behavior change
- readiness, cutover, launch, or promotion

Its sole job is to close the phase-2 prerequisite and define the exact smallest next admissible lane.

## Bottom line

The completed shadow-backtest bridge slice is sufficient to move the runtime/integration roadmap forward by **one** step only.

That step is a separate pre-code implementation packet for one bounded additive RI runtime-observability slice on `/strategy/evaluate`.

Nothing broader is opened here.
