## Context Map — extract_asof split (slice-8)

### Files to modify

| File                                                         | Purpose                            | Changes Needed                                                                                                                    |
| ------------------------------------------------------------ | ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `src/core/strategy/features_asof.py`                         | SSOT facade for feature extraction | Replace the inline post-cache validation/insufficient-data guard inside `_extract_asof(...)` with a thin internal delegation call |
| `src/core/strategy/features_asof_parts/input_guard_utils.py` | New internal helper module         | Host the extracted validation and insufficient-data guard logic with exact no-behavior-change semantics                           |
| `tests/utils/test_features_asof_input_guard.py`              | Focused helper verification        | Add focused coverage for length validation, `asof_bar` bounds validation, and insufficient-data payload parity                    |

### Dependencies (may need updates)

| File                                                                | Relationship                                                                                 |
| ------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `src/core/strategy/features_asof.py`                                | Cache lookup and miss metrics remain facade-owned before the new guard helper runs           |
| `src/core/strategy/features_asof_parts/extraction_context_utils.py` | Runs only after guard success; helper must not absorb its responsibilities                   |
| `src/core/strategy/features_asof_parts/result_finalize_utils.py`    | Remains downstream of successful guard and must not be reached for insufficient-data returns |
| `tests/utils/test_features.py`                                      | Guards feature/meta shape for valid paths                                                    |
| `tests/utils/test_feature_parity.py`                                | Guards parity once requests pass the guard stage                                             |

### Test files

| Test                                                                                                       | Coverage                                                                                                                                           |
| ---------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tests/utils/test_features_asof_input_guard.py`                                                            | Dedicated proof that length mismatch and `asof_bar` bounds raise the same errors, insufficient-data returns the same payload shape/content, cache-hit short-circuits before the guard helper, and insufficient-data results are not cached |
| `tests/utils/test_features.py::test_extract_features_stub_shapes`                                          | Valid-path feature/meta return shape remains unchanged                                                                                             |
| `tests/utils/test_feature_parity.py::test_runtime_vs_precomputed_features`                                 | Runtime vs precomputed parity remains unchanged                                                                                                    |
| `tests/integration/test_precompute_vs_runtime.py::test_precompute_features_match_runtime`                  | Precompute/runtime feature equivalence remains unchanged                                                                                           |
| `tests/backtest/test_backtest_determinism_smoke.py`                                                        | Determinism replay selector                                                                                                                        |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` | Pipeline invariant selector                                                                                                                        |
| `tests/governance/test_import_smoke_backtest_optuna.py`                                                    | Import smoke around backtest/optuna surfaces remains unchanged                                                                                     |

### Reference patterns

| File                                                             | Pattern                                                            |
| ---------------------------------------------------------------- | ------------------------------------------------------------------ |
| `src/core/strategy/features_asof_parts/result_finalize_utils.py` | Internal pure helper preserving caller-owned control flow          |
| `src/core/strategy/features_asof_parts/fibonacci_apply_utils.py` | Internal orchestration helper with injected authority boundaries   |
| `src/core/strategy/features_asof.py`                             | Thin facade wrappers delegating to internal helper implementations |

### Risk assessment

- [ ] Breaking changes to public API
- [x] High-sensitivity internal refactor risk (mitigation: keep all public signatures/exports unchanged and facade-owned cache authority in `features_asof.py`)
- [ ] Database migrations needed
- [ ] Configuration changes required

### Slice-8 decision

- Extract only the post-cache guard segment that computes or derives:
  - OHLCV length validation
  - `asof_bar` validation
  - `min_lookback = 50`
  - insufficient-data early return payload
- Keep cache lookup/miss accounting, prep/context build, indicator/base/fib/context/finalize orchestration, and all public wrappers inside `features_asof.py` in this slice.
- Preserve exact semantics for:
  - validation error text
  - insufficient-data payload content and keys
  - cache-before-validation ordering
  - min-lookback threshold value
- Helper must remain pure and must not take over cache authority from the facade.
- Keep helper internal-only; public SSOT remains `core.strategy.features_asof`.
- Leave `docs/audit/refactor/features_asof/context_map_extract_asof_split_slice1_2026-03-12.md`, `context_map_extract_asof_split_slice5_2026-03-12.md`, and `context_map_extract_asof_split_slice6_2026-03-12.md` untouched because they currently contain local user/automation edits outside this slice.
