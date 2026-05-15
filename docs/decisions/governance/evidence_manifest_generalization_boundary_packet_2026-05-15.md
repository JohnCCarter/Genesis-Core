# Evidence manifest generalization boundary packet

Date: 2026-05-15
Branch: `feature/evidence-closeout-pilot`
Status: `decision-recorded / docs-only / non-authorizing`

This document is a governance-adjacent decision artifact in `RESEARCH`. It records the current boundary after the evidence-script audit and grants no source, test, runtime, config-authority, paper/live, readiness, launch, or promotion authority.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via `feature/* -> RESEARCH`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice records a docs-only boundary decision and does not alter runtime, evidence-producing code, tests, or output contracts
- **Required Path:** `Quick path / docs-only decision record`
- **Lane:** `Research-evidence` — why: this packet bounds future evidence-closeout work and does not authorize runtime integration
- **Objective:** decide whether the two completed manifest-closeout pilots justify broader generalization across `scripts/analyze/**`
- **Base SHA:** `7471125a29bcf08a5f0da390dcef6b5710fa7317`
- **Related audit:** `docs/analysis/diagnostics/evidence_manifest_candidate_audit_2026-05-15.md`

### Scope

- **Scope IN:** this packet; the companion audit note `docs/analysis/diagnostics/evidence_manifest_candidate_audit_2026-05-15.md`
- **Scope OUT:** all source/test changes; all new manifest utilities; all replay-root rewrites; all third-pilot implementation work; all runtime/backtest/config-authority/public-edge changes; all promotion or readiness claims
- **Max files touched:** `2`

### Gates required

For this packet itself:

- targeted docs validation for this packet and the companion audit note
- manual wording audit that the conclusion remains docs-only and non-authorizing
- manual wording audit that the packet records a boundary decision rather than silently reopening a code slice

## Purpose

This packet answers one narrow question only:

- should the manifest-closeout pattern now be generalized beyond the two May 15 pilots?

## Governing basis

### Observed

1. `execution_proxy_evidence` and `edge_origin_isolation` now prove the bounded manifest-closeout pattern on two deterministic multi-output evidence producers with nearby verification surfaces.
2. `scpe_ri_v1_router_replay.py` already owns a richer provenance surface than the new pilot pattern, including replay-root manifests, input/output hashes, approved output inventories, and containment metadata.
3. Representative downstream SCPE scripts such as `scpe_ri_v1_router_diagnostics.py` and `scpe_ri_v1_no_trade_release_probe.py` consume or preserve that replay-root provenance and emit summary-only evaluation artifacts rather than opening a fresh same-shaped manifest gap.
4. `ri_policy_router_blocked_reason_split_20260429.py` represents a different class again: a one-off observational summary emitter without the same deterministic multi-output closeout seam as the two pilots.
5. The targeted audit did not surface a third representative script that both lacks direct manifest closeout and closely matches the pilot shape.

### Inferred

- A repo-wide or shared abstraction introduced now would be fitted to heterogeneous script classes instead of repeated same-shaped gaps.
- Generalizing now would therefore risk overfitting the solution to two pilots and under-describing the richer or narrower provenance contracts already present elsewhere.
- The honest current status is: **pattern proven locally, not standardized globally**.
- Future reopen work should happen only one script at a time, and only when the candidate script has all of the following:
  - a deterministic multi-output root
  - a genuine claim-bearing closeout gap
  - no richer existing provenance contract already owning the surface
  - a bounded verification story that does not require framework-first redesign

### Unverified in this packet

- whether a later third candidate with closer shape exists elsewhere in `scripts/analyze/**`
- whether a future minimal shared helper could emerge after more same-shaped candidates are proven
- whether any later provenance hardening should target summary-only emitters for reasons outside the May 15 pilot pattern

## Boundary decision

### Current standing conclusion

The manifest-closeout pattern should **not** be generalized further in this slice.

The correct bounded decision is:

- **defer repo-wide or shared manifest-closeout generalization**
- **retain the current pattern as a script-local closeout technique**
- **reopen only when a new candidate script actually matches the pilot shape and presents a real closeout gap**

### What this does not mean

This boundary decision does **not** mean:

- that the May 15 pilots were unsuccessful
- that future provenance hardening is forbidden
- that SCPE replay surfaces are weak or incomplete
- that one-off summary emitters can never be hardened

It means only that the audit did not justify a broader abstraction **now**.

## Reopen criteria

If this boundary is revisited later, the next admissible implementation packet should stay bounded to one candidate script and must define at minimum:

- why that script is a better same-shaped candidate than the representative scripts rejected here
- the exact output-root contract before and after the change
- the exact verification surface proving deterministic closeout behavior
- why the change is not duplicating an existing richer provenance owner

## Hard stop and reopen rule

If a future slice needs any of the following, it must stop and reopen as a separate bounded packet instead of leaning on this document:

- shared manifest utility extraction
- edits to multiple evidence scripts at once
- replay-root provenance redesign
- any runtime/backtest/config-authority/public-edge change
- any claim that the boundary decision itself grants implementation authority

## Bottom line

The two May 15 pilots proved a useful local pattern, not a repo-wide framework. The admissible governance answer is therefore to defer generalization, preserve the pattern as a bounded per-script closeout technique, and reopen only when a third candidate genuinely matches the same shape instead of merely being nearby in the `scripts/analyze/**` directory tree.
