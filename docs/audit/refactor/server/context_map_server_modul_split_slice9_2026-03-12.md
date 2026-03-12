# Context Map — server modul split slice 9

## Current target

Continue `feature/server-modul-split` with the final remaining inline route extraction from `src/core/server.py`.

## Files to modify

| File                                                                                | Purpose                      | Changes needed                                                                                 |
| ----------------------------------------------------------------------------------- | ---------------------------- | ---------------------------------------------------------------------------------------------- |
| `src/core/server.py`                                                                | FastAPI app assembly         | Remove inline `/paper/submit`, rebind compatibility alias, and continue including paper router |
| `src/core/server_paper_api.py`                                                      | Existing paper router module | Add `/paper/submit` while preserving late-bound helper access through `core.server`            |
| `tests/integration/test_ui_endpoints.py`                                            | Paper submit compatibility   | Add alias/direct-route parity and upstream error-shape coverage                                |
| `docs/audit/refactor/server/command_packet_server_modul_split_slice9_2026-03-12.md` | Commit contract              | Record slice scope, gates, and constraints                                                     |
| `docs/audit/refactor/server/context_map_server_modul_split_slice9_2026-03-12.md`    | Dependency/test map          | Capture affected files, tests, risks, and reference patterns                                   |

## Dependencies

| File                                     | Relationship                                                                                                                             |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `src/core/server.py`                     | Current owner of `paper_submit()`, clamp logic, wallet-cap logic, helper functions, and monkeypatch surfaces                             |
| `src/core/server_paper_api.py`           | Existing host for `/paper/estimate`; target module for the final `/paper/*` extraction                                                   |
| `src/core/server_ui_api.py`              | Dependency-only consumer: browser JS posts to `/paper/submit` after reading `/paper/estimate`; no code changes allowed in this slice     |
| `core.io.bitfinex.read_helpers`          | Wallet-cap branch reads exchange wallets via `bfx_read.get_wallets()`                                                                    |
| `core.io.bitfinex.exchange_client`       | Uses `get_exchange_client().public_request()` for wallet-cap pricing and `get_exchange_client().signed_request()` for order submission   |
| `tests/integration/test_ui_endpoints.py` | Existing focused server integration file already locks extracted-route compatibility and contains current `paper_submit` behavior proofs |

## Test files

| Test                                                                                                                      | Coverage                                                                                                                                 |
| ------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `tests/integration/test_ui_endpoints.py`                                                                                  | Direct `paper_submit()` compatibility plus required route parity, alias identity, wallet-cap helper parity, and exact error-shape proofs |
| `tests/backtest/test_backtest_determinism_smoke.py`                                                                       | Canonical determinism replay required by RESEARCH governance                                                                             |
| `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic`             | Pipeline determinism guard after server wiring change                                                                                    |
| `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed` | Cache-key determinism guard for feature hashing across `PYTHONHASHSEED`                                                                  |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`                | Pipeline invariant guard                                                                                                                 |
| `bandit -r src -c bandit.yaml`                                                                                            | Security scan required by repo-local policy                                                                                              |

## Reference patterns

| File                            | Pattern                                                                                |
| ------------------------------- | -------------------------------------------------------------------------------------- |
| `src/core/server_paper_api.py`  | Late-bound helper resolution already used for `/paper/estimate`                        |
| `src/core/server_public_api.py` | Single-route extraction that preserves monkeypatch behavior through late-bound helpers |
| `src/core/server_ui_api.py`     | Dependency-only consumer proving why UI files must remain out of scope                 |

## Risk assessment

- [x] Public API/HTTP contract risk: `/paper/submit` must preserve exact request validation and response payloads
- [x] App wiring risk: paper router must remain registered exactly once while now hosting both `/paper/estimate` and `/paper/submit`
- [x] Compatibility risk: direct `core.server.paper_submit` imports and `core.server` helper monkeypatches must remain stable
- [x] Hidden behavior risk: wallet-cap, size clamp, whitelist rejection, and upstream error-shape semantics must not drift
- [ ] Database migrations needed
- [ ] Configuration changes required

## Slice rationale

This slice stays contained because:

1. It is the last remaining inline server route in this worktree split.
2. The paper router module already exists, so only one new runtime host file remains in play.
3. Existing tests already cover several `paper_submit` behaviors and can be extended to prove route extraction parity.
4. Completing `/paper/submit` finishes the paper-route split without expanding into UI or config scope.

## Verification emphasis

- `/paper/submit` needs both direct-call and route-level parity under the same monkeypatched `core.server` helper surfaces.
- Compatibility proof must lock `core.server.paper_submit is core.server_paper_api.paper_submit` and `core.server.paper_router is core.server_paper_api.router` after extraction.
- Focused proof should lock successful signed-request parity, whitelist rejection, `invalid_action_or_size`, wallet-cap helper behavior, and exact upstream error-shape preservation.
- The route must remain registered exactly once in the assembled FastAPI app.

## Verification snapshot

- Formatter parity held after extraction: `black --check` passed for `src/core/server.py`, `src/core/server_paper_api.py`, and `tests/integration/test_ui_endpoints.py`.
- Lint parity held for the same slice files: `ruff check` passed with no findings.
- `tests/integration/test_ui_endpoints.py` now locks:
  - alias identity for `paper_submit` and `paper_router`
  - direct-call and route-level parity for `/paper/submit`
  - unknown-symbol rejection with the pinned `invalid_symbol` payload
  - the `invalid_action_or_size` branch for both direct-call and route-level access
  - wallet-cap helper semantics via monkeypatched `core.server.get_settings`, `core.server.bfx_read.get_wallets`, `core.server.get_exchange_client`, `core.server.MIN_ORDER_SIZE`, `core.server.MIN_ORDER_MARGIN`, `core.server._real_from_test`, and `core.server._base_ccy_from_test`
  - exact `HTTPStatusError` and generic exception payload shapes after extraction
  - exactly one registered `/paper/submit` route in the assembled FastAPI app
- Governance selectors passed via:
  - `tests/backtest/test_backtest_determinism_smoke.py`
  - `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic`
  - `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
  - `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- Security scan passed: `bandit -r src -c bandit.yaml -q` produced only the existing acknowledged `B608` `nosec` warning and no failed findings.
