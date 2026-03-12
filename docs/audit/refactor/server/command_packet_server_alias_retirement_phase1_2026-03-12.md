# Command Packet — server alias retirement phase 1

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` (`feature/server-modul-split`)
- **Risk:** `HIGH` — why: import-contract cleanup on API/config test surfaces with legacy alias compatibility still in play
- **Required Path:** `Full`
- **Objective:** Start the alias-stub retirement with an inventory-and-prep slice that classifies remaining `core.server_*_api` consumers, migrates only clearly removable test imports to canonical `core.api.*` paths, and refreshes the remaining live docstring reference without changing runtime behavior.
- **Candidate:** `server alias retirement phase 1`
- **Base SHA:** `b9fc5cf61653ef0967197244fc4433998c235633`

### Scope

- **Scope IN:**
  - `docs/audit/refactor/server/command_packet_server_alias_retirement_phase1_2026-03-12.md`
  - `docs/audit/refactor/server/context_map_server_alias_retirement_phase1_2026-03-12.md`
  - `src/core/config/validator.py`
  - `tests/integration/test_config_endpoints.py`
  - `tests/utils/test_observability.py`
- **Scope OUT:**
  - `src/core/server.py`
  - all `src/core/server_*_api.py` alias stub files
  - `src/core/api/config.py` logger identity (`_LOGGER = get_logger("core.server_config_api")` remains unchanged in this batch)
  - `tests/integration/test_ui_endpoints.py` code edits
  - runtime/config authority semantics
  - strategy/backtest/optimizer paths
  - historical audit artifacts outside the new packet/context map
- **Expected changed files:** 5
- **Max files touched:** 5

### Gates required

- `python -m black --check src/core/config/validator.py tests/integration/test_config_endpoints.py tests/utils/test_observability.py`
- `python -m ruff check src/core/config/validator.py tests/integration/test_config_endpoints.py tests/utils/test_observability.py`
- `python -m pytest -q tests/integration/test_config_endpoints.py tests/integration/test_ui_endpoints.py tests/utils/test_observability.py tests/utils/test_health.py tests/integration/test_account_endpoints.py`
- `python -m pytest -q tests/governance/test_import_smoke_backtest_optuna.py`
- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
- `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

### Stop Conditions

- Scope drift outside the five files above
- Any behavior change in FastAPI route outputs, alias import contracts, or monkeypatch-sensitive tests
- Any proposed logger-name change in `src/core/api/config.py`
- Any need to delete alias stubs before a dedicated removal batch
- Any failing determinism, cache-invariance, or pipeline-invariant guard

### Output required

- **Implementation Report**
- **PR evidence template**
