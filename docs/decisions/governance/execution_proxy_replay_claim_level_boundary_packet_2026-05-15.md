# Execution proxy replay claim-level boundary packet

Date: 2026-05-15
Branch: `feature/evidence-closeout-pilot`
Status: `decision-recorded / docs-only / non-authorizing`

This document records the current replay claim level for `execution_proxy_evidence` after the tracked-fixture smoke landing. It grants no source, test, runtime, config-authority, paper/live, promotion, or cross-chain replay authority by itself.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via `feature/* -> RESEARCH`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice records wording boundaries after a landed tracked-fixture smoke and does not modify scripts, tests, fixtures, results, or runtime behavior
- **Required Path:** `Quick path / docs-only boundary record`
- **Lane:** `Research-evidence` — why: this packet narrows the honest replay wording for one existing claim-bearing chain without authorizing implementation or label widening elsewhere
- **Objective:** pin the current `execution_proxy_evidence` proof to `fixture-level` and define the minimum future evidence required before stronger replay wording becomes valid
- **Base SHA:** `5d3771edb2ff1448163219180d59b71994c7fab6`
- **Related artifacts:** `docs/analysis/diagnostics/decision_influencing_replay_smoke_candidate_selection_2026-05-15.md`, `docs/decisions/governance/execution_proxy_clean_checkout_replay_smoke_boundary_packet_2026-05-15.md`, `docs/decisions/governance/execution_proxy_fixture_containment_packet_2026-05-15.md`, `registry/fixtures/execution_proxy_baseline_current_minimal.json`, `tests/backtest/test_execution_proxy_evidence.py`

### Scope

- **Scope IN:** this boundary packet; queue sync that records Slice 7 as completed and advances the next admissible slice
- **Scope OUT:** all changes under `scripts/**`; all changes under `tests/**`; all changes under `registry/fixtures/**`; all changes under `results/**`; all changes under `src/**`; all changes under `config/**`; any carrier decision for `edge_origin_isolation`; any carrier decision for SCPE replay surfaces; repo-wide claim-header discipline; ignored-artifact inventory; RI/policy-router candidate language; paper/live, readiness, promotion, or config-authority semantics
- **Max files touched:** `2`

### Gates required

For this packet itself:

- targeted docs validation for this packet and queue sync
- manual wording audit that the current `execution_proxy_evidence` proof stays at `fixture-level`
- manual wording audit that stronger labels are defined as future prerequisites only

## Purpose

This packet answers one narrow question only:

- what replay claim level is actually justified for the current `execution_proxy_evidence` line after the tracked-fixture smoke landing?

## What changed in this slice

- the current `execution_proxy_evidence` line is pinned explicitly to `fixture-level`
- the minimum future prerequisites for `historical-trace-level` and `full-chain clean-checkout-level` wording are recorded in one boundary packet

## What did not change

- no source, test, fixture, results, runtime, or config-authority behavior
- no paper/live, readiness, or promotion semantics
- no replay authority for any other claim-bearing chain

## Governing basis

### Observed

1. The candidate-selection slice chose `execution_proxy_evidence` as the first bounded decision-influencing replay-smoke candidate while recording that the original historical input trace was ignored/untracked.
2. The fixture-containment slice chose one tracked minimal JSON fixture under `registry/fixtures/` as the first commit-safe carrier for this chain.
3. The later implementation slice landed that carrier at `registry/fixtures/execution_proxy_baseline_current_minimal.json` and added focused smoke coverage in `tests/backtest/test_execution_proxy_evidence.py`.
4. The tracked-fixture tests now prove that `execution_proxy_evidence` can run, write its approved outputs, and repeat deterministically from the tracked compact carrier.
5. Those tests operate on the tracked minimal fixture, not on the original historical trace under `results/research/fa_v2_adaptation_off/trace_baseline_current.json`.
6. No current tracked artifact chain proves that a clean checkout can regenerate the full named `execution_proxy_evidence` claim-bearing chain from tracked inputs alone.
7. The script and tests continue to describe the outputs as observational-only and do not attest realized execution price, slippage, latency, or venue behavior.

### Inferred

- The current `execution_proxy_evidence` line supports `fixture-level` wording only.
- It does not yet support `historical-trace-level` wording, because the original historical trace or an explicitly retained equivalent carrier has not been made the tracked reproducibility surface for this chain.
- It does not yet support `full-chain clean-checkout-level` wording, because the repo has not yet proven that a clean checkout can regenerate the full named claim-bearing chain from tracked inputs under an explicit envelope.
- The tracked-fixture success closes one bounded portability gap; it does not close replay portability for other chains or for `execution_proxy_evidence` beyond the compact carrier path.

### Unverified in this packet

- whether a future `historical-trace-level` proof should use the original historical trace, a curated bundle pointer, or another retained commit-safe carrier
- whether pursuing `full-chain clean-checkout-level` for `execution_proxy_evidence` is worth the added carrier and envelope cost
- whether other claim-bearing chains should use the same upgrade path or different carrier decisions

## Boundary decision

### Current standing conclusion

The current justified replay label for `execution_proxy_evidence` is:

- **`fixture-level`**

This means the repo may currently say only that:

- one tracked minimal fixture under `registry/fixtures/` can drive the named `execution_proxy_evidence` script/test path
- that bounded path produces repeatable approved outputs from the tracked compact carrier
- the resulting outputs remain observational-only

This packet does **not** authorize stronger replay wording by citation drift.

### Wording that remains out of bounds now

Until a later packet proves otherwise, do **not** describe the current `execution_proxy_evidence` line as any of the following:

- `historical-trace-level`
- `full-chain clean-checkout-level`
- `clean-checkout replay solved`
- repo-wide replay portability
- portability proof for `edge_origin_isolation` or any SCPE replay surface
- paper/live safety or readiness evidence

### Minimum evidence before `historical-trace-level` wording is allowed

A future bounded slice would need at minimum:

- one exact named historical `execution_proxy_evidence` claim-bearing chain
- the original historical trace, or an explicitly retained equivalent carrier, recorded as the actual reproducibility input for that chain
- reproducible reruns against that retained carrier
- an explicit envelope naming at minimum the relevant `SHA`, `branch`, and the fact that the named chain no longer depends on ignored local-only inputs
- explicit confirmation that broader replay authority, other chains, and paper/live semantics remain out of scope

### Minimum evidence before `full-chain clean-checkout-level` wording is allowed

A future bounded slice would need at minimum:

- a clean checkout that can regenerate the full named `execution_proxy_evidence` claim-bearing chain from tracked inputs or explicitly retained commit-safe carriers
- no hidden dependence on ignored `results/**`, workstation-local caches, or local-only artifact roots
- an explicit regeneration envelope for the named chain rather than a compact-carrier rerun only
- explicit confirmation that the proof applies only to the named chain unless another packet widens scope

## What remains out of scope

This packet does not decide or authorize:

- any carrier decision for `edge_origin_isolation`
- any carrier decision for SCPE replay surfaces
- the repo-wide claim-header discipline queued later in the successor phase
- the ignored-artifact dependency inventory queued later in the successor phase
- any RI/policy-router promotion language
- any paper/live or readiness semantics
- any source, test, or fixture edits

## Hard stop and reopen rule

If a future slice needs any of the following, it must stop and reopen as a separate bounded packet instead of leaning on this document:

- a new carrier decision beyond the current tracked minimal fixture
- source/test/fixture changes
- stronger replay wording for another chain
- repo-wide claim-header or queue-governance policy
- any runtime, config-authority, paper/live, or promotion semantics

## Bottom line

The current `execution_proxy_evidence` reproducibility win is real but narrow. After the tracked-fixture smoke landing, the honest claim level is `fixture-level` only: one tracked compact carrier proves one bounded script/test path with repeatable observational outputs. It does not yet prove historical-trace portability, full-chain clean-checkout replay, or authority for any other claim-bearing chain.
