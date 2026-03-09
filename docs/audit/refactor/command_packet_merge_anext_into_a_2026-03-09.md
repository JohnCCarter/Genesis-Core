# Command Packet — Merge `a-next` into `a` (2026-03-09)

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping (`feature/refactor-scripts-structure-a`)
- **Risk:** `MED` — multi-file archive/docs merge
- **Required Path:** `Full`
- **Objective:** Merge `origin/feature/refactor-scripts-structure-a-next` into current branch `feature/refactor-scripts-structure-a` with governance evidence.
- **Candidate:** `merge_anext_into_a_candidate13`
- **Base SHA:** `5a42f8d8`

### Scope

- **Scope IN:**
  - Incoming changes from `origin/feature/refactor-scripts-structure-a-next`:
    - docs updates under `docs/archive/deprecated_2026-02-24/docs/{features,validation}/`
    - candidate9 docs/evidence under `docs/audit/refactor/`
    - delete batch under `scripts/archive/analysis/*` (12 files)
  - `docs/audit/refactor/command_packet_merge_anext_into_a_2026-03-09.md`
- **Scope OUT:**
  - `src/**`
  - `config/**`
  - `tests/**` (except executing tests)
  - `mcp_server/**`
  - `.github/workflows/**`
- **Expected changed files:** `20`
- **Max files touched:** `22`

### Constraints

Constraint: **NO BEHAVIOR CHANGE**.
Ändringen är begränsad till docs/archive/audit samt radering av arkiverade analys-skript under `scripts/archive/analysis/*`.
Inga ändringar i `src/**`, `config/**`, `tests/**` (förutom exekvering), `mcp_server/**`, `.github/workflows/**`.

### Skill usage evidence (pre + post)

- `python scripts/run_skill.py --skill repo_clean_refactor --manifest dev --dry-run`
- `python scripts/run_skill.py --skill python_engineering --manifest dev --dry-run`

### Gates required (pre + post)

- `pre-commit run --all-files`
- `pytest -q tests/test_import_smoke_backtest_optuna.py`
- `pytest -q tests/test_backtest_determinism_smoke.py`
- `pytest -q tests/test_feature_cache.py tests/test_features_asof_cache.py tests/test_features_asof_cache_key_deterministic.py`
- `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

### Stop Conditions

- Scope drift
- Behavior change without explicit exception
- Determinism/cache/pipeline invariant regression
- Forbidden paths touched

### Output required

- **Implementation Report**
- **PR evidence template**
- **Merge name-status artifact (scope proof)**
