# Edge-origin isolation manifest closeout packet

Date: 2026-05-15
Branch: `feature/evidence-closeout-pilot`
Status: `packet-defined / docs-only / non-authorizing`

This document is a planning/decision artifact in `RESEARCH` and grants no implementation, runtime, config-authority, readiness, paper/live, launch, or promotion authority. It must not be used as approval to begin source, test, or evidence-contract changes without a bounded implementation step.

> Current implementation-status note:
>
> - The candidate framed by this packet has since been landed in a separate bounded evidence slice limited to `scripts/analyze/edge_origin_isolation.py` and `tests/backtest/test_edge_origin_isolation.py`.
> - Verification on that later slice was green on touched-file `black --check` / `ruff check` and the focused edge-origin isolation test file.
> - Executed selectors / outcomes for that later slice:
>   - `black --check scripts/analyze/edge_origin_isolation.py tests/backtest/test_edge_origin_isolation.py` → `pass`
>   - `ruff check scripts/analyze/edge_origin_isolation.py tests/backtest/test_edge_origin_isolation.py` → `pass`
>   - `pytest tests/backtest/test_edge_origin_isolation.py -v --tb=short` → `7 passed`
> - This packet remains the historical pre-code framing artifact and does not retroactively authorize wider evidence-framework or runtime work.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/evidence-closeout-pilot`
- **Category:** `tooling`
- **Risk:** `LOW-MED` — why: this slice would touch one evidence-producing analysis script and its tests, but not runtime strategy, config authority, paper/live execution, or public API edges
- **Required Path:** `Smallest admissible governed slice`
- **Lane:** `Research-evidence` — why: the target is a deterministic evidence/closeout surface, not runtime integration
- **Objective:** select the smallest implementation-bearing reproducibility hardening slice that improves claim-bearing closeout for Phase 10 edge-origin outputs without broad framework or governance redesign
- **Candidate:** `add an explicit deterministic manifest output to edge_origin_isolation so repeatable Phase 10 outputs also carry stable input/hash/output inventory metadata`
- **Base SHA:** `547005d2`
- **Skill Usage:** consulted the repository evidence-closeout spec `.github/skills/slice_evidence_handoff.json` as a checklist aid for exact gates and closeout evidence; this does not create authority or replace required review/gate judgment

### Scope

- **Scope IN:** one bounded evidence-script slice centered on `scripts/analyze/edge_origin_isolation.py`; focused test updates in `tests/backtest/test_edge_origin_isolation.py`; this packet as the docs-first framing artifact; exact output-contract change from ten outputs to eleven outputs with one new deterministic manifest file only
- **Scope OUT:** all runtime strategy/backtest engine behavior; all API/config-authority behavior; all generic manifest framework extraction; all other analysis scripts; all new CLI flags or output roots; all broad repo-wide evidence policy rewrites; all claims that a single script manifest solves global evidence provenance
- **Expected future changed files:** `docs/decisions/governance/edge_origin_isolation_manifest_closeout_packet_2026-05-15.md`, `scripts/analyze/edge_origin_isolation.py`, `tests/backtest/test_edge_origin_isolation.py`
- **Max files touched:** `3`

### Gates required

For this packet itself:

- targeted docs validation for this file
- manual wording audit that the candidate stays on one existing evidence script only
- manual wording audit that the packet does not imply runtime, promotion, or repo-wide governance authority

## Purpose

This packet answers one narrow question only:

- what is the smallest next evidence-closeout slice after the execution-proxy manifest closeout?

## Governing basis

### Observed

1. `scripts/analyze/edge_origin_isolation.py` already produces deterministic repeatable outputs and an internal determinism audit, and `tests/backtest/test_edge_origin_isolation.py` already proves same-seed repeatability and CLI output generation
2. the script already computes non-self output hashes and a manifest-style aggregate hash, but it does not yet emit a dedicated manifest output that a later claim-bearing note could cite directly
3. unlike `scripts/analyze/execution_proxy_evidence.py`, the Phase 10 edge-origin script still leaves the approved output inventory and input-hash provenance implicit across multiple files
4. `edge_origin_isolation` consumes two locked inputs (`baseline_current` and `adaptation_off`), so any closeout manifest should record both input payload hashes as part of the compact provenance surface

### Inferred

- the smallest useful reproducibility hardening is not a shared manifest framework; it is to upgrade one already-deterministic evidence script with one deterministic manifest output
- this candidate is smaller and safer than touching multiple evidence scripts because the script already contains the required non-self hashing seams
- the manifest must remain non-self-referential: it should hash the other approved outputs, not itself

### Unverified in this packet

- the exact final field names for the two input hashes
- the minimum useful metadata beyond input hashes, `seed`, `shuffle_iterations`, approved output file list, non-self output hashes, and determinism verdict

## Boundary decision

### Current standing conclusion

The smallest next reproducibility/evidence hardening candidate should be framed as:

- **add one deterministic manifest output to `edge_origin_isolation` that records baseline/adaptation input hashes, fixed seed parameters, approved output inventory, and non-self output hashes**

This is a candidate-selection conclusion only. It is **not** approval to edit the script yet.

### Likely future implementation scope

If this candidate is reopened as a real implementation slice, the smallest honest starting scope is:

- `scripts/analyze/edge_origin_isolation.py`
- `tests/backtest/test_edge_origin_isolation.py`

### Likely future implementation scope OUT

A future packet for this candidate should keep the following out of scope unless separately reopened:

- generic shared manifest utilities
- `scripts/analyze/execution_proxy_evidence.py`
- other analysis scripts
- runtime/backtest execution semantics
- new output directories or CLI options
- broader docs/governance rewrites beyond minimal packet/status sync

## What that future implementation slice must define

A future implementation-bearing step for this candidate must define at minimum:

- the exact new output filename
- the exact approved output set after the change
- the exact non-self hash basis used by the manifest
- whether the manifest records canonical hashes for both locked input payloads
- which existing tests are updated versus which new regression is added
- what must remain unchanged in the existing Phase 10 payload and summary content

## Expected verification stack for the implementation slice

If the future implementation slice is opened, the expected minimum verification stack should be:

- touched-file `black --check`
- touched-file `ruff check`
- `pytest tests/backtest/test_edge_origin_isolation.py -v --tb=short`
- focused assertions that the CLI output set is deterministic across repeated runs and now includes the new manifest file only

## Future done criteria for the implementation slice

If the future implementation slice is opened, it should be considered done only if all of the following are true:

- `edge_origin_isolation` still produces deterministic repeatable outputs for identical locked inputs and identical seed/shuffle parameters
- the approved output set increases by exactly one deterministic manifest file and nothing else
- the manifest records stable hashes for both locked inputs and stable non-self output hashes
- the manifest does not hash itself or introduce nondeterminism
- existing Phase 10 payload and summary semantics remain observational-only

## Hard stop and reopen rule

If the future slice needs to change any of the following, it must stop and reopen as a separate bounded packet:

- runtime/backtest semantics
- shared utility extraction
- additional scripts beyond `edge_origin_isolation`
- new CLI contract or flag surface
- broad evidence policy or governance semantics

## Bottom line

The next small evidence-closeout move should not be a repo-wide framework. It should be a bounded evidence-script hardening step that lets `edge_origin_isolation` emit one explicit deterministic manifest closeout artifact alongside its already repeatable Phase 10 outputs.
