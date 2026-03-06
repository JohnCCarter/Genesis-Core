# Genesis Refactor Overlay — Shard C (Core/Services)

## Phase Status (LOCKED TRANSITION)

- Cleanup phase for Shard C is completed and must be treated as **historically locked**.
- Cleanup documents remain historical records and must not be rewritten.
- Refactor work starts from updated `master` on a new refactor branch.
- The cleanup branch must not be used for further development work.

Recommended branch flow:

- merge: `feature/cleanup-core-audit` -> `master`
- delete: `feature/cleanup-core-audit`
- create: `feature/refactor-<domain>-c`

## Assigned Shard Scope (LOCKED)

- **Shard:** C — Core/Services
- **Scope IN:**
  - `src/core/**`
  - `mcp_server/**`
- **Scope OUT:** all other paths

Editing outside scope is forbidden.

Allowed actions outside scope:

- read files
- search code
- verify symbol usage and dependencies

## Refactor Mission

This phase allows structural and maintainability improvements while preserving runtime behavior.

Primary goals:

- improve readability and maintainability
- reduce duplication and wrapper indirection
- simplify safe control flow
- normalize naming and helper usage
- consolidate equivalent implementations where behavior parity is proven

## Non-Negotiable Constraints

- Production/runtime behavior must not change.
- Determinism and runtime invariants must be preserved.
- Architecture boundaries must remain intact.
- Scope expansion outside Shard C is forbidden.

## Allowed Refactor Actions (Examples)

- reduce duplicated logic
- simplify complex functions (without semantic drift)
- consolidate duplicated implementations
- remove unnecessary wrappers
- improve naming consistency
- normalize helper utilities
- simplify control flow where safe and provable

## Forbidden Actions

- modifying production behavior
- changing architecture boundaries
- introducing new architecture layers
- introducing new abstractions during refactor without explicit approval
- mixing feature development into refactor batches
- broad automated rewrites without explicit evidence and review

## Governance Principles

- small atomic commits
- explicit rationale for structural changes
- evidence-driven refactor decisions
- fail-closed if impact is unclear
- preserve determinism and runtime invariants

## Validation Requirements

### 1) Hard Validation Gates (merge-blocking)

Run before finalizing refactor work:

- `pre-commit run --all-files`
- `ruff check .`
- `pytest`

If refactor touches sensitive runtime areas, also run:

- determinism replay selector
- feature cache invariance selector
- pipeline hash/invariant selector

### 2) Analysis / Discovery / Verification Tools (non-blocking by default)

Use these tools to identify and prioritize refactor targets:

- Semgrep
- JSCPD
- Vulture
- Radon
- Import-linter

These analysis tools are discovery aids and are **not automatically merge blockers** unless findings are promoted into explicit gate criteria for a specific batch.

## Execution Model

1. Discover candidate via analysis/search.
2. Capture evidence for current behavior and usages.
3. Apply minimal no-behavior-change refactor.
4. Run hard validation gates.
5. Stop and fail closed if parity cannot be demonstrated.

## Reporting Template (Refactor Batch)

- Finding / target:
- File(s):
- Rationale:
- Behavior parity evidence:
- Changes made:
- Gates and outcomes:
- Residual risk:
