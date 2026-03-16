# Closure — server module split and alias retirement

## Status

`Completed` on `feature/server-modul-split`.

## Scope completed

This closure note records the completion of the server modularization and legacy shim retirement workstream.

### Included outcomes

- Canonical API implementations were established under `src/core/api/`.
- `src/core/server.py` remained the stable FastAPI entrypoint and router assembler.
- Legacy `src/core/server_*_api.py` compatibility shims were retired from the active branch.
- In-scope tests were migrated from alias-proof coverage to canonical-module and server-entrypoint proofs.
- Explicit negative import-proof was added to verify that the retired legacy import paths no longer resolve.

### Explicitly out of scope

- Repo-wide historical/documentation cleanup of legacy path references.
- Worktree copies under `.claude/worktrees/**`.
- Observability metadata cleanup for `_LOGGER = get_logger("core.server_config_api")` in `src/core/api/config.py`.

## Key artifacts

### Package move foundation

- `docs/audit/refactor/server/command_packet_server_api_package_move_2026-03-12.md`
- `docs/audit/refactor/server/context_map_server_api_package_move_2026-03-12.md`

### Archive retention note

- `origin/archive/server-modul-split-contaminated-2026-03-12` is intentionally retained as a historical archive branch from the large cleanup/refactor phase.
- Current review indicates that the archive branch still carries unique traceability/governance evidence for the server-module-split workstream, including foundational command-packet/context-map material not currently present on the active branch.
- The branch should therefore be treated as `retain-for-traceability` rather than as a routine delete candidate.
- Re-review this archive branch later and make an explicit keep/delete decision only after the missing evidence has been salvaged into the active documentation set or the references have been deliberately retired.

### Alias retirement phases

- `docs/audit/refactor/server/command_packet_server_alias_retirement_phase1_2026-03-12.md`
- `docs/audit/refactor/server/context_map_server_alias_retirement_phase1_2026-03-12.md`
- `docs/audit/refactor/server/command_packet_server_alias_retirement_phase2_2026-03-12.md`
- `docs/audit/refactor/server/context_map_server_alias_retirement_phase2_2026-03-12.md`
- `docs/audit/refactor/server/command_packet_server_alias_retirement_phase3_2026-03-12.md`
- `docs/audit/refactor/server/context_map_server_alias_retirement_phase3_2026-03-12.md`
- `docs/audit/refactor/server/command_packet_server_alias_retirement_phase4_2026-03-12.md`
- `docs/audit/refactor/server/context_map_server_alias_retirement_phase4_2026-03-12.md`

## Commit trail

- `7a371558` — `refactor(server): move API routes into core.api package`
- `2c06b8f6` — `refactor(server): start alias retirement phase 1`
- `6124727e` — `refactor(server): advance alias retirement phase 2`
- `67ac920c` — `refactor(server): advance alias retirement phase 3`
- `d4b1d5f6` — `refactor(server): retire legacy api shim modules`

## Runtime end state

### Canonical runtime surface

- `src/core/server.py` is the canonical runtime entrypoint for `core.server:app`.
- `src/core/api/*.py` contains the canonical route implementations.
- No `src/core/server_*_api.py` files remain in the active branch.

### Intentionally retained legacy-adjacent detail

- `src/core/api/config.py` still uses `_LOGGER = get_logger("core.server_config_api")`.
- This was intentionally frozen to avoid observability metadata drift during the shim-retirement slice.

## Verification summary

The following evidence stack was exercised across the modular split and retirement phases:

- `black --check`
- `ruff check`
- focused API/integration selectors for config, UI, observability, health, and account surfaces
- `tests/governance/test_import_smoke_backtest_optuna.py`
- `tests/backtest/test_backtest_determinism_smoke.py`
- `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
- `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- focused config-authority lifecycle selectors during phase 1 where required

## READY_FOR_REVIEW evidence completeness

Complete for the active branch closure state:

- mode/risk/path documented per phase
- scope IN/OUT documented per phase
- pre-review and post-diff governance checkpoints completed for non-trivial slices
- gate stack and outcomes recorded in-session for the final retirement path
- canonical runtime baseline preserved (`src/core/server.py` untouched during shim retirement)

## Residual follow-up (optional, separate work)

- If desired later, do a separate docs/observability cleanup slice for:
  - historical documentation references to legacy `core.server_*_api` paths
  - logger-name normalization in `src/core/api/config.py`

## Conclusion

The server modular split workstream is functionally closed on `feature/server-modul-split`.
