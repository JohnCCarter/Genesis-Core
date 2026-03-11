# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` (`feature/* -> RESEARCH` for `feature/feautres_asof-modul-split`)
- **Risk:** `HIGH` — why: touches `src/core/strategy/*` (high-sensitivity zone)
- **Required Path:** `Full` (high-sensitivity path under `src/core/strategy/*`)
- **Objective:** Continue no-behavior-change modular split of `features_asof.py` with facade preserved.
- **Candidate:** `features_asof-modul-split (slice-8)`
- **Base SHA:** `cb746bab`
- **Category:** `refactor(server)`
- **Constraints:** `NO BEHAVIOR CHANGE` (default behavior and public API must remain unchanged)

## Scope

- **Scope IN:**
  - `src/core/strategy/features_asof.py`
  - `src/core/strategy/features_asof_parts/fibonacci_context_utils.py` (new)
  - `tests/utils/test_features_asof_fib_error_handling.py`
  - `docs/audit/refactor/features_asof/context_map_features_asof_modul_split_2026-03-11.md`
  - `docs/audit/refactor/features_asof/command_packet_features_asof_modul_split_2026-03-11.md`
- **Scope OUT:**
  - all non-listed `src/**` files
  - `config/**`, `.github/workflows/**`, `mcp_server/**`, `scripts/**`
  - runtime/config authority paths and freeze-sensitive workflow files
- **Expected changed files:** 5
- **Max files touched:** 6

## Gates required

- `python -m pre_commit run --all-files`
- `python -m pytest -q tests/governance/test_import_smoke_backtest_optuna.py`
- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/utils/test_feature_cache.py tests/utils/diffing/test_feature_cache.py tests/utils/test_features_asof_cache_key_deterministic.py`
- `python -m pytest -q tests/utils/test_feature_parity.py::test_runtime_vs_precomputed_features`
- `python -m pytest -q tests/integration/test_precompute_vs_runtime.py::test_precompute_features_match_runtime`
- `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `python -m pytest -q tests/utils/test_features.py::test_extract_features_stub_shapes`
- `python -m pytest -q tests/integration/test_model_schema_compat.py::test_feature_extraction_covers_all_model_schema_keys`
- focused slice tests:
  - `python -m pytest -q tests/utils/test_features_asof_fib_error_handling.py -k "ltf_context_error"`

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
- repo-local skill spec `feature_parity_check` reviewed and applied for runtime/precompute parity selectors and feature-surface guardrails.
- repo-local skill spec `repo_clean_refactor` reviewed and applied for strict scope, minimal diff, and reversible no-behavior-change sequencing.
- `features_asof_parts` is an internal extraction package. Public strategy import surface remains `core.strategy.features_asof`; package exports exist only to support local modularization and must not be treated as a stable external API.
- Slice-8 extracts only the LTF fibonacci context orchestration into `src/core/strategy/features_asof_parts/fibonacci_context_utils.py`. Public facade remains `core.strategy.features_asof`; no runtime behavior, cache ownership, metrics ownership, env/config interpretation, or public API may change.

## Gate outcomes (executed)

- `python -m pre_commit run --all-files` — **PASS**
- `python -m pytest -q tests/governance/test_import_smoke_backtest_optuna.py` — **PASS**
- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py` — **PASS**
- `python -m pytest -q tests/utils/test_feature_cache.py tests/utils/diffing/test_feature_cache.py tests/utils/test_features_asof_cache_key_deterministic.py` — **PASS**
- `python -m pytest -q tests/utils/test_feature_parity.py::test_runtime_vs_precomputed_features` — **PASS**
- `python -m pytest -q tests/integration/test_precompute_vs_runtime.py::test_precompute_features_match_runtime` — **PASS**
- `python -m pytest -q tests/utils/test_features.py::test_extract_features_stub_shapes` — **PASS**
- `python -m pytest -q tests/integration/test_model_schema_compat.py::test_feature_extraction_covers_all_model_schema_keys` — **PASS**
- `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` — **PASS**
- `python -m pytest -q tests/utils/test_features_asof_fib_error_handling.py -k "ltf_context_error"` — **PASS**
