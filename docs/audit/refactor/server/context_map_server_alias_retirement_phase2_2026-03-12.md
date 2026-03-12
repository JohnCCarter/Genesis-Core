# Context Map — server alias retirement phase 2

## Files to Modify

| File                                                                                     | Purpose                                                              | Changes Needed                                                                                            |
| ---------------------------------------------------------------------------------------- | -------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `tests/integration/test_ui_endpoints.py`                                                 | Mixed alias-proof and monkeypatch-sensitive UI/API integration tests | Canonicalize only tests that no longer need old-path imports, while leaving alias-proof anchors untouched |
| `docs/audit/refactor/server/command_packet_server_alias_retirement_phase2_2026-03-12.md` | Governance evidence                                                  | Capture scope, gates, and stop conditions for the UI-focused slice                                        |
| `docs/audit/refactor/server/context_map_server_alias_retirement_phase2_2026-03-12.md`    | Dependency map                                                       | Record which tests are canonicalizable versus which remain alias-proof/deferred                           |

## Alias-Proof Anchors To Keep Unchanged

| Test                                                            | Why it stays                                              |
| --------------------------------------------------------------- | --------------------------------------------------------- |
| `test_ui_route_alias_identity`                                  | Explicit `core.server` ↔ `core.server_ui_api` alias proof |
| `test_server_api_module_aliases_resolve_to_same_module_objects` | Cross-module old/new same-object proof                    |
| `test_account_route_alias_and_cache_identity`                   | Shared-object alias proof for account surface             |
| `test_health_shared_auth_object_identity`                       | Shared-object alias proof for status surface              |

## Canonicalizable Tests In This Slice

| Test                                                     | Old import                 | New import          | Classification                                               | Notes                                               |
| -------------------------------------------------------- | -------------------------- | ------------------- | ------------------------------------------------------------ | --------------------------------------------------- |
| `test_strategy_evaluate_delegates_with_current_defaults` | `core.server_strategy_api` | `core.api.strategy` | canonicalizable monkeypatch-sensitive route parity           | Alias-proof already covered elsewhere in file       |
| `test_models_reload_route_and_delegation_parity`         | `core.server_models_api`   | `core.api.models`   | canonicalizable direct/route parity + monkeypatch delegation | Renamed from `...alias_parity` to avoid stale claim |
| `test_debug_auth_route_matches_direct_function`          | `core.server_status_api`   | `core.api.status`   | canonicalizable monkeypatch-sensitive route parity           | Alias-proof already covered elsewhere in file       |

## Deferred Tests

| Test                                         | Why deferred                                                          |
| -------------------------------------------- | --------------------------------------------------------------------- |
| `test_public_candles_endpoint_smoke`         | Still mixes route parity, cache identity, and old import surface      |
| `test_auth_check_uses_helpers`               | Still asserts direct/shared identity against old import path          |
| `test_paper_submit_monkeypatched`            | Still couples monkeypatching with explicit old-path parity assertions |
| `test_paper_estimate_route_alias_and_parity` | Still couples route parity, monkeypatching, and alias-facing claims   |

## Active Dependencies

| File                              | Relationship                                                                                                 |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `src/core/api/strategy.py`        | Canonical strategy route module with `evaluate_pipeline` module global used by the migrated strategy test    |
| `src/core/api/models.py`          | Canonical models route module with `ModelRegistry.clear_cache()` delegation used by the migrated models test |
| `src/core/api/status.py`          | Canonical status route module with `get_settings()` module global used by the migrated debug-auth test       |
| `src/core/server_strategy_api.py` | Legacy alias stub left untouched; same-module-object proof remains covered elsewhere                         |
| `src/core/server_models_api.py`   | Legacy alias stub left untouched; same-module-object proof remains covered elsewhere                         |
| `src/core/server_status_api.py`   | Legacy alias stub left untouched; same-module-object proof remains covered elsewhere                         |

## Exit Criteria For This Slice

- The three canonicalizable tests use `core.api.*` imports.
- No alias-proof anchor tests are modified.
- `test_models_reload_route_and_delegation_parity` no longer claims alias parity.
- Full gate set for the slice passes.
