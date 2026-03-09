# Genesis Refactor — Hard Rules (Shared Baseline)

## Purpose

This file is the shared non-negotiable baseline for all **refactor windows** (A/B/C).
Use it together with shard-specific refactor overlays under `docs/audit/refactor/`.

Rule of thumb:

- Shared baseline = identical in all refactor windows
- Shard overlay = scope and task deltas only

## 1) Safety first (fail-closed)

1. Refactor is not feature development.
2. Default is **NO BEHAVIOR CHANGE**.
3. If uncertain: **KEEP** (do not alter behavior-sensitive paths).
4. If evidence is incomplete: **STOP** and request review.
5. Never edit outside approved scope.

## 2) Authority / precedence

Use this precedence in conflicts:

1. Explicit user request for current task
2. `.github/copilot-instructions.md`
3. `docs/OPUS_46_GOVERNANCE.md`
4. `AGENTS.md`
5. Refactor overlay file(s)

## 3) Branch and workspace discipline

Mandatory:

- Never run refactor execution from `master`.
- Keep one shard per branch/PR when doing multi-shard work.
- Keep branch names shard-explicit when possible.

## 4) Allowed vs forbidden change types

Allowed (with parity evidence):

- structural simplification
- duplicate reduction
- naming/organization clarity
- dead-branch removal after usage verification

Forbidden:

- production behavior changes without explicit exception
- architecture boundary changes
- broad auto-rewrites without evidence
- mixed-purpose commits

## 5) Evidence requirement (before REFACTOR/DELETE)

For each candidate symbol/file:

1. Search usages (imports, calls, decorators, registries)
2. Check dynamic references (`importlib`, `getattr`, string dispatch)
3. Check config/registry/entrypoint links
4. Check nearby tests and assertions likely to lock behavior

If active usage/impact is uncertain -> KEEP and escalate.

## 6) Validation model

### Required validation gates (merge-blocking)

- `pre-commit run --all-files`
- `ruff check .`
- `pytest`

If touching high-sensitivity zones, also run:

- determinism replay selector
- feature cache invariance selector
- pipeline invariant/hash guard selector

### Discovery tools (situational)

These inform target selection and risk analysis but are not equivalent merge blockers by default:

- Semgrep
- JSCPD
- Vulture
- Radon
- Import-linter

## 7) Execution sequence (per finding)

1. Read-only discovery
2. Evidence capture
3. Decision class (`REFACTOR`, `KEEP`, `ALLOWLIST`, `DELETE`)
4. Minimal patch
5. Run required gates
6. If gate fails: rollback minimal risky change
7. Commit atomically

## 8) Commit and PR discipline

Commits:

- small and atomic
- one refactor intent per commit
- clear rationale in message/body

PR:

- one shard per PR
- include findings addressed + parity rationale + gate outcomes
- state explicitly whether default behavior remains unchanged

## 9) Stop conditions

Stop immediately if:

- scope is unclear
- dynamic usage cannot be disproven
- candidate touches architecture boundaries unexpectedly
- repeated gate failures without clear minimal fix

Escalate with evidence snapshot.

## 10) Reporting template

Finding:
File:
Decision: REFACTOR / KEEP / ALLOWLIST / DELETE
Rationale:
Evidence:
Action taken:
Behavior parity note:
Gate results:
