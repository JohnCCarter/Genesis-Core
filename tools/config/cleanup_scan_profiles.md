# Cleanup Scan Profiles

This file defines safe command profiles for **hard discovery** and **shard execution**.

## Preferred execution entrypoint (orchestrated)

Use the orchestration script to enforce deterministic order and avoid drift:

- `scripts/run/cleanup_orchestrate.ps1 -Mode hard`
- `scripts/run/cleanup_orchestrate.ps1 -Mode shard-a`
- `scripts/run/cleanup_orchestrate.ps1 -Mode shard-b`
- `scripts/run/cleanup_orchestrate.ps1 -Mode shard-c`
- `scripts/run/cleanup_orchestrate.ps1 -Mode all` (runs `hard -> shard-a -> shard-b -> shard-c`)

## Execution order (mandatory)

1. Run **Hard discovery profile** across all tools first (read-only signal collection).
2. Triage findings (`DELETE` / `KEEP` / `ALLOWLIST` / `REFACTOR`).
3. Run shard-specific profile(s) for scoped verification and implementation.
4. Keep no-behavior-change default unless explicitly approved otherwise.

## Hard discovery profile (global baseline)

Use this first to get broad signal with low noise.

- Semgrep (default ignore policy from `.semgrepignore`):
  - `C:\\Users\\fa06662\\AppData\\Local\\DevTools\\pytools\\Scripts\\semgrep.exe scan --config p/python --exclude scripts/archive .`
- JSCPD:
  - `C:\\Users\\fa06662\\AppData\\Local\\Programs\\nodejs\\jscpd.cmd --config .jscpd.json`
- Vulture (project baseline in `pyproject.toml`):
  - `C:\\Users\\fa06662\\Projects\\Genesis-Core\\.venv\\Scripts\\python.exe -m vulture src/core mcp_server scripts tests`
- Radon (explicit excludes; `radon cc` has no config-file flag):
  - `C:\\Users\\fa06662\\Projects\\Genesis-Core\\.venv\\Scripts\\python.exe -m radon cc src mcp_server scripts tests --exclude ".venv,archive,artifacts,cache,data,logs,results,tmp,reports,scripts/archive" --ignore "__pycache__"`

## Shard A profile (scripts + scripts/archive)

Use this profile after hard discovery when doing script cleanup.

- Semgrep (target scripts only; includes `scripts/archive` for shard-A review):
  - `C:\\Users\\fa06662\\AppData\\Local\\DevTools\\pytools\\Scripts\\semgrep.exe scan --config p/python scripts scripts/archive --exclude ".venv" --exclude "artifacts" --exclude "cache" --exclude "data" --exclude "logs" --exclude "results" --exclude "tmp" --exclude "reports"`
- JSCPD:
  - `C:\\Users\\fa06662\\AppData\\Local\\Programs\\nodejs\\jscpd.cmd --config .jscpd.shard-a.json`
- Vulture:
  - `C:\\Users\\fa06662\\Projects\\Genesis-Core\\.venv\\Scripts\\python.exe -m vulture --config tools/config/vulture_shard_a.toml scripts scripts/archive`
- Radon:
  - `C:\\Users\\fa06662\\Projects\\Genesis-Core\\.venv\\Scripts\\python.exe -m radon cc scripts scripts/archive --exclude ".venv,artifacts,cache,data,logs,results,tmp,reports" --ignore "__pycache__"`

## Shard B profile (tests)

Use this profile after hard discovery when doing tests cleanup.

- Semgrep:
  - `C:\\Users\\fa06662\\AppData\\Local\\DevTools\\pytools\\Scripts\\semgrep.exe scan --config p/python tests`
- JSCPD:
  - `C:\\Users\\fa06662\\AppData\\Local\\Programs\\nodejs\\jscpd.cmd --config .jscpd.json --mode weak --silent --exitCode 0 tests`
- Vulture:
  - `C:\\Users\\fa06662\\Projects\\Genesis-Core\\.venv\\Scripts\\python.exe -m vulture --config pyproject.toml tests`
- Radon:
  - `C:\\Users\\fa06662\\Projects\\Genesis-Core\\.venv\\Scripts\\python.exe -m radon cc tests --exclude ".venv,archive,artifacts,cache,data,logs,results,tmp,reports,scripts/archive" --ignore "__pycache__"`

## Shard C profile (core/services)

Use this profile after hard discovery when doing core/services cleanup.

- Semgrep:
  - `C:\\Users\\fa06662\\AppData\\Local\\DevTools\\pytools\\Scripts\\semgrep.exe scan --config p/python src/core mcp_server`
- JSCPD:
  - `C:\\Users\\fa06662\\AppData\\Local\\Programs\\nodejs\\jscpd.cmd --config .jscpd.json --mode weak --silent --exitCode 0 src/core mcp_server`
- Vulture:
  - `C:\\Users\\fa06662\\Projects\\Genesis-Core\\.venv\\Scripts\\python.exe -m vulture --config pyproject.toml src/core mcp_server`
- Radon:
  - `C:\\Users\\fa06662\\Projects\\Genesis-Core\\.venv\\Scripts\\python.exe -m radon cc src/core mcp_server --exclude ".venv,archive,artifacts,cache,data,logs,results,tmp,reports,scripts/archive" --ignore "__pycache__"`

## Safety notes

- Hard profile is for discovery only (read-only).
- Shard profile is for scoped evidence collection and cleanup.
- If a tool output is uncertain, classify as `KEEP` until usage is disproven.
