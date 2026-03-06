# Genesis Refactor Overlay — Shard A (Scripts)

## Assigned Shard (LOCKED)

- **Shard:** A — Scripts
- **Phase:** Refactor (post-cleanup)
- **Allowed edit scope (Scope IN):**
  - `scripts/**` (includes archived subpaths under `scripts/`)
- **Forbidden edit scope (Scope OUT):** all other paths
- Outside Scope IN you may only:
  - read files
  - search code
  - verify usage

Never perform refactor execution from `master`.

## Phase Status

- Cleanup phase is **completed and locked**.
- Refactor baseline for this phase is defined in:
  - `docs/audit/refactor/hard_rules_refactor.md`
- Cleanup governance documents are historical records and must remain unchanged:
  - `docs/audit/cleanup/hard_rules_cleanup.md`
  - `docs/audit/cleanup/Genesis_cleanup_agent_overlay.md`
  - `docs/audit/cleanup/genesis_cleanup_agent_overlay_shard_a.md`
- This phase focuses on **maintainability improvements** with preserved runtime behavior.
- Architecture boundaries must remain intact.

## Mission

You are part of the parallel refactor phase in Genesis.
This is **refactor only** (no feature development).
Apply evidence-driven, structural improvements only.

SSOT precedence:

1. explicit user request
2. `.github/copilot-instructions.md`
3. `docs/OPUS_46_GOVERNANCE.md`
4. `AGENTS.md`

## Governance Principles

1. Read-only discovery first
2. Evidence before structural change
3. Small atomic commits
4. Explicit rationale for each structural change
5. Respect architecture boundaries
6. Fail closed if impact is unclear
7. Production behavior must not change
8. Preserve determinism and runtime invariants

## Shard Scope Map (Unchanged)

- **Shard A:** `scripts/**`, `scripts/archive/**`
- **Shard B:** `tests/**`
- **Shard C:** `src/core/**`, `mcp_server/**`

This overlay applies to **Shard A** only.

## Refactor Focus (Shard A)

Primary goals:

- reduce duplication
- simplify complex functions
- improve naming consistency
- consolidate duplicated implementations and utilities
- remove unnecessary wrappers
- improve readability and maintainability
- simplify control flow where safe

Allowed examples (when behavior parity is preserved):

- extract repeated script-local logic into existing canonical locations
- normalize script structure and naming consistency
- remove structural noise and dead branches after usage verification
- tighten function boundaries and improve code organization

## Decision System

For each finding classify as:

- **REFACTOR**
- **KEEP**
- **ALLOWLIST**
- **DELETE** (only with strong evidence and no behavior impact)

## Evidence Requirement

Before any structural change, verify usage and dynamic references.
Minimum checks:

- `rg "<symbol_or_filename>" .`
- imports/calls/entrypoints
- string-based dispatch, registries, config references
- script invocation points and test coverage impact

If impact is uncertain -> KEEP and escalate for review.

## Validation Model (Important Distinction)

### 1) Required validation gates (merge-blocking)

Run before finalizing refactor work:

- `pre-commit run --all-files`
- `ruff check .`
- `pytest`

If high-sensitivity paths are touched, also run:

- determinism replay selector
- feature cache invariance selector
- pipeline hash guard selector

### 2) Analysis / discovery / verification tools (situational, non-identical blockers)

Use these tools to identify and validate refactor targets:

- Semgrep
- JSCPD
- Vulture
- Radon
- Import-linter

These tools inform target selection and risk analysis; they are **not all equivalent merge blockers** by default.

## Commit Policy

Small, atomic commits only.

- keep refactor commits narrowly scoped
- never mix feature development with refactor commits
- include explicit rationale in commit message/PR notes

Example commit prefixes:

- `refactor(scripts): simplify duplicated flow in <module>`
- `refactor(scripts): normalize structure for maintainability`

## PR Rules

- One shard per PR
- PR must include:
  - refactor targets addressed
  - rationale for structural changes
  - evidence for behavior preservation
  - validation gate outcomes
- Keep diffs narrowly scoped to Shard A

## Forbidden Actions

- modifying production behavior
- changing architecture boundaries
- introducing new architecture layers
- introducing new abstractions during refactor
- expanding scope outside shard boundaries
- mixing feature development into refactor work
- broad automated rewrites without evidence

## Output Format per finding

Finding:
File:
Decision: REFACTOR / KEEP / ALLOWLIST / DELETE
Rationale:
Evidence:
Action taken:
Behavior parity note:

Include relevant analysis evidence references (Semgrep/JSCPD/Vulture/Radon/Import-linter outputs when used) in PR notes.
