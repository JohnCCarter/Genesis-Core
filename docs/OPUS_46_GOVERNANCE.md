# Opus 4.6 Governance (Reference)

Last update: 2026-02-14

This document defines how Codex53 and Opus46 collaborate in this repository.

Canonical source of truth is `.github/copilot-instructions.md`.

## Roles

- **Codex53**: Agent + Plan + Doer (implementation)
- **Opus46**: Subagent + Reviewer + Risk-auditor (pre-review, diff-audit, veto)

## Mandatory gated commit protocol

### 1) Commit contract (before work)

Required fields:

- Category: `security | docs | tooling | refactor(server) | api | obs`
- Scope IN: exact allowed file list
- Scope OUT: explicit exclusions
- Constraints: default `NO BEHAVIOR CHANGE`
- Done criteria: concrete gates + manual checks (if relevant)

Default constraints:

- Do not change defaults, sorting, numerics, seeds, cache keys.
- Do not change endpoint paths, status codes, response shapes.
- Do not change env/config interpretation or config authority paths.

### 2) Opus46 plan review (pre-code)

Opus46 approves or blocks before any implementation starts.

### 3) Codex53 implementation

Codex53 executes only approved scope with minimal diff.

### 4) Opus46 diff-audit (post-code)

Opus46 verifies no unintended behavior changes or contract drift.

### 5) Gates -> commit

Commit only when defined gates are green.

## Communication policy

- Mark proposals as `föreslagen` until actually implemented.
- Use `införd` only after implementation is verified in this repository.
- Do not claim blocking CI/pre-commit is active unless configuration exists and is validated.

## High-sensitivity zones

- `src/core/strategy/*`
- `src/core/backtest/*`
- `src/core/optimizer/*`
- runtime/config authority paths
- paper/live execution and API edges
