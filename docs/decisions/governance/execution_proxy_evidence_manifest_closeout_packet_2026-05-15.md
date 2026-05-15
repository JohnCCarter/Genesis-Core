# Execution proxy evidence manifest closeout packet

Date: 2026-05-15
Branch: `feature/editor-worker-orchestrator`
Status: `packet-defined / docs-only / non-authorizing`

This document is a planning/decision artifact in `RESEARCH` and grants no implementation, runtime, config-authority, readiness, paper/live, launch, or promotion authority. It must not be used as approval to begin source, test, or evidence-contract changes without a bounded implementation step.

> Current implementation-status note:
>
> - The candidate framed by this packet has since been landed in a separate bounded evidence slice limited to `scripts/analyze/execution_proxy_evidence.py` and `tests/backtest/test_execution_proxy_evidence.py`.
> - Verification on that later slice was green on touched-file `black --check` / `ruff check` and the focused execution-proxy evidence test file.
> - Executed selectors / outcomes for that later slice:
>   - `black --check scripts/analyze/execution_proxy_evidence.py tests/backtest/test_execution_proxy_evidence.py` → `pass`
>   - `ruff check scripts/analyze/execution_proxy_evidence.py tests/backtest/test_execution_proxy_evidence.py` → `pass`
>   - `pytest tests/backtest/test_execution_proxy_evidence.py -v --tb=short` → `18 passed`
> - This packet remains the historical pre-code framing artifact and does not retroactively authorize wider evidence-framework or runtime work.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/editor-worker-orchestrator`
- **Category:** `tooling`
- **Risk:** `LOW-MED` — why: this slice would touch an evidence-producing analysis script and its tests, but not runtime strategy, config authority, paper/live execution, or public API edges
- **Required Path:** `Smallest admissible governed slice`
- **Lane:** `Research-evidence` — why: the target is a deterministic evidence/closeout surface, not runtime integration
- **Objective:** select the smallest implementation-bearing reproducibility hardening slice that improves claim-bearing closeout without broad governance/process redesign
- **Candidate:** `add an explicit deterministic manifest output to execution_proxy_evidence so repeatable outputs also carry stable input/hash/output inventory metadata`
- **Base SHA:** `66f97acc`
- **Skill Usage:** consulted the repository evidence-closeout spec `.github/skills/slice_evidence_handoff.json` as a checklist aid for exact gates and closeout evidence; this does not create authority or replace required review/gate judgment

### Scope

- **Scope IN:** one bounded evidence-script slice centered on `scripts/analyze/execution_proxy_evidence.py`; focused test updates in `tests/backtest/test_execution_proxy_evidence.py`; exact output-contract change from three outputs to four outputs with one new deterministic manifest file only
- **Scope OUT:** all runtime strategy/backtest engine behavior; all API/config-authority behavior; all generic manifest framework extraction; all new CLI flags; all broad repo-wide evidence policy rewrites; all claims that a single script manifest solves global evidence provenance
- **Expected future changed files:** `scripts/analyze/execution_proxy_evidence.py`, `tests/backtest/test_execution_proxy_evidence.py`
- **Max files touched:** `2` for implementation, plus packet sync docs if landed

### Gates required

For this packet itself:

- targeted docs validation for this file
- manual wording audit that the candidate stays on one existing evidence script only
- manual wording audit that the packet does not imply runtime, promotion, or repo-wide governance authority

### Stop Conditions

- any widening from one evidence script into a repo-wide manifest framework or shared utility extraction
- any runtime strategy/backtest semantics change
- any output that becomes self-referential or non-deterministic because the manifest hashes itself
- any change that requires new CLI flags, environment variables, or output roots beyond the current bounded script contract

## Purpose

This packet answers one narrow question only:

- what is the smallest real reproducibility closeout slice left from the premortem now that claim-bearing docs boundaries already exist?

## Governing basis

### Observed

1. `docs/governance/templates/evidence_claim_header.md` and `docs/governance/runbooks/evidence_claim_adoption.md` already define when claim-bearing notes should record provenance and authority boundaries
2. `scripts/analyze/execution_proxy_evidence.py` already produces deterministic repeatable outputs and an internal determinism audit, and `tests/backtest/test_execution_proxy_evidence.py` already proves same-input repeatability and repeatable CLI outputs
3. unlike stronger replay/evidence scripts such as `scripts/analyze/scpe_ri_v1_router_replay.py`, the execution-proxy evidence script does not currently emit a dedicated manifest recording approved output files, stable non-self output hashes, and an input payload hash in one closeout artifact
4. the current CLI tests therefore prove byte-repeatability, but the output set still lacks one explicit closeout surface that a later claim-bearing note could cite as a compact inventory/hash anchor

### Inferred

- the smallest useful reproducibility hardening is not a new generic evidence framework; it is to upgrade one already-deterministic evidence script with a deterministic manifest output
- this candidate is smaller and safer than building repo-wide helpers because the script already computes non-self output hashes and determinism audit data
- the manifest must remain non-self-referential: it should hash the other approved outputs, not itself

### Unverified in this packet

- the exact manifest filename (`manifest.json` vs a script-specific name) to use for best consistency with existing evidence surfaces
- the final minimum field set beyond input hash, approved output file list, non-self output hashes, and determinism verdict

## Boundary decision

### Current standing conclusion

The smallest remaining reproducibility/evidence hardening candidate should be framed as:

- **add one deterministic manifest output to `execution_proxy_evidence` that records input hash, approved output inventory, and non-self output hashes**

This is a candidate-selection conclusion only. It is **not** approval to edit the script yet.

### Likely future implementation scope

If this candidate is reopened as a real implementation slice, the smallest honest starting scope is:

- `scripts/analyze/execution_proxy_evidence.py`
- `tests/backtest/test_execution_proxy_evidence.py`

### Likely future implementation scope OUT

A future packet for this candidate should keep the following out of scope unless separately reopened:

- generic shared manifest utilities
- other analysis scripts
- runtime/backtest execution semantics
- new output directories or CLI options
- broader docs/governance rewrites beyond minimal indexing/status sync

## What that future implementation slice must define

A future implementation-bearing step for this candidate must define at minimum:

- the exact new output filename
- the exact approved output set after the change
- the exact non-self hash basis used by the manifest
- whether the manifest records the canonical input payload hash
- which existing tests are updated versus which new regression is added
- what must remain unchanged in the evidence payload and summary content

## Expected verification stack for the implementation slice

If the future implementation slice is opened, the expected minimum verification stack should be:

- touched-file `black --check`
- touched-file `ruff check`
- `pytest tests/backtest/test_execution_proxy_evidence.py -v --tb=short`
- focused assertions that the CLI output set is deterministic across repeated runs and now includes the new manifest file only

## Future done criteria for the implementation slice

If the future implementation slice is opened, it should be considered done only if all of the following are true:

- `execution_proxy_evidence` still produces deterministic repeatable outputs for identical input
- the approved output set increases by exactly one deterministic manifest file and nothing else
- the manifest records a stable input hash and stable non-self output hashes
- the manifest does not hash itself or introduce nondeterminism
- existing evidence payload/summary semantics remain unchanged

## Hard stop and reopen rule

If the future slice needs to change any of the following, it must stop and reopen as a separate bounded packet:

- runtime/backtest semantics
- shared utility extraction
- additional scripts beyond `execution_proxy_evidence`
- new CLI contract or flag surface
- broad evidence policy or governance semantics

## Bottom line

The last small premortem reproducibility move should not be a repo-wide framework. It should be a bounded evidence-script hardening step that lets `execution_proxy_evidence` emit one explicit deterministic manifest closeout artifact alongside its already repeatable outputs.
