# Context Map — server alias retirement phase 4

## Files to Modify

| File                                                                                     | Purpose                     | Changes Needed                                                                                                                         |
| ---------------------------------------------------------------------------------------- | --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `tests/integration/test_config_endpoints.py`                                             | Config endpoint coverage    | Remove legacy alias-proof tests and keep canonical endpoint/authority/error coverage                                                   |
| `tests/utils/test_observability.py`                                                      | Observability coverage      | Remove legacy info-alias proof and keep dashboard shape/passthrough coverage                                                           |
| `tests/integration/test_ui_endpoints.py`                                                 | UI/API integration coverage | Replace remaining alias-proof anchors with canonical-module/server-entrypoint proofs and add negative import-proof for retired modules |
| `src/core/server_account_api.py`                                                         | Legacy alias shim           | Delete                                                                                                                                 |
| `src/core/server_config_api.py`                                                          | Legacy alias shim           | Delete                                                                                                                                 |
| `src/core/server_info_api.py`                                                            | Legacy alias shim           | Delete                                                                                                                                 |
| `src/core/server_models_api.py`                                                          | Legacy alias shim           | Delete                                                                                                                                 |
| `src/core/server_paper_api.py`                                                           | Legacy alias shim           | Delete                                                                                                                                 |
| `src/core/server_public_api.py`                                                          | Legacy alias shim           | Delete                                                                                                                                 |
| `src/core/server_status_api.py`                                                          | Legacy alias shim           | Delete                                                                                                                                 |
| `src/core/server_strategy_api.py`                                                        | Legacy alias shim           | Delete                                                                                                                                 |
| `src/core/server_ui_api.py`                                                              | Legacy alias shim           | Delete                                                                                                                                 |
| `docs/audit/refactor/server/command_packet_server_alias_retirement_phase4_2026-03-12.md` | Governance evidence         | Capture explicit compatibility-drop scope and gates                                                                                    |
| `docs/audit/refactor/server/context_map_server_alias_retirement_phase4_2026-03-12.md`    | Dependency map              | Document active proof replacements and frozen out-of-scope items                                                                       |

## Canonical Runtime Baseline

| File                      | Role                                                                                                                                   |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `src/core/server.py`      | Canonical FastAPI entrypoint/assembler already bound to `core.api.*`; untouched in this phase                                          |
| `src/core/api/config.py`  | Canonical config route module; logger name `core.server_config_api` remains intentionally frozen to avoid observability metadata drift |
| `src/core/api/ui.py`      | Canonical UI route module used by `core.server.ui_page` / `core.server.ui_router`                                                      |
| `src/core/api/account.py` | Canonical account route module used by `core.server.auth_check` and account caches                                                     |
| `src/core/api/status.py`  | Canonical status route module used by `core.server._AUTH`, `health`, and `debug_auth`                                                  |

## Legacy Proofs Retired In This Slice

| Existing test                                                                         | Replacement / outcome                                                   |
| ------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| `test_config_module_alias_resolves_to_same_module_object`                             | Removed; no legacy import-path compatibility remains                    |
| `test_config_module_alias_resolves_to_same_module_object_when_old_path_imports_first` | Removed; replaced by negative import-proof in UI integration suite      |
| `test_info_module_alias_resolves_to_same_module_object`                               | Removed; no legacy info-module import-path compatibility remains        |
| `test_ui_route_alias_identity`                                                        | Rewritten as canonical server-to-`core.api.ui` identity proof           |
| `test_server_api_module_aliases_resolve_to_same_module_objects`                       | Replaced by parameterized negative import-proof for retired modules     |
| `test_account_route_alias_and_cache_identity`                                         | Rewritten as canonical server-to-`core.api.account` shared-object proof |
| `test_health_shared_auth_object_identity`                                             | Rewritten as canonical server-to-`core.api.status` shared-object proof  |

## New / Updated Proof Intent

| Test intent                                                      | Why it matters                                                                   |
| ---------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| Canonical-module identity between `core.server` and `core.api.*` | Preserves default runtime behavior proof without relying on deleted stub modules |
| Negative import-proof for `core.server_*_api`                    | Proves the compatibility drop is intentional and complete                        |
| Existing direct/route parity tests                               | Continue proving route behavior is unchanged through `core.server:app`           |

## Frozen / Out-of-Scope Items

| Item                                                                 | Reason                                                           |
| -------------------------------------------------------------------- | ---------------------------------------------------------------- |
| `src/core/api/config.py` logger name `core.server_config_api`        | Frozen in this phase to avoid observability metadata drift       |
| `docs/architecture/ARCHITECTURE_VISUAL.md` legacy route reference(s) | Historical/doc cleanup is explicitly out of scope for this phase |
| `.claude/worktrees/**`                                               | Worktree noise excluded from active-branch retirement evidence   |

## Exit Criteria For This Slice

- No `src/core/server_*_api.py` files remain in the active branch.
- The three in-scope test files contain no imports of `core.server_*_api`.
- Canonical server-to-`core.api.*` identity proofs remain in place where needed.
- A parameterized negative import-proof verifies that retired legacy modules raise `ModuleNotFoundError`.
- Full gate set for the slice passes.
