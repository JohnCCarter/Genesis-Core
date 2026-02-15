# Repo Cleanup D21 Minimal Delete Execution Contract (2026-02-15)

## Category

`tooling`

## Scope IN

- Delete-only execution av exakt en föråldrad mapp:
  - `results/hparam_search/phase7b_grid_3months/`
  - Innehåll (10 filer):
    - `run_meta.json`
    - `trial_001.json`
    - `trial_001_config.json`
    - `trial_001.log`
    - `trial_002.json`
    - `trial_002_config.json`
    - `trial_002.log`
    - `trial_003.json`
    - `trial_003_config.json`
    - `trial_003.log`
- `docs/ops/REPO_CLEANUP_D21_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D21_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_NEXT_BACKLOG_2026-02-14.md`
- `AGENTS.md`

## Scope OUT

- `src/**`
- `tests/**`
- `config/**`
- `.github/**`
- `.gitignore`
- `tmp/**`
- `results/**` (förutom exakt `results/hparam_search/phase7b_grid_3months/**`)

## Constraints

Default: `NO BEHAVIOR CHANGE`

- Ingen policyändring i `.gitignore`.
- Ingen deletion utanför scopead mapp.
- Ingen runtime/API/config-ändring.

## Preconditions

- Explicit requester-beslut: börja radera föråldrade resultatmappar.
- Kandidaten är äldre (2025-10-22) och tidigare dokumenterad i D4A som låg extern ref-risk.
- Aktuell champion-setup pekar på andra resultatpaths och denna mapp är inte championkritisk.

## Required gates (BEFORE + AFTER)

1. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m black --check .`
2. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m ruff check .`
3. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest tests/test_import_smoke_backtest_optuna.py -q`
4. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest tests/test_backtest_determinism_smoke.py -q`
5. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py -q`
6. `C:\Users\salib\Desktop\Repos\Genesis-Core\.venv\Scripts\python.exe -m pytest tests/test_pipeline_fast_hash_guard.py -q`

## Done criteria

1. Exakt en scopead föråldrad resultatmapp raderad.
2. D21 kontrakt + rapport skapade.
3. Backlog + `AGENTS.md` uppdaterade med korrekt statusdisciplin.
4. Diffen är strikt scopead till 1 radering + docs i Scope IN.
5. Required gates passerar efter ändring.
6. Opus post-code diff-audit är `APPROVED`.

## Status

- D21 i denna tranche är en minimal delete-only batch.
- Vidare destruktiv radering utanför scopead batch är fortsatt föreslagen i separat kontrakt.
