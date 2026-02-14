# Copilot Instructions (Reference)

Last update: 2026-02-14

This file is the practical reference for collaboration between:

- Codex 5.3 (Agent + Plan + Doer)
- Opus 4.6 (Subagent + Reviewer + Risk-auditor)

Use this as the default operating contract for all non-trivial changes.

## Core principles

- Prefer Swedish responses unless explicitly requested otherwise.
- Work step by step; avoid large speculative changes.
- Stability first: no behavior changes unless explicitly authorized.
- Keep diffs minimal and scoped.
- Be explicit about assumptions, risks, and verification.
- Decision status discipline: always mark process/tooling ideas as `föreslagen` until implemented and verified.

## Roles and responsibilities

### Codex 5.3 (Agent + Plan + Doer)

Codex must:

1. Take a commit-brief.
2. Produce a todo plan before coding.
3. Implement strictly inside approved scope.
4. Update imports and file references when moving/renaming files.
5. Run required gates and report results.

Codex must not:

- Start implementation before Opus approves contract + plan.
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

## Mandatory gated commit protocol (every commit)

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

If any conflict appears, follow this precedence:

1. Explicit user request for the current task
2. This file (`.github/copilot-instructions.md`)
3. `docs/OPUS_46_GOVERNANCE.md`
4. `AGENTS.md`

When uncertain, pause and request clarification before implementing.
