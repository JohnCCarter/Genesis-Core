# Context Map — server modul split slice 8

## Current target

Continue `feature/server-modul-split` with the next smallest safe extraction from `src/core/server.py`.

## Files to modify

| File                                                                                | Purpose                         | Changes needed                                                                                 |
| ----------------------------------------------------------------------------------- | ------------------------------- | ---------------------------------------------------------------------------------------------- |
| `src/core/server.py`                                                                | FastAPI app assembly            | Remove inline `/paper/estimate`, rebind compatibility aliases, and include a dedicated router  |
| `src/core/server_paper_api.py`                                                      | New slice-8 paper router module | Host `/paper/estimate` while preserving helper indirection through `core.server`               |
| `tests/integration/test_ui_endpoints.py`                                            | Paper estimate compatibility    | Add direct/route parity, helper-monkeypatch proof, alias checks, and route-registration checks |
| `docs/audit/refactor/server/command_packet_server_modul_split_slice8_2026-03-12.md` | Commit contract                 | Record slice scope, gates, and constraints                                                     |
| `docs/audit/refactor/server/context_map_server_modul_split_slice8_2026-03-12.md`    | Dependency/test map             | Capture affected files, tests, risks, and reference patterns                                   |

## Dependencies

| File                                     | Relationship                                                                                                                                                                                       |
| ---------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/core/server.py`                     | Current owner of `paper_estimate()`, helper functions, whitelist/default semantics, and monkeypatch surfaces                                                                                       |
| `core.io.bitfinex.read_helpers`          | `/paper/estimate` reads wallets via `bfx_read.get_wallets()`                                                                                                                                       |
| `core.io.bitfinex.exchange_client`       | `/paper/estimate` reads ticker price via `get_exchange_client().public_request()`                                                                                                                  |
| `src/core/server_ui_api.py`              | Dependency-only consumer: browser JS calls `/paper/estimate` and reads `required_min`, `min_with_margin`, `usd_available`, `last_price`, and `est_max_size`; no code changes allowed in this slice |
| `tests/integration/test_ui_endpoints.py` | Existing focused server integration file already locks direct-call compatibility for other extracted endpoints                                                                                     |

## Test files

| Test                                                                                                                      | Coverage                                                                                         |
| ------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `tests/integration/test_ui_endpoints.py`                                                                                  | Direct `paper_estimate()` compatibility, route contract, helper/default parity via `core.server` |
| `tests/backtest/test_backtest_determinism_smoke.py`                                                                       | Canonical determinism replay required by RESEARCH governance                                     |
| `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic`             | Pipeline determinism guard after server wiring change                                            |
| `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed` | Cache-key determinism guard for feature hashing across `PYTHONHASHSEED`                          |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`                | Pipeline invariant guard                                                                         |
| `bandit -r src -c bandit.yaml`                                                                                            | Security scan required by repo-local policy                                                      |

## Reference patterns

| File                             | Pattern                                                                                |
| -------------------------------- | -------------------------------------------------------------------------------------- |
| `src/core/server_public_api.py`  | Single-route extraction that preserves monkeypatch behavior through late-bound helpers |
| `src/core/server_account_api.py` | Router extraction with shared dependency access and no-behavior-change response logic  |
| `src/core/server_ui_api.py`      | Recent single-route extraction with explicit alias and single-registration proof       |

## Risk assessment

- [x] Public API/HTTP contract risk: `/paper/estimate` must preserve exact query handling and response keys
- [x] App wiring risk: adding another extracted router must not disturb existing router includes
- [x] Compatibility risk: direct `core.server.paper_estimate` imports and `core.server` helper monkeypatches may need to remain stable
- [x] Hidden behavior risk: whitelist/default fallback, helper-based symbol conversion, and wallet/ticker lookups must not drift
- [ ] Database migrations needed
- [ ] Configuration changes required

## Slice rationale

This slice stays contained because:

1. `/paper/estimate` is read-only and does not submit orders.
2. It is smaller and safer than `/paper/submit`, but still exercises the helper-indirection pattern needed for paper routes.
3. Existing integration coverage already centralizes extracted-route compatibility checks in `tests/integration/test_ui_endpoints.py`.
4. Extracting estimate first should reduce risk before moving the order-submission endpoint.

## Verification emphasis

- `/paper/estimate` needs both direct-call and route-level parity under the same monkeypatched `core.server` helper surfaces.
- Compatibility proof must lock `core.server.paper_estimate is core.server_paper_api.paper_estimate` and `core.server.paper_router is core.server_paper_api.router` if extracted under that module name.
- Focused proof should lock whitelist/default fallback, helper-driven real/base symbol conversion, wallet-derived `usd_available` / `base_available`, and price-derived `last_price` / `est_max_size`.
- The route must remain registered exactly once in the assembled FastAPI app.

## Verification snapshot

- Formatter parity held after extraction: `black --check` passed for `src/core/server.py`, `src/core/server_paper_api.py`, and `tests/integration/test_ui_endpoints.py`.
- Lint parity held for the same slice files: `ruff check` passed with no findings.
- `tests/integration/test_ui_endpoints.py` now locks:
  - direct-call and route-level parity for `/paper/estimate`
  - preserved monkeypatch propagation from `core.server.get_settings`, `core.server.bfx_read.get_wallets`, `core.server.get_exchange_client`, `core.server.MIN_ORDER_SIZE`, `core.server.MIN_ORDER_MARGIN`, `core.server._real_from_test`, and `core.server._base_ccy_from_test`
  - alias identity for `paper_estimate` and `paper_router`
  - unknown-symbol fallback to `tTESTBTC:TESTUSD`
  - wallet-derived `usd_available` / `base_available`, price-derived `last_price`, and computed `est_max_size`
  - the no-credentials branch skipping wallet lookup while preserving the ticker lookup path
  - the `paper_submit` wallet-cap branch still honoring shared helper semantics for `_real_from_test` and `_base_ccy_from_test` after helper deduping
  - exactly one registered `/paper/estimate` route in the assembled FastAPI app
- Governance selectors passed via:
  - `tests/backtest/test_backtest_determinism_smoke.py`
  - `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic`
  - `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
  - `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- Security scan passed: `bandit -r src -c bandit.yaml -q` produced only the existing acknowledged `B608` `nosec` warning and no failed findings.
