# Context Map — server modul split slice 6

## Current target

Continue `feature/server-modul-split` with the next smallest safe extraction from `src/core/server.py`.

## Files to modify

| File                                                                                | Purpose                   | Changes needed                                                           |
| ----------------------------------------------------------------------------------- | ------------------------- | ------------------------------------------------------------------------ |
| `src/core/server.py`                                                                | FastAPI app assembly      | Remove inline `/ui` implementation and include a dedicated UI router     |
| `src/core/server_ui_api.py`                                                         | New slice-6 router module | Host `/ui` with the exact existing HTML response and response class      |
| `tests/integration/test_ui_endpoints.py`                                            | UI route compatibility    | Keep route contract proof and add alias identity/direct parity if needed |
| `docs/audit/refactor/server/command_packet_server_modul_split_slice6_2026-03-12.md` | Commit contract           | Record slice scope, gates, and constraints                               |
| `docs/audit/refactor/server/context_map_server_modul_split_slice6_2026-03-12.md`    | Dependency/test map       | Capture affected files, tests, and risks                                 |

## Dependencies

| File                                     | Relationship                                                             |
| ---------------------------------------- | ------------------------------------------------------------------------ |
| `fastapi.responses.HTMLResponse`         | `/ui` must preserve explicit HTML response class                         |
| `src/core/server.py`                     | Current owner of `ui_page()` and app route registration                  |
| `tests/integration/test_ui_endpoints.py` | Existing route test already locks key HTML marker and route availability |

## Test files

| Test                                                                                                                      | Coverage                                                                           |
| ------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `tests/integration/test_ui_endpoints.py`                                                                                  | `/ui` returns `200`, keeps `text/html`, and locks alias/direct parity if extracted |
| `tests/backtest/test_backtest_determinism_smoke.py`                                                                       | Canonical determinism replay required by RESEARCH governance                       |
| `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic`             | Pipeline determinism guard after server wiring change                              |
| `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed` | Cache-key determinism guard for feature hashing across `PYTHONHASHSEED`            |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`                | Pipeline invariant guard                                                           |
| `bandit -r src -c bandit.yaml`                                                                                            | Security scan required by repo-local policy                                        |

## Reference patterns

| File                            | Pattern                                                                       |
| ------------------------------- | ----------------------------------------------------------------------------- |
| `src/core/server_models_api.py` | Recent single-route extraction with compatibility aliasing and router include |
| `src/core/server_info_api.py`   | Router extraction plus top-level symbol rebinding in `core.server`            |
| `src/core/server_status_api.py` | Small extracted router preserving response contract through aliasing          |

## Risk assessment

- [x] Public API/HTTP contract risk: `/ui` must preserve exact route exposure, response class, and key HTML content
- [x] App wiring risk: adding another extracted router must not disturb existing router includes
- [x] Compatibility risk: `core.server.ui_page` may need to remain stable for hidden Python-surface consumers
- [ ] Database migrations needed
- [ ] Configuration changes required

## Slice rationale

This slice stays contained because:

1. `/ui` is a single pure function with no shared runtime state.
2. The route does not call exchange helpers, caches, config authority, or trading logic.
3. Existing integration coverage already proves route reachability and a stable HTML marker.
4. The extraction pattern mirrors earlier single-route no-behavior-change slices while avoiding monkeypatch-heavy surfaces.

## Verification emphasis

- `/ui` needs both route-level and direct-call parity proof so the extracted handler remains identical through `core.server.ui_page`.
- The focused test must verify the response header still starts with `text/html`.
- Compatibility proof must also lock `core.server.ui_router is core.server_ui_api.router` and assert `/ui` is registered exactly once in the assembled FastAPI app.

## Verification snapshot

- Formatter parity held after extraction: `black --check` passed for `src/core/server.py`, `src/core/server_ui_api.py`, and `tests/integration/test_ui_endpoints.py`.
- Lint parity held for the same slice files: `ruff check` passed with no findings.
- `tests/integration/test_ui_endpoints.py` now locks:
  - route status `200` and stable `Minimal test` marker for `/ui`
  - `content-type` prefix `text/html`
  - direct-return parity between the route payload, `core.server.ui_page()`, and `core.server_ui_api.ui_page()`
  - alias identity for `ui_page` and `ui_router`
  - single registration of `/ui` in the assembled FastAPI app
- Governance selectors passed via:
  - `tests/backtest/test_backtest_determinism_smoke.py`
  - `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic`
  - `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
  - `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- Security scan passed: `bandit -r src -c bandit.yaml -q` produced only the existing acknowledged `B608` `nosec` warning and no failed findings.
