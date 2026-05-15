# SCPE defensive-probe carrier decision packet

Date: 2026-05-15
Branch: `feature/evidence-closeout-pilot`
Status: `decision-recorded / docs-only / non-authorizing`

This document records the exact SCPE-derived carrier strategy to use if the `defensive_probe` concept/replay line is reopened. It grants no runtime, config-authority, paper/live, promotion, or broader SCPE replay authority by itself.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via `feature/* -> RESEARCH`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice chooses one bounded SCPE-derived carrier only and does not modify scripts, tests, results, runtime behavior, or policy semantics
- **Required Path:** `Quick path / docs-only pre-code packet`
- **Lane:** `Research-evidence` — why: the packet narrows one exact SCPE-derived carrier without reopening runtime, broader replay-root authority, or paper/live semantics
- **Objective:** choose one exact commit-safe SCPE-derived carrier for the `defensive_probe` line
- **Base SHA:** `30c59e8e41ae7a284c84b7cf38c22ce08dc027a4`
- **Related artifacts:** `docs/analysis/diagnostics/next_phase_verkstad_queue_2026-05-15.md`, `docs/analysis/diagnostics/decision_influencing_replay_smoke_candidate_selection_2026-05-15.md`, `docs/analysis/diagnostics/evidence_manifest_candidate_audit_2026-05-15.md`, `docs/decisions/regime_intelligence/policy_router/ri_policy_router_defensive_probe_concept_precode_packet_2026-04-29.md`, `docs/analysis/regime_intelligence/policy_router/ri_policy_router_defensive_probe_exact_carrier_evidence_2026-04-29.md`

### Scope

- **Scope IN:** this carrier-decision packet; queue sync that records Slice 9 as completed and advances the next admissible slice
- **Scope OUT:** all changes under `scripts/**`; all changes under `tests/**`; all changes under `results/**`; all changes under `src/**`; all changes under `config/**`; all changes under `artifacts/**`; all changes under `registry/fixtures/**`; repo-wide claim-header discipline; ignored-artifact inventory; RI/policy-router runtime language; paper/live, readiness, promotion, or config-authority semantics
- **Max files touched:** `2`

### Gates required

For this packet itself:

- targeted docs validation for this packet and queue sync
- manual wording audit that the carrier decision stays exact and local to the `defensive_probe` line
- manual wording audit that the packet does not widen into broader SCPE replay-root authority or runtime/paper-live semantics

## Purpose

This packet answers one narrow question only:

- what exact SCPE-derived replay surface should a future `defensive_probe` line use as its first commit-safe carrier?

## What changed in this slice

- the SCPE-derived `defensive_probe` line now has one explicit exact carrier instead of inheriting replay confidence from the broader SCPE replay root by shorthand
- the repo now records which SCPE surface is primary carrier and which nearby surfaces remain citation-only or comparator-only

## What did not change

- no source, test, results, runtime, or config-authority behavior
- no paper/live, readiness, or promotion semantics
- no broader SCPE replay portability or runtime identity authority

## Governing basis

### Observed

1. The successor queue asks for one exact SCPE replay surface as the next carrier decision, not for a full-root SCPE replay reopening.
2. The replay-smoke candidate-selection note records `scpe_ri_v1_router_replay.py` as highly relevant but broader than the smallest first bounded replay move.
3. The evidence-manifest candidate audit records that SCPE replay already has a richer provenance contract and that downstream SCPE probes behave as consumers or summary producers rather than as fresh missing-manifest gaps.
4. The `defensive_probe` concept pre-code packet explicitly preferred one later read-only evidence slice that isolates one exact `defensive_transition_state` carrier or row-set instead of widening into runtime or annual reinterpretation.
5. The exact carrier evidence note already localized the smallest honest repo-visible `defensive_probe` carrier to the two-row selected-defensive pocket around `2024-01-16T00:00:00` and `2024-01-17T12:00:00` on the frozen baseline replay surface, with only one `defensive_transition_state` member reaching selected defensive.
6. That same note also records the nearest retained `RI_no_trade_policy` and continuation comparators outside the tiny fresh low-zone pocket, which keeps the line local rather than broad.
7. The surrounding SCPE lineage is historical and tracked, but earlier docs already treat those surfaces as context or historical reference rather than inherited authority for a fresh slice.

### Inferred

- The smallest admissible SCPE-derived carrier is **not** the whole `scpe_ri_v1_router_replay` root and **not** a summary-only evaluation artifact.
- The smallest admissible first carrier is **the exact two-row selected-defensive pocket** already localized in `docs/analysis/regime_intelligence/policy_router/ri_policy_router_defensive_probe_exact_carrier_evidence_2026-04-29.md` on the frozen baseline replay surface.
- The retained `RI_no_trade_policy` and continuation rows remain useful comparators, but they are comparator context rather than the primary carrier.
- This carrier is commit-safe precisely because it is already anchored to tracked historical reference surfaces and a repo-visible exact-carrier note, while still staying concept-only and local.
- The packet must keep the line below broader SCPE replay portability, broader regime-personality claims, and any paper/live or runtime semantics.

### Unverified in this packet

- whether any future step beyond concept-only or local evidence should ever exist for `defensive_probe`
- whether the tiny two-row pocket could ever support a stronger `historical-trace-level` or `full-chain clean-checkout-level` claim for this line
- whether other SCPE-derived lines need separate carrier decisions later

## Boundary decision

### Current standing conclusion

If the `defensive_probe` line is reopened, the exact first SCPE-derived carrier should be:

- **the two-row selected-defensive pocket localized in `docs/analysis/regime_intelligence/policy_router/ri_policy_router_defensive_probe_exact_carrier_evidence_2026-04-29.md` on the frozen baseline replay surface**

In exact row terms, that carrier is bounded to:

- `2024-01-16T00:00:00`
- `2024-01-17T12:00:00`

This is a carrier-selection conclusion only. It is **not** approval to run new evidence, reopen the full SCPE replay root, or claim a distinct runtime `defensive_probe` identity.

### Primary carrier versus nearby non-primary surfaces

For this line, treat the following as **primary carrier**:

- the two-row selected-defensive pocket above

Treat the following as **not** the primary carrier for this slice:

- the full `scpe_ri_v1_router_replay` root
- summary-only or downstream consumer artifacts
- broader annual or multi-window reinterpretation
- paper/live or runtime-policy semantics

### Comparator boundary retained for interpretation only

If this line is reopened later, the nearest retained comparators may still be cited for interpretation discipline only:

- the retained `RI_no_trade_policy` comparator at `2025-01-28T06:00:00`
- the retained continuation comparator at `2024-03-22T12:00:00`

They remain comparator context only. They do **not** widen the primary carrier beyond the two-row pocket.

## Hard stop and reopen rule

If a future slice needs any of the following, it must stop and reopen as a separate bounded packet:

- script, test, or result-root changes
- full-root SCPE replay portability claims
- wider annual/window sweeps
- runtime, config-authority, paper/live, or promotion language
- a claim that the `defensive_probe` line already exists as a runtime identity

## Bottom line

The smallest honest SCPE-derived carrier is local, not global. For the `defensive_probe` line, the first commit-safe carrier is the exact two-row selected-defensive pocket already localized on the frozen baseline replay surface. That keeps Slice 9 below broader SCPE replay-root authority, below runtime identity claims, and below paper/live semantics.
