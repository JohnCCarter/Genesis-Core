## Context Map — extract_asof split (slice-7)

### Files to modify

| File                                                             | Purpose                            | Changes Needed                                                                                                          |
| ---------------------------------------------------------------- | ---------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `src/core/strategy/features_asof.py`                             | SSOT facade for feature extraction | Replace the inline Fibonacci feature application block inside `_extract_asof(...)` with a thin internal delegation call |
| `src/core/strategy/features_asof_parts/fibonacci_apply_utils.py` | New internal helper module         | Host the extracted Fibonacci application/orchestration logic with exact no-behavior-change semantics                    |
| `tests/utils/test_features_asof_fibonacci_apply.py`              | Focused helper verification        | Add focused coverage for default fib status, builder passthrough, same-dict mutation, and status propagation            |

### Dependencies (may need updates)

| File                                                               | Relationship                                                                                           |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------ |
| `src/core/strategy/features_asof_parts/fibonacci_feature_utils.py` | Existing Fibonacci update builder remains canonical upstream implementation used by the facade wrapper |
| `src/core/strategy/features_asof.py`                               | Existing `_build_fibonacci_feature_updates(...)` wrapper remains the only injected builder authority   |
| `src/core/strategy/features_asof_parts/context_bundle_utils.py`    | Consumes the updated `features` and `fib_feature_status` after the Fibonacci application block         |
| `src/core/strategy/features_asof_parts/result_finalize_utils.py`   | Finalizer consumes the propagated fib status after the application block                               |
| `tests/utils/test_features_asof_fib_error_handling.py`             | Guards fallback/meta-reason semantics across the full facade                                           |

### Test files

| Test                                                                                                       | Coverage                                                                                                                                                                                                                                                                                                                     |
| ---------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tests/utils/test_features_asof_fibonacci_apply.py`                                                        | Dedicated proof that the helper calls the injected builder exactly once with unchanged arguments, mutates and returns the same `features` dict, preserves builder-returned fib status, and includes a facade-near monkeypatch test proving `_extract_asof(...)` still routes through `_build_fibonacci_feature_updates(...)` |
| `tests/utils/test_features_asof_fib_error_handling.py`                                                     | Fallback feature values and meta reason propagation remain unchanged                                                                                                                                                                                                                                                         |
| `tests/utils/test_features.py::test_extract_features_stub_shapes`                                          | Feature/meta return shape remains unchanged                                                                                                                                                                                                                                                                                  |
| `tests/utils/test_feature_parity.py::test_runtime_vs_precomputed_features`                                 | Runtime vs precomputed parity remains unchanged                                                                                                                                                                                                                                                                              |
| `tests/integration/test_precompute_vs_runtime.py::test_precompute_features_match_runtime`                  | Precompute/runtime feature equivalence remains unchanged                                                                                                                                                                                                                                                                     |
| `tests/backtest/test_backtest_determinism_smoke.py`                                                        | Determinism replay selector                                                                                                                                                                                                                                                                                                  |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` | Pipeline invariant selector                                                                                                                                                                                                                                                                                                  |
| `tests/governance/test_import_smoke_backtest_optuna.py`                                                    | Import smoke around backtest/optuna surfaces remains unchanged                                                                                                                                                                                                                                                               |

### Reference patterns

| File                                                               | Pattern                                                                                      |
| ------------------------------------------------------------------ | -------------------------------------------------------------------------------------------- |
| `src/core/strategy/features_asof_parts/context_bundle_utils.py`    | Internal helper returning caller-consumed bundle while preserving facade-owned orchestration |
| `src/core/strategy/features_asof_parts/result_finalize_utils.py`   | Internal helper using dependency injection and preserving caller-owned objects               |
| `src/core/strategy/features_asof_parts/fibonacci_feature_utils.py` | Canonical low-level Fibonacci update builder that should remain untouched in this slice      |
| `src/core/strategy/features_asof.py`                               | Thin facade wrappers delegating to internal helper implementations                           |

### Risk assessment

- [x] Breaking changes to public API (mitigation: keep all public signatures/exports unchanged)
- [ ] Database migrations needed
- [ ] Configuration changes required

### Slice-7 decision

- Extract only the Fibonacci application segment that computes or derives:
  - default `fib_feature_status = {"available": True, "reason": "OK"}`
  - `fib_feature_updates, fib_feature_status = _build_fibonacci_feature_updates(...)`
  - `features.update(fib_feature_updates)`
- Keep indicator-state assembly, context bundle assembly, finalizer tail, cache lookup, and all public wrappers inside `features_asof.py` in this slice.
- Preserve exact semantics for:
  - fallback feature values provided by the existing builder chain
  - feature update mutation order
  - fib status propagation into final meta
  - use of the existing facade wrapper `_build_fibonacci_feature_updates(...)`
- Helper must use dependency injection for the Fibonacci update builder and must not bypass or replace the existing wrapper authority.
- Helper must not take over fallback or exception authority from the existing Fibonacci builder chain.
- Keep helper internal-only; public SSOT remains `core.strategy.features_asof`.
- Leave `docs/audit/refactor/features_asof/context_map_extract_asof_split_slice1_2026-03-12.md`, `context_map_extract_asof_split_slice5_2026-03-12.md`, and `context_map_extract_asof_split_slice6_2026-03-12.md` untouched because they currently contain local user/automation edits outside this slice.
