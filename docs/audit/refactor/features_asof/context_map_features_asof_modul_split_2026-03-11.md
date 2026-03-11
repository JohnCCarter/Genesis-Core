## Context Map — features_asof modul-split (slice-2)

### Files to modify

| File                                                        | Purpose                     | Changes Needed                                                      |
| ----------------------------------------------------------- | --------------------------- | ------------------------------------------------------------------- |
| `src/core/strategy/features_asof.py`                        | SSOT for feature extraction | Keep facade/API, delegate selected hash helpers to extracted module |
| `src/core/strategy/features_asof_parts/hash_utils.py`       | New extracted helper module | Host pure hash/config helper logic used by cache-key generation     |
| `src/core/strategy/features_asof_parts/precompute_utils.py` | New extracted helper module | Host remap helper logic for precomputed feature windows             |
| `src/core/strategy/features_asof_parts/__init__.py`         | Package entrypoint          | Export extracted helpers for explicit internal imports              |

### Dependencies (may need updates)

| File                            | Relationship                                                                       |
| ------------------------------- | ---------------------------------------------------------------------------------- |
| `src/core/strategy/evaluate.py` | Imports `extract_features_live` / `extract_features_backtest` from `features_asof` |
| `src/core/strategy/features.py` | Legacy wrapper delegates into `features_asof`                                      |
| `src/core/backtest/engine.py`   | Runtime/backtest integration uses `features_asof` behavior and counters            |

### Test files

| Test                                                        | Coverage                                 |
| ----------------------------------------------------------- | ---------------------------------------- |
| `tests/utils/test_features_asof_cache.py`                   | Cache key behavior and helper semantics  |
| `tests/utils/test_features_asof_cache_key_deterministic.py` | Cross-process deterministic key behavior |
| `tests/utils/test_features_asof_fast_hash_env_case.py`      | Fast-hash env behavior                   |
| `tests/backtest/test_backtest_determinism_smoke.py`         | Determinism replay selector              |
| `tests/governance/test_pipeline_fast_hash_guard.py`         | Pipeline invariant selector              |

### Reference patterns

| File                                | Pattern                                                    |
| ----------------------------------- | ---------------------------------------------------------- |
| `src/core/strategy/components/*.py` | Small focused modules with clear responsibility boundaries |
| `src/core/strategy/features.py`     | Facade/delegation pattern preserving API surface           |

### Risk assessment

- [x] Breaking changes to public API (mitigation: keep function signatures and exports unchanged)
- [ ] Database migrations needed
- [ ] Configuration changes required

### Slice-2 decision

- Extract pure helper logic incrementally (no decision logic / no indicator math flow changes).
- Slice-2 extends extraction with precompute remap helper in `features_asof_parts/precompute_utils.py` while preserving facade wrappers in `features_asof.py`.
- Keep import path `core.strategy.features_asof` as the only public SSOT.
- Use dedicated task folder `docs/audit/refactor/features_asof/` for governance artifacts.
