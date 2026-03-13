## Context Map — extract_asof split (slice-9)

### Files to modify

| File | Purpose | Changes Needed |
| --- | --- | --- |
| `src/core/strategy/features_asof.py` | SSOT facade for feature extraction | Replace the inline indicator/base-feature orchestration block inside `_extract_asof(...)` with a thin internal delegation call |
| `src/core/strategy/features_asof_parts/indicator_pipeline_utils.py` | New internal helper module | Host the extracted indicator/base-feature orchestration with exact no-behavior-change semantics |
| `tests/utils/test_features_asof_indicator_pipeline.py` | Focused helper verification | Add focused coverage for builder passthrough, FAST/SLOW accounting signal, dataclass field unpacking, and downstream return values |

### Dependencies (may need updates)

| File | Relationship |
| --- | --- |
| `src/core/strategy/features_asof_parts/indicator_state_utils.py` | Existing canonical indicator-state builder remains unchanged and injected into the new orchestration helper |
| `src/core/strategy/features_asof_parts/base_feature_utils.py` | Existing canonical base-feature builder remains unchanged and injected into the new orchestration helper |
| `src/core/strategy/features_asof.py` | Facade continues to own FAST/SLOW counter globals and downstream helper chaining |
| `src/core/strategy/features_asof_parts/fibonacci_apply_utils.py` | Consumes `features`, `rsi_current`, and indicator-derived values produced by this orchestration block |
| `src/core/strategy/features_asof_parts/result_finalize_utils.py` | Downstream finalizer still consumes `atr_percentiles`, `atr_vals`, and `atr14_current` derived here |

### Test files

| Test | Coverage |
| --- | --- |
| `tests/utils/test_features_asof_indicator_pipeline.py` | Dedicated proof that the helper calls injected builders in order, preserves `rsi_used_fast_path` accounting signal without mutating globals, keeps `atr_vals` uncoerced, returns a fresh `features` dict copy, and returns downstream inputs unchanged |
| `tests/utils/test_features_asof_indicator_state.py` | Canonical indicator-state semantics remain unchanged |
| `tests/utils/test_features_asof_base_features.py` | Canonical base-feature semantics remain unchanged |
| `tests/utils/test_features.py::test_extract_features_stub_shapes` | Feature/meta return shape remains unchanged |
| `tests/utils/test_feature_parity.py::test_runtime_vs_precomputed_features` | Runtime vs precomputed parity remains unchanged |
| `tests/integration/test_precompute_vs_runtime.py::test_precompute_features_match_runtime` | Precompute/runtime feature equivalence remains unchanged |
| `tests/backtest/test_backtest_determinism_smoke.py` | Determinism replay selector |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` | Pipeline invariant selector |

### Reference patterns

| File | Pattern |
| --- | --- |
| `src/core/strategy/features_asof_parts/fibonacci_apply_utils.py` | Internal orchestration helper returning caller-consumed outputs with injected authority |
| `src/core/strategy/features_asof_parts/result_finalize_utils.py` | Internal helper preserving caller-owned control flow and returned objects |
| `src/core/strategy/features_asof.py` | Thin facade wrappers delegating to internal helper implementations |

### Risk assessment

- [ ] Breaking changes to public API
- [x] High-sensitivity internal refactor risk (mitigation: keep public signatures unchanged and preserve facade-owned FAST/SLOW hit accounting)
- [ ] Database migrations needed
- [ ] Configuration changes required

### Slice-9 decision

- Extract only the indicator/base-feature orchestration segment that computes or derives:
  - `_build_indicator_state_impl(...)`
  - FAST/SLOW hit signal from `indicator_state.rsi_used_fast_path`
  - field unpacking from `indicator_state`
  - `_build_base_feature_bundle_impl(...)`
  - `features`, `rsi_current`, `atr_percentiles`
- Keep cache/guard/prep orchestration, Fibonacci apply/context/finalizer orchestration, and all public wrappers inside `features_asof.py` in this slice.
- Preserve exact semantics for:
  - injected builder argument order
  - FAST/SLOW accounting signal propagation
  - indicator dataclass field unpacking
  - fresh-copy semantics for `features`
  - downstream values consumed by later helpers
- Helper must use dependency injection for the indicator-state and base-feature builders and must not take over global counter authority from the facade.
- `_log_precompute_status(...)` and precompute warning ownership stay in `features_asof.py` and are explicitly out of scope for this slice.
- Keep helper internal-only; public SSOT remains `core.strategy.features_asof`.
- Leave `docs/audit/refactor/features_asof/context_map_extract_asof_split_slice1_2026-03-12.md` untouched because it currently contains a local user/automation edit outside this slice.
