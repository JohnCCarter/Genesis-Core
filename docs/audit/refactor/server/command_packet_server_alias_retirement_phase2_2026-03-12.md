# Command Packet — server alias retirement phase 2

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` (`feature/server-modul-split`)
- **Risk:** `HIGH` — why: targeted cleanup inside the remaining alias-heavy `tests/integration/test_ui_endpoints.py` surface while preserving separate alias-proof anchors
- **Required Path:** `Full`
- **Objective:** Canonicalize three monkeypatch-sensitive but non-alias-proof tests in `tests/integration/test_ui_endpoints.py` from `core.server_*_api` imports to `core.api.*` imports, while keeping the file's explicit alias-proof tests untouched.
- **Candidate:** `server alias retirement phase 2`
- **Base SHA:** `2c06b8f6`

### Scope

- **Scope IN:**
  - `docs/audit/refactor/server/command_packet_server_alias_retirement_phase2_2026-03-12.md`
  - `docs/audit/refactor/server/context_map_server_alias_retirement_phase2_2026-03-12.md`
  - `tests/integration/test_ui_endpoints.py`
- **Scope OUT:**
  - `src/core/server.py`
  - all `src/core/server_*_api.py` alias stub files
  - all `src/core/api/*.py` runtime modules
  - tests outside `tests/integration/test_ui_endpoints.py`
  - logger identity in `src/core/api/config.py`
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
- Any regression in explicit alias-proof tests inside `tests/integration/test_ui_endpoints.py`
- Any need to touch runtime code or alias stubs
- Any mismatch between test claims and what the updated tests actually prove
- Any failing determinism, cache-invariance, or pipeline-invariant guard

### Output required

- **Implementation Report**
- **PR evidence template**
