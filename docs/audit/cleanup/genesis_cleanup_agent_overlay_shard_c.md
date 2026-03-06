# Genesis Cleanup Overlay — Shard C (Core/Services)

## Assigned Shard (LOCKED)

- **Shard:** C — Core/Services
- **Branch:** `feature/cleanup-core-audit`
- **Scope IN:**
  - `src/core/**`
  - `mcp_server/**`
- **Scope OUT:** all other paths

## Tooling References (mandatory)

Källor för vilka verktyg som gäller och hur de körs:

1. `tools/config/cleanup_scan_profiles.md`
   - Definierar hard + shard-profiler.
   - Innehåller **Shard C profile (core/services)** med Semgrep, JSCPD, Vulture, Radon.

2. `scripts/run/cleanup_orchestrate.ps1`
   - Orchestrated entrypoint (`-Mode hard|shard-a|shard-b|shard-c|all`).
   - Implementerar `Invoke-HardProfile` och `Invoke-ShardCProfile` med faktisk körordning.

Använd script-entrypoint ovan som SSOT vid körning, inte ad-hoc kommandon.

## Required Execution Order

1. `hard` discovery
2. triage (`DELETE | KEEP | ALLOWLIST | REFACTOR`)
3. `shard-c` scope-verifiering
4. no-behavior-change default

## Preferred Commands

- `scripts/run/cleanup_orchestrate.ps1 -Mode hard`
- `scripts/run/cleanup_orchestrate.ps1 -Mode shard-c`

## Safety Checks

- `pre-commit run --all-files`
- `ruff check .`
- relevanta pytest-selectors för berörd scope

## Commit Batch Guideline

- 3–10 related deletions per commit.
- Never mix unrelated cleanup types in the same commit.
