# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` (`feature/* -> RESEARCH` for `feature/feautres_asof-modul-split`)
- **Risk:** `HIGH` — why: touches `src/core/strategy/*` (high-sensitivity zone)
- **Required Path:** `Full` (high-sensitivity path under `src/core/strategy/*`)
- **Objective:** Continue no-behavior-change modular split of `features_asof.py` with facade preserved.
- **Candidate:** `features_asof-modul-split (slice-5)`
- **Base SHA:** `34848989`
- **Category:** `refactor(server)`
- **Constraints:** `NO BEHAVIOR CHANGE` (default behavior and public API must remain unchanged)

## Scope

- **Scope IN:**
  - `src/core/strategy/features_asof.py`
  - `src/core/strategy/features_asof_parts/result_cache_utils.py` (new)
  - `tests/utils/test_features_asof_cache.py`
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
- `python -m pytest -q tests/utils/test_feature_parity.py::test_runtime_vs_precomputed_features`
- `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py`
- focused slice tests:
  - `python -m pytest -q tests/utils/test_features_asof_fast_hash_env_case.py`
  - `python -m pytest -q tests/utils/test_features.py::test_compute_candles_hash_accepts_numpy_arrays`
  - `python -m pytest -q tests/utils/test_env_flags.py::test_indicator_cache_disable_flag_parsing`
  - `python -m pytest -q tests/integration/test_precompute_vs_runtime.py::test_precompute_features_match_runtime`

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
- `features_asof_parts` is an internal extraction package. Public strategy import surface remains `core.strategy.features_asof`; package exports exist only to support local modularization and must not be treated as a stable external API.
- Slice-5 is a no-behavior-change internal refactor in `src/core/strategy/features_asof.py` that extracts only feature-result-cache LRU mechanics into an internal helper, while preserving cache-key ownership, metrics ownership, and default runtime behavior in `features_asof.py`.

## Gate outcomes (executed)

- `python -m pre_commit run --all-files` — **PASS**
- `python -m pytest -q tests/governance/test_import_smoke_backtest_optuna.py` — **PASS**
- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py` — **PASS**
- `python -m pytest -q tests/utils/test_feature_cache.py tests/utils/diffing/test_feature_cache.py tests/utils/test_features_asof_cache.py tests/utils/test_features_asof_cache_key_deterministic.py` — **PASS**
- `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py` — **PASS**
- `python -m pytest -q tests/utils/test_features_asof_fast_hash_env_case.py` — **PASS**
- `python -m pytest -q tests/utils/test_env_flags.py::test_indicator_cache_disable_flag_parsing` — **PASS**
- `python -m pytest -q tests/utils/test_feature_parity.py::test_runtime_vs_precomputed_features` — **PASS**
- `python -m pytest -q tests/integration/test_precompute_vs_runtime.py::test_precompute_features_match_runtime` — **PASS**
- `formatting/linting covered by python -m pre_commit run --all-files` — **PASS**
