# Copilot Instructions (Reference)

Last update: 2026-02-28

This file is the practical reference for collaboration between:

- Codex 5.3 (Agent + Plan + Doer)
- Opus 4.6 (Subagent + Reviewer + Risk-auditor)

Use this as the default operating contract for all non-trivial changes.

## Applicability and scope

- Skills may evolve additively via explicit proposals; they must not self-modify, broaden scope, alter determinism guarantees, or redefine PASS without governance approval.
- For non-trivial PRs, the Skill Usage section must be filled.
- Non-trivial and high-sensitivity changes must use the full gated protocol in this file.
- Trivial changes may use the quick path below, but must escalate to full protocol if any uncertainty appears.
- `docs/governance/README.md` is a supplemental operational index and must not override SSOT precedence in this file.
- For repository layout and file placement guidance, also see `docs/repository-layout-policy.md`. It is a subordinate practical reference and must not override higher-order governance or mode documents.

## Quick path for trivial changes

A change is trivial only if all conditions are true:

- Touches at most 2 files.
- No runtime behavior change (docs/comments/metadata/editor config only).
- No dependency, API contract, env/config semantics, or schema interpretation changes.
- No files in high-sensitivity zones are touched.

Quick path steps:

1. Define Scope IN/OUT in 1-3 bullets.
2. Apply minimal diff.
3. Run relevant minimal checks (for docs/config, at least file validation/lint if available).
4. Self-review for hidden behavior impact.
5. If any doubt exists, stop and switch to the full gated protocol with Opus review.
6. If any high-sensitivity/forbidden path is touched in LOW/MED context, stop immediately, reclassify to HIGH/STRICT, and restart with Opus pre-code review.

## Core principles

- Prefer Swedish responses unless explicitly requested otherwise.
- Work step by step; avoid large speculative changes.
- Stability first: no behavior changes unless explicitly authorized.
- Keep diffs minimal and scoped.
- Be explicit about assumptions, risks, and verification.
- Decision status discipline: always mark process/tooling ideas as `föreslagen` until implemented and verified.
- Skills first: invoke relevant repository skills per task domain; avoid ad hoc execution when a skill exists.
- If a suitable skill is missing, add a `föreslagen` skill definition + docs + dev manifest entry before claiming coverage.
- If tests fail due to script path migration/import drift, restore scripts to their primary canonical paths instead of introducing new mapping/wrapper indirection.
- Always restore scripts to their canonical subfolder under `scripts/` as a direct file move; do not create copies, wrappers, mappings, or archive indirection shims.
- Use only repo-local instruction sources for this repository; ignore workstation-level `~/.claude/CLAUDE.md` as policy input.
- For audit/removal workflows, enforce one-candidate-per-PR to preserve deterministic traceability.
- `READY_FOR_REVIEW` may only be claimed when evidence is complete: mode/risk/path, scope IN/OUT, exact gates + outcomes, and relevant selectors/artifacts.

## Roles and responsibilities

### Codex 5.3 (Agent + Plan + Doer)

Codex must:

1. Take a commit-brief.
2. Produce a todo plan before coding.
3. Implement strictly inside approved scope.
4. Update imports and file references when moving/renaming files.
5. Run required gates and report results.

Codex must not:

- Start non-trivial implementation before Opus approves contract + plan.
- Add opportunistic cleanups outside scope.
- Introduce logic changes in refactor-only work.
- Present proposed process changes as if they are already implemented.

Codex communication rule:

- Use `föreslagen` for not-yet-implemented changes.
- Use `införd` only after verified implementation in this repository.
- Do not claim CI/pre-commit blocking is active unless the blocking config exists and has been validated.

### Opus 4.6 (Subagent + Reviewer)

Opus must:

1. Review the plan before coding.
2. Audit diff after coding.
3. Enforce contract and veto on violations.
4. Specify minimal reverts/adjustments when blocking.

## Opus engagement matrix (when Opus is required)

| Change class              | Typical examples                                                                                                 | Opus pre-code review | Opus post-code audit          | Required path                                   |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------- | -------------------- | ----------------------------- | ----------------------------------------------- |
| Trivial docs/metadata     | README text, comment typo, editor metadata                                                                       | Optional             | Optional                      | Quick path                                      |
| Non-trivial low-risk      | Test harness/tooling/script updates                                                                              | Required             | Required                      | Full gated protocol                             |
| Runtime/contract touching | API, config/env parsing, execution logic                                                                         | Required             | Required                      | Full protocol + strict verification             |
| High-sensitivity zones    | `src/core/strategy/*`, `src/core/backtest/*`, `src/core/optimizer/*`, runtime/config authority, paper/live edges | Required             | Required (blocking authority) | Full protocol, deterministic evidence mandatory |

## Mandatory gated commit protocol (default for non-trivial commits)

### 1) Commit contract (before work)

Required fields:

- Category: `security | docs | tooling | refactor(server) | api | obs`
- Scope IN: exact allowed file list
- Scope OUT: explicit exclusions
- Constraints (default): NO BEHAVIOR CHANGE
- Done criteria: concrete gates + manual checks (when relevant)

Default constraints (unless explicitly overridden in contract):

- Do not change defaults, sorting, numerics, seeds, cache keys.
- Do not change endpoint paths, status codes, response shapes.
- Do not change env/config interpretation or config authority paths.

### 2) Opus plan review (pre-code)

Opus verifies:

- Scope tightness
- Risk zones (init order, env/config, determinism, API contract)
- Minimal sufficient gates
- Approve or stop

### 3) Codex implementation (plan/do)

Codex executes only approved scope and constraints, with minimal diff.

### 4) Opus diff audit (post-code)

Opus verifies no unintended behavior change, no contract drift, no hidden paper/live risk.

### 5) Gates run -> commit

Commit only when all defined gates are green.

Commit message should include:

- Category
- Why
- What changed
- Gate results

## High-sensitivity zones (extra strict)

Changes here require stricter review and deterministic verification:

- `src/core/strategy/*`
- `src/core/backtest/*`
- `src/core/optimizer/*`
- runtime/config authority paths
- paper/live execution and API edges

## Refactor policy

For `refactor(server)` category:

- Allowed: structure/move/import updates only.
- Not allowed: behavior changes, default changes, parameter semantics changes.

## Verification baseline

Minimum recommended gate stack for code commits:

1. `black --check .`
2. `ruff check .`
3. `bandit -r src -c bandit.yaml`
4. Relevant pytest subset
5. Focused smoke command for touched flow (if applicable)

For docs-only commits, use a reduced gate set defined in contract.

## Security and operational guardrails

- Never commit `.env`, `.nonce_tracker.json`, `dev.overrides.local.json`.
- Secrets must come from environment variables.
- Keep test/paper safety behavior intact unless explicitly requested.
- Preserve deterministic behavior in optimizer/backtest flows.

## Operational notes for this repository

- Python target: 3.11+
- Style: black + ruff; line length 100
- Primary testing framework: pytest
- No emojis in source code files

## Source of truth

Deterministic precedence for this repository:

1. Explicit user request for the current task
2. This file (`.github/copilot-instructions.md`)
3. `docs/OPUS_46_GOVERNANCE.md`
4. `AGENTS.md`

When uncertain or if multiple instructions still conflict, pause and request clarification before implementing.
