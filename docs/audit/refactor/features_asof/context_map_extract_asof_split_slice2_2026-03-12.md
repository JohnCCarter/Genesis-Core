## Context Map — extract_asof split (slice-2)

### Files to modify

| File                                                             | Purpose                            | Changes Needed                                                                                                |
| ---------------------------------------------------------------- | ---------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `src/core/strategy/features_asof.py`                             | SSOT facade for feature extraction | Replace the inline indicator-state assembly inside `_extract_asof(...)` with a thin internal delegation call  |
| `src/core/strategy/features_asof_parts/indicator_state_utils.py` | New internal helper module         | Host the extracted indicator-state assembly logic with exact no-behavior-change semantics                     |
| `tests/utils/test_features_asof_indicator_state.py`              | Focused helper verification        | Add focused coverage for RSI/BB/ATR/volatility-shift state semantics without changing public runtime behavior |

### Dependencies (may need updates)

| File                                                                | Relationship                                                                                            |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `src/core/strategy/features_asof_parts/extraction_context_utils.py` | Slice-1 helper provides prep inputs consumed by the new indicator-state helper                          |
| `src/core/strategy/features_asof_parts/precompute_utils.py`         | Existing remap helper shapes the precomputed inputs used by indicator-state assembly                    |
| `src/core/strategy/features_asof_parts/atr_percentile_utils.py`     | Downstream feature/meta assembly still consumes ATR outputs from the indicator-state helper             |
| `src/core/backtest/engine.py`                                       | Backtest integration depends on stable `_global_index` and unchanged feature parity via `features_asof` |
| `src/core/strategy/evaluate.py`                                     | Imports public feature extraction wrappers and depends on unchanged facade semantics                    |

### Test files

| Test                                                                                                                      | Coverage                                                                                     |
| ------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `tests/utils/test_features_asof_indicator_state.py`                                                                       | Dedicated proof for RSI fast/slow path, ATR/ATR14 semantics, and volatility-shift derivation |
| `tests/utils/test_feature_parity.py::test_runtime_vs_precomputed_features`                                                | Runtime vs precomputed parity remains unchanged                                              |
| `tests/integration/test_precompute_vs_runtime.py::test_precompute_features_match_runtime`                                 | Precompute/runtime feature equivalence remains unchanged                                     |
| `tests/utils/test_features.py::test_extract_features_atr14_is_true_atr14_even_when_atr_period_differs`                    | `atr_14` backcompat semantics remain unchanged                                               |
| `tests/utils/test_features.py::test_extract_features_stub_shapes`                                                         | Feature shape remains unchanged                                                              |
| `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed` | Cache determinism remains unchanged                                                          |
| `tests/backtest/test_backtest_determinism_smoke.py`                                                                       | Determinism replay selector                                                                  |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`                | Pipeline invariant selector                                                                  |
| `tests/governance/test_import_smoke_backtest_optuna.py`                                                                   | Import smoke around backtest/optuna surfaces remains unchanged                               |

### Reference patterns

| File                                                                | Pattern                                                              |
| ------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `src/core/strategy/features_asof_parts/extraction_context_utils.py` | Internal dataclass-based helper returning caller-consumed prep state |
| `src/core/strategy/features_asof_parts/fibonacci_context_utils.py`  | Internal orchestration helper with dependency injection from facade  |
| `src/core/strategy/features_asof_parts/result_cache_utils.py`       | Stateless helper module pattern for extracted logic                  |
| `src/core/strategy/features_asof.py`                                | Thin facade wrappers delegating to internal helper implementations   |

### Risk assessment

- [x] Breaking changes to public API (mitigation: keep all public signatures/exports unchanged)
- [ ] Database migrations needed
- [ ] Configuration changes required

### Slice-2 decision

- Extract only the indicator-state assembly segment that computes or derives:
  - RSI current / lag1
  - Bollinger last-3 position window
  - ATR current-period window and trailing percentile source
  - true `atr_14` backcompat value
  - ATR long and volatility-shift current / last-3 state
- Do **not** move base feature assembly, fib assembly, HTF/LTF context, or meta/result build in this slice.
- Preserve exact semantics for:
  - FAST_HITS / SLOW_HITS accounting
  - precomputed RSI fast path
  - Bollinger last-3 assembly
  - `atr_period` vs `atr_14` backcompat split
  - `current_atr_used` downstream source continuity via `atr_vals`
  - volatility-shift fallback when precomputed values are absent
- Keep helper internal-only; public SSOT remains `core.strategy.features_asof`.
- Leave `docs/audit/refactor/features_asof/context_map_extract_asof_split_slice1_2026-03-12.md` untouched because it currently has a local user/automation edit outside this slice.
