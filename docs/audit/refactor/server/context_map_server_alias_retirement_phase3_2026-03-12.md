# Context Map — server alias retirement phase 3

## Files to Modify

| File                                                                                     | Purpose                                           | Changes Needed                                                                                        |
| ---------------------------------------------------------------------------------------- | ------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `tests/integration/test_ui_endpoints.py`                                                 | Remaining mixed public/account/paper parity tests | Canonicalize the four remaining non-anchor legacy imports while keeping alias-proof anchors untouched |
| `docs/audit/refactor/server/command_packet_server_alias_retirement_phase3_2026-03-12.md` | Governance evidence                               | Capture exact scope, gates, and stop conditions for the public/account/paper slice                    |
| `docs/audit/refactor/server/context_map_server_alias_retirement_phase3_2026-03-12.md`    | Dependency map                                    | Record which remaining tests become canonical-module parity versus which stay as alias-proof anchors  |

## Alias-Proof Anchors To Keep Unchanged

| Test                                                            | Why it stays                                              |
| --------------------------------------------------------------- | --------------------------------------------------------- |
| `test_ui_route_alias_identity`                                  | Explicit `core.server` ↔ `core.server_ui_api` alias proof |
| `test_server_api_module_aliases_resolve_to_same_module_objects` | Cross-module old/new same-object proof                    |
| `test_account_route_alias_and_cache_identity`                   | Shared-object alias proof for account surface             |
| `test_health_shared_auth_object_identity`                       | Shared-object alias proof for status surface              |

## Canonicalizable Tests In This Slice

| Test                                                    | Old import                | New import         | Classification                                                  | Notes                                               |
| ------------------------------------------------------- | ------------------------- | ------------------ | --------------------------------------------------------------- | --------------------------------------------------- |
| `test_public_candles_endpoint_smoke`                    | `core.server_public_api`  | `core.api.public`  | canonicalizable direct/route parity + shared cache identity     | Alias-proof remains covered elsewhere in file       |
| `test_auth_check_uses_helpers`                          | `core.server_account_api` | `core.api.account` | canonicalizable direct/route parity + helper usage proof        | Alias-proof remains covered elsewhere in file       |
| `test_paper_submit_monkeypatched`                       | `core.server_paper_api`   | `core.api.paper`   | canonicalizable monkeypatch-sensitive route parity              | Alias-proof remains covered elsewhere in file       |
| `test_paper_estimate_route_and_canonical_module_parity` | `core.server_paper_api`   | `core.api.paper`   | canonicalizable direct/route parity + canonical-module identity | Renamed from `...alias_parity` to avoid stale claim |

## Active Dependencies

| File                             | Relationship                                                                                                                       |
| -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `src/core/api/public.py`         | Canonical public route module with cache and exchange-client resolution used by the migrated public test                           |
| `src/core/api/account.py`        | Canonical account route module with `bfx_read` helper usage used by the migrated auth-check test                                   |
| `src/core/api/paper.py`          | Canonical paper route module with route/direct parity and monkeypatch-sensitive server resolution used by the migrated paper tests |
| `src/core/server_public_api.py`  | Legacy alias stub left untouched; same-module-object proof remains covered elsewhere                                               |
| `src/core/server_account_api.py` | Legacy alias stub left untouched; same-module-object proof remains covered elsewhere                                               |
| `src/core/server_paper_api.py`   | Legacy alias stub left untouched; same-module-object proof remains covered elsewhere                                               |

## Exit Criteria For This Slice

- The four canonicalizable tests use `core.api.*` imports.
- No alias-proof anchor tests are modified.
- `test_paper_estimate_route_and_canonical_module_parity` no longer claims alias proof.
- Full gate set for the slice passes.
