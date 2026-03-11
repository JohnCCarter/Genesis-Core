## Context Map — features_asof modul-split (slice-6)

### Files to modify

| File                                                     | Purpose                     | Changes Needed                                                                                         |
| -------------------------------------------------------- | --------------------------- | ------------------------------------------------------------------------------------------------------ |
| `src/core/strategy/features_asof.py`                     | SSOT for feature extraction | Keep facade/API, replace nested `_clip` with a thin module-level wrapper delegating to internal helper |
| `src/core/strategy/features_asof_parts/numeric_utils.py` | New extracted helper module | Host stateless numeric clamp/NaN-normalization helper with exact current semantics                     |
| `tests/utils/test_features_asof_cache.py`                | Focused helper semantics    | Prove NaN handling, lower/upper bound clipping, and wrapper/helper parity                              |

### Dependencies (may need updates)

| File                            | Relationship                                                                       |
| ------------------------------- | ---------------------------------------------------------------------------------- |
| `src/core/strategy/evaluate.py` | Imports `extract_features_live` / `extract_features_backtest` from `features_asof` |
| `src/core/strategy/features.py` | Legacy wrapper delegates into `features_asof`                                      |
| `src/core/backtest/engine.py`   | Runtime/backtest integration uses `features_asof` behavior and counters            |

### Test files

| Test                                                        | Coverage                                                                           |
| ----------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `tests/utils/test_features_asof_cache.py`                   | Exact `_clip` / `clip_feature_value` semantics plus existing helper/cache coverage |
| `tests/utils/test_feature_parity.py`                        | Runtime vs precomputed parity remains unchanged                                    |
| `tests/integration/test_precompute_vs_runtime.py`           | Precompute/runtime feature equivalence remains unchanged                           |
| `tests/utils/test_features_asof_cache_key_deterministic.py` | Cache-key determinism remains unchanged                                            |
| `tests/backtest/test_backtest_determinism_smoke.py`         | Determinism replay selector                                                        |
| `tests/governance/test_pipeline_fast_hash_guard.py`         | Pipeline invariant selector                                                        |

### Reference patterns

| File                                                          | Pattern                                                      |
| ------------------------------------------------------------- | ------------------------------------------------------------ |
| `src/core/strategy/components/*.py`                           | Small focused modules with clear responsibility boundaries   |
| `src/core/strategy/features.py`                               | Facade/delegation pattern preserving API surface             |
| `src/core/strategy/features_asof_parts/result_cache_utils.py` | Stateless internal helper module pattern for extracted logic |

### Risk assessment

- [x] Breaking changes to public API (mitigation: keep function signatures and exports unchanged)
- [ ] Database migrations needed
- [ ] Configuration changes required

### Slice-6 decision

- Extract pure helper logic incrementally (no decision logic / no indicator math flow changes).
- Slice-6 extracts only the numeric clamp/NaN-normalization helper into `features_asof_parts/numeric_utils.py` while preserving call sites, cache ownership, metrics ownership, and default runtime behavior in `features_asof.py`.
- `features_asof_parts` is internal-only modularization support; public import surface remains `core.strategy.features_asof`.
- Keep import path `core.strategy.features_asof` as the only public SSOT.
- `src/core/strategy/features_asof_parts/__init__.py` remains unchanged because no package-root export is required for this slice.
- Use dedicated task folder `docs/audit/refactor/features_asof/` for governance artifacts.
