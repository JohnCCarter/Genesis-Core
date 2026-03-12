# Context Map — server modul split

## Current target

Start `feature/server-modul-split` with the smallest safe extraction from the monolithic `src/core/server.py`.

## Files to modify

| File                                                                         | Purpose                                      | Changes needed                                                                                  |
| ---------------------------------------------------------------------------- | -------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| `src/core/server.py`                                                         | FastAPI app assembly and many route handlers | Remove inline `/strategy/evaluate` route implementation and include a dedicated strategy router |
| `src/core/server_strategy_api.py`                                            | New slice-1 router module                    | Host `/strategy/evaluate` route and preserve current validation + response semantics            |
| `tests/integration/test_ui_endpoints.py`                                     | Route parity lock                            | Prove preserved `evaluate_pipeline(...)` delegation defaults and invalid-candles edge semantics |
| `docs/audit/refactor/server/command_packet_server_modul_split_2026-03-12.md` | Commit contract                              | Record slice scope, gates, and constraints                                                      |
| `docs/audit/refactor/server/context_map_server_modul_split_2026-03-12.md`    | Dependency/test map                          | Capture affected files, tests, and risks                                                        |

## Dependencies

| File                                                              | Relationship                                                  |
| ----------------------------------------------------------------- | ------------------------------------------------------------- |
| `src/core/strategy/evaluate.py`                                   | `strategy_evaluate` delegates to `evaluate_pipeline(...)`     |
| `src/core/server_config_api.py`                                   | Existing router include pattern to mirror                     |
| `core.config.authority`, `core.config.settings`, Bitfinex helpers | Still owned by `src/core/server.py`, out of scope for slice 1 |

## Test files

| Test                                                                                                                      | Coverage                                                                                                                       |
| ------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `tests/integration/test_ui_endpoints.py`                                                                                  | Direct `/strategy/evaluate` contract, invalid-candles payloads, route-delegation parity, plus neighboring UI endpoint coverage |
| `tests/integration/test_config_endpoints.py`                                                                              | App assembly smoke: confirms `core.server.app` still exposes `/config/runtime*` after router wiring                            |
| `tests/utils/test_health.py`                                                                                              | App-level health smoke                                                                                                         |
| `tests/backtest/test_backtest_determinism_smoke.py`                                                                       | Canonical determinism replay required by RESEARCH governance                                                                   |
| `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic`             | Pipeline determinism signal for route delegate path                                                                            |
| `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed` | Feature cache invariance guard                                                                                                 |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`                | Pipeline invariant guard                                                                                                       |
| `bandit -r src -c bandit.yaml`                                                                                            | Security scan required by repo-local Python engineering skill                                                                  |

## Reference patterns

| File                            | Pattern                                                                   |
| ------------------------------- | ------------------------------------------------------------------------- |
| `src/core/server_config_api.py` | Existing `APIRouter` extraction pattern already included by `core.server` |

## Risk assessment

- [x] Public API/HTTP contract risk: `/strategy/evaluate` payload and invalid-candles response must remain byte-for-byte equivalent in structure
- [x] App wiring risk: adding/importing a new router must not break existing `app.include_router(...)` behavior
- [ ] Database migrations needed
- [ ] Configuration changes required

## First safe slice rationale

`src/core/server.py` is the main monolith. `/strategy/evaluate` is a clean first slice because:

1. It already has concentrated test coverage in `tests/integration/test_ui_endpoints.py`.
2. It depends mainly on `evaluate_pipeline(...)`, not on the broader paper/account side effects.
3. There is an existing router-extraction pattern in `src/core/server_config_api.py` to mirror.
4. Route-parity can be locked with a tiny monkeypatch test and one extra invalid-length payload case.

## Verification snapshot

- Formatter/lint on touched runtime and route-test files: `PASS`
- Canonical determinism replay: `PASS`
- Route/app/invariant pytest selectors: `PASS`
- `bandit -r src -c bandit.yaml`: `PASS` with warning only for an existing acknowledged `nosec` (`B608`), no failed findings
