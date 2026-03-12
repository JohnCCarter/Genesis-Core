## Context Map — extract_asof split (slice-5)

### Files to modify

| File                                                            | Purpose                            | Changes Needed                                                                                                              |
| --------------------------------------------------------------- | ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `src/core/strategy/features_asof.py`                            | SSOT facade for feature extraction | Replace the inline HTF/LTF Fibonacci context orchestration inside `_extract_asof(...)` with a thin internal delegation call |
| `src/core/strategy/features_asof_parts/context_bundle_utils.py` | New internal helper module         | Host the extracted HTF/LTF context orchestration logic with exact no-behavior-change semantics                              |
| `tests/utils/test_features_asof_context_bundle.py`              | Focused helper verification        | Add focused coverage for timeframe gating, selector passthrough, and default empty-context behavior                         |

### Dependencies (may need updates)

| File                                                               | Relationship                                                                                                |
| ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| `src/core/strategy/features_asof_parts/fibonacci_context_utils.py` | Existing HTF/LTF context builders remain canonical upstream helpers used by the new orchestration bundle    |
| `src/core/strategy/features_asof_parts/meta_utils.py`              | Slice-4 helper consumes the HTF/LTF context outputs and selector metadata produced by the new bundle helper |
| `src/core/backtest/engine.py`                                      | Backtest integration depends on stable HTF/LTF context availability semantics inside extracted feature meta |
| `src/core/strategy/evaluate.py`                                    | Imports public feature extraction wrappers and depends on unchanged facade semantics                        |
| `src/core/strategy/components/context_builder.py`                  | Downstream consumers rely on stable `htf_fibonacci` / `ltf_fibonacci` availability flags in feature meta    |

### Test files

| Test                                                                                                                      | Coverage                                                                                                               |
| ------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `tests/utils/test_features_asof_context_bundle.py`                                                                        | Dedicated proof for ineligible default shape with no builder invocation, plus eligible selector/`atr_vals` passthrough |
| `tests/utils/test_features_asof_fib_error_handling.py`                                                                    | Downstream HTF/LTF error behavior and selector semantics remain unchanged                                              |
| `tests/utils/test_features.py::test_extract_features_stub_shapes`                                                         | Feature shape and version count remain unchanged                                                                       |
| `tests/utils/test_feature_parity.py::test_runtime_vs_precomputed_features`                                                | Runtime vs precomputed parity remains unchanged                                                                        |
| `tests/integration/test_precompute_vs_runtime.py::test_precompute_features_match_runtime`                                 | Precompute/runtime feature equivalence remains unchanged                                                               |
| `tests/utils/test_features_asof_cache.py::test_feature_result_cache_lookup_moves_hit_to_mru_end`                          | Result-cache invariance remains unchanged                                                                              |
| `tests/utils/test_features_asof_cache.py::test_feature_result_cache_store_enforces_size_and_overwrite_semantics`          | Result-cache overwrite/eviction semantics remain unchanged                                                             |
| `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed` | Cache determinism remains unchanged                                                                                    |
| `tests/backtest/test_backtest_determinism_smoke.py`                                                                       | Determinism replay selector                                                                                            |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`                | Pipeline invariant selector                                                                                            |
| `tests/governance/test_import_smoke_backtest_optuna.py`                                                                   | Import smoke around backtest/optuna surfaces remains unchanged                                                         |

### Reference patterns

| File                                                             | Pattern                                                                            |
| ---------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `src/core/strategy/features_asof_parts/indicator_state_utils.py` | Internal dataclass-based helper returning caller-consumed indicator state          |
| `src/core/strategy/features_asof_parts/base_feature_utils.py`    | Internal helper returning caller-consumed bundle while preserving facade ownership |
| `src/core/strategy/features_asof_parts/meta_utils.py`            | Internal helper returning caller-consumed meta dictionary                          |
| `src/core/strategy/features_asof.py`                             | Thin facade wrappers delegating to internal helper implementations                 |

### Risk assessment

- [x] Breaking changes to public API (mitigation: keep all public signatures/exports unchanged)
- [ ] Database migrations needed
- [ ] Configuration changes required

### Slice-5 decision

- Extract only the HTF/LTF context orchestration segment that computes or derives:
  - default empty `htf_fibonacci_context`
  - default empty `ltf_fibonacci_context`
  - default `htf_selector_meta`
  - eligible timeframe gating for `1h`, `30m`, `6h`, `15m`
  - delegation to existing `_build_htf_fibonacci_context(...)`
  - delegation to existing `_build_ltf_fibonacci_context(...)`
- Keep upstream Fibonacci feature assembly, meta build, result tuple build, cache store, and all public wrappers inside `features_asof.py` in this slice.
- Preserve exact semantics for:
  - eligible timeframe set
  - HTF selector passthrough to meta
  - empty dict defaults when timeframe is not eligible
  - LTF context receiving `atr_vals`
  - no upstream HTF/LTF builder invocation when timeframe is not eligible
- Keep helper internal-only; public SSOT remains `core.strategy.features_asof`.
- Leave `docs/audit/refactor/features_asof/context_map_extract_asof_split_slice1_2026-03-12.md` and `context_map_extract_asof_split_slice4_2026-03-12.md` untouched because they currently contain local user/automation edits outside this slice.
