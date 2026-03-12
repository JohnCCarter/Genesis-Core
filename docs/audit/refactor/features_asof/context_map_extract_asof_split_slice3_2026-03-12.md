## Context Map — extract_asof split (slice-3)

### Files to modify

| File                                                          | Purpose                            | Changes Needed                                                                                                               |
| ------------------------------------------------------------- | ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `src/core/strategy/features_asof.py`                          | SSOT facade for feature extraction | Replace the inline base-feature and ATR-percentile assembly inside `_extract_asof(...)` with a thin internal delegation call |
| `src/core/strategy/features_asof_parts/base_feature_utils.py` | New internal helper module         | Host the extracted base-feature assembly logic and ATR-percentile bundle with exact no-behavior-change semantics             |
| `tests/utils/test_features_asof_base_features.py`             | Focused helper verification        | Add focused coverage for base feature formulas, fallback defaults, clipping semantics, and ATR-percentile continuity         |

### Dependencies (may need updates)

| File                                                               | Relationship                                                                                                            |
| ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------- |
| `src/core/strategy/features_asof_parts/indicator_state_utils.py`   | Slice-2 helper provides the indicator-state inputs consumed by the new base-feature helper                              |
| `src/core/strategy/features_asof_parts/atr_percentile_utils.py`    | Existing helper remains the canonical ATR-percentile implementation that the new bundle helper will delegate to         |
| `src/core/strategy/features_asof_parts/numeric_utils.py`           | Existing clipping helper remains canonical for base feature clipping                                                    |
| `src/core/strategy/features_asof_parts/fibonacci_feature_utils.py` | Downstream Fibonacci feature assembly still consumes `rsi_current` and the base `features` dict built by the new helper |
| `src/core/backtest/engine.py`                                      | Backtest integration depends on stable feature values and unchanged `_extract_asof(...)` parity                         |
| `src/core/strategy/evaluate.py`                                    | Imports public feature extraction wrappers and depends on unchanged facade semantics                                    |

### Test files

| Test                                                                                                                      | Coverage                                                                                     |
| ------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `tests/utils/test_features_asof_base_features.py`                                                                         | Dedicated proof for base feature formulas, clipping, defaults, and ATR percentile continuity |
| `tests/utils/test_feature_parity.py::test_runtime_vs_precomputed_features`                                                | Runtime vs precomputed parity remains unchanged                                              |
| `tests/integration/test_precompute_vs_runtime.py::test_precompute_features_match_runtime`                                 | Precompute/runtime feature equivalence remains unchanged                                     |
| `tests/utils/test_features.py::test_extract_features_atr14_is_true_atr14_even_when_atr_period_differs`                    | `atr_14` backcompat semantics remain unchanged                                               |
| `tests/utils/test_features.py::test_extract_features_stub_shapes`                                                         | Feature shape and count remain unchanged                                                     |
| `tests/utils/test_features_asof_fib_error_handling.py`                                                                    | Confirms downstream fib/meta behavior still sees an unchanged base feature shape             |
| `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed` | Cache determinism remains unchanged                                                          |
| `tests/backtest/test_backtest_determinism_smoke.py`                                                                       | Determinism replay selector                                                                  |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`                | Pipeline invariant selector                                                                  |
| `tests/governance/test_import_smoke_backtest_optuna.py`                                                                   | Import smoke around backtest/optuna surfaces remains unchanged                               |

### Reference patterns

| File                                                                | Pattern                                                                   |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| `src/core/strategy/features_asof_parts/extraction_context_utils.py` | Internal dataclass-based helper returning caller-consumed prep state      |
| `src/core/strategy/features_asof_parts/indicator_state_utils.py`    | Internal dataclass-based helper returning caller-consumed indicator state |
| `src/core/strategy/features_asof_parts/fibonacci_context_utils.py`  | Internal orchestration helper with dependency injection from facade       |
| `src/core/strategy/features_asof.py`                                | Thin facade wrappers delegating to internal helper implementations        |

### Risk assessment

- [x] Breaking changes to public API (mitigation: keep all public signatures/exports unchanged)
- [ ] Database migrations needed
- [ ] Configuration changes required

### Slice-3 decision

- Extract only the base feature assembly segment that computes or derives:
  - `rsi_inv_lag1`
  - `volatility_shift_ma3`
  - `bb_position_inv_ma3`
  - `rsi_vol_interaction`
  - `vol_regime`
  - `atr_14`
  - ATR percentile bundle from `atr_window_56` / `atr_vals`
- Keep downstream Fibonacci feature assembly, HTF/LTF context assembly, and meta/result build inside `features_asof.py` in this slice.
- Preserve exact semantics for:
  - default fallbacks when indicator windows are empty
  - `_clip(...)` bounds per feature
  - `rsi_current` handoff into Fibonacci feature assembly
  - `atr_source` preference (`atr_window_56` first, else `atr_vals`)
  - feature key set and feature count
- Keep helper internal-only; public SSOT remains `core.strategy.features_asof`.
- Leave `docs/audit/refactor/features_asof/context_map_extract_asof_split_slice1_2026-03-12.md` and `context_map_extract_asof_split_slice2_2026-03-12.md` untouched because they currently contain local user/automation edits outside this slice.
