# Context Map — server API package move

## Files to Modify

| File                                         | Purpose                                  | Changes Needed                                                                                              |
| -------------------------------------------- | ---------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `src/core/server.py`                         | FastAPI assembly + compatibility surface | Import routers from `core.api.*` instead of scattered root modules while preserving aliases                 |
| `src/core/api/__init__.py`                   | New package marker                       | Establish dedicated API package                                                                             |
| `src/core/api/*.py`                          | Route modules                            | Relocate `server_*_api.py` modules into cohesive API package with updated intra-package imports             |
| `src/core/server_*_api.py`                   | Compatibility import surface             | Convert each old root module into a module-alias stub that resolves to the exact `core.api.*` module object |
| `tests/integration/test_ui_endpoints.py`     | Route alias/parity proof                 | Preserve old imports, add old/new module identity assertions, and keep existing route proofs                |
| `tests/integration/test_config_endpoints.py` | Config endpoint tests                    | Preserve old import proof and add compatibility proof against `core.api.config`                             |
| `tests/utils/test_observability.py`          | Info route tests                         | Preserve old import proof and add compatibility proof against `core.api.info`                               |
| `src/core/config/validator.py`               | Runtime-validation helper docs           | Refresh legacy docstring reference away from removed root module path                                       |
| `docs/architecture/ARCHITECTURE_VISUAL.md`   | Live architecture doc                    | Update route-module path references to `src/core/api/*`                                                     |

## Dependencies (may need updates)

| File                                          | Relationship                                                                           |
| --------------------------------------------- | -------------------------------------------------------------------------------------- |
| `src/core/server.py`                          | Re-exports aliases that tests monkeypatch through `core.server`                        |
| `src/core/api/paper.py`                       | Depends on `core.server` for late-bound helper resolution and on info whitelist module |
| `src/core/api/public.py`                      | Depends on `core.server` for late-bound exchange-client access                         |
| `src/core/server_*_api.py`                    | Must remain importable aliases that resolve to the same module objects as `core.api.*` |
| `tests/utils/test_health.py`                  | Validates shared `_AUTH` / logger behavior via `core.server`                           |
| `tests/integration/test_account_endpoints.py` | Exercises assembled app routes and account router behavior                             |

## Test Files

| Test                                                                                                                      | Coverage                                                                |
| ------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| `tests/integration/test_ui_endpoints.py`                                                                                  | direct/route parity, alias identity, route count, paper/public behavior |
| `tests/integration/test_config_endpoints.py`                                                                              | config endpoint wiring and authority passthrough                        |
| `tests/utils/test_observability.py`                                                                                       | info endpoint passthrough                                               |
| `tests/utils/test_health.py`                                                                                              | shared `_AUTH` and logger identity                                      |
| `tests/integration/test_account_endpoints.py`                                                                             | account route smoke coverage                                            |
| `tests/governance/test_import_smoke_backtest_optuna.py`                                                                   | baseline import-smoke pattern; extend/consult for package relocation    |
| `tests/backtest/test_backtest_determinism_smoke.py`                                                                       | determinism replay guard                                                |
| `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed` | feature cache invariance                                                |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`                | pipeline invariant                                                      |

## Reference Patterns

| File                                     | Pattern                                                                                   |
| ---------------------------------------- | ----------------------------------------------------------------------------------------- |
| `src/core/server.py`                     | Compatibility aliasing + `include_router` assembly                                        |
| `src/core/server_paper_api.py`           | Existing module contract that must survive after implementation moves via module aliasing |
| `tests/integration/test_ui_endpoints.py` | Identity and single-registration assertions plus old/new module-object parity proofs      |

## Risk Assessment

- [x] Breaking changes to public API possible if imports/aliases drift
- [ ] Database migrations needed
- [ ] Configuration changes required
- [x] Import-cycle risk exists because route modules resolve helpers through `core.server`
- [x] Old root-module import contracts must remain valid even after implementation moves to `core.api`, including monkeypatching on old module paths
- [x] Historical audit docs should remain untouched as evidence, even if they mention old file paths
