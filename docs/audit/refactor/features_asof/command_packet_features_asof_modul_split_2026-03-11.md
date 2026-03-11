# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` (`feature/* -> RESEARCH` for `feature/feautres_asof-modul-split`)
- **Risk:** `HIGH` — why: touches `src/core/strategy/*` (high-sensitivity zone)
- **Required Path:** `Full` (high-sensitivity path under `src/core/strategy/*`)
- **Objective:** Continue no-behavior-change modular split of `features_asof.py` with facade preserved.
- **Candidate:** `features_asof-modul-split (slice-2)`
- **Base SHA:** `34848989`
- **Category:** `refactor(server)`
- **Constraints:** `NO BEHAVIOR CHANGE` (default behavior and public API must remain unchanged)

## Scope

- **Scope IN:**
  - `src/core/strategy/features_asof.py`
  - `src/core/strategy/features_asof_parts/__init__.py` (new)
  - `src/core/strategy/features_asof_parts/hash_utils.py` (new)
  - `src/core/strategy/features_asof_parts/precompute_utils.py` (new)
  - `tests/utils/test_features_asof_cache.py`
  - `tests/utils/test_features_asof_cache_key_deterministic.py`
  - `tests/utils/test_features_asof_fast_hash_env_case.py`
  - `docs/audit/refactor/features_asof/context_map_features_asof_modul_split_2026-03-11.md`
  - `docs/audit/refactor/features_asof/command_packet_features_asof_modul_split_2026-03-11.md`
- **Scope OUT:**
  - all non-listed `src/**` files
  - `config/**`, `.github/workflows/**`, `mcp_server/**`, `scripts/**`
  - runtime/config authority paths and freeze-sensitive workflow files
- **Expected changed files:** 6–8
- **Max files touched:** 8

## Gates required

- `python -m pre_commit run --all-files`
- `python -m pytest -q tests/governance/test_import_smoke_backtest_optuna.py`
- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/utils/test_feature_cache.py tests/utils/diffing/test_feature_cache.py tests/utils/test_features_asof_cache.py tests/utils/test_features_asof_cache_key_deterministic.py`
- `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py`
- focused slice tests:
  - `python -m pytest -q tests/utils/test_features_asof_fast_hash_env_case.py`
  - `python -m pytest -q tests/utils/test_features.py::test_compute_candles_hash_accepts_numpy_arrays`

## Stop Conditions

- Scope drift outside Scope IN
- Any behavior/API drift in `extract_features_live`, `extract_features_backtest`, `extract_features`
- Determinism/cache/pipeline regression
- Forbidden/high-sensitivity paths touched outside approved scope

## Output required

- **Implementation Report**
- **PR evidence template**

## Skill Usage

- `context-map` skill loaded and applied for dependency/test surface verification.
- `refactor-plan` skill loaded and applied for phased no-behavior-change extraction sequencing.

## Gate outcomes (executed)

- `python -m pre_commit run --all-files` — **PASS**
- `python -m pytest -q tests/governance/test_import_smoke_backtest_optuna.py` — **PASS**
- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py` — **PASS**
- `python -m pytest -q tests/utils/test_feature_cache.py tests/utils/diffing/test_feature_cache.py tests/utils/test_features_asof_cache.py tests/utils/test_features_asof_cache_key_deterministic.py` — **PASS**
- `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py` — **PASS**
- `python -m pytest -q tests/utils/test_features_asof_fast_hash_env_case.py` — **PASS**
- `python -m pytest -q tests/utils/test_features.py::test_compute_candles_hash_accepts_numpy_arrays` — **PASS**
- `python -m pytest -q tests/integration/test_precompute_vs_runtime.py` — **PASS**
- `python -m black --check src/core/strategy/features_asof_parts/hash_utils.py src/core/strategy/features_asof_parts/precompute_utils.py src/core/strategy/features_asof_parts/__init__.py` — **PASS**
- `python -m ruff check src/core/strategy/features_asof_parts/hash_utils.py src/core/strategy/features_asof_parts/precompute_utils.py src/core/strategy/features_asof_parts/__init__.py` — **PASS**
