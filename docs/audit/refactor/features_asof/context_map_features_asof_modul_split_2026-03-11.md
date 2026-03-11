## Context Map — features_asof modul-split (slice-10)

### Files to modify

| File                                                               | Purpose                     | Changes Needed                                                                                                                           |
| ------------------------------------------------------------------ | --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `src/core/strategy/features_asof.py`                               | SSOT for feature extraction | Keep facade/API, replace the remaining Fibonacci feature-engine try/except block with a thin module-level wrapper delegating to helper   |
| `src/core/strategy/features_asof_parts/fibonacci_feature_utils.py` | New extracted helper module | Host the remaining Fibonacci feature engine as an internal helper that returns feature updates plus status with exact fallback semantics |
| `tests/utils/test_features_asof_fib_error_handling.py`             | Focused fib failure proof   | Preserve `FIB_FEATURES_CONTEXT_ERROR` fallback semantics and prove no feature-shape/count drift on the failure path                      |

### Dependencies (may need updates)

| File                            | Relationship                                                                       |
| ------------------------------- | ---------------------------------------------------------------------------------- |
| `src/core/strategy/evaluate.py` | Imports `extract_features_live` / `extract_features_backtest` from `features_asof` |
| `src/core/strategy/features.py` | Legacy wrapper delegates into `features_asof`                                      |
| `src/core/backtest/engine.py`   | Runtime/backtest integration uses `features_asof` behavior and counters            |

### Test files

| Test                                                                                                            | Coverage                                                                                                              |
| --------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `tests/utils/test_features_asof_fib_error_handling.py::test_fibonacci_feature_error_exposes_meta_and_fallbacks` | Facade-level Fibonacci failure fallback semantics, exact feature updates, and failure-path feature shape/count guards |
| `tests/utils/test_feature_parity.py`                                                                            | Runtime vs precomputed parity remains unchanged                                                                       |
| `tests/integration/test_precompute_vs_runtime.py`                                                               | Precompute/runtime feature equivalence remains unchanged                                                              |
| `tests/utils/test_features_asof_cache_key_deterministic.py`                                                     | Cache-key determinism remains unchanged                                                                               |
| `tests/utils/test_features.py::test_extract_features_stub_shapes`                                               | Feature shape remains unchanged                                                                                       |
| `tests/integration/test_model_schema_compat.py::test_feature_extraction_covers_all_model_schema_keys`           | Model schema compatibility remains unchanged                                                                          |
| `tests/backtest/test_backtest_determinism_smoke.py`                                                             | Determinism replay selector                                                                                           |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`      | Pipeline invariant selector                                                                                           |

### Reference patterns

| File                                                               | Pattern                                                               |
| ------------------------------------------------------------------ | --------------------------------------------------------------------- |
| `src/core/strategy/components/*.py`                                | Small focused modules with clear responsibility boundaries            |
| `src/core/strategy/features.py`                                    | Facade/delegation pattern preserving API surface                      |
| `src/core/strategy/features_asof_parts/atr_percentile_utils.py`    | Small extracted helper with thin facade wrapper in `features_asof.py` |
| `src/core/strategy/features_asof_parts/fibonacci_context_utils.py` | Internal orchestration helper with injected dependencies              |
| `src/core/strategy/features_asof_parts/result_cache_utils.py`      | Stateless internal helper module pattern for extracted logic          |

### Risk assessment

- [x] Breaking changes to public API (mitigation: keep function signatures and exports unchanged)
- [ ] Database migrations needed
- [ ] Configuration changes required

### Slice-10 decision

- Extract pure helper logic incrementally (no decision logic / no indicator math flow changes).
- Slice-10 extracts only the remaining Fibonacci feature engine into `features_asof_parts/fibonacci_feature_utils.py` while preserving call sites, exact fallback values, exact failure reason string, metrics/log side-effects, feature keys, and default runtime behavior in `features_asof.py`.
- `features_asof_parts` is internal-only modularization support; public import surface remains `core.strategy.features_asof`.
- Keep import path `core.strategy.features_asof` as the only public SSOT.
- `src/core/strategy/features_asof_parts/__init__.py` remains unchanged because no package-root export is required for this slice.
- Use dedicated task folder `docs/audit/refactor/features_asof/` for governance artifacts.
