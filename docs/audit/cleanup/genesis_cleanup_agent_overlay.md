# Genesis Cleanup Shard Contract (Agent Instructions)

## Mission

You are part of a **parallel cleanup operation** on the Genesis repository.

The goal is to analyze tool reports and perform **safe code cleanup**.

This is **NOT feature development**.

Only perform actions supported by evidence.

Follow repository SSOT precedence:

1. explicit user request
2. `.github/copilot-instructions.md`
3. `docs/OPUS_46_GOVERNANCE.md`
4. `AGENTS.md`

---

# Governance Principles

1. **Read-only discovery first**
2. **Evidence before deletion**
3. **Small commits**
4. **Respect architecture**
5. **Never create helpers/wrappers**
6. **Prefer moving existing code over creating new code**

---

# Scope (CRITICAL)

You must **ONLY operate inside your assigned shard**.

Do NOT modify files outside your shard.

Allowed actions outside shard:

- read files
- search code
- verify usage

Forbidden:

- editing
- refactoring
- deleting

---

# Tool Profiles (Explicit Reference)

Use these as authoritative references for cleanup tooling:

- Profile definitions and execution order: `tools/config/cleanup_scan_profiles.md`
- Orchestrated implementation entrypoint: `scripts/run/cleanup_orchestrate.ps1`

Mandatory order:

1. Run hard discovery first (`-Mode hard` / `Invoke-HardProfile`).
2. Triage findings (`DELETE` / `KEEP` / `ALLOWLIST` / `REFACTOR`).
3. Run shard-specific profile (`-Mode shard-a|shard-b|shard-c`).

Required tool family per profile:

- **Semgrep**
- **JSCPD**
- **Vulture**
- **Radon (cc)**

The orchestration script maps these tools via:

- `Invoke-HardProfile`
- `Invoke-ShardAProfile`
- `Invoke-ShardBProfile`
- `Invoke-ShardCProfile`

---

# Shards

## Shard A — Scripts

Scope:

scripts/**
scripts/archive/**

Tasks:

- remove duplicate scripts
- move scripts from archive when needed
- add script metadata headers
- consolidate script logic

High probability actions:

- DELETE duplicates
- MOVE scripts out of archive
- MERGE duplicated logic

Do NOT:

- create new scripts if archive contains equivalent logic

---

## Shard B — Tests

Scope:

tests/\*\*

Tasks:

- detect duplicated test logic
- consolidate fixtures
- remove unused helpers
- fix forbidden imports

High probability actions:

- MERGE duplicate test helpers
- REMOVE dead test utilities
- MOVE fixtures to proper locations

Do NOT:

- introduce forbidden layer imports or new import cycles
- create generic helpers like `common.py`

---

## Shard C — Core / Services

Scope:

src/core/**
mcp_server/**

Tasks:

- detect duplicated logic
- remove dead code
- enforce architecture rules

High probability actions:

- DELETE unused functions
- MERGE duplicated implementations
- REMOVE wrapper functions

Do NOT:

- modify architecture boundaries
- introduce new abstractions during cleanup

---

# Decision System

For every finding, classify:

### DELETE

Conditions:

- no usage found via search
- not dynamically registered
- safe after test verification

### KEEP

Conditions:

- code is used
- dynamic usage detected
- architecture dependency

### ALLOWLIST

Conditions:

- tool false positive
- dynamic registry or plugin usage

### REFACTOR

Conditions:

- duplicate implementations
- wrapper functions
- logic drift

---

# Evidence Requirement

Before any deletion run:

rg "<symbol_name>" .

Search for:

- imports
- function calls
- decorators
- registries
- dynamic loading

And verify dynamic references in:

- `registry/**`
- `config/**`
- CLI entrypoints under `scripts/**`
- importlib / getattr / string-based dispatch patterns

If usage found → **KEEP**

---

# Commit Policy

Commits must be **small and atomic**

Batch size guideline:

- 3–10 related deletions per commit.
- Never mix unrelated cleanup types in the same commit.

Examples:

chore(cleanup): remove unused helper functions
chore(cleanup): merge duplicated script logic
chore(cleanup): remove dead imports

Avoid mixed commits.

---

# Pull Request Rules

Each shard produces its own PR.

Branch naming:

feature/cleanup-scripts-audit
feature/cleanup-tests-audit
feature/cleanup-core-audit

PR must include:

- description of changes
- tool findings addressed
- reasoning for deletions

---

# Safety Checks

Before finalizing work:

Run:

pre-commit run --all-files
pytest
ruff check .

If shard touches high-sensitivity paths, also run:

- determinism replay selector
- feature cache invariance selector
- pipeline hash guard selector

If tests fail → rollback change.

---

# Forbidden Actions

You MUST NOT:

- introduce new abstractions
- create new helper modules
- create wrappers
- change architecture boundaries
- auto-fix large sections of code

---

# Cleanup Philosophy

Genesis cleanup must be:

- **surgical**
- **evidence-driven**
- **governance compliant**

Speed is good.

Safety is mandatory.

---

# Output Format

For each resolved finding produce:

Finding:
File:

Decision:
DELETE / KEEP / ALLOWLIST / REFACTOR

Evidence:
(search results)

Action taken:

---

# Expected Outcome

After cleanup:

- fewer duplicates
- fewer scripts
- no dead code
- architecture respected
- repo easier for AI to maintain

---

## Startup Instructions

When launching the cleanup environment:

Window 1 → scripts cleanup
Window 2 → tests cleanup
Window 3 → core cleanup

A fourth role (controller) monitors:

- PR merges
- conflicts
- governance compliance

This usually keeps parallel work stable.
