# Context Map — server modul split slice 5

## Current target

Continue `feature/server-modul-split` with the next smallest safe extraction from `src/core/server.py`.

## Files to modify

| File                                                                                | Purpose                     | Changes needed                                                                          |
| ----------------------------------------------------------------------------------- | --------------------------- | --------------------------------------------------------------------------------------- |
| `src/core/server.py`                                                                | FastAPI app assembly        | Remove inline auth/account route implementations and include a dedicated account router |
| `src/core/server_account_api.py`                                                    | New slice-5 router module   | Host `/auth/check` and `/account/*` routes plus shared account cache state              |
| `tests/integration/test_ui_endpoints.py`                                            | Auth compatibility lock     | Preserve direct `auth_check()` compatibility and any needed cache/alias proof           |
| `tests/integration/test_account_endpoints.py`                                       | Account route contract lock | Keep filtering and exception-redaction proofs green under extracted routing             |
| `docs/audit/refactor/server/command_packet_server_modul_split_slice5_2026-03-12.md` | Commit contract             | Record slice scope, gates, and constraints                                              |
| `docs/audit/refactor/server/context_map_server_modul_split_slice5_2026-03-12.md`    | Dependency/test map         | Capture affected files, tests, and risks                                                |

## Dependencies

| File                                     | Relationship                                                                                            |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `core.io.bitfinex.read_helpers`          | `auth_check` and `/account/*` routes delegate to `get_wallets()`, `get_positions()`, and `get_orders()` |
| `src/core/server.py`                     | Current owner of `_ACCOUNT_CACHE` and `_ACCOUNT_TTL`; likely compatibility alias surface                |
| `src/core/server_status_api.py`          | Existing alias + include pattern for small compatibility-preserving extractions                         |
| `tests/integration/test_ui_endpoints.py` | Directly imports `auth_check` from `core.server` and monkeypatches `srv.bfx_read.*`                     |

## Test files

| Test                                                                                                                      | Coverage                                                                                        |
| ------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| `tests/integration/test_ui_endpoints.py`                                                                                  | Direct `auth_check()` compatibility through `core.server`                                       |
| `tests/integration/test_account_endpoints.py`                                                                             | `/account/wallets`, `/account/positions`, `/account/orders` route filtering and error redaction |
| `tests/backtest/test_backtest_determinism_smoke.py`                                                                       | Canonical determinism replay required by RESEARCH governance                                    |
| `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic`             | Pipeline determinism guard after server wiring change                                           |
| `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed` | Feature cache invariance guard                                                                  |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`                | Pipeline invariant guard                                                                        |
| `bandit -r src -c bandit.yaml`                                                                                            | Security scan required by repo-local policy                                                     |

## Reference patterns

| File                            | Pattern                                                                       |
| ------------------------------- | ----------------------------------------------------------------------------- |
| `src/core/server_status_api.py` | Small extracted router with compatibility aliasing and dedicated shared state |
| `src/core/server_info_api.py`   | Router extraction plus top-level symbol rebinding in `core.server`            |
| `src/core/server_models_api.py` | Smallest recent single-route extraction with app include wiring               |

## Risk assessment

- [x] Public API/HTTP contract risk: `/auth/check` and `/account/*` must preserve exact response semantics
- [x] App wiring risk: adding another extracted router must not disturb existing router includes
- [x] Compatibility risk: direct `core.server.auth_check` imports and shared `_ACCOUNT_CACHE` aliases may need to remain stable
- [x] Observability risk: exception paths on `/account/*` must continue redacting internal exception details from responses
- [ ] Database migrations needed
- [ ] Configuration changes required

## Slice rationale

This slice stays contained because:

1. The four routes already form a logical read-only cluster around account inspection.
2. They share `_ACCOUNT_CACHE` and `_ACCOUNT_TTL`, so grouping them removes a coherent block instead of fragmenting shared state.
3. Existing tests already lock the critical route behavior for auth-check, account filtering, and exception redaction.
4. The monkeypatch surface is likely preservable because all helpers come from the shared `core.io.bitfinex.read_helpers` module object.

## Verification emphasis

- `/auth/check` needs both direct-call and route-level proof under the same `srv.bfx_read` monkeypatch setup.
- Shared cache compatibility must be proven by alias identity for `core.server._ACCOUNT_CACHE` against `core.server_account_api._ACCOUNT_CACHE`, not only by matching values.
- The extracted module must keep `read_helpers` as module alias `bfx_read`, not symbol-level imports.

## Verification snapshot

- Formatter parity held after extraction: `black --check` passed for `src/core/server.py`, `src/core/server_account_api.py`, `tests/integration/test_ui_endpoints.py`, and `tests/integration/test_account_endpoints.py`.
- Lint parity held for the same slice files: `ruff check` passed with no findings.
- `tests/integration/test_ui_endpoints.py` now locks:
  - direct-call and route-level parity for `/auth/check` under monkeypatched `srv.bfx_read`
  - alias identity for `auth_check`
  - alias identity for `_ACCOUNT_CACHE` and route-function symbols in `core.server`
- `tests/integration/test_account_endpoints.py` remained green for:
  - `/account/wallets` exchange-only filtering and exception redaction
  - `/account/positions` TEST-symbol filtering
  - `/account/orders` TEST-symbol filtering
- Governance selectors passed via:
  - `tests/backtest/test_backtest_determinism_smoke.py`
  - `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic`
  - `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
  - `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- Security scan passed: `bandit -r src -c bandit.yaml -q` produced only the existing acknowledged `B608` `nosec` warning and no failed findings.
