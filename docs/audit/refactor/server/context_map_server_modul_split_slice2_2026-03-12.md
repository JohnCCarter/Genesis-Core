# Context Map — server modul split slice 2

## Current target

Continue `feature/server-modul-split` with the next smallest safe extraction from `src/core/server.py`.

## Files to modify

| File                                                                                | Purpose                                      | Changes needed                                                                                                      |
| ----------------------------------------------------------------------------------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `src/core/server.py`                                                                | FastAPI app assembly and remaining route set | Remove inline `/paper/whitelist` and `/observability/dashboard` implementations and include a dedicated info router |
| `src/core/server_info_api.py`                                                       | New slice-2 router module                    | Host the two read-only info routes and preserve current response semantics                                          |
| `tests/integration/test_ui_endpoints.py`                                            | Route contract lock                          | Add a focused `/paper/whitelist` route assertion for sorted whitelist semantics                                     |
| `tests/utils/test_observability.py`                                                 | Route passthrough lock                       | Prove `/observability/dashboard` returns the exact sentinel payload from `get_dashboard()`                          |
| `docs/audit/refactor/server/command_packet_server_modul_split_slice2_2026-03-12.md` | Commit contract                              | Record slice scope, gates, and constraints                                                                          |
| `docs/audit/refactor/server/context_map_server_modul_split_slice2_2026-03-12.md`    | Dependency/test map                          | Capture affected files, tests, and risks                                                                            |

## Dependencies

| File                            | Relationship                                                                                          |
| ------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `src/core/server_config_api.py` | Existing router include pattern to mirror                                                             |
| `core.observability.metrics`    | `observability_dashboard` delegates directly to `get_dashboard()`                                     |
| `src/core/server_info_api.py`   | Owns `TEST_SPOT_WHITELIST` so `paper_whitelist` and later paper routes share a single source of truth |

## Test files

| Test                                                                                                                      | Coverage                                                                           |
| ------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `tests/integration/test_ui_endpoints.py`                                                                                  | `/paper/whitelist` route contract + neighboring app endpoint coverage              |
| `tests/utils/test_observability.py`                                                                                       | Direct `/observability/dashboard` route contract + passthrough proof               |
| `tests/integration/test_config_endpoints.py`                                                                              | App assembly smoke: confirms `core.server.app` still exposes runtime config routes |
| `tests/utils/test_health.py`                                                                                              | App-level health smoke                                                             |
| `tests/backtest/test_backtest_determinism_smoke.py`                                                                       | Canonical determinism replay required by RESEARCH governance                       |
| `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic`             | Pipeline determinism signal for route assembly path                                |
| `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed` | Feature cache invariance guard                                                     |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`                | Pipeline invariant guard                                                           |
| `bandit -r src -c bandit.yaml`                                                                                            | Security scan required by repo-local Python engineering skill                      |

## Reference patterns

| File                              | Pattern                                                                                |
| --------------------------------- | -------------------------------------------------------------------------------------- |
| `src/core/server_config_api.py`   | Existing `APIRouter` extraction pattern already included by `core.server`              |
| `src/core/server_strategy_api.py` | Fresh slice-1 extraction pattern for preserving route contracts in a new router module |

## Risk assessment

- [x] Public API/HTTP contract risk: `/paper/whitelist` and `/observability/dashboard` must preserve paths and payload structures
- [x] App wiring risk: adding/importing a second extracted router must not break existing `app.include_router(...)` behavior
- [ ] Database migrations needed
- [ ] Configuration changes required

## First safe slice rationale

This slice stays low-complexity because:

1. Both endpoints are read-only GET handlers with tiny bodies.
2. `/observability/dashboard` already has focused endpoint coverage in `tests/utils/test_observability.py`.
3. `/paper/whitelist` only returns a sorted constant-derived payload, so a tiny route smoke test can lock parity.
4. The extraction pattern can mirror the already-verified router split from slice 1 while keeping `TEST_SPOT_WHITELIST` as a single shared constant source.

## Verification snapshot

- Formatter/lint on touched runtime and route-test files: `PASS`
- Focused route/app/invariant pytest selectors plus canonical determinism replay: `PASS`
- `bandit -r src -c bandit.yaml`: `PASS` with warning only for an existing acknowledged `nosec` (`B608`), no failed findings
