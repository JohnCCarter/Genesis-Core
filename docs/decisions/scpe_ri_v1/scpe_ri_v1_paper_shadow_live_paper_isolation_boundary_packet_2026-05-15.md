# SCPE RI V1 paper-shadow / live-paper isolation boundary packet

Date: 2026-05-15
Branch: `feature/evidence-closeout-pilot`
Status: `decision-recorded / docs-only / non-authorizing`

This boundary record is a documentation snapshot of the currently cited evidence as of 2026-05-15. It does not change runtime behavior, does not grant deployment, readiness, paper, or live-paper authority, and does not supersede implementation or test artifacts.

This packet freezes only the documentation boundary for closeout traceability. It does not freeze implementation, operational policy, deployment state, or approval status.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via `feature/* -> RESEARCH`
- **Category:** `docs`
- **Risk:** `MED` — why: this slice records a paper/live-adjacent interpretation boundary, but it stays docs-only and citation-driven
- **Required Path:** `Quick path / docs-only boundary record`
- **Lane:** `Research-evidence` — why: this packet reduces authority drift without reopening runner, API, or operational surfaces
- **Objective:** record the current isolation boundary between dry-run-only RI paper-shadow and live-paper semantics using already tracked code, tests, packets, and citation-only operational references
- **Base SHA:** `57bc4cb0`
- **Related queue item:** `docs/analysis/diagnostics/next_phase_verkstad_queue_2026-05-15.md`

### Scope

- **Scope IN:** this boundary packet; the queue update that records Slice 6 as closed
- **Scope OUT:** all edits under `src/**`, `scripts/**`, `tests/**`, `config/**`, `results/**`, and `artifacts/**`; all edits to `docs/paper_trading/runner_deployment.md` and `docs/paper_trading/phase3_runbook.md`; all readiness, cutover, launch, deployment, paper approval, live-paper approval, runtime, promotion, or champion semantics; all edits to `scripts/paper_trading_runner.py`, `src/core/strategy/evaluate.py`, and `src/core/api/paper.py`
- **Max files touched:** `2`

### Gates required

For this packet itself:

- targeted docs validation on this packet and the queue file only
- manual wording audit that this packet stays documentation-closeout only
- manual wording audit that `runner_deployment.md` and `phase3_runbook.md` remain citation-only context rather than implementation or readiness authority
- manual wording audit that the `logs/paper_trading` vs `results/paper_live` distinction is recorded only as a cited operational-documentation boundary / terminology ambiguity rather than as a fix instruction

## Purpose

This packet answers one narrow question only:

- given the currently tracked SCPE RI paper-shadow evidence, tests, and operational references, what isolation interpretation is admissible now between dry-run-only RI paper-shadow and live-paper semantics?

## Governing basis

### Observed

1. `scripts/paper_trading_runner.py` enforces the seam at multiple levels:
   - `parse_args()` rejects `--ri-paper-shadow` together with `--live-paper`
   - `validate_ri_paper_shadow_guardrails()` and `enforce_ri_paper_shadow_guardrails()` fail fast if `live_paper=True`, `dry_run=False`, or pre-existing outbound `state_in["observability"]` would create ambiguous authority
   - `_build_evaluate_state()` injects only `state["observability"]["scpe_ri_v1"] = true` when the opt-in is enabled
   - `run_loop()` reaches `/paper/submit` only when `config.live_paper` is true
2. `tests/integration/test_paper_trading_runner.py` covers the primary isolation chain:
   - parser conflict for `--ri-paper-shadow` + `--live-paper`
   - evaluate-path rejection when RI paper-shadow is requested in live-paper configuration
   - fail-fast rejection of pre-existing `state_in["observability"]`
   - allowlisted RI paper-shadow summary in `DECISION_CONTEXT` with non-allowlisted fields excluded
   - separate live-paper guardrails for execution mode and results namespace
3. `docs/decisions/scpe_ri_v1/scpe_ri_v1_paper_shadow_slice1_precode_packet_2026-04-21.md` bounded this lane to default-OFF, dry-run-only, no order authority, no edits to `docs/paper_trading/**`, and no readiness/live-paper semantics.
4. `docs/analysis/scpe_ri_v1/scpe_ri_v1_paper_shadow_slice1_implementation_report_2026-04-21.md` records that the bounded slice was implemented with gates green and no paper approval, live-paper approval, readiness, cutover, launch, deployment, or promotion claim.
5. `docs/analysis/scpe_ri_v1/archive/scpe_ri_v1_runtime_integration_seam_inventory_2026-04-20.md` classed the paper-runner seam as operationally later than earlier SCPE RI lanes.
6. `docs/decisions/scpe_ri_v1/archive/scpe_ri_v1_runtime_observability_closeout_transition_packet_2026-04-21.md` preserved the carry-forward rule that later paper-shadow work remains separately governed and citation-only with respect to `scripts/paper_trading_runner.py`, `docs/paper_trading/runner_deployment.md`, and `docs/paper_trading/phase3_runbook.md` until separately packeted.
7. `src/core/strategy/evaluate.py` emits `meta["observability"]["scpe_ri_v1"]` only when explicitly requested, and the emitted payload remains `observational_only = True` and `decision_input = False`.
8. `src/core/api/paper.py` remains the operational order-authority surface through `/paper/submit`, which this packet does not reopen.
9. `docs/paper_trading/runner_deployment.md` and `docs/paper_trading/phase3_runbook.md` still describe dry-run/live-paper operational procedures and are therefore citation-only operational context in this slice.
10. A cited operational-documentation boundary / terminology ambiguity is visible today:
    - current runner CLI defaults and live-paper path guardrails point to `results/paper_live/**`
    - historical operational docs still heavily reference `logs/paper_trading/**`
    - `build_runner_contract_snapshot()` in `scripts/paper_trading_runner.py` records `path_contract_mode = dual_primary_results_compat_logs` and the active path mode

### Inferred

- The cited code, test, packet, and report set provides materially sufficient bounded evidence to document the current RI paper-shadow ↔ live-paper isolation seam.
- The primary remaining risk here is interpretation drift, not absence of primary parser/guardrail/evaluate-path isolation coverage.
- Given the cited evidence set, the next bounded closeout action is to record the isolation boundary in documentation only.
- The `logs/paper_trading` vs `results/paper_live` distinction can be recorded as a cited operational-documentation boundary / terminology ambiguity only; this packet is not a fix instruction, defect classification, migration directive, or approval signal.

### Unverified in this packet

- whether all historical operational docs should later be harmonized with current runner defaults
- whether a future operational lane would want additional startup-path or run-loop-path seam tests
- whether the archived Phase 3 paper-trading documents reflect every current default path in the runner

## Minimal claim-to-source map

- **Parser + runner guardrail isolation:** `scripts/paper_trading_runner.py` and `tests/integration/test_paper_trading_runner.py`
- **Dry-run-only local observability shape:** `scripts/paper_trading_runner.py`, `src/core/strategy/evaluate.py`, and `tests/integration/test_paper_trading_runner.py`
- **Order authority remains separate:** `scripts/paper_trading_runner.py` and `src/core/api/paper.py`
- **Historical bounded lane contract:** `docs/decisions/scpe_ri_v1/scpe_ri_v1_paper_shadow_slice1_precode_packet_2026-04-21.md` and `docs/analysis/scpe_ri_v1/scpe_ri_v1_paper_shadow_slice1_implementation_report_2026-04-21.md`
- **Operational context only:** `docs/paper_trading/runner_deployment.md` and `docs/paper_trading/phase3_runbook.md`

## Boundary record

### Boundary label

- `SCPE_RI_PAPER_SHADOW_LIVE_PAPER_ISOLATION_BOUNDARY_RECORDED`

### Meaning of that label

This label means only the following:

- the currently cited repository evidence is sufficient to record the present isolation boundary between dry-run-only RI paper-shadow and live-paper semantics
- RI paper-shadow remains default-OFF, dry-run-only, and local-observability-only
- live-paper order authority remains separate and out of scope
- historical operational documents remain citation-only context in this slice
- no runtime, deployment, readiness, promotion, or champion authority follows from this packet

This label does **not** mean:

- the operational documentation set is harmonized or newly approved
- the `logs/paper_trading` vs `results/paper_live` distinction is hereby classified as a defect or fixed
- live-paper safety or readiness is proven by this packet
- no future tests or operational packets will ever be needed
- this packet authorizes edits to runner, API, or operational documentation surfaces

## What remains out of scope

This packet keeps the following out of scope unless separately reopened:

- all edits to `scripts/paper_trading_runner.py`
- all edits to `tests/integration/test_paper_trading_runner.py`
- all edits to `src/core/strategy/evaluate.py`
- all edits to `src/core/api/paper.py`
- all edits to `docs/paper_trading/runner_deployment.md`
- all edits to `docs/paper_trading/phase3_runbook.md`
- all live-paper readiness, cutover, launch, deployment, or operational approval semantics
- all runtime, promotion, champion, or config-authority interpretation
- all attempts to harmonize path defaults or operational docs inside this slice

## Hard stop and reopen rule

If a future slice needs any of the following, it must stop and reopen instead of leaning on this packet:

- harmonizing or changing `logs/paper_trading/**` and `results/paper_live/**` documentation or defaults
- adding new runner, API, or order-path tests
- modifying `/paper/submit` semantics, runner order authority, or live-paper guardrails
- using this packet as readiness, deployment, or operational approval
- widening the subject into promotion, runtime, or champion semantics

## Bottom line

The cited test and packet set provides materially sufficient bounded evidence to document the current RI paper-shadow ↔ live-paper isolation seam. This is a documentation closeout statement only, not a new implementation, operational, or readiness claim.
