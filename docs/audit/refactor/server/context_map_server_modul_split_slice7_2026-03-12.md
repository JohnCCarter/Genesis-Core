# Context Map — server modul split slice 7

## Current target

Continue `feature/server-modul-split` with the next smallest safe extraction from `src/core/server.py`.

## Files to modify

| File                                                                                | Purpose                      | Changes needed                                                                                |
| ----------------------------------------------------------------------------------- | ---------------------------- | --------------------------------------------------------------------------------------------- |
| `src/core/server.py`                                                                | FastAPI app assembly         | Remove inline `/public/candles`, rebind compatibility aliases, and include a dedicated router |
| `src/core/server_public_api.py`                                                     | New slice-7 router module    | Host `/public/candles` plus shared candles cache state                                        |
| `tests/integration/test_ui_endpoints.py`                                            | Public candles compatibility | Keep route contract proof and add alias/cache/monkeypatch parity coverage                     |
| `docs/audit/refactor/server/command_packet_server_modul_split_slice7_2026-03-12.md` | Commit contract              | Record slice scope, gates, and constraints                                                    |
| `docs/audit/refactor/server/context_map_server_modul_split_slice7_2026-03-12.md`    | Dependency/test map          | Capture affected files, tests, and risks                                                      |

## Dependencies

| File                                     | Relationship                                                                                                 |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `core.io.bitfinex.exchange_client`       | `/public/candles` delegates to `get_exchange_client().public_request()`                                      |
| `src/core/server.py`                     | Current owner of `public_candles()`, `_CANDLES_CACHE`, `_CANDLES_TTL`, and the legacy monkeypatch surface    |
| `tests/integration/test_ui_endpoints.py` | Existing direct test imports `public_candles` from `core.server` and monkeypatches `srv.get_exchange_client` |

## Test files

| Test                                                                                                                      | Coverage                                                                                              |
| ------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `tests/integration/test_ui_endpoints.py`                                                                                  | Direct `public_candles()` compatibility, route contract, and monkeypatch parity through `core.server` |
| `tests/backtest/test_backtest_determinism_smoke.py`                                                                       | Canonical determinism replay required by RESEARCH governance                                          |
| `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic`             | Pipeline determinism guard after server wiring change                                                 |
| `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed` | Cache-key determinism guard for feature hashing across `PYTHONHASHSEED`                               |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`                | Pipeline invariant guard                                                                              |
| `bandit -r src -c bandit.yaml`                                                                                            | Security scan required by repo-local policy                                                           |

## Reference patterns

| File                             | Pattern                                                                         |
| -------------------------------- | ------------------------------------------------------------------------------- |
| `src/core/server_models_api.py`  | Single-route extraction with compatibility aliasing and router include          |
| `src/core/server_account_api.py` | Shared-state extraction with cache alias preservation through `core.server`     |
| `src/core/server_ui_api.py`      | Recent single-route extraction with explicit alias and route-registration proof |

## Risk assessment

- [x] Public API/HTTP contract risk: `/public/candles` must preserve exact query handling and OHLCV response shape
- [x] App wiring risk: adding another extracted router must not disturb existing router includes
- [x] Compatibility risk: direct `core.server.public_candles` imports plus `_CANDLES_CACHE` alias identity may need to remain stable
- [x] Test-surface risk: legacy `core.server.get_exchange_client` monkeypatch behavior may break if the extracted module binds helpers too early
- [ ] Database migrations needed
- [ ] Configuration changes required

## Slice rationale

This slice stays contained because:

1. `/public/candles` is a single read-only route with local normalization logic.
2. Its only shared state is the small in-module candles cache and TTL.
3. Existing integration coverage already proves the normalized response keys and the direct import surface.
4. The remaining paper routes are more entangled with auth, wallets, and order semantics, so extracting candles first keeps risk lower.

## Verification emphasis

- `/public/candles` needs both direct-call and route-level parity under the same monkeypatched `core.server.get_exchange_client` surface.
- Compatibility proof must lock `core.server.public_candles is core.server_public_api.public_candles` and `core.server.public_router is core.server_public_api.router` if extracted under that module name.
- Shared cache compatibility must be proven by alias identity for `_CANDLES_CACHE` and stable equality for `_CANDLES_TTL`.
- Focused proof must also lock the pre-clamp cache key `f"{symbol}:{timeframe}:{limit}"` and a single upstream fetch across direct-call plus route-level access.
- The route must remain registered exactly once in the assembled FastAPI app.

## Verification snapshot

- Formatter parity held after extraction: `black --check` passed for `src/core/server.py`, `src/core/server_public_api.py`, and `tests/integration/test_ui_endpoints.py`.
- Lint parity held for the same slice files: `ruff check` passed with no findings.
- `tests/integration/test_ui_endpoints.py` now locks:
  - direct-call and route-level parity for `/public/candles`
  - preserved monkeypatch propagation from `core.server.get_exchange_client`
  - alias identity for `public_candles` and `public_router`
  - alias identity for `_CANDLES_CACHE` and stable equality for `_CANDLES_TTL`
  - pre-clamp cache key semantics `tBTCUSD:1m:1001`
  - a single upstream fetch across direct-call plus route access
  - exactly one registered `/public/candles` route in the assembled FastAPI app
- Governance selectors passed via:
  - `tests/backtest/test_backtest_determinism_smoke.py`
  - `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic`
  - `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
  - `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- Security scan passed: `bandit -r src -c bandit.yaml -q` produced only the existing acknowledged `B608` `nosec` warning and no failed findings.
