# Command Packet — server alias retirement phase 4

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` (`feature/server-modul-split`)
- **Risk:** `HIGH` — why: explicit retirement of the legacy `core.server_*_api` import surface while preserving default runtime behavior through `core.server:app`
- **Required Path:** `Full`
- **Objective:** Remove the active legacy compatibility stubs under `src/core/server_*_api.py`, retire the in-scope alias-proof tests that depended on them, and replace them with canonical-module/server-entrypoint proofs plus an explicit negative import-proof.
- **Candidate:** `server alias retirement phase 4`
- **Base SHA:** `67ac920c`

### Scope

- **Scope IN:**
  - `docs/audit/refactor/server/command_packet_server_alias_retirement_phase4_2026-03-12.md`
  - `docs/audit/refactor/server/context_map_server_alias_retirement_phase4_2026-03-12.md`
  - `tests/integration/test_config_endpoints.py`
  - `tests/utils/test_observability.py`
  - `tests/integration/test_ui_endpoints.py`
  - `src/core/server_account_api.py`
  - `src/core/server_config_api.py`
  - `src/core/server_info_api.py`
  - `src/core/server_models_api.py`
  - `src/core/server_paper_api.py`
  - `src/core/server_public_api.py`
  - `src/core/server_status_api.py`
  - `src/core/server_strategy_api.py`
  - `src/core/server_ui_api.py`
- **Scope OUT:**
  - `src/core/server.py`
  - all runtime logic under `src/core/api/*.py`
  - `src/core/api/config.py` logger identity (`_LOGGER = get_logger("core.server_config_api")` remains frozen in this batch)
  - strategy/backtest/optimizer/config-authority semantics
  - tests outside the three files above
  - repo-wide historical/doc cleanup, including `docs/architecture/ARCHITECTURE_VISUAL.md`
- **Expected changed files:** 14
- **Max files touched:** 14

### Gates required

- `python -m black --check tests/integration/test_config_endpoints.py tests/integration/test_ui_endpoints.py tests/utils/test_observability.py`
- `python -m ruff check tests/integration/test_config_endpoints.py tests/integration/test_ui_endpoints.py tests/utils/test_observability.py`
- `python -m pytest -q tests/integration/test_config_endpoints.py tests/integration/test_ui_endpoints.py tests/utils/test_observability.py tests/utils/test_health.py tests/integration/test_account_endpoints.py`
- `python -m pytest -q tests/governance/test_import_smoke_backtest_optuna.py`
- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
- `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

### Stop Conditions

- Scope drift outside the fourteen files above
- Any regression in `core.server:app` route behavior or router registration count
- Any need to modify `src/core/server.py` or runtime `src/core/api/*.py` logic
- Any change to the frozen logger identity in `src/core/api/config.py`
- Negative import-proof fails to demonstrate intentional retirement of `core.server_*_api`
- Any failing determinism, cache-invariance, or pipeline-invariant guard

### Output required

- **Implementation Report**
- **PR evidence template**
