## Context Map — extract_asof split (slice-6)

### Files to modify

| File                                                             | Purpose                            | Changes Needed                                                                                                          |
| ---------------------------------------------------------------- | ---------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `src/core/strategy/features_asof.py`                             | SSOT facade for feature extraction | Replace the inline meta/result/cache-finalization tail inside `_extract_asof(...)` with a thin internal delegation call |
| `src/core/strategy/features_asof_parts/result_finalize_utils.py` | New internal helper module         | Host the extracted meta/result/cache-finalization logic with exact no-behavior-change semantics                         |
| `tests/utils/test_features_asof_result_finalize.py`              | Focused helper verification        | Add focused coverage for meta-builder passthrough, tuple-shape preservation, and cache-store call semantics             |

### Dependencies (may need updates)

| File                                                            | Relationship                                                                                                 |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `src/core/strategy/features_asof_parts/meta_utils.py`           | Existing meta builder remains the canonical upstream helper used by the new finalization helper              |
| `src/core/strategy/features_asof_parts/result_cache_utils.py`   | Existing cache-store helper remains canonical upstream implementation used through facade wrapper delegation |
| `src/core/strategy/features_asof_parts/context_bundle_utils.py` | Slice-5 helper produces HTF/LTF context inputs consumed by the finalization tail                             |
| `src/core/strategy/features_asof.py`                            | Thin facade wrappers and cache-key orchestration remain public SSOT                                          |
| `src/core/strategy/evaluate.py`                                 | Downstream consumers rely on unchanged return tuple and meta shape                                           |

### Test files

| Test                                                                                                             | Coverage                                                                                                                                                                                                                                                        |
| ---------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tests/utils/test_features_asof_result_finalize.py`                                                              | Dedicated proof that meta inputs pass through unchanged, object identity is preserved, the same result tuple is cached and returned, cache store is called exactly once with the original cache key/result/max size, and meta-builder failure skips cache store |
| `tests/utils/test_features_asof_cache.py::test_feature_result_cache_lookup_moves_hit_to_mru_end`                 | Result-cache lookup invariance remains unchanged                                                                                                                                                                                                                |
| `tests/utils/test_features_asof_cache.py::test_feature_result_cache_store_enforces_size_and_overwrite_semantics` | Result-cache store semantics remain unchanged                                                                                                                                                                                                                   |
| `tests/utils/test_features.py::test_extract_features_stub_shapes`                                                | Feature/meta return shape remains unchanged                                                                                                                                                                                                                     |
| `tests/utils/test_feature_parity.py::test_runtime_vs_precomputed_features`                                       | Runtime vs precomputed parity remains unchanged                                                                                                                                                                                                                 |
| `tests/integration/test_precompute_vs_runtime.py::test_precompute_features_match_runtime`                        | Precompute/runtime feature equivalence remains unchanged                                                                                                                                                                                                        |
| `tests/backtest/test_backtest_determinism_smoke.py`                                                              | Determinism replay selector                                                                                                                                                                                                                                     |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`       | Pipeline invariant selector                                                                                                                                                                                                                                     |
| `tests/governance/test_import_smoke_backtest_optuna.py`                                                          | Import smoke around backtest/optuna surfaces remains unchanged                                                                                                                                                                                                  |

### Reference patterns

| File                                                            | Pattern                                                                                             |
| --------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| `src/core/strategy/features_asof_parts/context_bundle_utils.py` | Internal dataclass-based helper returning a caller-consumed bundle with exact passthrough semantics |
| `src/core/strategy/features_asof_parts/meta_utils.py`           | Internal helper returning caller-consumed meta dictionary                                           |
| `src/core/strategy/features_asof_parts/result_cache_utils.py`   | Internal cache helper preserving LRU behavior                                                       |
| `src/core/strategy/features_asof.py`                            | Thin facade wrappers delegating to internal helper implementations                                  |

### Risk assessment

- [x] Breaking changes to public API (mitigation: keep all public signatures/exports unchanged)
- [ ] Database migrations needed
- [ ] Configuration changes required

### Slice-6 decision

- Extract only the finalization segment that computes or derives:
  - `meta = _build_feature_meta_impl(...)`
  - `result = (features, meta)`
  - `_feature_cache_store(cache_key, result)`
  - `return result`
- Keep Fibonacci feature assembly, context bundle assembly, cache lookup, and all public wrappers inside `features_asof.py` in this slice.
- Preserve exact semantics for:
  - meta payload contents and keys
  - result tuple order and object identity expectations
  - cache store timing and cache-key usage
  - delegation to existing meta builder and cache-store helper chain
- Helper must use dependency injection for meta build and cache store; it must not own `_feature_cache`, `_MAX_CACHE_SIZE`, or bypass facade-level cache delegation.
- Keep helper internal-only; public SSOT remains `core.strategy.features_asof`.
- Leave `docs/audit/refactor/features_asof/context_map_extract_asof_split_slice1_2026-03-12.md` untouched because it currently contains a local user/automation edit outside this slice.
