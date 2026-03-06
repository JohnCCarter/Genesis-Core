# Genesis Cleanup — Hard Rules (Shared Baseline)

## Purpose

This file is the **shared non-negotiable baseline** for all cleanup windows (A/B/C).
Use this together with shard-specific files:

- `genesis_cleanup_agent_overlay_shard_a.md`
- `genesis_cleanup_agent_overlay_shard_b.md`
- `genesis_cleanup_agent_overlay_shard_c.md`

Rule of thumb:

- **Shared baseline = identical in all windows**
- **Shard overlay = scope and task deltas only**

---

## 1) Safety First (Fail-Closed)

1. Cleanup is **not feature development**.
2. Default is **NO BEHAVIOR CHANGE**.
3. If uncertain: **KEEP** (do not delete/refactor).
4. If evidence is incomplete: **STOP** and ask for review.
5. Never edit outside assigned shard scope.

---

## 2) Authority / Precedence

Use this precedence in conflicts:

1. Explicit user request for current task
2. `.github/copilot-instructions.md`
3. `docs/OPUS_46_GOVERNANCE.md`
4. `AGENTS.md`
5. Shard overlay file

---

## 3) Branch & Workspace Isolation

Mandatory:

- Never run cleanup work from `master`.
- Use shard branch naming pattern:
  - `feature/cleanup-scripts-audit`
  - `feature/cleanup-tests-audit`
  - `feature/cleanup-core-audit`
- Use separate worktree per shard.

Recommended mapping:

- Window A -> `Genesis-Core-shard-a`
- Window B -> `Genesis-Core-shard-b`
- Window C -> `Genesis-Core-shard-c`

---

## 4) Allowed vs Forbidden Change Types

Allowed:

- remove dead imports
- remove truly unused private helpers/functions
- merge obvious duplicates
- delete wrappers with proven no-value and no behavior drift

Forbidden:

- introducing new abstractions/helpers during cleanup
- architecture boundary changes
- broad auto-fix across large areas
- wrapper/mapping indirection to avoid moving/deleting legacy code
- mixed-purpose commits

---

## 5) Evidence Requirement (Before DELETE/REFACTOR)

For each candidate symbol/file:

1. Search usages (`imports`, `calls`, decorators, registries)
2. Check dynamic references (`importlib`, `getattr`, string dispatch)
3. Check config/registry/entrypoint links
4. Check nearby tests

If any active usage found -> **KEEP** or **REFACTOR carefully**.

Decision classes:

- `DELETE`
- `KEEP`
- `ALLOWLIST`
- `REFACTOR`

---

## 6) Tooling Guardrails (Damage Minimization)

### Project venv (stable runtime/tooling)

Use repo `.venv` for:

- `pre-commit`, `ruff`, `black`, `pytest`, `bandit`, `detect-secrets`
- plus lightweight Python static checks used in repo workflows

### Isolated tool venv (heavy analyzers)

Use isolated tool environment for analyzers that can cause dependency drift:

- `semgrep`
- optional heavy extras

Current verified absolute paths:

- Semgrep: `C:\Users\fa06662\AppData\Local\DevTools\pytools\Scripts\semgrep.exe`
- JSCPD: `C:\Users\fa06662\AppData\Local\Programs\nodejs\jscpd.cmd`

Do **not** install heavy analyzer stacks into project `.venv` unless explicitly approved.

---

## 7) Execution Sequence (Per Finding)

1. Read-only discovery
2. Evidence capture
3. Decide class (DELETE/KEEP/ALLOWLIST/REFACTOR)
4. Minimal patch
5. Run required gates
6. If gate fails -> rollback minimal risky change
7. Commit atomically

---

## 8) Minimum Gates

Run before finalizing shard changes:

- `pre-commit run --all-files`
- `ruff check .`
- `pytest`

If touching high-sensitivity zones, also run:

- determinism replay selector
- feature cache invariance selector
- pipeline hash/invariant selector

No green gates -> no merge claim.

---

## 9) Commit/PR Discipline

Commits:

- small and atomic
- one cleanup intent per commit
- batch size guideline: **3–10 related deletions per commit**
- never mix unrelated cleanup types in the same commit
- clear message prefix: `chore(cleanup): ...`

PR:

- one shard per PR
- include findings addressed + evidence + rationale
- explicitly state no-behavior-change claim (or exception)

---

## 10) Stop Conditions

Stop immediately if:

- scope is unclear
- dynamic usage cannot be disproven
- candidate touches architecture boundaries
- repeated gate failures without clear minimal fix

Escalate to controller/reviewer with evidence snapshot.

---

## 11) Reporting Template (Copy/Paste)

Finding:
File:
Decision: DELETE / KEEP / ALLOWLIST / REFACTOR
Evidence:
Action taken:
Risk note:
Gate results:

---

## 12) Practical Working Model

Use this baseline in all windows, then add shard overlay rules.

In short:

- **Common hard rules everywhere**
- **Shard-specific scope and task deltas per window**
- **Fail closed when uncertain**
