# Execution proxy clean-checkout replay smoke boundary packet

Date: 2026-05-15
Branch: `feature/evidence-closeout-pilot`
Status: `decision-recorded / docs-only / non-authorizing`

This document records the boundary after selecting `execution_proxy_evidence` as the first clean-checkout replay smoke candidate. It grants no source, test, runtime, config-authority, paper/live, promotion, or artifact-chain authority by itself.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via `feature/* -> RESEARCH`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice records a docs-only boundary for a future reproducibility candidate and does not modify scripts, tests, results, or runtime behavior
- **Required Path:** `Quick path / docs-only boundary record`
- **Lane:** `Research-evidence` — why: this packet narrows the next admissible reproducibility step without authorizing implementation
- **Objective:** define what packet type must come next after selecting `execution_proxy_evidence` as the first clean-checkout replay smoke candidate
- **Base SHA:** `57ce4bd8`
- **Related selection note:** `docs/analysis/diagnostics/decision_influencing_replay_smoke_candidate_selection_2026-05-15.md`

### Scope

- **Scope IN:** this boundary packet; the companion selection note; the queue update that records the selected candidate and the newly exposed fixture-containment gap
- **Scope OUT:** all script/test changes; all fixture imports; all bundle creation; all new replay automation; all CI wiring; all edge-origin or SCPE replay implementation work; all runtime/config-authority/paper/live/promotion changes
- **Max files touched:** `3`

### Gates required

For this packet itself:

- targeted docs validation for this packet and companion selection note
- manual wording audit that the packet stays non-authorizing
- manual wording audit that the next step is narrowed to one candidate chain and one fixture-containment question only

## Purpose

This packet answers one narrow question only:

- what is the next admissible packet type after choosing `execution_proxy_evidence` as the first clean-checkout replay smoke candidate?

## Governing basis

### Observed

1. `execution_proxy_evidence` is the smallest reviewed manifest-backed claim-bearing chain with focused deterministic tests and a single locked input.
2. `edge_origin_isolation` and `scpe_ri_v1_router_replay` remain valid later candidates, but they are broader first moves.
3. The locally present candidate input artifacts reviewed in this slice are ignored/untracked rather than tracked repo inputs.
4. A clean-checkout replay-smoke claim cannot honestly depend on ignored local research artifacts that are absent from a fresh tracked checkout.

### Inferred

- The next step is **not** direct replay-smoke implementation.
- The next step must instead be a separate pre-code packet for one exact `execution_proxy_evidence` fixture-containment strategy.
- That future packet must choose one bounded reproducibility carrier and reject convenience widening.

### Unverified in this packet

- whether the future carrier should be a tracked minimal fixture, a curated bundle pointer, or another commit-safe mechanism
- whether the eventual implementation belongs primarily in a test file, a helper harness, or a small script/test/docs combination

## Boundary decision

### Current standing conclusion

The selected first clean-checkout replay smoke candidate is:

- **`execution_proxy_evidence`**

But the next admissible follow-up is:

- **a separate pre-code packet for one exact `execution_proxy_evidence` fixture-containment strategy**

This is a candidate-narrowing and sequencing conclusion only. It is **not** approval to implement the smoke yet.

### What the next admissible packet must define

If this line is reopened, the next packet must define at minimum:

- the exact input carrier for `execution_proxy_evidence`
- whether that carrier is tracked directly or referenced through a commit-safe bundle mechanism
- the exact future touched files for the smoke implementation slice
- the exact verification stack for proving clean-checkout reproducibility
- what remains unchanged for the existing script/test/runtime path
- what other candidate chains remain explicitly out of scope

### What must remain out of scope

The next packet must keep the following out of scope unless separately reopened:

- `edge_origin_isolation` replay smoke implementation
- `scpe_ri_v1_router_replay` replay smoke implementation
- repo-wide replay-smoke framework extraction
- CI rollout across multiple chains at once
- new authority claims about runtime quality, promotion, or paper/live readiness

## Hard stop and reopen rule

If a future slice needs any of the following, it must stop and reopen as a separate bounded packet instead of leaning on this document:

- multiple candidate chains in the same implementation slice
- generic replay-smoke helpers or framework extraction
- new bundle/LFS policy beyond one named carrier decision
- any runtime/backtest/config-authority/public-edge change
- any claim that this boundary packet itself authorizes implementation

## Bottom line

The first clean-checkout replay smoke line is now narrowed to `execution_proxy_evidence`, but the repo is not yet ready for an honest implementation because the current input artifact is ignored/untracked. The next correct move is therefore a separate fixture-containment packet for that one chain — not a premature smoke implementation and not a broader automation framework.
