# Context Map — server modul split slice 3

## Current target

Continue `feature/server-modul-split` with the next smallest safe extraction from `src/core/server.py`.

## Files to modify

| File                                                                                | Purpose                        | Changes needed                                                                                             |
| ----------------------------------------------------------------------------------- | ------------------------------ | ---------------------------------------------------------------------------------------------------------- |
| `src/core/server.py`                                                                | FastAPI app assembly           | Remove inline `/health` and `/debug/auth` implementations and include a dedicated status router            |
| `src/core/server_status_api.py`                                                     | New slice-3 router module      | Host the two status/debug routes and preserve current response semantics                                   |
| `tests/utils/test_health.py`                                                        | Health route contract lock     | Extend coverage with exact healthy-path payload parity if needed                                           |
| `tests/integration/test_ui_endpoints.py`                                            | Error/debug compatibility lock | Preserve `503` health path, `_AUTH` object identity, direct `debug_auth()` compatibility, and route parity |
| `docs/audit/refactor/server/command_packet_server_modul_split_slice3_2026-03-12.md` | Commit contract                | Record slice scope, gates, and constraints                                                                 |
| `docs/audit/refactor/server/context_map_server_modul_split_slice3_2026-03-12.md`    | Dependency/test map            | Capture affected files, tests, and risks                                                                   |

## Dependencies

| File                            | Relationship                                                                |
| ------------------------------- | --------------------------------------------------------------------------- |
| `core.config.authority`         | `health` relies on `ConfigAuthority()` state via `_AUTH.get()`              |
| `core.config.settings`          | `debug_auth` reads API-key settings and must preserve masking semantics     |
| `core.utils.logging_redaction`  | `health` logs config-read failures; logging behavior must remain equivalent |
| `src/core/server_config_api.py` | Existing router include pattern to mirror                                   |

## Test files

| Test                                                                                                                      | Coverage                                                                           |
| ------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `tests/utils/test_health.py`                                                                                              | `/health` success route contract                                                   |
| `tests/integration/test_ui_endpoints.py`                                                                                  | `/health` error payload, `debug_auth()` compatibility, route parity work           |
| `tests/integration/test_config_endpoints.py`                                                                              | App assembly smoke: confirms `core.server.app` still exposes runtime config routes |
| `tests/backtest/test_backtest_determinism_smoke.py`                                                                       | Canonical determinism replay required by RESEARCH governance                       |
| `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic`             | Pipeline determinism signal for route assembly path                                |
| `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed` | Feature cache invariance guard                                                     |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`                | Pipeline invariant guard                                                           |
| `bandit -r src -c bandit.yaml`                                                                                            | Security scan required by repo-local Python engineering skill                      |

## Reference patterns

| File                              | Pattern                                                                      |
| --------------------------------- | ---------------------------------------------------------------------------- |
| `src/core/server_config_api.py`   | Existing `APIRouter` extraction pattern already included by `core.server`    |
| `src/core/server_strategy_api.py` | Slice-1 pattern for route extraction with preserved public names             |
| `src/core/server_info_api.py`     | Slice-2 pattern for router extraction plus symbol rebinding in `core.server` |

## Risk assessment

- [x] Public API/HTTP contract risk: `/health` and `/debug/auth` must preserve payloads and status code behavior
- [x] App wiring risk: adding/importing another extracted router must not break existing `app.include_router(...)` behavior
- [x] Test compatibility risk: `core.server._AUTH` and exported function names must remain monkeypatchable/importable
- [ ] Database migrations needed
- [ ] Configuration changes required

## Slice rationale

This slice stays contained because:

1. Both handlers are small and read-only.
2. Existing tests already cover `/health` success and error paths plus direct `debug_auth()` masking semantics.
3. The only sensitive part is preserving the `_AUTH` object identity and route exposure, which can be locked with small tests and top-level aliasing.
4. The extraction pattern can mirror earlier verified server router splits.

## Verification snapshot

- Formatter parity held after extraction: `black --check` passed for `src/core/server.py`, `src/core/server_status_api.py`, `tests/utils/test_health.py`, and `tests/integration/test_ui_endpoints.py`.
- Lint parity held for the same slice files: `ruff check` passed with no findings.
- `/health` error-path observability parity is now explicitly locked: `tests/utils/test_health.py` asserts the warning still emits under logger name `core.server`.
- Focused route + governance proof passed via:
  - `tests/utils/test_health.py`
  - `tests/integration/test_ui_endpoints.py`
  - `tests/integration/test_config_endpoints.py`
  - `tests/backtest/test_backtest_determinism_smoke.py`
  - `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic`
  - `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
  - `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- Security scan passed: `bandit -r src -c bandit.yaml -q` produced only the existing acknowledged `B608` `nosec` warning and no failed findings.
