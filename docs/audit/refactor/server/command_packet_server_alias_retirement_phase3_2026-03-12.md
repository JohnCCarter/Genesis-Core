# Command Packet — server alias retirement phase 3

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` (`feature/server-modul-split`)
- **Risk:** `HIGH` — why: targeted cleanup inside the remaining public/account/paper legacy-import surface in `tests/integration/test_ui_endpoints.py` while preserving explicit alias-proof anchors
- **Required Path:** `Full`
- **Objective:** Canonicalize the remaining non-anchor `core.server_*_api` test imports for public/account/paper coverage in `tests/integration/test_ui_endpoints.py`, while keeping separate alias-proof anchors untouched and renaming any stale alias-facing test claim.
- **Candidate:** `server alias retirement phase 3`
- **Base SHA:** `6124727e`

### Scope

- **Scope IN:**
  - `docs/audit/refactor/server/command_packet_server_alias_retirement_phase3_2026-03-12.md`
  - `docs/audit/refactor/server/context_map_server_alias_retirement_phase3_2026-03-12.md`
  - `tests/integration/test_ui_endpoints.py`
- **Scope OUT:**
  - `src/core/server.py`
  - all `src/core/server_*_api.py` alias stub files
  - all `src/core/api/*.py` runtime modules
  - tests outside `tests/integration/test_ui_endpoints.py`
  - runtime/config authority semantics
- **Expected changed files:** 3
- **Max files touched:** 3

### Gates required

- `python -m black --check tests/integration/test_ui_endpoints.py`
- `python -m ruff check tests/integration/test_ui_endpoints.py`
- `python -m pytest -q tests/integration/test_ui_endpoints.py tests/integration/test_config_endpoints.py tests/utils/test_observability.py tests/utils/test_health.py tests/integration/test_account_endpoints.py`
- `python -m pytest -q tests/governance/test_import_smoke_backtest_optuna.py`
- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
- `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

### Stop Conditions

- Scope drift outside the three files above
- Any regression in explicit alias-proof anchor tests inside `tests/integration/test_ui_endpoints.py`
- Any need to touch runtime code or alias stubs
- Any mismatch between test claims and what the updated tests actually prove
- Any failing determinism, cache-invariance, or pipeline-invariant guard

### Output required

- **Implementation Report**
- **PR evidence template**
