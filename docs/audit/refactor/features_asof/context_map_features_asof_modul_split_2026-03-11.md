## Context Map — features_asof modul-split (slice-5)

### Files to modify

| File                                                          | Purpose                     | Changes Needed                                                                              |
| ------------------------------------------------------------- | --------------------------- | ------------------------------------------------------------------------------------------- |
| `src/core/strategy/features_asof.py`                          | SSOT for feature extraction | Keep facade/API, delegate only result-cache LRU mechanics to extracted internal helper      |
| `src/core/strategy/features_asof_parts/result_cache_utils.py` | New extracted helper module | Host stateless feature-result-cache lookup/store/eviction mechanics                         |
| `tests/utils/test_features_asof_cache.py`                     | Focused cache semantics     | Prove MRU move-on-hit, bounded eviction, and overwrite semantics without return-value drift |

### Dependencies (may need updates)

| File                            | Relationship                                                                       |
| ------------------------------- | ---------------------------------------------------------------------------------- |
| `src/core/strategy/evaluate.py` | Imports `extract_features_live` / `extract_features_backtest` from `features_asof` |
| `src/core/strategy/features.py` | Legacy wrapper delegates into `features_asof`                                      |
| `src/core/backtest/engine.py`   | Runtime/backtest integration uses `features_asof` behavior and counters            |

### Test files

| Test                                                        | Coverage                                                 |
| ----------------------------------------------------------- | -------------------------------------------------------- |
| `tests/utils/test_features_asof_cache.py`                   | LRU semantics for local feature-result-cache             |
| `tests/utils/test_feature_parity.py`                        | Runtime vs precomputed parity remains unchanged          |
| `tests/integration/test_precompute_vs_runtime.py`           | Precompute/runtime feature equivalence remains unchanged |
| `tests/utils/test_features_asof_cache_key_deterministic.py` | Cache-key determinism remains unchanged                  |
| `tests/backtest/test_backtest_determinism_smoke.py`         | Determinism replay selector                              |
| `tests/governance/test_pipeline_fast_hash_guard.py`         | Pipeline invariant selector                              |

### Reference patterns

| File                                | Pattern                                                    |
| ----------------------------------- | ---------------------------------------------------------- |
| `src/core/strategy/components/*.py` | Small focused modules with clear responsibility boundaries |
| `src/core/strategy/features.py`     | Facade/delegation pattern preserving API surface           |

### Risk assessment

- [x] Breaking changes to public API (mitigation: keep function signatures and exports unchanged)
- [ ] Database migrations needed
- [ ] Configuration changes required

### Slice-5 decision

- Extract pure helper logic incrementally (no decision logic / no indicator math flow changes).
- Slice-5 extracts only feature-result-cache LRU mechanics into `features_asof_parts/result_cache_utils.py` while preserving cache-key ownership, metrics ownership, `_feature_cache` ownership, and default runtime behavior in `features_asof.py`.
- `features_asof_parts` is internal-only modularization support; public import surface remains `core.strategy.features_asof`.
- Keep import path `core.strategy.features_asof` as the only public SSOT.
- Use dedicated task folder `docs/audit/refactor/features_asof/` for governance artifacts.
