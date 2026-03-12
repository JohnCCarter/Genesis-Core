## Context Map — extract_asof split (slice-1)

### Files to modify

| File                                                                | Purpose                             | Changes Needed                                                                                                     |
| ------------------------------------------------------------------- | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `src/core/strategy/features_asof.py`                                | SSOT facade for feature extraction  | Replace the inline context/index/precompute setup inside `_extract_asof(...)` with a thin internal delegation call |
| `src/core/strategy/features_asof_parts/extraction_context_utils.py` | New internal helper module          | Host the extracted context/index/precompute preparation logic with exact no-behavior-change semantics              |
| `tests/utils/test_features_asof_extraction_context.py`              | Focused helper/wrapper verification | Add focused coverage for remap/index/ATR-period/precompute fallback semantics without changing public runtime behavior |

### Dependencies (may need updates)

| File                                                        | Relationship                                                                                                                 |
| ----------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `src/core/strategy/evaluate.py`                             | Imports `extract_features_live` / `extract_features_backtest` from `features_asof` and depends on unchanged facade semantics |
| `src/core/strategy/features.py`                             | Legacy wrapper delegates into `features_asof`; public surface must remain unchanged                                          |
| `src/core/backtest/engine.py`                               | Backtest integration relies on stable `_global_index` / `precomputed_features` handling through `features_asof`              |
| `src/core/strategy/features_asof_parts/precompute_utils.py` | Existing helper used by extracted block for remap semantics                                                                  |

### Test files

| Test                                                                                                                      | Coverage                                                          |
| ------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| `tests/utils/test_features_asof_extraction_context.py`                                                                    | Dedicated proof for remap/index/ATR-period/precompute fallback and caller-owned warning semantics |
| `tests/utils/test_features_asof_precompute_logging.py`                                                                    | Existing precompute logging state remains caller-owned in `features_asof.py` |
| `tests/utils/test_feature_parity.py::test_runtime_vs_precomputed_features`                                                | Runtime vs precomputed parity remains unchanged                   |
| `tests/integration/test_precompute_vs_runtime.py::test_precompute_features_match_runtime`                                 | Precompute/runtime feature equivalence remains unchanged          |
| `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed` | Cache determinism remains unchanged                               |
| `tests/backtest/test_backtest_determinism_smoke.py`                                                                       | Determinism replay selector                                       |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`                | Pipeline invariant selector                                       |
| `tests/governance/test_import_smoke_backtest_optuna.py`                                                                   | Import smoke around backtest/optuna surfaces remains unchanged    |

### Reference patterns

| File                                                               | Pattern                                                             |
| ------------------------------------------------------------------ | ------------------------------------------------------------------- |
| `src/core/strategy/features_asof_parts/precompute_utils.py`        | Small extracted helper with exact fallback semantics                |
| `src/core/strategy/features_asof_parts/fibonacci_context_utils.py` | Internal orchestration helper with dependency injection from facade |
| `src/core/strategy/features_asof_parts/result_cache_utils.py`      | Stateless helper module pattern for extracted logic                 |
| `src/core/strategy/features_asof.py`                               | Thin facade wrappers delegating to internal helper implementations  |

### Risk assessment

- [x] Breaking changes to public API (mitigation: keep all public signatures/exports unchanged)
- [ ] Database migrations needed
- [ ] Configuration changes required

### Slice-1 decision

- Extract only the `_extract_asof(...)` preparation segment that establishes window arrays, lookup/remap semantics, and ATR-period selection.
- Do **not** move indicator calculation, fib assembly, HTF/LTF context, or meta/result build in this slice.
- Preserve exact semantics for:
  - `lookup_idx = (config or {}).get("_global_index", asof_bar)`
  - `window_start_idx`
  - `pre = dict((config or {}).get("precomputed_features") or {})`
  - `_remap_precomputed_features(...)`
  - `pre_idx`
  - `thresholds.signal_adaptation.atr_period` fallback to `14`
  - `GENESIS_PRECOMPUTE_FEATURES` warning/fallback path
- Keep `_PRECOMPUTE_WARN_ONCE` in `features_asof.py`; helper may only return a warning signal, not own global warning state.
- Keep `features_asof_parts` internal-only; public SSOT remains `core.strategy.features_asof`.
