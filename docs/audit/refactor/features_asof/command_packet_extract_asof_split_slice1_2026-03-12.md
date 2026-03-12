# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` (`feature/* -> RESEARCH` for `feature/extract-asof-split`)
- **Risk:** `HIGH` — why: touches `src/core/strategy/*` (`features_asof.py` is a high-sensitivity path for feature parity)
- **Required Path:** `Full` (high-sensitivity path under `src/core/strategy/*`)
- **Objective:** Start a no-behavior-change internal split of `_extract_asof(...)` by extracting only the context/index/precompute preparation block into an internal helper while preserving facade behavior exactly.
- **Candidate:** `extract-asof-split (slice-1)`
- **Base SHA:** `b82e1967`
- **Category:** `api`
- **Constraints:** `NO BEHAVIOR CHANGE` (default behavior, public API, feature values, cache semantics, and meta shape must remain unchanged)

## Scope

- **Scope IN:**
  - `src/core/strategy/features_asof.py`
  - `src/core/strategy/features_asof_parts/extraction_context_utils.py` (new)
  - `tests/utils/test_features_asof_extraction_context.py` (new)
  - `docs/audit/refactor/features_asof/command_packet_extract_asof_split_slice1_2026-03-12.md`
  - `docs/audit/refactor/features_asof/context_map_extract_asof_split_slice1_2026-03-12.md`
- **Scope OUT:**
  - all non-listed `src/**` files
  - `src/core/strategy/evaluate.py`
  - `src/core/strategy/features.py`
  - `src/core/strategy/features_asof_parts/fibonacci_*`
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
- `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `python -m pytest -q tests/utils/test_feature_parity.py::test_runtime_vs_precomputed_features`
- `python -m pytest -q tests/integration/test_precompute_vs_runtime.py::test_precompute_features_match_runtime`
- focused slice tests:
  - `python -m pytest -q tests/utils/test_features_asof_extraction_context.py`
  - `python -m pytest -q tests/utils/test_features_asof_precompute_logging.py`

## Stop Conditions

- Scope drift outside Scope IN
- Any behavior/API drift in `extract_features_live`, `extract_features_backtest`, or `extract_features`
- Any change in `_global_index` / `precomputed_features` remap semantics or fallback index semantics
- Determinism/cache/pipeline regression
- Forbidden/high-sensitivity paths touched outside approved scope

## Output required

- **Implementation Report**
- **PR evidence template**

## Skill Usage

- `context-map` skill loaded and applied for dependency/test-surface verification.
- `refactor-plan` skill loaded and applied for phased no-behavior-change extraction sequencing.
- Slice-1 extracts only context/index/precompute preparation from `_extract_asof(...)` into an internal helper module. Public import surface remains `core.strategy.features_asof`, and helper module remains internal-only.
- This slice must preserve exact semantics for `lookup_idx`, `window_start_idx`, `pre`, `pre_idx`, `atr_period`, and early fallback behavior when precompute is missing or remap fails.
- `_PRECOMPUTE_WARN_ONCE` remains caller-owned in `features_asof.py`; the helper may only return a warning signal and must not introduce a new module-global warning state.
