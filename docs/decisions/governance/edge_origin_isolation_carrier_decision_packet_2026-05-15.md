# Edge-origin isolation carrier decision packet

Date: 2026-05-15
Branch: `feature/evidence-closeout-pilot`
Status: `decision-recorded / docs-only / non-authorizing`

This document records the exact commit-safe carrier strategy to use if the `edge_origin_isolation` replay/claim-bearing portability line is reopened. It grants no source, test, runtime, config-authority, paper/live, promotion, or cross-chain replay authority by itself.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via `feature/* -> RESEARCH`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice chooses one bounded carrier strategy only and does not modify scripts, tests, fixtures, results, or runtime behavior
- **Required Path:** `Quick path / docs-only pre-code packet`
- **Lane:** `Research-evidence` — why: the packet narrows one reproducibility carrier for one existing claim-bearing chain without authorizing implementation
- **Objective:** choose the smallest admissible commit-safe carrier for a future `edge_origin_isolation` replay/claim-bearing portability slice
- **Base SHA:** `fa26bd78bc4dcb75f859599c5f53fdd91eb51a3f`
- **Related artifacts:** `docs/analysis/diagnostics/next_phase_verkstad_queue_2026-05-15.md`, `docs/analysis/diagnostics/decision_influencing_replay_smoke_candidate_selection_2026-05-15.md`, `docs/decisions/governance/execution_proxy_replay_claim_level_boundary_packet_2026-05-15.md`, `docs/decisions/governance/edge_origin_isolation_manifest_closeout_packet_2026-05-15.md`, `docs/analysis/diagnostics/edge_origin_isolation_manifest_claim_pilot_2026-05-15.md`, `tests/backtest/test_edge_origin_isolation.py`

### Scope

- **Scope IN:** this carrier-decision packet; queue sync that records Slice 8 as completed and advances the next admissible slice
- **Scope OUT:** all changes under `scripts/**`; all changes under `tests/**`; all changes under `registry/fixtures/**`; all changes under `results/**`; all changes under `src/**`; all changes under `config/**`; any carrier decision for SCPE replay surfaces; repo-wide claim-header discipline; ignored-artifact inventory; RI/policy-router candidate language; paper/live, readiness, promotion, or config-authority semantics
- **Max files touched:** `2`

### Gates required

For this packet itself:

- targeted docs validation for this packet and queue sync
- manual wording audit that the carrier decision stays exact and chain-local to `edge_origin_isolation`
- manual wording audit that the packet does not imply implementation, replay portability for other chains, or authority drift from ignored results roots

## Purpose

This packet answers one narrow question only:

- what exact commit-safe carrier should a future `edge_origin_isolation` replay/claim-bearing portability slice use?

## What changed in this slice

- the current `edge_origin_isolation` line now has one explicit first carrier strategy instead of inheriting replay confidence by analogy from `execution_proxy_evidence`
- the repo now records what the next honest implementation slice would use if this line is reopened

## What did not change

- no source, test, fixture, results, runtime, or config-authority behavior
- no paper/live, readiness, or promotion semantics
- no replay authority for SCPE or any other claim-bearing chain

## Governing basis

### Observed

1. The replay-smoke candidate-selection slice recorded `edge_origin_isolation` as a credible later candidate, but broader than `execution_proxy_evidence`, and also recorded that the currently inspected historical inputs remained ignored/untracked under `results/research/**`.
2. The `edge_origin_isolation` manifest-closeout implementation has already landed, so the chain now emits deterministic manifest-backed outputs and focused tests prove repeatability and CLI smoke.
3. The `edge_origin_isolation` manifest claim pilot records one fresh observational artifact root, but that root is also under ignored `results/research/**` and the note preserves the historical dirty/untracked framing of that slice.
4. `scripts/analyze/edge_origin_isolation.py` accepts explicit baseline/adaptation input paths and an optional output directory rather than requiring a special runtime-only location.
5. `tests/backtest/test_edge_origin_isolation.py` already proves deterministic behavior from compact synthetic payloads and repeatable CLI output generation using temporary input files.
6. `.gitignore` broadly excludes `results/**`, so treating the historical Phase 10 traces or the manifest-pilot output root as the commit-safe replay carrier would fight current repo policy instead of fitting it.
7. The adjacent `execution_proxy_evidence` carrier and claim-level slices were explicitly chain-local and do not authorize replay portability by inheritance for `edge_origin_isolation`.

### Inferred

- The current historical traces and manifest-pilot output root are useful citation surfaces, but they are not honest commit-safe carriers for clean-checkout portability.
- The smallest admissible first carrier is **one tracked minimal JSON fixture pair under `registry/fixtures/`**, because this chain needs two inputs and the script/test surface already proves that compact deterministic payloads can drive the analysis path.
- A summary-only citation carrier is weaker than the needed replay carrier because it can support evidence citation without supporting rerun-capable portability.
- The future implementation slice can likely stay bounded to one tracked baseline fixture, one tracked adaptation fixture, and focused additions in `tests/backtest/test_edge_origin_isolation.py`.
- `scripts/analyze/edge_origin_isolation.py` should remain **OUT** for the first carrier-implementation slice unless inspection proves a strictly necessary helper seam.

### Unverified in this packet

- the exact future filenames for the tracked minimal fixture pair under `registry/fixtures/`
- whether a later stronger `historical-trace-level` or `full-chain clean-checkout-level` claim for this chain would still require a retained historical-trace carrier beyond the minimal fixture pair
- whether the first implementation slice can stay entirely inside tracked fixtures plus focused tests without any script changes

## Boundary decision

### Current standing conclusion

If the `edge_origin_isolation` replay/claim-bearing portability line is reopened, the exact first carrier strategy should be:

- **one tracked minimal JSON fixture pair under `registry/fixtures/`**

This is a carrier-selection conclusion only. It is **not** approval to implement the replay slice yet.

### Likely future implementation scope

If this line is reopened as a real implementation slice, the smallest honest starting scope is likely:

- one tracked `baseline_current` minimal fixture under `registry/fixtures/`
- one tracked `adaptation_off` minimal fixture under `registry/fixtures/`
- focused additions in `tests/backtest/test_edge_origin_isolation.py`

### Likely future implementation scope OUT

A future implementation slice should keep the following out of scope unless separately reopened:

- `scripts/analyze/edge_origin_isolation.py`
- `results/research/**`
- the historical `phase10_edge_origin_isolation` root and the manifest-pilot output root
- `execution_proxy_evidence`
- SCPE replay surfaces
- repo-wide replay helpers or framework extraction

## Hard stop and reopen rule

If the future implementation slice discovers any of the following, it must stop and reopen as a separate bounded packet:

- the minimal tracked fixture pair cannot honestly preserve the needed `edge_origin_isolation` contract
- the carrier must become large or historical enough to justify a retained bundle or other archival mechanism
- the script itself needs behavior changes beyond simple smoke/test reuse
- multiple replay chains need to be solved together

## Bottom line

`edge_origin_isolation` should not inherit replay portability from `execution_proxy_evidence`, and it should not rely on ignored `results/research/**` roots as its first commit-safe carrier. The smallest admissible first carrier is one tracked minimal JSON fixture pair under `registry/fixtures/`, paired with focused test-level smoke coverage and no broader replay-framework widening.
