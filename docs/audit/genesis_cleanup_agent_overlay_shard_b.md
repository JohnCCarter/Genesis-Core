# Genesis Cleanup Overlay — Shard B (Tests)

## Assigned Shard (LOCKED)

- **Shard:** B — Tests
- **Branch:** `feature/cleanup-tests-audit`
- **Branch naming policy (mandatory):** include shard in branch name for every run.
- **Canonical pattern:** `feature/cleanup-<shard>-audit`
- **Allowed edit scope (Scope IN):**
  - `tests/**`
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
5. Never create generic helper wrappers
6. Prefer consolidation of existing fixtures/helpers

## Tooling Reference (Shard B explicit)

Authoritative sources:

- `tools/config/cleanup_scan_profiles.md`
- `scripts/run/cleanup_orchestrate.ps1`

Required flow:

1. Run hard discovery first (`scripts/run/cleanup_orchestrate.ps1 -Mode hard`; implemented in `Invoke-HardProfile`).
2. Triage findings (`DELETE` / `KEEP` / `ALLOWLIST` / `REFACTOR`).
3. Run shard-B profile (`scripts/run/cleanup_orchestrate.ps1 -Mode shard-b`; implemented in `Invoke-ShardBProfile`).

Shard-B tooling (must be explicit in reports):

- **Semgrep**: `scan --config p/python --metrics off --quiet tests`
- **JSCPD**: `--config .jscpd.json --mode weak --silent --exitCode 0 --output reports/.../jscpd/shard-b tests`
- **Vulture**: `python -m vulture --config pyproject.toml tests`
- **Radon (cc)**: `python -m radon cc tests --exclude ".venv,archive,artifacts,cache,data,logs,results,tmp,reports,scripts/archive" --ignore "__pycache__"`

## Task Focus (Shard B)

- detect duplicated test logic
- consolidate fixtures
- remove unused test helpers
- fix forbidden imports

Do NOT create generic helper modules like `common.py`.
Do NOT introduce import cycles or forbidden layer imports.

## Decision System

For each finding classify as:

- **DELETE**
- **KEEP**
- **ALLOWLIST**
- **REFACTOR**

## Evidence Requirement

Before deletion/move, verify real usage and indirect references.
Minimum checks:

- `rg "<symbol_or_fixture>" tests`
- fixture imports and pytest discovery patterns
- conftest/parametrize/dynamic fixture names

If usage exists -> KEEP or REFACTOR (not DELETE).

## Commit Policy

Small, atomic commits only. Examples:

- `chore(cleanup): remove dead test helper`
- `chore(cleanup): merge duplicate fixtures`
- `chore(cleanup): remove redundant imports in tests`

## PR Rules

- One shard per PR
- PR must include: findings addressed, evidence, rationale
- Keep diffs narrowly scoped to Shard B

## Safety Checks

Run before finalizing:

- `pre-commit run --all-files`
- `ruff check .`
- `pytest`

If high-sensitivity runtime paths are touched indirectly, add:

- determinism replay selector
- feature cache invariance selector
- pipeline hash guard selector

If checks fail -> rollback minimal risky change and re-verify.

## Forbidden Actions

- introducing runtime behavior changes via tests-only cleanup
- creating wrappers/new abstractions
- changing architecture boundaries
- broad auto-fix/refactor outside shard

## Output Format per finding

Finding:
File:
Decision: DELETE / KEEP / ALLOWLIST / REFACTOR
Evidence:
Action taken:
