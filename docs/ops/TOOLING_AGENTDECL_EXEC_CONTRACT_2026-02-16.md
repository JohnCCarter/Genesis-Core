# Tooling Agent Declaration Execution Contract (2026-02-16)

## Category

`tooling`

## Scope IN

- `.github/agents/Codex53.agent.md`
- `docs/ops/TOOLING_AGENTDECL_EXEC_CONTRACT_2026-02-16.md`
- `docs/ops/TOOLING_AGENTDECL_EXEC_REPORT_2026-02-16.md`

## Scope OUT

- `src/**`
- `tests/**`
- `docs/audits/**`
- `scripts/**`
- `config/**`
- `data/**`
- `results/**`
- `tmp/**`
- alla övriga paths

## Constraints

Default: `NO BEHAVIOR CHANGE`

Explicit tooling-undantag:

- Ta bort bred wildcard-deklaration `github/*`.
- Behåll explicita `github.vscode-pull-request-github/*` entries.
- Normalisera ordning för `io.github.upstash/context7/*` och `genesis-core-windows/*`.

## Preconditions

- Explicit requester-intent att slutföra separat commit för kvarvarande out-of-scope diff.
- Opus pre-code review: `APPROVED`.
- Tranche är exekverad och verifierad i commit `cdfe8e0`.

## Required gates (BEFORE + AFTER)

1. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m black --check .`
2. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m ruff check .`
3. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_import_smoke_backtest_optuna.py`
4. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_backtest_determinism_smoke.py`
5. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py`
6. `C:\Users\fa06662\Projects\Genesis-Core\.venv\Scripts\python.exe -m pytest -q tests/test_pipeline_fast_hash_guard.py`

## Done criteria

1. Tool-list normaliserad enligt kontrakt i agentfilen.
2. Diff i exekveringscommit begränsad till agentfilen.
3. Before/After-gates är passerade.
4. Opus post-code audit: `APPROVED`.

## Status

- Tooling agent-declaration tranche: `införd` (retrospektivt dokumenterad via commit `cdfe8e0`).
