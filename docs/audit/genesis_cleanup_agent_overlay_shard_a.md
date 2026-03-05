# Genesis Cleanup Overlay — Shard A (Scripts)

## Assigned Shard (LOCKED)

- **Shard:** A — Scripts
- **Branch:** `feature/cleanup-scripts-audit`
- **Branch naming policy (mandatory):** include shard in branch name for every run.
- **Canonical pattern:** `feature/cleanup-<shard>-audit`
- **Allowed edit scope (Scope IN):**
  - `scripts/**`
  - `scripts/archive/**`
- **Forbidden edit scope (Scope OUT):** all other paths
- Outside Scope IN you may only do read/search/usage verification.

Never work from `master` for cleanup execution.

## Mission

You are part of a parallel cleanup operation in Genesis.
This is **cleanup only** (no feature development).
Apply evidence-driven, surgical changes only.

SSOT precedence:

1. explicit user request
2. `.github/copilot-instructions.md`
3. `docs/OPUS_46_GOVERNANCE.md`
4. `AGENTS.md`

## Governance Principles

1. Read-only discovery first
2. Evidence before delete/move
3. Small atomic commits
4. Respect architecture boundaries
5. Never create wrappers/helpers for cleanup
6. Prefer move/merge of existing code

## Task Focus (Shard A)

- remove duplicate scripts
- move scripts from archive when needed
- add/fix script metadata headers if missing
- consolidate duplicated script logic

Do NOT create new scripts when equivalent archived script exists.

## Decision System

For each finding classify as:

- **DELETE**
- **KEEP**
- **ALLOWLIST**
- **REFACTOR**

## Evidence Requirement

Before deletion/move, verify usage and dynamic references.
Minimum checks:

- `rg "<symbol_or_filename>" .`
- imports/calls/entrypoints
- string-based dispatch, registries, config references

If usage exists -> KEEP or REFACTOR (not DELETE).

## Commit Policy

Small, atomic commits only. Examples:

- `chore(cleanup): remove dead script`
- `chore(cleanup): merge duplicate script logic`
- `chore(cleanup): move canonical script from archive`

## PR Rules

- One shard per PR
- PR must include: findings addressed, evidence, deletion/move rationale
- Keep diffs narrowly scoped to Shard A

## Safety Checks

Run before finalizing:

- `pre-commit run --all-files`
- `ruff check .`
- `pytest`
- `scripts/run/cleanup_orchestrate.ps1 -Mode shard-a` (or equivalent profile execution) to run:
  - `semgrep`
  - `jscpd`
  - `vulture`
  - `radon`

Tool profile definitions live in `tools/config/cleanup_scan_profiles.md` and must be treated as mandatory evidence for Shard A cleanup.

If high-sensitivity paths are touched (should normally not happen in Shard A), also run:

- determinism replay selector
- feature cache invariance selector
- pipeline hash guard selector

If checks fail -> rollback minimal risky change and re-verify.

## Forbidden Actions

- introducing new abstractions
- creating wrappers/mapping indirection
- changing architecture boundaries
- broad auto-fix/refactor outside shard

## Output Format per finding

Finding:
File:
Decision: DELETE / KEEP / ALLOWLIST / REFACTOR
Evidence:
Action taken:

Include relevant scan evidence references (semgrep/jscpd/vulture/radon report paths or summarized outcomes) in PR notes.
