## Context Map — extract_asof split (slice-4)

### Files to modify

| File                                                  | Purpose                            | Changes Needed                                                                                                       |
| ----------------------------------------------------- | ---------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `src/core/strategy/features_asof.py`                  | SSOT facade for feature extraction | Replace the inline meta assembly inside `_extract_asof(...)` with a thin internal delegation call                    |
| `src/core/strategy/features_asof_parts/meta_utils.py` | New internal helper module         | Host the extracted meta assembly logic with exact no-behavior-change semantics                                       |
| `tests/utils/test_features_asof_meta_utils.py`        | Focused helper verification        | Add focused coverage for meta keys, reason/default semantics, ATR transparency fields, and feature-count propagation |

### Dependencies (may need updates)

| File                                                               | Relationship                                                                                                                 |
| ------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| `src/core/strategy/features_asof_parts/base_feature_utils.py`      | Slice-3 helper provides `atr_percentiles` and base features consumed by the new meta helper                                  |
| `src/core/strategy/features_asof_parts/fibonacci_feature_utils.py` | Fibonacci status remains an upstream input passed through into the meta helper                                               |
| `src/core/strategy/features_asof_parts/fibonacci_context_utils.py` | HTF/LTF context outputs and selector metadata remain upstream inputs passed through into the meta helper                     |
| `src/core/backtest/engine.py`                                      | Backtest integration depends on stable meta fields like `current_atr`, `atr_percentiles`, and fibonacci context availability |
| `src/core/strategy/evaluate.py`                                    | Imports public feature extraction wrappers and depends on unchanged facade/meta semantics                                    |

### Test files

| Test                                                                                                                      | Coverage                                                                                              |
| ------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `tests/utils/test_features_asof_meta_utils.py`                                                                            | Dedicated proof for meta key set, reason semantics, ATR transparency fields, and passthrough behavior |
| `tests/utils/test_features.py::test_extract_features_atr14_is_true_atr14_even_when_atr_period_differs`                    | `current_atr`, `current_atr_used`, and `atr_period_used` semantics remain unchanged                   |
| `tests/utils/test_features.py::test_extract_features_stub_shapes`                                                         | Feature count and version flags remain unchanged                                                      |
| `tests/utils/test_features_asof_fib_error_handling.py`                                                                    | Downstream fib/HTF/LTF meta error behavior remains unchanged                                          |
| `tests/utils/test_feature_parity.py::test_runtime_vs_precomputed_features`                                                | Runtime vs precomputed parity remains unchanged                                                       |
| `tests/integration/test_precompute_vs_runtime.py::test_precompute_features_match_runtime`                                 | Precompute/runtime feature equivalence remains unchanged                                              |
| `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed` | Cache determinism remains unchanged                                                                   |
| `tests/backtest/test_backtest_determinism_smoke.py`                                                                       | Determinism replay selector                                                                           |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`                | Pipeline invariant selector                                                                           |
| `tests/governance/test_import_smoke_backtest_optuna.py`                                                                   | Import smoke around backtest/optuna surfaces remains unchanged                                        |

### Reference patterns

| File                                                                | Pattern                                                                            |
| ------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `src/core/strategy/features_asof_parts/extraction_context_utils.py` | Internal dataclass-based helper returning caller-consumed prep state               |
| `src/core/strategy/features_asof_parts/indicator_state_utils.py`    | Internal dataclass-based helper returning caller-consumed indicator state          |
| `src/core/strategy/features_asof_parts/base_feature_utils.py`       | Internal helper returning caller-consumed bundle while preserving facade ownership |
| `src/core/strategy/features_asof.py`                                | Thin facade wrappers delegating to internal helper implementations                 |

### Risk assessment

- [x] Breaking changes to public API (mitigation: keep all public signatures/exports unchanged)
- [ ] Database migrations needed
- [ ] Configuration changes required

### Slice-4 decision

- Extract only the meta assembly segment that computes or derives:
  - `meta["versions"]`
  - `meta["reasons"]`
  - `feature_count`
  - `current_atr`
  - `current_atr_used`
  - `atr_period_used`
  - `atr_percentiles`
  - passthrough of `fibonacci_features`, `htf_fibonacci`, `ltf_fibonacci`, and `htf_selector`
- Keep upstream Fibonacci feature assembly, HTF/LTF context fetching, result tuple build, cache store, and all public wrappers inside `features_asof.py` in this slice.
- Preserve exact semantics for:
  - `FIB_FEATURES_CONTEXT_ERROR` default reason when fib status is unavailable/false
  - `current_atr` alignment with `features["atr_14"]`
  - `current_atr_used` deriving from the tail of `atr_vals` when present
  - `feature_count == len(features)`
  - version flags and context/meta key names
- Keep helper internal-only; public SSOT remains `core.strategy.features_asof`.
- Leave `docs/audit/refactor/features_asof/context_map_extract_asof_split_slice1_2026-03-12.md` and `context_map_extract_asof_split_slice3_2026-03-12.md` untouched because they currently contain local user/automation edits outside this slice.
