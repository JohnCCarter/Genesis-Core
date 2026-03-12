# Context Map — server alias retirement phase 1

## Files to Modify

| File                                                                                     | Purpose                      | Changes Needed                                                                                            |
| ---------------------------------------------------------------------------------------- | ---------------------------- | --------------------------------------------------------------------------------------------------------- |
| `src/core/config/validator.py`                                                           | Test-only config helper docs | Update the live module-path reference from the legacy alias to canonical `core.api.config`                |
| `tests/integration/test_config_endpoints.py`                                             | Config endpoint tests        | Keep explicit alias-proof tests, but migrate non-alias monkeypatch tests to canonical `core.api.config`   |
| `tests/utils/test_observability.py`                                                      | Observability endpoint tests | Keep explicit alias-proof test, but migrate the passthrough monkeypatch test to canonical `core.api.info` |
| `docs/audit/refactor/server/command_packet_server_alias_retirement_phase1_2026-03-12.md` | Governance evidence          | Capture scope, constraints, gates, and stop conditions for this slice                                     |
| `docs/audit/refactor/server/context_map_server_alias_retirement_phase1_2026-03-12.md`    | Dependency map               | Classify all remaining `core.server_*_api` imports before any removal batch                               |

## Active Dependencies

| File                                     | Relationship                                                                                                                   |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `src/core/api/config.py`                 | Canonical config route module; logger name remains pinned to `core.server_config_api` for compatibility in this slice          |
| `src/core/server_config_api.py`          | Legacy alias stub resolving to the same module object as `core.api.config`; not modified here                                  |
| `src/core/server_info_api.py`            | Legacy alias stub resolving to the same module object as `core.api.info`; not modified here                                    |
| `tests/integration/test_ui_endpoints.py` | Densest remaining alias/parity surface; treated as evidence/input for later retirement work, not code-edit scope in this slice |

## Remaining Alias-Import Classification

### `tests/integration/test_config_endpoints.py`

| Test / usage                                                                          | Current role                                | Classification                                                                | Migration in this slice             |
| ------------------------------------------------------------------------------------- | ------------------------------------------- | ----------------------------------------------------------------------------- | ----------------------------------- |
| `test_config_module_alias_resolves_to_same_module_object`                             | Verifies same-module-object alias contract  | `alias-proof`                                                                 | Keep old/new imports unchanged      |
| `test_config_module_alias_resolves_to_same_module_object_when_old_path_imports_first` | Verifies old-import-first compatibility     | `alias-proof`                                                                 | Keep unchanged                      |
| `test_runtime_validate_uses_config_authority_validate`                                | Monkeypatches route module authority object | `monkeypatch-sensitive`, but not alias-specific after alias-proof tests exist | Migrate import to `core.api.config` |
| `test_runtime_endpoints_do_not_leak_exceptions`                                       | Monkeypatches authority error path          | `monkeypatch-sensitive`, but not alias-specific after alias-proof tests exist | Migrate import to `core.api.config` |

### `tests/utils/test_observability.py`

| Test / usage                                            | Current role                     | Classification                                                                | Migration in this slice           |
| ------------------------------------------------------- | -------------------------------- | ----------------------------------------------------------------------------- | --------------------------------- |
| `test_info_module_alias_resolves_to_same_module_object` | Verifies info alias contract     | `alias-proof`                                                                 | Keep old/new imports unchanged    |
| `test_observability_dashboard_passthrough`              | Monkeypatches dashboard provider | `monkeypatch-sensitive`, but not alias-specific after alias-proof test exists | Migrate import to `core.api.info` |

### `tests/integration/test_ui_endpoints.py`

| Test / usage                                                    | Current role                                              | Classification                                  | Migration in this slice |
| --------------------------------------------------------------- | --------------------------------------------------------- | ----------------------------------------------- | ----------------------- |
| `test_ui_get_and_evaluate_post`                                 | UI route smoke + direct/server parity                     | `route smoke`                                   | No change               |
| `test_ui_route_alias_identity`                                  | Proves `core.server` ↔ `core.server_ui_api` alias surface | `alias-proof`                                   | No change               |
| `test_server_api_module_aliases_resolve_to_same_module_objects` | Cross-module same-object proof                            | `alias-proof`                                   | No change               |
| `test_strategy_evaluate_delegates_with_current_defaults`        | Monkeypatches strategy route module                       | `monkeypatch-sensitive`                         | Deferred                |
| `test_public_candles_endpoint_smoke`                            | Direct/route parity + shared cache identity               | `monkeypatch-sensitive`                         | Deferred                |
| `test_auth_check_uses_helpers`                                  | Direct/route parity + account helper identity             | `monkeypatch-sensitive`                         | Deferred                |
| `test_account_route_alias_and_cache_identity`                   | Account shared-object proof                               | `alias-proof`                                   | No change               |
| `test_models_reload_route_and_alias_parity`                     | Models parity + monkeypatching                            | `monkeypatch-sensitive`                         | Deferred                |
| `test_health_shared_auth_object_identity`                       | Shared object identity proof                              | `alias-proof`                                   | No change               |
| `test_paper_submit_monkeypatched`                               | Paper route monkeypatch parity                            | `monkeypatch-sensitive`                         | Deferred                |
| `test_paper_estimate_route_alias_and_parity`                    | Paper estimate parity + monkeypatching                    | `monkeypatch-sensitive`                         | Deferred                |
| Remaining old alias imports in file                             | Mixed route-smoke/parity coverage                         | `requires dedicated later classification slice` | Deferred                |

## Risk Notes

- Changing `_LOGGER` in `src/core/api/config.py` would alter observability metadata and is intentionally out of scope.
- `tests/integration/test_ui_endpoints.py` remains the main blocker for actual alias-stub deletion.
- No alias stub files are deleted or edited in this phase.

## Exit Criteria For This Slice

- New command packet and context map exist for alias retirement phase 1.
- Live product-code reference in `src/core/config/validator.py` points to canonical `core.api.config`.
- Alias-proof tests remain intact.
- Only clearly removable test imports are canonicalized.
- Full gate set for the slice passes.
