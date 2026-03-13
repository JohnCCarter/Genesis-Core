# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` (`feature/* -> RESEARCH` for `feature/extract-asof-split`)
- **Risk:** `HIGH` — why: touches `src/core/strategy/*` (`features_asof.py` remains a high-sensitivity feature-parity surface)
- **Required Path:** `Full` (high-sensitivity path under `src/core/strategy/*`)
- **Objective:** Continue the no-behavior-change internal split of `_extract_asof(...)` by extracting only the indicator/base-feature orchestration block into an internal helper while preserving facade behavior exactly.
- **Candidate:** `extract-asof-split (slice-9)`
- **Base SHA:** `de65996d`
- **Category:** `api` (internal no-behavior-change refactor only; no public API/wrapper/config-authority semantics change)
- **Constraints:** `NO BEHAVIOR CHANGE` (default behavior, FAST/SLOW hit accounting, indicator unpacking semantics, feature values, wrapper signatures, and runtime defaults must remain unchanged)

## Scope

- **Scope IN:**
  - `src/core/strategy/features_asof.py`
  - `src/core/strategy/features_asof_parts/indicator_pipeline_utils.py` (new)
  - `tests/utils/test_features_asof_indicator_pipeline.py` (new)
  - `docs/audit/refactor/features_asof/command_packet_extract_asof_split_slice9_2026-03-13.md`
  - `docs/audit/refactor/features_asof/context_map_extract_asof_split_slice9_2026-03-13.md`
- **Scope OUT:**
  - `docs/audit/refactor/features_asof/context_map_extract_asof_split_slice1_2026-03-12.md` (user/local edit remains untouched)
  - all non-listed `src/**` files
  - `src/core/strategy/evaluate.py`
  - `src/core/strategy/features.py`
  - `src/core/strategy/features_asof_parts/indicator_state_utils.py`
  - `src/core/strategy/features_asof_parts/base_feature_utils.py`
  - `src/core/strategy/features_asof_parts/fibonacci_*`
  - `src/core/strategy/features_asof_parts/context_bundle_utils.py`
  - `src/core/strategy/features_asof_parts/result_finalize_utils.py`
  - `src/core/strategy/features_asof_parts/input_guard_utils.py`
  - `config/**`, `.github/workflows/**`, `mcp_server/**`, `scripts/**`
  - runtime/config authority paths and freeze-sensitive workflow files
- **Expected changed files:** 5
- **Max files touched:** 5

## Gates required

- `python -m black --check src tests`
- `python -m ruff check src tests`
- `python -m pytest -q tests/governance/test_import_smoke_backtest_optuna.py`
- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
- `python -m pytest -q tests/utils/test_features_asof_cache.py::test_feature_result_cache_lookup_moves_hit_to_mru_end tests/utils/test_features_asof_cache.py::test_feature_result_cache_store_enforces_size_and_overwrite_semantics`
- `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `python -m pytest -q tests/utils/test_feature_parity.py::test_runtime_vs_precomputed_features`
- `python -m pytest -q tests/integration/test_precompute_vs_runtime.py::test_precompute_features_match_runtime`
- `python -m pytest -q tests/utils/test_features.py::test_extract_features_atr14_is_true_atr14_even_when_atr_period_differs tests/utils/test_features.py::test_extract_features_stub_shapes`
- `python -m pytest -q tests/utils/test_features_asof_fib_error_handling.py`
- `python -m pytest -q tests/utils/test_features_asof_indicator_state.py`
- `python -m pytest -q tests/utils/test_features_asof_base_features.py`
- focused slice tests:
  - `python -m pytest -q tests/utils/test_features_asof_indicator_pipeline.py`

Focused slice test must prove exact no-drift indicator/base-feature orchestration semantics: the helper must call the injected indicator-state builder and base-feature builder with the same arguments in the same order, return the FAST/SLOW accounting signal without mutating global counters itself, unpack the returned dataclass fields without reshaping, preserve `atr_vals` without coercion, and return a fresh `features` dict copy (not the same object as `base_feature_bundle.features`) with the same content plus the same `rsi_current`, `atr_percentiles`, `atr_vals`, and `atr14_current` that downstream slices consume.

## Stop Conditions

- Scope drift outside Scope IN
- Any behavior/API drift in `extract_features_live`, `extract_features_backtest`, or `extract_features`
- Any change in FAST/SLOW hit accounting, indicator unpacking semantics, base-feature values, or downstream inputs to Fibonacci/context/finalizer helpers
- Determinism/cache/pipeline regression
- Forbidden/high-sensitivity paths touched outside approved scope

## Output required

- **Implementation Report**
- **PR evidence template**

## Skill Usage

- Relevant repo-local governance specs loaded/applied: `.github/skills/repo_clean_refactor.json` and `.github/skills/feature_parity_check.json`.
- Generic context-mapping/refactor-planning aids may be used, but pass/fail governance for this slice is anchored in the repo-local no-drift and parity specs above.
- Slice-9 extracts only the indicator/base-feature orchestration block from `_extract_asof(...)` into an internal helper module. Public import surface remains `core.strategy.features_asof`, and helper module remains internal-only.
- This slice is an internal refactor of `_extract_asof(...)` orchestration only. No public API, wrapper signature, config-authority behavior, or runtime default semantics are changed.
- Helper must use dependency injection for the existing indicator-state and base-feature builders; it must not become new indicator or base-feature authority and must not bypass existing facade-owned FAST/SLOW hit accounting semantics. `_log_precompute_status(...)` and precompute warning ownership remain outside this slice in `features_asof.py`.
